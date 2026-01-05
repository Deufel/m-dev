import marimo

__generated_with = "0.18.4"
app = marimo.App(
    width="full",
    css_file="styles.css",
    html_head_file="mike.html",
)

with app.setup:
    from a_core import Kind, Param, Node, Config, read_config
    from b_read import scan, nb_name, read_meta
    from pathlib import Path
    import ast
    import marimo as mo
    from functools import partial

    from fastcore.xml import Span, Code, Li, Article, Div, Ul, P, FT, to_xml, Pre, Link, A, Iframe, Button, H1, H2, H3, Nav, Aside, Header, Input
    from fasthtml.components import Html, Head, Script, Body, show, Style, Title

    def _repr_html_(self):
        return str(to_xml(self))

    FT._repr_html_ = _repr_html_


@app.function
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


@app.function
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


@app.function
def sig(
    n:Node, # the node to generate signature for
)->str:     # formatted signature string
    "Generate a signature string for a class or function node."
    t = exp_type(n)
    if t == 'class': return cls_sig(n, dataclass=n.src.lstrip().startswith('@dataclass'))
    return fn_sig(n, is_async=t == 'async')


@app.function
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


@app.function
def exp_type(n):
    src = n.src.lstrip()
    if n.methods or src.startswith(('@dataclass', 'class ')): return 'class'
    if src.startswith('async def'): return 'async'
    return 'func'


@app.function
def render_param(p):
    parts = [Code(p.name)]
    if p.anno: parts.append(Span(f": {p.anno}", style="color: #666;"))
    if p.default: parts.append(Span(f" = {p.default}", style="color: #888;"))
    if p.doc: parts.append(Span(f" — {p.doc}", style="color: #555; font-style: italic;"))
    return Li(*parts)


@app.cell
def _(render_node):

    meta, mods = scan()
    nodes = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
    print(f"Found {len(nodes)} export nodes")

    Div(*[render_node(n) for n in nodes[:10]])
    return meta, mods


@app.function
def nb_path(mod_name, root='.'):
    cfg = read_config(root)
    for f in (Path(root) / cfg.nbs).glob('*.py'):
        if nb_name(f, root) == mod_name: return f.relative_to(root)
    return None


@app.cell
def _():
    def render_node(n, repo_url=None, root='.'):
        t = exp_type(n)
        signature = sig(n)
        lines = signature.split('\n')
        line_nums = '\n'.join(str(i+1) for i in range(len(lines)))
        node_id = f"code-{n.module}-{n.name}"
        tag_colors = {'func': '#10b981', 'async': '#f59e0b', 'class': '#8b5cf6'}
        tag = Span(t, style=f"padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: {tag_colors.get(t, '#666')}; color: white;")
        full_name = Span(Span(f"{n.module}.", style="color: #666;"), Span(n.name, style="color: #e5e5e5;"), style="font-weight: 500; font-size: 1rem; margin-left: 0.75rem;") if n.module else Span(n.name, style="font-weight: 500; font-size: 1rem; color: #e5e5e5; margin-left: 0.75rem;")
        nb = nb_path(n.module, root)
        source_url = f"{repo_url}/blob/main/{nb}" if repo_url and nb else None
        copy_btn = Button("📋", onclick=f"navigator.clipboard.writeText(document.getElementById('{node_id}').textContent).then(() => this.textContent = '✓').then(() => setTimeout(() => this.textContent = '📋', 1500))",
            style="background: transparent; border: none; cursor: pointer; font-size: 0.9rem; padding: 0.25rem;")
        header = Div(
            Div(tag, full_name, style="display: flex; align-items: center;"),
            Div(copy_btn, A("↗", href=source_url, target="_blank", style="color: #666; text-decoration: none;") if source_url else None, style="display: flex; align-items: center; gap: 0.5rem;"),
            style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem;")
        doc_line = P(n.doc, style="margin: 0; padding: 0 1rem 0.5rem 1rem; color: #888; font-size: 0.85rem;") if n.doc else None
        code_block = Div(
            Pre(Code(line_nums), style="margin: 0; padding: 0; color: #555; text-align: right; user-select: none; font-size: 0.8rem; line-height: 1.6;"),
            Pre(Code(signature, cls="language-python", id=node_id), style="margin: 0; padding: 0; flex: 1; overflow-x: auto; font-size: 0.8rem; line-height: 1.6;"),
            style="display: flex; background: #1a1a1a; border-top: 1px solid #2a2a2a;")
        return Article(header, doc_line, code_block, style="margin-bottom: 0.75rem; border-radius: 8px; overflow: hidden; background: #1e1e1e;")

    def render_module_page(mod_name, mod_nodes, all_mod_names, meta, root='.'):
        repo_url = meta.get('urls', {}).get('Repository')
        exp_nodes = [n for n in mod_nodes if n.kind == Kind.EXP]
        content = Div(*[render_node(n, repo_url, root) for n in exp_nodes], style="padding: 1rem; background: #121212; overflow-y: auto;")
        head_elements = [
            Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js"),
            Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css"),
            Script(src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"),
            Script("hljs.highlightAll();"),
            Style("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; } code { font-family: 'SF Mono', Consolas, monospace; }"),
            Title(f"{mod_name} - {meta['name']}")]
        search_input = Input(type="text", placeholder="Search...", style="width: 100%; padding: 0.5rem; border: 1px solid #333; border-radius: 4px; background: #252525; color: #fff; margin-bottom: 1rem;",
            **{"data-bind": "search"})
        nav_links = [Li(A("← Index", href="index.html", style="color: #888; text-decoration: none; font-size: 0.85rem;"))] + [Li(A(m, href=f"{m}.html", style=f"color: {'#fff' if m == mod_name else '#aaa'}; text-decoration: none;")) for m in all_mod_names]
        nav = Nav(
            H3(meta['name'], style="margin: 0 0 1rem 0; color: #fff;"),
            search_input,
            Ul(*nav_links, style="list-style: none; padding: 0; margin: 0;"),
            style="padding: 1rem; background: #1a1a1a; min-width: 180px;")
        header = Header(
            H1(mod_name, style="margin: 0; font-size: 1.5rem; color: #fff;"),
            style="padding: 1rem; background: #1e1e1e; border-bottom: 1px solid #333;")
        body = Body(nav, Div(header, content, style="flex: 1; display: flex; flex-direction: column;"), style="display: flex; height: 100vh; margin: 0; background: #121212;", **{"data-signals": "{search: ''}"})
        return Html(Head(*head_elements), body)

    def build_docs(root='.'):
        cfg = read_config(root)
        meta = read_meta(root)
        _, mods = scan(root)
        mod_names = [name for name, _ in mods]
        docs_path = Path(root) / cfg.docs
        docs_path.mkdir(exist_ok=True)
        (docs_path / "index.html").write_text(to_xml(render_index_page(meta, mods)))
        for mod_name, mod_nodes in mods:
            (docs_path / f"{mod_name}.html").write_text(to_xml(render_module_page(mod_name, mod_nodes, mod_names, meta, root)))
        return f"Generated index + {len(mods)} module pages in {docs_path}"

    build_docs()
    return (render_node,)


@app.function
def html_preview(width='100%', height='300px'):
    "Display FT components in an IFrame"
    def _preview(*components): show(Iframe(srcdoc=to_xml(components[0] if len(components) == 1 else Div(*components)), width=width, height=height))
    return _preview


@app.function
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


@app.cell
def _(meta, mods):
    html_preview(height='400px')(render_index_page(meta, mods, "https://github.com/user/repo"))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
