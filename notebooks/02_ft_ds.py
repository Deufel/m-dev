import marimo

__generated_with = "0.18.1"
app = marimo.App(width="full")

with app.setup:
    from functools import partial
    from fastcore.xml import attrmap
    from fasthtml.components import ft_html
    from fastcore.meta import use_kwargs
    from typing import Literal, Optional
    import json, re


@app.cell
def _():
    import marimo as mo
    return


@app.function
def attrmap_ds(o):
    "Custom attribute mapper for Datastar - handles data-X:key__modifier syntax"
    ds_colon = "on bind signals computed class style attr ref indicator".split()
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


@app.function
def ft_ds(tag:str, *c, **kw):
    "Create FastTag with Datastar support: data_on_click -> data-on:click, data_bind_foo -> data-bind:foo"
    return ft_html(tag, *c, attrmap=attrmap_ds, **kw)


@app.cell
def _():
    _all_ = 'A Abbr Address Area Article Aside Audio B Base Bdi Bdo Blockquote Body Br Button Canvas Caption Cite Code Col Colgroup Data Datalist Dd Del Details Dfn Dialog Div Dl Dt Em Embed Fieldset Figcaption Figure Footer Form H1 H2 H3 H4 H5 H6 Head Header Hgroup Hr I Iframe Img Input Ins Kbd Label Legend Li Link Main Map Mark Menu Meta Meter Nav Noscript Object Ol Optgroup Option Output P Picture Pre Progress Q Rp Rt Ruby S Samp Script Search Section Select Slot Small Source Span Strong Style Sub Summary Sup Table Tbody Td Template Textarea Tfoot Th Thead Time Title Tr Track U Ul Var Video Wbr'.split()
    for o in _all_: globals()[o] = partial(ft_ds, o.lower())
    return


@app.cell
def _(A):
    A(data_on_Click__delay_3s="@get('/moreinfo')")("probwont work")
    return


@app.cell
def _(Div):
    Div(data_class_Mike__case_camel='$this')
    return


@app.cell
def _(Div, d):
    Div(d)
    return


if __name__ == "__main__":
    app.run()
