# /// script
# dependencies = ["fastcore", "fasthtml", "marimo"]
# ///


import ast, re, tomllib, json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
import ast, re, tomllib
import ast, re
import ast, re, os
import marimo as mo
from functools import partial
from fastcore.xml import Span, Code, Li, Article, Div, Ul, P, FT, to_xml, Pre, Link, A, Iframe, Button, H1, H2, H3, Nav, Aside, Header, Input, NotStr, Strong, Main
from fasthtml.components import ft, Html, Head, Script, Body, show, Style, Title
import ast, shutil, re, sys
import subprocess, configparser, shutil
import sys, subprocess

icons = {'home': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-house-icon lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>', 'pypi': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-blocks-icon lucide-blocks"><path d="M10 22V7a1 1 0 0 0-1-1H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5a1 1 0 0 0-1-1H2"/><rect x="14" y="2" width="8" height="8" rx="1"/></svg>', 'menu': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu-icon lucide-menu"><path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg>', 'x': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x-icon lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>', 'github': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-github-icon lucide-github"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>', 'code': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-code-icon lucide-code"><path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/></svg>', 'info': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info-icon lucide-info"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>', 'calendar': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar1-icon lucide-calendar-1"><path d="M11 14h1v4"/><path d="M16 2v4"/><path d="M3 10h18"/><path d="M8 2v4"/><rect x="3" y="4" width="18" height="18" rx="2"/></svg>', 'circle-x': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-x-icon lucide-circle-x"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>', 'external-link': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link-icon lucide-external-link"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>'}
COLORS = {'keyword': '#c792ea', 'string': '#c3e88d', 'builtin': '#82aaff', 'decorator': '#f78c6c', 'comment': '#546e7a', 'number': '#f78c6c', 'punctuation': '#89ddff', 'defname': '#82aaff', 'classname': '#ffcb6b', 'operator': '#89ddff', 'call': '#82aaff', 'fstring': '#c3e88d', 'type': '#ffcb6b'}
IMPORT_TO_PYPI = {'bs4': 'beautifulsoup4', 'PIL': 'pillow', 'cv2': 'opencv-python', 'sklearn': 'scikit-learn', 'yaml': 'pyyaml'}
CREDENTIALS = {'testpypi': {'file': '~/.pypirc', 'section': 'testpypi', 'key_field': 'password', 'prefix': 'pypi-', 'url': 'https://test.pypi.org/manage/account/'}, 'pypi': {'file': '~/.pypirc', 'section': 'pypi', 'key_field': 'password', 'prefix': 'pypi-', 'url': 'https://pypi.org/manage/account/'}, 'github': {'cmd': 'gh auth status', 'url': 'https://github.com/settings/tokens'}}

@dataclass
class Config:
    nbs: str = 'notebooks'
    out: str = 'src'
    docs: str = 'docs'
    root: str = '.'
    decorators: list[str] = field(default_factory=lambda: ['app.function', 'app.class_definition'])
    skip_prefixes: list[str] = field(default_factory=lambda: ['XX_', 'test_'])
    renames: dict[str,str] = field(default_factory=dict)

def read_config(root='.'):
    "Read config from pyproject.toml [tool.marimo-dev] section with defaults"
    try:
        with open(Path(root)/'pyproject.toml', 'rb') as f: cfg = tomllib.load(f).get('tool', {}).get('marimo-dev', {})
        return Config(**{k: v for k, v in cfg.items() if k in Config.__dataclass_fields__})
    except FileNotFoundError: return Config()

class Kind(Enum):
    "Types of nodes in parsed code"
    IMP="import"
    CONST="const"
    SETUP="setup"
    EXP="export"
    RAW="raw"

@dataclass
class Param:
    name: str                # parameter name
    anno: str|None = None    # type annotation
    default: str|None = None # default value
    doc: str = ''

@dataclass 
class Node:
    "A parsed code node representing an import, constant, or exported function/class."
    kind: Kind
    name: str
    src: str
    doc: str = ''
    params: list[Param] = field(default_factory=list)
    methods: list = field(default_factory=list)
    ret: tuple[str,str]|None = None
    hash_pipes: list[str] = field(default_factory=list)
    module: str = ''
    lineno: int = 0

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

def parse_hash_pipe(
    ls:list,       # source code lines
    export_dec,    # the export decorator node
)->list[str]:      # list of extracted directive names
    "Extract hash pipe directives from line immediately after export decorator"
    line_idx = export_dec.end_lineno
    if line_idx >= len(ls): return []
    if m := re.match(r'#\|\s*(.+)', ls[line_idx].strip()): return m.group(1).split()
    return []

def parse_class_params(
    n:ast.ClassDef, # class node to extract params from
    ls:list,        # source lines for inline doc extraction
)->list[Param]:     # list of parameter objects
    "Extract parameters from __init__ method if present, else class attributes."
    for item in n.body:
        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
            return parse_params(item, ls)
    return [Param(t.id, ast.unparse(a.annotation) if a.annotation else None, None, inline_doc(ls, a.lineno, t.id))
            for a in n.body if isinstance(a, ast.AnnAssign) and isinstance((t := a.target), ast.Name)]

def parse_class_methods(n: ast.ClassDef, ls: list):
    """Extract methods from a class definition."""
    methods = []
    for item in n.body:
        if isinstance(item, ast.FunctionDef):
            params = parse_params(item, ls)
            ret = parse_ret(item, ls)
            doc = ast.get_docstring(item) or ""
            methods.append({
                'name': item.name,
                'params': params,
                'ret': ret,
                'doc': doc
            })
    return methods

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
    d,          # decorator node to check
    cfg:Config, # configuration object
)->bool:        # whether decorator marks node for export
    "Check if decorator marks a node for export."
    return ast.unparse(d.func if isinstance(d, ast.Call) else d) in cfg.decorators

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
    "Extract constant definition from assignment."
    if not isinstance(n, ast.Assign): return None
    for t in n.targets:
        if isinstance(t, ast.Name): return Node(Kind.CONST, t.id, ast.unparse(n))

def parse_export(
    n:ast.AST,  # AST node to check
    ls:list,    # source lines for inline doc and decorators
    cfg:Config  # configuration object
)->Node|None:   # Node if exported function/class, else None
    "Extract exported function or class decorated with export decorators from config."
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): return None
    export_dec = next((d for d in n.decorator_list if is_export(d, cfg)), None)
    if not export_dec or n.name.startswith('test_'): return None
    doc,src = ast.get_docstring(n) or '', src_with_decs(n, ls)
    hash_pipes = parse_hash_pipe(ls, export_dec)
    if isinstance(n, ast.ClassDef): return Node(Kind.EXP, n.name, src, doc, parse_class_params(n, ls), parse_class_methods(n, ls), None, hash_pipes, '', n.lineno)
    return Node(Kind.EXP, n.name, src, doc, parse_params(n, ls), [], parse_ret(n, ls), hash_pipes, '', n.lineno)

def parse_node(
    n:ast.AST, # AST node to parse
    src:str,   # full source code text
    cfg:Config # configuration object
):             # yields Node objects for imports, constants, and exports
    "Extract importable nodes from an AST node."
    ls = src.splitlines()

    # Handle setup cells
    if isinstance(n, ast.With):
        for s in n.body:
            if (node := parse_import(s, ls)): yield node
            elif (node := parse_const(s, ls)): yield node
            else: yield Node(Kind.SETUP,
                             getattr(s, 'name', '_setup'),
                             ast.get_source_segment(src, s) or ast.unparse(s)
                            )
    # Handle export-named cells (e.g. def export(): or def export_main():)
    if isinstance(n, ast.FunctionDef) and n.name.startswith('export'):
        # Check it's decorated with @app.cell, not @app.function
        is_cell = any(
            (isinstance(d, ast.Attribute) and d.attr == 'cell') or
            (isinstance(d, ast.Name) and d.id == 'cell')
            for d in n.decorator_list
        )
        if is_cell:
            body = [s for s in n.body if not isinstance(s, ast.Return)]
            if body:
                src = '\n\n'.join(ast.unparse(s) for s in body)
                yield Node(Kind.EXP, n.name, src)
                return

    # Handle raw escape hatch cells
    if isinstance(n, ast.FunctionDef) and n.name.startswith('_'):
        body_src = '\n'.join(ls[n.lineno-1:n.end_lineno])
        if '#| raw' in body_src:
            raw_lines = [l for l in body_src.splitlines() if not l.strip().startswith(('#|', '@app.', 'def _(', 'return'))]
            raw_src = '\n'.join(raw_lines).strip()
            if raw_src: yield Node(Kind.RAW, '_raw', raw_src)
            return

    # Handle decorated exports
    if (node := parse_export(n, ls, cfg)): yield node

def parse_file(
    p: str|Path,     # path to Python file to parse
    module: str='',  # module name to assign to nodes
    root: str='.'    # root directory containing pyproject.toml
)->list[Node]:       # list of parsed nodes from the file
    "Parse a Python file and extract all nodes."
    cfg = read_config(root)
    src = Path(p).read_text()
    nodes = [node for n in ast.parse(src).body for node in parse_node(n, src, cfg)]
    for node in nodes: node.module = module
    return nodes

def read_meta(
    root='.', # project root directory containing pyproject.toml
)->dict:      # metadata dict with name, version, desc, license, author, urls
    "Read project metadata from pyproject.toml."
    with open(Path(root)/'pyproject.toml', 'rb') as f: 
        p = tomllib.load(f).get('project', {})

    # Extract author
    a = (p.get('authors') or [{}])[0]
    author = f"{a.get('name','')} <{a.get('email','')}>".strip(' <>') if isinstance(a, dict) else str(a)

    # Extract license
    lic = p.get('license', {})
    license_text = lic.get('text','') if isinstance(lic, dict) else lic

    return dict(
        name=p.get('name',''),
        version=p.get('version','0.0.0'),
        desc=p.get('description',''),
        license=license_text,
        author=author,
        urls=p.get('urls', {})
    )

def nb_name(
    f: Path,       # file path to extract notebook name from
    root: str='.'  # root directory containing pyproject.toml
)->str|None:       # cleaned notebook name or None if should be skipped
    "Extract notebook name from file path, skipping hidden, test, and configured prefix files."
    cfg = read_config(root)
    if f.name.startswith('.') or any(f.stem.startswith(prefix) for prefix in cfg.skip_prefixes): return None
    name = re.sub(r'^[a-z]_(\w+)', r'\1', f.stem)
    return None if name.startswith('test') else name

def scan(
    root='.',  # root directory containing pyproject.toml
):             # tuple of (meta dict, list of (name, nodes) tuples)
    "Scan notebooks directory and extract metadata and module definitions."
    cfg = read_config(root)
    meta = read_meta(root)
    mods = [(name, parse_file(f, name, root)) for f in sorted((Path(root) / cfg.nbs).glob('*.py')) if (name := nb_name(f, root))]
    return meta, mods

def clean(
    src:str, # source code to clean
)->str:      # cleaned source code
    "Remove decorator and hash pipe lines from source code"
    return '\n'.join(l for l in src.splitlines() if not l.strip().startswith(('@app.function', '@app.class_definition', '#|')))

def write(
    p:str,      # path to write to
    *parts:str, # content parts to join with blank lines
):
    "Write parts to file, filtering None values and joining with blank lines."
    Path(p).write_text('\n\n'.join(filter(None, parts)) + '\n')

def write_mod(
    path,           # output file path
    nodes:list,     # list of Node objects to write
    mod_names:list, # list of module names for import rewriting
    renames:dict=None, # prefix substitution map
):
    "Write module file with imports, constants, and exports."
    g = {k: [n for n in nodes if n.kind == k] for k in Kind}
    imports = '\n'.join(rewrite_imports(n.src, mod_names) for n in g[Kind.IMP])
    exp_src = '\n\n'.join(apply_renames(clean(n.src), n.name, renames) for n in g[Kind.EXP])
    parts = [imports, '\n'.join(n.src for n in g[Kind.CONST]), '\n'.join(n.src for n in g[Kind.SETUP]), exp_src, '\n\n'.join(n.src for n in g[Kind.RAW])]
    write(path, *parts)

def rename(
    name:str,         # original function/class name
    renames:dict=None # prefix substitution map
)->str:               # renamed identifier
    "Apply prefix substitutions to a name. Symmetric prefixes like __ wrap both sides."
    for prefix, replacement in (renames or {}).items():
        if not name.startswith(prefix): continue
        stem = name[len(prefix):]
        if replacement.startswith('__'): return replacement + stem + '__'
        return replacement + stem
    return name

def apply_renames(
    src:str,          # source code
    name:str,         # original function/class name
    renames:dict=None # prefix substitution map
)->str:               # source with renamed identifier
    "Replace function/class name in source code using prefix substitution."
    new = rename(name, renames)
    return src.replace(name, new, 1) if new != name else src

def rewrite_imports(
    src:str,       # source code to rewrite
    mod_names:list # list of module names
)->str:            # rewritten source code
    "Rewrite cross-notebook imports to relative package imports"
    if not src.strip().startswith('from '): return src
    parts = src.split()
    if len(parts) < 2: return src
    module = parts[1]
    if module.startswith('.'): return src
    stripped = re.sub(r'^[a-z]_', '', module)
    if stripped in mod_names: return src.replace(f'from {module}', f'from .{stripped}')
    return src

def write_init(
    path:str|Path, # path to write __init__.py file
    meta:dict,     # metadata dict with desc, version, author
    mods:list,     # list of (name, nodes) tuples
    renames:dict=None, # prefix substitution map
):
    "Generate and write __init__.py file with metadata and exports."
    lines = [f'"""{meta["desc"]}"""', f"__version__ = '{meta['version']}'"]
    if meta['author']: lines.append(f"__author__ = '{meta['author'].split('<')[0].strip()}'")
    exports = []
    for name, nodes in mods:
        if name.startswith('00_'): continue
        pub = [rename(n.name, renames) for n in nodes if n.kind == Kind.EXP and not n.name.startswith('__') and 'internal' not in n.hash_pipes]
        if pub: lines.append(f"from .{name} import {', '.join(pub)}"); exports.extend(pub)
    if exports: lines.append('__all__ = [\n' + '\n'.join(f'    "{n}",' for n in sorted(exports)) + '\n]')
    write(path, '\n'.join(lines))

def nb_path(
    mod_name, 
    root='.'
):
    '''[TODO] '''
    cfg = read_config(root)
    for f in (Path(root) / cfg.nbs).glob('*.py'):
        if nb_name(f, root) == mod_name: return f.relative_to(root)
    return None

def render_node(n, repo_url=None, root='.'):
    '''Builds a `node` for docs'''
    t = 'class' if 'class ' in n.src else 'async' if n.src.lstrip().startswith('async ') else 'func'
    signature = clean(n.src)
    node_id = f"code-{n.module}-{n.name}"
    nb = nb_path(n.module, root)
    tag_colors = {'func': '#10b981', 'async': '#f59e0b', 'class': '#8b5cf6'}

    code_lines = [Span(line, cls="code-line") for line in signature.split('\n')]

    def ghbtn(icon, label, url):
        if not url: return None
        return A(Button(Icon(icon, size=16), label, cls="gh-btn"), href=url, target="_blank", cls="gh-link")

    tag = Span(t, cls="tag", style=f"background:{tag_colors.get(t, '#666')};")
    mod_name = Span(Span(f"{n.module}.", cls="mod"), Span(n.name, cls="name"), cls="full-name") if n.module else Span(n.name, cls="full-name name")

    copy_btn = Button("📋", cls="copy-btn", onclick=f"navigator.clipboard.writeText(document.getElementById('{node_id}').textContent).then(() => this.textContent = '✓').then(() => setTimeout(() => this.textContent = '📋', 1500))")
    source_btn = ghbtn('github', 'Source', f"{repo_url}/blob/master/{nb}#L{n.lineno}" if repo_url and nb and n.lineno else None)
    edit_btn = ghbtn('code', 'Edit', f"{repo_url}/edit/master/{nb}" if repo_url and nb else None)
    blame_btn = ghbtn('info', 'Blame', f"{repo_url}/blame/master/{nb}#L{n.lineno}" if repo_url and nb and n.lineno else None)
    history_btn = ghbtn('calendar', 'History', f"{repo_url}/commits/master/{nb}" if repo_url and nb else None)
    issue_btn = ghbtn('circle-x', 'Issue', f"{repo_url}/issues/new?title=Issue%20with%20{n.name}&body={repo_url}/blob/master/{nb}%23L{n.lineno}" if repo_url and nb and n.lineno else None)

    return Article(
        Style("""
            me { margin-bottom: 0.75rem; border-radius: 8px; overflow: hidden; background: #1e1e1e; max-width: 100%; }
            me .header { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; }
            me .header-left { display: flex; align-items: center; }
            me .header-right { display: flex; align-items: center; gap: 0.5rem; }
            me .tag { padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; color: white; }
            me .full-name { font-weight: 500; font-size: 1rem; margin-left: 0.75rem; }
            me .mod { color: #666; }
            me .name { color: #e5e5e5; }
            me .doc { margin: 0; padding: 0 1rem 0.5rem 1rem; color: #888; font-size: 0.85rem; }
            me .gh-btn { display: flex; align-items: center; gap: 0.25rem; background: #333; border: 1px solid #444; color: #ccc; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.75rem; }
            me .gh-link { text-decoration: none; }
            me .copy-btn { background: transparent; border: none; cursor: pointer; font-size: 0.9rem; padding: 0.25rem; }
            me pre { background: #1a1a1a; border-top: 1px solid #2a2a2a; margin: 0; padding: 0.5rem 0; }
            me code { counter-reset: line; font-size: 0.8rem; line-height: 1.6; color: #ccc; }
            me .code-line { display: block; padding-left: 3.5em; white-space: pre-wrap; word-break: break-all; position: relative; }
            me .code-line::before { content: counter(line); counter-increment: line; position: absolute; left: 0; width: 2.5em; text-align: right; color: #555; user-select: none; }
        """),
        Div(Div(tag, mod_name, cls="header-left"),
            Div(copy_btn, source_btn, edit_btn, blame_btn, history_btn, issue_btn, cls="header-right"),
            cls="header"),
        P(n.doc, cls="doc") if n.doc else None,
        Pre(Code(*code_lines, cls="language-python", id=node_id)))

def render_module_page(mod_name, mod_nodes, all_mod_names, meta, root='.'):
    '''Builds a Module Page'''
    repo_url = meta.get('urls', {}).get('Repository')
    exp_nodes = [n for n in mod_nodes if n.kind == Kind.EXP]

    head_elements = [
        Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.8/bundles/datastar.js"),
        Script(src="https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js"),
        Script(src="js/highlight.js", type="module"),
        Style("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; } code { font-family: 'SF Mono', Consolas, monospace; }"),
        Title(f"{mod_name} - {meta['name']}")]

    nav_links = [Li(A("← Index", href="index.html", cls="back-link"))] + [
        Li(A(m, href=f"{m}.html", cls=f"nav-link {'active' if m == mod_name else ''}")) for m in all_mod_names]

    nav = Nav(
        Style("""
            me { padding: 1rem; background: #1a1a1a; min-width: 180px; }
            me h3 { margin: 0 0 1rem 0; color: #fff; }
            me ul { list-style: none; padding: 0; margin: 0; }
            me .back-link { color: #888; text-decoration: none; font-size: 0.85rem; }
            me .back-link:hover { color: #fff; }
            me .nav-link { color: #aaa; text-decoration: none; }
            me .nav-link:hover { color: #fff; }
            me .nav-link.active { color: #fff; }
            me input { width: 100%; padding: 0.5rem; border: 1px solid #333; border-radius: 4px; background: #252525; color: #fff; margin-bottom: 1rem; box-sizing: border-box; }
        """),
        H3(meta['name']),
        Input(type="text", placeholder="Search...", **{"data-bind": "search"}),
        Ul(*nav_links))

    header = Header(
        Style("""
            me { padding: 1rem; background: #1e1e1e; border-bottom: 1px solid #333; }
            me .header-row { display: flex; align-items: center; justify-content: space-between; }
            me h1 { margin: 0; font-size: 1.5rem; color: #fff; }
            me .wasm-btn { display: flex; align-items: center; gap: 0.25rem; background: #333; border: 1px solid #444; color: #ccc; padding: 0.5rem 0.75rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
            me .wasm-link { text-decoration: none; }
        """),
        Div(H1(mod_name),
            A(Button(Icon('external-link', size=16), "Run in Browser", cls="wasm-btn"),
              href=f"wasm/{mod_name}/index.html", target="_blank", cls="wasm-link"),
            cls="header-row"))

    content = Div(
        Style("""
            me { padding: 1rem; background: #121212; overflow-y: auto; flex: 1; }
        """),
        *[render_node(n, repo_url, root) for n in exp_nodes])

    body = Body(nav,
        Div(header, content, style="flex: 1; display: flex; flex-direction: column;"),
        style="display: flex; height: 100vh; margin: 0; background: #121212;",
        **{"data-signals": "{search: ''}"})

    return Html(Head(*head_elements), body)

def build_docs(
    root='.'    # the project root (this should never really change)
):
    '''Builds the static documentation website'''
    cfg = read_config(root)
    meta = read_meta(root)
    _, mods = scan(root)
    mod_names = [name for name, _ in mods]
    docs_path = Path(root) / cfg.docs
    docs_path.mkdir(exist_ok=True)
    (docs_path / "index.html").write_text(to_xml(render_index_page(meta, mods)))
    for mod_name, mod_nodes in mods:
        (docs_path / f"{mod_name}.html").write_text(to_xml(render_module_page(mod_name, mod_nodes, mod_names, meta, root)))
    export_wasm(root)
    return f"Generated index + {len(mods)} module pages in {docs_path}"

def export_wasm(
    root='.'  # Project Root
):
    """Uses the bundeled notebook to make a WASM marimo notebook"""
    cfg = read_config(root)
    wasm_dir = Path(root) / cfg.docs / 'wasm'
    wasm_dir.mkdir(parents=True, exist_ok=True)
    bundled = Path(root) / cfg.nbs / '_bundled.py'
    bundle_notebook(root, name=str(bundled))
    os.system(f"marimo export html-wasm {bundled} -o {wasm_dir} --mode edit")
    bundled.unlink()

def write_nojekyll(root='.'):
    cfg = read_config(root)
    Path(root, cfg.docs, '.nojekyll').touch()

def html_preview(width='100%', height='300px'):
    "Display FT components in an IFrame"
    def _preview(*components): show(Iframe(srcdoc=to_xml(components[0] if len(components) == 1 else Div(*components)), width=width, height=height))
    return _preview

def render_index_page(meta, mods, repo_url=None):
    mod_names = [name for name, _ in mods]
    head_elements = [
        Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js"),
        Script(src="https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js"),
        Script(src="js/highlight.js", type="module"),
        Style("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; } code { font-family: 'SF Mono', Consolas, monospace; }"),
        Title(meta['name'])]

    nav_links = [Li(A(m, href=f"{m}.html", cls="nav-link")) for m in mod_names]

    nav = Nav(
        Style("""
            me { padding: 1rem; background: #1a1a1a; min-width: 180px; }
            me h3 { margin: 0 0 1rem 0; color: #fff; }
            me ul { list-style: none; padding: 0; margin: 0; }
            me .nav-link { color: #aaa; text-decoration: none; }
            me .nav-link:hover { color: #fff; }
        """),
        H3(meta['name']),
        Ul(*nav_links))

    module_cards = [A(
        Div(H3(name, cls="card-title"),
            P(f"{len([n for n in nodes if n.kind == Kind.EXP])} exports", cls="card-count"),
            cls="card"),
        href=f"{name}.html", cls="card-link")
        for name, nodes in mods]

    content = Div(
        Style("""
            me { padding: 2rem; flex: 1; }
            me h1 { margin: 0 0 0.5rem 0; color: #fff; }
            me .desc { color: #888; margin: 0 0 2rem 0; }
            me .version { color: #666; margin: 0 0 2rem 0; font-size: 0.9rem; }
            me h2 { color: #fff; margin: 0 0 1rem 0; font-size: 1.2rem; }
            me .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
            me .card-link { text-decoration: none; }
            me .card { padding: 1rem; background: #1e1e1e; border-radius: 8px; }
            me .card:hover { background: #252525; }
            me .card-title { margin: 0 0 0.5rem 0; color: #fff; }
            me .card-count { margin: 0; color: #888; }
        """),
        H1(meta['name']),
        P(meta['desc'], cls="desc"),
        P(f"Version {meta['version']}", cls="version"),
        H2("Modules"),
        Div(*module_cards, cls="grid"))

    body = Body(nav, content, style="display: flex; min-height: 100vh; margin: 0; background: #121212;")
    return Html(Head(*head_elements), body)

def Icon(name: str,            # name of the icon MUST be in icon_dict
         size=24,              # value to be passed to height and width of the icon
         stroke=1.5,           # stroke width 
         cls=None,             # css class
         icon_dict:dict=icons, # Dict of icons {"name":"<svg...>"}
         **kwargs              # passed to through to FT 
        ) -> 'Any':            # Follow recomendation from fastHTML docs
    '''
    Creates a custom html compliant <icon-{name}>... 
    Intended to be used with a Global Dict of icons {"home": "<svg...", "info": "<svg..."} 
    Icon('home') -> <icon-home> ....  </icon-home>
    '''
    if name not in icon_dict: raise ValueError(f"Icon '{name}' not found")

    # count=1 Replace only the first occurrence of width & height 99% of time this is what you want
    svg_string = icon_dict[name]
    svg_string = re.sub(r'width="\d+"', f'width="{size}"', svg_string, count=1)
    svg_string = re.sub(r'height="\d+"', f'height="{size}"', svg_string, count=1)
    svg_string = re.sub(r'stroke-width="\d+"', f'stroke-width="{stroke}"', svg_string)

    return ft(f'icon-{name}', NotStr(svg_string), cls=cls, **kwargs)

def write_highlighter(root='.'):
    "Write Python syntax highlighter JS to docs folder."
    cfg = read_config(root)
    js_dir = Path(root) / cfg.docs / 'js'
    js_dir.mkdir(parents=True, exist_ok=True)

    tokens = [
        ('py-decorator',   r'@[\w.]+'),
        ('py-defname',     r'(?<=def )\w+'),
        ('py-classname',   r'(?<=class )\w+'),
        ('py-keyword',     r'\b(?:def|class|return|if|elif|else|for|while|import|from|as|with|try|except|finally|raise|yield|async|await|pass|break|continue|in|is|not|and|or|lambda|None|True|False|self)\b'),
        ('py-builtin',     r'\b(?:print|len|range|list|dict|set|tuple|int|str|float|bool|isinstance|hasattr|getattr|setattr|enumerate|zip|map|filter|any|all|sorted|reversed|super|type|open|next)\b'),
        ('py-call',        r'\b\w+(?=\()'),
        ('py-number',      r'\b\d[\d_]*(?:\.\d[\d_]*)?(?:e[+-]?\d+)?\b'),
        ('py-operator',    r'->|==|!=|<=|>=|\*\*|\/\/|[+\-*/%=<>&|^~]'),
        ('py-punctuation', r'[{}\(\)\[\]:,;]'),
        ('py-fstring',     r"f(?='|\")"),
        ('py-type',        r'(?<=: )\w+'),
        ('py-string',      r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\''),
        ('py-comment',     r'#.*'),
    ]


    token_js = ',\n  '.join(f"['{name}', /{pattern}/g]" for name, pattern in tokens)
    color_css = '\n'.join(f'::highlight({name}) {{ color: {COLORS[name.replace("py-", "")]}; }}' for name, _ in tokens)

    js = f"""const PY_TOKENS = [
  {token_js}
];

function highlightAll(root = document) {{
  if (!CSS?.highlights) return;
  for (const [name] of PY_TOKENS) CSS.highlights.delete(name);
  root.querySelectorAll('pre code').forEach(code => {{
    const textNodes = [];
    code.querySelectorAll('.code-line').forEach(line => {{
        if (line.firstChild?.nodeType === Node.TEXT_NODE) textNodes.push(line.firstChild);
    }});
    if (!textNodes.length) return;

    for (const [name, pattern] of PY_TOKENS) {{
      const highlight = CSS.highlights.get(name) ?? new Highlight();
      for (const node of textNodes) {{
        const src = node.textContent;
        const re = new RegExp(pattern.source, pattern.flags);
        for (const match of src.matchAll(re)) {{
          const range = new Range();
          range.setStart(node, match.index);
          range.setEnd(node, match.index + match[0].length);
          highlight.add(range);
        }}
      }}
      if (highlight.size > 0) CSS.highlights.set(name, highlight);
    }}
  }});
}}

// Inject highlight styles
const style = document.createElement('style');
style.textContent = `{color_css}`;
document.head.appendChild(style);

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => highlightAll());
else highlightAll();
"""


    (js_dir / 'highlight.js').write_text(js)
    return f"Wrote {js_dir}/highlight.js"

def build(
    root='.',  # root directory containing pyproject.toml
)->str:        # path to built package
    "Build a Python package from notebooks."
    cfg = read_config(root)
    meta, mods = scan(root)
    mod_names = [name for name, _ in mods]
    pkg = Path(root) / cfg.out / meta['name'].replace('-', '_')
    if pkg.exists(): shutil.rmtree(pkg)
    pkg.mkdir(parents=True, exist_ok=True)
    for name, nodes in mods:
        stripped = re.sub(r'^[a-z]_', '', name)
        if stripped != 'index' and any(n.kind == Kind.EXP for n in nodes): write_mod(pkg/f'{stripped}.py', nodes, mod_names, cfg.renames)
    write_init(pkg/'__init__.py', meta, mods, cfg.renames)
    all_exp = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
    if all_exp: write_llms()
    return str(pkg)

def tidy():
    "Remove cache and temporary files (__pycache__, __marimo__, .pytest_cache, etc)."
    import shutil
    for p in Path('.').rglob('__pycache__'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('__marimo__'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('.pytest_cache'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('*.pyc'): p.unlink(missing_ok=True)
    print("Cleaned cache files")

def nuke():
    "Remove all build artifacts (dist, docs, src) and cache files."
    import shutil
    tidy()
    for d in ['dist', 'docs', 'src', 'temp']: shutil.rmtree(d, ignore_errors=True)
    print("Nuked build artifacts")

def get_pypi_name(import_name):
    "Map import name to PyPI package name."
    root = import_name.split('.')[0]
    return IMPORT_TO_PYPI.get(root, root)

def extract_import_names(nodes):
    "Extract top-level module names from import nodes."
    names = set()
    for n in nodes:
        if n.kind != Kind.IMP: continue
        tree = ast.parse(n.src)
        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    names.add(alias.name.split('.')[0])
            elif isinstance(stmt, ast.ImportFrom) and stmt.module:
                names.add(stmt.module.split('.')[0])
    return names

def pep723_header(deps):
    "Generate PEP 723 inline script metadata."
    deps_str = ', '.join(f'"{d}"' for d in sorted(deps))
    return f'# /// script\n# dependencies = [{deps_str}]\n# ///\n'

def write_llms(root='.'):
    "Generate llms.txt and llms-full.txt from parsed notebooks."
    cfg = read_config(root)
    meta, mods = scan(root)
    name = meta['name']
    desc = meta.get('description', '')
    docs_dir = Path(root) / cfg.docs
    docs_dir.mkdir(parents=True, exist_ok=True)

    # llms-full.txt — complete cleaned source
    full_parts = [f"# {name}\n\n> {desc}\n"]
    for mod_name, nodes in mods:
        exports = [n for n in nodes if n.kind == Kind.EXP]
        if not exports: continue
        stripped = re.sub(r'^[a-z]_', '', mod_name)
        full_parts.append(f"## {stripped}\n")
        for n in exports:
            full_parts.append(clean(n.src))
    Path(docs_dir / 'llms-full.txt').write_text('\n\n'.join(full_parts) + '\n')

    # llms.txt — summary with links
    base_url = meta.get('url', '')
    lines = [f"# {name}\n", f"> {desc}\n"]
    for mod_name, nodes in mods:
        exports = [n for n in nodes if n.kind == Kind.EXP]
        if not exports: continue
        stripped = re.sub(r'^[a-z]_', '', mod_name)
        names = ', '.join(n.name for n in exports)
        lines.append(f"- [{stripped}]({base_url}/{stripped}): {names}")
    lines.append(f"\n- [llms-full.txt]({base_url}/llms-full.txt): Complete source code")
    Path(docs_dir / 'llms.txt').write_text('\n'.join(lines) + '\n')

    return f"Wrote {docs_dir}/llms.txt and llms-full.txt"

def bundle(root='.', name=None):
    "Bundle all notebooks into a single Python file with PEP 723 dependencies."
    cfg = read_config(root)
    meta, mods = scan(root)

    # Get notebook filenames to filter out local imports
    nbs_dir = Path(root) / cfg.nbs
    nb_names = {f.stem for f in nbs_dir.glob('*.py')}

    # Collect all nodes
    all_nodes = [n for _, nodes in mods for n in nodes]

    # Extract dependencies
    import_names = extract_import_names(all_nodes)
    mod_names = [m for m, _ in mods]

    # Filter out local modules, notebook names, and stdlib
    external = {get_pypi_name(n) for n in import_names 
                if n not in mod_names 
                and n not in nb_names 
                and n not in sys.stdlib_module_names}

    # Build output
    header = pep723_header(external)

    # Filter out local imports, dedupe externals
    seen = set()
    filtered_imports = []
    for n in all_nodes:
        if n.kind != Kind.IMP: continue
        # Skip if it's a local notebook import
        if any(nb in n.src for nb in nb_names): continue
        if n.src not in seen:
            seen.add(n.src)
            filtered_imports.append(n.src)

    imports = '\n'.join(filtered_imports)

    consts = '\n'.join(n.src for n in all_nodes if n.kind == Kind.CONST)
    setup = '\n'.join(n.src for n in all_nodes if n.kind == Kind.SETUP)
    exports = '\n\n'.join(clean(n.src) for n in all_nodes if n.kind == Kind.EXP)

    content = '\n\n'.join(p for p in [header, imports, consts, setup, exports] if p.strip())

    # Determine output path
    if name:
        out_path = Path(root) / name
    else:
        out_path = Path(root) / cfg.out / meta['name'].replace('-', '_') / '__init__.py'

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    return f"Bundled to {out_path}"

def bundle_notebook(root='.', name=None, include_cells=False):
    "Bundle all notebooks into a single marimo notebook file."
    cfg = read_config(root)
    nbs_dir = Path(root) / cfg.nbs

    # Get ordered notebook files (skip XX_ and test_)
    files = sorted(f for f in nbs_dir.glob('*.py')
                   if not any(f.name.startswith(p) for p in cfg.skip_prefixes))
    nb_stems = {f.stem for f in files}

    # Decorators to keep
    keep = {'app.function', 'app.class_definition'}
    if include_cells: keep.add('app.cell')

    setup_lines = []
    cells = []

    for f in files:
        txt = f.read_text()
        tree = ast.parse(txt)
        lines = txt.splitlines()

        for node in tree.body:
            # Collect setup block contents
            if isinstance(node, ast.With):
                for s in node.body:
                    line = ast.get_source_segment(txt, s)
                    if not line: continue
                    # Skip cross-notebook imports
                    if any(nb in line for nb in nb_stems): continue
                    if line.strip() not in setup_lines: setup_lines.append(line.strip())

            # Collect decorated cells
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                src = ast.get_source_segment(txt, node)
                if not src: continue
                # Check decorators
                dec_names = []
                for d in getattr(node, 'decorator_list', []):
                    if isinstance(d, ast.Attribute): dec_names.append(f"{ast.unparse(d)}")
                    elif isinstance(d, ast.Name): dec_names.append(d.id)
                if any(d in keep for d in dec_names):
                    # Reconstruct with decorators
                    dec_lines = [lines[d.lineno - 1] for d in node.decorator_list]
                    block = '\n'.join(dec_lines) + '\n' + src
                    cells.append(block)

    # Check for name collisions
    seen = {}
    for f in files:
        txt = f.read_text()
        tree = ast.parse(txt)
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): continue
            if node.name.startswith('_'): continue
            if node.name in seen:
                raise ValueError(f"Name collision: '{node.name}' defined in both {seen[node.name]} and {f.name}")
            seen[node.name] = f.name

    # Build output
    meta = read_meta(root)
    header = f'import marimo\n\n__generated_with = "0.20.4"\napp = marimo.App(width="full")\n'
    setup = 'with app.setup:\n' + '\n'.join(f'    {l}' for l in setup_lines)
    body = '\n\n\n'.join(cells)
    footer = 'if __name__ == "__main__":\n    app.run()'

    content = '\n\n'.join([header, setup, body, footer]) + '\n'

    out_path = Path(root) / (name or f"{meta['name'].replace('-', '_')}_bundled.py")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    return f"Bundled notebook to {out_path}"

def check_credentials(platform='testpypi'):
    "Check if credentials exist for a platform and return status info."
    cred = CREDENTIALS.get(platform)
    if not cred: return {'found': False, 'msg': f"Unknown platform: {platform}"}

    url = cred['url']

    # Command-based check (e.g. GitHub)
    if 'cmd' in cred:
        try:
            r = subprocess.run(cred['cmd'].split(), capture_output=True, text=True)
            if r.returncode == 0:
                return {'found': True, 'platform': platform, 'msg': r.stdout.strip(), 'source': cred['cmd']}
            return {'found': False, 'msg': f"Not authenticated. Set up at {url}"}
        except FileNotFoundError:
            return {'found': False, 'msg': f"CLI not installed. Get it at {url}"}

    # File-based check (e.g. PyPI)
    path = Path(cred['file']).expanduser()
    if not path.exists():
        return {'found': False, 'msg': f"No {cred['file']} found. Create a token at {url}"}

    config = configparser.ConfigParser()
    config.read(path)
    section = cred['section']

    if section not in config:
        return {'found': False, 'msg': f"No [{section}] section in {cred['file']}. Create a token at {url}"}

    password = config[section].get(cred['key_field'], '')
    if not password:
        return {'found': False, 'msg': f"No {cred['key_field']} in [{section}]. Create a token at {url}"}

    prefix = cred.get('prefix', '')
    preview = password[:len(prefix)+4] + '...' if password.startswith(prefix) else '****'
    return {'found': True, 'platform': platform, 'username': config[section].get('username', ''), 'preview': preview, 'source': str(path)}

def check_pypi_auth(test=True):
    "Check if PyPI credentials exist and return status info."
    pypirc = Path.home() / '.pypirc'
    section = 'testpypi' if test else 'pypi'
    target = 'Test PyPI' if test else 'PyPI'
    url = 'https://test.pypi.org/manage/account/' if test else 'https://pypi.org/manage/account/'

    if not pypirc.exists():
        return {'found': False, 'msg': f"No ~/.pypirc found. Create a token at {url}"}

    config = configparser.ConfigParser()
    config.read(pypirc)

    if section not in config:
        return {'found': False, 'msg': f"No [{section}] section in ~/.pypirc. Create a token at {url}"}

    password = config[section].get('password', '')
    if not password:
        return {'found': False, 'msg': f"No password in [{section}]. Create a token at {url}"}

    preview = password[:9] + '...' if password.startswith('pypi-') else '****'
    return {'found': True, 'section': section, 'username': config[section].get('username', ''), 'preview': preview, 'source': str(pypirc)}

def publish(
    test=True  # When ready to upload to PyPi change this to false
):
    "Build and publish package to PyPI."
    platform = 'testpypi' if test else 'pypi'
    auth = check_credentials(platform)
    if not auth['found']:
        print(f"❌ {auth['msg']}")
        return

    print(f"✅ Authenticated as {auth['username']} ({auth['preview']}) from {auth['source']}")
    print("Rebuilding package from notebooks...")
    build()

    shutil.rmtree('dist', ignore_errors=True)
    print("Building distribution...")
    subprocess.run(['uv', 'build'], check=True)

    cmd = ['uv', 'publish']
    if test: cmd.extend(['--publish-url', 'https://test.pypi.org/legacy/'])
    else: cmd.extend(['--publish-url', 'https://upload.pypi.org/legacy/'])

    config = configparser.ConfigParser()
    config.read(Path.home() / '.pypirc')
    section = auth['section'] if 'section' in auth else platform
    username = config[section].get('username', '__token__')
    password = config[section].get('password', '')
    cmd.extend(['--username', username, '--password', password])

    target = 'Test PyPI' if test else 'PyPI'
    print(f"Publishing to {target}...")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Published to {target}!")
    except subprocess.CalledProcessError as e:
        if '403' in (e.stderr or ''):
            print(f"❌ Auth failed. Token may be expired. Regenerate at {CREDENTIALS[platform]['url']}")
        else:
            print(f"❌ Publish failed: {e.stderr}")

def main():
    if len(sys.argv) < 2: print("Usage: md [build|publish|docs|tidy|nuke]"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'build':
        print(f"Built package at: {build()}")
        print(build_docs())
    elif cmd == 'publish':
        test = '--test' in sys.argv or '-t' in sys.argv
        target = "TestPyPI" if test else "PyPI"
        if input(f"Publish to {target}? [y/N] ").lower() != 'y': print("Aborted"); sys.exit(0)
        publish(test=test)
    elif cmd == 'docs': build_docs()
    elif cmd == 'tidy': tidy()
    elif cmd == 'nuke': nuke()
    elif cmd == 'bundle':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        print(bundle(name=name))

    else: print(f"Unknown command: {cmd}"); sys.exit(1)