from marimo_dev.core import Kind, Param, Node
from marimo_dev.read import scan
from marimo_dev.pkg import write_mod, write_init
from marimo_dev.docs import write_llms
from pathlib import Path
import ast, shutil

def build(
    nbs='notebooks', # directory containing notebook files
    out='src',       # output directory for built package
    root='.',        # root directory containing pyproject.toml
    rebuild=True,    # remove existing package directory before building
)->str:              # path to built package
    "Build a Python package from notebooks."
    meta, mods = scan(nbs, root)
    pkg = Path(out) / meta['name'].replace('-', '_')
    if rebuild and pkg.exists(): shutil.rmtree(pkg)
    pkg.mkdir(parents=True, exist_ok=True)
    for name, nodes in mods:
        if name != 'index' and any(n.kind == Kind.EXP for n in nodes): write_mod(pkg/f'{name}.py', nodes)
    write_init(pkg/'__init__.py', meta, mods)
    all_exp = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
    if all_exp: write_llms(meta, all_exp)
    return str(pkg)

def tidy():
    "Remove cache and temporary files (__pycache__, __marimo__, .pytest_cache, etc)."
    import shutil
    for p in Path('.').rglob('__pycache__'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('__marimo__'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('.pytest_cache'): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('*.pyc'): p.unlink(missing_ok=True)
    print("Cleaned cache files")

def nuke():
    "Remove all build artifacts (dist, docs, src) and cache files."
    import shutil
    tidy()
    for d in ['dist', 'docs', 'src']: shutil.rmtree(d, ignore_errors=True)
    print("Nuked build artifacts")
