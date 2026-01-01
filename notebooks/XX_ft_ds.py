import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full", css_file="mike.css", html_head_file="mike.html")

with app.setup:
    from functools import partial
    from fastcore.xml import attrmap, to_xml, FT, ft, NotStr
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
    from fastcore.xml import Html, Head, Body, Header, Nav, Main, Aside, Footer, Div, H1, H2, H3, H4, H5, H6, P, A, Ul, Li, Img, Script, Link, Meta, Title, Strong, Code, Pre, Hr, Button, Section, Small, Input, Span
    return (
        A,
        Aside,
        Body,
        Button,
        Div,
        Footer,
        H1,
        Header,
        Li,
        Main,
        Nav,
        P,
        Section,
        Small,
        Ul,
    )


@app.cell
def _():
    def _repr_html_(self):
        return str(to_xml(self))

    FT._repr_html_ = _repr_html_
    return


@app.cell(hide_code=True)
def _():
    ICONS = {
        'logo':        '''<svg width="135" height="31" viewBox="0 0 96.625336 22.003906" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="logo" version="1.0" id="svg3" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs id="defs3" /><g id="g2-4" transform="translate(232.55574,351.7295)"><path id="path29-8" style="fill:none;fill-opacity:1;stroke:#ca2b39;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;paint-order:normal" d="m -231.55573,-338.2295 h 8 m 4,-12.5 h -12 v 20 h 12" /><path id="path31-7-5-0" style="fill:none;fill-opacity:1;stroke:#ca2b39;stroke-width:2;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:3.7;stroke-dasharray:none;stroke-opacity:1;paint-order:normal" d="m -208.54829,-343.2295 -4,7.5 m 1.33333,-2.5 -4,7.5 m -6.66667,-12.5 4,7.5 m -1.33333,-2.5 4,7.5" /><path id="path39-4" style="fill:none;fill-opacity:1;stroke:#ca2b39;stroke-width:2;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:3.7;stroke-dasharray:none;stroke-opacity:1;paint-order:normal" d="m -200.66445,-330.7295 0.92885,-1.74134 m -7.17885,-4.50866 h 9.58202 m 0,0 1.85771,-3.48269 m -5.18973,9.73269 a 6.25,6.25 0 0 1 -6.25,-6.25 6.25,6.25 0 0 1 1.05792,-3.47921 m 0,0 a 6.25,6.25 0 0 1 5.19208,-2.77079 6.25,6.25 0 0 1 5.18973,2.76731" /><path id="path45-6" style="fill:none;fill-opacity:1;stroke:#ca2b39;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:3.7;stroke-dasharray:none;stroke-opacity:1;paint-order:normal" d="m -178.94349,-343.22559 -1.83059,1.83058 m -4.41941,-1.83058 h 6.25 v 12.5 m -12.5,-12.5 v 12.5 m 0,-6.25 a 6.25,6.25 0 0 1 6.25,-6.25 6.25,6.25 0 0 1 6.25,6.25" /><path id="path50-2-0" style="fill:none;fill-opacity:1;stroke:#ca2b39;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:3.7;stroke-dasharray:none;stroke-opacity:1;paint-order:normal" d="m -172.40792,-330.72559 h 2.5 m -5,-12.5 h 2.5 m -2.5,10 v -12.5 m 2.5,15 a 2.5,2.5 0 0 1 -2.5,-2.5" /></g><path id="path1540-3-1-2-5-6-8-3-7-1-2-44-1-9-0-2-8-3" style="display:inline;fill:none;fill-opacity:1;stroke:#0066ff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;stroke-opacity:1;paint-order:stroke fill markers" d="m 95.195603,3.0070299 c -0.95443,-0.93759 -2.26465,-1.60012 -3.69937,-1.87075 -3.36097,-0.63403004 -6.50654,1.0057 -7.02591,3.66232 -0.0416,0.26685 -0.0558,0.53791 -0.0416,0.81029 l 1.68106,3.44594 c 0.93344,0.84712 2.16492,1.4451201 3.5035,1.7012801 m -5.98786,8.31216 c 1.10445,0.85015 2.51248,1.46115 4.0241,1.74624 3.60274,0.67784 7.01221,-0.61386 7.97583,-3.02177 l -2.85973,-5.86177 c -0.93699,-0.55389 -2.01637,-0.95618 -3.14994,-1.17419 v 0 0" /><rect style="fill:none;fill-opacity:1;stroke:#0066ff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:3.7;stroke-dasharray:none;stroke-opacity:1;paint-order:normal" id="rect51-0-4-8-2" width="13" height="20" x="66.68338" y="1.0000048" ry="6.3132529" rx="6.3132529" /><circle cx="73.183411" cy="6.5000048" id="circle1-1-7-4-9-1-9-5-8-5-5-4-6" style="fill:#aaaaaa;fill-opacity:1;stroke:#aaaaaa;stroke-width:2;stroke-opacity:1" r="2" /><path id="path13-2-7-9-0-4-3-9-8-5-7-0-8-8-94" style="fill:none;fill-opacity:1;stroke:#aaaaaa;stroke-width:1.99999;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:9.4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1;paint-order:stroke fill markers" d="m 71.815173,16.73085 c -0.54951,-0.55116 -0.71245,-1.38055 -0.41245,-2.09946 0.29997,-0.71889 1.00341,-1.18489 1.78067,-1.1796 0.77733,0.005 1.47446,0.48084 1.76465,1.20383 0.29017,0.72295 0.11595,1.55002 -0.44101,2.09361" /></svg>''',

        'account-settings':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user-cog-icon lucide-user-cog"><path d="M10 15H6a4 4 0 0 0-4 4v2"/><path d="m14.305 16.53.923-.382"/><path d="m15.228 13.852-.923-.383"/><path d="m16.852 12.228-.383-.923"/><path d="m16.852 17.772-.383.924"/><path d="m19.148 12.228.383-.923"/><path d="m19.53 18.696-.382-.924"/><path d="m20.772 13.852.924-.383"/><path d="m20.772 16.148.924.383"/><circle cx="18" cy="15" r="3"/><circle cx="9" cy="7" r="4"/></svg>''',
        'arrow-left':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-left-icon lucide-arrow-left"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>''',
        'arrow-right': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right-icon lucide-arrow-right"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>''',
        'bell':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bell-icon lucide-bell"><path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/></svg>''',
        'bicycle':     '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 512 512"><path fill="currentColor" d="M388 448a92 92 0 1 1 92-92a92.1 92.1 0 0 1-92 92m0-152a60 60 0 1 0 60 60a60.07 60.07 0 0 0-60-60M124 448a92 92 0 1 1 92-92a92.1 92.1 0 0 1-92 92m0-152a60 60 0 1 0 60 60a60.07 60.07 0 0 0-60-60m196-168a31.89 31.89 0 0 0 32-32.1A31.55 31.55 0 0 0 320.2 64a32 32 0 1 0-.2 64"/><path fill="currentColor" d="M367.55 192h-43.76a4 4 0 0 1-3.51-2.08l-31.74-58.17a31 31 0 0 0-49.38-7.75l-69.86 70.4a32.56 32.56 0 0 0-9.3 22.4c0 17.4 12.6 23.6 18.5 27.1c28.5 16.42 48.57 28.43 59.58 35.1a4 4 0 0 1 1.92 3.41v69.12c0 8.61 6.62 16 15.23 16.43A16 16 0 0 0 272 352v-86a16 16 0 0 0-6.66-13l-37-26.61a4 4 0 0 1-.58-6l42-44.79a4 4 0 0 1 6.42.79L298 215.77a16 16 0 0 0 14 8.23h56a16 16 0 0 0 16-16.77c-.42-8.61-7.84-15.23-16.45-15.23"/></svg>''',
        'bold':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bold-icon lucide-bold"><path d="M6 12h9a4 4 0 0 1 0 8H7a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h7a4 4 0 0 1 0 8"/></svg>''',
        'bookmark':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-marked-icon lucide-book-marked"><path d="M10 2v8l3-3 3 3V2"/><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/></svg>''',
        'calendar':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar1-icon lucide-calendar-1"><path d="M11 14h1v4"/><path d="M16 2v4"/><path d="M3 10h18"/><path d="M8 2v4"/><rect x="3" y="4" width="18" height="18" rx="2"/></svg>''',
        'car':         '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-car-icon lucide-car"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>''',
        'chart-area':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-area-icon lucide-chart-area"><path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M7 11.207a.5.5 0 0 1 .146-.353l2-2a.5.5 0 0 1 .708 0l3.292 3.292a.5.5 0 0 0 .708 0l4.292-4.292a.5.5 0 0 1 .854.353V16a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1z"/></svg>''',
        'chart-line':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-line-icon lucide-chart-line"><path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="m19 9-5 5-4-4-3 3"/></svg>''',
        'chart-no-axis-combined': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-no-axes-combined-icon lucide-chart-no-axes-combined"><path d="M12 16v5"/><path d="M16 14v7"/><path d="M20 10v11"/><path d="m22 3-8.646 8.646a.5.5 0 0 1-.708 0L9.354 8.354a.5.5 0 0 0-.707 0L2 15"/><path d="M4 18v3"/><path d="M8 14v7"/></svg>''',
        'check':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check-icon lucide-check"><path d="M20 6 9 17l-5-5"/></svg>''',
        'chevron-up':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-up-icon lucide-chevron-up"><path d="m18 15-6-6-6 6"/></svg>''',
        'circle-dashed': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-dashed-icon lucide-circle-dashed"><path d="M10.1 2.182a10 10 0 0 1 3.8 0"/><path d="M13.9 21.818a10 10 0 0 1-3.8 0"/><path d="M17.609 3.721a10 10 0 0 1 2.69 2.7"/><path d="M2.182 13.9a10 10 0 0 1 0-3.8"/><path d="M20.279 17.609a10 10 0 0 1-2.7 2.69"/><path d="M21.818 10.1a10 10 0 0 1 0 3.8"/><path d="M3.721 6.391a10 10 0 0 1 2.7-2.69"/><path d="M6.391 20.279a10 10 0 0 1-2.69-2.7"/></svg>''',
        'clipboard':   '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clipboard-icon lucide-clipboard"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>''',
        'contrast':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-contrast-icon lucide-contrast"><circle cx="12" cy="12" r="10"/><path d="M12 18a6 6 0 0 0 0-12v12z"/></svg>''',
        'cuboid':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-cuboid-icon lucide-cuboid"><path d="m21.12 6.4-6.05-4.06a2 2 0 0 0-2.17-.05L2.95 8.41a2 2 0 0 0-.95 1.7v5.82a2 2 0 0 0 .88 1.66l6.05 4.07a2 2 0 0 0 2.17.05l9.95-6.12a2 2 0 0 0 .95-1.7V8.06a2 2 0 0 0-.88-1.66Z"/><path d="M10 22v-8L2.25 9.15"/><path d="m10 14 11.77-6.87"/></svg>''',
        'external-link': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link-icon lucide-external-link"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>''',
        'drink':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M18 3l-2 18h-9l-2 -18Z"/><path d="M6 7.67c0.6 -0.37 1.22 -0.67 2 -0.67c2 0 3 2 5 2c1.64 0 2.6 -1.34 4 -1.83"/></g></svg>''',
        'G':           '''<svg xmlns="http://www.w3.org/2000/svg" fill="none" version="1.1" width="24" height="24" viewBox="0 0 24 24"> <g transform="translate(-8,-8.1159)" clip-path="url(#a)"> <path d="m29.6 20.227c0-.7091-.0636-1.3909-.1818-2.0455h-9.4182v3.8682h5.3818c-.2318 1.25-.9363 2.3091-1.9954 3.0182v2.5091h3.2318c1.8909-1.7409 2.9818-4.3046 2.9818-7.35z" fill="#4285f4"/> <path d="m20 30c2.7 0 4.9636-.8955 6.6181-2.4227l-3.2318-2.5091c-.8954.6-2.0409.9545-3.3863.9545-2.6046 0-4.8091-1.7591-5.5955-4.1227h-3.3409v2.5909c1.6455 3.2682 5.0273 5.5091 8.9364 5.5091z" fill="#34a853"/> <path d="m14.404 21.9c-.2-.6-.3136-1.2409-.3136-1.9s.1136-1.3.3136-1.9v-2.5909h-3.3409c-.6772 1.35-1.0636 2.8773-1.0636 4.4909s.3864 3.1409 1.0636 4.4909z" fill="#fbbc04"/> <path d="m20 13.977c1.4681 0 2.7863.5045 3.8227 1.4954l2.8682-2.8682c-1.7318-1.6136-3.9955-2.6045-6.6909-2.6045-3.9091 0-7.2909 2.2409-8.9364 5.5091l3.3409 2.5909c.7864-2.3636 2.9909-4.1227 5.5955-4.1227z" fill="#e94235"/> </g> <defs> <clipPath id="a"> <rect transform="translate(10,10)" width="20" height="20" fill="#fff"/> </clipPath> </defs> </svg>''',
        'gauge':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-gauge-icon lucide-gauge"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>''',
        'handshake':   '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-handshake-icon lucide-handshake"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/></svg>''',
        'heart':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-heart-icon lucide-heart"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>''',
        'helping-hand':'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-hand-helping-icon lucide-hand-helping"><path d="M11 12h2a2 2 0 1 0 0-4h-3c-.6 0-1.1.2-1.4.6L3 14"/><path d="m7 18 1.6-1.4c.3-.4.8-.6 1.4-.6h4c1.1 0 2.1-.4 2.8-1.2l4.6-4.4a2 2 0 0 0-2.75-2.91l-4.2 3.9"/><path d="m2 13 6 6"/></svg>''',
        'home':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-house-icon lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>''',
        'info':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info-icon lucide-info"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>''', 
        'italic':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-italic-icon lucide-italic"><line x1="19" x2="10" y1="4" y2="4"/><line x1="14" x2="5" y1="20" y2="20"/><line x1="15" x2="9" y1="4" y2="20"/></svg>''',
        'land-plot':   '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-land-plot-icon lucide-land-plot"><path d="m12 8 6-3-6-3v10"/><path d="m8 11.99-5.5 3.14a1 1 0 0 0 0 1.74l8.5 4.86a2 2 0 0 0 2 0l8.5-4.86a1 1 0 0 0 0-1.74L16 12"/><path d="m6.49 12.85 11.02 6.3"/><path d="M17.51 12.85 6.5 19.15"/></svg>''',
        'lock':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-lock-keyhole-icon lucide-lock-keyhole"><circle cx="12" cy="16" r="1"/><rect x="3" y="10" width="18" height="12" rx="2"/><path d="M7 10V7a5 5 0 0 1 10 0v3"/></svg>''',
        'log-in':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-log-in-icon lucide-log-in"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" x2="3" y1="12" y2="12"/></svg>''',
        'log-out':     '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-log-out-icon lucide-log-out"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>''',
        'mail-check':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-mail-check-icon lucide-mail-check"><path d="M22 13V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12c0 1.1.9 2 2 2h8"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/><path d="m16 19 2 2 4-4"/></svg>''',
        'map':         '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-map-icon lucide-map"><path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/></svg>''',
        'menu':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu-icon lucide-menu"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>''',
        'monitor-cog': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-monitor-cog-icon lucide-monitor-cog"><path d="M12 17v4"/><path d="m14.305 7.53.923-.382"/><path d="m15.228 4.852-.923-.383"/><path d="m16.852 3.228-.383-.924"/><path d="m16.852 8.772-.383.923"/><path d="m19.148 3.228.383-.924"/><path d="m19.53 9.696-.382-.924"/><path d="m20.772 4.852.924-.383"/><path d="m20.772 7.148.924.383"/><path d="M22 13v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"/><path d="M8 21h8"/><circle cx="18" cy="6" r="3"/></svg>''',
        'moon':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-moon-icon lucide-moon"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>''',
        'open-book-check': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open-check-icon lucide-book-open-check"><path d="M12 21V7"/><path d="m16 12 2 2 4-4"/><path d="M22 6V4a1 1 0 0 0-1-1h-5a4 4 0 0 0-4 4 4 4 0 0 0-4-4H3a1 1 0 0 0-1 1v13a1 1 0 0 0 1 1h6a3 3 0 0 1 3 3 3 3 0 0 1 3-3h6a1 1 0 0 0 1-1v-1.3"/></svg>''',
        'orbit':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-orbit-icon lucide-orbit"><path d="M20.341 6.484A10 10 0 0 1 10.266 21.85"/><path d="M3.659 17.516A10 10 0 0 1 13.74 2.152"/><circle cx="12" cy="12" r="3"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/></svg>''',
        'package':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-package-icon lucide-package"><path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><polyline points="3.29 7 12 12 20.71 7"/><path d="m7.5 4.27 9 5.15"/></svg>''',
        'package-search': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-package-search-icon lucide-package-search"><path d="M21 10V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l2-1.14"/><path d="m7.5 4.27 9 5.15"/><polyline points="3.29 7 12 12 20.71 7"/><line x1="12" x2="12" y1="22" y2="12"/><circle cx="18.5" cy="15.5" r="2.5"/><path d="M20.27 17.27 22 19"/></svg>''',
        'paintbrush':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-paintbrush-icon lucide-paintbrush"><path d="m14.622 17.897-10.68-2.913"/><path d="M18.376 2.622a1 1 0 1 1 3.002 3.002L17.36 9.643a.5.5 0 0 0 0 .707l.944.944a2.41 2.41 0 0 1 0 3.408l-.944.944a.5.5 0 0 1-.707 0L8.354 7.348a.5.5 0 0 1 0-.707l.944-.944a2.41 2.41 0 0 1 3.408 0l.944.944a.5.5 0 0 0 .707 0z"/><path d="M9 8c-1.804 2.71-3.97 3.46-6.583 3.948a.507.507 0 0 0-.302.819l7.32 8.883a1 1 0 0 0 1.185.204C12.735 20.405 16 16.792 16 15"/></svg>''',
        'paintcan':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-paint-bucket-icon lucide-paint-bucket"><path d="m19 11-8-8-8.6 8.6a2 2 0 0 0 0 2.8l5.2 5.2c.8.8 2 .8 2.8 0L19 11Z"/><path d="m5 2 5 5"/><path d="M2 13h15"/><path d="M22 20a2 2 0 1 1-4 0c0-1.6 1.7-2.4 2-4 .3 1.6 2 2.4 2 4Z"/></svg>''',
        'save':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-save-icon lucide-save"><path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/><path d="M7 3v4a1 1 0 0 0 1 1h7"/></svg>''',
        'search':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search-icon lucide-search"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>''',
        'settings':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-settings-icon lucide-settings"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>''',
        'shield':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shield-icon lucide-shield"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>''',
        'shield-check':'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shield-check-icon lucide-shield-check"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>''',
        'shopping-basket': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shopping-basket-icon lucide-shopping-basket"><path d="m15 11-1 9"/><path d="m19 11-4-7"/><path d="M2 11h20"/><path d="m3.5 11 1.6 7.4a2 2 0 0 0 2 1.6h9.8a2 2 0 0 0 2-1.6l1.7-7.4"/><path d="M4.5 15.5h15"/><path d="m5 11 4-7"/><path d="m9 11 1 9"/></svg>''',
        'square-check-big': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-check-big-icon lucide-square-check-big"><path d="M21 10.5V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12.5"/><path d="m9 11 3 3L22 4"/></svg>''',
        'sun':         '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sun-icon lucide-sun"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>''',
        'sun-moon':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sun-moon-icon lucide-sun-moon"><path d="M12 8a2.83 2.83 0 0 0 4 4 4 4 0 1 1-4-4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.9 4.9 1.4 1.4"/><path d="m17.7 17.7 1.4 1.4"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.3 17.7-1.4 1.4"/><path d="m19.1 4.9-1.4 1.4"/></svg>''',
        'table':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-table-icon lucide-table"><path d="M12 3v18"/><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/></svg>''',
        'user-pen':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user-pen-icon lucide-user-pen"><path d="M11.5 15H7a4 4 0 0 0-4 4v2"/><path d="M21.378 16.626a1 1 0 0 0-3.004-3.004l-4.01 4.012a2 2 0 0 0-.506.854l-.837 2.87a.5.5 0 0 0 .62.62l2.87-.837a2 2 0 0 0 .854-.506z"/><circle cx="10" cy="7" r="4"/></svg>''',
        'user-plus':   '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user-plus-icon lucide-user-plus"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/></svg>''',
        'underline':   '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-underline-icon lucide-underline"><path d="M6 4v6a6 6 0 0 0 12 0V4"/><line x1="4" x2="20" y1="20" y2="20"/></svg>''',
        'walk':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M12 4a1 1 0 1 0 2 0a1 1 0 1 0-2 0M7 21l3-4m6 4l-2-4l-3-3l1-6"/><path d="m6 12l2-3l4-1l3 3l3 1"/></g></svg>''',
        'x':           '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x-icon lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>''',

        # Special Colors
        'cyan':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="oklch(0.58 0.1869 245)" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-icon lucide-square"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',
        'red':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="oklch(0.58 0.1869 60)" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-icon lucide-square"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',
        'pink':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="oklch(0.58 0.1869 25)" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-icon lucide-square"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',
        'indigo':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="oklch(0.58 0.1869 305)" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-icon lucide-square"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',
        'blue':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="oklch(0.58 0.1869 275)" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-icon lucide-square"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',
        'green':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="oklch(0.58 0.1869 180)" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-icon lucide-square"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',
        'lime':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="oklch(0.58 0.1869 160)" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-icon lucide-square"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>''',


        # add additional icons here, keep in alphebetical order #todo add caching if you feel like it has not been a problem
    }
    return (ICONS,)


@app.cell
def _(ICONS):

    def Icon(name:str,     # Name of the icon to display
             size:int=24,  # Height and width of the icon in pixels
             stroke:int=2, # Stroke width of the icon
             cls:str=None, # Optional CSS class to apply to the icon
             **kwargs      # Additional HTML attributes for the SVG element
            ) -> 'Any':    # Follow recomendation for dynamic hints
        '''
        Creates an SVG icon element with the specified name, size, and stroke 
        Intended to be used with a Dict of ICONS{ } 
        Use only Stroke Icons for best results
        '''
        if name not in ICONS: raise ValueError(f"Icon '{name}' not found")

        # Replace only the first occurrence of each attribute
        svg_string = ICONS[name]
        svg_string = re.sub(r'width="\d+"', f'width="{size}"', svg_string, count=1)
        svg_string = re.sub(r'height="\d+"', f'height="{size}"', svg_string, count=1)
        svg_string = re.sub(r'stroke-width="\d+"', f'stroke-width="{stroke}"', svg_string, count=1)

        return ft(f'icon-{name}', NotStr(svg_string), cls=cls, **kwargs)
    return (Icon,)


@app.cell
def _():
    NAV = "white-space: nowrap; width: calc-size(auto, size + 1rem);"
    CARD = "border: 1px solid hsl(0 0% 80%); border-radius: 0.5rem; outline: 1px solid hsl(0 0% 90%); outline-offset: -1px; padding: 0.5rem"
    return CARD, NAV


@app.cell
def _(
    A,
    Aside,
    Button,
    CARD,
    Div,
    Footer,
    H1,
    Header,
    Icon,
    Li,
    Main,
    NAV,
    Nav,
    P,
    Section,
    Small,
    Ul,
):
    Section(
        style="""background: #3D3C3A;
        margin: 0;
        padding:0; 
        display:grid; 
        grid-template: auto 1fr auto / auto 1fr auto; 
        gap: 0.5em;
      """,
        **{"data-signals":"{_header: true, _nav: true, _footer: false, _aside: false, _fullscreen: false}",
           "data-style:height": "$_fullscreen ? '100svh' : '50svh'"
          }
           )(
        Header(id="header", style=CARD,
            **{"data-style:grid-area":"`1/1/${1+$_header}/4`",
               "data-show":"$_header"}
        )(
            Div(cls="--make-split:row")(
                Div(cls="--make-flank")(
                    Button(Icon('package'),    **{"data-on:click":"$_nav= !$_nav"}),
                    H1('Template Layout', style="white-space: nowrap")
                ),
                Button(Icon('menu'),  **{"data-on:click":"$_aside= !$_aside"}),
            )
        ),
        Nav(id="nav", style=CARD,
                **{
                "data-show":"$_nav",
                "data-style:grid-area":"`${1+$_header}/1/${3+!$_footer}/1`"
            })(
                Button(style=NAV,
                    **{
                      "data-on:click":"$_activeNav = 'readme'",
                      "data-attr:class":"$_activeNav === 'readme' ? '--make-split' : '--make-cluster'"
                    })(
                    Icon('info'),
                    P('Readme')
                ),
                Button(style=NAV,
                    **{
                      "data-on:click":"$_activeNav = 'map'",
                      "data-attr:class":"$_activeNav === 'map' ? '--make-split' : '--make-cluster'"
                    })(
                    Icon('map'),
                    P('Map')
                ),
                Button(style=NAV,
                    **{
                      "data-on:click":"$_activeNav = 'report'",
                      "data-attr:class":"$_activeNav === 'report' ? '--make-split' : '--make-cluster'"
                    })(
                    Icon('chart-line'),
                    P('Reports')
                ),
                Button(style=NAV,
                    **{
                      "data-on:click":"$_activeNav = 'settings'",
                      "data-attr:class":"$_activeNav === 'settings' ? '--make-split' : '--make-cluster'"
                    })(
                    Icon('settings'),
                    P('Settings')
                ),
        ),

        Main( id="main", style=CARD,
            **{"data-style:grid-area":"` ${1+$_header} / ${1+$_nav} / ${3+!$_footer} / ${3+!$_aside}` "})(
            H1("Main", data_text="$_activeNav"),
            Button(Icon('menu'),    **{"data-on:click":"$_nav= !$_nav"}),
            Button("Footer", **{"data-on:click":"$_footer = !$_footer"}),
            Button("Full Screen?", **{"data-on:click":"$_fullscreen = !$_fullscreen"}),

        ),

        Aside(**{
            "data-show":"$_aside",
            "data-style:grid-area":"`${1+$_header}/3/${3+!$_footer}/4`"
        })(
            Ul(
                Li( A("Home Page", href="someLink") ),
                Li( A("Map Page", href="someLink") ),
                Li( A("Stuff Page", href="someLink") ),
                Li( A("Calendar Page", href="someLink") ),
                Li( A("Contacts Page", href="someLink") ),
                Li( A("Settings", href="someLink") ),
            )
        ),


        Footer(**{
            "data-show":"$_footer",
            "data-style:grid-area":"`${3+!$_footer}/1/4/4`"
        })(
            Div(cls="--make-split")(
                Small(A("About",       href="someLink")),
                Small(A("Legal",       href="someLink")),
                Small(A("Contact Us",  href="someLink")),
                Small(A("Blog",        href="someLink")),
            )
        ),
    )
    return


@app.cell
def _(Body):
    Body("")
    return


@app.cell
def _(Button, H1, Main):
    print(Main( **{"data-style:grid-area":"` ${1+$_header} / ${1+$_nav} / ${3+!$_footer} / ${3+!$_aside}` "})(
            H1("Main", data_bind="_activeNav"),
     
            Button("Footer", **{"data-on:click":"$_footer = !$_footer"}),
            Button("Full Screen?", **{"data-on:click":"$_fullscreen = !$_fullscreen"}),

    )    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
