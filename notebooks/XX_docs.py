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
    from pathlib import Path


    from mohtml import div, span, code, p, pre, a, html, head, body, script, style, form, input, button, h1, aside, h3

    from mdev_deufel.core import CodeNode, NodeKind


@app.cell
def _():
    import marimo as mo
    import pytest
    return


@app.function
def doc_card(
    node: CodeNode,  # Node with function/class metadata
    idx: int,        # Unique index for signal names
):
    "Generate HTML card for a single function/class with Datastar search integration"
    searchable = f"{node.name} {node.docstring} {' '.join(p.name + ' ' + (p.doc or '') for p in (node.params or []))}"
    match_sig = f"matchCount{idx}"
    
    return div(
        span(cls="match-badge", data_show=f"$tags.length > 0 || $search.trim().length > 0", data_text=f"${match_sig}"),
        div(code(f"data-{node.name}" if node.name.startswith('on') else node.name), cls="attribute-name"),
        div(
            p(node.docstring) if node.docstring else None,
            pre(code(node.src[:200] + '...' if len(node.src) > 200 else node.src)) if node.src else None,
            cls="description"
        ),
        id=node.name,
        cls="attribute",
        data_signals=f"{{searchable{idx}: '{searchable}', {match_sig}: 0}}",
        data_effect=f"${match_sig} = [...$tags, $search.trim()].filter(tag => tag.length > 0 && $searchable{idx}.toLowerCase().includes(tag.toLowerCase())).length",
        data_show=f"($tags.length === 0 && $search.trim().length === 0) || ${match_sig} > 0",
        data_style__order=f"($tags.length === 0 && $search.trim().length === 0) ? 0 : -${match_sig}"
    )


@app.cell
def _():
    doc_card(CodeNode(NodeKind.EXP, 'test_func', 'def test(): pass', docstring='A test function'), 0)

    return


@app.function
def nav_item(
    node: CodeNode,  # Node with function/class metadata
    idx: int,        # Unique index matching doc_card
):
    "Generate sidenav link with match count badge"
    match_sig = f"matchCount{idx}"
    return a(
        span(node.name),
        span(cls="nav-badge", data_show=f"$tags.length > 0 || $search.trim().length > 0", data_text=f"${match_sig}"),
        href=f"#{node.name}",
        cls="nav-item",
        data_class__disabled=f"($tags.length > 0 || $search.trim().length > 0) && ${match_sig} === 0"
    )


@app.cell
def _():
    nav_item(CodeNode(NodeKind.EXP, 'test_func', 'def test(): pass'), 0)

    return


@app.function
def docs_page(
    title: str,            # Page title
    subtitle: str,         # Page subtitle
    nodes: list[CodeNode], # List of functions/classes to document
):
    "Generate complete Datastar-powered documentation page"
    return html(
        head(
            script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"),
            style("*{scrollbar-gutter:stable}body{font-family:sans-serif;max-width:1400px;margin:1rem auto;padding:0 1rem;line-height:1.5}.header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;gap:2rem}.search-section{position:fixed;top:1rem;right:1rem;z-index:100;display:flex;gap:0.5rem;align-items:center;background:white;padding:0.75rem;border-radius:0.5rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1)}.content-wrapper{display:grid;grid-template-columns:250px 1fr;gap:2rem}.sidenav{position:sticky;top:1rem;height:fit-content;max-height:calc(100vh - 2rem);overflow-y:auto;padding:1rem;background:#f9fafb;border-radius:0.375rem;border:1px solid #e5e7eb}.nav-item{display:flex;align-items:center;justify-content:space-between;padding:0.5rem;margin-bottom:0.25rem;border-radius:0.25rem;font-size:0.875rem;color:#374151;text-decoration:none;transition:all 0.15s}.nav-item:hover{background:#e5e7eb}.nav-item.disabled{opacity:0.4;cursor:not-allowed;pointer-events:none}.nav-badge{background:#3b82f6;color:white;padding:0.125rem 0.5rem;border-radius:9999px;font-size:0.7rem;font-weight:600;min-width:1.5rem;text-align:center}.attribute{position:relative;padding:1rem;border:1px solid #e5e7eb;border-radius:0.375rem;background:#fff;scroll-margin-top:3rem;transition:order 0.5s cubic-bezier(0.4,0,0.2,1),transform 0.5s cubic-bezier(0.4,0,0.2,1),opacity 0.3s ease-in-out}.attribute:hover{box-shadow:0 2px 4px rgba(0,0,0,0.1)}.match-badge{position:absolute;top:1rem;right:1rem;background:#3b82f6;color:white;padding:0.25rem 0.75rem;border-radius:9999px;font-size:0.8rem;font-weight:600}.attribute-name{font-weight:bold;font-size:1.25rem;margin-bottom:0.25rem;color:#1e40af}.description{margin:0.5rem 0;color:#374151;font-size:0.9rem}input{padding:0.625rem;border:1px solid #d1d5db;border-radius:0.375rem;min-width:250px;font-size:0.95rem}input:focus{outline:2px solid #3b82f6;outline-offset:0}button{padding:0.625rem 1.25rem;background:#3b82f6;color:white;border:none;border-radius:0.375rem;cursor:pointer;font-size:0.95rem;transition:background 0.15s;white-space:nowrap}button:hover{background:#2563eb}button.clear-btn{background:#dc2626}button.clear-btn:hover{background:#b91c1c}code{background:#f3f4f6;color:#1f2937;padding:0.125rem 0.375rem;border-radius:0.25rem;font-size:0.85rem;font-family:monospace}pre{background:#1f2937;color:#f9fafb;padding:0.75rem;border-radius:0.375rem;overflow-x:auto;font-size:0.8rem;margin:0.375rem 0}pre code{background:transparent;color:#f9fafb;padding:0}")
        ),
        body(
            form(input(type="text", placeholder="Live Search ...(enter to add tag)", data_bind__search=""), button("Add Tag", type="submit"), button("Clear All", cls="clear-btn", type="button", data_on__click="$tags = [], $search = ''"), cls="search-section", data_on__submit____prevent="$search.trim() ? ($tags = [...$tags, $search.trim()], $search = '') : null"),
            div(div(h1(title), p(subtitle, cls="subtitle"), cls="title-section"), cls="header"),
            div(
                aside(h3("Functions"), *[nav_item(n, i) for i, n in enumerate(nodes)], cls="sidenav"),
                div(div(*[doc_card(n, i) for i, n in enumerate(nodes)], cls="attributes"), cls="main-content"),
                cls="content-wrapper"
            ),
            data_signals=dict(search='', tags=[])
        ),
        style="scroll-behavior:smooth"
    )


@app.function
def write_docs(
    title: str,            # Page title
    subtitle: str,         # Page subtitle  
    nodes: list[CodeNode], # List of functions/classes to document
    out: str='docs',       # Output directory
):
    "Write Datastar documentation page to index.html"
    Path(out).mkdir(exist_ok=True)
    html = to_xml(docs_page(title, subtitle, nodes))
    Path(out)/'index.html'.write_text(f'<!doctype html>\n{html}')


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
