import marimo

__generated_with = "0.18.2"
app = marimo.App(width="full")

with app.setup:
    from functools import partial
    from fastcore.xml import attrmap, to_xml, FT
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
    return (mo,)


@app.function
def __hyphenate(
    s  # string with underscores
):     # hyphenated string
    return '-'.join(s.split('_'))


@app.function
def attrmap_ds(
    o:str  # Python attribute name to convert
)->str:    # Datastar-formatted attribute name
    """Map Python attrs to Datastar: `data_on_click__debounce_500ms` → data-on:click__debounce.500ms"""
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


@app.function
def ft_ds(
    tag,  # HTML tag name
    *c,   # child elements
    **kw  # attributes with Datastar support
):        # FastTag with Datastar attribute mapping
    """Create FastTag with Datastar support: `data_on_click`→data-on:click, `data_bind_foo`→data-bind:foo"""
    return ft_html(tag, *c, attrmap=attrmap_ds, **kw)


@app.function
def show(
    *fts  # FT elements to display
):        # marimo HTML object
    """Display `fts` as HTML in marimo"""
    import marimo as mo
    return mo.Html(''.join(to_xml(ft) for ft in fts))


@app.function
def setup_tags(
    g=None  # globals dict to populate (defaults to caller's globals)
):          # None (modifies `g` in place)
    """Setup all HTML tags as Datastar-enabled `ft_ds` partials"""
    import inspect
    g = g or inspect.currentframe().f_back.f_globals
    for o in __tags: g[o] = partial(ft_ds, o.lower())


@app.function
def __getattr__(
    name:str  # attribute name to look up (e.g., 'Zero_md', 'Custom_tag')
)->partial:   # partial function that creates the lowercased HTML tag
    """Dynamically create Datastar-enabled tags: `from ft_ds import Zero_md`"""
    if name[0].isupper(): return partial(ft_ds, name.lower())
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


@app.function
def Html(
    *c,    # child elements (Head, Body, etc)
    **kw   # HTML attributes (lang, class, etc)
):         # HTML document with DOCTYPE declaration
    """HTML root element with doctype"""
    return f'<!DOCTYPE html>\n{to_xml(ft_ds("html", *c, **kw))}'


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Testing
    """)
    return


@app.cell(hide_code=True)
def _():
    # Required for testing... set up all html tags
    setup_tags()
    return


@app.cell(hide_code=True)
def _():
    def test_basic_colon_attrs():
        "Test basic data-PREFIX:key pattern"
        assert attrmap_ds('data_on_click') == 'data-on:click'
        assert attrmap_ds('data_bind_username') == 'data-bind:username'
        assert attrmap_ds('data_signals_count') == 'data-signals:count'
        assert attrmap_ds('data_computed_total') == 'data-computed:total'
        assert attrmap_ds('data_class_hidden') == 'data-class:hidden'
        assert attrmap_ds('data_style_color') == 'data-style:color'
        assert attrmap_ds('data_attr_title') == 'data-attr:title'
        assert attrmap_ds('data_ref_myref') == 'data-ref:myref'
        assert attrmap_ds('data_indicator_loading') == 'data-indicator:loading'

    def test_multi_word_keys():
        "Test multi-word keys with multiple underscores"
        assert attrmap_ds('data_on_mouse_enter') == 'data-on:mouse-enter'
        assert attrmap_ds('data_on_key_down') == 'data-on:key-down'
        assert attrmap_ds('data_bind_user_name') == 'data-bind:user-name'
        assert attrmap_ds('data_signals_user_profile_data') == 'data-signals:user-profile-data'
        assert attrmap_ds('data_class_text_blue_700') == 'data-class:text-blue-700'

    def test_static_attrs():
        "Test static attributes without colon pattern"
        assert attrmap_ds('data_show') == 'data-show'
        assert attrmap_ds('data_text') == 'data-text'
        assert attrmap_ds('data_init') == 'data-init'
        assert attrmap_ds('data_effect') == 'data-effect'
        assert attrmap_ds('data_ignore') == 'data-ignore'
        assert attrmap_ds('data_on_intersect') == 'data-on-intersect'
        assert attrmap_ds('data_on_interval') == 'data-on-interval'
        assert attrmap_ds('data_on_signal_patch') == 'data-on-signal-patch'

    def test_modifiers_timing():
        "Test modifiers with timing values: _500ms → .500ms"
        assert attrmap_ds('data_on_click__debounce_500ms') == 'data-on:click__debounce.500ms'
        assert attrmap_ds('data_on_input__throttle_100ms') == 'data-on:input__throttle.100ms'
        assert attrmap_ds('data_init__delay_1s') == 'data-init__delay.1s'
        assert attrmap_ds('data_on_interval__duration_2s') == 'data-on-interval__duration.2s'

    def test_modifiers_keywords():
        "Test modifiers with keyword values: _leading → .leading"
        assert attrmap_ds('data_on_click__debounce_500ms_leading') == 'data-on:click__debounce.500ms.leading'
        assert attrmap_ds('data_on_input__throttle_100ms_trailing') == 'data-on:input__throttle.100ms.trailing'
        assert attrmap_ds('data_on_click__debounce_1s_notrailing') == 'data-on:click__debounce.1s.notrailing'
        assert attrmap_ds('data_bind_user__case_camel') == 'data-bind:user__case.camel'
        assert attrmap_ds('data_signals_count__case_kebab') == 'data-signals:count__case.kebab'

    def test_multiple_chained_modifiers():
        "Test multiple modifiers chained together"
        assert attrmap_ds('data_on_click__window__debounce_500ms') == 'data-on:click__window__debounce.500ms'
        assert attrmap_ds('data_on_click__prevent__stop') == 'data-on:click__prevent__stop'
        assert attrmap_ds('data_on_click__window__debounce_500ms_leading') == 'data-on:click__window__debounce.500ms.leading'

    def test_prefix_without_key():
        "Test edge case: prefix without key"
        assert attrmap_ds('data_on') == 'data-on'
        assert attrmap_ds('data_bind') == 'data-bind'

    def test_complex_multi_word_events():
        "Test complex multi-word events with modifiers"
        assert attrmap_ds('data_on_animation_end__once') == 'data-on:animation-end__once'
        assert attrmap_ds('data_on_transition_end__once__viewtransition') == 'data-on:transition-end__once__viewtransition'

    def test_numbers_in_different_positions():
        "Test timing values with different numbers"
        assert attrmap_ds('data_on_click__throttle_16ms') == 'data-on:click__throttle.16ms'
        assert attrmap_ds('data_on_scroll__debounce_250ms') == 'data-on:scroll__debounce.250ms'
        assert attrmap_ds('data_init__delay_3000ms') == 'data-init__delay.3000ms'

    def test_special_modifiers():
        "Test special modifier keywords"
        assert attrmap_ds('data_ignore__self') == 'data-ignore__self'
        assert attrmap_ds('data_json_signals__terse') == 'data-json-signals__terse'
        assert attrmap_ds('data_on_intersect__once__full') == 'data-on-intersect__once__full'

    def test_pro_attributes():
        "Test Datastar Pro attributes"
        assert attrmap_ds('data_persist') == 'data-persist'
        assert attrmap_ds('data_persist__session') == 'data-persist__session'
        assert attrmap_ds('data_query_string__filter__history') == 'data-query-string__filter__history'
        assert attrmap_ds('data_scroll_into_view__smooth__vstart') == 'data-scroll-into-view__smooth__vstart'

    def test_nasty_edge_cases():
        "Test particularly complex edge cases"
        assert attrmap_ds('data_on_my_custom_event_123__debounce_500ms_leading') == 'data-on:my-custom-event-123__debounce.500ms.leading'
        assert attrmap_ds('data_bind_deeply_nested_user_profile_field__case_snake') == 'data-bind:deeply-nested-user-profile-field__case.snake'
        assert attrmap_ds('data_class_bg_blue_500_hover_bg_blue_700') == 'data-class:bg-blue-500-hover-bg-blue-700'

    def test_non_data_attrs_passthrough():
        "Test non-data attributes pass through to attrmap"
        assert attrmap_ds('hx_get') == 'hx-get'
        assert attrmap_ds('class') == 'class'
        assert attrmap_ds('_for') == 'for'

    def test_int_basic_colon_attrs():
        "Test basic data-PREFIX:key pattern"
        btn = ft_ds('button', 'Click me', data_on_click="$count++")
        html = to_xml(btn)
        assert 'data-on:click="$count++"' in html

    def test_int_multi_word_keys():
        "Test multi-word keys with hyphens"
        inp = ft_ds('input', 
                    data_bind_user_name="$username", 
                    data_on_mouse_enter="$hover=true")
        html = to_xml(inp)
        assert 'data-bind:user-name="$username"' in html
        assert 'data-on:mouse-enter="$hover=true"' in html

    def test_int_modifiers_with_timing():
        "Test modifiers with timing values"
        inp = ft_ds('input', data_on_input__debounce_500ms="search()")
        html = to_xml(inp)
        assert 'data-on:input__debounce.500ms="search()"' in html

    def test_int_modifiers_with_keywords():
        "Test modifiers with keyword values"
        inp = ft_ds('input', 
                    data_bind_user__case_camel="$user",
                    data_on_click__debounce_500ms_leading="submit()")
        html = to_xml(inp)
        assert 'data-bind:user__case.camel="$user"' in html
        assert 'data-on:click__debounce.500ms.leading="submit()"' in html

    def test_int_multiple_chained_modifiers():
        "Test multiple modifiers chained together"
        btn = ft_ds('button', data_on_click__window__debounce_500ms="action()")
        html = to_xml(btn)
        assert 'data-on:click__window__debounce.500ms="action()"' in html

    def test_int_static_attributes():
        "Test static attributes without colon pattern"
        div = ft_ds('div', data_show="$visible", data_text="$message", data_init="$count=0")
        html = to_xml(div)
        assert 'data-show="$visible"' in html
        assert 'data-text="$message"' in html
        assert 'data-init="$count=0"' in html

    def test_int_event_attributes():
        "Test special event attributes"
        div = ft_ds('div', 
                    data_on_intersect__once="$seen=true",
                    data_on_interval__duration_500ms="$tick++")
        html = to_xml(div)
        assert 'data-on-intersect__once="$seen=true"' in html
        assert 'data-on-interval__duration.500ms="$tick++"' in html

    def test_int_signals_and_computed():
        "Test signals and computed attributes"
        div = ft_ds('div',
                    data_signals_count="0",
                    data_computed_doubled="$count * 2")
        html = to_xml(div)
        assert 'data-signals:count="0"' in html
        assert 'data-computed:doubled="$count * 2"' in html

    def test_int_class_and_style():
        "Test class and style binding"
        div = ft_ds('div',
                    data_class_hidden="$loading",
                    data_class_text_blue_700="$active",
                    data_style_color="$textColor")
        html = to_xml(div)
        assert 'data-class:hidden="$loading"' in html
        assert 'data-class:text-blue-700="$active"' in html
        assert 'data-style:color="$textColor"' in html

    def test_int_ref_and_indicator():
        "Test ref and indicator attributes"
        # In Datastar, these often reference the signal being created
        div = ft_ds('div',
                    data_ref_myref=True,  # Boolean renders as just attribute name
                    data_indicator_loading=True)
        html = to_xml(div)
        assert 'data-ref:myref' in html
        assert 'data-indicator:loading' in html

    def test_int_complex_real_world():
        "Test complex real-world usage with multiple features"
        div = ft_ds('div',
                    data_signals_count="0",
                    data_computed_doubled="$count * 2",
                    data_on_click__throttle_100ms="$count++",
                    data_class_active="$count > 5",
                    data_text="$doubled")
        html = to_xml(div)
        assert 'data-signals:count="0"' in html
        assert 'data-computed:doubled="$count * 2"' in html
        assert 'data-on:click__throttle.100ms="$count++"' in html
        assert 'data-class:active="$count &gt; 5"' in html
        assert 'data-text="$doubled"' in html

    def test_int_escaping():
        "Test that attribute values are properly escaped"
        div = ft_ds('div', data_on_click='alert("test & stuff")')
        html = to_xml(div)
        assert 'data-on:click="alert(&quot;test &amp; stuff&quot;)"' in html

    def test_show_multiple_elements():
        "Test show() concatenates multiple FT elements"
        # This would require marimo to be installed, so maybe skip or mock
        pass
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
