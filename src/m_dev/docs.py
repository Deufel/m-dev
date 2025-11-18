from fasthtml.components import Form, Input, Div, P, Button, Span, Br, Hr, Pre, Code, NotStr, Html, Head, Aside, Nav, Main, Footer, Iframe, Body, Script, to_xml, show, Style, H1, H2, H3, A
import inspect
import ast
from fastcore.docments import docments, docstring, get_source

def extract_builtin_func_info(func):
    """Extract function name, params, return type, and docstring from function object"""
    is_builtin = inspect.isbuiltin(func)
    assert inspect.isbuiltin(func) or not inspect.isfunction(func), 'Use extract_func_info_docments for regular Python functions'
    name = func.__name__
    docstr = inspect.getdoc(func) or ''
    try:
        sig = inspect.signature(func)
        params = [(param.name, str(param.annotation) if param.annotation != inspect.Parameter.empty else None) for param in sig.parameters.values()]
        ret_type = str(sig.return_annotation) if sig.return_annotation is not inspect.Signature.empty else None
    except ValueError:
        params = []
        ret_type = None
    return {'name': name, 'params': params, 'return': ret_type, 'docstring': docstr, 'source': 'Built-in function', 'is_builtin': True}

def extract_func_info_docments(func):
    """Extract function info using fastcore.docments"""
    try:
        docs = docments(func, full=True)
        params = [(name, str(info['anno']) if info['anno'] != inspect.Parameter.empty else None) for name, info in docs.items() if name != 'return']
        ret_info = docs.get('return', {})
        ret_type = str(ret_info.get('anno')) if ret_info.get('anno') != inspect.Parameter.empty else None
        return {'name': func.__name__, 'params': params, 'return': ret_type, 'docstring': docstring(func) or '', 'source': get_source(func), 'is_builtin': False}
    except Exception:
        return extract_builtin_func_info(func)

def search_form():
    """Render search form with tag support"""
    return Form(Input(type='text', placeholder='Live Search ...(enter to add tag)', **{'data-bind:search': True}), Button('Add Tag', type='submit'), Button('Clear All', type='button', cls='clear-btn', **{'data-on:click': "$tags = [], $search = ''"}), cls='search-section', **{'data-on:submit__prevent': "$search.trim() ? ($tags = [...$tags, $search.trim()], $search = '') : null"})

def debug_area():
    """Render debug/tags display area"""
    return Div(Div('Tags: ', Span('[]', **{'data-text': 'JSON.stringify($tags)'}), Br(), 'Search: ', Span(**{'data-text': '$search'}), cls='debug-info'), Button('Clear All', type='button', cls='clear-btn', **{'data-on:click': "$tags = [], $search = ''"}), cls='debug')

def render_func_card(info, idx):
    """Render function with relevance ordering and match counting"""
    searchable = f"{info['name']} {' '.join([n for n, t in info['params']])} {info['docstring']}".lower().replace("'", "\\'").replace('\n', ' ')
    match_var = f'matchCount{idx}'
    searchable_var = f'searchable{idx}'
    params_str = ', '.join([f'{name}: {typ}' if typ else name for name, typ in info['params']])
    sig = f"{info['name']}({params_str})"
    if info['return']:
        sig += f" -> {info['return']}"
    return Div(Span('0', cls='match-badge', style='display: none;', **{'data-show': NotStr('$tags.length > 0 || $search.trim().length > 0'), 'data-text': f'${match_var}'}), Div(Code(sig), cls='attribute-name'), Div(info['docstring'], Pre(Code(info['source'])), cls='description'), id=info['name'], cls='attribute', **{'data-signals': NotStr(f"{{ {searchable_var}: '{searchable}', {match_var}: 0 }}"), 'data-effect': NotStr(f'${match_var} = [...$tags, $search.trim()].filter(tag => tag.length > 0 && ${searchable_var}.toLowerCase().includes(tag.toLowerCase())).length'), 'data-show': NotStr(f'($tags.length === 0 && $search.trim().length === 0) || ${match_var} > 0'), 'data-style:order': NotStr(f'($tags.length === 0 && $search.trim().length === 0) ? {idx} : -${match_var}')})

def sidenav(funcs_info):
    """Render sidebar navigation with match counts"""
    items = [A(Span(info['name']), Span('0', cls='nav-badge', style='display: none;', **{'data-show': NotStr('$tags.length > 0 || $search.trim().length > 0'), 'data-text': f'$matchCount{i}'}), href=f"#{info['name']}", cls='nav-item', **{'data-class:disabled': NotStr(f'($tags.length > 0 || $search.trim().length > 0) && $matchCount{i} === 0')}) for i, info in enumerate(funcs_info)]
    return Aside(H3('Functions'), *items, cls='sidenav')

def DS(*components, width='100%', height='300px'):
    """Display FT components with isolated Datastar in an IFrame"""
    datastar_url = 'https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js'
    datastar_script = Script(type='module', src=datastar_url)
    doc = Html(Head(datastar_script), Body(*components))
    return Iframe(srcdoc=to_xml(doc), width=width, height=height)

def get_module_funcs(module):
    """Extract all functions from a module"""
    return [obj for name, obj in inspect.getmembers(module) if inspect.isroutine(obj) and obj.__module__ == module.__name__]

