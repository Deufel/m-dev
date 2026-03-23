from .core import Kind, Param, Node, Config, read_config
from .read import scan, nb_name, read_meta
from .pkg import clean
from .build import bundle_notebook
import ast, re, tomllib, json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
import os, sys, subprocess, configparser, shutil
from functools import partial
from html_tags import mktag, setup_svg, Tag

Link = mktag('link', self_closing=True)
icons = {'home': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-house-icon lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>', 'pypi': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-blocks-icon lucide-blocks"><path d="M10 22V7a1 1 0 0 0-1-1H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5a1 1 0 0 0-1-1H2"/><rect x="14" y="2" width="8" height="8" rx="1"/></svg>', 'menu': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu-icon lucide-menu"><path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg>', 'x': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x-icon lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>', 'github': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-github-icon lucide-github"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>', 'code': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-code-icon lucide-code"><path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/></svg>', 'info': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info-icon lucide-info"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>', 'calendar': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar1-icon lucide-calendar-1"><path d="M11 14h1v4"/><path d="M16 2v4"/><path d="M3 10h18"/><path d="M8 2v4"/><rect x="3" y="4" width="18" height="18" rx="2"/></svg>', 'circle-x': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-x-icon lucide-circle-x"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>', 'external-link': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link-icon lucide-external-link"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>'}
COLORS = {'keyword': '#c792ea', 'string': '#c3e88d', 'builtin': '#82aaff', 'decorator': '#f78c6c', 'comment': '#546e7a', 'number': '#f78c6c', 'punctuation': '#89ddff', 'defname': '#82aaff', 'classname': '#ffcb6b', 'operator': '#89ddff', 'call': '#82aaff', 'fstring': '#c3e88d', 'type': '#ffcb6b'}

Div, Span, P, A, Button, Pre, Code, Li, Ul = (mktag(t) for t in 
        'div span p a button pre code li ul'.split())
H1, H2, H3, Nav, Article, Header, Main, Aside = (mktag(t) for t in
        'h1 h2 h3 nav article header main aside'.split())
Html, Head, Body, Title, Input, Strong = (mktag(t) for t in
        'html head body title input strong'.split())
Script, Style, Iframe = (mktag(t, mode='raw') for t in
        'script style iframe'.split())

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

    code_lines = [Span(cls="code-line")(line) for line in signature.split('\n')]

    def ghbtn(icon, label, url):
        if not url: return None
        return A(href=url, target="_blank", cls="gh-link")(
            Button(cls="gh-btn")(Icon(icon, size=16), label))

    tag = Span(cls="tag", style=f"background:{tag_colors.get(t, '#666')};")(t)
    mod_name = Span(cls="full-name")(Span(cls="mod")(f"{n.module}."), Span(cls="name")(n.name)) if n.module else Span(cls="full-name name")(n.name)

    copy_btn = Button(cls="copy-btn", onclick=f"navigator.clipboard.writeText(document.getElementById('{node_id}').textContent).then(() => this.textContent = '✓').then(() => setTimeout(() => this.textContent = '📋', 1500))")("📋")
    source_btn = ghbtn('github', 'Source', f"{repo_url}/blob/master/{nb}#L{n.lineno}" if repo_url and nb and n.lineno else None)
    edit_btn = ghbtn('code', 'Edit', f"{repo_url}/edit/master/{nb}" if repo_url and nb else None)
    blame_btn = ghbtn('info', 'Blame', f"{repo_url}/blame/master/{nb}#L{n.lineno}" if repo_url and nb and n.lineno else None)
    history_btn = ghbtn('calendar', 'History', f"{repo_url}/commits/master/{nb}" if repo_url and nb else None)
    issue_btn = ghbtn('circle-x', 'Issue', f"{repo_url}/issues/new?title=Issue%20with%20{n.name}&body={repo_url}/blob/master/{nb}%23L{n.lineno}" if repo_url and nb and n.lineno else None)

    return Article()(
        Style()("""
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
        Div(cls="header")(
            Div(cls="header-left")(tag, mod_name),
            Div(cls="header-right")(copy_btn, source_btn, edit_btn, blame_btn, history_btn, issue_btn)),
        P(cls="doc")(n.doc) if n.doc else None,
        Pre()(Code(cls="language-python", id=node_id)(*code_lines)))

def render_module_page(mod_name, mod_nodes, all_mod_names, meta, root='.'):
    '''Builds a Module Page'''
    repo_url = meta.get('urls', {}).get('Repository')
    exp_nodes = [n for n in mod_nodes if n.kind == Kind.EXP]

    head_elements = [
        Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.8/bundles/datastar.js")(),
        mktag('script', mode='raw')(src="https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js")(),
        Script(src="js/highlight.js", type="module")(),
        Style()("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; } code { font-family: 'SF Mono', Consolas, monospace; }"),
        Title()(f"{mod_name} - {meta['name']}")]

    nav_links = [Li()(A(href="index.html", cls="back-link")("← Index"))] + [
        Li()(A(href=f"{m}.html", cls=f"nav-link {'active' if m == mod_name else ''}")(m)) for m in all_mod_names]

    nav = Nav()(
        Style()("""
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
        H3()(meta['name']),
        Input(type="text", placeholder="Search...", **{"data-bind": "search"})(),
        Ul()(*nav_links))

    header = Header()(
        Style()("""
            me { padding: 1rem; background: #1e1e1e; border-bottom: 1px solid #333; }
            me .header-row { display: flex; align-items: center; justify-content: space-between; }
            me h1 { margin: 0; font-size: 1.5rem; color: #fff; }
            me .wasm-btn { display: flex; align-items: center; gap: 0.25rem; background: #333; border: 1px solid #444; color: #ccc; padding: 0.5rem 0.75rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
            me .wasm-link { text-decoration: none; }
        """),
        Div(cls="header-row")(
            H1()(mod_name),
            A(href=f"wasm/{mod_name}/index.html", target="_blank", cls="wasm-link")(
                Button(cls="wasm-btn")(Icon('external-link', size=16), "Run in Browser"))))

    content = Div()(
        Style()("""
            me { padding: 1rem; background: #121212; overflow-y: auto; flex: 1; }
        """),
        *[render_node(n, repo_url, root) for n in exp_nodes])

    body = Body(style="display: flex; height: 100vh; margin: 0; background: #121212;", **{"data-signals": "{search: ''}"})(
        nav,
        Div(style="flex: 1; display: flex; flex-direction: column;")(header, content))

    return Html()(Head()(*head_elements), body)

def render_index_page(meta, mods, repo_url=None):
    mod_names = [name for name, _ in mods]
    head_elements = [
        Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js")(),
        mktag('script', mode='raw')(src="https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js")(),
        Script(src="js/highlight.js", type="module")(),
        Style()("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; } code { font-family: 'SF Mono', Consolas, monospace; }"),
        Title()(meta['name'])]

    nav_links = [Li()(A(href=f"{m}.html", cls="nav-link")(m)) for m in mod_names]

    nav = Nav()(
        Style()("""
            me { padding: 1rem; background: #1a1a1a; min-width: 180px; }
            me h3 { margin: 0 0 1rem 0; color: #fff; }
            me ul { list-style: none; padding: 0; margin: 0; }
            me .nav-link { color: #aaa; text-decoration: none; }
            me .nav-link:hover { color: #fff; }
        """),
        H3()(meta['name']),
        Ul()(*nav_links))

    module_cards = [A(href=f"{name}.html", cls="card-link")(
        Div(cls="card")(
            H3(cls="card-title")(name),
            P(cls="card-count")(f"{len([n for n in nodes if n.kind == Kind.EXP])} exports")))
        for name, nodes in mods]

    content = Div()(
        Style()("""
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
        H1()(meta['name']),
        P(cls="desc")(meta['desc']),
        P(cls="version")(f"Version {meta['version']}"),
        H2()("Modules"),
        Div(cls="grid")(*module_cards))

    body = Body(style="display: flex; min-height: 100vh; margin: 0; background: #121212;")(nav, content)
    return Html()(Head()(*head_elements), body)

def html_preview(width='100%', height='300px'):
    "Display FT components in an IFrame"
    from IPython.display import display, HTML
    def _preview(*components):
        html = str(components[0]) if len(components) == 1 else str(Div()(*components))
        display(HTML(f'<iframe srcdoc="{html}" width="{width}" height="{height}"></iframe>'))
    return _preview

def build_docs(root='.'):
    '''Builds the static documentation website'''
    cfg = read_config(root)
    meta = read_meta(root)
    _, mods = scan(root)
    mod_names = [name for name, _ in mods]
    docs_path = Path(root) / cfg.docs
    docs_path.mkdir(exist_ok=True)
    (docs_path / "index.html").write_text(str(render_index_page(meta, mods)))
    for mod_name, mod_nodes in mods:
        (docs_path / f"{mod_name}.html").write_text(str(render_module_page(mod_name, mod_nodes, mod_names, meta, root)))
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

def Icon(name: str,            # name of the icon MUST be in icon_dict
         size=24,              # value to be passed to height and width of the icon
         stroke=1.5,           # stroke width 
         cls=None,             # css class
         icon_dict:dict=icons, # Dict of icons {"name":"<svg...>"}
         **kwargs              # passed through to tag
        ):
    '''Creates a custom html compliant <icon-{name}>...'''
    if name not in icon_dict: raise ValueError(f"Icon '{name}' not found")

    svg_string = icon_dict[name]
    svg_string = re.sub(r'width="\d+"', f'width="{size}"', svg_string, count=1)
    svg_string = re.sub(r'height="\d+"', f'height="{size}"', svg_string, count=1)
    svg_string = re.sub(r'stroke-width="\d+"', f'stroke-width="{stroke}"', svg_string)

    return mktag(f'icon-{name}', mode='raw')(cls=cls, **kwargs)(svg_string)

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
