import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    from functools import partial
    from fastcore.xml import attrmap, to_xml, FT, ft
    from fasthtml.components import ft_html
    from fastcore.meta import use_kwargs
    from typing import Literal, Optional
    import json, re
    import sys


    __ds_special = 'on_intersect on_interval on_signal_patch on_signal_patch_filter on_raf on_resize preserve_attr json_signals scroll_into_view view_transition custom_validity replace_url query_string persist'.split()
    __ds_prefixes = 'on bind signals computed class style attr ref indicator'.split()
    __mod_pat = re.compile(r'_(\d+(?:ms|s)?|leading|trailing|notrailing|noleading|camel|kebab|snake|pascal|self|terse)')
    __tags = 'A Abbr Address Area Article Aside Audio B Base Bdi Bdo Blockquote Body Br Button Canvas Caption Cite Code Col Colgroup Data Datalist Dd Del Details Dfn Dialog Div Dl Dt Em Embed Fieldset Figcaption Figure Footer Form H1 H2 H3 H4 H5 H6 Head Header Hgroup Hr I Iframe Img Input Ins Kbd Label Legend Li Link Main Map Mark Menu Meta Meter Nav Noscript Object Ol Optgroup Option Output P Picture Pre Progress Q Rp Rt Ruby S Samp Script Search Section Select Slot Small Source Span Strong Style Sub Summary Sup Table Tbody Td Template Textarea Tfoot Th Thead Time Title Tr Track U Ul Var Video Wbr'.split()


@app.cell
def _():
    import marimo as mo
    import pytest
    return


@app.function
def attrmap_ds(
    o:str  # Python attribute name to convert
)->str:    # Datastar-formatted attribute name
    """Map Python attrs to Datastar: `data_on_click__debounce_500ms` → data-on:click__debounce.500ms"""

    if not o.startswith('data_'): return attrmap(o)
    p = o.split('__')
    main,mod = p[0],'__'+__mod_pat.sub(r'.\1','__'.join(p[1:])) if len(p)>1 else ''
    segs = main.split('_')
    m = main[5:]
    if m in __ds_special: return f'data-{m.replace("_","-")}{mod}'
    for sp in __ds_special:
        if m.startswith(f'{sp}_'):
            n = len(sp.split('_'))+1
            return f'{"_".join(segs[:n]).replace("_","-")}:{"_".join(segs[n:]).replace("_","-")}{mod}'
    for pfx in __ds_prefixes:
        if m.startswith(f'{pfx}_'):
            key = '.'.join(segs[2:]) if pfx=='signals' else '_'.join(segs[2:]).replace('_','-')
            return f'data-{pfx}:{key}{mod}' if key else f'data-{pfx}{mod}'
    return main.replace('_','-')+mod


@app.cell
def _(ft_ds):
    def setup_tags(
        g=None  # globals dict to populate (defaults to caller's globals)
    ):          # None (modifies `g` in place)
        """Setup all HTML tags as Datastar-enabled `ft_ds` partials"""
        import inspect
        g = g or inspect.currentframe().f_back.f_globals
        for o in __tags: g[o] = partial(ft_ds, o.lower())
    return


@app.cell
def _(ft_ds):
    def __getattr__(
        name:str  # attribute name to look up (e.g., 'Zero_md', 'Custom_tag')
    )->partial:   # partial function that creates the lowercased HTML tag
        """Dynamically create Datastar-enabled tags: `from ft_ds import Zero_md`"""
        if name[0].isupper(): return partial(ft_ds, name.lower())
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
