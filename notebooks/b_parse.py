import marimo

__generated_with = "0.22.0"
app = marimo.App(width="medium", app_title="")

with app.setup:
    from pathlib import Path
    import ast, re, tomllib

    from a_types import (
        Config, Meta, Project, Module, 
        Import, Const, Setup, Export, ParsedFile,
        Param, Method, Return, ExportKind,
        EXPORT_DECORATORS, rename, 
    )


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # marimo-dev.parser

    >All ast and regex machinery lives here. No other module imports ast.
    >No other module knows about marimo's notebook format.

    Three branches per AST node:
    1. ast.With (setup cell)  → Import, Const, Setup
    2. Decorated export       → Export
    3. Everything else        → skip
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Config & Meta
    """)
    return


@app.function
def read_config(
    root: str = '.', # project root containing pyproject.toml
) -> Config:         # parsed configuration
    "Read config once from pyproject.toml [tool.marimo-dev]."
    try:
        with open(Path(root) / 'pyproject.toml', 'rb') as f:
            cfg = tomllib.load(f).get('tool', {}).get('marimo-dev', {})
        if 'skip_prefixes' in cfg: cfg['skip_prefixes'] = tuple(cfg['skip_prefixes'])
        return Config(**{k: v for k, v in cfg.items() if k in Config.__dataclass_fields__})
    except FileNotFoundError:
        return Config()


@app.function
def internal_read_meta(
    root: str, # project root containing pyproject.toml
) -> Meta:     # parsed project metadata
    "Read project metadata from pyproject.toml [project]."
    with open(Path(root) / 'pyproject.toml', 'rb') as f:
        p = tomllib.load(f).get('project', {})
    a = (p.get('authors') or [{}])[0]
    author = f"{a.get('name','')} <{a.get('email','')}>".strip(' <>') if isinstance(a, dict) else str(a)
    lic = p.get('license', {})
    return Meta(
        name    = p.get('name', ''),
        version = p.get('version', '0.0.0'),
        desc    = p.get('description', ''),
        license = lic.get('text', '') if isinstance(lic, dict) else lic,
        author  = author,
        urls    = p.get('urls', {}),
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inline doc extraction
    (the reason we can't just use ast)
    """)
    return


@app.function
def internal_inline_doc(
    lines: list[str], # source lines
    lineno: int,       # 1-indexed line number
    anchor: str,       # identifier to match before comment
) -> str:              # inline comment text or ''
    "Extract inline comment following an identifier on a source line."
    if 0 < lineno <= len(lines):
        if m := re.search(rf'\b{re.escape(anchor)}\b.*?#\s*(.+)', lines[lineno - 1]):
            return m.group(1).strip()
    return ''


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Parameter & return extraction
    """)
    return


@app.function
def internal_parse_params(
    fn,                # function AST node
    lines: list[str],  # source lines for inline doc extraction
) -> list[Param]:      # parameters with inline docs
    "Extract parameters with inline docs from a function AST node."
    if not hasattr(fn, 'args'): return []
    args, defs = fn.args.args, fn.args.defaults
    pad = [None] * (len(args) - len(defs))
    return [
        Param(
            name    = a.arg,
            anno    = ast.unparse(a.annotation) if a.annotation else '',
            default = ast.unparse(d) if d else '',
            doc     = internal_inline_doc(lines, a.lineno, a.arg),
        )
        for a, d in zip(args, pad + defs)
        if a.arg not in ('self', 'cls')
    ]


@app.function
def internal_parse_return(
    fn,                # function AST node
    lines: list[str],  # source lines for inline doc extraction
) -> Return | None:    # return annotation or None
    "Extract return type and inline doc from a function AST node."
    if not fn.returns or isinstance(fn.returns, ast.Constant): return None
    doc = internal_inline_doc(lines, fn.returns.lineno, '->') if hasattr(fn.returns, 'lineno') else ''
    return Return(anno=ast.unparse(fn.returns), doc=doc)


@app.function
def internal_parse_methods(
    cls_node: ast.ClassDef, # class AST node
    lines: list[str],       # source lines for inline doc extraction
) -> list[Method]:          # methods with params and return info
    "Extract methods from a class definition."
    return [
        Method(
            name   = item.name,
            doc    = ast.get_docstring(item) or '',
            params = internal_parse_params(item, lines),
            ret    = internal_parse_return(item, lines),
        )
        for item in cls_node.body
        if isinstance(item, ast.FunctionDef)
    ]


@app.function
def internal_parse_class_params(
    cls_node: ast.ClassDef, # class AST node
    lines: list[str],       # source lines for inline doc extraction
) -> list[Param]:           # params from __init__ or class attributes
    "Extract params from __init__ method if present, else annotated class attributes."
    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
            return internal_parse_params(item, lines)
    return [
        Param(
            name = t.id,
            anno = ast.unparse(a.annotation) if a.annotation else '',
            doc  = internal_inline_doc(lines, a.lineno, t.id),
        )
        for a in cls_node.body
        if isinstance(a, ast.AnnAssign) and isinstance((t := a.target), ast.Name)
    ]


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source extraction helpers
    """)
    return


@app.function
def internal_src_with_decs(
    node,              # AST node with potential decorators
    lines: list[str],  # source lines
) -> str:              # source including decorator lines
    "Get source including decorators."
    start = node.decorator_list[0].lineno - 1 if node.decorator_list else node.lineno - 1
    return '\n'.join(lines[start:node.end_lineno])


@app.function
def internal_clean_src(
    src: str, # source text with marimo decorators
) -> str:     # source text without marimo decorators
    "Remove marimo export decorators from source."
    strip = tuple(f'@{d}' for d in EXPORT_DECORATORS)
    return '\n'.join(
        l for l in src.splitlines()
        if not l.strip().startswith(strip)
    )


@app.function
def internal_is_export_dec(
    d, # decorator AST node
) -> bool: # True if decorator marks a cell for export
    "Check if decorator is a marimo export marker."
    return ast.unparse(d.func if isinstance(d, ast.Call) else d) in EXPORT_DECORATORS


@app.function
def internal_classify(
    node, # AST node (FunctionDef, AsyncFunctionDef, or ClassDef)
) -> ExportKind: # classification of the export
    "Determine export kind from AST node type."
    if isinstance(node, ast.ClassDef): return ExportKind.CLASS
    if isinstance(node, ast.AsyncFunctionDef): return ExportKind.ASYNC
    return ExportKind.FUNC


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Per-file parsing
    """)
    return


@app.function
def internal_parse_file(
    path: Path,    # path to notebook .py file
    cfg: Config,   # project configuration (for renames)
) -> ParsedFile:   # custom dataclass
    """Parse a single notebook file into its constituent parts.

    Three branches:
        1. ast.With  → imports, consts, setup
        2. Decorated → exports (final_name and public resolved here)
        3. else      → skip
    """
    src = path.read_text()
    tree = ast.parse(src)
    lines = src.splitlines()

    imports, consts, setup, exports = [], [], [], []

    for n in tree.body:

        # ── Branch 1: Setup cells (with app.setup:) ──────────
        if isinstance(n, ast.With):
            for s in n.body:
                if isinstance(s, (ast.Import, ast.ImportFrom)):
                    imports.append(Import(src=ast.unparse(s)))
                elif isinstance(s, ast.Assign):
                    for t in s.targets:
                        if isinstance(t, ast.Name):
                            consts.append(Const(name=t.id, src=ast.unparse(s)))
                else:
                    code = ast.get_source_segment(src, s) or ast.unparse(s)
                    setup.append(Setup(src=code))
            continue

        # ── Branch 2: Decorated exports ──────────────────────
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        dec = next((d for d in n.decorator_list if internal_is_export_dec(d)), None)
        if not dec or n.name.startswith('test_'):
            continue

        kind = internal_classify(n)
        full_src = internal_src_with_decs(n, lines)
        final_name = rename(n.name, cfg.renames)

        if kind == ExportKind.CLASS:
            params  = internal_parse_class_params(n, lines)
            methods = internal_parse_methods(n, lines)
            ret     = None
        else:
            params  = internal_parse_params(n, lines)
            methods = []
            ret     = internal_parse_return(n, lines)

        exports.append(Export(
            name       = n.name,
            final_name = final_name,
            public     = not final_name.startswith('_'),
            kind       = kind,
            src        = full_src,
            clean_src  = internal_clean_src(full_src),
            doc        = ast.get_docstring(n) or '',
            params     = params,
            methods    = methods,
            ret        = ret,
            lineno     = n.lineno,
        ))

        # ── Branch 3: everything else → skip (implicit) ─────

    return ParsedFile(imports, consts, setup, exports)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Module name logic
    """)
    return


@app.function
def internal_module_name(
    f: Path,       # notebook file path
    cfg: Config,   # project configuration
) -> str | None:   # module name or None to skip
    "Extract module name from file path, or None to skip."
    if f.name.startswith('.'):
        return None
    if any(f.stem.startswith(p) for p in cfg.skip_prefixes):
        return None
    name = re.sub(r'^[a-z]_(\w+)', r'\1', f.stem)
    return None if name.startswith('test') else name


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##  Public API
    """)
    return


@app.function
def read_project(
    root: str = '.', # project root containing pyproject.toml and notebooks
) -> Project:        # complete parsed project
    """Read an entire marimo-dev project into a Project.

    Single entry point. Call once, get everything.
    """

    cfg  = read_config(root)
    meta = internal_read_meta(root)
    nbs  = Path(root) / cfg.nbs

    init_extras, modules = ParsedFile([], [], [], []), []
    for f in sorted(nbs.glob('*.py')):
        if f.name == cfg.init:
            init_extras = _parse_file(f, cfg)
            continue
        name = _module_name(f, cfg)
        if name is None: continue
        parsed = _parse_file(f, cfg)
        modules.append(Module(
            name    = name,
            nb_stem = f.stem,
            imports = parsed.imports,
            consts  = parsed.consts,
            setup   = parsed.setup,
            exports = parsed.exports,
        ))

    return Project(meta=meta, config=cfg, init_extras=init_extras, modules=modules)


if __name__ == "__main__":
    app.run()
