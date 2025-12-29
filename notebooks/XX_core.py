import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    import re, ast, tomllib
    from pathlib import Path
    from dataclasses import dataclass
    from enum import Enum
    from fastcore.xml import to_xml
    from fasthtml.components import Div, Span, Code, P, Pre, A, Html, Head, Body, Script, Style, Form, Input, Button, H1, Aside, H3, Link



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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 2: Read metadata from pyproject.toml
    """)
    return


@app.function
def read_metadata(
    root='.'    # Location of pyproject.toml
) -> dict:      # Dict with package_name, version, description, license, author
    """Read package metadata from pyproject.toml"""
    with open(Path(root)/'pyproject.toml', 'rb') as f: data = tomllib.load(f)
    proj = data.get('project', {})
    authors = proj.get('authors', [])
    a = authors[0] if authors else {}
    author = f"{a.get('name','')} <{a.get('email','')}>" if isinstance(a, dict) and a.get('email') else (a.get('name','') if isinstance(a,dict) else str(a) if a else '')
    return dict(__package_name__=proj.get('name',''), __version__=proj.get('version','0.0.0'), __description__=proj.get('description',''),
                __license__=proj.get('license',{}).get('text','') if isinstance(proj.get('license'),dict) else proj.get('license',''), __author__=author)


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
# def __extract_class_attributes(
#     n: ast.ClassDef,  # Class AST node to extract from
#     full_src: str,    # FULL source (not segment) to get line numbers right
# ) -> list[Param]:     # List of extracted attribute Params
#     """Extract class attribute annotations with inline comments"""
#     attrs = []
#     full_lines = full_src.splitlines()

#     for node in n.body:
#         # AnnAssign is: name: Type = value
#         if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
#             name = node.target.id
#             anno = ast.unparse(node.annotation) if node.annotation else None
#             doc = ''

#             # Use absolute line number from AST (1-indexed)
#             if hasattr(node, 'lineno') and 0 < node.lineno <= len(full_lines):
#                 line = full_lines[node.lineno - 1]
#                 # Extract inline comment
#                 if m := re.search(r'#\s*(.+)', line):
#                     doc = m.group(1).strip()

#             attrs.append(Param(name, anno, default=None, doc=doc))

#     return attrs


def __extract_class_attributes(
    n: ast.ClassDef,  # Class AST node to extract from
    src: str,    # FULL source (not segment) to get line numbers right
) -> list[Param]:     # List of extracted attribute Params
    """Extract class attribute annotations with inline comments"""
    lines = src.splitlines()
    def get_attr(node):
        if not (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)): return None
        name, anno = node.target.id, ast.unparse(node.annotation) if node.annotation else None
        doc = (m.group(1).strip() if (m := re.search(r'#\s*(.+)', lines[node.lineno-1])) else '') if hasattr(node,'lineno') and 0 < node.lineno <= len(lines) else ''
        return Param(name, anno, default=None, doc=doc)
    return [a for node in n.body if (a := get_attr(node))]


@app.function
def __extract_signature(
    n: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,  # AST node
    src_seg: str,                                              # Source segment
    src: str,                                             # FULL source for line lookups
) -> tuple[list[Param], tuple[str, str] | None, list[Param] | None]:  # (params, return_info, init_params)
    """Extract params and return info from function/class """
    lines = src_seg.splitlines()
    if isinstance(n, ast.ClassDef):
        attrs = __extract_class_attributes(n, src)
        init = next((item for item in n.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == '__init__'), None)
        return (attrs, None, __extract_signature(init, src_seg, src)[0] if init else None)
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): return [], None, None
    
    total, defs = len(n.args.args), n.args.defaults
    defaults = [None] * (total - len(defs)) + [ast.unparse(d) if d else None for d in defs]
    
    params = [Param(a.arg, ast.unparse(a.annotation) if a.annotation else None, defaults[i] if i < len(defaults) else None,
              __get_inline_comment(src, a.lineno, rf'\b{re.escape(a.arg)}\b')) for i,a in enumerate(n.args.args) if a.arg not in ('self','cls')]
    if n.args.vararg: params.append(Param('*args', ast.unparse(n.args.vararg.annotation) if n.args.vararg.annotation else None,
                                          doc=__get_inline_comment(src, n.args.vararg.lineno or n.lineno, r'\*args'), is_vararg=True))
    if n.args.kwarg: params.append(Param('**kwargs', ast.unparse(n.args.kwarg.annotation) if n.args.kwarg.annotation else None,
                                         doc=__get_inline_comment(src, n.args.kwarg.lineno or n.lineno, r'\*\*kwargs'), is_kwarg=True))
    
    ret = None
    if n.returns and not isinstance(n.returns, ast.Constant):
        ret_doc = ''
        if hasattr(n.returns, 'lineno'):
            ret_line = src.splitlines()[n.returns.lineno - 1]
            if '->' in ret_line and '#' in ret_line and (m := re.search(r'#\s*(.+)', ret_line.split('->',1)[1])): ret_doc = m.group(1).strip()
        ret = (ast.unparse(n.returns), ret_doc)
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
    if isinstance(n, ast.With):
        imps = [CodeNode(NodeKind.IMP, '', ast.unparse(s)) for s in n.body if isinstance(s, (ast.Import, ast.ImportFrom))]
        consts = [CodeNode(NodeKind.CONST, t.id, ast.unparse(s)) for s in n.body if isinstance(s, ast.Assign) 
                  for t in s.targets if isinstance(t, ast.Name) and t.id.startswith('__') and not t.id.endswith('__')]
        return imps + consts
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        if any(__is_export(d) for d in n.decorator_list) and not n.name.startswith('test_'):
            src_seg = __get_source_with_decorators(n, src)
            if src_seg:
                params, ret, init_params = __extract_signature(n, src_seg, src)
                return [CodeNode(NodeKind.EXP, n.name, src_seg, params=params, ret_anno=ret[0] if ret else None,
                                 ret_doc=ret[1] if ret else '', docstring=ast.get_docstring(n) or '', init_params=init_params)]
    return []


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
def __node_2_docments(node):
    is_class, is_async = node.src.lstrip().startswith(('@dataclass','class ')), node.src.lstrip().startswith('async def')
    if is_class:
        lines = [l.strip() for l in node.src.splitlines() if l.strip().startswith('@')]
        lines += [next(l.strip().rstrip(':')+':' for l in node.src.splitlines() if l.strip().startswith('class '))]
        if node.docstring: lines.append(f'    """{node.docstring}"""')
        lines += [f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}{f'  # {p.doc}' if p.doc else ''}" for p in (node.params or [])]
        return '\n'.join(lines)
    if not node.params and not node.ret_anno: return node.src
    kw = "async def" if is_async else "def"
    params = [f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}{',' if i < len(node.params)-1 else ''}{f'  # {p.doc}' if p.doc else ''}" 
              if not p.is_vararg and not p.is_kwarg else f"    {'*args' if p.is_vararg else '**kwargs'}{f': {p.anno}' if p.anno else ''}{',' if i < len(node.params)-1 else ''}{f'  # {p.doc}' if p.doc else ''}"
              for i,p in enumerate(node.params or [])]
    sig = [f"{kw} {node.name}("] + params + [f"){f' -> {node.ret_anno}' if node.ret_anno else ''}:{f'  # {node.ret_doc}' if node.ret_doc else ''}"]
    if node.docstring: sig.append(f'    """{node.docstring}"""')
    return '\n'.join(sig)


@app.function
def transform_src(
    src: str,         # Source code to transform
    style: str,   # Style to transform to ('google', 'docments', 'unmodified')
    node: CodeNode,   # CodeNode with pre-extracted metadata
) -> str:             # Transformed source code
    """Apply doc_style transformation using pre-extracted node metadata"""
    cleaned = __clean(src)
    if style == 'google': return __node_2_google(cleaned, node)
    if style == 'nbdev': return __node_2_docments(node)
    return cleaned


@app.function
def __fmt_param(p):
    if p.is_vararg: return f"    *args: {p.doc or 'Variable length argument list.'}"
    if p.is_kwarg: return f"    **kwargs: {p.doc or 'Arbitrary keyword arguments.'}"
    typ = f" ({p.anno})" if p.anno else ""
    default = f" (default: {p.default})" if p.default else ""
    return f"    {p.name}{typ}{default}: {p.doc or 'TODO'}"


@app.function
def __node_2_google(src, node):
    tree = ast.parse(src)
    fn = tree.body[0]
    is_class = isinstance(fn, ast.ClassDef)
    
    doc = ['"""'] + (node.docstring.strip().split('\n') + [''] if node.docstring else [])
    if is_class and node.params: doc += ['Attributes:'] + [__fmt_param(p) for p in node.params] + ['']
    if is_class and node.init_params: doc += ['Args:'] + [__fmt_param(p) for p in node.init_params] + ['']
    if not is_class and node.params: doc += ['Args:'] + [__fmt_param(p) for p in node.params] + ['']
    if not is_class and (node.ret_anno or node.ret_doc): doc += ['Returns:', f"    {node.ret_anno + ': ' if node.ret_anno else ''}{node.ret_doc or 'The return value.'}", '']
    doc.append('"""')
    
    lines = src.splitlines()
    decs = [l for l in lines if l.lstrip().startswith('@')]
    
    if is_class:
        cls_idx = next(i for i,l in enumerate(lines) if l.lstrip().startswith('class '))
        indent = ' ' * (len(lines[cls_idx]) - len(lines[cls_idx].lstrip()) + 4)
        body_start = cls_idx + 1
        if body_start < len(lines) and lines[body_start].strip().startswith(('"""', "'''")):
            q = '"""' if '"""' in lines[body_start] else "'''"
            while body_start < len(lines) and not lines[body_start].strip().endswith(q): body_start += 1
            body_start += 1
        body = [re.sub(r'\s*#.*$', '', l).rstrip() if ':' in l and '#' in l else l for l in lines[body_start:]]
        return '\n'.join(decs + [lines[cls_idx]] + [indent + d if d else '' for d in doc] + body)
    
    sig_end = fn.body[0].lineno - 1 if fn.body else len(lines)
    sig = ' '.join(re.sub(r'\s*#.*$', '', l).rstrip() for l in lines[fn.lineno-1:sig_end] if l.strip())
    sig = re.sub(r'\s+', ' ', re.sub(r'\s*([:\=\-\>])\s*', lambda m: ': ' if m.group(1)==':' else '=' if m.group(1)=='=' else ' -> ', sig)).rstrip(': ')
    
    body_start = fn.body[0].lineno - 1 if fn.body else len(lines)
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant):
        body_start = fn.body[0].end_lineno
    body = '\n'.join(lines[body_start:])
    
    docstr = '\n'.join('    ' + d if d else '' for d in doc)
    return '\n'.join(filter(None, ['\n'.join(decs) if decs else None, f"{sig}:\n{docstr}\n{body}"]))


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 6: Extraction
    """)
    return


@app.function
def __extract(
    p: Path | str,    # Notebook path
    style: str,       # Doc style
) -> dict:            # Extracted content
    """find content in notebook to extract"""
    src = Path(p).read_text()
    nodes = [n for node in ast.parse(src).body for n in classify_node(node, src)]
    groups = {k: [n for n in nodes if n.kind == k] for k in NodeKind}
    return dict(imports=[n.src for n in groups[NodeKind.IMP]], exports=[transform_src(n.src, style, n) for n in groups[NodeKind.EXP]],
                exp_names=[n.name for n in groups[NodeKind.EXP]], consts=[n.src for n in groups[NodeKind.CONST]])


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
    Development notebooks are prefixed via XX_ and will be left out.
    """
    if f.name.startswith('.'): return None
    name = re.sub(r'^\d+_','',f.stem)
    if name.startswith('test') or name.startswith('XX_'): return None
    return name


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### STEP 8: Main scanning logic
    """)
    return


@app.function
def scan(
    nbs: str='notebooks',        # Directory containing notebook files
    doc_style: str='inline',     # Documentation style for exports
    project_root: str='.',       # Root directory with pyproject.toml
) -> dict:                 # Dict with meta and mods
    "Scan notebooks and read metadata from pyproject.toml"
    meta = read_metadata(project_root)
    p = Path(nbs)
    files = [(f, name) for f in sorted(p.glob('*.py')) if (name := nb_name(f))]
    mods = [{'name': name, **__extract(f, doc_style)} for f, name in files]
    return {'meta': meta, 'mods': mods}


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
def build(nbs: str='notebooks', out: str='src', doc_style: str='inline', project_root: str='.') -> str:
    res = scan(nbs, doc_style, project_root)
    name = res['meta']['__package_name__'].replace('-', '_')
    pkg = Path(out)/name
    pkg.mkdir(parents=True, exist_ok=True)
    for m in res['mods']:
        if m['name'] == 'index' or not m['exp_names']: continue
        write_mod(m['name'], m['imports'], m['consts'], m['exports'], pkg/f"{m['name']}.py")
    write_init(name, res['meta'], res['mods'], pkg/'__init__.py')
    all_nodes = []
    for f in sorted(Path(nbs).glob('*.py')):
        if n := nb_name(f):
            src = f.read_text()
            tree = ast.parse(src)
            for node in tree.body: all_nodes.extend(classify_node(node, src))
    export_nodes = [n for n in all_nodes if n.kind == NodeKind.EXP]
    if export_nodes:
        write_docs(res['meta']['__package_name__'], res['meta']['__description__'], export_nodes)
        write_llms_txt(res['meta'], export_nodes)
    return str(pkg)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Documents
    """)
    return


@app.function
def doc_card(
    node: CodeNode,  # Node with function/class metadata
    idx: int,        # Unique index for signal names
):
    "Generate HTML card for a single function/class with Datastar search integration"
    searchable = f"{node.name} {node.docstring} {' '.join(p.name + ' ' + (p.doc or '') for p in (node.params or []))}".replace('\n', ' ').replace("'", "\\'")
    match_sig = f"matchCount{idx}"
    show_sig = f"_show{idx}"
    
    is_async = node.src.lstrip().startswith('async def')
    is_class = node.src.lstrip().startswith(('@dataclass','class'))
    
    if is_class:
        sig_parts = [f"class {node.name}:"]
        if node.docstring: sig_parts.append(f'    """{node.docstring}"""')
        if node.params:
            for p in node.params:
                anno = f": {p.anno}" if p.anno else ""
                default = f" = {p.default}" if p.default else ""
                sig_parts.append(f"    {p.name}{anno}{default}")
    else:
        params_str = ', '.join([f"{p.name}: {p.anno}" + (f"={p.default}" if p.default else "") if p.anno else p.name + (f"={p.default}" if p.default else "") for p in (node.params or [])])
        ret_str = f" -> {node.ret_anno}" if node.ret_anno else ""
        func_kw = "async def" if is_async else "def"
        sig_parts = [f"{func_kw} {node.name}({params_str}){ret_str}:"]
        if node.docstring: sig_parts.append(f'    """{node.docstring}"""')
    
    sig_display = '\n'.join(sig_parts)
    
    return Div(
        Span(cls="match-badge", **{"data-show": f"$tags.length > 0 || $search.trim().length > 0", "data-text": f"${match_sig}"}),
        Div(Code(node.name), cls="attribute-name"),
        Div(
            Pre(Code(sig_display, cls="language-python line-numbers"), style="max-width:160ch; overflow-x:auto; white-space:pre", **{"data-show": f"!${show_sig}"}),
            Pre(Code(node.src, cls="language-python line-numbers"), style="max-width:160ch; overflow-x:auto; white-space:pre", **{"data-show": f"${show_sig}"}),
            Button("Show full implementation", **{"data-on:click": f"${show_sig} = true", "data-show": f"!${show_sig}"}),
            Button("Show signature only", **{"data-on:click": f"${show_sig} = false", "data-show": f"${show_sig}"}),
            cls="description"
        ),
        id=node.name, cls="attribute",
        **{"data-signals": f"{{searchable{idx}: '{searchable}', {match_sig}: 0, {show_sig}: false}}", "data-effect": f"${match_sig} = [...$tags, $search.trim()].filter(tag => tag.length > 0 && $searchable{idx}.toLowerCase().includes(tag.toLowerCase())).length", "data-show": f"($tags.length === 0 && $search.trim().length === 0) || ${match_sig} > 0", "data-style:order": f"($tags.length === 0 && $search.trim().length === 0) ? 0 : -${match_sig}"}
    )


@app.function
def nav_item(
    node: CodeNode,  # Node with function/class metadata
    idx: int,        # Unique index matching doc_card
):
    "Generate sidenav link with match count badge"
    match_sig = f"matchCount{idx}"
    return A(
        Span(node.name),
        Span(cls="nav-badge", **{"data-show": f"$tags.length > 0 || $search.trim().length > 0", "data-text": f"${match_sig}"}),
        href=f"#{node.name}", cls="nav-item",
        **{"data-class:disabled": f"($tags.length > 0 || $search.trim().length > 0) && ${match_sig} === 0"}
    )


@app.function
def docs_page(
    title: str,            # Page title
    subtitle: str,         # Page subtitle
    nodes: list[CodeNode], # List of functions/classes to document
):
    "Generate complete Datastar-powered documentation page"
    return Html(
        Head(
            Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"),
            Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"),
            Script(src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"),
            Script(src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"),
            Script("hljs.highlightAll();"),
            Style("*{scrollbar-gutter:stable}body{font-family:sans-serif;max-width:1400px;margin:1rem auto;padding:0 1rem;line-height:1.5}.header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;gap:2rem}.search-section{position:fixed;top:1rem;right:1rem;z-index:100;display:flex;gap:0.5rem;align-items:center;background:white;padding:0.75rem;border-radius:0.5rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1)}.content-wrapper{display:grid;grid-template-columns:250px 1fr;gap:2rem}.sidenav{position:sticky;top:1rem;height:fit-content;max-height:calc(100vh - 2rem);overflow-y:auto;padding:1rem;background:#f9fafb;border-radius:0.375rem;border:1px solid #e5e7eb}.nav-item{display:flex;align-items:center;justify-content:space-between;padding:0.5rem;margin-bottom:0.25rem;border-radius:0.25rem;font-size:0.875rem;color:#374151;text-decoration:none;transition:all 0.15s}.nav-item:hover{background:#e5e7eb}.nav-item.disabled{opacity:0.4;cursor:not-allowed;pointer-events:none}.nav-badge{background:#3b82f6;color:white;padding:0.125rem 0.5rem;border-radius:9999px;font-size:0.7rem;font-weight:600;min-width:1.5rem;text-align:center}.attribute{position:relative;padding:1rem;border:1px solid #e5e7eb;border-radius:0.375rem;background:#fff;scroll-margin-top:3rem;transition:order 0.5s cubic-bezier(0.4,0,0.2,1),transform 0.5s cubic-bezier(0.4,0,0.2,1),opacity 0.3s ease-in-out}.attribute:hover{box-shadow:0 2px 4px rgba(0,0,0,0.1)}.match-badge{position:absolute;top:1rem;right:1rem;background:#3b82f6;color:white;padding:0.25rem 0.75rem;border-radius:9999px;font-size:0.8rem;font-weight:600}.attribute-name{font-weight:bold;font-size:1.25rem;margin-bottom:0.25rem;color:#1e40af}.description{margin:0.5rem 0;color:#374151;font-size:0.9rem}input{padding:0.625rem;border:1px solid #d1d5db;border-radius:0.375rem;min-width:250px;font-size:0.95rem}input:focus{outline:2px solid #3b82f6;outline-offset:0}button{padding:0.625rem 1.25rem;background:#3b82f6;color:white;border:none;border-radius:0.375rem;cursor:pointer;font-size:0.95rem;transition:background 0.15s;white-space:nowrap}button:hover{background:#2563eb}button.clear-btn{background:#dc2626}button.clear-btn:hover{background:#b91c1c}code{background:#f3f4f6;color:#1f2937;padding:0.125rem 0.375rem;border-radius:0.25rem;font-size:0.85rem;font-family:monospace}pre{border-radius:0.375rem;overflow-x:auto;font-size:0.8rem;margin:0.375rem 0}pre code{background:transparent;color:#f9fafb;padding:0}")
        ),
        Body(
            Form(Input(type="text", placeholder="Live Search ...(enter to add tag)", **{"data-bind": "search"}), Button("Add Tag", type="submit"), Button("Clear All", cls="clear-btn", type="button", **{"data-on:click": "$tags = [], $search = ''"}), cls="search-section", **{"data-on:submit__prevent": "$search.trim() ? ($tags = [...$tags, $search.trim()], $search = '') : null"}),
            Div(Div(H1(title), P(subtitle, cls="subtitle"), cls="title-section"), cls="header"),
            Div(Aside(H3("Functions"), *[nav_item(n, i) for i, n in enumerate(nodes)], cls="sidenav"), Div(Div(*[doc_card(n, i) for i, n in enumerate(nodes)], cls="attributes"), cls="main-content"), cls="content-wrapper"),
            **{"data-signals": '{"search": "", "tags": []}'}
        ),
        style="scroll-behavior:smooth"
    )


@app.function
def write_docs(
    title: str,            # Page title
    subtitle: str,         # Page subtitle  
    nodes: list[CodeNode], # List of functions/classes to document
    out: str='docs',       # Output directory
):
    "Write Datastar documentation page to index.html"
    Path(out).mkdir(exist_ok=True)
    html = to_xml(docs_page(title, subtitle, nodes))
    (Path(out)/'index.html').write_text(f'<!doctype html>\n{html}')


@app.function
def format_sig(node: CodeNode) -> str:
    "Generate concise function/class signature for LLM context"
    is_class = node.src.lstrip().startswith(('@dataclass', 'class '))
    if is_class:
        lines = []
        for line in node.src.splitlines():
            stripped = line.strip()
            if stripped.startswith('@'): lines.append(stripped)
            elif stripped.startswith('class '): lines.append(stripped.rstrip(':') + ':'); break
        if node.docstring: lines.append(f'    """{node.docstring}"""')
        if node.params:
            for p in node.params:
                anno = f": {p.anno}" if p.anno else ""
                default = f" = {p.default}" if p.default else ""
                doc = f"  # {p.doc}" if p.doc else ""
                lines.append(f"    {p.name}{anno}{default}{doc}")
        return '\n'.join(lines)
    if not node.params and not node.ret_anno: return node.src
    lines = []
    is_async = node.src.lstrip().startswith('async def')
    lines.append(f"{'async def' if is_async else 'def'} {node.name}(")
    for i, p in enumerate(node.params):
        comma = ',' if i < len(node.params) - 1 else ''
        if p.is_vararg: lines.append(f"    *args{f': {p.anno}' if p.anno else ''}{comma}{f'  # {p.doc}' if p.doc else ''}")
        elif p.is_kwarg: lines.append(f"    **kwargs{f': {p.anno}' if p.anno else ''}{comma}{f'  # {p.doc}' if p.doc else ''}")
        else: lines.append(f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}{comma}{f'  # {p.doc}' if p.doc else ''}")
    lines.append(f"){f' -> {node.ret_anno}' if node.ret_anno else ''}:{f'  # {node.ret_doc}' if node.ret_doc else ''}")
    if node.docstring: lines.append(f'    """{node.docstring}"""')
    return '\n'.join(lines)


@app.function
def write_llms_txt(
    meta: dict,  # Package metadata from pyproject.toml
    nodes: list[CodeNode],  # List of exported functions/classes
    out: str='docs'  # Output directory
):  # Writes llms.txt file
    "Write llms.txt with package overview and API signatures"
    name, desc, ver = meta['__package_name__'], meta.get('__description__', ''), meta.get('__version__', '')
    sigs = '\n\n'.join(format_sig(n) for n in nodes if not n.name.startswith('__'))
    lines = [f'# {name}', '', f'> {desc}', '', f'Version: {ver}', '', '## API', '', '```python', sigs, '```']
    Path(out).mkdir(exist_ok=True)
    (Path(out)/'llms.txt').write_text('\n'.join(lines))


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Build
    """)
    return


@app.cell
def _():
    build(out="src2", doc_style="google")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Publish
    """)
    return


@app.function
def publish(
    test: bool = True,  # Use Test PyPI if True, real PyPI if False
):
    """Build and publish package to PyPI

    Looks for ~/.pypirc for credentials, otherwise prompts.
    """
    import subprocess
    import configparser
    from pathlib import Path

    # Build the package
    print("Building package...")
    subprocess.run(['uv', 'build'], check=True)

    # Check for .pypirc
    pypirc = Path.home() / '.pypirc'
    cmd = ['uv', 'publish']

    if test:
        cmd.extend(['--publish-url', 'https://test.pypi.org/legacy/'])
        section = 'testpypi'
    else:
        cmd.extend(['--publish-url', 'https://upload.pypi.org/legacy/'])
        section = 'pypi'

    if pypirc.exists():
        config = configparser.ConfigParser()
        config.read(pypirc)
        if section in config:
            username = config[section].get('username', '__token__')
            password = config[section].get('password', '')
            cmd.extend(['--username', username, '--password', password])

    print(f"Publishing to {'Test ' if test else ''}PyPI...")
    subprocess.run(cmd, check=True)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Preview
    """)
    return


@app.function
def preview(
    port: int=8000,  # Port to serve on
    docs_dir: str='docs',  # Directory containing index.html
):
    "Serve documentation on local server in background thread"
    import http.server, socketserver, threading
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs): super().__init__(*args, directory=docs_dir, **kwargs)
    
    def serve():
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Serving docs at http://localhost:{port}")
            httpd.serve_forever()
    
    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    return f"http://localhost:{port}"


@app.cell
def _():
    # preview()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Testing
    """)
    return


@app.cell
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
