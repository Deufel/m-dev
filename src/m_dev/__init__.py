import re
import ast
import tomllib
import copy
import os
import tempfile
import shutil
import inspect

def extract_script_metadata(filename: str) -> dict:
    """Extract PEP 723 script metadata from marimo notebook header"""
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

def extract_exports(filename: str) -> tuple:
    """Extract metadata, imports, and exportable functions/classes from marimo notebook"""
    with open(filename) as f:
        tree = ast.parse(f.read())
    setup_code = []
    setup_packages = []
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
                    if isinstance(stmt, ast.Import):
                        for alias in stmt.names:
                            setup_packages.append(alias.name)
                    elif isinstance(stmt, ast.ImportFrom):
                        setup_packages.append(stmt.module)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if any((ast.unparse(d) in ['app.function', 'app.class_definition'] for d in node.decorator_list)):
                if not node.name.startswith('test_'):
                    node_copy = copy.deepcopy(node)
                    node_copy.decorator_list = [d for d in node.decorator_list if ast.unparse(d) not in ['app.function', 'app.class_definition']]
                    exports.append(ast.unparse(node_copy))
    return (metadata, imports, setup_packages, exports)

def generate_pyproject_toml(metadata: dict, script_metadata: dict, setup_packages: list, output_file: str='pyproject.toml') -> None:
    """Generate pyproject.toml from notebook metadata, including only dependencies from setup cell and script block"""
    readme_line = ''
    if os.path.exists('README.md'):
        readme_line = 'readme = "README.md"'
    prod_deps = [dep for dep in script_metadata['dependencies'] if any((dep.startswith(pkg) for pkg in setup_packages))]
    toml_content = f'''[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n\n[project]\n{readme_line}\nname = "{metadata['__package_name__']}"\nversion = "{metadata['__version__']}"\ndescription = "{metadata['__description__']}"\nauthors = [\n    {{name = "{metadata['__author__'].split('<')[0].strip()}", email = "{metadata['__author__'].split('<')[1].strip('>')}"}},\n]\nlicense = {{text = "{metadata['__license__']}"}}\nrequires-python = "{script_metadata['requires-python']}"\ndependencies = {prod_deps}\n'''
    with open(output_file, 'w') as f:
        f.write(toml_content)

def write_module(setup_code: list, exports: list, output_file: str) -> None:
    """Write Python module file with imports and exported code"""
    with open(output_file, 'w') as f:
        for imp in setup_code:
            f.write(imp + '\n')
        f.write('\n')
        for export in exports:
            f.write(export + '\n\n')

def build_package(notebook_file: str, output_dir: str='dist') -> None:
    """Build a Python package from a marimo notebook"""
    os.makedirs(output_dir, exist_ok=True)
    metadata, imports, setup_packages, exports = extract_exports(notebook_file)
    script_meta = extract_script_metadata(notebook_file)
    package_name = metadata['__package_name__'].replace('-', '_')
    os.makedirs(f'{output_dir}/{package_name}', exist_ok=True)
    generate_pyproject_toml(metadata, script_meta, setup_packages, f'{output_dir}/pyproject.toml')
    write_module(imports, exports, f'{output_dir}/{package_name}/__init__.py')
    if os.path.exists('README.md'):
        shutil.copy('README.md', f'{output_dir}/README.md')
    print(f'✅ Package built in {output_dir}/')

