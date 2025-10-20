# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pytest==8.4.2",
# ]
# ///

import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full")

with app.setup:
    __version__ = "0.0.2"
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
    import shutil


@app.cell
def _(mo):
    mo.md(
        r"""
    # m-dev
    > A NB Dev inspired python library for writing python modules in a marimo notebook.

    This is a work in progress
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import inspect
    mo.sidebar( [ mo.outline() ] )
    return (mo,)


@app.function
def extract_script_metadata(filename:str  # Path to the marimo notebook file
                           ) -> dict:     # Dictionary containing requires-python and dependencies
    '''Extract PEP 723 script metadata from marimo notebook header'''
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


@app.cell
def _():
    format_function_doc(extract_script_metadata)
    return


@app.function
def extract_exports(filename:str  # Path to the marimo notebook file
                   ) -> tuple:    # Tuple of (metadata dict, imports list, exports list)
    '''Extract metadata, imports, and exportable functions/classes from marimo notebook'''

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


@app.cell
def _():
    format_function_doc(extract_exports)
    return


@app.function
def generate_pyproject_toml(metadata:dict,           # Package metadata from setup cell
                            script_metadata:dict,    # Script metadata from /// script block
                            output_file:str="pyproject.toml"  # Path for output file
                           ) -> None:                # Writes file, returns nothing
    '''Generate pyproject.toml from notebook metadata'''

    readme_line = ""
    if os.path.exists("../README.md"):
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


@app.cell
def _():
    format_function_doc(generate_pyproject_toml)
    return


@app.function
def write_module(setup_code:list,      # List of import statements from setup cell
                 exports:list,         # List of exported function/class definitions
                 output_file:str       # Path for output Python module file
                ) -> None:             # Writes file, returns nothing
    '''Write Python module file with imports and exported code'''
    with open(output_file, 'w') as f:
        # Write imports
        for imp in setup_code:
            f.write(imp + '\n')

        f.write('\n')  # Blank line between imports and code

        # Write exported functions/classes
        for export in exports:
            f.write(export + '\n\n')


@app.cell
def _():
    format_function_doc(write_module)
    return


@app.function
def build_package(notebook_file:str,        # Path to marimo notebook to build from
                  output_dir:str="dist"     # Directory for generated package files
                 ) -> None:                 # Builds package, returns nothing
    '''Build a Python package from a marimo notebook'''
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

    # Copy Readme to output dir to appease pypi
    shutil.copy("README.md", f"{output_dir}/README.md")

    print(f"✅ Package built in {output_dir}/")


@app.cell
def _():
    format_function_doc(build_package)
    return


@app.cell
def _():
    #build_package("./notebooks/00_core.py", output_dir="src")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Docs
    -Docs Generation
    """
    )
    return


@app.function
def format_function_doc(func):
    import marimo as mo
    import inspect

    source = inspect.getsource(func)

    # Find the first quote style that appears (the docstring opener)
    triple_double = source.find('"""')
    triple_single = source.find("'''")

    # Determine which comes first
    if triple_double == -1 and triple_single == -1:
        return mo.vstack([mo.md("No docstring found")])

    if triple_double == -1:
        quote_style = "'''"
        start = triple_single
    elif triple_single == -1:
        quote_style = '"""'
        start = triple_double
    else:
        # Both exist, use whichever comes first
        if triple_single < triple_double:
            quote_style = "'''"
            start = triple_single
        else:
            quote_style = '"""'
            start = triple_double

    end = source.find(quote_style, start + len(quote_style))

    if end == -1:
        return mo.vstack([mo.md("Unclosed docstring")])

    end += len(quote_style)
    signature_and_doc = source[:end]

    source_md = mo.md(f"""```python
{signature_and_doc}
```""")
    return mo.vstack([source_md])


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Testing""")
    return


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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
