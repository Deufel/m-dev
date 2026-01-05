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
    import ast, re, os
    import marimo as mo
    from functools import partial

    from fastcore.xml import Span, Code, Li, Article, Div, Ul, P, FT, to_xml, Pre, Link, A, Iframe, Button, H1, H2, H3, Nav, Aside, Header, Input, NotStr, Strong, Main
    from fasthtml.components import ft, Html, Head, Script, Body, show, Style, Title

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
    if n.methods or 'class ' in n.src: return 'class'
    if n.src.lstrip().startswith('async def'): return 'async'
    return 'func'


@app.function
def render_param(p):
    parts = [Code(p.name)]
    if p.anno: parts.append(Span(f": {p.anno}", style="color: #666;"))
    if p.default: parts.append(Span(f" = {p.default}", style="color: #888;"))
    if p.doc: parts.append(Span(f" — {p.doc}", style="color: #555; font-style: italic;"))
    return Li(*parts)


@app.cell
def _():

    # meta, mods = scan()
    # nodes = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
    # print(f"Found {len(nodes)} export nodes")

    # Div(*[render_node(n) for n in nodes[:10]])
    return


@app.function
def nb_path(mod_name, root='.'):
    cfg = read_config(root)
    for f in (Path(root) / cfg.nbs).glob('*.py'):
        if nb_name(f, root) == mod_name: return f.relative_to(root)
    return None


@app.cell
def _():
    return


@app.cell
def _(Icon):
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
        btn_style = "display: flex; align-items: center; gap: 0.25rem; background: #333; border: 1px solid #444; color: #ccc; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.75rem;"
        link_style = "text-decoration: none;"
        copy_btn = Button("📋", onclick=f"navigator.clipboard.writeText(document.getElementById('{node_id}').textContent).then(() => this.textContent = '✓').then(() => setTimeout(() => this.textContent = '📋', 1500))", style="background: transparent; border: none; cursor: pointer; font-size: 0.9rem; padding: 0.25rem;")
        source_btn = A(Button(Icon('github', size=16), "Source", style=btn_style), href=f"{repo_url}/blob/master/{nb}#L{n.lineno}", target="_blank", style=link_style) if repo_url and nb and n.lineno else None
        edit_btn = A(Button(Icon('code', size=16), "Edit", style=btn_style), href=f"{repo_url}/edit/master/{nb}", target="_blank", style=link_style) if repo_url and nb else None
        blame_btn = A(Button(Icon('info', size=16), "Blame", style=btn_style), href=f"{repo_url}/blame/master/{nb}#L{n.lineno}", target="_blank", style=link_style) if repo_url and nb and n.lineno else None
        history_btn = A(Button(Icon('calendar', size=16), "History", style=btn_style), href=f"{repo_url}/commits/master/{nb}", target="_blank", style=link_style) if repo_url and nb else None
        issue_btn = A(Button(Icon('circle-x', size=16), "Issue", style=btn_style), href=f"{repo_url}/issues/new?title=Issue%20with%20{n.name}&body=Found%20in%20{nb}%23L{n.lineno}", target="_blank", style=link_style) if repo_url and nb else None
        header = Div(
            Div(tag, full_name, style="display: flex; align-items: center;"),
            Div(copy_btn, source_btn, edit_btn, blame_btn, history_btn, issue_btn, style="display: flex; align-items: center; gap: 0.5rem;"),
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
        search_input = Input(type="text", placeholder="Search...", style="width: 100%; padding: 0.5rem; border: 1px solid #333; border-radius: 4px; background: #252525; color: #fff; margin-bottom: 1rem;", **{"data-bind": "search"})
        nav_links = [Li(A("← Index", href="index.html", style="color: #888; text-decoration: none; font-size: 0.85rem;"))] + [Li(A(m, href=f"{m}.html", style=f"color: {'#fff' if m == mod_name else '#aaa'}; text-decoration: none;")) for m in all_mod_names]
        nav = Nav(
            H3(meta['name'], style="margin: 0 0 1rem 0; color: #fff;"),
            search_input,
            Ul(*nav_links, style="list-style: none; padding: 0; margin: 0;"),
            style="padding: 1rem; background: #1a1a1a; min-width: 180px;")
        btn_style = "display: flex; align-items: center; gap: 0.25rem; background: #333; border: 1px solid #444; color: #ccc; padding: 0.5rem 0.75rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem;"
        wasm_btn = A(Button(Icon('external-link', size=16), "Run in Browser", style=btn_style), href=f"wasm/{mod_name}.html", target="_blank", style="text-decoration: none;")
        header = Header(
            Div(H1(mod_name, style="margin: 0; font-size: 1.5rem; color: #fff;"), wasm_btn, style="display: flex; align-items: center; justify-content: space-between;"),
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
    return (build_docs,)


@app.cell
def _(build_docs):
    build_docs()
    return


@app.function
def export_wasm(root='.'):
    cfg = read_config(root)
    nbs_dir = Path(root) / cfg.nbs
    wasm_dir = Path(root) / cfg.docs / 'wasm'
    wasm_dir.mkdir(parents=True, exist_ok=True)
    for f in nbs_dir.glob('*.py'):
        name = nb_name(f, root)
        if name: os.system(f"marimo export html-wasm {f} -o {wasm_dir}/{name} --mode edit")


@app.cell
def _():
    export_wasm()
    return


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
def _():
    icons = {
        'home':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-house-icon lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>',
        "pypi":'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-blocks-icon lucide-blocks"><path d="M10 22V7a1 1 0 0 0-1-1H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5a1 1 0 0 0-1-1H2"/><rect x="14" y="2" width="8" height="8" rx="1"/></svg>',
        'menu':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu-icon lucide-menu"><path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg>',
        'x':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x-icon lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
        'github':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-github-icon lucide-github"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>',
        'code':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-code-icon lucide-code"><path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/></svg>',
        'info':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info-icon lucide-info"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
        'calendar':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar1-icon lucide-calendar-1"><path d="M11 14h1v4"/><path d="M16 2v4"/><path d="M3 10h18"/><path d="M8 2v4"/><rect x="3" y="4" width="18" height="18" rx="2"/></svg>',
        'circle-x':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-x-icon lucide-circle-x"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>',
        'external-link':'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link-icon lucide-external-link"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>',
    
    


    }
    return (icons,)


@app.cell
def _(Icon):
    Icon("home")
    return


@app.cell
def _(icons):

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
    return (Icon,)


@app.cell
def _(Icon):
    def Page(main_content, nav_items, title="Documentation"):
        head_elements = [
            Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js"),
            Title(title)]

        signals = "{_header: true, _nav: true, _footer: false, _aside: false}"
        body_style = "background: lightgrey; margin:0; height: 100svh; display:grid; grid-template: auto 1fr auto / auto 1fr auto; gap: 0.5em;"

        nav_btn = Button(Icon('menu'), style="background: none; border: none; cursor: pointer;", **{"data-on:click": "$_nav = !$_nav"})
        left = Div(nav_btn, H1(title), cls="--make-cluster")

        middle = Input(type="text", placeholder="Search...", style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;")

        right = Div(
            A(Icon('github'), href="https://github.com/user/repo", target="_blank", style="color: inherit;"),
            A(Icon('pypi'), href="https://pypi.org/project/marimo-dev", target="_blank", style="color: inherit;"),
            cls="--make-cluster")

        header = Header(
            Div(left, middle, right, cls="--make-lcr"),
            style="background: white; border-radius: 0.5em; border: 1px solid #ddd; display:none; padding: 0.5em;",
            **{"data-style:grid-area": "'1/1/2/-1'", "data-show": "$_header"})

        nav_links = [Li(A(n, href=f"{n}.html")) for n in nav_items]
        nav = Nav(
            Strong("NAV"),
            Ul(*nav_links, style="list-style-type: none; margin-inline: 0; padding: 10px;"),
            style="background: white; border-radius: 0.5em; border: 1px solid #ddd; display:none;",
            **{"data-show": "$_nav", "data-effect": "$_navArea = `${1+$_header}/1/${3+!$_footer}/2`", "data-style:grid-area": "$_navArea"})

        main = Main(
            main_content,
            style="background: white; border-radius: 0.5em; border: 1px solid #ddd; transition: max-height 0.4s ease;",
            **{"data-effect": "$_mainArea = `${1+$_header}/${1+$_nav}/${3+!$_footer}/${3+!$_aside}`", "data-style:grid-area": "$_mainArea"})

        return Html(Head(*head_elements), Body(header, nav, main, style=body_style, **{"data-signals": signals}))


    html_preview(height='400px')(Page(Div(H2("Main Content"), P("Hello world")), ['readme', 'core', 'utils']))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
