from fasthtml.components import Form, Input, Div, P, Button, Span, Br, Hr, Pre, Code, NotStr, Html, Head, Aside, Nav, Main, Footer, Iframe, Body, Script, to_xml, show, Style, H1, H2, H3, H4, H5, H6, A, Title, Details, Summary, Article, Ul, Li, Small, Header, Footer

import inspect

import ast

from fastcore.docments import docments, docstring, get_source

from fastcore.xml import FT

from pathlib import Path

def extract_builtin_func_info(func):
"""
"""
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

def extract_func_info_docments(func):
"""
"""
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

def search_form():
    "Render search form with tag support"
    return Form(
        Input(type='text', placeholder='Live Search ...(enter to add tag)', **{'data-bind:search': True}),
        Button('Add Tag', type='submit'),
        Button('Clear All', type='button', cls='clear-btn', **{'data-on:click': "$tags = [], $search = ''"}),
        cls='search-section',
        **{'data-on:submit__prevent': "$search.trim() ? ($tags = [...$tags, $search.trim()], $search = '') : null"}
    )

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

def old_render_func_card(info, idx):
"""
"""
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

def sidenav(funcs_info):
"""
"""
    "Render sidebar navigation with match counts"
    items = [A(
        Span(info['name']),
        Span('0', cls='nav-badge', style='display: none;', **{'data-show': NotStr('$tags.length > 0 || $search.trim().length > 0'), 'data-text': f'$matchCount{i}'}),
        href=f"#{info['name']}", cls='nav-item',
        **{'data-class:disabled': NotStr(f"($tags.length > 0 || $search.trim().length > 0) && $matchCount{i} === 0")}
    ) for i,info in enumerate(funcs_info)]
    return Aside(H3('Functions'), *items, cls='sidenav')

def DS(*components, width='100%', height='300px'):
    """Display FT components with isolated Datastar in an IFrame"""
    datastar_url = 'https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js'
    datastar_script = Script(type='module', src=datastar_url)
    doc = Html(Head(datastar_script), Body(*components))
    return Iframe(srcdoc=to_xml(doc), width=width, height=height)

def get_module_funcs(module):
"""
"""
    "Extract all functions from a module"
    return [obj for name, obj in inspect.getmembers(module) 
            if inspect.isroutine(obj) and obj.__module__ == module.__name__]

def write_to_docs(
"""
Args:
    content: FTs
    filepath (str): filepath
    title (str): document title
"""
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

def get_package_links(package_name):
"""
"""
    from importlib.metadata import metadata
    meta = metadata(package_name)

    project_urls = meta.get_all("Project-URL") or []
    url_dict = {label.strip(): url.strip() 
                for entry in project_urls 
                for label, url in [entry.split(", ", 1)]}

    if home := meta.get("Home-page"):
        url_dict["Home-page"] = home

    return {'Links': url_dict}

def get_package_name(package_name):
"""
"""
    from importlib.metadata import metadata
    return {'Name': metadata(package_name)['Name']}

def get_package_version(package_name):
"""
"""
    from importlib.metadata import metadata
    return {'Version': metadata(package_name)['Version']}

def get_package_contributers(package_name):
"""
"""
    from importlib.metadata import metadata
    meta = metadata(package_name)

    authors = meta.get_all('Author') or meta.get_all('Author-email') or []
    maintainers = meta.get_all('Maintainer') or meta.get_all('Maintainer-email') or []

    return {
        'Authors': authors if authors else None,
        'Maintainers': maintainers if maintainers else None
    }

def get_package_info(package_name):
"""
"""
    info = {}
    info.update(get_package_name(package_name))
    info.update(get_package_version(package_name))
    info.update(get_package_contributers(package_name))
    info.update(get_package_links(package_name))
    return info

