from .core import Kind, Param, Node, Config, read_config
from .read import scan, read_meta
from .pkg import write_mod, write_init
from .docs import write_llms
from pathlib import Path
import ast, shutil, re

def build(
    root='.',  # root directory containing pyproject.toml
)->str:        # path to built package
    "Build a Python package from notebooks."
    cfg = read_config(root)
    meta, mods = scan(root)
    mod_names = [name for name, _ in mods]
    pkg = Path(root) / cfg.out / meta['name'].replace('-', '_')
    if pkg.exists(): shutil.rmtree(pkg)
    pkg.mkdir(parents=True, exist_ok=True)
    for name, nodes in mods:
        stripped = re.sub(r'^[a-z]_', '', name)
        if stripped != 'index' and any(n.kind == Kind.EXP for n in nodes): write_mod(pkg/f'{stripped}.py', nodes, mod_names)
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
    for d in ['dist', 'docs', 'src', 'temp']: shutil.rmtree(d, ignore_errors=True)
    print("Nuked build artifacts")
