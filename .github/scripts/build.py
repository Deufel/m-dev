"""
Build script for m-dev: builds package and exports marimo notebooks to static HTML.
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fire==0.7.0",
#     "loguru==0.7.0"
# ]
# ///

import subprocess
import ast
import copy
import os
import shutil
import tomllib
from typing import List, Union
from pathlib import Path

import fire
from loguru import logger

# Package building functions
def extract_script_metadata(filename):
    with open(filename) as f:
        lines = f.readlines()
    
    in_block = False
    script_lines = []
    
    for line in lines:
        if line.strip() == '# /// script':
            in_block = True
        elif line.strip() == '# ///':
            break
        elif in_block:
            script_lines.append(line[2:])
    
    return tomllib.loads(''.join(script_lines))

def extract_exports(filename):
    with open(filename) as f:
        tree = ast.parse(f.read())
    
    setup_code = []
    exports = []
    
    for node in tree.body:
        if isinstance(node, ast.With):
            metadata = {}
            imports = []
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    metadata[stmt.targets[0].id] = ast.literal_eval(stmt.value)
                elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(stmt))
        
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if any(ast.unparse(d) in ['app.function', 'app.class_definition'] for d in node.decorator_list):
                if not node.name.startswith('test_'):
                    node_copy = copy.deepcopy(node)
                    node_copy.decorator_list = [d for d in node.decorator_list if ast.unparse(d) not in ['app.function', 'app.class_definition']]
                    exports.append(ast.unparse(node_copy))
    
    return metadata, imports, exports

def generate_pyproject_toml(metadata, script_metadata, output_file="pyproject.toml"):
    """Generate pyproject.toml from notebook metadata"""
    
    readme_line = ""
    if os.path.exists("README.md"):
        readme_line = 'readme = "README.md"'
    
    toml_content = f"""[project]
{readme_line}
name = "{metadata['__package_name__']}"
version = "{metadata['__version__']}"
description = "{metadata['__description__']}"
authors = [
    {{name = "{metadata['__author__'].split('<')[0].strip()}", email = "{metadata['__author__'].split('<')[1].strip('>')}"}},
]
license = {{text = "{metadata['__license__']}"}}
requires-python = "{script_metadata['requires-python']}"
dependencies = {script_metadata['dependencies']}
"""
    
    with open(output_file, 'w') as f:
        f.write(toml_content)

def write_module(setup_code, exports, output_file):
    with open(output_file, 'w') as f:
        for imp in setup_code:
            f.write(imp + '\n')
        
        f.write('\n')
        
        for export in exports:
            f.write(export + '\n\n')

def build_package(notebook_file, output_dir="src"):
    """Build a Python package from a marimo notebook"""
    os.makedirs(output_dir, exist_ok=True)
    
    metadata, imports, exports = extract_exports(notebook_file)
    script_meta = extract_script_metadata(notebook_file)
    
    generate_pyproject_toml(metadata, script_meta, 
                           f"{output_dir}/pyproject.toml")
    
    package_name = metadata['__package_name__'].replace('-', '_')
    write_module(imports, exports, f"{output_dir}/{package_name}.py")
    
    if os.path.exists("README.md"):
        shutil.copy("README.md", f"{output_dir}/README.md")
    
    logger.info(f"✅ Package built in {output_dir}/")

# Notebook export functions
def _export_html(notebook_path: Path, output_dir: Path) -> bool:
    """Export a single marimo notebook to static HTML."""
    logger.info(f"Exporting {notebook_path} to static HTML")
    
    cmd: List[str] = ["uvx", "marimo", "export", "html", "--sandbox", "--no-include-code"]
    
    try:
        output_file: Path = output_dir / notebook_path.with_suffix(".html")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        cmd.extend([str(notebook_path), "-o", str(output_file)])
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Successfully exported {notebook_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error exporting {notebook_path}: {e.stderr}")
        return False

def _export(folder: Path, output_dir: Path) -> List[dict]:
    """Export all marimo notebooks in a folder."""
    if not folder.exists():
        logger.warning(f"Directory not found: {folder}")
        return []
    
    notebooks = list(folder.rglob("*.py"))
    
    if not notebooks:
        logger.warning(f"No notebooks found in {folder}!")
        return []
    
    notebook_data = [
        {
            "display_name": (nb.stem.replace("_", " ").title()),
            "html_path": str(nb.with_suffix(".html")),
        }
        for nb in notebooks
        if _export_html(nb, output_dir)
    ]
    
    logger.info(f"Successfully exported {len(notebook_data)} out of {len(notebooks)} files")
    return notebook_data

def _generate_index(output_dir: Path, notebooks_data: List[dict]) -> None:
    """Generate index.html listing all notebooks."""
    logger.info("Generating index.html")
    
    index_path: Path = output_dir / "index.html"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        links = [f'<li><a href="{nb["html_path"]}">{nb["display_name"]}</a></li>' 
                 for nb in notebooks_data]
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>m-dev Documentation</title>
    <style>
        body {{ font-family: system-ui; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
        h1 {{ color: #333; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 1rem 0; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>m-dev Documentation</h1>
    <p>Static marimo notebook documentation</p>
    <ul>{''.join(links)}</ul>
</body>
</html>
"""
        
        with open(index_path, "w") as f:
            f.write(html_content)
        logger.info(f"Successfully generated index.html")
        
    except Exception as e:
        logger.error(f"Error generating index.html: {e}")

def main(output_dir: Union[str, Path] = "_site") -> None:
    """Main build function."""
    logger.info("Starting m-dev build process")
    
    output_dir: Path = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build the package
    core_notebook = Path("notebooks/00_core.py")
    if core_notebook.exists():
        build_package(str(core_notebook))
    
    # Export notebooks
    notebooks_data = _export(Path("notebooks"), output_dir)
    
    if not notebooks_data:
        logger.warning("No notebooks found!")
        return
    
    _generate_index(output_dir=output_dir, notebooks_data=notebooks_data)
    
    logger.info(f"✅ Build completed. Output: {output_dir}")

if __name__ == '__main__':
    fire.Fire(main)
