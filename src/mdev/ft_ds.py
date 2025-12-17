from functools import partial
from fastcore.xml import attrmap, to_xml, FT
from fasthtml.components import ft_html
from fastcore.meta import use_kwargs
from typing import Literal, Optional
import json, re
import sys

__ds_special = 'on_intersect on_interval on_signal_patch on_signal_patch_filter on_raf on_resize preserve_attr json_signals scroll_into_view view_transition custom_validity replace_url query_string persist'.split()
__ds_prefixes = 'on bind signals computed class style attr ref indicator'.split()
__mod_pat = re.compile('_(\\d+(?:ms|s)?|leading|trailing|notrailing|noleading|camel|kebab|snake|pascal|self|terse)')
__tags = 'A Abbr Address Area Article Aside Audio B Base Bdi Bdo Blockquote Body Br Button Canvas Caption Cite Code Col Colgroup Data Datalist Dd Del Details Dfn Dialog Div Dl Dt Em Embed Fieldset Figcaption Figure Footer Form H1 H2 H3 H4 H5 H6 Head Header Hgroup Hr I Iframe Img Input Ins Kbd Label Legend Li Link Main Map Mark Menu Meta Meter Nav Noscript Object Ol Optgroup Option Output P Picture Pre Progress Q Rp Rt Ruby S Samp Script Search Section Select Slot Small Source Span Strong Style Sub Summary Sup Table Tbody Td Template Textarea Tfoot Th Thead Time Title Tr Track U Ul Var Video Wbr'.split()

def __hyphenate(s):
    """
    Args:
        s: string with underscores

    """
    return '-'.join(s.split('_'))

def attrmap_ds(o: str) -> str:
    """
    Map Python attrs to Datastar: `data_on_click__debounce_500ms` → data-on:click__debounce.500ms

    Args:
        o (str): Python attribute name to convert

    Returns:
        str: Datastar-formatted attribute name

    """
    if not o.startswith('data_'): return attrmap(o)
    p = o.split('__')
    main,mod = p[0],'__' + __mod_pat.sub(r'.\1', '__'.join(p[1:])) if len(p) > 1 else ''

    # Special multi-word attrs: data_on_intersect or data_on_intersect_foo
    for s in __ds_special:
        pfx = f'data_{s}'
        if main == pfx: return __hyphenate(main) + mod
        if main.startswith(pfx + '_'):
            segs = main.split('_')
            n = len(s.split('_')) + 1  # +1 for 'data' prefix
            return f'{__hyphenate("_".join(segs[:n]))}:{__hyphenate("_".join(segs[n:]))}{mod}'

    # Colon-based attrs: data_on_click → data-on:click
    for pfx in __ds_prefixes:
        if not main.startswith(f'data_{pfx}_'): continue
        segs = main.split('_')
        key = __hyphenate('_'.join(segs[2:]))  # Skip 'data' and prefix
        return f'data-{pfx}:{key}{mod}' if key else f'data-{pfx}{mod}'

    return __hyphenate(main) + mod

def ft_ds(tag, *c, **kw):
    """
    Create FastTag with Datastar support: `data_on_click`→data-on:click, `data_bind_foo`→data-bind:foo

    Args:
        tag: HTML tag name
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    """
    return ft_html(tag, *c, attrmap=attrmap_ds, **kw)

def show(*fts):
    """
    Display `fts` as HTML in marimo

    Args:
        *args: Variable length argument list.

    """
    import marimo as mo
    return mo.Html(''.join(to_xml(ft) for ft in fts))

def setup_tags(g=None):
    """
    Setup all HTML tags as Datastar-enabled `ft_ds` partials

    Args:
        g (default: None): globals dict to populate (defaults to caller's globals)

    """
    import inspect
    g = g or inspect.currentframe().f_back.f_globals
    for o in __tags: g[o] = partial(ft_ds, o.lower())

def __getattr__(name: str) -> partial:
    """
    Dynamically create Datastar-enabled tags: `from ft_ds import Zero_md`

    Args:
        name (str): attribute name to look up (e.g., 'Zero_md', 'Custom_tag')

    Returns:
        partial: partial function that creates the lowercased HTML tag

    """
    if name[0].isupper(): return partial(ft_ds, name.lower())
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def Html(*c, **kw):
    """
    HTML root element with doctype

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    """
    return f'<!DOCTYPE html>\n{to_xml(ft_ds("html", *c, **kw))}'
