import re
import ast
import tomllib
import copy
import os
import tempfile
import shutil
import inspect
import marimo as mo

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
            if any((ast.unparse(d) in ['app.function', 'app.class_definition'] for d in node.decorator_list)):
                if not node.name.startswith('test_'):
                    node_copy = copy.deepcopy(node)
                    node_copy.decorator_list = [d for d in node.decorator_list if ast.unparse(d) not in ['app.function', 'app.class_definition']]
                    exports.append(ast.unparse(node_copy))
    return (metadata, imports, exports)

def generate_pyproject_toml(metadata: dict, script_metadata: dict, output_file: str='pyproject.toml') -> None:
    """Generate pyproject.toml from notebook metadata"""
    readme_line = ''
    if os.path.exists('../README.md'):
        readme_line = 'readme = "README.md"'
    toml_content = f'''[project]\n{readme_line}\nname = "{metadata['__package_name__']}"\nversion = "{metadata['__version__']}"\ndescription = "{metadata['__description__']}"\nauthors = [\n    {{name = "{metadata['__author__'].split('<')[0].strip()}", email = "{metadata['__author__'].split('<')[1].strip('>')}"}},\n]\nlicense = {{text = "{metadata['__license__']}"}}\nrequires-python = "{script_metadata['requires-python']}"\ndependencies = {script_metadata['dependencies']}\n'''
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
    metadata, imports, exports = extract_exports(notebook_file)
    script_meta = extract_script_metadata(notebook_file)
    generate_pyproject_toml(metadata, script_meta, f'{output_dir}/pyproject.toml')
    package_name = metadata['__package_name__'].replace('-', '_')
    write_module(imports, exports, f'{output_dir}/{package_name}.py')
    shutil.copy('README.md', f'{output_dir}/README.md')
    print(f'✅ Package built in {output_dir}/')

def format_function_doc(func: str) -> mo.Html:
    """
    Very simple function for documenting functions with very specific function definitions
    """
    source = inspect.getsource(func)
    triple_double = source.find('"""')
    triple_single = source.find("'''")
    if triple_double == -1 and triple_single == -1:
        return mo.vstack([mo.md('No docstring found')])
    if triple_double == -1:
        quote_style = "'''"
        start = triple_single
    elif triple_single == -1:
        quote_style = '"""'
        start = triple_double
    elif triple_single < triple_double:
        quote_style = "'''"
        start = triple_single
    else:
        quote_style = '"""'
        start = triple_double
    end = source.find(quote_style, start + len(quote_style))
    if end == -1:
        return mo.vstack([mo.md('Unclosed docstring')])
    end += len(quote_style)
    signature_and_doc = source[:end]
    source_md = mo.md(f'```python\n{signature_and_doc}\n```')
    return mo.vstack([source_md])

def dev_only(content: str) -> None | str:
    """Display content only in edit mode"""
    if mo.app_meta().mode == 'edit':
        return mo.md(content)
    elif mo.app_meta().mode == 'run':
        return None

