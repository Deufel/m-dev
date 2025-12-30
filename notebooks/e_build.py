import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    from a_core import Kind, Param, Node, Config
    from b_read import scan
    from c_pkg import write_mod, write_init
    from d_docs import write_llms
    from pathlib import Path
    import ast, shutil, re


@app.cell
def _():
    build()
    return


@app.function
def build(
    nbs='notebooks', # directory containing notebook files
    out='src',       # output directory for built package
    root='.',        # root directory containing pyproject.toml
    rebuild=True,    # remove existing package directory before building
)->str:              # path to built package
    "Build a Python package from notebooks."
    meta, mods = scan(nbs, root)
    mod_names = [name for name, _ in mods]
    pkg = Path(out) / meta['name'].replace('-', '_')
    if rebuild and pkg.exists(): shutil.rmtree(pkg)
    pkg.mkdir(parents=True, exist_ok=True)
    for name, nodes in mods:
        stripped = re.sub(r'^[a-z]_', '', name)
        if stripped != 'index' and any(n.kind == Kind.EXP for n in nodes): write_mod(pkg/f'{stripped}.py', nodes, mod_names)
    write_init(pkg/'__init__.py', meta, mods)
    all_exp = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
    if all_exp: write_llms(meta, all_exp)
    return str(pkg)


@app.function
def tidy():
    "Remove cache and temporary files (__pycache__, __marimo__, .pytest_cache, etc)."
    import shutil
    for p in Path('.').rglob('__pycache__'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('__marimo__'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('.pytest_cache'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('*.pyc'): p.unlink(missing_ok=True)
    print("Cleaned cache files")


@app.function
def nuke():
    "Remove all build artifacts (dist, docs, src) and cache files."
    import shutil
    tidy()
    for d in ['dist', 'docs', 'src', 'temp']: shutil.rmtree(d, ignore_errors=True)
    print("Nuked build artifacts")


@app.cell
def _():
    license_text = '''MIT License

    Copyright (c) 2025 [Your Name]

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    '''

    Path('LICENSE').write_text(license_text)

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
