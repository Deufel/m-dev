import marimo

__generated_with = "0.18.1"
app = marimo.App(width="full")

with app.setup:
    from functools import partial
    from fastcore.xml import attrmap
    from fasthtml.components import ft_html
    from fastcore.meta import use_kwargs
    from typing import Literal, Optional, Union, Any
    import json, re# Initialization code that runs before all other cells


@app.cell
def _():


    # Attrs that use colon pattern data-PREFIX:key
    ds_colon_prefixes = 'on bind signals computed class style attr ref indicator'.split()

    # Special multi-word attrs (no colon, just convert underscore to hyphen)
    ds_special = 'on_intersect on_interval on_raf on_resize on_signal_patch on_signal_patch_filter preserve_attr json_signals scroll_into_view view_transition custom_validity replace_url query_string'.split()

    def attrmap_ds(o):
        "Map Python attrs to Datastar syntax: data_on_click__debounce_500ms → data-on:click__debounce.500ms"
    
        # Check if it's a data attribute
        if not o.startswith('data_'): return attrmap(o)
    
        # Split on double underscore to isolate modifiers
        parts = o.split('__')
        main = parts[0]
        mods = '__'.join(parts[1:]) if len(parts) > 1 else ''
    
        # Convert modifiers: _500ms → .500ms, _leading → .leading
        if mods: mods = '__' + re.sub(r'_(\d+|leading|trailing|notrailing|noleading|camel|kebab|snake|pascal|self|terse)', r'.\1', mods)
    
        # Check for special multi-word attrs first (these don't use colon)
        for special in ds_special:
            special_prefix = f'data_{special}'
            if main == special_prefix:
                return '-'.join(main.split('_')) + mods
            if main.startswith(special_prefix + '_'):
                # Has a key after the special attr, e.g., data_persist_mykey
                segs = main.split('_')
                prefix_len = len(special.split('_')) + 1  # +1 for 'data'
                key = '-'.join(segs[prefix_len:])
                base = '-'.join(segs[:prefix_len])
                return f'{base}:{key}{mods}'
    
        # Check for colon-based attrs: data_PREFIX_key
        segs = main.split('_')
        if len(segs) >= 2 and segs[1] in ds_colon_prefixes:
            # data_on_click → data-on:click
            # data_bind_user_name → data-bind:user-name
            prefix = f'data-{segs[1]}'  # data-on, data-bind, etc.
            key_parts = segs[2:]  # everything after prefix
            if key_parts:
                key = '-'.join(key_parts)  # multi-word events: mouse_enter → mouse-enter
                return f'{prefix}:{key}{mods}'
            else:
                # No key, just return the prefix (e.g., data_on without event)
                return prefix + mods
    
        # Default: just convert underscores to hyphens
        return '-'.join(main.split('_')) + mods

    def ft_ds(tag:str, *c, **kwargs:Any):
        """
        Create FastTag with Datastar attribute support.
    
        Convention: data_PREFIX_key__modifiers
        - First _ after data_PREFIX → colon (:)
        - __ → modifier separator
        - _ before digit/keyword in modifier → dot (.)
        - Other _ → hyphen (-)
    
        Examples:
            data_on_click → data-on:click
            data_on_mouse_enter → data-on:mouse-enter
            data_on_click__debounce_500ms → data-on:click__debounce.500ms
            data_bind_user_name → data-bind:user-name
            data_signals_count → data-signals:count
            data_class_hidden → data-class:hidden
            data_init__delay_500ms → data-init__delay.500ms
        """
        return ft_html(tag, *c, attrmap=attrmap_ds, **kwargs)

    # Create tag functions
    _g = globals()
    _tags = 'A Abbr Address Area Article Aside Audio B Base Bdi Bdo Blockquote Body Br Button Canvas Caption Cite Code Col Colgroup Data Datalist Dd Del Details Dfn Dialog Div Dl Dt Em Embed Fieldset Figcaption Figure Footer Form H1 H2 H3 H4 H5 H6 Head Header Hgroup Hr I Iframe Img Input Ins Kbd Label Legend Li Link Main Map Mark Menu Meta Meter Nav Noscript Object Ol Optgroup Option Output P Picture Pre Progress Q Rp Rt Ruby S Samp Script Search Section Select Slot Small Source Span Strong Style Sub Summary Sup Table Tbody Td Template Textarea Tfoot Th Thead Time Title Tr Track U Ul Var Video Wbr'.split()
    for o in _tags: _g[o] = partial(ft_ds, o.lower())
    return


@app.cell
def _(A):
    A(data_on_Click__delay_3s="@get('/moreinfo')")("probwont work")
    return


@app.cell
def _(Div):
    Div(data_class_Mike__case_camel='$this')
    return


if __name__ == "__main__":
    app.run()
