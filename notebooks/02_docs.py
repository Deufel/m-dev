import marimo

__generated_with = "0.17.8"
app = marimo.App(width="full", html_head_file="head.html")

with app.setup:
    from fasthtml.components import Form, Input, Div, P, Button, Span, Br, Hr, Pre, Code, NotStr, Html, Head, Aside, Nav, Main, Footer, Iframe, Body, Script, to_xml, show, Style, H1, H2, H3, H4, H5, H6, A, Title, Details, Summary, Article, Ul, Li, Small, Header, Footer
    import inspect
    import ast
    from fastcore.docments import docments, docstring, get_source
    from fastcore.xml import FT
    from pathlib import Path


@app.cell
def _():
    import marimo as mo
    import pytest
    from typing import Callable

    # Helpful "monkey patch" for viewing components in marimo 
    #def _display_(self): return mo.md(f"{self}")
    #FT._display_ = _display_
    return (mo,)


@app.function
def extract_builtin_func_info(func):
    "Extract function name, params, return type, and docstring from function object"
    is_builtin = inspect.isbuiltin(func)
    # some kinf of assert here? 
    assert inspect.isbuiltin(func) or not inspect.isfunction(func), "Use extract_func_info_docments for regular Python functions"

    name = func.__name__
    docstr = inspect.getdoc(func) or ''
    try:
        sig = inspect.signature(func)
        params = [(param.name, str(param.annotation) if param.annotation != inspect.Parameter.empty else None) 
                for param in sig.parameters.values()]
        ret_type = str(sig.return_annotation) if sig.return_annotation is not inspect.Signature.empty else None
    except ValueError:
        params = []
        ret_type = None
    return {'name': name, 'params': params, 'return': ret_type, 'docstring': docstr, 'source': 'Built-in function', 'is_builtin': True}


@app.function
def extract_func_info_docments(func):
    """Extract function info using fastcore.docments"""
    try:
        # Get the docments with full info (types, defaults, comments)
        docs = docments(func, full=True)

        # Build params list: [(name, type_annotation)]
        params = [(name, str(info['anno']) if info['anno'] != inspect.Parameter.empty else None) 
                  for name, info in docs.items() 
                  if name != 'return']

        # Get return type
        ret_info = docs.get('return', {})
        ret_type = str(ret_info.get('anno')) if ret_info.get('anno') != inspect.Parameter.empty else None

        return {
            'name': func.__name__,
            'params': params,
            'return': ret_type,
            'docstring': docstring(func) or '',
            'source': get_source(func),
            'is_builtin': False
        }
    except Exception:
        return extract_builtin_func_info(func)


@app.cell
def _():
    def sample_func_a(a: int, b: str = "hello") -> bool:
            """A sample function"""
            return True

    def sample_func_b(
        a: int, 
        b: str = "hello"
    ) -> bool:
            """A sample function"""
            return True
    return sample_func_a, sample_func_b


@app.cell(hide_code=True)
def _(sample_func_a, sample_func_b):
    def test_extract_func_info_docments_1():
        result = extract_func_info_docments(sample_func_b)
        assert result['name'] == 'sample_func_b'
        assert result['params'] == [('a', "<class 'int'>"), ('b', "<class 'str'>")]
        assert result['return'] == "<class 'bool'>"
        assert result['docstring'] == 'A sample function'
        assert result['is_builtin'] == False

    def test_extract_func_info_docments_2():
        result = extract_func_info_docments(sample_func_a)
        assert result['name'] == 'sample_func_a'
        assert result['params'] == [('a', "<class 'int'>"), ('b', "<class 'str'>")]
        assert result['return'] == "<class 'bool'>"
        assert result['docstring'] == 'A sample function'
        assert result['is_builtin'] == False

    def test_extract_func_docments_ccode():
        import math
        result = extract_func_info_docments(math.hypot)
        assert result['name'] == 'hypot'
        assert result['params'] == []
        assert result['return'] == None
        assert result['docstring'] == 'hypot(*coordinates) -> value\n\nMultidimensional Euclidean distance from the origin to a point.\n\nRoughly equivalent to:\n    sqrt(sum(x**2 for x in coordinates))\n\nFor a two dimensional point (x, y), gives the hypotenuse\nusing the Pythagorean theorem:  sqrt(x*x + y*y).\n\nFor example, the hypotenuse of a 3/4/5 right triangle is:\n\n    >>> hypot(3.0, 4.0)\n    5.0'
        assert result['is_builtin'] == True
    return


@app.function
def search_form():
    "Render search form with tag support"
    return Form(
        Input(type='text', placeholder='Live Search ...(enter to add tag)', **{'data-bind:search': True}),
        Button('Add Tag', type='submit'),
        Button('Clear All', type='button', cls='clear-btn', **{'data-on:click': "$tags = [], $search = ''"}),
        cls='search-section',
        **{'data-on:submit__prevent': "$search.trim() ? ($tags = [...$tags, $search.trim()], $search = '') : null"}
    )


@app.function
def debug_area():
    "Render debug/tags display area"
    return Div(
        Div(
            'Tags: ', Span('[]', **{'data-text': 'JSON.stringify($tags)'}), Br(),
            'Search: ', Span(**{'data-text': '$search'}),
            cls='debug-info'
        ),
        Button('Clear All', type='button', cls='clear-btn', **{'data-on:click': "$tags = [], $search = ''"}),
        cls='debug'
    )


@app.function
def old_render_func_card(info, idx):
    "Render function with relevance ordering and match counting"
    searchable = f"{info['name']} {' '.join([n for n,t in info['params']])} {info['docstring']}".lower().replace("'", "\\'").replace("\n", " ")
    match_var = f"matchCount{idx}"
    searchable_var = f"searchable{idx}"
    params_str = ', '.join([f"{name}: {typ}" if typ else name for name,typ in info['params']])
    sig = f"{info['name']}({params_str})"
    if info['return']: sig += f" -> {info['return']}"
    return Div(
        Span('0', cls='match-badge', style='display: none;', **{'data-show': NotStr('$tags.length > 0 || $search.trim().length > 0'), 'data-text': f'${match_var}'}),
        Div(Code(sig), cls='attribute-name'),
        Div(info['docstring'], Pre(Code(info['source'])), cls='description'),
        id=info['name'],
        cls='attribute',
        **{'data-signals': NotStr(f"{{ {searchable_var}: '{searchable}', {match_var}: 0 }}"), 'data-effect': NotStr(f"${match_var} = [...$tags, $search.trim()].filter(tag => tag.length > 0 && ${searchable_var}.toLowerCase().includes(tag.toLowerCase())).length"), 'data-show': NotStr(f"($tags.length === 0 && $search.trim().length === 0) || ${match_var} > 0"), 'data-style:order': NotStr(f"($tags.length === 0 && $search.trim().length === 0) ? {idx} : -${match_var}")}
    )


@app.cell
def _():
    def _render_func_card(info, idx):
        """Render a beautiful, searchable function card with module, collapsible source, and full type info"""
        name = info['name']
        module = info.get('module', f"<built-in>")
        params = info['params']
        return_type = info['return']
        docstring = info['docstring'] or "No docstring available."
        source = info['source']

        # Build searchable text (used by Data* for filtering)
        searchable_text = f"{name} {module} {' '.join([n for n, _ in params])} {docstring}".lower()
        searchable_text = searchable_text.replace("'", "\\'").replace("\n", " ")

        # Unique signal names per card
        match_var = f'matchCount{idx}'
        searchable_var = f'searchable{idx}'

        # Build pretty signature: func(arg1: int, arg2: str = 'default') -> Optional[List[str]]
        param_parts = []
        for param_name, param_type in params:
            if param_type and param_type != 'None':
                param_parts.append(f"{param_name}: {param_type}")
            else:
                param_parts.append(param_name)
        signature = f"{name}({', '.join(param_parts)})"
        if return_type and return_type != 'None':
            signature += f" → {return_type}"

        return Div(
            # main card
            # Match badge (top-right)
            Span('0', cls='match-badge', style='display:none;',
                 data_show=NotStr('$tags.length > 0 || $search.trim().length > 0'),
                 data_text=f'${match_var}'),

            # Header: name + module
            Div(
                H2(name, cls='func-name'),
                Span(f"Module: {module}", cls='func-module'),
                cls='func-header'
            ),

            # Signature
            Code(signature, cls='func-signature'),

            # Docstring
            P(docstring, cls='func-docstring'),

            # Collapsible source code
            Div(
                Details(
                    Summary("Source code ▼", style="cursor:pointer; color:#2563eb; font-weight:600; margin:0.5rem 0;"),
                    Pre(Code(source, language='python'), style="margin:0;")
                ),
                cls='source-section'
            ),

            # Hidden signals & effects (unchanged logic)
            id=name,
            cls='attribute',
            data_signals=NotStr(f"{{ {searchable_var}: '{searchable_text}', {match_var}: 0 }}"),
            data_effect=NotStr(
                f'${match_var} = [...$tags, $search.trim()]'
                f'.filter(t => t && ${searchable_var}.includes(t.toLowerCase())).length'
            ),
            data_show=NotStr(f'($tags.length === 0 && $search.trim().length === 0) || ${match_var} > 0'),
            data_style_order=NotStr(f'($tags.length === 0 && $search.trim().length === 0) ? {idx} : -${match_var}')
        )
    return


@app.function
def sidenav(funcs_info):
    "Render sidebar navigation with match counts"
    items = [A(
        Span(info['name']),
        Span('0', cls='nav-badge', style='display: none;', **{'data-show': NotStr('$tags.length > 0 || $search.trim().length > 0'), 'data-text': f'$matchCount{i}'}),
        href=f"#{info['name']}", cls='nav-item',
        **{'data-class:disabled': NotStr(f"($tags.length > 0 || $search.trim().length > 0) && $matchCount{i} === 0")}
    ) for i,info in enumerate(funcs_info)]
    return Aside(H3('Functions'), *items, cls='sidenav')


@app.cell
def _(render_func_card):
    def doc_page(funcs):
        "Generate complete HTML page with new template design"
        funcs_info = [extract_func_info_docments(f) for f in funcs]

        func_cards = [render_func_card(info, i) for i,info in enumerate(funcs_info)]
        return Body(
                search_form(),
                Div(Div(H1('Documentation'), P('Interactive documentation with live search and relevance-based ordering', cls='subtitle'), cls='title-section'), cls='header'),
                debug_area(),
                Div(sidenav(funcs_info), Div(Div(*func_cards, cls='attributes'), cls='main-content'), cls='content-wrapper'),
                **{'data-signals': "{ search: '', tags: [] }"}
            )
    return (doc_page,)


@app.function
def DS(*components, width='100%', height='300px'):
    """Display FT components with isolated Datastar in an IFrame"""
    datastar_url = 'https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js'
    datastar_script = Script(type='module', src=datastar_url)
    doc = Html(Head(datastar_script), Body(*components))
    return Iframe(srcdoc=to_xml(doc), width=width, height=height)


@app.function
def get_module_funcs(module):
    "Extract all functions from a module"
    return [obj for name, obj in inspect.getmembers(module) 
            if inspect.isroutine(obj) and obj.__module__ == module.__name__]


@app.cell
def _(doc_page):
    def _doc_module(module, width='100%', height='600px'):
        """Generate documentation page for all functions in a module"""
        funcs = get_module_funcs(module)
        return doc_page(funcs)
    return


@app.function
def write_to_docs(
    content,                             # FTs
    filepath: str = "./docs/index.html", # filepath
    title: str = "docs"                  # document title
) -> str:                                # file:// URI string
    """Save content as a standalone Datastar-ready HTML file and return the path as string"""

    html_string = to_xml(
        Html(
            Head(
                Title(title),
                Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"),
                Style("""
      * {
        scrollbar-gutter: stable;
      }
      body{
        font-family:sans-serif;
        max-width:1400px;
        margin:1rem auto;
        padding:0 1rem;
        line-height:1.5;
      }
      .header{
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        margin-bottom:1rem;
        gap:2rem;
      }
      .title-section{
        flex:1;
      }
      .search-section{
        position:fixed;
        top:1rem;
        right:1rem;
        z-index:100;
        display:flex;
        gap:0.5rem;
        align-items:center;
        background:white;
        padding:0.75rem;
        border-radius:0.5rem;
        box-shadow:0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
      }
      .content-wrapper{
        display:grid;
        grid-template-columns:250px 1fr;
        gap:2rem;
      }
      .main-content{
        min-width:0;
      }
      .sidenav{
        position:sticky;
        top:1rem;
        height:fit-content;
        max-height:calc(100vh - 2rem);
        overflow-y:auto;
        padding:1rem;
        background:#f9fafb;
        border-radius:0.375rem;
        border:1px solid #e5e7eb;
      }
      .sidenav h3{
        margin:0 0 0.75rem 0;
        font-size:0.875rem;
        font-weight:600;
        color:#6b7280;
        text-transform:uppercase;
      }
      .nav-item{
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding:0.5rem;
        margin-bottom:0.25rem;
        border-radius:0.25rem;
        font-size:0.875rem;
        color:#374151;
        text-decoration:none;
        transition:all 0.15s;
      }
      .nav-item:hover{
        background:#e5e7eb;
      }
      .nav-item.disabled{
        opacity:0.4;
        cursor:not-allowed;
        pointer-events:none;
      }
      .nav-badge{
        background:#3b82f6;
        color:white;
        padding:0.125rem 0.5rem;
        border-radius:9999px;
        font-size:0.7rem;
        font-weight:600;
        min-width:1.5rem;
        text-align:center;
      }
      .attribute-name{font-weight:bold;font-size:1.25rem;margin-bottom:0.25rem;color:#1e40af}
      .description{margin:0.5rem 0;color:#374151;font-size:0.9rem}
      .attributes{display:flex;flex-direction:column;gap:1rem}
      .attribute{
        position:relative;
        padding:1rem;
        border:1px solid #e5e7eb;
        border-radius:0.375rem;
        background:#fff;
        scroll-margin-top:3rem;
        transition: order 0.5s cubic-bezier(0.4, 0, 0.2, 1), 
                    transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
                    opacity 0.3s ease-in-out;
      }
      .attribute:hover{box-shadow:0 2px 4px rgba(0,0,0,0.1)}
      input{padding:0.625rem;border:1px solid #d1d5db;border-radius:0.375rem;min-width:250px;font-size:0.95rem}
      input:focus{outline:2px solid #3b82f6;outline-offset:0}
      .debug{
        margin-bottom:1rem;
        padding:0.75rem;
        background:#f3f4f6;
        font-family:monospace;
        font-size:0.8rem;
        border-radius:0.375rem;
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:1rem;
      }
      .debug-info{
        flex:1;
      }
      .match-badge{
        position:absolute;
        top:1rem;
        right:1rem;
        background:#3b82f6;
        color:white;
        padding:0.25rem 0.75rem;
        border-radius:9999px;
        font-size:0.8rem;
        font-weight:600;
      }
      button{
        padding:0.625rem 1.25rem;
        background:#3b82f6;
        color:white;
        border:none;
        border-radius:0.375rem;
        cursor:pointer;
        font-size:0.95rem;
        transition:background 0.15s;
        white-space:nowrap;
      }
      button:hover{background:#2563eb}
      button:active{background:#1d4ed8}
      button.clear-btn{
        background:#dc2626;
      }
      button.clear-btn:hover{
        background:#b91c1c;
      }
      code{background:#f3f4f6;color:#1f2937;padding:0.125rem 0.375rem;border-radius:0.25rem;font-size:0.85rem;font-family:monospace}
      h1{color:#111827;margin:0 0 0.25rem 0;font-size:1.75rem}
      .subtitle{color:#6b7280;margin:0;font-size:0.9rem}
      pre{background:#1f2937;color:#f9fafb;padding:0.75rem;border-radius:0.375rem;overflow-x:auto;font-size:0.8rem;margin:0.375rem 0}
      pre code{background:transparent;color:#f9fafb;padding:0}
      """
        )
            ),
            Body(content)
        )
    )

    path = Path(filepath).resolve()           # clean absolute Path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_string, encoding="utf-8")

    return path.as_uri()


@app.cell
def _():
    from fastcore.docments import MarkdownRenderer
    #from fasthtml.common import NotStr

    def render_func_card(sym, idx):
        name = sym.__name__
        module = sym.__module__

        # THIS IS THE MAGIC LINE
        markdown_content = MarkdownRenderer(sym)._repr_markdown_()

        # Make it searchable (include module + param names + docments)
        docs = docments(sym, full=True)
        search_parts = [name, module] + list(docs.keys())
        if sym.__doc__: search_parts.append(sym.__doc__)
        searchable = " ".join(str(p) for p in search_parts).lower()

        match_var = f'matchCount{idx}'
        searchable_var = f'searchable{idx}'

        return Div(
            # Match badge
            Span('0', cls='match-badge', style='display:none;',
                 data_show=NotStr('$tags.length > 0 || $search.trim().length > 0'),
                 data_text=f'${match_var}'),

            # Module badge in corner
            Div(Span(module, cls='func-module'), cls='func-header-right'),

            # THIS IS THE ONLY THING WE RENDER: pure fastcore Markdown → FastHTML auto-converts!
            NotStr(markdown_content),

            # Optional: add collapsible source if you want (fastcore doesn't include it)
            Details(
                Summary("Source code", style="cursor:pointer; margin-top:1rem; color:#2563eb"),
                Pre(Code(get_source(sym)))
            ),

            id=name,
            cls='attribute',
            data_signals=NotStr(f"{{ {searchable_var}: '{searchable}', {match_var}: 0 }}"),
            data_effect=NotStr(
                f'${match_var} = [...$tags, $search.trim()]'
                f'.filter(t => t && ${searchable_var}.includes(t.toLowerCase())).length'
            ),
            data_show=NotStr(f'($tags.length === 0 && $search.trim().length === 0) || ${match_var} > 0'),
            data_style_order=NotStr(f'($tags.length === 0 && $search.trim().length === 0) ? {idx} : -${match_var}')
        )
    return (render_func_card,)


@app.cell
def _(render_func_card):
    def doc_module(module):
        funcs = [o for n,o in inspect.getmembers(module) 
                 if inspect.isfunction(o) and o.__module__ == module.__name__]

        cards = [render_func_card(f, i) for i,f in enumerate(funcs)]

        return Body(
            search_form(),
            Div(H1(f"{module.__name__} — Interactive Docs"), cls='title-section'),
            debug_area(),
            Div(sidenav([{'name':f.__name__} for f in funcs]),
                Div(Div(*cards, cls='attributes'), cls='main-content'),
                cls='content-wrapper'),
            data_signals="{ search: '', tags: [] }"
        )
    return


@app.cell
def _():
    #doc_module(core)
    return


@app.cell
def _():
    #write_to_docs(doc_module(core))
    return


@app.cell
def _():
    from fastcore.docments import extract_docstrings
    from m_dev import core

    # This gets the ACTUAL source code of your module
    module_source = inspect.getsource(core)

    # extract_docstrings(module_source)
    get_module_funcs(core)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Notes

    [] Documentation page requirements
        - Author (not really required REMOVE)
        - Seperate Readme page (this will be a new file and utilize a ds get to navigate to this... ) (remove)
        - Any way to access the github page? (Remove for now)
        - package readme (remove for now)
        - package version
        - package update date
    [] Build information matrix
        - Module
        - Builtin?
        - Function / Class
        - Function Name
        - Parameters : type = default  # Comment
        - Returns    : type            # Comment
        - Source Code
        - Search Matrix


    FE Template

    [] Page Layout
        - dynamic nav
        - dynamic asiede
        - dynamic footer
        - dynamic header..
        - main

    [] Search live and tag system
        -
    """)
    return


@app.function
def get_package_links(package_name):
    from importlib.metadata import metadata
    meta = metadata(package_name)

    project_urls = meta.get_all("Project-URL") or []
    url_dict = {label.strip(): url.strip() 
                for entry in project_urls 
                for label, url in [entry.split(", ", 1)]}

    if home := meta.get("Home-page"):
        url_dict["Home-page"] = home

    return {'Links': url_dict}


@app.function
def get_package_name(package_name):
    from importlib.metadata import metadata
    return {'Name': metadata(package_name)['Name']}


@app.function
def get_package_version(package_name):
    from importlib.metadata import metadata
    return {'Version': metadata(package_name)['Version']}


@app.function
def get_package_contributers(package_name):
    from importlib.metadata import metadata
    meta = metadata(package_name)

    authors = meta.get_all('Author') or meta.get_all('Author-email') or []
    maintainers = meta.get_all('Maintainer') or meta.get_all('Maintainer-email') or []

    return {
        'Authors': authors if authors else None,
        'Maintainers': maintainers if maintainers else None
    }


@app.function
def get_package_info(package_name):
    info = {}
    info.update(get_package_name(package_name))
    info.update(get_package_version(package_name))
    info.update(get_package_contributers(package_name))
    info.update(get_package_links(package_name))
    return info


@app.cell
def _():
    get_package_info("httpx")

    return


app._unparsable_cell(
    r"""
    Article(
        H1(info['Name']),
        Span(f\"Ver: {info['Version']}\")
        A(src=info[\"Links\"])
    
    )

    """,
    name="_"
)


@app.cell
def _(info):
    info["Links"]
    return


@app.cell
def _(mo):
    info = get_package_info("fastcore")

    components = [
        H3("Links"),
        Ul(*[Li(A(label, href=url)) for label, url in info["Links"].items()])
    ]

    # Only add Contributors section if we have authors or maintainers
    if info.get("Authors") or info.get("Maintainers"):
        components.append(H3("Contributers"))
    
    if info.get("Authors"):
        components.append(P(*['author: ' + author for author in info["Authors"]]))
    
    if info.get("Maintainers"):
        components.append(P(*['maintainer: ' + maintainer for maintainer in info["Maintainers"]]))

    demo = Aside(*components)
    print(demo)
    mo.md(f"{demo}")
    return (info,)


@app.cell
def _(info):
    package = Header(
        H1(info['Name']),
        Span(info['Version'])          if info['Version']     != None else None,
        Div(
            Form(
                Input(type="search", placeholder="Live serach (enter to add tag)"),
                Button("Add Tag"), 
                Button("Clear All")
            ),
            Div(
                Span(cls="tag")("new"),
                Span(cls="tag")("data"),
                Span(cls="tag")("math"),
            )
        )
    )
    

    Links = Ul(*[Li(A(label, href=url)) for label, url in info["Links"].items()])

    package
    return


@app.cell
def _():
    style = '''
    <style>
      :root {
        --bg: #f5f6f5;
        --text: #1c2526;
        --border: #d9d9d9;
        --accent: #c9ff00;
      }

      @media (prefers-color-scheme: dark) {
        :root {
          --bg: #1c2526;
          --text: #f5f6f5;
          --border: #333d3f;
          --accent: #c9ff00;
        }
      }

      body {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: light-dark(#ffffff, #121212);
      }

      header {
        max-width: 960px;
        margin: 0 auto;
        padding: 2rem 2.5rem;
        background: light-dark(var(--bg), var(--bg));
        border-bottom: 1px solid light-dark(var(--border), var(--border));
        position: relative;
        overflow: hidden;

        /* Thin accent bar at the top */
        box-shadow: 0 -5px 0 var(--accent) inset; /* cleaner than ::before */
    
        display: grid;
        grid-template-columns: auto 1fr auto;
        align-items: center;
        gap: 2rem;
      }

      h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 750;
        color: light-dark(var(--text), var(--text));
        padding-right: 4rem; /* space for badge */
        position: relative;
      }

      /* Tiny neon version badge – same as Option C */
      span {
        position: absolute;
        top: -0.4rem;
        right: 0;
        background: var(--accent);
        color: #000;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        white-space: nowrap;
      }

      input[type="search"] {
        justify-self: end;
        width: 100%;
        max-width: 360px;
        padding: 0.75rem 1rem 0.75rem 2.7rem;
        font-size: 1rem;
        border: 1.5px solid light-dark(var(--border), var(--border));
        border-radius: 12px;
        background: light-dark(var(--bg), var(--bg));
        color: light-dark(var(--text), var(--text));
        outline: none;
        transition: all 0.2s;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E");
        background-position: 0.9rem center;
        background-repeat: no-repeat;
        background-size: 16px;
      }

      input[type="search"]:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 18%, transparent);
      }

      /* Responsive – stack on small screens */
      @media (max-width: 720px) {
        header {
          grid-template-columns: 1fr;
          text-align: center;
          padding: 2rem 1.5rem;
        }
        h1 { padding-right: 0; display: inline-block; }
        span { right: auto; left: 50%; transform: translateX(-50%); top: -0.6rem; }
        input[type="search"] { max-width: 100%; justify-self: stretch; }
      }
    </style>
    '''
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
