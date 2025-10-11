# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pytest==8.4.2",
# ]
# ///

import marimo

__generated_with = "0.16.5"
app = marimo.App()

with app.setup:
    __version__ = "0.0.1"
    __package_name__ = "m-dev"
    __description__ = "Build and publish Python packages directly from marimo notebooks"
    __author__ = "Deufel <MDeufel13@gmail.com>"
    __license__ = "MIT"

    import re
    import ast
    import tomllib
    import copy
    import os
    import tempfile


@app.function
def extract_script_metadata(filename):
    with open(filename) as f:
        lines = f.readlines()

    # Find the script block
    in_block = False
    script_lines = []

    for line in lines:
        if line.strip() == '# /// script':
            in_block = True
        elif line.strip() == '# ///':
            break
        elif in_block:
            script_lines.append(line[2:])  # Remove '# ' prefix

    return tomllib.loads(''.join(script_lines))


@app.function
def test_extract_script_metadata():
    
    
    test_content = """# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy==1.24.0"]
# ///
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_path = f.name
    
    result = extract_script_metadata(temp_path)
    assert result['requires-python'] == ">=3.11"
    assert result['dependencies'] == ["numpy==1.24.0"]


@app.function
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
                    if not node.name.startswith('test_'):  # Skip test functions
                        node_copy = copy.deepcopy(node)
                        node_copy.decorator_list = [d for d in node.decorator_list if ast.unparse(d) not in ['app.function', 'app.class_definition']]
                        exports.append(ast.unparse(node_copy))

    return metadata, imports, exports


@app.function
def generate_pyproject_toml(metadata, script_metadata, output_file="pyproject.toml"):
    """Generate pyproject.toml from notebook metadata"""

    toml_content = f"""[project]
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


@app.function
def write_module(setup_code, exports, output_file):
    with open(output_file, 'w') as f:
        # Write imports
        for imp in setup_code:
            f.write(imp + '\n')

        f.write('\n')  # Blank line between imports and code

        # Write exported functions/classes
        for export in exports:
            f.write(export + '\n\n')


@app.function
def build_package(notebook_file, output_dir="dist"):
    """Build a Python package from a marimo notebook"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract all the pieces
    metadata, imports, exports = extract_exports(notebook_file)
    script_meta = extract_script_metadata(notebook_file)
    
    # Generate pyproject.toml
    generate_pyproject_toml(metadata, script_meta, 
                           f"{output_dir}/pyproject.toml")
    
    # Write the module file
    package_name = metadata['__package_name__'].replace('-', '_')
    write_module(imports, exports, f"{output_dir}/{package_name}.py")
    
    print(f"✅ Package built in {output_dir}/")


@app.cell
def _():
    build_package("./notebooks/00_core.py", output_dir="src")

    return


if __name__ == "__main__":
    app.run()
