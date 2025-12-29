import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    from marimo_dev.core import Kind, Param, Node
    from pathlib import Path
    import ast


@app.function
def clean(
    src:str, # source code to clean
)->str:      # cleaned source code
    "Remove decorator lines from source code."
    return '\n'.join(l for l in src.splitlines() if not l.strip().startswith(('@app.function', '@app.class_definition')))


@app.function
def write(
    p:str,      # path to write to
    *parts:str, # content parts to join with blank lines
):
    "Write parts to file, filtering None values and joining with blank lines."
    Path(p).write_text('\n\n'.join(filter(None, parts)) + '\n')


@app.function
def write_mod(
    path,           # output file path
    nodes:list,     # list of Node objects to write
):
    "Write module file with imports, constants, and exports."
    g = {k: [n for n in nodes if n.kind == k] for k in Kind}
    parts = ['\n'.join(n.src for n in g[Kind.IMP]), '\n'.join(n.src for n in g[Kind.CONST]), '\n\n'.join(clean(n.src) for n in g[Kind.EXP])]
    write(path, *parts)


@app.function
def write_init(
    path:str|Path, # path to write __init__.py file
    meta:dict,     # metadata dict with desc, version, author
    mods:list,     # list of (name, nodes) tuples
):
    "Generate and write __init__.py file with metadata and exports."
    lines = [f'"""{meta["desc"]}"""', f"__version__ = '{meta['version']}'"]
    if meta['author']: lines.append(f"__author__ = '{meta['author'].split('<')[0].strip()}'")
    exports = []
    for name, nodes in mods:
        if name.startswith('00_'): continue
        pub = [n.name for n in nodes if n.kind == Kind.EXP and not n.name.startswith('__')]
        if pub: lines.append(f"from .{name} import {', '.join(pub)}"); exports.extend(pub)
    if exports: lines.append('__all__ = [\n' + '\n'.join(f'    "{n}",' for n in sorted(exports)) + '\n]')
    write(path, '\n'.join(lines))


@app.cell
def _():
    import marimo as mo
    return


if __name__ == "__main__":
    app.run()
