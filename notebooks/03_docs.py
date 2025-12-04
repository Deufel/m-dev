import marimo

__generated_with = "0.18.1"
app = marimo.App(width="full")

with app.setup:
    import marimo as mo


@app.cell
def _():
    from mohtml import body, form, input, button, div, aside, a, span, nav, header, code, h1, h2, h3, h4, script, img, p, main, ul, li

    d = body(
        script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"),
        header( h1("This is the docs...")),
        nav(
            ul(
                li("Module 1"),
                li("module 2")
            )
        ),
        main(),
        p("my name is Mike", klass="text-gray-500 text-sm"),
        a("please check my site", href="https://calmcode.io", klass="underline"),
        data_signals="{ search: '', tags: [] }"
    )
    print(d)
    d
    return


@app.cell
def _():
    from fastcore.xml import Html, Script, Head, Body
    return Body, Head, Html, Script


@app.cell
def _(Body, Head, Html, Script):
    page = Html(
        Head(
            Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"),
        ),
        Body(data_signals="{ search: '', tags: [] }")("body")
    )
    return (page,)


@app.cell
def _(page):
    page
    return


@app.cell
def _():
    """Datastar convenience functions for FastHTML - adds `data-*` attribute support with type hints"""

    from functools import partial
    from fastcore.xml import attrmap
    from fasthtml.components import ft_html
    from fastcore.meta import use_kwargs
    from typing import Literal, Optional
    import json, re
    # Attributes that use colon syntax: data-X:key
    ds_colon = 'on bind signals computed class style attr ref indicator'.split()

    # Type hints for common Datastar attributes
    ds_annos = {
        'data_show': Optional[str], 'data_text': Optional[str], 'data_effect': Optional[str],
        'data_init': Optional[str], 'data_ignore': Optional[bool], 'data_ignore_morph': Optional[bool],
        'data_preserve_attr': Optional[str], 'data_json_signals': Optional[str],
        'data_replace_url': Optional[str], 'data_scroll_into_view': Optional[bool],
        'data_view_transition': Optional[str], 'data_custom_validity': Optional[str],
    }

    def attrmap_ds(o):
        "Custom attribute mapper for Datastar - handles data-X:key__modifier syntax"
        for pfx in ds_colon:
            pfx_pat = f'data_{pfx}_'
            if not o.startswith(pfx_pat): continue
            parts = o.split('__')
            main,mods = parts[0],'__'.join(parts[1:]) if len(parts)>1 else ''
            segs = main.split('_')
            key = '-'.join(segs[len(f'data_{pfx}'.split('_')):])
            base = f'data-{pfx}'
            result = f'{base}:{key}' if key else base
            if mods: result = f'{result}__{re.sub(r"_(\d+)", r".\1", mods)}'
            return result
        return attrmap(o)

    @use_kwargs(ds_annos, keep=True)
    def ft_ds(tag:str, *c, **kw):
        "Create FastTag with Datastar support: data_on_click -> data-on:click, data_bind_foo -> data-bind:foo"
        return ft_html(tag, *c, attrmap=attrmap_ds, **kw)

    # Generate all HTML tags with Datastar support
    _all_ = 'A Abbr Address Area Article Aside Audio B Base Bdi Bdo Blockquote Body Br Button Canvas Caption Cite Code Col Colgroup Data Datalist Dd Del Details Dfn Dialog Div Dl Dt Em Embed Fieldset Figcaption Figure Footer Form H1 H2 H3 H4 H5 H6 Head Header Hgroup Hr I Iframe Img Input Ins Kbd Label Legend Li Link Main Map Mark Menu Meta Meter Nav Noscript Object Ol Optgroup Option Output P Picture Pre Progress Q Rp Rt Ruby S Samp Script Search Section Select Slot Small Source Span Strong Style Sub Summary Sup Table Tbody Td Template Textarea Tfoot Th Thead Time Title Tr Track U Ul Var Video Wbr'.split()
    for o in _all_: globals()[o] = partial(ft_ds, o.lower())
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
