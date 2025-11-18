import marimo

__generated_with = "0.17.7"
app = marimo.App(width="full", html_head_file="head.html")

with app.setup:
    from fasthtml.components import Form, Input, Div, P, Button, Span, Br, Hr, Pre, Code, NotStr, Html, Head, Aside, Nav, Main, Footer, Iframe, Body, Script, to_xml, show, Style, H1, H2, H3, A
    import inspect
    import ast
    from fastcore.docments import docments, docstring, get_source
    from fastcore.xml import FT


@app.cell
def _():
    import marimo as mo
    import pytest
    from typing import Callable

    # Helpful "monkey patch" for viewing components in marimo 
    def _display_(self):
        import marimo as mo
        return mo.md(f"{self}")

    FT._display_ = _display_

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
def render_func_card(info, idx):
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
def _(math):
    info = extract_func_info_docments(math.sqrt)
    card = render_func_card(info, 0)

    return (card,)


@app.cell
def _(card, mo):
    print(type(card))
    print(card)
    mo.md(f"{to_xml(card)}")
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
def _(extract_func_info):
    def doc_page(funcs):
        "Generate complete HTML page with new template design"
        funcs_info = [extract_func_info(f) for f in funcs]

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


@app.cell
def _():
    return


@app.cell
def _(doc_page, sample_func_a):
    DS()(doc_page([sample_func_a]))
    return


@app.function
def get_module_funcs(module):
    "Extract all functions from a module"
    return [obj for name, obj in inspect.getmembers(module) 
            if inspect.isroutine(obj) and obj.__module__ == module.__name__]


@app.cell
def _(doc_page):

    def doc_module(module, width='100%', height='600px'):
        """Generate documentation page for all functions in a module"""
        funcs = get_module_funcs(module)
        return doc_page(funcs) 
    return (doc_module,)


@app.cell
def _():
    from m_dev import core
    return


@app.cell
def _(doc_module):
    import math 
    doc_module(math)
    return (math,)


@app.cell
def _(doc_page):

    def new_doc_module(module, width='100%', height='600px'):
        """Generate and display documentation page for all functions in a module"""
        funcs = get_module_funcs(module)
        DS(width, height)(doc_page(funcs))
    return (new_doc_module,)


@app.cell
def _(math, new_doc_module):
    new_doc_module(math)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
