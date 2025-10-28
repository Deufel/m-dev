# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "anthropic==0.71.0",
#     "fastcore==1.8.13",
#     "mcp==1.18.0",
#     "mistletoe==1.5.0",
#     "pytest==8.4.2",
#     "scikit-learn==1.7.2",
# ]
# ///

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="columns", app_title="", auto_download=["html"])

with app.setup(hide_code=True):
    __version__ = "0.0.1"
    __package_name__ = "m-dev"
    __description__ = "Build and publish python packages from marimo notebooks"
    __author__ = "Deufel <MDeufel13@gmail.com>"
    __license__ = "MIT"

    import re
    import ast
    import tomllib
    import copy
    import os
    import tempfile
    import shutil
    import inspect
    import sys
    import importlib
    import io
    import zipfile

    from pathlib import Path
    from importlib.metadata import packages_distributions
    from textwrap import dedent, indent
    from typing import Callable, Literal, Dict, Any, Tuple

    from tokenize import tokenize, COMMENT
    from textwrap import dedent

    from mistletoe import markdown

    import numpy as np


@app.cell(hide_code=True)
def _(mo, todo_checklist):
    mo.md(
        rf"""
    #| README


    # m-dev

    Version: {__version__}


    {todo_checklist}

    **Build Python packages from a single marimo notebook.**

    Version: `0.0.1` | **Work in progress**

    ---

    ## What it does

    `m-dev` turns **one marimo notebook** into a **clean, installable Python package**.

    - Exports **self-contained functions/classes** (auto-detected via marimo’s `@function` / `@class_definition`)
    - Generates `pyproject.toml` from `/// script` and `app.setup`
    - Tracks **real dependencies** using marimo + UV in `--sandbox` mode
    - Copies `#| readme` cell → `README.md`
    - Builds docstrings from `#| param` comments (nbdev-style)
    - Final package: **marimo-free, PyPI-ready**

    Your notebook is your **IDE, test runner, demo, and source of truth**.

    ---

    ## Problems it solves

    | Problem | How `m-dev` helps |
    |--------|------------------|
    | "I deleted a cell and didn’t notice" | With marimo, **downstream cells break immediately** — you *can’t* miss it |
    | "I don’t know what packages I need" | marimo + UV in `--sandbox` **tracks every import** and suggests missing ones |
    | "My package has wrong/outdated deps" | Only **deps from `app.setup` cell** go into `pyproject.toml` — versions pulled from **current UV environment** |
    | "Jupyter execution order is fragile" | marimo runs via **DAG** — no hidden state, no out-of-order surprises |

    ---

    ## How it works

    1. Write in a marimo notebook:
        - TODO Build an init CLI
    2. Run in a Sandbox (required for accurate dependency tracking)
        - uvx marimo edit --sandbox mypkg.py
    3. Build the Package
       ```python
        import m_dev (need  anew name wont let me use this.. ?)
        m_dev.build("mypkg.py", "dist/")
        ```
    4. Output
       ```bash
        dist/
        ├── src/mypkg/
        │   ├── __init__.py
        │   └── core.py
        ├── pyproject.toml
        └── README.md
        ```
    5. install
        ```python
        pip install dist/mypkg-0.1.0.tar.gz
        ```

    ## Design choices

     - No #| export needed → Exports auto-detected from marimo decorators via AST
     - Self-containment via marimo’s DAG → If a function uses a variable from another cell, it won’t export
     - Dependencies = only what’s in app.setup → Version numbers pulled from current UV lockfile → tests run on exact versions that ship
     - Unused imports? Still require manual cleanup → Not perfect, but: if you delete all deps, marimo detects missing imports and prompts to install
     - Testing stays in notebook → Use marimo’s built-in pytest support — runs live, never exported
    """
    )
    return


@app.cell
def _():
    return


@app.cell(column=1, hide_code=True)
def _(mo):
    mo.md(r"""## Development Packages""")
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pytest
    from sklearn.model_selection import train_test_split #allows us to test imports
    return mo, pytest


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Utilities""")
    return


@app.class_definition(hide_code=True)
class PEP723Parser:
    "a simple parser also a bit of a test to ensure that classes are parsed correctlly"
    REGEX = r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$'
    @staticmethod
    def extract_content(match):
        '''Extract TOML content from a PEP 723 metadata block match'''
        content = ''.join(
            line[2:] if line.startswith('# ') else line[1:]
            for line in match.group('content').splitlines(keepends=True)
        )
        return content


@app.function(hide_code=True)
def get_package_name(
    module_name: str  # Import module name (e.g., 'sklearn', 'bs4')
) -> str:             # PyPI package name (e.g., 'scikit-learn', 'beautifulsoup4')
    "Map import module name to PyPI package name"
    pkg_map = packages_distributions()
    if module_name in pkg_map: return pkg_map[module_name][0]
    return module_name


@app.function(hide_code=True)
def is_marimo_export_decorator(
    decorator # the decorator that marimo attached to the cell
) -> bool:    # True if the function or cell is reusable - should match marimos detection
    "Check if decorator is app.function or app.class_definition (with or without args)"
    # If it's a call like @app.function(hide_code=True), check the func part
    if isinstance(decorator, ast.Call):
        decorator_name = ast.unparse(decorator.func)
    else:
        # Simple decorator like @app.function
        decorator_name = ast.unparse(decorator)

    return decorator_name in ['app.function', 'app.class_definition']


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Validation""")
    return


@app.function(hide_code=True)
def validate_setup_metadata(
    setup_metadata: dict  # Package metadata from setup cell
) -> None:                # Raises ValueError if invalid
    "Validate that required metadata keys exist and have valid values for package generation"

    required = ['__package_name__', '__version__', '__description__', '__author__', '__license__']
    missing = [k for k in required if k not in setup_metadata]
    if missing: raise ValueError(f"Setup cell missing required metadata: {', '.join(missing)}\n\nAdd these to your setup cell:\n" + '\n'.join([f"    {k} = '...'" for k in missing]))
    pkg_name = setup_metadata['__package_name__']
    if not pkg_name or not pkg_name.strip(): raise ValueError("__package_name__ cannot be empty")
    if not pkg_name.replace('-', '').replace('_', '').isalnum(): raise ValueError(f"__package_name__ '{pkg_name}' must contain only letters, numbers, hyphens, and underscores")
    version = setup_metadata['__version__']
    if not version or not version.strip(): raise ValueError("__version__ cannot be empty")
    desc = setup_metadata['__description__']
    if not desc or not desc.strip(): raise ValueError("__description__ cannot be empty")
    author = setup_metadata['__author__']
    if not author or not author.strip(): raise ValueError("__author__ cannot be empty")
    if '<' not in author or '>' not in author: raise ValueError("__author__ must be in format 'Name <email@example.com>'")
    email_part = author.split('<')[1].split('>')[0].strip()
    if not email_part or '@' not in email_part: raise ValueError(f"__author__ email '{email_part}' is not valid")
    license_val = setup_metadata['__license__']
    if not license_val or not license_val.strip(): raise ValueError("__license__ cannot be empty")


@app.function(hide_code=True)
def validate_script_metadata(
    script_metadata: dict # metadata from script tag that is injected by marimo (must be running in sandbox mode) 
) -> None:                # Raises ValueError if invalid
    "Validate script metadata has required fields for package generation"

    if not script_metadata: raise ValueError("No PEP 723 script metadata found. Run notebook with --sandbox flag to generate it.")
    if 'requires-python' not in script_metadata: raise ValueError("Script metadata missing 'requires-python'. This should be auto-generated by marimo.")
    if 'dependencies' not in script_metadata: raise ValueError("Script metadata missing 'dependencies'. This should be auto-generated by marimo.")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Extraction""")
    return


@app.function(hide_code=True)
def extract_script_metadata(
    notebook_path: str  # Path to the marimo notebook file
) -> dict:              # Dictionary containing requires-python and dependencies
    "Extract PEP 723 script metadata from marimo notebook header"

    with open(notebook_path) as f:
        script = f.read()

    matches = [m for m in re.finditer(PEP723Parser.REGEX, script) if m.group('type') == 'script']

    if len(matches) > 1:
        raise ValueError('Multiple script blocks found')
    elif len(matches) == 1:
        content = PEP723Parser.extract_content(matches[0])
        return tomllib.loads(content)
    else:
        return {}


@app.function(hide_code=True)
def extract_exports(
    notebook_path: str  # Notebook path / name
) -> tuple:             # Tuple contaning (setup_metadata, setup_imports, setup_packages, exports)
    "Extract metadata, imports, and exportable functions/classes from marimo notebook"
    source_code = Path(notebook_path).read_text()

    tree = ast.parse(source_code)
    setup_metadata, setup_imports, setup_packages, exports = ({}, [], [], [])

    for node in tree.body:
        if isinstance(node, ast.With):
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    setup_metadata[stmt.targets[0].id] = ast.literal_eval(stmt.value)
                elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    setup_imports.append(ast.unparse(stmt))
                    if isinstance(stmt, ast.Import):
                        for alias in stmt.names:
                            setup_packages.append(alias.name)
                    elif isinstance(stmt, ast.ImportFrom):
                        setup_packages.append(stmt.module.split('.')[0])

        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if any(is_marimo_export_decorator(d) for d in node.decorator_list):
                if not node.name.startswith('test_'):
                    # Extract original source with comments
                    original_source = ast.get_source_segment(source_code, node)

                    # Remove the marimo decorators from the source
                    lines = original_source.split('\n')
                    filtered_lines = []
                    for line in lines:
                        stripped = line.strip()
                        if not (stripped.startswith('@app.function') or 
                                stripped.startswith('@app.class_definition')):
                            filtered_lines.append(line)

                    exports.append('\n'.join(filtered_lines))

    return (setup_metadata, setup_imports, setup_packages, exports)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Write Files""")
    return


@app.function(hide_code=True)
def generate_pyproject_toml(
    setup_metadata: dict,         # package metadata from setup cell 
    script_metadata: dict,        # metadata from /// script block 
    setup_packages: list,         # Package Dependencies; inner join from script and setup 
    output_file='pyproject.toml'  # Path for output file
) -> str:                         # Path to written file
    "Generate pyproject.toml from notebook using ///script block and setup cell"

    validate_setup_metadata(setup_metadata)
    readme_line = 'readme = "README.md"' if Path('README.md').exists() else ''
    pkg_names = [get_package_name(pkg) for pkg in setup_packages]
    prod_deps = [dep for dep in script_metadata['dependencies'] if any((dep.split('==')[0].strip() == pkg for pkg in pkg_names))]
    toml_content = f'''[build-system]\nrequires = ["setuptools>=45", "wheel"]\nbuild-backend = "setuptools.build_meta"\n\n[project]\n{readme_line}\nname = "{setup_metadata['__package_name__']}"\nversion = "{setup_metadata['__version__']}"\ndescription = "{setup_metadata['__description__']}"\nauthors = [\n    {{name = "{setup_metadata['__author__'].split('<')[0].strip()}", email = "{setup_metadata['__author__'].split('<')[1].strip('>')}"}},\n]\nlicense = {{text = "{setup_metadata['__license__']}"}}\nrequires-python = "{script_metadata['requires-python']}"\ndependencies = {prod_deps}\n'''
    Path(output_file).write_text(toml_content)
    return output_file


@app.function(hide_code=True)
def write_module(
    setup_imports: list, # Import statements from setup cell
    exports: list,       # Exported function/class definitions
    output_file: str     # Path for output Python module file
) -> str:                # Path to written file
    "Write Python module file with imports and exported code"

    with Path(output_file).open('w') as f:
        for imp in setup_imports: f.write(imp + '\n')
        f.write('\n')
        for export in exports: f.write(export + '\n\n')
    return output_file


@app.function(hide_code=True)
def process_exports(
    exports: list,        # List of exported function/class source strings
    docstring_style: str  # Target docstring style: 'google', 'numpy', or 'nbdev'
) -> list:                # List of processed exports
    "Process exports list, reformatting docstrings if needed"
    if docstring_style == 'nbdev':
        return exports  # No processing needed

    processed = []
    for export in exports:
        reformatted = reformat_function_docstring(export, docstring_style)
        processed.append(reformatted)

    return processed


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Readme Extraction""")
    return


@app.function(hide_code=True)
def extract_readme(
    notebook_path: str,      # Path to the marimo notebook file
    output_dir: str,         # Directory where README.md will be written
    setup_metadata: dict     # Setup cell metadata for f-string substitution
) -> str:                    # Path to written README.md file, or empty string if no readme cell found
    "Extract README from notebook cell marked with #| readme and write to output directory"

    source_code = Path(notebook_path).read_text()

    tree = ast.parse(source_code)
    readme_contents = []

    # Check both regular cells (FunctionDef) and setup cells (With blocks)
    for node in tree.body:
        # Check @app.cell decorated functions (hidden or not)
        if isinstance(node, ast.FunctionDef):
            func_source = ast.get_source_segment(source_code, node)
            if func_source and 'mo.md(' in func_source and '#| README' in func_source:
                # Extract the string content from mo.md(...)
                content = extract_mo_md_content(func_source)
                if content and '#| README' in content:
                    lines = content.split('\n')
                    readme_text = '\n'.join(line for line in lines if not line.strip().startswith('#| README'))
                    readme_contents.append(readme_text.strip())

        # Check setup cell (with app.setup:)
        elif isinstance(node, ast.With):
            for stmt in node.body:
                if isinstance(stmt, ast.Expr):
                    stmt_source = ast.get_source_segment(source_code, stmt)
                    if stmt_source and 'mo.md(' in stmt_source and '#| README' in stmt_source:
                        content = extract_mo_md_content(stmt_source)
                        if content and '#| README' in content:
                            lines = content.split('\n')
                            readme_text = '\n'.join(line for line in lines if not line.strip().startswith('#| README'))
                            readme_contents.append(readme_text.strip())

    if len(readme_contents) == 0:
        print('⚠️  Warning: No #| README cell found. README.md will not be generated.')
        print('   For PyPI distribution, consider adding a cell with mo.md() containing #| README')
        return ''

    if len(readme_contents) > 1:
        print(f'⚠️  Warning: Found {len(readme_contents)} cells with #| README marker. Using only the first one.')

    # Substitute f-string variables from setup_metadata
    readme_text = readme_contents[0]
    for key, value in setup_metadata.items():
        readme_text = readme_text.replace(f'{{{key}}}', str(value))

    readme_path = Path(output_dir) / 'README.md'
    readme_path.write_text(readme_text)

    print(f'✅ README.md generated from notebook')
    return str(readme_path)


@app.function(hide_code=True)
def extract_mo_md_content(source: str) -> str:
    "Extract the string content from a mo.md() call, handling r/f/rf string prefixes"
    # Find mo.md( and extract everything between the opening and closing quotes
    import re
    # Match mo.md with optional whitespace, then capture string with various prefixes
    pattern = r'mo\.md\s*\(\s*[rf]*"""(.*?)"""|mo\.md\s*\(\s*[rf]*\'\'\'(.*?)\'\'\'|mo\.md\s*\(\s*[rf]*"(.*?)"|mo\.md\s*\(\s*[rf]*\'(.*?)\''
    match = re.search(pattern, source, re.DOTALL)
    if match:
        # Return whichever group matched (triple quotes or single quotes)
        for i in range(1, len(match.groups()) + 1):
            if match.group(i) is not None:
                return match.group(i)
    return ''


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Documentation Standardnization""")
    return


@app.function(hide_code=True)
def extract_param_docs_from_source(
    func_source: str   # function source to be tokenized and processed
) -> dict:             # nested dict {'param_name': {'anno': type, 'default': value, 'docment': 'doc'}, 'return': {...}}
    "Extract parameter documentation from source code with nbdev-style comments"    
    # 1. Tokenize to get comments
    tokens = tokenize(io.BytesIO(func_source.encode('utf-8')).readline)
    clean_re = re.compile(r'^\s*#(.*)\s*$')
    comments = {}
    for token in tokens:
        if token.type == COMMENT:
            match = clean_re.findall(token.string)
            if match:
                comments[token.start[0]] = match[0].strip()

    # 2. Parse AST to get parameter locations and info
    tree = ast.parse(dedent(func_source))
    if not tree.body:
        return {}

    defn = tree.body[0]
    if not isinstance(defn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return {}

    # Build line number to param name mapping
    param_locs = {}
    for arg in defn.args.args:
        param_locs[arg.lineno] = arg.arg
    if defn.args.vararg:
        param_locs[defn.args.vararg.lineno] = defn.args.vararg.arg
    for arg in defn.args.kwonlyargs:
        param_locs[arg.lineno] = arg.arg
    if defn.args.kwarg:
        param_locs[defn.args.kwarg.lineno] = defn.args.kwarg.arg
    if defn.returns:
        param_locs[defn.returns.lineno] = 'return'

    # 3. Match comments to parameters
    def get_comment_for_param(line, param_name):
        # Check same line
        if line in comments:
            return comments[line]
        # Check lines above (multi-line comments)
        line -= 1
        result = []
        while line > 0 and line in comments and line not in param_locs:
            result.append(comments[line])
            line -= 1
        return dedent('\n'.join(reversed(result))) if result else None

    param_docs = {}
    for line, param_name in param_locs.items():
        param_docs[param_name] = get_comment_for_param(line, param_name)

    # 4. Extract full signature info from AST
    result = {}

    # Process regular args
    for i, arg in enumerate(defn.args.args):
        anno = ast.unparse(arg.annotation) if arg.annotation else None
        default = None
        # Defaults are stored backwards from the end
        default_offset = len(defn.args.args) - len(defn.args.defaults)
        if i >= default_offset:
            default = ast.unparse(defn.args.defaults[i - default_offset])

        result[arg.arg] = {
            'anno': anno,
            'default': default,
            'docment': param_docs.get(arg.arg)
        }

    # Process *args
    if defn.args.vararg:
        result[defn.args.vararg.arg] = {
            'anno': ast.unparse(defn.args.vararg.annotation) if defn.args.vararg.annotation else None,
            'default': None,
            'docment': param_docs.get(defn.args.vararg.arg)
        }

    # Process keyword-only args
    for i, arg in enumerate(defn.args.kwonlyargs):
        anno = ast.unparse(arg.annotation) if arg.annotation else None
        default = ast.unparse(defn.args.kw_defaults[i]) if defn.args.kw_defaults[i] else None

        result[arg.arg] = {
            'anno': anno,
            'default': default,
            'docment': param_docs.get(arg.arg)
        }

    # Process **kwargs
    if defn.args.kwarg:
        result[defn.args.kwarg.arg] = {
            'anno': ast.unparse(defn.args.kwarg.annotation) if defn.args.kwarg.annotation else None,
            'default': None,
            'docment': param_docs.get(defn.args.kwarg.arg)
        }

    # Process return annotation
    if defn.returns:
        result['return'] = {
            'anno': ast.unparse(defn.returns),
            'default': None,
            'docment': param_docs.get('return')
        }

    return result


@app.function(hide_code=True)
def reformat_function_docstring(
    func_source: str,             # source function
    target_style: str = 'google'  # one of "google", "numpy", or "nbdev"
) -> str:                         # Reformatted function with the docstring in the target style
    "Reformat function docstring to target style, preserving nbdev-style comments"
    try:
        # Step 1: Execute the source to get a function object
        namespace = {}
        exec(func_source, namespace)
        func = next(v for v in namespace.values() if callable(v) and hasattr(v, '__name__'))

        # Step 2: Extract structured docs using fastcore
        docs = extract_param_docs_from_source(func_source)

        # Step 3: Build new docstring inline
        lines = []

        # Main description
        if func.__doc__:
            lines.append(func.__doc__.strip())

        if target_style == 'google':
            # Args section
            params = {k: v for k, v in docs.items() if k != 'return'}
            if params:
                lines.append("")
                lines.append("Args:")
                for name, info in params.items():
                    anno = info.get('anno')
                    anno_str = getattr(anno, '__name__', str(anno)) if anno != inspect._empty else ''
                    doc = info.get('docment', '')
                    if anno_str:
                        lines.append(f"    {name} ({anno_str}): {doc}")
                    else:
                        lines.append(f"    {name}: {doc}")

            # Returns section
            ret = docs.get('return')
            if ret and ret.get('docment'):
                lines.append("")
                lines.append("Returns:")
                ret_anno = ret.get('anno')
                ret_anno_str = getattr(ret_anno, '__name__', str(ret_anno)) if ret_anno != inspect._empty else ''
                ret_doc = ret.get('docment', '')
                if ret_anno_str:
                    lines.append(f"    {ret_anno_str}: {ret_doc}")
                else:
                    lines.append(f"    {ret_doc}")

        elif target_style == 'numpy':
            # Parameters section
            params = {k: v for k, v in docs.items() if k != 'return'}
            if params:
                lines.append("")
                lines.append("Parameters")
                lines.append("----------")
                for name, info in params.items():
                    anno = info.get('anno')
                    anno_str = getattr(anno, '__name__', str(anno)) if anno != inspect._empty else ''
                    doc = info.get('docment', '')
                    if anno_str:
                        lines.append(f"{name} : {anno_str}")
                    else:
                        lines.append(f"{name}")
                    if doc:
                        lines.append(f"    {doc}")

            # Returns section
            ret = docs.get('return')
            if ret and ret.get('docment'):
                lines.append("")
                lines.append("Returns")
                lines.append("-------")
                ret_anno = ret.get('anno')
                ret_anno_str = getattr(ret_anno, '__name__', str(ret_anno)) if ret_anno != inspect._empty else ''
                ret_doc = ret.get('docment', '')
                if ret_anno_str:
                    lines.append(f"{ret_anno_str}")
                if ret_doc:
                    lines.append(f"    {ret_doc}")

        else:  # nbdev or unknown
            return func_source

        new_docstring = '\n'.join(lines)

        # Step 4: Replace docstring in source using AST
        tree = ast.parse(func_source)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if (node.body and isinstance(node.body[0], ast.Expr) 
                    and isinstance(node.body[0].value, ast.Constant)):
                    # Has existing docstring
                    node.body[0].value.value = new_docstring
                else:
                    # No docstring, add one
                    doc_node = ast.Expr(value=ast.Constant(value=new_docstring))
                    node.body.insert(0, doc_node)
                break

        return ast.unparse(tree)

    except Exception as e:
        print(f"⚠️  Could not reformat docstring: {e}")
        return func_source


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Build Package""")
    return


@app.function(hide_code=True)
def build_package(
    notebook_path: str,            # Path to the marimo notebook file
    output_dir: str='dist',        # Output directory for package files
    docstring_style: str='google'  # Docsignature to use in final package (google, numpy, nbdev)
) -> str:
    "Build a Python package from a marimo notebook"

    setup_metadata, setup_imports, setup_packages, exports = extract_exports(notebook_path)
    exports = process_exports(exports, docstring_style)
    script_metadata = extract_script_metadata(notebook_path)
    validate_setup_metadata(setup_metadata)
    validate_script_metadata(script_metadata)
    if not exports:
        print('⚠️  Warning: No exports found. Ensure functions/classes are self contained')
    if not setup_packages:
        print('⚠️  Warning: No packages imported in setup cell. Ensure package dependencies are imported there.')
    os.makedirs(output_dir, exist_ok=True)
    package_name = setup_metadata['__package_name__'].replace('-', '_')
    os.makedirs(f'{output_dir}/{package_name}', exist_ok=True)
    generate_pyproject_toml(setup_metadata, script_metadata, setup_packages, f'{output_dir}/pyproject.toml')
    write_module(setup_imports, exports, f'{output_dir}/{package_name}/__init__.py')
    extract_readme(notebook_path, output_dir, setup_metadata)
    print(f'✅ Package built in {output_dir}/')
    return output_dir


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Generate Documentation""")
    return


@app.function(hide_code=True)
def generate_docs(
    notebook_path: str,     # Path to notebook
    package_dir: str,       # Path to built package (e.g., "src")
    output_dir: str = "docs"  # Where to write index.html
) -> str:                   # Path to generated index.html
    "Generate static HTML documentation from README and package API"



    # Step 1: Read the README
    readme_path = Path(package_dir) / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding='utf-8')
    else:
        readme_content = "# Documentation\n\nNo README found."

    # Step 2: Dynamically import the built package
    package_name = [d.name for d in Path(package_dir).iterdir() 
                    if d.is_dir() and not d.name.startswith('.')][0]
    sys.path.insert(0, str(package_dir))
    package = importlib.import_module(package_name)

    # Step 3: Extract functions/classes and their info
    members = inspect.getmembers(package, lambda x: inspect.isfunction(x) or inspect.isclass(x))
    api_docs = []
    for name, obj in members:
        if name.startswith('_'):  # Skip private
            continue
        sig = inspect.signature(obj)
        doc = inspect.getdoc(obj) or "No documentation available."
        api_docs.append({
            'name': name,
            'signature': sig,
            'docstring': doc,
            'type': 'function' if inspect.isfunction(obj) else 'class'
        })

    # Step 4: Convert to markdown
    markdown_parts = [readme_content, "\n\n## API Reference\n\n"]
    for item in api_docs:
        markdown_parts.append(f"### {item['name']}\n\n")
        markdown_parts.append(f"```python\n{item['name']}{item['signature']}\n```\n\n")
        markdown_parts.append(f"{item['docstring']}\n\n")
    full_markdown = "".join(markdown_parts)

    # Step 5: Convert to HTML and write file
    html_body = markdown(full_markdown)
    html_template = f"""<!DOCTYPE html>
<html>

<body>
{html_body}
</body>
</html>"""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    index_path = output_path / "index.html"
    index_path.write_text(html_template, encoding='utf-8')

    print(f'✅ Documentation generated at {index_path}')
    return str(index_path)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Multi Note book support""")
    return


@app.function
def func():
    x = np.abs(-5)
    return print(f"{x = }")


@app.cell
def _():
    func()
    return


@app.cell
def _():
    return


@app.cell(column=2, hide_code=True)
def _(mo):
    mo.md(r"""## Testing""")
    return


@app.function(hide_code=True)
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


@app.function(hide_code=True)
def test_get_package_name_known_modules():
    # Test cases from your screenshot
    assert get_package_name('sklearn') == 'scikit-learn'
    assert get_package_name('numpy') == 'numpy'
    assert get_package_name('bs4') == 'bs4'


@app.cell(hide_code=True)
def _(pytest):
    def test_get_package_name_unknown_module():
        # Should return the module name itself if not in map
        assert get_package_name('nonexistent_module') == 'nonexistent_module'

    def test_get_package_name_empty_string():
        # Edge case
        assert get_package_name('') == ''

    @pytest.mark.parametrize("module, expected", [
        ('sklearn', 'scikit-learn'),
        ('numpy', 'numpy'),
        ('bs4', 'bs4'),
        ('requests', 'requests'),  # assuming it's in the map
        ('unknown_pkg', 'unknown_pkg'),
    ])
    def test_get_package_name_parametrized(module, expected):
        assert get_package_name(module) == expected
    return


@app.function
def test_generate_docs():
    # Build the package first
    build_package("./notebooks/00_core.py", output_dir="test_output", docstring_style="google")

    # Generate docs
    docs_path = generate_docs(
        notebook_path="./notebooks/00_core.py",
        package_dir="test_output",
        output_dir="test_output/docs"
    )

    # Check the output exists
    assert Path(docs_path).exists()

    # Optional: check content
    content = Path(docs_path).read_text()
    assert "API Reference" in content


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Build Package""")
    return


@app.cell
def _():
    build_package("./notebooks/00_core.py", output_dir="src", docstring_style="google")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    to add to pypi run 

    ```
    uv build
    ```

    # Test PyPi
    ```
    uv publish --publish-url https://test.pypi.org/legacy/ dist/*
    ```

    # Real PyPi
    ```
    uv publish --token pypi-... dist/*
    ```
    """
    )
    return


@app.cell
def _(mo):
    _todo_items = [
        {"item": "Normalize and Restructure NBDev Deocs -> more standard documentation", "status": True},
        {"item": "Extract README.md from notebook", "status": True},
        {"item": "Integrate CLI for init, test, and mkdocs", "status": False},
        {"item": "Static Docs Generation with no dependencies", "status": False},
        {"item": "Better testing", "status": False},
        {"item": "Better PyPI integration", "status": False},

        {"item": "Generate PyPI setup thing from marimo", "status": False},
        {"item": "Enhance Pyproject.toml with repo. and other good info", "status": False},
        {"item": "Multi notebook support", "status": False},
        {"item": "GitHub Actions Support", "status": False},
        {"item": "Clean up os.path and Path - use Path throughout", "status": False},
    ]

    todo_checklist = mo.md(f"""
    ## 📋 Package Development TODOs

    {mo.vstack([
        mo.hstack([mo.ui.checkbox(value=todo["status"]), mo.md(f"**{todo['item']}**")], align="center", justify="start") 
        for todo in _todo_items
    ])}
    """)

    todo_checklist
    return (todo_checklist,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
