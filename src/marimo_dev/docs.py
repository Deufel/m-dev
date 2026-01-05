from .core import Kind, Param, Node, Config, read_config
from .read import scan, nb_name, read_meta
from pathlib import Path
import ast, re
import marimo as mo
from functools import partial
from fastcore.xml import Span, Code, Li, Article, Div, Ul, P, FT, to_xml, Pre, Link, A, Iframe, Button, H1, H2, H3, Nav, Aside, Header, Input, NotStr, Strong, Main
from fasthtml.components import ft, Html, Head, Script, Body, show, Style, Title

def cls_sig(
    n:Node,           # the node to generate signature for
    dataclass=False,  # whether to include @dataclass decorator
)->str:               # formatted class signature
    "Generate a class signature string."
    header = f"@dataclass\nclass {n.name}:" if dataclass else f"class {n.name}:"
    lines = [header]
    if n.doc: lines.append(f'    """{n.doc}"""')
    for p in n.params:
        attr = f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}"
        if p.doc: attr += f"  # {p.doc}"
        lines.append(attr)
    for m in n.methods:
        ps = ', '.join(f"{p.name}{f': {p.anno}' if p.anno else ''}{f'={p.default}' if p.default else ''}" for p in m['params'])
        ret = f" -> {m['ret'][0]}" if m['ret'] else ""
        lines.append(f"    def {m['name']}({ps}){ret}:")
        if m['doc']: lines.append(f'        """{m["doc"]}"""')
    return '\n'.join(lines)

def fn_sig(n, is_async=False):
    "Generate a function signature string with inline parameter documentation."
    prefix = 'async def' if is_async else 'def'
    ret = f" -> {n.ret[0]}" if n.ret else ""
    if not n.params:
        sig = f"{prefix} {n.name}(){ret}:"
        return f'{sig}\n    """{n.doc}"""' if n.doc else sig
    params = [f"    {p.name}{f': {p.anno}' if p.anno else ''}{f'={p.default}' if p.default else ''},{f'  # {p.doc}' if p.doc else ''}" for p in n.params]
    params[-1] = params[-1].replace(',', '')
    lines = [f"{prefix} {n.name}("] + params + [f"){ret}:"]
    if n.doc: lines.append(f'    """{n.doc}"""')
    return '\n'.join(lines)

def sig(
    n:Node, # the node to generate signature for
)->str:     # formatted signature string
    "Generate a signature string for a class or function node."
    t = exp_type(n)
    if t == 'class': return cls_sig(n, dataclass=n.src.lstrip().startswith('@dataclass'))
    return fn_sig(n, is_async=t == 'async')

def write_llms(
    meta: dict,    # project metadata from pyproject.toml
    nodes: list,   # list of Node objects to document
    root: str='.'  # root directory containing pyproject.toml
):
    "Write API signatures to llms.txt file for LLM consumption."
    cfg = read_config(root)
    sigs = '\n\n'.join(sig(n) for n in nodes if not n.name.startswith('__') and 'nodoc' not in n.hash_pipes)
    content = f"# {meta['name']}\n\n> {meta['desc']}\n\nVersion: {meta['version']}\n\n## API\n\n```python\n{sigs}\n```"
    Path(cfg.docs).mkdir(exist_ok=True)
    (Path(cfg.docs)/'llms.txt').write_text(content)

def exp_type(n):
    src = n.src.lstrip()
    if n.methods or src.startswith(('@dataclass', 'class ')): return 'class'
    if src.startswith('async def'): return 'async'
    return 'func'

def render_param(p):
    parts = [Code(p.name)]
    if p.anno: parts.append(Span(f": {p.anno}", style="color: #666;"))
    if p.default: parts.append(Span(f" = {p.default}", style="color: #888;"))
    if p.doc: parts.append(Span(f" — {p.doc}", style="color: #555; font-style: italic;"))
    return Li(*parts)

def nb_path(mod_name, root='.'):
    cfg = read_config(root)
    for f in (Path(root) / cfg.nbs).glob('*.py'):
        if nb_name(f, root) == mod_name: return f.relative_to(root)
    return None

def html_preview(width='100%', height='300px'):
    "Display FT components in an IFrame"
    def _preview(*components): show(Iframe(srcdoc=to_xml(components[0] if len(components) == 1 else Div(*components)), width=width, height=height))
    return _preview

def render_index_page(meta, mods, repo_url=None):
    mod_names = [name for name, _ in mods]
    head_elements = [
        Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js"),
        Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css"),
        Script(src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"),
        Script("hljs.highlightAll();"),
        Style("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; } code { font-family: 'SF Mono', Consolas, monospace; }"),
        Title(meta['name'])]
    nav_links = [Li(A(m, href=f"{m}.html", style="color: #aaa; text-decoration: none;")) for m in mod_names]
    nav = Nav(
        H3(meta['name'], style="margin: 0 0 1rem 0; color: #fff;"),
        Ul(*nav_links, style="list-style: none; padding: 0; margin: 0;"),
        style="padding: 1rem; background: #1a1a1a; min-width: 180px;")
    module_cards = [A(Div(H3(name, style="margin: 0 0 0.5rem 0; color: #fff;"), P(f"{len([n for n in nodes if n.kind == Kind.EXP])} exports", style="margin: 0; color: #888;"), 
        style="padding: 1rem; background: #1e1e1e; border-radius: 8px;"), href=f"{name}.html", style="text-decoration: none;") for name, nodes in mods]
    content = Div(
        H1(meta['name'], style="margin: 0 0 0.5rem 0; color: #fff;"),
        P(meta['desc'], style="color: #888; margin: 0 0 2rem 0;"),
        P(f"Version {meta['version']}", style="color: #666; margin: 0 0 2rem 0; font-size: 0.9rem;"),
        H2("Modules", style="color: #fff; margin: 0 0 1rem 0; font-size: 1.2rem;"),
        Div(*module_cards, style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;"),
        style="padding: 2rem; flex: 1;")
    body = Body(nav, content, style="display: flex; min-height: 100vh; margin: 0; background: #121212;")
    return Html(Head(*head_elements), body)
