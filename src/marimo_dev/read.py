from m_dev.core import Kind, Param, Node
from pathlib import Path
import ast, re, tomllib

def inline_doc(
    ls:list[str], # source code lines
    ln:int,       # line number to search
    name:str,     # identifier name to match before comment
)->str:           # extracted inline comment or empty string
    "Extract inline comment following an identifier on a source line."
    if 0 < ln <= len(ls) and (m := re.search(rf'\b{re.escape(name)}\b.*?#\s*(.+)', ls[ln-1])): return m.group(1).strip()
    return ''

def parse_params(
    fn,            # function node to extract parameters from
    ls,            # source lines for inline doc extraction
)->list[Param]:    # list of parameter objects
    "Extract parameters from a function node with inline documentation."
    if not hasattr(fn, 'args'): return []
    args, defs = fn.args.args, fn.args.defaults
    pad = [None] * (len(args) - len(defs))
    return [Param(a.arg, ast.unparse(a.annotation) if a.annotation else None, ast.unparse(d) if d else None, inline_doc(ls, a.lineno, a.arg)) for a, d in zip(args, pad + defs) if a.arg not in ('self', 'cls')]

def parse_class_params(
    n:ast.ClassDef, # class node to extract params from
    ls:list,        # source lines for inline doc
)->list[Param]:     # list of class attribute parameters
    "Extract annotated class attributes as parameters."
    return [Param(t.id, ast.unparse(a.annotation) if a.annotation else None, None, inline_doc(ls, a.lineno, t.id))
            for a in n.body if isinstance(a, ast.AnnAssign) and isinstance((t := a.target), ast.Name)]

def parse_ret(
    fn,  # function node to parse return annotation from
    ls,  # source code lines
)->tuple[str,str]|None:  # tuple of (return type, inline doc) or None
    "Extract return type annotation and inline documentation from function node."
    if not fn.returns or isinstance(fn.returns, ast.Constant): return None
    return (ast.unparse(fn.returns), inline_doc(ls, fn.returns.lineno, '->') if hasattr(fn.returns, 'lineno') else '')

def src_with_decs(
    n,   # AST node with potential decorators
    ls,  # source code lines
)->str:  # source code including decorators
    "Extract source code including decorators from AST node."
    start = n.decorator_list[0].lineno - 1 if n.decorator_list else n.lineno - 1
    return '\n'.join(ls[start:n.end_lineno])

def is_export(
    d,   # decorator node to check
)->bool: # whether decorator marks node for export
    "Check if decorator marks a node for export."
    return ast.unparse(d.func if isinstance(d, ast.Call) else d) in {'app.function', 'app.class_definition'}

def parse_import(
    n:ast.AST, # AST node to check
    ls:list,   # source lines (unused but kept for consistent interface)
)->Node|None:  # Node if import statement, else None
    "Extract import node from AST."
    if isinstance(n, (ast.Import, ast.ImportFrom)): return Node(Kind.IMP, '', ast.unparse(n))

def parse_const(
    n:ast.AST, # AST node to check
    ls:list,   # source lines (unused)
)->Node|None:  # Node if constant assignment, else None
    "Extract constant definition (dunder-prefixed, non-dunder-suffixed)."
    if not isinstance(n, ast.Assign): return None
    for t in n.targets:
        if isinstance(t, ast.Name) and t.id.startswith('__') and not t.id.endswith('__'): return Node(Kind.CONST, t.id, ast.unparse(n))

def parse_export(
    n:ast.AST, # AST node to check
    ls:list,   # source lines for inline doc and decorators
)->Node|None:  # Node if exported function/class, else None
    "Extract exported function or class decorated with @app.function or @app.class_definition."
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): return None
    if not any(is_export(d) for d in n.decorator_list) or n.name.startswith('test_'): return None
    doc, src = ast.get_docstring(n) or '', src_with_decs(n, ls)
    if isinstance(n, ast.ClassDef): return Node(Kind.EXP, n.name, src, doc, parse_class_params(n, ls), None)
    return Node(Kind.EXP, n.name, src, doc, parse_params(n, ls), parse_ret(n, ls))

def parse_node(
    n:ast.AST, # AST node to parse
    src:str,   # full source code text
):             # yields Node objects for imports, constants, and exports
    "Extract importable nodes from an AST node."
    ls = src.splitlines()
    if isinstance(n, ast.With):
        for s in n.body:
            if (node := parse_import(s, ls)): yield node
            if (node := parse_const(s, ls)): yield node
    if (node := parse_export(n, ls)): yield node

def parse_file(
    p:str|Path, # path to Python file to parse
)->list[Node]:  # list of parsed nodes from the file
    "Parse a Python file and extract all nodes."
    src = Path(p).read_text()
    return [node for n in ast.parse(src).body for node in parse_node(n, src)]

def read_meta(
    root='.', # project root directory containing pyproject.toml
)->dict:      # metadata dict with name, version, desc, license, author
    "Read project metadata from pyproject.toml."
    with open(Path(root)/'pyproject.toml', 'rb') as f: p = tomllib.load(f).get('project', {})
    a = (p.get('authors') or [{}])[0]
    author = f"{a.get('name','')} <{a.get('email','')}>".strip(' <>') if isinstance(a, dict) else str(a)
    lic = p.get('license', {})
    return dict(name=p.get('name',''), version=p.get('version','0.0.0'), desc=p.get('description',''), license=lic.get('text','') if isinstance(lic, dict) else lic, author=author)

def nb_name(
    f:Path,   # file path to extract notebook name from
)->str|None:  # cleaned notebook name or None if should be skipped
    "Extract notebook name from file path, skipping hidden, test, and XX_ prefixed files."
    if f.name.startswith('.') or f.stem.startswith('XX_'): return None
    name = re.sub(r'^\d+_', '', f.stem)
    return None if name.startswith('test') else name

def scan(
    nbs='notebooks', # directory containing notebook .py files
    root='.',        # root directory containing pyproject.toml
):                   # tuple of (meta dict, list of (name, nodes) tuples)
    "Scan notebooks directory and extract metadata and module definitions."
    meta = read_meta(root)
    mods = [(name, parse_file(f)) for f in sorted(Path(nbs).glob('*.py')) if (name := nb_name(f))]
    return meta, mods
