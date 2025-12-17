import marimo

__generated_with = "0.18.3"
app = marimo.App(width="full")

with app.setup:
    import re,ast,tomllib
    from pathlib import Path
    from typing import TypedDict
    from dataclasses import dataclass,asdict
    from enum import Enum

    # Testing classes 
    from dataclasses import field
    from typing import ClassVar


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 1: Define the data structures (Wirth's key insight)
    """)
    return


@app.class_definition
class NodeKind(Enum):
    """All the types of things we extract from notebooks"""
    IMP = 'import'      # Import statements
    CONST = 'constant'  # Private constants (__var)
    EXP = 'export'


@app.class_definition
@dataclass
class Param:
    name: str                     # Parameter name
    anno: str | None = None       # Type annotation if present
    default: any = None           # Default value if present
    doc: str = ''                 # Inline comment documentation
    is_vararg: bool = False       # True if *args
    is_kwarg: bool = False


@app.class_definition
@dataclass
class CodeNode:
    """A single extracted item from the AST"""
    kind: NodeKind                      # Type of node (import/const/export)
    name: str                           # Variable/function/class name
    src: str                            # Full source code
    params: list[Param] | None = None   # Function params OR class attributes
    ret_anno: str | None = None         # Return type annotation
    ret_doc: str = ''                   # Return inline comment
    docstring: str = ''                 # Main docstring
    init_params: list[Param] | None = None


@app.class_definition
@dataclass
class Extracted:
    """Everything extracted from one notebook"""
    imports: list[str]      # All import statements as strings
    exports: list[str]      # All exported function/class source code
    exp_names: list[str]    # Just the names of exports
    consts: list[str]


@app.class_definition
class ScanResult(TypedDict):
    meta: dict                 # Package metadata from pyproject.toml
    mods: list[dict]          # List of module extraction results
    idx_path: str | None


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 2: Read metadata from pyproject.toml
    """)
    return


@app.function
def read_metadata(
    project_root: str='.',  # Location of pyproject.toml
) -> dict:                  # Dict with package_name, version, description, license, author
    """Read package metadata from pyproject.toml.

    This is the ONLY source of truth for package metadata. 
    This should always be in the root folder.
    """
    toml_path = Path(project_root)/'pyproject.toml'
    if not toml_path.exists():
        raise ValueError(f"pyproject.toml not found at {toml_path}")

    with open(toml_path,'rb') as f:
        data = tomllib.load(f)

    # Extract project metadata
    proj = data.get('project',{})

    meta = {
        '__package_name__': proj.get('name',''),
        '__version__': proj.get('version','0.0.0'),
        '__description__': proj.get('description',''),
        '__license__': proj.get('license',{}).get('text','') if isinstance(proj.get('license'),dict) else proj.get('license',''),
    }

    # Handle authors (can be list of dicts or simple string)
    authors = proj.get('authors',[])
    if authors and isinstance(authors,list) and len(authors) > 0:
        author = authors[0]
        if isinstance(author,dict):
            name = author.get('name','')
            email = author.get('email','')
            meta['__author__'] = f"{name} <{email}>" if email else name
        else:
            meta['__author__'] = str(author)
    else:
        meta['__author__'] = ''

    return meta


@app.function
def check_meta(
    meta: dict,  # Metadata dict from read_metadata()
):
    """Validate that required metadata fields are present

    Raises ValueError if __package_name__, __version__, or __description__ missing.
    """
    req = ['__package_name__','__version__','__description__']
    if miss := [k for k in req if not meta.get(k)]:
        raise ValueError(f"Missing required fields in pyproject.toml: {', '.join(miss)}")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 3: Classification
    """)
    return


@app.function
def __get_source_with_decorators(
    n: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,  # AST node
    src: str,  # Full source
) -> str:      # Source including decorators
    """Extract source including all decorators above the function/class"""
    lines = src.splitlines()

    # Find first decorator line, or function/class line if no decorators
    if n.decorator_list:
        start_line = n.decorator_list[0].lineno - 1
    else:
        start_line = n.lineno - 1

    # Find end line
    end_line = n.end_lineno if hasattr(n, 'end_lineno') else n.lineno

    return '\n'.join(lines[start_line:end_line])


@app.function
def __is_export(
    dec,  # AST decorator node to check
) -> bool:  # True if marimo export decorator
    """Check if decorator is a marimo export (@app.function or @app.class_definition)"""
    n = ast.unparse(dec.func if isinstance(dec,ast.Call) else dec)
    return n in {'app.function','app.class_definition'}


@app.function
def __extract_class_attributes(
    n: ast.ClassDef,  # Class AST node to extract from
    full_src: str,    # FULL source (not segment) to get line numbers right
) -> list[Param]:     # List of extracted attribute Params
    """Extract class attribute annotations with inline comments"""
    attrs = []
    full_lines = full_src.splitlines()

    for node in n.body:
        # AnnAssign is: name: Type = value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            anno = ast.unparse(node.annotation) if node.annotation else None
            doc = ''

            # Use absolute line number from AST (1-indexed)
            if hasattr(node, 'lineno') and 0 < node.lineno <= len(full_lines):
                line = full_lines[node.lineno - 1]
                # Extract inline comment
                if m := re.search(r'#\s*(.+)', line):
                    doc = m.group(1).strip()

            attrs.append(Param(name, anno, default=None, doc=doc))

    return attrs


@app.function
def __extract_signature(
    n: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,  # AST node
    src_seg: str,                                              # Source segment
    full_src: str,                                             # FULL source for line lookups
) -> tuple[list[Param], tuple[str, str] | None, list[Param] | None]:  # (params, return_info, init_params)
    """Extract params and return info from function/class

    Returns: (params/attributes, return_info, init_params_for_classes)
    """
    lines = src_seg.splitlines()

    # Handle classes
    if isinstance(n, ast.ClassDef):
        attrs = __extract_class_attributes(n, full_src)
        init_method = next(
            (item for item in n.body 
             if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == '__init__'), 
            None
        )
        if init_method:
            init_params, _, _ = __extract_signature(init_method, src_seg, full_src)
            return attrs, None, init_params
        return attrs, None, None

    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [], None, None

    params: list[Param] = []

    # Build defaults mapping
    total_args = len(n.args.args)
    defaults = [None] * (total_args - len(n.args.defaults)) + [
        ast.unparse(d) if d is not None else None for d in n.args.defaults
    ]

    # Regular parameters - use full_src for comment extraction
    for i, arg in enumerate(n.args.args):
        if arg.arg in ('self', 'cls'):
            continue

        anno = ast.unparse(arg.annotation) if arg.annotation else None
        default = defaults[i] if i < len(defaults) else None
        doc = __get_inline_comment(full_src, arg.lineno, rf'\b{re.escape(arg.arg)}\b')

        params.append(Param(name=arg.arg, anno=anno, default=default, doc=doc))

    # *args - use full_src
    if n.args.vararg:
        anno = ast.unparse(n.args.vararg.annotation) if n.args.vararg.annotation else None
        doc = __get_inline_comment(full_src, n.args.vararg.lineno or n.lineno, r'\*args')
        params.append(Param(name='*args', anno=anno, doc=doc, is_vararg=True))

    # **kwargs - use full_src
    if n.args.kwarg:
        anno = ast.unparse(n.args.kwarg.annotation) if n.args.kwarg.annotation else None
        doc = __get_inline_comment(full_src, n.args.kwarg.lineno or n.lineno, r'\*\*kwargs')
        params.append(Param(name='**kwargs', anno=anno, doc=doc, is_kwarg=True))

    # Return - use full_src
    ret = None
    if n.returns and not isinstance(n.returns, ast.Constant):
        ret_anno = ast.unparse(n.returns)
        ret_doc = ''
        if hasattr(n.returns, 'lineno'):
            full_lines = full_src.splitlines()
            ret_line_idx = n.returns.lineno - 1
            if 0 <= ret_line_idx < len(full_lines):
                ret_line = full_lines[ret_line_idx]
                if '->' in ret_line and '#' in ret_line:
                    after_arrow = ret_line.split('->', 1)[1]
                    if m := re.search(r'#\s*(.+)', after_arrow):
                        ret_doc = m.group(1).strip()
        ret = (ret_anno, ret_doc)

    return params, ret, None


@app.function
def __get_inline_comment(
    full_src: str,  # Full source to search in
    lineno: int,    # Absolute line number (1-indexed)
    pattern: str,   # Regex pattern to find
) -> str:           # Extracted comment or empty string
    """Extract inline comment from a specific line"""
    lines = full_src.splitlines()
    if 0 <= lineno - 1 < len(lines):
        line = lines[lineno - 1]
        if m := re.search(rf'{pattern}.*?#\s*(.+)', line):
            return m.group(1).strip()
    return ''


@app.function
def classify_node(
    n,        # AST node to classify
    src: str, # Full source code for extracting segments
) -> list[CodeNode]:  # List of extracted CodeNode objects
    """Classify AST nodes into imports, constants, and exports.

    - Imports: from ast.Import or ast.ImportFrom inside with blocks
    - Constants: private variables (__foo) from assignments
    - Exports: functions/classes with @app.function or @app.class_definition
    """
    results = []
    if isinstance(n, ast.With):
        for s in n.body:
            if isinstance(s, (ast.Import, ast.ImportFrom)):
                results.append(CodeNode(NodeKind.IMP, '', ast.unparse(s)))
            elif isinstance(s, ast.Assign):
                for tgt in s.targets:
                    if isinstance(tgt, ast.Name):
                        name = tgt.id
                        if name.startswith('__') and not name.endswith('__'):
                            results.append(CodeNode(NodeKind.CONST, name, ast.unparse(s)))

    elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        if any(__is_export(d) for d in n.decorator_list):
            if not n.name.startswith('test_'):
                # Extract source INCLUDING decorators
                src_seg = __get_source_with_decorators(n, src)

                if src_seg:
                    params, ret, init_params = __extract_signature(n, src_seg, src)
                    docstring = ast.get_docstring(n) or ''

                    results.append(CodeNode(
                        NodeKind.EXP, n.name, src_seg,
                        params=params,
                        ret_anno=ret[0] if ret else None,
                        ret_doc=ret[1] if ret else '',
                        docstring=docstring,
                        init_params=init_params
                    ))

    return results


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 4: Grouping
    """)
    return


@app.function
def group_nodes(
    nodes: list[CodeNode],  # Flat list of CodeNode objects
) -> dict[NodeKind, list[CodeNode]]:  # Dict grouped by NodeKind
    """Group nodes by their kind (IMP/CONST/EXP)"""
    groups = {k:[] for k in NodeKind}
    for n in nodes:
        groups[n.kind].append(n)
    return groups


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 5: Transformation
    """)
    return


@app.function
def __clean(src: str) -> str:
    """Remove marimo decorator lines"""
    return '\n'.join(l for l in src.splitlines() 
                     if not l.strip().startswith(('@app.function', '@app.class_definition')))


@app.function
def __param_docs(
    src: str,  # Function source code
) -> dict:     # Dict mapping param names to {anno, doc}
    """Extract ALL parameters and their docs (empty string if no comment)

    Returns dict with param names as keys, 'return' for return info.
    Each value is {anno: str|None, doc: str}.
    """
    tree = ast.parse(src); n = tree.body[0]
    if not isinstance(n,ast.FunctionDef): return {}
    res,lines = {},src.splitlines()

    # STEP 1: Get ALL parameters from AST (with empty docs)
    for arg in n.args.args:
        anno = ast.unparse(arg.annotation) if arg.annotation else None
        res[arg.arg] = {'anno':anno,'doc':''}

    # STEP 2: Fill in comments where they exist
    sig_start,sig_end = n.lineno-1, n.body[0].lineno-1 if n.body else len(lines)
    for l in lines[sig_start:sig_end]:
        if ')->' in l: continue
        if m := re.search(r'(\w+)[:=].*#\s*(.+)',l):
            name,doc = m.groups()
            if name in res: res[name]['doc'] = doc.strip()

    # STEP 3: Always include return if it exists
    if n.returns:
        anno = ast.unparse(n.returns) if not isinstance(n.returns,ast.Constant) else None
        res['return'] = {'anno':anno,'doc':''}
        if n.returns.lineno:
            ret_line = lines[n.returns.lineno-1]
            if m := re.search(r'->[^#]*#\s*(.+)',ret_line):
                res['return']['doc'] = m.group(1).strip()
    return res


@app.function
def transform_src(
    src: str,         # Source code to transform
    doc_style: str,   # Style to transform to ('google', 'unmodified', 'nbdev')
    node: CodeNode,   # CodeNode with pre-extracted metadata
) -> str:             # Transformed source code
    "Apply doc_style transformation using pre-extracted node metadata"
    cleaned = __clean(src)

    if doc_style == 'google':
        return __to_google_from_node(cleaned, node)
    elif doc_style == 'nbdev':
        return format_nbdev_signature(node)
    else:
        return cleaned


@app.function
def __to_google_from_node(
    src: str,        # Clean source (marimo decorators already removed by __clean)
    node: CodeNode,  # Node metadata
) -> str:            # With Google docstring
    """Build Google docstring from node metadata"""

    tree = ast.parse(src)
    func_node = tree.body[0]
    is_class = isinstance(func_node, ast.ClassDef)

    # Build docstring
    doc_lines = ['"""']
    if node.docstring:
        for line in node.docstring.strip().split('\n'):
            doc_lines.append(line)
        doc_lines.append('')

    if is_class:
        # Class: Attributes + Args (for __init__)
        if node.params:
            doc_lines.append('Attributes:')
            for p in node.params:
                typ = f" ({p.anno})" if p.anno else ""
                doc = p.doc or "TODO"
                doc_lines.append(f"    {p.name}{typ}: {doc}")
            doc_lines.append('')

        if node.init_params:
            doc_lines.append('Args:')
            for p in node.init_params:
                if p.is_vararg:
                    doc_lines.append(f"    *args: {p.doc or 'Variable length argument list.'}")
                elif p.is_kwarg:
                    doc_lines.append(f"    **kwargs: {p.doc or 'Arbitrary keyword arguments.'}")
                else:
                    typ = f" ({p.anno})" if p.anno else ""
                    default = f" (default: {p.default})" if p.default else ""
                    doc_lines.append(f"    {p.name}{typ}{default}: {p.doc or 'TODO'}")
            doc_lines.append('')

        doc_lines.append('"""')

        # For classes, preserve decorators and STRIP inline comments from attributes
        lines = src.splitlines()
        result = []

        # Find the class declaration line
        class_line_idx = None
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped.endswith(':') and stripped.lstrip().startswith('class '):
                class_line_idx = i
                break

        if class_line_idx is None:
            return src  # Shouldn't happen, but safety

        # Preserve all decorators before class (they're already cleaned by __clean)
        for i in range(class_line_idx):
            line = lines[i].strip()
            if line.startswith('@'):  # It's a decorator
                result.append(lines[i])

        # Add class declaration
        result.append(lines[class_line_idx])

        # Insert docstring
        indent = len(lines[class_line_idx]) - len(lines[class_line_idx].lstrip())
        base_indent = ' ' * (indent + 4)

        for doc_line in doc_lines:
            if doc_line:
                result.append(base_indent + doc_line)
            else:
                result.append('')

        # Skip old docstring if present
        j = class_line_idx + 1
        if j < len(lines):
            next_line = lines[j].strip()
            if next_line.startswith(('"""', "'''")):
                quote = '"""' if next_line.startswith('"""') else "'''"
                while j < len(lines):
                    if lines[j].strip().endswith(quote):
                        j += 1
                        break
                    j += 1

        # Process class body - STRIP inline comments from attributes
        while j < len(lines):
            body_line = lines[j]
            # Check if this is an attribute line (has : for annotation)
            if ':' in body_line and '=' in body_line and '#' in body_line:
                # This is an attribute with inline comment - strip it
                cleaned = re.sub(r'\s*#.*$', '', body_line).rstrip()
                result.append(cleaned)
            elif ':' in body_line and '#' in body_line and '=' not in body_line:
                # Attribute without default but with comment
                cleaned = re.sub(r'\s*#.*$', '', body_line).rstrip()
                result.append(cleaned)
            else:
                # Keep as-is (methods, etc)
                result.append(body_line)
            j += 1

        return '\n'.join(result)

    else:
        # FUNCTION: Build clean signature and preserve decorators
        if node.params:
            doc_lines.append('Args:')
            for p in node.params:
                if p.is_vararg:
                    doc_lines.append(f"    *args: {p.doc or 'Variable length argument list.'}")
                elif p.is_kwarg:
                    doc_lines.append(f"    **kwargs: {p.doc or 'Arbitrary keyword arguments.'}")
                else:
                    typ = f" ({p.anno})" if p.anno else ""
                    default = f" (default: {p.default})" if p.default else ""
                    doc_lines.append(f"    {p.name}{typ}{default}: {p.doc or 'TODO'}")
            doc_lines.append('')

        if node.ret_anno or node.ret_doc:
            doc_lines.append('Returns:')
            typ = f"{node.ret_anno}: " if node.ret_anno else ""
            doc_lines.append(f"    {typ}{node.ret_doc or 'The return value.'}")
            doc_lines.append('')

        doc_lines.append('"""')

        src_lines = src.splitlines()

        # Find decorators (lines before def that start with @)
        decorators = []
        for i, line in enumerate(src_lines):
            stripped = line.lstrip()
            if stripped.startswith('def ') or stripped.startswith('async def '):
                break
            if stripped.startswith('@'):
                decorators.append(line)

        # Build clean signature WITHOUT inline comments
        sig_start = func_node.lineno - 1
        sig_end = func_node.body[0].lineno - 1 if func_node.body and hasattr(func_node.body[0], 'lineno') else len(src_lines)

        sig_lines = []
        for l in src_lines[sig_start:sig_end]:
            # Strip inline comments
            if cleaned := re.sub(r'\s*#.*$', '', l).rstrip():
                sig_lines.append(cleaned)

        # Compact signature into one line
        sig = ' '.join(sig_lines).strip()
        sig = re.sub(r'\s*:\s*', ': ', sig)
        sig = re.sub(r'\s*=\s*', '=', sig)
        sig = re.sub(r'\s*->\s*', ' -> ', sig)
        sig = re.sub(r'\s+', ' ', sig)
        sig = re.sub(r'\(\s+', '(', sig)
        sig = re.sub(r'\s+\)', ')', sig)
        sig = sig.rstrip(': ')

        # Get function body (skip old docstring if present)
        body_start = func_node.body[0].lineno - 1 if func_node.body and hasattr(func_node.body[0], 'lineno') else len(src_lines)
        body_lines = src_lines[body_start:]

        if func_node.body and isinstance(func_node.body[0], ast.Expr) and isinstance(func_node.body[0].value, ast.Constant):
            skip = func_node.body[0].end_lineno - func_node.body[0].lineno + 1
            body_lines = body_lines[skip:]

        body = '\n'.join(body_lines)

        # Build final result: decorators + clean signature + docstring + body
        docstring = '\n'.join('    ' + l if l else '' for l in doc_lines)

        result_parts = []
        if decorators:
            result_parts.append('\n'.join(decorators))
        result_parts.append(f"{sig}:\n{docstring}\n{body}")

        return '\n'.join(result_parts)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 6: Extraction
    """)
    return


@app.function
def __extract(
    p: Path | str,    # Notebook path
    doc_style: str,   # Doc style
) -> Extracted:       # Extracted content
    """Extract from one notebook"""
    src = Path(p).read_text()
    tree = ast.parse(src)

    all_nodes = []
    for n in tree.body:
        all_nodes.extend(classify_node(n, src))

    groups = group_nodes(all_nodes)

    exports = []
    for node in groups[NodeKind.EXP]:
        transformed = transform_src(node.src, doc_style, node)
        exports.append(transformed)

    return Extracted(
        imports = [n.src for n in groups[NodeKind.IMP]],
        exports = exports,
        exp_names = [n.name for n in groups[NodeKind.EXP]],
        consts = [n.src for n in groups[NodeKind.CONST]]
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 7: Helper functions
    """)
    return


@app.function
def nb_name(
    f: Path,  # Path to notebook file
) -> str | None:  # Notebook name without prefix, or None to skip
    """Extract notebook name, None if should skip

    Strips numeric prefix (01_), returns None for hidden files (.*) 
    and test files (test_*).
    """
    if f.name.startswith('.'): return None
    name = re.sub(r'^\d+_','',f.stem)
    return None if name.startswith('test') else name


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 8: Main scanning logic
    """)
    return


@app.function
def scan(
    nbs: str='notebooks',        # Directory containing notebook files
    doc_style: str='google',     # Documentation style for exports
    project_root: str='.',       # Root directory with pyproject.toml
) -> ScanResult:                 # Dict with meta and mods
    """Scan notebooks and read metadata from pyproject.toml.

    No more metadata cells in notebooks! All metadata from pyproject.toml.
    Returns metadata and list of module extractions.
    """
    # Read metadata from pyproject.toml (single source of truth!)
    meta = read_metadata(project_root)
    check_meta(meta)

    # Scan notebooks
    p = Path(nbs)
    files = [(f,nb_name(f)) for f in sorted(p.glob('*.py'))]
    files = [(f,name) for f,name in files if name]

    # Extract from all files
    extracts = [(name,__extract(f,doc_style)) for f,name in files]

    # Build module list
    mods = [{'name':name,**asdict(ex)} for name,ex in extracts]

    # No more idx_path - we don't need to find metadata in notebooks
    return {'meta':meta,'mods':mods,'idx_path':None}


@app.cell
def _(mo):
    mo.md(r"""
    ### Step 9: File writing
    """)
    return


@app.function
def write_file(
    p: str,            # Output file path
    parts: list[str],  # Parts to join with double newlines
):
    """General file writer

    Joins parts with \\n\\n, filters out None/empty, adds trailing newline.
    """
    Path(p).write_text('\n\n'.join(filter(None,parts))+'\n')


@app.function
def write_mod(
    name: str,         # Module name
    imps: list[str],   # Import statements
    consts: list[str], # Private constants
    exps: list[str],   # Export source code
    p: str,            # Output file path
):
    """Write single module file

    Combines imports, constants, and exports into properly formatted module.
    """
    parts = [
        '\n'.join(imps) if imps else None,
        '\n'.join(consts) if consts else None,
        *exps
    ]
    write_file(p,parts)


@app.function
def write_init(
    pkg: str,         # Package name (for display only)
    meta: dict,       # Package metadata from pyproject.toml
    mods: list[dict], # List of module dicts with exports
    p: str,           # Path to __init__.py
):
    """Generate __init__.py with package metadata from pyproject.toml

    Includes __version__, __author__, imports public exports, builds __all__.
    Skips modules starting with '00_' or without exports.
    """
    exports = []
    parts = [f'"""{meta.get("__description__","")}"""']
    parts.append(f"__version__ = '{meta['__version__']}'")
    if a := meta.get('__author__'): 
        parts.append(f"__author__ = '{a.split('<')[0].strip()}'")

    imports = []
    for m in mods:
        if m['name'].startswith('00_') or not m['exp_names']: continue
        if public := [n for n in m['exp_names'] if not n.startswith('__')]:
            names = ', '.join(public)
            imports.append(f"from .{m['name']} import {names}")
            exports.extend(public)

    if imports: parts.append('\n'.join(imports))
    if exports:
        all_lines = ['__all__ = ['] + [f'    "{n}",' for n in sorted(exports)] + [']']
        parts.append('\n'.join(all_lines))

    write_file(p,parts)


@app.function
def extract_readme(
    meta: dict,  # Package metadata for template substitution
    nbs: str,    # Directory containing notebooks
) -> str:        # Path to generated README.md or empty string
    """Generate README.md from any notebook with mo.md() cells

    Searches notebooks for mo.md() markdown cells, concatenates them,
    substitutes metadata placeholders like {__version__}.
    """
    # Look for any notebook with README content
    for f in sorted(Path(nbs).glob('*.py')):
        src = f.read_text()
        if parts := re.findall(r'mo\.md\((?:[rf]|rf)?"""([\s\S]*?)"""',src):
            txt = '\n\n'.join(parts)
            for k,v in meta.items(): txt = txt.replace(f'{{{k}}}',str(v))
            Path('README.md').write_text(txt)
            return 'README.md'
    return ''


@app.function
def build(
    nbs: str='notebooks',        # Directory containing notebook files
    out: str='src',              # Output directory for package
    doc_style: str='google',     # Documentation style (google/nbdev/unmodified)
    project_root: str='.',       # Root directory with pyproject.toml
) -> str:                        # Path to created package directory
    """Build installable package from marimo notebooks

    Scans notebooks, extracts exports, transforms docs, writes modules.
    Creates __init__.py and README.md. Returns package directory path.
    """
    res = scan(nbs,doc_style,project_root)
    name = res['meta']['__package_name__'].replace('-','_')

    pkg = Path(out)/name
    pkg.mkdir(parents=True,exist_ok=True)

    for m in res['mods']:
        if m['name']=='index' or not m['exp_names']: continue
        write_mod(m['name'],m['imports'],m['consts'],m['exports'],pkg/f"{m['name']}.py")

    write_init(name,res['meta'],res['mods'],pkg/'__init__.py')
    extract_readme(res['meta'],nbs)

    return str(pkg)


@app.function
def format_nbdev_signature(
    node: CodeNode,  # Node metadata
) -> str:            # nbdev signature
    """Generate nbdev-style function signature for documentation"""

    # Check if this is actually a class by looking at source
    is_class = node.src.lstrip().startswith(('@dataclass', 'class '))

    if is_class:
        # Class with attributes
        lines = []

        # Preserve decorators
        for line in node.src.splitlines():
            stripped = line.strip()
            if stripped.startswith('@'):
                lines.append(stripped)
            elif stripped.startswith('class '):
                lines.append(stripped.rstrip(':') + ':')
                break

        if node.docstring:
            lines.append('    """' + node.docstring.split('\n')[0])
            for doc_line in node.docstring.split('\n')[1:]:
                lines.append('    ' + doc_line if doc_line.strip() else '')
            lines.append('    """')

        # Add attributes WITH inline comments
        if node.params:
            for p in node.params:
                anno = f": {p.anno}" if p.anno else ""
                default = f" = {p.default}" if p.default else ""
                doc = f"  # {p.doc}" if p.doc else ""
                lines.append(f"    {p.name}{anno}{default}{doc}")

        return '\n'.join(lines)

    # FUNCTION - build signature with inline comments
    if not node.params and not node.ret_anno:
        return node.src  # No signature info, return as-is

    # Build function signature with inline comments
    lines = []

    # Handle async
    is_async = node.src.lstrip().startswith('async def')
    func_keyword = 'async def' if is_async else 'def'

    lines.append(f"{func_keyword} {node.name}(")

    # Add parameters with inline comments
    for i, p in enumerate(node.params):
        comma = ',' if i < len(node.params) - 1 else ''

        if p.is_vararg:
            anno = f": {p.anno}" if p.anno else ''
            doc = f"  # {p.doc}" if p.doc else ''
            lines.append(f"    *args{anno}{comma}{doc}")
        elif p.is_kwarg:
            anno = f": {p.anno}" if p.anno else ''
            doc = f"  # {p.doc}" if p.doc else ''
            lines.append(f"    **kwargs{anno}{comma}{doc}")
        else:
            anno = f": {p.anno}" if p.anno else ''
            default = f" = {p.default}" if p.default else ''
            doc = f"  # {p.doc}" if p.doc else ''
            lines.append(f"    {p.name}{anno}{default}{comma}{doc}")

    # Close signature with return annotation
    ret_anno = f" -> {node.ret_anno}" if node.ret_anno else ''
    ret_doc = f"  # {node.ret_doc}" if node.ret_doc else ''
    lines.append(f"){ret_anno}:{ret_doc}")

    # Add docstring
    if node.docstring:
        lines.append('    """' + node.docstring.split('\n')[0])
        for doc_line in node.docstring.split('\n')[1:]:
            lines.append('    ' + doc_line if doc_line.strip() else '')
        lines.append('    """')

    return '\n'.join(lines)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Build
    """)
    return


@app.cell
def _():
    build(out="src", doc_style="google")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Testing
    """)
    return


@app.cell(hide_code=True)
def _():
    def test_nb_name_strips_prefix():
        "Remove numeric prefix from notebook names"
        assert nb_name(Path('01_core.py')) == 'core'
        assert nb_name(Path('00_index.py')) == 'index'
        assert nb_name(Path('123_utils.py')) == 'utils'

    def test_nb_name_skips_hidden():
        "Hidden files return None"
        assert nb_name(Path('.hidden.py')) is None

    def test_nb_name_skips_tests():
        "Test files return None"
        assert nb_name(Path('test_core.py')) is None
        assert nb_name(Path('01_test_utils.py')) is None

    def test_nb_name_no_prefix():
        "Files without prefix work"
        assert nb_name(Path('core.py')) == 'core'

    def test_group_nodes_empty():
        "Empty list returns empty groups"
        grps = group_nodes([])
        assert all(grps[k] == [] for k in NodeKind)

    def test_group_nodes_by_kind():
        "Nodes grouped by their kind"
        nodes = [
            CodeNode(NodeKind.IMP, '', 'import os'),
            CodeNode(NodeKind.EXP, 'foo', 'def foo(): pass'),
            CodeNode(NodeKind.IMP, '', 'import sys'),
        ]
        grps = group_nodes(nodes)
        assert len(grps[NodeKind.IMP]) == 2
        assert len(grps[NodeKind.EXP]) == 1
        assert len(grps[NodeKind.CONST]) == 0

    def test_clean_removes_decorators():
        "Marimo decorators stripped from source"
        src = """@app.function
    def foo():
        return 1"""
        cleaned = __clean(src)
        assert '@app.function' not in cleaned
        assert 'def foo()' in cleaned

    def test_clean_preserves_body():
        "Function body unchanged"
        src = """@app.function
    def foo():
        return 1"""
        cleaned = __clean(src)
        assert 'return 1' in cleaned

    def test_is_export_detects_function():
        "Recognizes app.function decorator"
        dec = ast.parse('@app.function\ndef f(): pass').body[0].decorator_list[0]
        assert __is_export(dec)

    def test_is_export_detects_class():
        "Recognizes app.class_definition decorator"
        dec = ast.parse('@app.class_definition\nclass C: pass').body[0].decorator_list[0]
        assert __is_export(dec)

    def test_is_export_ignores_others():
        "Other decorators return False"
        dec = ast.parse('@cache\ndef f(): pass').body[0].decorator_list[0]
        assert not __is_export(dec)

    def test_classify_node_import():
        "Extract import statements"
        src = """with app.cell():
        import os
        import sys"""
        tree = ast.parse(src)
        nodes = classify_node(tree.body[0], src)
        assert len(nodes) == 2
        assert all(n.kind == NodeKind.IMP for n in nodes)

    def test_classify_node_const():
        "Extract private constants"
        src = """with app.cell():
        __private = 42"""
        tree = ast.parse(src)
        nodes = classify_node(tree.body[0], src)
        assert len(nodes) == 1
        assert nodes[0].kind == NodeKind.CONST
        assert nodes[0].name == '__private'

    def test_classify_node_skips_metadata():
        "Metadata dunder variables ignored"
        src = """with app.cell():
        __version__ = '1.0'"""
        tree = ast.parse(src)
        nodes = classify_node(tree.body[0], src)
        assert len(nodes) == 0

    def test_classify_node_export():
        "Extract exported functions"
        src = """@app.function
    def foo():
        return 1"""
        tree = ast.parse(src)
        nodes = classify_node(tree.body[0], src)
        assert len(nodes) == 1
        assert nodes[0].kind == NodeKind.EXP
        assert nodes[0].name == 'foo'

    def test_classify_node_skips_test_functions():
        "Test functions not exported"
        src = """@app.function
    def test_foo():
        pass"""
        tree = ast.parse(src)
        nodes = classify_node(tree.body[0], src)
        assert len(nodes) == 0




    def test_read_metadata_missing_file():
        "Raises error when pyproject.toml missing"
        try:
            read_metadata('/nonexistent/path')
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert 'not found' in str(e)

    def test_check_meta_missing_fields():
        "Validates required metadata fields"
        try:
            check_meta({'__version__': '1.0'})  # Missing name and description
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert '__package_name__' in str(e)

    def test_extract_signature_params():
        "Extract parameters with docs"
        src = """def foo(
        a: int, # first param
        b=0     # second param
    ):
        pass"""
        tree = ast.parse(src)
        params, _, _ = __extract_signature(tree.body[0], src, src)  # Pass src twice
        assert len(params) == 2
        assert params[0].name == 'a'
        assert params[0].anno == 'int'
        assert params[0].doc == 'first param'

    def test_extract_signature_return():
        "Extract return annotation and doc"
        src = """def foo() -> int: # the result
        pass"""
        tree = ast.parse(src)
        _, ret, _ = __extract_signature(tree.body[0], src, src)  # Pass src twice
        assert ret is not None
        assert ret[0] == 'int'
        assert ret[1] == 'the result'

    def test_extract_signature_no_annotations():
        "Works without type annotations"
        src = """def foo(a, b):
        pass"""
        tree = ast.parse(src)
        params, ret, _ = __extract_signature(tree.body[0], src, src)  # Pass src twice
        assert len(params) == 2
        assert params[0].anno is None
        assert ret is None

    def test_extract_signature_async():
        "Works with async functions"
        src = """async def fetch(url: str, # the url
                           ):
        pass"""
        tree = ast.parse(src)
        params, _, _ = __extract_signature(tree.body[0], src, src)  # Pass src twice
        assert len(params) == 1
        assert params[0].name == 'url'

    def test_extract_signature_class_init():
        "Extracts from class __init__"
        src = """class Foo:
        def __init__(self, x: int, # x value
                    ):
            pass"""
        tree = ast.parse(src)
        params, _, init_params = __extract_signature(tree.body[0], src, src)  # Pass src twice
        assert len(init_params) == 1  # 'self' skipped
        assert init_params[0].name == 'x'

    def test_extract_signature_class_no_init():
        "Class without __init__ returns empty"
        src = """class Foo:
        value = 42"""
        tree = ast.parse(src)
        params, ret, init_params = __extract_signature(tree.body[0], src, src)  # Pass src twice
        assert params == []
        assert ret is None
        assert init_params is None
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
