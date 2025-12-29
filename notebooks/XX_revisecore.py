import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    from dataclasses import dataclass, field
    from typing import Callable
    from pathlib import Path
    from enum import Enum
    import ast, re, tomllib, json
    from fastcore.xml import to_xml
    from fasthtml.components import Div, Span, Code, P, Pre, A, Html, Head, Body, Script, Style, Form, Input, Button, H1, Aside, H3, Link



    CSS = "*{scrollbar-gutter:stable}body{font-family:sans-serif;max-width:1400px;margin:1rem auto;padding:0 1rem;line-height:1.5}.header{display:flex;justify-content:space-between;margin-bottom:1rem}.search-section{position:fixed;top:1rem;right:1rem;z-index:100;display:flex;gap:0.5rem;background:white;padding:0.75rem;border-radius:0.5rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1)}.content-wrapper{display:grid;grid-template-columns:250px 1fr;gap:2rem}.sidenav{position:sticky;top:1rem;max-height:calc(100vh - 2rem);overflow-y:auto;padding:1rem;background:#f9fafb;border-radius:0.375rem;border:1px solid #e5e7eb}.nav-item{display:flex;justify-content:space-between;padding:0.5rem;margin-bottom:0.25rem;border-radius:0.25rem;font-size:0.875rem;color:#374151;text-decoration:none}.nav-item:hover{background:#e5e7eb}.nav-item.disabled{opacity:0.4;pointer-events:none}.nav-badge,.match-badge{background:#3b82f6;color:white;padding:0.125rem 0.5rem;border-radius:9999px;font-size:0.7rem}.match-badge{position:absolute;top:1rem;right:1rem}.attribute{position:relative;padding:1rem;border:1px solid #e5e7eb;border-radius:0.375rem;background:#fff;scroll-margin-top:3rem;transition:order 0.5s}.attribute-name{font-weight:bold;font-size:1.25rem;color:#1e40af}input{padding:0.625rem;border:1px solid #d1d5db;border-radius:0.375rem;min-width:250px}button{padding:0.625rem 1.25rem;background:#3b82f6;color:white;border:none;border-radius:0.375rem;cursor:pointer}button.clear-btn{background:#dc2626}pre{border-radius:0.375rem;overflow-x:auto;font-size:0.8rem}"


@app.class_definition
class Kind(Enum): IMP='import'; CONST='const'; EXP='export'


@app.class_definition
@dataclass
class Param:
    name: str
    anno: str|None = None
    default: str|None = None
    doc: str = ''


@app.class_definition
@dataclass 
class Node:
    kind: Kind
    name: str
    src: str
    doc: str = ''
    params: list[Param] = field(default_factory=list)
    ret: tuple[str,str]|None = None  # (anno, doc)


@app.function
def __inline_doc(lines, lineno, pat): 
    if 0 < lineno <= len(lines) and (m := re.search(rf'{pat}.*?#\s*(.+)', lines[lineno-1])): return m.group(1).strip()
    return ''


@app.function
def __params(fn, lines):
    if not hasattr(fn, 'args'): return []
    args, defs = fn.args.args, fn.args.defaults
    pad = [None] * (len(args) - len(defs))
    return [Param(a.arg, ast.unparse(a.annotation) if a.annotation else None, 
                  ast.unparse(d) if d else None, __inline_doc(lines, a.lineno, rf'\b{a.arg}\b'))
            for a, d in zip(args, pad + defs) if a.arg not in ('self', 'cls')]


@app.function
def __ret(fn, lines):
    if not fn.returns or isinstance(fn.returns, ast.Constant): return None
    anno = ast.unparse(fn.returns)
    doc = __inline_doc(lines, fn.returns.lineno, r'->') if hasattr(fn.returns, 'lineno') else ''
    return (anno, doc)


@app.function
def __src_with_decs(n, lines):
    start = n.decorator_list[0].lineno - 1 if n.decorator_list else n.lineno - 1
    return '\n'.join(lines[start:n.end_lineno])


@app.function
def __is_export(d): return ast.unparse(d.func if isinstance(d, ast.Call) else d) in {'app.function', 'app.class_definition'}


@app.function
def parse_node(n, src):
    lines = src.splitlines()
    if isinstance(n, ast.With):
        for s in n.body:
            if isinstance(s, (ast.Import, ast.ImportFrom)): yield Node(Kind.IMP, '', ast.unparse(s))
            if isinstance(s, ast.Assign):
                for t in s.targets:
                    if isinstance(t, ast.Name) and t.id.startswith('__') and not t.id.endswith('__'):
                        yield Node(Kind.CONST, t.id, ast.unparse(s))
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and any(__is_export(d) for d in n.decorator_list):
        if n.name.startswith('test_'): return
        body = n.body[0] if n.body else None
        doc = ast.get_docstring(n) or ''
        params = __params(n, lines) if not isinstance(n, ast.ClassDef) else [Param(t.id, ast.unparse(a.annotation) if a.annotation else None, None, __inline_doc(lines, a.lineno, rf'\b{t.id}\b')) for a in n.body if isinstance(a, ast.AnnAssign) and isinstance((t := a.target), ast.Name)]
        ret = __ret(n, lines) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) else None
        yield Node(Kind.EXP, n.name, __src_with_decs(n, lines), doc, params, ret)


@app.function
def parse_file(p):
    src = Path(p).read_text()
    return [node for n in ast.parse(src).body for node in parse_node(n, src)]


@app.function
def clean(src): return '\n'.join(l for l in src.splitlines() if not l.strip().startswith(('@app.function', '@app.class_definition')))


@app.function
def read_meta(root='.'):
    "Read package metadata from pyproject.toml"
    with open(Path(root)/'pyproject.toml', 'rb') as f: data = tomllib.load(f)
    p = data.get('project', {})
    a = (p.get('authors') or [{}])[0]
    author = f"{a.get('name','')} <{a.get('email','')}>".strip(' <>') if isinstance(a, dict) else str(a)
    lic = p.get('license', {})
    return dict(name=p.get('name',''), version=p.get('version','0.0.0'), desc=p.get('description',''),
                license=lic.get('text','') if isinstance(lic, dict) else lic, author=author)


@app.function
def nb_name(f):
    "Extract module name from notebook path, None to skip"
    if f.name.startswith('.') or f.stem.startswith('XX_'): return None
    name = re.sub(r'^\d+_', '', f.stem)
    return None if name.startswith('test') else name


@app.function
def group(nodes): return {k: [n for n in nodes if n.kind == k] for k in Kind}


@app.function
def scan(nbs='notebooks', root='.'):
    "Scan notebooks directory, return metadata and parsed nodes per module"
    meta = read_meta(root)
    mods = [(name, parse_file(f)) for f in sorted(Path(nbs).glob('*.py')) if (name := nb_name(f))]
    return meta, mods


@app.function
def write(p, *parts): Path(p).write_text('\n\n'.join(filter(None, parts)) + '\n')


@app.function
def write_mod(path, nodes):
    "Write single module file from nodes"
    g = group(nodes)
    imps = '\n'.join(n.src for n in g[Kind.IMP])
    consts = '\n'.join(n.src for n in g[Kind.CONST])
    exps = '\n\n'.join(clean(n.src) for n in g[Kind.EXP])
    write(path, imps, consts, exps)


@app.function
def write_init(path, meta, mods):
    "Generate __init__.py with exports"
    lines = [f'"""{meta["desc"]}"""', f"__version__ = '{meta['version']}'"]
    if meta['author']: lines.append(f"__author__ = '{meta['author'].split('<')[0].strip()}'")
    exports = []
    for name, nodes in mods:
        if name.startswith('00_'): continue
        pub = [n.name for n in nodes if n.kind == Kind.EXP and not n.name.startswith('__')]
        if pub:
            lines.append(f"from .{name} import {', '.join(pub)}")
            exports.extend(pub)
    if exports: lines.append('__all__ = [\n' + '\n'.join(f'    "{n}",' for n in sorted(exports)) + '\n]')
    write(path, '\n'.join(lines))


@app.function
def __searchable(n):
    parts = [n.name, n.doc] + [f"{p.name} {p.doc}" for p in n.params]
    return ' '.join(parts).replace('\n', ' ').replace("'", "\\'")


@app.function
def __sig(n):
    is_cls = n.src.lstrip().startswith(('@dataclass', 'class '))
    is_async = n.src.lstrip().startswith('async def')
    if is_cls:
        lines = [f"class {n.name}:"]
        if n.doc: lines.append(f'    """{n.doc}"""')
        for p in n.params: lines.append(f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}")
        return '\n'.join(lines)
    ps = ', '.join(f"{p.name}{f': {p.anno}' if p.anno else ''}{f'={p.default}' if p.default else ''}" for p in n.params)
    ret = f" -> {n.ret[0]}" if n.ret else ""
    sig = f"{'async def' if is_async else 'def'} {n.name}({ps}){ret}:"
    return f"{sig}\n    \"\"\"{n.doc}\"\"\"" if n.doc else sig


@app.function
def doc_card(n, i):
    "Generate HTML card for function/class with Datastar search"
    srch, msig, show = f"srch{i}", f"mc{i}", f"_show{i}"
    return Div(
        Span(cls="match-badge", **{"data-show": "$tags.length > 0 || $search.trim().length > 0", "data-text": f"${msig}"}),
        Div(Code(n.name), cls="attribute-name"),
        Div(Pre(Code(__sig(n), cls="language-python"), style="max-width:160ch;overflow-x:auto;white-space:pre", **{"data-show": f"!${show}"}),
            Pre(Code(clean(n.src), cls="language-python"), style="max-width:160ch;overflow-x:auto;white-space:pre", **{"data-show": f"${show}"}),
            Button("Show full", **{"data-on:click": f"${show} = true", "data-show": f"!${show}"}),
            Button("Show sig", **{"data-on:click": f"${show} = false", "data-show": f"${show}"}),
            cls="description"),
        id=n.name, cls="attribute",
        **{"data-signals": f"{{'{srch}': '{__searchable(n)}', '{msig}': 0, '{show}': false}}",
           "data-effect": f"${msig} = [...$tags, $search.trim()].filter(t => t.length > 0 && ${srch}.toLowerCase().includes(t.toLowerCase())).length",
           "data-show": f"($tags.length === 0 && $search.trim().length === 0) || ${msig} > 0",
           "data-style:order": f"($tags.length === 0 && $search.trim().length === 0) ? 0 : -${msig}"})


@app.function
def nav_item(n, i):
    "Generate sidenav link with match count"
    msig = f"mc{i}"
    return A(Span(n.name), Span(cls="nav-badge", **{"data-show": "$tags.length > 0 || $search.trim().length > 0", "data-text": f"${msig}"}),
             href=f"#{n.name}", cls="nav-item", **{"data-class:disabled": f"($tags.length > 0 || $search.trim().length > 0) && ${msig} === 0"})


@app.function
def docs_page(title, subtitle, nodes):
    "Generate complete Datastar docs page"
    return Html(
        Head(Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"),
             Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"),
             Script(src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"),
             Script("hljs.highlightAll();"), Style(CSS)),
        Body(Form(Input(type="text", placeholder="Search...", **{"data-bind": "search"}),
                  Button("Add Tag", type="submit"), Button("Clear", cls="clear-btn", type="button", **{"data-on:click": "$tags=[],$search=''"}),
                  cls="search-section", **{"data-on:submit__prevent": "$search.trim() ? ($tags=[...$tags,$search.trim()],$search='') : null"}),
             Div(Div(H1(title), P(subtitle, cls="subtitle"), cls="title-section"), cls="header"),
             Div(Aside(H3("Functions"), *[nav_item(n, i) for i, n in enumerate(nodes)], cls="sidenav"),
                 Div(Div(*[doc_card(n, i) for i, n in enumerate(nodes)], cls="attributes"), cls="main-content"), cls="content-wrapper"),
             **{"data-signals": '{"search":"","tags":[]}'}),
        style="scroll-behavior:smooth")


@app.function
def write_docs(title, subtitle, nodes, out='docs'):
    "Write Datastar docs page to index.html"
    Path(out).mkdir(exist_ok=True)
    (Path(out)/'index.html').write_text(f'<!doctype html>\n{to_xml(docs_page(title, subtitle, nodes))}')


@app.function
def write_llms(meta, nodes, out='docs'):
    "Write llms.txt with API signatures"
    sigs = '\n\n'.join(__sig(n) for n in nodes if not n.name.startswith('__'))
    content = f"# {meta['name']}\n\n> {meta['desc']}\n\nVersion: {meta['version']}\n\n## API\n\n```python\n{sigs}\n```"
    Path(out).mkdir(exist_ok=True)
    (Path(out)/'llms.txt').write_text(content)


@app.cell
def _(mo):
    mo.md(r"""
    ## CLI
    """)
    return


@app.function
def build(nbs='notebooks', out='src', root='.'):
    "Build package from notebooks"
    meta, mods = scan(nbs, root)
    pkg = Path(out) / meta['name'].replace('-', '_')
    pkg.mkdir(parents=True, exist_ok=True)
    for name, nodes in mods:
        if name != 'index' and any(n.kind == Kind.EXP for n in nodes): write_mod(pkg/f'{name}.py', nodes)
    write_init(pkg/'__init__.py', meta, mods)
    all_exp = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
    if all_exp: write_docs(meta['name'], meta['desc'], all_exp); write_llms(meta, all_exp)
    return str(pkg)


@app.function
def publish(test=True):
    "Build and publish to PyPI (test=True for TestPyPI)"
    import subprocess, configparser
    subprocess.run(['uv', 'build'], check=True)
    pypirc, section = Path.home()/'.pypirc', 'testpypi' if test else 'pypi'
    url = 'https://test.pypi.org/legacy/' if test else 'https://upload.pypi.org/legacy/'
    cmd = ['uv', 'publish', '--publish-url', url]
    if pypirc.exists():
        cfg = configparser.ConfigParser(); cfg.read(pypirc)
        if section in cfg: cmd.extend(['--username', cfg[section].get('username', '__token__'), '--password', cfg[section].get('password', '')])
    subprocess.run(cmd, check=True)


@app.function
def preview(port=8000, docs_dir='docs'):
    "Serve docs locally in background thread"
    import http.server, socketserver, threading
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw): super().__init__(*a, directory=docs_dir, **kw)
    def serve():
        with socketserver.TCPServer(("", port), H) as s: print(f"Serving at http://localhost:{port}"); s.serve_forever()
    threading.Thread(target=serve, daemon=True).start()
    return f"http://localhost:{port}"


@app.cell
def _():
    build(out="test")
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
