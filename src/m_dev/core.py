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
from tokenize import tokenize, COMMENT
from pathlib import Path
from textwrap import dedent, indent
from typing import Callable, Literal, Dict, Any, Tuple, TypedDict, List, Optional
from fastcore.docments import docments, docstring, empty

class ModuleInfo(TypedDict):
    name: str           # module name (without .py)
    imports: List[str]  # import statements (assuming strings; adjust if needed)
    exports: List[str]  # formatted source code (assuming strings)
    export_names: List[str]

class ScanResult(TypedDict):
    metadata: Optional[dict]  # or a more specific type if known
    modules: List[ModuleInfo] # list of modules with \d+_ stripped     
    index_path: Optional[str]

def is_marimo_export_decorator(decorator) -> bool:
    """Check if decorator is app.function or app.class_definition (with or without args)

Parameters
----------
decorator
    the decorator that marimo attached to the cell

Returns
-------
bool
    True if the function or cell is reusable - should match marimos detection"""
    if isinstance(decorator, ast.Call):
        decorator_name = ast.unparse(decorator.func)
    else:
        decorator_name = ast.unparse(decorator)
    return decorator_name in ['app.function', 'app.class_definition']

def validate_setup_metadata(setup_metadata: dict) -> None:
    """Validate that required metadata keys exist and have valid values for package generation

Parameters
----------
setup_metadata : dict
    Package metadata from setup cell

Returns
-------
None
    Raises ValueError if invalid"""
    required = ['__version__', '__description__', '__author__', '__license__']
    missing = [k for k in required if k not in setup_metadata]
    if missing:
        raise ValueError(f"Setup cell missing required metadata: {', '.join(missing)}\n\nAdd these to your setup cell:\n" + '\n'.join([f"    {k} = '...'" for k in missing]))
    version = setup_metadata['__version__']
    if not version or not version.strip():
        raise ValueError('__version__ cannot be empty')
    desc = setup_metadata['__description__']
    if not desc or not desc.strip():
        raise ValueError('__description__ cannot be empty')
    author = setup_metadata['__author__']
    if not author or not author.strip():
        raise ValueError('__author__ cannot be empty')
    if '<' not in author or '>' not in author:
        raise ValueError("__author__ must be in format 'Name <email@example.com>'")
    email_part = author.split('<')[1].split('>')[0].strip()
    if not email_part or '@' not in email_part:
        raise ValueError(f"__author__ email '{email_part}' is not valid")
    license_val = setup_metadata['__license__']
    if not license_val or not license_val.strip():
        raise ValueError('__license__ cannot be empty')

def scan_notebooks(notebooks_dir: str='notebooks', docstring_style: str='nbdev') -> ScanResult:
    """Scan notebooks directory and extract all exports, metadata, and README

Parameters
----------
notebooks_dir : str
    Directory containing notebook files
docstring_style : str
    Docstring style for all exports

Returns
-------
ScanResult
    A typed dict with the described structure."""
    notebooks_path = Path(notebooks_dir)
    if not notebooks_path.exists():
        raise ValueError(f"Notebooks directory '{notebooks_dir}' does not exist")
    notebook_files = sorted(notebooks_path.glob('*.py'))
    if not notebook_files:
        raise ValueError(f"No .py files found in '{notebooks_dir}'")
    metadata = None
    metadata_found_in = None
    index_path = None
    modules = []
    for notebook_file in notebook_files:
        if notebook_file.name.startswith('.') or notebook_file.name == '__pycache__':
            continue
        nb_metadata, setup_imports, exports, export_names = extract_exports(str(notebook_file), docstring_style)
        if nb_metadata:
            if metadata_found_in:
                raise ValueError(f'Project metadata defined in multiple notebooks:\n  - {metadata_found_in}\n  - {notebook_file.name}\nMetadata should only be defined in one notebook (typically 00_index or index.py)')
            metadata = nb_metadata
            metadata_found_in = notebook_file.name
            index_path = str(notebook_file)
        module_name = re.sub('^\\d+_', '', notebook_file.stem)
        modules.append({'name': module_name, 'imports': setup_imports, 'exports': exports, 'export_names': export_names})
    if not metadata:
        raise ValueError(f"No project metadata found in any notebook.\nAdd metadata to your config notebook (e.g., 00_index.py) in the setup cell:\n    __version__ = '0.1.0'\n    __description__ = 'My package'\n    __author__ = 'Name <email@example.com>'\n    __license__ = 'MIT'")
    return {'metadata': metadata, 'modules': modules, 'index_path': index_path}

def extract_exports(notebook_path: str, docstring_style: str='nbdev') -> tuple:
    """Extract metadata, imports, and exportable functions/classes from marimo notebook

Parameters
----------
notebook_path : str
    Path to marimo notebook file
docstring_style : str
    Target docstring format: 'google', 'numpy', or 'nbdev'

Returns
-------
tuple
    (setup_metadata, setup_imports, exports, export_names)"""
    source_code = Path(notebook_path).read_text()
    tree = ast.parse(source_code)
    setup_metadata = {}
    setup_imports = []
    exports = []
    export_names = []
    for node in tree.body:
        if isinstance(node, ast.With):
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    setup_metadata[stmt.targets[0].id] = ast.literal_eval(stmt.value)
                elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    setup_imports.append(ast.unparse(stmt))
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if any((is_marimo_export_decorator(d) for d in node.decorator_list)):
                if node.name.startswith('test_'):
                    continue
                original_source = ast.get_source_segment(source_code, node)
                lines = original_source.split('\n')
                filtered_lines = []
                for line in lines:
                    stripped = line.strip()
                    if not (stripped.startswith('@app.function') or stripped.startswith('@app.class_definition')):
                        filtered_lines.append(line)
                clean_source = '\n'.join(filtered_lines)
                if docstring_style != 'nbdev':
                    try:
                        docs = extract_param_docs_from_ast(clean_source)
                        formatted_source = build_formatted_docstring(clean_source, docs, docstring_style)
                        exports.append(formatted_source)
                    except Exception as e:
                        print(f'⚠️  Could not reformat {node.name}: {e}')
                        exports.append(clean_source)
                else:
                    exports.append(clean_source)
                export_names.append(node.name)
    return (setup_metadata, setup_imports, exports, export_names)

def extract_param_docs_from_ast(func_source: str) -> dict:
    """Extract parameter docs using AST + tokenizer, no exec needed

Parameters
----------
func_source : str
    Function source code as string

Returns
-------
dict
    Dict mapping param names to {'anno': type, 'docment': comment}"""
    tree = ast.parse(func_source)
    func_node = tree.body[0]
    param_locs = {}
    for arg in func_node.args.args:
        param_locs[arg.lineno] = {'name': arg.arg, 'anno': ast.unparse(arg.annotation) if arg.annotation else None}
    if func_node.args.vararg:
        param_locs[func_node.args.vararg.lineno] = {'name': func_node.args.vararg.arg, 'anno': None}
    for arg in func_node.args.kwonlyargs:
        param_locs[arg.lineno] = {'name': arg.arg, 'anno': ast.unparse(arg.annotation) if arg.annotation else None}
    if func_node.args.kwarg:
        param_locs[func_node.args.kwarg.lineno] = {'name': func_node.args.kwarg.arg, 'anno': None}
    if func_node.returns:
        param_locs[func_node.returns.lineno] = {'name': 'return', 'anno': ast.unparse(func_node.returns)}
    tokens = tokenize(io.BytesIO(func_source.encode('utf-8')).readline)
    clean_re = re.compile('^\\s*#(.*)\\s*$')
    comments = {}
    for token in tokens:
        if token.type == COMMENT:
            match = clean_re.findall(token.string)
            if match:
                comments[token.start[0]] = match[0].strip()
    result = {}
    for line, param_info in param_locs.items():
        name = param_info['name']
        comment = comments.get(line, '')
        result[name] = {'anno': param_info['anno'], 'docment': comment}
    return result

def build_formatted_docstring(func_source: str, docs: dict, target_style: str) -> str:
    """Build formatted docstring from docs dict

Parameters
----------
func_source : str
    Original function source code
docs : dict
    Parameter docs from extract_param_docs_from_ast
target_style : str
    'google' or 'numpy'

Returns
-------
str
    Function source with reformatted docstring"""
    tree = ast.parse(func_source)
    func_node = tree.body[0]
    existing_doc = ast.get_docstring(func_node) or ''
    lines = [existing_doc.strip()] if existing_doc else []
    if target_style == 'google':
        params = {k: v for k, v in docs.items() if k != 'return' and v.get('docment')}
        if params:
            lines.append('')
            lines.append('Args:')
            for name, info in params.items():
                anno = info.get('anno', '')
                doc = info.get('docment', '')
                if anno:
                    lines.append(f'    {name} ({anno}): {doc}')
                else:
                    lines.append(f'    {name}: {doc}')
        ret = docs.get('return')
        if ret and ret.get('docment'):
            lines.append('')
            lines.append('Returns:')
            ret_anno = ret.get('anno', '')
            ret_doc = ret.get('docment', '')
            if ret_anno:
                lines.append(f'    {ret_anno}: {ret_doc}')
            else:
                lines.append(f'    {ret_doc}')
    elif target_style == 'numpy':
        params = {k: v for k, v in docs.items() if k != 'return' and v.get('docment')}
        if params:
            lines.append('')
            lines.append('Parameters')
            lines.append('----------')
            for name, info in params.items():
                anno = info.get('anno', '')
                doc = info.get('docment', '')
                if anno:
                    lines.append(f'{name} : {anno}')
                else:
                    lines.append(f'{name}')
                if doc:
                    lines.append(f'    {doc}')
        ret = docs.get('return')
        if ret and ret.get('docment'):
            lines.append('')
            lines.append('Returns')
            lines.append('-------')
            ret_anno = ret.get('anno', '')
            ret_doc = ret.get('docment', '')
            if ret_anno:
                lines.append(f'{ret_anno}')
            if ret_doc:
                lines.append(f'    {ret_doc}')
    new_docstring = '\n'.join(lines)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                node.body[0].value.value = new_docstring
            else:
                doc_node = ast.Expr(value=ast.Constant(value=new_docstring))
                node.body.insert(0, doc_node)
            break
    return ast.unparse(tree)

def update_pyproject_toml(setup_metadata: dict, pyproject_path: str='pyproject.toml') -> str:
    """Update pyproject.toml with metadata from notebook setup cell

Parameters
----------
setup_metadata : dict
    Package metadata from setup cell
pyproject_path : str
    Path to pyproject.toml

Returns
-------
str
    Path to updated file"""
    validate_setup_metadata(setup_metadata)
    with open(pyproject_path, 'rb') as f:
        config = tomllib.load(f)
    if 'project' not in config:
        config['project'] = {}
    config['project']['version'] = setup_metadata['__version__']
    config['project']['description'] = setup_metadata['__description__']
    config['project']['license'] = {'text': setup_metadata['__license__']}
    author_name = setup_metadata['__author__'].split('<')[0].strip()
    author_email = setup_metadata['__author__'].split('<')[1].strip('>')
    config['project']['authors'] = [{'name': author_name, 'email': author_email}]
    if '__keywords__' in setup_metadata and setup_metadata['__keywords__']:
        config['project']['keywords'] = setup_metadata['__keywords__']
    if '__classifiers__' in setup_metadata and setup_metadata['__classifiers__']:
        config['project']['classifiers'] = setup_metadata['__classifiers__']
    if any((k in setup_metadata for k in ['__repository__', '__homepage__', '__documentation__'])):
        config['project']['urls'] = {}
        if '__repository__' in setup_metadata:
            config['project']['urls']['Repository'] = setup_metadata['__repository__']
        if '__homepage__' in setup_metadata:
            config['project']['urls']['Homepage'] = setup_metadata['__homepage__']
        if '__documentation__' in setup_metadata:
            config['project']['urls']['Documentation'] = setup_metadata['__documentation__']
    try:
        import tomlkit
        with open(pyproject_path, 'r') as f:
            doc = tomlkit.load(f)
        if 'project' not in doc:
            doc['project'] = {}
        doc['project']['version'] = setup_metadata['__version__']
        doc['project']['description'] = setup_metadata['__description__']
        doc['project']['license'] = {'text': setup_metadata['__license__']}
        doc['project']['authors'] = [{'name': author_name, 'email': author_email}]
        if '__keywords__' in setup_metadata and setup_metadata['__keywords__']:
            doc['project']['keywords'] = setup_metadata['__keywords__']
        if '__classifiers__' in setup_metadata and setup_metadata['__classifiers__']:
            doc['project']['classifiers'] = setup_metadata['__classifiers__']
        if any((k in setup_metadata for k in ['__repository__', '__homepage__', '__documentation__'])):
            if 'urls' not in doc['project']:
                doc['project']['urls'] = {}
            if '__repository__' in setup_metadata:
                doc['project']['urls']['Repository'] = setup_metadata['__repository__']
            if '__homepage__' in setup_metadata:
                doc['project']['urls']['Homepage'] = setup_metadata['__homepage__']
            if '__documentation__' in setup_metadata:
                doc['project']['urls']['Documentation'] = setup_metadata['__documentation__']
        with open(pyproject_path, 'w') as f:
            tomlkit.dump(doc, f)
    except ImportError:
        print('⚠️  tomlkit not available, using basic TOML writing')
        import json
        with open(pyproject_path, 'a') as f:
            f.write(f'\n# Updated by m-dev\n')
    print(f'✅ Updated {pyproject_path} with metadata')
    return pyproject_path

def write_module(module_name: str, setup_imports: list, exports: list, output_file: str) -> str:
    """Write Python module file with imports and exported code

Parameters
----------
module_name : str
    Name of the module (without .py)
setup_imports : list
    Import statements from setup cell
exports : list
    Exported function/class source code
output_file : str
    Path for output file

Returns
-------
str
    Path to written file"""
    with Path(output_file).open('w') as f:
        if setup_imports:
            for imp in setup_imports:
                f.write(imp + '\n')
            f.write('\n')
        for export in exports:
            f.write(export + '\n\n')
    return output_file

def write_init(package_name: str, metadata: dict, modules: list, output_file: str) -> str:
    """Write package __init__.py with metadata and cross-module imports

Parameters
----------
package_name : str
    Package name
metadata : dict
    Project metadata from setup cell
modules : list
    List of module dicts from scan_notebooks
output_file : str
    Path to __init__.py

Returns
-------
str
    Path to written file"""
    with Path(output_file).open('w') as f:
        description = metadata.get('__description__', 'No description provided')
        f.write(f'"""{description}"""\n\n')
        f.write(f"__version__ = '{metadata['__version__']}'\n")
        if '__author__' in metadata:
            author_name = metadata['__author__'].split('<')[0].strip()
            f.write(f"__author__ = '{author_name}'\n")
        f.write('\n')
        all_exports = []
        for module in modules:
            if module['name'].startswith('00_') or not module['export_names']:
                continue
            if module['export_names']:
                exports_str = ', '.join(module['export_names'])
                f.write(f"from .{module['name']} import {exports_str}\n")
                all_exports.extend(module['export_names'])
        if all_exports:
            f.write('\n')
            f.write('__all__ = [\n')
            for name in all_exports:
                f.write(f'    "{name}",\n')
            f.write(']\n')
    print(f'✅ Generated {output_file}')
    return output_file

def old_write_init(package_name: str, metadata: dict, modules: list, output_file: str) -> str:
    """Write package __init__.py with metadata and cross-module imports

Parameters
----------
package_name : str
    Package name
metadata : dict
    Project metadata from setup cell
modules : list
    List of module dicts from scan_notebooks
output_file : str
    Path to __init__.py

Returns
-------
str
    Path to written file"""
    with Path(output_file).open('w') as f:
        description = metadata.get('__description__', 'No description provided')
        f.write(f'"""{description}"""\n\n')
        f.write(f"__version__ = '{metadata['__version__']}'\n")
        if '__author__' in metadata:
            author_name = metadata['__author__'].split('<')[0].strip()
            f.write(f"__author__ = '{author_name}'\n")
        f.write('\n')
        all_exports = []
        for module in modules:
            if module['name'].startswith('00_') or not module['export_names']:
                continue
            if module['export_names']:
                exports_str = ', '.join(module['export_names'])
                f.write(f"from {module['name']} import {exports_str}\n")
                all_exports.extend(module['export_names'])
        if all_exports:
            f.write('\n')
            f.write('__all__ = [\n')
            for name in all_exports:
                f.write(f'    "{name}",\n')
            f.write(']\n')
    print(f'✅ Generated {output_file}')
    return output_file

def extract_mo_md_content(source: str) -> str:
    """Extract the string content from a mo.md() call, handling r/f/rf string prefixes"""
    import re
    pattern = 'mo\\.md\\s*\\(\\s*[rf]*"""(.*?)"""|mo\\.md\\s*\\(\\s*[rf]*\\\'\\\'\\\'(.*?)\\\'\\\'\\\'|mo\\.md\\s*\\(\\s*[rf]*"(.*?)"|mo\\.md\\s*\\(\\s*[rf]*\\\'(.*?)\\\''
    match = re.search(pattern, source, re.DOTALL)
    if match:
        for i in range(1, len(match.groups()) + 1):
            if match.group(i) is not None:
                return match.group(i)
    return ''

def extract_all_mo_md(source: str) -> list:
    """Extract all mo.md() content from source

Returns
-------
list
    Returns list of strings"""
    pattern = 'mo\\.md\\s*\\(\\s*[rf]*"""(.*?)"""|mo\\.md\\s*\\(\\s*[rf]*\\\'\\\'\\\'(.*?)\\\'\\\'\\\'|mo\\.md\\s*\\(\\s*[rf]*"(.*?)"|mo\\.md\\s*\\(\\s*[rf]*\\\'(.*?)\\\''
    results = []
    for match in re.finditer(pattern, source, re.DOTALL):
        for i in range(1, len(match.groups()) + 1):
            if match.group(i) is not None:
                results.append(match.group(i))
    return results

def extract_readme(setup_metadata: dict, index_path: str) -> str:
    """Extract all mo.md() cells from index.py and substitute metadata

Parameters
----------
setup_metadata : dict
    Setup cell metadata for substitution
index_path : str
    Path to index notebook file

Returns
-------
str
    Path to README.md or empty string"""
    index_path = Path(index_path) if index_path else None
    if not index_path or not index_path.exists():
        print('⚠️  No index.py found. README.md will not be generated.')
        return ''
    source_code = index_path.read_text()
    md_contents = extract_all_mo_md(source_code)
    if not md_contents:
        print('⚠️  No mo.md() cells found in index.py')
        return ''
    readme_text = '\n\n'.join(md_contents)
    for key, value in setup_metadata.items():
        readme_text = readme_text.replace(f'{{{key}}}', str(value))
    Path('README.md').write_text(readme_text)
    print('✅ README.md generated from index.py')
    return 'README.md'

def build_package(notebooks_dir: str='notebooks', output_dir: str='src', docstring_style: str='nbdev') -> str:
    """Build a Python package from marimo notebook(s)

Parameters
----------
notebooks_dir : str
    Directory with notebook files
output_dir : str
    Output directory for package
docstring_style : str
    Docstring format

Returns
-------
str
    Path to built package"""
    print(f'🔍 Scanning notebooks in {notebooks_dir}/')
    scan_result = scan_notebooks(notebooks_dir, docstring_style)
    metadata = scan_result['metadata']
    modules = scan_result['modules']
    index_path = scan_result['index_path']
    package_name = metadata.get('__package_name__')
    if not package_name:
        try:
            import tomllib
            with open('pyproject.toml', 'rb') as f:
                config = tomllib.load(f)
                package_name = config['project']['name']
        except:
            raise ValueError('No __package_name__ in metadata and no pyproject.toml found')
    package_name = package_name.replace('-', '_')
    print(f'📦 Building package: {package_name}')
    package_dir = Path(output_dir) / package_name
    package_dir.mkdir(parents=True, exist_ok=True)
    for module in modules:
        if module['name'] == 'index':
            continue
        if module['exports']:
            module_file = package_dir / f"{module['name']}.py"
            write_module(module['name'], module['imports'], module['exports'], str(module_file))
            print(f"  ✅ {module['name']}.py")
    init_file = package_dir / '__init__.py'
    write_init(package_name, metadata, modules, str(init_file))
    if Path('pyproject.toml').exists():
        update_pyproject_toml(metadata, 'pyproject.toml')
    else:
        print("⚠️  No pyproject.toml found. Run 'uv init' first.")
    extract_readme(metadata, index_path)
    print(f'\n✅ Package built in {output_dir}/{package_name}/')
    return str(output_dir)

def add(a: int, b: int) -> int:
    """Add `a` to `b`

Returns
-------
int
    The result is calculated using Python's builtin `+` operator."""
    return a + b

def convert_docstyle(func, target_style='google', include_signature=True) -> str:
    """Convert function documentation between different styles.

Parameters
----------
func
    The function to convert documentation for
target_style
    One of 'docments', 'google', or 'numpy'
include_signature
    Whether to include the function signature

Returns
-------
str
    String representation in the target documentation style"""
    docs_full = docments(func, full=True)
    main_doc = docstring(func)
    func_name = func.__name__
    sig = inspect.signature(func)
    params = {k: v for k, v in docs_full.items() if k != 'return'}
    return_info = docs_full.get('return', {})
    if target_style == 'docments':
        return format_docments_style(func_name, params, return_info, main_doc, include_signature)
    elif target_style == 'google':
        return format_google_style(func_name, params, return_info, main_doc, include_signature, sig)
    elif target_style == 'numpy':
        return format_numpy_style(func_name, params, return_info, main_doc, include_signature, sig)
    else:
        raise ValueError(f"Unknown style: {target_style}. Use 'docments', 'google', or 'numpy'")

def format_docments_style(func_name, params: dict, return_info: dict, main_doc: str, include_signature: bool) -> str:
    """Format in docments style (inline comments)

Parameters
----------
func_name
    Name of the function
params : dict
    Dictionary of parameter information
return_info : dict
    Dictionary of return information
main_doc : str
    Main Docustring content
include_signature : bool
    whether to include the function signature

Returns
-------
str
    String representation in the target documentation style"""
    lines = [f'def {func_name}(']
    for i, (name, info) in enumerate(params.items()):
        anno = f":{info['anno'].__name__}" if info['anno'] != empty and hasattr(info['anno'], '__name__') else ''
        default = f"={repr(info['default'])}" if info['default'] != empty else ''
        comment = f"  # {info['docment']}" if info['docment'] and info['docment'] != empty else ''
        comma = ',' if i < len(params) - 1 else ''
        lines.append(f'    {name}{anno}{default}{comma}{comment}')
    ret_anno = f"->{return_info['anno'].__name__}" if return_info.get('anno') != empty and hasattr(return_info.get('anno'), '__name__') else ''
    ret_comment = f"  # {return_info['docment']}" if return_info.get('docment') and return_info['docment'] != empty else ''
    lines.append(f'){ret_anno}:{ret_comment}')
    if main_doc:
        lines.append(f'    "{main_doc}"')
    return '\n'.join(lines)

def format_google_style(func_name, params, return_info, main_doc, include_signature: bool, sig) -> str:
    """Format in Google style

Parameters
----------
func_name
    Name of the function
params
    Dictionary of parameter information
return_info
    Dictionary of return information
main_doc
    Main docstring content
include_signature : bool
    Whether to include the function signature
sig
    Function signature object

Returns
-------
str
    Formatted string in Google style"""
    lines = []
    if include_signature:
        lines.append(f'def {func_name}{sig}:')
    lines.append('    """' + (main_doc or ''))
    lines.append('')
    if params:
        lines.append('    Args:')
        for name, info in params.items():
            type_str = f" ({info['anno'].__name__})" if info['anno'] != empty and hasattr(info['anno'], '__name__') else ''
            default_str = f", optional, default={repr(info['default'])}" if info['default'] != empty else ''
            desc = info.get('docment', '') or ''
            lines.append(f'        {name}{type_str}: {desc}{default_str}')
        lines.append('')
    if return_info.get('anno') != empty or return_info.get('docment'):
        lines.append('    Returns:')
        ret_type = return_info.get('anno')
        type_str = f'{ret_type.__name__}: ' if ret_type != empty and hasattr(ret_type, '__name__') else ''
        ret_desc = return_info.get('docment', '') or ''
        lines.append(f'        {type_str}{ret_desc}')
    lines.append('    """')
    return '\n'.join(lines)

def format_numpy_style(func_name, params, return_info, main_doc, include_signature: bool, sig) -> str:
    """Format in NumPy style

Parameters
----------
func_name
    Name of the function
params
    Dictionary of parameter information
return_info
    Dictionary of return information
main_doc
    Main docstring content
include_signature : bool
    Whether to include the function signature
sig
    Function signature object

Returns
-------
str
    Formatted string in NumPy style"""
    lines = []
    if include_signature:
        lines.append(f'def {func_name}{sig}:')
    lines.append('    """' + (main_doc or ''))
    lines.append('')
    if params:
        lines.append('    Parameters')
        lines.append('    ----------')
        for name, info in params.items():
            type_str = info['anno'].__name__ if info['anno'] != empty and hasattr(info['anno'], '__name__') else ''
            lines.append(f'    {name} : {type_str}')
            desc = info.get('docment', '') or ''
            if desc:
                for desc_line in desc.split('\n'):
                    lines.append(f'        {desc_line}')
            if info['default'] != empty:
                lines.append(f"        (default: {repr(info['default'])})")
        lines.append('')
    if return_info.get('anno') != empty or return_info.get('docment'):
        lines.append('    Returns')
        lines.append('    -------')
        ret_type = return_info.get('anno')
        type_str = ret_type.__name__ if ret_type != empty and hasattr(ret_type, '__name__') else ''
        lines.append(f'    {type_str}')
        ret_desc = return_info.get('docment', '') or ''
        if ret_desc:
            for desc_line in ret_desc.split('\n'):
                lines.append(f'        {desc_line}')
    lines.append('    """')
    return '\n'.join(lines)

