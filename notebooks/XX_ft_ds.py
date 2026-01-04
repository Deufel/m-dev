import marimo

__generated_with = "0.18.4"
app = marimo.App(
    width="full",
    css_file="public/styles.css",
    html_head_file="public/mike.html",
)

with app.setup:
    from functools import partial
    from fastcore.xml import attrmap, to_xml, FT, ft, NotStr
    from fasthtml.components import ft_html, show
    from fastcore.meta import use_kwargs
    from typing import Literal, Optional
    import json, re, sys, uuid
    from pathlib import Path
    from b_read import scan, read_config
    from a_core import read_config, Node


    from fastcore.xml import Html, Head, Body, Header, Nav, Main, Aside, Footer, Div, H1, H2, H3, H4, H5, H6, P, A, Ul, Li, Img, Script, Link, Meta, Title, Strong, Code, Pre, Hr, Button, Section, Small, Input, Span, Iframe, Article, Style


    __ds_special = 'on_intersect on_interval on_signal_patch on_signal_patch_filter on_raf on_resize preserve_attr json_signals scroll_into_view view_transition custom_validity replace_url query_string persist'.split()
    __ds_prefixes = 'on bind signals computed class style attr ref indicator'.split()
    __mod_pat = re.compile(r'_(\d+(?:ms|s)?|leading|trailing|notrailing|noleading|camel|kebab|snake|pascal|self|terse)')
    __tags = 'A Abbr Address Area Article Aside Audio B Base Bdi Bdo Blockquote Body Br Button Canvas Caption Cite Code Col Colgroup Data Datalist Dd Del Details Dfn Dialog Div Dl Dt Em Embed Fieldset Figcaption Figure Footer Form H1 H2 H3 H4 H5 H6 Head Header Hgroup Hr I Iframe Img Input Ins Kbd Label Legend Li Link Main Map Mark Menu Meta Meter Nav Noscript Object Ol Optgroup Option Output P Picture Pre Progress Q Rp Rt Ruby S Samp Script Search Section Select Slot Small Source Span Strong Style Sub Summary Sup Table Tbody Td Template Textarea Tfoot Th Thead Time Title Tr Track U Ul Var Video Wbr'.split()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Local Setup
    Dev stuff helpers..
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pytest
    return (mo,)


@app.cell
def _():

    icons = {

        'account-settings':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user-cog-icon lucide-user-cog"><path d="M10 15H6a4 4 0 0 0-4 4v2"/><path d="m14.305 16.53.923-.382"/><path d="m15.228 13.852-.923-.383"/><path d="m16.852 12.228-.383-.923"/><path d="m16.852 17.772-.383.924"/><path d="m19.148 12.228.383-.923"/><path d="m19.53 18.696-.382-.924"/><path d="m20.772 13.852.924-.383"/><path d="m20.772 16.148.924.383"/><circle cx="18" cy="15" r="3"/><circle cx="9" cy="7" r="4"/></svg>''',
        'arrow-left':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-left-icon lucide-arrow-left"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>''',
        'arrow-right': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right-icon lucide-arrow-right"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>''',
        'blocks':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-blocks-icon lucide-blocks"><path d="M10 22V7a1 1 0 0 0-1-1H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5a1 1 0 0 0-1-1H2"/><rect x="14" y="2" width="8" height="8" rx="1"/></svg>''',
        'bell':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bell-icon lucide-bell"><path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/></svg>''',
        'bicycle':     '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 512 512"><path fill="currentColor" d="M388 448a92 92 0 1 1 92-92a92.1 92.1 0 0 1-92 92m0-152a60 60 0 1 0 60 60a60.07 60.07 0 0 0-60-60M124 448a92 92 0 1 1 92-92a92.1 92.1 0 0 1-92 92m0-152a60 60 0 1 0 60 60a60.07 60.07 0 0 0-60-60m196-168a31.89 31.89 0 0 0 32-32.1A31.55 31.55 0 0 0 320.2 64a32 32 0 1 0-.2 64"/><path fill="currentColor" d="M367.55 192h-43.76a4 4 0 0 1-3.51-2.08l-31.74-58.17a31 31 0 0 0-49.38-7.75l-69.86 70.4a32.56 32.56 0 0 0-9.3 22.4c0 17.4 12.6 23.6 18.5 27.1c28.5 16.42 48.57 28.43 59.58 35.1a4 4 0 0 1 1.92 3.41v69.12c0 8.61 6.62 16 15.23 16.43A16 16 0 0 0 272 352v-86a16 16 0 0 0-6.66-13l-37-26.61a4 4 0 0 1-.58-6l42-44.79a4 4 0 0 1 6.42.79L298 215.77a16 16 0 0 0 14 8.23h56a16 16 0 0 0 16-16.77c-.42-8.61-7.84-15.23-16.45-15.23"/></svg>''',
        'bold':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bold-icon lucide-bold"><path d="M6 12h9a4 4 0 0 1 0 8H7a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h7a4 4 0 0 1 0 8"/></svg>''',
        'book-open-text': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open-text-icon lucide-book-open-text"><path d="M12 7v14"/><path d="M16 12h2"/><path d="M16 8h2"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/><path d="M6 12h2"/><path d="M6 8h2"/></svg>''',
        'bookmark':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-marked-icon lucide-book-marked"><path d="M10 2v8l3-3 3 3V2"/><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/></svg>''',
        'calendar':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar1-icon lucide-calendar-1"><path d="M11 14h1v4"/><path d="M16 2v4"/><path d="M3 10h18"/><path d="M8 2v4"/><rect x="3" y="4" width="18" height="18" rx="2"/></svg>''',
        'car':         '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-car-icon lucide-car"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>''',
        'circle-x':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-x-icon lucide-circle-x"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>''',
        'chart-area':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-area-icon lucide-chart-area"><path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M7 11.207a.5.5 0 0 1 .146-.353l2-2a.5.5 0 0 1 .708 0l3.292 3.292a.5.5 0 0 0 .708 0l4.292-4.292a.5.5 0 0 1 .854.353V16a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1z"/></svg>''',
        'chart-line':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-line-icon lucide-chart-line"><path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="m19 9-5 5-4-4-3 3"/></svg>''',
        'chart-no-axis-combined': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-no-axes-combined-icon lucide-chart-no-axes-combined"><path d="M12 16v5"/><path d="M16 14v7"/><path d="M20 10v11"/><path d="m22 3-8.646 8.646a.5.5 0 0 1-.708 0L9.354 8.354a.5.5 0 0 0-.707 0L2 15"/><path d="M4 18v3"/><path d="M8 14v7"/></svg>''',
        'check':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check-icon lucide-check"><path d="M20 6 9 17l-5-5"/></svg>''',
        'chevron-up':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-up-icon lucide-chevron-up"><path d="m18 15-6-6-6 6"/></svg>''',
        'circle-chevron-up': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-chevron-up-icon lucide-circle-chevron-up"><circle cx="12" cy="12" r="10"/><path d="m8 14 4-4 4 4"/></svg>''',
        'chevron-down': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-down-icon lucide-chevron-down"><path d="m6 9 6 6 6-6"/></svg>''',
        'circle-dashed': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-dashed-icon lucide-circle-dashed"><path d="M10.1 2.182a10 10 0 0 1 3.8 0"/><path d="M13.9 21.818a10 10 0 0 1-3.8 0"/><path d="M17.609 3.721a10 10 0 0 1 2.69 2.7"/><path d="M2.182 13.9a10 10 0 0 1 0-3.8"/><path d="M20.279 17.609a10 10 0 0 1-2.7 2.69"/><path d="M21.818 10.1a10 10 0 0 1 0 3.8"/><path d="M3.721 6.391a10 10 0 0 1 2.7-2.69"/><path d="M6.391 20.279a10 10 0 0 1-2.69-2.7"/></svg>''',
        'clipboard':   '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clipboard-icon lucide-clipboard"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>''',
        'contrast':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-contrast-icon lucide-contrast"><circle cx="12" cy="12" r="10"/><path d="M12 18a6 6 0 0 0 0-12v12z"/></svg>''',
        'code':        '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-code-icon lucide-code"><path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/></svg>''',
        'cuboid':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-cuboid-icon lucide-cuboid"><path d="m21.12 6.4-6.05-4.06a2 2 0 0 0-2.17-.05L2.95 8.41a2 2 0 0 0-.95 1.7v5.82a2 2 0 0 0 .88 1.66l6.05 4.07a2 2 0 0 0 2.17.05l9.95-6.12a2 2 0 0 0 .95-1.7V8.06a2 2 0 0 0-.88-1.66Z"/><path d="M10 22v-8L2.25 9.15"/><path d="m10 14 11.77-6.87"/></svg>''',
        'external-link': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link-icon lucide-external-link"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>''',
        'drink':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M18 3l-2 18h-9l-2 -18Z"/><path d="M6 7.67c0.6 -0.37 1.22 -0.67 2 -0.67c2 0 3 2 5 2c1.64 0 2.6 -1.34 4 -1.83"/></g></svg>''',
        'expand':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-expand-icon lucide-expand"><path d="m15 15 6 6"/><path d="m15 9 6-6"/><path d="M21 16v5h-5"/><path d="M21 8V3h-5"/><path d="M3 16v5h5"/><path d="m3 21 6-6"/><path d="M3 8V3h5"/><path d="M9 9 3 3"/></svg>''',
        'fullscreen':  '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-fullscreen-icon lucide-fullscreen"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><rect width="10" height="8" x="7" y="8" rx="1"/></svg>''',  
        'G':           '''<svg xmlns="http://www.w3.org/2000/svg" fill="none" version="1.1" width="24" height="24" viewBox="0 0 24 24"> <g transform="translate(-8,-8.1159)" clip-path="url(#a)"> <path d="m29.6 20.227c0-.7091-.0636-1.3909-.1818-2.0455h-9.4182v3.8682h5.3818c-.2318 1.25-.9363 2.3091-1.9954 3.0182v2.5091h3.2318c1.8909-1.7409 2.9818-4.3046 2.9818-7.35z" fill="#4285f4"/> <path d="m20 30c2.7 0 4.9636-.8955 6.6181-2.4227l-3.2318-2.5091c-.8954.6-2.0409.9545-3.3863.9545-2.6046 0-4.8091-1.7591-5.5955-4.1227h-3.3409v2.5909c1.6455 3.2682 5.0273 5.5091 8.9364 5.5091z" fill="#34a853"/> <path d="m14.404 21.9c-.2-.6-.3136-1.2409-.3136-1.9s.1136-1.3.3136-1.9v-2.5909h-3.3409c-.6772 1.35-1.0636 2.8773-1.0636 4.4909s.3864 3.1409 1.0636 4.4909z" fill="#fbbc04"/> <path d="m20 13.977c1.4681 0 2.7863.5045 3.8227 1.4954l2.8682-2.8682c-1.7318-1.6136-3.9955-2.6045-6.6909-2.6045-3.9091 0-7.2909 2.2409-8.9364 5.5091l3.3409 2.5909c.7864-2.3636 2.9909-4.1227 5.5955-4.1227z" fill="#e94235"/> </g> <defs> <clipPath id="a"> <rect transform="translate(10,10)" width="20" height="20" fill="#fff"/> </clipPath> </defs> </svg>''',
        'github':      '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-github-icon lucide-github"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>''',
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
        'minimize':    '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-minimize2-icon lucide-minimize-2"><path d="m14 10 7-7"/><path d="M20 10h-6V4"/><path d="m3 21 7-7"/><path d="M4 14h6v6"/></svg>''',
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
        'scale':       '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-scale-icon lucide-scale"><path d="M12 3v18"/><path d="m19 8 3 8a5 5 0 0 1-6 0zV7"/><path d="M3 7h1a17 17 0 0 0 8-2 17 17 0 0 0 8 2h1"/><path d="m5 8 3 8a5 5 0 0 1-6 0zV7"/><path d="M7 21h10"/></svg>''',
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
    return (icons,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Docs Generator

    > This is a work in progress for a static site generator that will let the docs be easy to publish to github

    ```md
    In general this is not as robust as the rest of the project as this does not impact the performance as much, and this has external dependencies...

    goals for generated docs
        1. mobile friendly
        2. build in navigation for readme page, and pages for all modules. and a all page...
        3. delacate balance between customization and long term maintanability
        4. use githubs ability to fetch get requests and build full html pages with datastar to navigate website.

    Setup:
        for marimo to serve local files they need to be in a public directory adjacent to notebooks (ie mkdir ./notebooks/public) may need to rething config set up
    ```
    """)
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
def _(AttrDict, StreamingResponse, asyncio):
    def sse_signals(signals): return f"event: datastar-patch-signals\ndata: signals {json.dumps(signals)}\n\n"
    def sse_morph(selector, html, mode='inner'): return f"event: datastar-patch-elements\ndata: selector {selector}\ndata: mode {mode}\ndata: elements {html.replace(chr(10), ' ')}\n\n"
    def sse_remove(selector): return sse_morph(selector, '', 'remove')
    class Broadcaster:
        def __init__(self): self.clients = set()
        async def connect(self, initial=None):
            q = asyncio.Queue()
            self.clients.add(q)
            async def gen():
                try:
                    if initial: yield initial() if callable(initial) else initial
                    while True: yield await q.get()
                except asyncio.CancelledError: pass
                finally: self.clients.discard(q)
            return StreamingResponse(gen(), media_type="text/event-stream")
        async def send(self, msg):
            for q in list(self.clients): await q.put(msg)
        def __len__(self): return len(self.clients)
    def scoped(prefix):
        def sig(name): return f"{prefix}{name}"
        def ui(name): return f"_{prefix}{name}"
        def ref(name): return f"${prefix}{name}"
        def ui_ref(name): return f"$_{prefix}{name}"
        return AttrDict(sig=sig, ui=ui, ref=ref, ui_ref=ui_ref)
    return


@app.cell
def _():
    def _repr_html_(self):
        return str(to_xml(self))

    FT._repr_html_ = _repr_html_
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## CSS

    > Bit of a hacky way to write my css in marimo this is injected into the public/styles.css file with a `extract_write_css()` function

    still for me makes for a nice dev experience
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```css
    /* remove marimo padding */
    @layer marimo {
      [id^="output-"] {
        padding: 0 !important;
      }
    }

    @layer picoscale {
        body.picoscale {
            --pico-font-family-sans-serif: Inter, system-ui, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, Helvetica, Arial, "Helvetica Neue", sans-serif, var(--pico-font-family-emoji);
            --pico-font-size: 87.5%;
            --pico-line-height: 1.25;
            --pico-form-element-spacing-vertical: 0.5rem;
            --pico-form-element-spacing-horizontal: 1.0rem;
            --pico-border-radius: 0.375rem;
        }

        @media (min-width: 576px) {
            body.picoscale {
                --pico-font-size: 87.5%;
            }
        }

        @media (min-width: 768px) {
            body.picoscale {
                --pico-font-size: 87.5%;
            }
        }

        @media (min-width: 1024px) {
            body.picoscale {
                --pico-font-size: 87.5%;
            }
        }

        @media (min-width: 1280px) {
            body.picoscale {
                --pico-font-size: 87.5%;
            }
        }

        @media (min-width: 1536px) {
            body.picoscale {
                --pico-font-size: 87.5%;
            }
        }

        body.picoscale h1,
        body.picoscale h2,
        body.picoscale h3,
        body.picoscale h4,
        body.picoscale h5,
        body.picoscale h6 {
            --pico-font-weight: 600;
        }

        body.picoscale article {
            border: 1px solid var(--pico-muted-border-color);
            border-radius: calc(var(--pico-border-radius) * 2);
        }

        body.picoscale article > footer {
            border-radius: calc(var(--pico-border-radius) * 2);
        }
    }

    @layer utils {
        /* ===== SIZE SCALE ===== */
        :where(html) {
            --make-size-1: 0.25rem;  /* 4px */
            --make-size-2: 0.5rem;   /* 8px */
            --make-size-3: 1rem;     /* 16px */
            --make-size-4: 1.5rem;   /* 24px */
            --make-size-5: 2rem;     /* 32px */
            --make-size-6: 3rem;     /* 48px */
            --make-size-7: 4rem;     /* 64px */
            --make-size-8: 6rem;     /* 96px */
        }

        /* ===== LAYOUT PRIMITIVES ===== */
        /* Reset margins for all layout primitives */
        :is(
            [class*="--make-cluster"],
            [class*="--make-flank"],
            [class*="--make-frame"],
            [class*="--make-grid"],
            [class*="--make-split"],
            [class*="--make-stack"],
            [class*="--make-lcr"],
            [class*="--make-tmb"]
        ) > * {
            margin-block: 0;
            margin-inline: 0;
        }

        /* Default gap for all layout primitives */
        :where(
            [class*="--make-cluster"],
            [class*="--make-flank"],
            [class*="--make-frame"],
            [class*="--make-grid"],
            [class*="--make-stack"],
            [class*="--make-split"],
            [class*="--make-lcr"],
            [class*="--make-tmb"]
        ) {
            gap: var(--make-size-2);
        }

        /* Cluster - flex wrap with alignment */
        [class*="--make-cluster"] {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-start;
            align-items: center;
        }

        /* Flank - flexible sidebar layout */
        [class*="--make-flank"] {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
        }

        [class*="--make-flank"]:not([class*="\:end"]) > :first-child,
        [class*="--make-flank"][class*="\:start"] > :first-child {
            flex-basis: var(--flank-size, auto);
            flex-grow: 1;
        }

        [class*="--make-flank"]:not([class*="\:end"]) > :last-child,
        [class*="--make-flank"][class*="\:start"] > :last-child {
            flex-basis: 0;
            flex-grow: 999;
            min-inline-size: var(--content-percentage, 50%);
        }

        [class*="--make-flank"][class*="\:end"] > :last-child {
            flex-basis: var(--flank-size, auto);
            flex-grow: 1;
        }

        [class*="--make-flank"][class*="\:end"] > :first-child {
            flex-basis: 0;
            flex-grow: 999;
            min-inline-size: var(--content-percentage, 50%);
        }

        /* Frame - aspect ratio container for media */
        [class*="--make-frame"] {
            display: flex;
            aspect-ratio: 1 / 1;
            justify-content: center;
            align-items: center;
            overflow: hidden;

            > img,
            > video {
                block-size: 100%;
                inline-size: 100%;
                object-fit: cover;
            }
        }

        [class*="--make-frame"][class*="\:square"] { aspect-ratio: 1 / 1; }
        [class*="--make-frame"][class*="\:landscape"] { aspect-ratio: 16 / 9; }
        [class*="--make-frame"][class*="\:portrait"] { aspect-ratio: 9 / 16; }

        /* Grid - responsive auto-fit grid */
        [class*="--make-grid"] {
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(min(var(--min-column-size, 20ch), 100%), 1fr)
            );
        }

        [class*="--make-span-grid"] { grid-column: 1 / -1; }

        /* Split - space-between layout */
        [class*="--make-split"] {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
        }

        [class*="--make-split"],
        [class*="--make-split"][class*="\:row"] {
            flex-direction: row;
            block-size: auto;
            inline-size: 100%;
        }

        [class*="--make-split"]:not([class*="\:column"]) > :first-child {
            flex: 0 1 auto;
        }

        [class*="--make-split"][class*="\:column"] {
            flex-direction: column;
            block-size: auto;
            inline-size: auto;
            align-self: stretch;
        }

        /* Stack - vertical flex layout */
        [class*="--make-stack"] {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: stretch;
        }

        /* LCR - left center right grid */
        [class*="--make-lcr"] {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
            align-items: center;
        }

        [class*="--make-lcr"] > :nth-child(1) {
            justify-self: start;
        }

        [class*="--make-lcr"] > :nth-child(2) {
            justify-self: center;
        }

        [class*="--make-lcr"] > :nth-child(3) {
            justify-self: end;
        }

        /* TMB - top middle bottom grid */
        [class*="--make-tmb"] {
            display: grid;
            grid-template-rows: minmax(0, 1fr) auto minmax(0, 1fr);
            justify-items: center;
        }

        [class*="--make-tmb"] > :nth-child(1) {
            align-self: start;
        }

        [class*="--make-tmb"] > :nth-child(2) {
            align-self: center;
        }

        [class*="--make-tmb"] > :nth-child(3) {
            align-self: end;
        }

        /* ===== CONTAINER ===== */
        .make-container {
            width: clamp(20rem, 90%, 87.5rem);
            left: 50%;
            transform: translateX(-50%) translateZ(0);
            transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            will-change: width, transform;
        }
    }

    ```
    """)
    return


@app.cell
def _(extract_write_css):
    extract_write_css()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Development

    lots of work inprogres here
    """)
    return


@app.cell
def _(icons):

    def Icon(name: str,            # name of the icon MUST be in icon_dict
             size=24,              # value to be passed to height and width of the icon
             stroke=1.5,           # stroke width 
             cls=None,             # css class
             icon_dict:dict=icons, # Dict of icons {"name":"<svg...>"}
             **kwargs              # passed to through to FT 
            ) -> 'Any':            # Follow recomendation from fastHTML docs
        '''
        Creates a custom html compliant <icon-{name}>... 
        Intended to be used with a Global Dict of icons {"home": "<svg...", "info": "<svg..."} 
        Icon('home') -> <icon-home> ....  </icon-home>
        '''
        if name not in icon_dict: raise ValueError(f"Icon '{name}' not found")

        # count=1 Replace only the first occurrence of width & height 99% of time this is what you want
        svg_string = icon_dict[name]
        svg_string = re.sub(r'width="\d+"', f'width="{size}"', svg_string, count=1)
        svg_string = re.sub(r'height="\d+"', f'height="{size}"', svg_string, count=1)
        svg_string = re.sub(r'stroke-width="\d+"', f'stroke-width="{stroke}"', svg_string)

        return ft(f'icon-{name}', NotStr(svg_string), cls=cls, **kwargs)
    return (Icon,)


@app.cell
def _(mo):
    mo.md(r"""
    # Demo layout testing
    """)
    return


@app.cell
def _():
    _NAV    = "white-space: nowrap; width: calc-size(auto, size + 1rem);"
    NAV    = "white-space: nowrap;"
    CARD   = "border: 1px solid hsl(0 0% 80%); border-radius: 0.5rem; outline: 1px solid hsl(0 0% 90%); outline-offset: -1px; padding: 0.5rem"
    HEADER = "border-radius: 0.5rem; "
    PILL   = "border: 1px solid hsl(0 0% 80%); border-radius: 9999px;  outline: 1px solid hsl(0 0% 90%); outline-offset: -1px; padding: 0.5rem 1rem; "
    LAYOUT = "margin: 0; padding:0;  display:grid;  grid-template: auto 1fr auto / auto 1fr auto;  gap: 0.5em;"
    return CARD, HEADER, NAV, PILL


@app.cell
def _():
    return


@app.cell
def _(HEADER, Icon, PILL):

    meta, mods = scan()
    repo_url = meta.get('urls', {}).get('Repository')
    pypi_url = meta.get('urls', {}).get('PyPI')
    pkg_name = meta.get('name')

    print(f"{meta.get('urls', {}).get('Repository') = }")
    print(f"{meta.get('urls', {}).get('PyPI') = }")


    header = Header(id="header", style=HEADER,
            **{"data-style:grid-area":"`1/1/${1+$_header}/4`",
               "data-show":"$_header"}
        )(
            Div(cls="--make-lcr")(
                Div(cls="--make-cluster")(
                    Button(Icon('menu'), **{"data-on:click":"$_nav= !$_nav"}),
                    Span("|"),
                    Icon("package"),
                    H1(pkg_name, style="white-space: nowrap")
                ),
                Input(style=PILL, placeholder="search..."),

                Div(cls="--make-cluster")(
                    A(Icon('blocks'), href=pypi_url),
                    A(Icon('github'), href=repo_url),
                )
            )
        )
    return mods, pkg_name, pypi_url, repo_url


@app.cell
def _(CARD, Icon, NAV, mods):
    module_names = [name.capitalize() for name, _ in mods]



    nav = Nav(id="nav", style=CARD, cls="--make-split:column")(
                **{
                "data-show":"$_nav",
                "data-style:grid-area":"`${1+$_header}/1/${3+!$_footer}/1`"
            })(
            Div(
                Button(cls="--make-cluster",style=NAV)(Icon('book-open-text', stroke=1), P('Readme')),
                Div(
                    *[Button(cls="--make-cluster")(Icon('code', stroke=1.5), P(name)) 
                      for name in module_names]
                )
            ),
            Div(
                Button(cls="--make-cluster",style=NAV)(Icon('scale'), P('License') ) ,
                Button(cls="--make-cluster",style=NAV)(Icon('settings'), P('Settings') ) ,
            )

        )


    nav
    return (module_names,)


@app.cell
def _(CARD):
    main = Main( id="main", style=CARD, **{"data-style:grid-area":"` ${1+$_header} / ${1+$_nav} / ${3+!$_footer} / ${3+!$_aside}` "})(

        Div(cls="--make-flank:end")(

            Pre(Code("Pure module code her... ")),
            Aside("I think this will be the section list here..")
        )
    )
    return


@app.cell
def _(CARD, render_function):
    def render_main(nodes: list[Node]) -> FT:
        """Render main content area with function cards for one module"""
        return Main(
            id="main", 
            style=CARD, 
            **{"data-style:grid-area": "` ${1+$_header} / ${1+$_nav} / ${3+!$_footer} / ${3+!$_aside}` "}
        )(
            *[render_function(node) for node in nodes]
        )

    return (render_main,)


@app.cell
def _(CARD):
    def render_aside(nodes: list[Node]) -> FT:
        """Render aside TOC for one module's functions"""
        return Aside(
            id="aside",
            style=CARD,
            **{"data-style:grid-area": "` ${1+$_header} / 3 / ${3+!$_footer} / 3` ",
               "data-show": "$_aside"}
        )(
            H3("Functions"),
            Ul(
                *[Li(A(node.name, href=f"#fn-{node.name}")) for node in nodes]
            )
        )
    return (render_aside,)


@app.cell
def _(HEADER, Icon, PILL, pkg_name, pypi_url, repo_url):
    def render_header() -> FT:
        """Render page header"""
        return Header(id="header", style=HEADER,
            **{"data-style:grid-area":"`1/1/${1+$_header}/4`",
               "data-show":"$_header"}
        )(
            Div(cls="--make-lcr")(
                Div(cls="--make-cluster")(
                    Button(Icon('menu'), **{"data-on:click":"$_nav= !$_nav"}),
                    Span("|"),
                    Icon("package"),
                    H1(pkg_name, style="white-space: nowrap")
                ),
                Input(style=PILL, placeholder="search..."),
                Div(cls="--make-cluster")(
                    A(Icon('blocks'), href=pypi_url),
                    A(Icon('github'), href=repo_url),
                )
            )
        )
    return (render_header,)


@app.function
def get_pages_url(repo_url: str) -> str:
    """Convert GitHub repo URL to GitHub Pages URL"""
    # https://github.com/Deufel/m-dev -> https://deufel.github.io/m-dev/
    if 'github.com' in repo_url:
        parts = repo_url.rstrip('/').split('/')
        username = parts[-2]
        repo = parts[-1]
        return f"https://{username.lower()}.github.io/{repo}/"
    return repo_url  # Return as-is if not GitHub


@app.cell
def _(CARD, Icon, NAV, module_names, repo_url):
    def render_nav() -> FT:
        """Render navigation sidebar"""
        base_url = get_pages_url(repo_url)
    
        return Nav(id="nav", style=CARD, cls="--make-split:column",
            **{
                "data-show":"$_nav",
                "data-style:grid-area":"`${1+$_header}/1/${3+!$_footer}/1`"
            }
        )(
            Div(
                A(Button(cls="--make-cluster",style=NAV)(Icon('book-open-text', stroke=1), P('Readme')), href=f"{base_url}index.html"),
                Div(
                    *[A(Button(cls="--make-cluster")(Icon('code', stroke=1.5), P(name)), href=f"{base_url}{name}.html") 
                      for name in module_names]
                )
            ),
            Div(
                A(Button(cls="--make-cluster",style=NAV)(Icon('scale'), P('License')), href=f"{base_url}LICENSE.html"),
                Button(cls="--make-cluster",style=NAV)(Icon('settings'), P('Settings')),
            )
        )

    return (render_nav,)


@app.cell
def _(render_aside, render_header, render_main, render_nav):
    def render_page(module_name: str, nodes: list[Node]) -> FT:
        """Render a complete module documentation page"""
        return Section(
            style="""background: #3D3C3A;
        
            margin: 0;
            padding:0; 
            display:grid; 
            grid-template: auto 1fr auto / auto 1fr auto; 
            gap: 0.5rem;  
            padding-inline: 1rem; 
            padding-block: 0.25rem;
            height: 100svh;
            """,
            **{"data-signals":"{_header: true, _nav: true, _footer: false, _aside: true}"}
        )(
            render_header(),
            render_nav(),   
            render_main(nodes),
            render_aside(nodes)
        )

    return (render_page,)


@app.cell
def _(CARD, get_project_root):
    def render_readme_main() -> FT:
        """Render main content area with README"""
        root = get_project_root(__file__)
        readme_path = root / 'README.md'
        readme_content = readme_path.read_text() if readme_path.exists() else "README not found"
    
        return Main(
            id="main", 
            style=f"{CARD}; max-width: 120ch; margin: 0 auto;", 
            **{"data-style:grid-area": "` ${1+$_header} / ${1+$_nav} / ${3+!$_footer} / 3` "}
        )(
            H2("README"),
            Pre(Code(readme_content, cls="language-markdown"))
        )

    def render_license_main() -> FT:
        """Render main content area with LICENSE"""
        root = get_project_root(__file__)
        license_path = root / 'LICENSE'
        license_content = license_path.read_text() if license_path.exists() else "LICENSE not found"
    
        return Main(
            id="main", 
            style=f"{CARD}; max-width: 80ch; margin: 0 auto;", 
            **{"data-style:grid-area": "` ${1+$_header} / ${1+$_nav} / ${3+!$_footer} / 3` "}
        )(
            H2("LICENSE"),
            Pre(Code(license_content))
        )

    return render_license_main, render_readme_main


@app.function
def render_head(title: str) -> FT:
    """Render HTML head with common resources"""
    return Head(
        Meta(charset='UTF-8'),
        Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
        Title(title),
        Style("* { interpolate-size: allow-keywords; }"),
        Link(id="theme-css", rel='stylesheet', href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css'),
        Link(rel='stylesheet', href='styles.css'),
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css'),
        Script(src='https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js'),
        Script(src='https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js'),
        Script(src='https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/toolbar/prism-toolbar.min.js'),
        Script(src='https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js'),
        Script(type='module', src='https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js')
    )


@app.cell
def _(
    get_project_root,
    pkg_name,
    render_header,
    render_license_main,
    render_nav,
    render_page,
    render_readme_main,
):
    def write_docs_pages():
        """Write documentation pages for all modules plus index and license"""
        root = get_project_root(__file__)
        docs_dir = root / 'docs'
        docs_dir.mkdir(parents=True, exist_ok=True)
    
        meta, mods = scan()
    
        # Write module pages
        for module_name, nodes in mods:
            page = render_page(module_name, nodes)
            html_doc = Html(
                render_head(f'{module_name} - {pkg_name} Documentation'),
                Body(cls="picoscale", style='margin: 0; font-family: system-ui, -apple-system, sans-serif;')(page)
            )
            out_path = docs_dir / f'{module_name}.html'
            out_path.write_text(str(to_xml(html_doc)))
            print(f"Wrote {out_path}")
    
        # Write index.html (README)
        readme_section = Section(
            style="""background: #3D3C3A; margin: 0; padding:0; display:grid; 
            grid-template: auto 1fr auto / auto 1fr auto; gap: 0.5rem; 
            padding-inline: 1rem; padding-block: 0.25rem; height: 100svh;""",
            **{"data-signals":"{_header: true, _nav: true, _footer: false, _aside: false}"}
        )(render_header(), render_nav(), render_readme_main())
    
        html_doc = Html(
            render_head(f'{pkg_name} Documentation'),
            Body(cls="picoscale", style='margin: 0; font-family: system-ui, -apple-system, sans-serif;')(readme_section)
        )
        out_path = docs_dir / 'index.html'
        out_path.write_text(str(to_xml(html_doc)))
        print(f"Wrote {out_path}")
    
        # Write LICENSE.html
        license_section = Section(
            style="""background: #3D3C3A; margin: 0; padding:0; display:grid; 
            grid-template: auto 1fr auto / auto 1fr auto; gap: 0.5rem; 
            padding-inline: 1rem; padding-block: 0.25rem; height: 100svh;""",
            **{"data-signals":"{_header: true, _nav: true, _footer: false, _aside: false}"}
        )(render_header(), render_nav(), render_license_main())
    
        html_doc = Html(
            render_head(f'LICENSE - {pkg_name}'),
            Body(cls="picoscale", style='margin: 0; font-family: system-ui, -apple-system, sans-serif;')(license_section)
        )
        out_path = docs_dir / 'LICENSE.html'
        out_path.write_text(str(to_xml(html_doc)))
        print(f"Wrote {out_path}")

    return (write_docs_pages,)


@app.cell
def _():
    def get_project_root(__file__):
        """Find project root by looking for marker files (.git, pyproject.toml, etc)"""
        from pathlib import Path

        current = Path(__file__).resolve().parent
        markers = {'.git', 'pyproject.toml', 'setup.py', 'requirements.txt'}

        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent

        return Path(__file__).resolve().parent

    get_project_root(__file__)
    return (get_project_root,)


@app.cell
def _():
    def hflip():
        sig = f"_{uuid.uuid4().hex[:8]}"
        return {
            "data-on:mouseenter__throttle.300ms": f"${sig} = !${sig}",
            "data-style:transform": f"${sig} ? 'scaleX(-1)' : ''",
            "data-style:transition": "'transform 0.3s ease'",
            "data-style:color": f"${sig} ? 'dodgerblue' : ''"
        }

    def vflip_signal(trigger_sig):
        return {
            "data-on:click": f"${trigger_sig} = !${trigger_sig}",
            "data-style:display": "'inline-block'",
            "data-style:transform": f"${trigger_sig} ? 'scaleY(-1)' : ''",
            "data-style:transition": "'transform 0.3s ease'"
        }
    return


@app.cell
def _(get_project_root):
    def extract_write_css(out_filename='styles.css'):
        """Extract CSS from current notebook and write to public/styles.css and docs/styles.css"""
        import re
        from pathlib import Path

        # Get project root and config
        root = get_project_root(__file__)
        config = read_config(root)

        # Read current notebook file
        notebook_content = Path(__file__).read_text()

        # Find all mo.md() blocks with CSS
        md_pattern = r'mo\.md\(r"""(.*?)"""\)'
        css_pattern = r'```css\n(.*?)```'

        css_blocks = []
        for md_match in re.finditer(md_pattern, notebook_content, re.DOTALL):
            md_content = md_match.group(1)
            css_matches = re.findall(css_pattern, md_content, re.DOTALL)
            css_blocks.extend(css_matches)

        if not css_blocks:
            print("No CSS blocks found")
            return None

        css_content = '\n\n'.join(css_blocks)

        # Write to public folder in notebooks directory
        nbs_dir = root / config.nbs
        public_path = nbs_dir / 'public' / out_filename
        public_path.parent.mkdir(parents=True, exist_ok=True)
        public_path.write_text(css_content)
        print(f"Wrote {len(css_blocks)} CSS block(s) to {public_path}")

        # Write to docs folder
        docs_dir = root / config.docs
        docs_path = docs_dir / out_filename
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        docs_path.write_text(css_content)
        print(f"Wrote {len(css_blocks)} CSS block(s) to {docs_path}")

        return public_path
    return (extract_write_css,)


@app.cell
def _(extract_write_css, write_docs_pages):
    extract_write_css()
    write_docs_pages()

    return


@app.cell
def _(mo):
    mo.md(r"""
    ## YouTube transcript api
    > Need a youtube transcript?
    """)
    return


@app.cell
def _():
    from youtube_transcript_api import YouTubeTranscriptApi

    ytt = YouTubeTranscriptApi()
    transcript = ytt.fetch('WhS4xRSIjws')
    text = ' '.join(t.text for t in transcript)
    print(text)
    return


@app.cell
def _(mods, write_docs_pages):

    module_name, nodes = mods[0]
    #page = render_page(module_name, nodes)

    write_docs_pages()

    return


@app.cell
def _(CARD, PILL):
    def render_function(node: Node) -> FT:
        """Render a function Node as collapsible card"""
    
        return Article(
            id=f"fn-{node.name}", 
            style=f"{CARD}; transition: height 0.3s ease;",  # Added transition
            **{"data-signals": f"{{show_{node.name}: false}}"}
        )(
            # Header with badges and toggle button
            Div(cls="--make-flank:end")(
                Div(cls="--make-cluster")(
                    H3(node.name),
                    Span(node.kind.value, style=PILL),
                    Span(node.module, style=PILL)
                ),
                # Toggle button (right-aligned)
                Button(**{
                    "data-on:click": f"$show_{node.name} = !$show_{node.name}",
                    "data-text": f"$show_{node.name} ? 'Hide' : 'View'"
                })
            ),
        
            # Docstring summary
            P(node.doc) if node.doc else None,
        
            # Collapsible code block
            Div(**{"data-show": f"$show_{node.name}"})(
                Pre(Code(node.src, cls="language-python"))
            ),
        
            # Toggle button (bottom)
            Button(**{
                "data-on:click": f"$show_{node.name} = !$show_{node.name}",
                "data-text": f"$show_{node.name} ? 'Hide source' : 'View source'"
            })
        )

    return (render_function,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
