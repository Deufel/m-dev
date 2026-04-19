import marimo

__generated_with = "0.23.1"
app = marimo.App()

with app.setup:
    """HTML documentation renderer for marimo-dev projects.

    Renders a Project into a single-page HTML doc with Datastar-driven tab
    switching. The parse step has already extracted everything needed — this
    module is pure transformation from typed data to tag tree.

    Layout: app-style grid
      header → project name + version + description
      nav    → module tabs (drive the $current signal)
      main   → the active module's exports (signature + docstring + source)
      aside  → on-this-page anchors for the active module
    """
    import json
    import html_tags as h
    from  a_types import Project, Module, Export, Param, Return, ExportKind


@app.cell
def _():

    import marimo as mo

    return


@app.function
# ── Signature rendering ──────────────────────────────────────────────────────

def internal_fmt_param(
    p, # a Param dataclass instance
):     # a single line like "    name: str = default, # doc" (leading 4-space indent)
    "Format one parameter line in the docments style."
    line = f"    {p.name}"
    if p.anno:    line += f": {p.anno}"
    if p.default: line += f" = {p.default}"
    line += ","
    if p.doc:     line += f" # {p.doc}"
    return line


@app.function
def internal_fmt_return(
    ret, # a Return dataclass instance or None
):       # a string like ") -> Type: # doc" or just "):"
    "Format the closing line of a signature including return type and doc."
    if ret is None: return "):"
    line = f") -> {ret.anno}:"
    if ret.doc: line += f" # {ret.doc}"
    return line


@app.function
def signature_text(
    exp, # Export dataclass
):       # full signature as plain text (ready for a <pre><code>)
    "Build a docments-style signature reconstruction from an Export."
    kw = 'async def' if exp.kind == ExportKind.ASYNC else \
         'class'      if exp.kind == ExportKind.CLASS else 'def'
    lines = [f"{kw} {exp.final_name}("]
    for p in exp.params:
        lines.append(internal_fmt_param(p))
    lines.append(internal_fmt_return(exp.ret))
    if exp.doc:
        # Render docstring inside the signature block so it highlights as Python
        lines.append(f'    """{exp.doc}"""')
    return '\n'.join(lines)


@app.function
def method_signature_text(
    m, # Method dataclass
):     # signature reconstruction, indented as a class method
    "Build a docments-style signature for a method (used inside classes)."
    lines = [f"def {m.name}("]
    for p in m.params:
        lines.append(internal_fmt_param(p))
    lines.append(internal_fmt_return(m.ret))
    if m.doc:
        lines.append(f'    """{m.doc}"""')
    return '\n'.join(lines)


@app.function
# ── Export rendering ─────────────────────────────────────────────────────────

def internal_export_id(
    mod,  # Module
    exp,  # Export
):        # anchor id like "utils_rename"
    "Compute the DOM id for an export (module-scoped so names can collide)."
    return f"{mod.name}_{exp.final_name}"


@app.function
def render_export(
    mod,  # parent Module (for anchor id)
    exp,  # Export to render
):        # a <section> tag for this export
    "Render one export: heading, signature block, methods (if class), full source disclosure."
    parts = [
        h.h3(id=_export_id(mod, exp))(exp.final_name),
    ]

    # If the final name differs from the original, show that
    if exp.final_name != exp.name:
        parts.append(h.small({"style": "--contrast: 0.6"})(
            "originally ", h.code(exp.name),
        ))

    # Signature + docstring as one highlighted code block
    parts.append(h.pre()(h.code({"class": "python"})(signature_text(exp))))

    # For classes: render each method as a nested signature block
    if exp.methods:
        parts.append(h.h4({"style": "--contrast: 0.7"})("Methods"))
        for m in exp.methods:
            if m.name.startswith('_') and m.name != '__init__':
                continue  # skip private methods except __init__
            parts.append(h.pre()(h.code({"class": "python"})(method_signature_text(m))))

    # Full source, collapsed by default
    parts.append(h.details(
        h.summary({"style": "--contrast: 0.7; cursor: pointer"})("Source"),
        h.pre()(h.code({"class": "python"})(exp.clean_src)),
    ))

    return h.section({"class": "surface stack"})(*parts)


@app.function
# ── Module-setup block (imports / consts / setup) ────────────────────────────


def render_module_setup(
    mod, # Module containing imports/consts/setup lists
):       # a <details> tag if there's setup content, else None
    "Render the module's imports / consts / setup inside a collapsed <details>."
    has_any = mod.imports or mod.consts or mod.setup
    if not has_any: return None

    blocks = []
    if mod.imports:
        src = '\n'.join(i.src for i in mod.imports)
        blocks.append(h.div(
            h.small({"style": "--contrast: 0.6"})("IMPORTS"),
            h.pre()(h.code({"class": "python"})(src)),
        ))
    if mod.consts:
        src = '\n'.join(c.src for c in mod.consts)
        blocks.append(h.div(
            h.small({"style": "--contrast: 0.6"})("CONSTANTS"),
            h.pre()(h.code({"class": "python"})(src)),
        ))
    if mod.setup:
        src = '\n'.join(s.src for s in mod.setup)
        blocks.append(h.div(
            h.small({"style": "--contrast: 0.6"})("SETUP"),
            h.pre()(h.code({"class": "python"})(src)),
        ))

    return h.details({"class": "surface stack"},
        h.summary({"style": "--contrast: 0.7; cursor: pointer"})("Module setup"),
        *blocks,
    )


@app.function
# ── Module rendering (one tab panel per module) ──────────────────────────────

def render_module_panel(
    mod, # Module to render
):       # a <div> panel that shows/hides based on $current
    "Render one module's content as a panel (hidden unless $current matches)."
    children = [
        h.h2({"id": mod.name})(mod.name),
    ]

    setup_block = render_module_setup(mod)
    if setup_block is not None:
        children.append(setup_block)

    for exp in mod.public_exports:
        children.append(render_export(mod, exp))

    return h.div(
        {"data-show": f"$current === '{mod.name}'",
         "class": "stack"},
        *children,
    )


@app.function
# ── Navigation & sidebar ─────────────────────────────────────────────────────

def render_tabs(
    proj, # Project
):        # nav element with a button per module
    "Render the tab strip — each button flips $current to that module name."
    modules = proj.nonempty_modules
    buttons = [
        h.button(
            {"class": "btn",
             "data-on:click": f"$current = '{m.name}'",
             "data-class": f"{{active: $current === '{m.name}'}}"},
            m.name,
        )
        for m in modules
    ]
    return h.div({"class": "stack"})(*buttons)


@app.function
def render_sidebar(
    proj, # Project
):        # aside content — per-module on-this-page lists (only active one visible)
    "Render the 'on this page' sidebar, scoped to the active module."
    lists = []
    for mod in proj.nonempty_modules:
        if not mod.public_exports: continue
        items = [
            h.li(h.a({
                "href": f"#{_export_id(mod, exp)}",
                "data-on:click": f"$current = '{mod.name}'",
            })(exp.final_name))
            for exp in mod.public_exports
        ]
        lists.append(h.div(
            {"data-show": f"$current === '{mod.name}'"},
            h.small({"style": "--contrast: 0.6"})("ON THIS PAGE"),
            h.ul({"role": "list", "class": "stack", "style": "--space: -1"},
                 *items),
        ))
    return h.div({"class": "stack"})(*lists)


@app.function
# ── Header ───────────────────────────────────────────────────────────────────

def render_header(
    proj, # Project
):        # header content with name, version, description, optional repo link
    "Render the top-of-page project header."
    meta = proj.meta
    title_bits = [meta.name or 'Untitled']
    if meta.version:
        title_bits.append(h.small({"style": "--contrast: 0.6"})(f"v{meta.version}"))

    children = [
        h.div({"class": "cluster", "style": "justify-content: flex-start"},
              *title_bits),
    ]
    if meta.desc:
        children.append(h.p(meta.desc))
    if meta.repo_url:
        children.append(h.p(h.a({"href": meta.repo_url})(meta.repo_url)))
    return h.div({"class": "stack"})(*children)


@app.function
# ── Full page ────────────────────────────────────────────────────────────────

def render_page(
    proj, # the complete parsed Project
):        # a Safe string of the complete HTML document
    "Assemble the full HTML page for a Project."
    modules = proj.nonempty_modules
    if not modules:
        return h.html_doc(h.head(h.title("No modules")), h.body(h.p("Empty project")))

    # Initial signal: show the first module
    init_current = modules[0].name

    # On load: if the URL hash contains a module_export anchor, switch to that module.
    # Expression parses '#utils_foo' → 'utils' and sets $current if it's a valid module.
    module_names_js = json.dumps([m.name for m in modules])
    on_load = (
        f"const mods = {module_names_js}; "
        "const hash = location.hash.slice(1); "
        "if (!hash) return; "
        # If hash is a plain module name, use it. Otherwise strip to first '_' segment.
        "const exact = mods.includes(hash) ? hash : null; "
        "const prefix = hash.includes('_') ? hash.split('_')[0] : null; "
        "const match = exact || (mods.includes(prefix) ? prefix : null); "
        "if (match) $current = match;"
    )

    body_content = h.body(
        {"class": "app",
         "data-signals": json.dumps({"current": init_current}),
         "data-init": on_load},
        h.header({"id": "header", "style": "padding: var(--s)"})(
            render_header(proj),
        ),
        h.nav({"id": "nav", "style": "padding: var(--s)"})(
            render_tabs(proj),
        ),
        h.main({"id": "main", "class": "surface", "style": "padding: var(--s)"},
            *[render_module_panel(m) for m in modules],
        ),
        h.aside({"id": "aside", "style": "padding: var(--s)"})(
            render_sidebar(proj),
        ),
    )

    head_content = h.head(
        h.meta(charset="utf-8"),
        h.meta(name="viewport", content="width=device-width, initial-scale=1"),
        h.title(f"{proj.meta.name} docs" if proj.meta.name else "Documentation"),
        h.Favicon("📚"),
        h.Color_type_css(),
        h.Pointer(),
        h.Highlight(),
        h.Datastar(),
    )

    return h.html_doc(head_content, body_content)


@app.function
def build_docs_html(
    proj,       # complete parsed Project
    path=None,  # output path, defaults to {root}/{docs}/index.html
):              # status message
    "Write index.html alongside the existing llms.* files."
    from pathlib import Path
    docs = Path(proj.config.root) / proj.config.docs
    docs.mkdir(parents=True, exist_ok=True)
    out = Path(path) if path else docs / 'index.html'
    out.write_text(str(render_page(proj)))
    return f"Wrote HTML docs to {out}"


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
