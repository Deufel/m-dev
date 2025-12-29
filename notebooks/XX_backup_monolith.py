import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    import ast, re, tomllib, json
    from pathlib import Path
    #from fastcore.xml import to_xml
    #from fasthtml.components import Div, Span, Code, P, Pre, A, Html, Head, Body, Script, Style, Form, Input, Button, H1, Aside, H3, Link
    from enum import Enum
    from dataclasses import dataclass, field


@app.class_definition
class Kind(Enum):
    "Types of nodes in parsed code"
    IMP='import'    # Import statement
    CONST='const'   # Constant definition
    EXP='export'


@app.class_definition
@dataclass
class Param:
    name: str                # parameter name
    anno: str|None = None    # type annotation
    default: str|None = None # default value
    doc: str = ''


@app.class_definition
@dataclass 
class Node:
    "A parsed code node representing an import, constant, or exported function/class."
    kind: Kind       # type of node (import/const/export)
    name: str        # identifier name
    src: str         # source code
    doc: str = ''    # docstring text
    params: list[Param] = field(default_factory=list)    # function/class parameters
    ret: tuple[str,str]|None = None


@app.function
def inline_doc(
    ls:list[str], # source code lines
    ln:int,       # line number to search
    name:str,     # identifier name to match before comment
)->str:           # extracted inline comment or empty string
    "Extract inline comment following an identifier on a source line."
    if 0 < ln <= len(ls) and (m := re.search(rf'\b{re.escape(name)}\b.*?#\s*(.+)', ls[ln-1])): return m.group(1).strip()
    return ''


@app.function
def parse_params(
    fn,            # function node to extract parameters from
    ls,            # source lines for inline doc extraction
)->list[Param]:    # list of parameter objects
    "Extract parameters from a function node with inline documentation."
    if not hasattr(fn, 'args'): return []
    args, defs = fn.args.args, fn.args.defaults
    pad = [None] * (len(args) - len(defs))
    return [Param(a.arg, ast.unparse(a.annotation) if a.annotation else None, ast.unparse(d) if d else None, inline_doc(ls, a.lineno, a.arg)) for a, d in zip(args, pad + defs) if a.arg not in ('self', 'cls')]


@app.function
def parse_class_params(
    n:ast.ClassDef, # class node to extract params from
    ls:list,        # source lines for inline doc
)->list[Param]:     # list of class attribute parameters
    "Extract annotated class attributes as parameters."
    return [Param(t.id, ast.unparse(a.annotation) if a.annotation else None, None, inline_doc(ls, a.lineno, t.id))
            for a in n.body if isinstance(a, ast.AnnAssign) and isinstance((t := a.target), ast.Name)]


@app.function
def parse_ret(
    fn,  # function node to parse return annotation from
    ls,  # source code lines
)->tuple[str,str]|None:  # tuple of (return type, inline doc) or None
    "Extract return type annotation and inline documentation from function node."
    if not fn.returns or isinstance(fn.returns, ast.Constant): return None
    return (ast.unparse(fn.returns), inline_doc(ls, fn.returns.lineno, '->') if hasattr(fn.returns, 'lineno') else '')


@app.function
def src_with_decs(
    n,   # AST node with potential decorators
    ls,  # source code lines
)->str:  # source code including decorators
    "Extract source code including decorators from AST node."
    start = n.decorator_list[0].lineno - 1 if n.decorator_list else n.lineno - 1
    return '\n'.join(ls[start:n.end_lineno])


@app.function
def is_export(
    d,   # decorator node to check
)->bool: # whether decorator marks node for export
    "Check if decorator marks a node for export."
    return ast.unparse(d.func if isinstance(d, ast.Call) else d) in {'app.function', 'app.class_definition'}


@app.function
def parse_import(
    n:ast.AST, # AST node to check
    ls:list,   # source lines (unused but kept for consistent interface)
)->Node|None:  # Node if import statement, else None
    "Extract import node from AST."
    if isinstance(n, (ast.Import, ast.ImportFrom)): return Node(Kind.IMP, '', ast.unparse(n))


@app.function
def parse_const(
    n:ast.AST, # AST node to check
    ls:list,   # source lines (unused)
)->Node|None:  # Node if constant assignment, else None
    "Extract constant definition (dunder-prefixed, non-dunder-suffixed)."
    if not isinstance(n, ast.Assign): return None
    for t in n.targets:
        if isinstance(t, ast.Name) and t.id.startswith('__') and not t.id.endswith('__'): return Node(Kind.CONST, t.id, ast.unparse(n))


@app.function
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


@app.function
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


@app.function
def parse_file(
    p:str|Path, # path to Python file to parse
)->list[Node]:  # list of parsed nodes from the file
    "Parse a Python file and extract all nodes."
    src = Path(p).read_text()
    return [node for n in ast.parse(src).body for node in parse_node(n, src)]


@app.function
def clean(
    src:str, # source code to clean
)->str:      # cleaned source code
    "Remove decorator lines from source code."
    return '\n'.join(l for l in src.splitlines() if not l.strip().startswith(('@app.function', '@app.class_definition')))


@app.cell
def _(mo):
    mo.md(r"""
    ## Part 2
    """)
    return


@app.function
def read_meta(
    root='.', # project root directory containing pyproject.toml
)->dict:      # metadata dict with name, version, desc, license, author
    "Read project metadata from pyproject.toml."
    with open(Path(root)/'pyproject.toml', 'rb') as f: p = tomllib.load(f).get('project', {})
    a = (p.get('authors') or [{}])[0]
    author = f"{a.get('name','')} <{a.get('email','')}>".strip(' <>') if isinstance(a, dict) else str(a)
    lic = p.get('license', {})
    return dict(name=p.get('name',''), version=p.get('version','0.0.0'), desc=p.get('description',''), license=lic.get('text','') if isinstance(lic, dict) else lic, author=author)


@app.function
def nb_name(
    f:Path,   # file path to extract notebook name from
)->str|None:  # cleaned notebook name or None if should be skipped
    "Extract notebook name from file path, skipping hidden, test, and XX_ prefixed files."
    if f.name.startswith('.') or f.stem.startswith('XX_'): return None
    name = re.sub(r'^\d+_', '', f.stem)
    return None if name.startswith('test') else name


@app.function
def scan(
    nbs='notebooks', # directory containing notebook .py files
    root='.',        # root directory containing pyproject.toml
):                   # tuple of (meta dict, list of (name, nodes) tuples)
    "Scan notebooks directory and extract metadata and module definitions."
    meta = read_meta(root)
    mods = [(name, parse_file(f)) for f in sorted(Path(nbs).glob('*.py')) if (name := nb_name(f))]
    return meta, mods


@app.function
def write(
    p:str,      # path to write to
    *parts:str, # content parts to join with blank lines
):
    "Write parts to file, filtering None values and joining with blank lines."
    Path(p).write_text('\n\n'.join(filter(None, parts)) + '\n')


@app.function
def write_mod(
    path,           # output file path
    nodes:list,     # list of Node objects to write
):
    "Write module file with imports, constants, and exports."
    g = {k: [n for n in nodes if n.kind == k] for k in Kind}
    parts = ['\n'.join(n.src for n in g[Kind.IMP]), '\n'.join(n.src for n in g[Kind.CONST]), '\n\n'.join(clean(n.src) for n in g[Kind.EXP])]
    write(path, *parts)


@app.function
def write_init(
    path:str|Path, # path to write __init__.py file
    meta:dict,     # metadata dict with desc, version, author
    mods:list,     # list of (name, nodes) tuples
):
    "Generate and write __init__.py file with metadata and exports."
    lines = [f'"""{meta["desc"]}"""', f"__version__ = '{meta['version']}'"]
    if meta['author']: lines.append(f"__author__ = '{meta['author'].split('<')[0].strip()}'")
    exports = []
    for name, nodes in mods:
        if name.startswith('00_'): continue
        pub = [n.name for n in nodes if n.kind == Kind.EXP and not n.name.startswith('__')]
        if pub: lines.append(f"from .{name} import {', '.join(pub)}"); exports.extend(pub)
    if exports: lines.append('__all__ = [\n' + '\n'.join(f'    "{n}",' for n in sorted(exports)) + '\n]')
    write(path, '\n'.join(lines))


@app.function
def cls_sig(
    n:Node,           # the node to generate signature for
    dataclass=False,  # whether to include @dataclass decorator
)->str:               # formatted class signature
    "Generate a class signature string."
    header = f"@dataclass\nclass {n.name}:" if dataclass else f"class {n.name}:"
    lines = [header]
    if n.doc: lines.append(f'    """{n.doc}"""')
    lines.extend(f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}" for p in n.params)
    return '\n'.join(lines)


@app.function
def fn_sig(
    n:Node,         # the node to generate signature for
    is_async=False, # whether function is async
)->str:             # formatted function signature
    "Generate a function signature string."
    ps = ', '.join(f"{p.name}{f': {p.anno}' if p.anno else ''}{f'={p.default}' if p.default else ''}" for p in n.params)
    ret = f" -> {n.ret[0]}" if n.ret else ""
    s = f"{'async def' if is_async else 'def'} {n.name}({ps}){ret}:"
    return f"{s}\n    \"\"\"{n.doc}\"\"\"" if n.doc else s


@app.function
def sig(
    n:Node, # the node to generate signature for
)->str:     # formatted signature string
    "Generate a signature string for a class or function node."
    src = n.src.lstrip()
    if src.startswith('@dataclass'): return cls_sig(n, dataclass=True)
    if src.startswith('class '): return cls_sig(n)
    return fn_sig(n, is_async=src.startswith('async def'))


@app.function
def write_llms(
    meta:dict,    # project metadata from pyproject.toml
    nodes:list,   # list of Node objects to document
    out='docs',   # output directory path
):
    "Write API signatures to llms.txt file for LLM consumption."
    sigs = '\n\n'.join(sig(n) for n in nodes if not n.name.startswith('__'))
    content = f"# {meta['name']}\n\n> {meta['desc']}\n\nVersion: {meta['version']}\n\n## API\n\n```python\n{sigs}\n```"
    Path(out).mkdir(exist_ok=True)
    (Path(out)/'llms.txt').write_text(content)


@app.function
def build(
    nbs='notebooks', # directory containing notebook files
    out='src',       # output directory for built package
    root='.',        # root directory containing pyproject.toml
)->str:              # path to built package
    "Build a Python package from notebooks."
    meta, mods = scan(nbs, root)
    pkg = Path(out) / meta['name'].replace('-', '_')
    pkg.mkdir(parents=True, exist_ok=True)
    for name, nodes in mods:
        if name != 'index' and any(n.kind == Kind.EXP for n in nodes): write_mod(pkg/f'{name}.py', nodes)
    write_init(pkg/'__init__.py', meta, mods)
    all_exp = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
    if all_exp: write_llms(meta, all_exp)
    return str(pkg)


@app.cell
def _():
    build(out="src")
    return


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
