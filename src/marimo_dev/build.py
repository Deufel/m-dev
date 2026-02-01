from .core import Kind, Param, Node, Config, read_config
from .read import scan, read_meta
from .pkg import write_mod, write_init, clean
from .docs import write_llms
from pathlib import Path
import ast, shutil, re, sys

IMPORT_TO_PYPI = {'bs4': 'beautifulsoup4', 'PIL': 'pillow', 'cv2': 'opencv-python', 'sklearn': 'scikit-learn', 'yaml': 'pyyaml'}

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

def get_pypi_name(import_name):
    "Map import name to PyPI package name."
    root = import_name.split('.')[0]
    return IMPORT_TO_PYPI.get(root, root)

def extract_import_names(nodes):
    "Extract top-level module names from import nodes."
    names = set()
    for n in nodes:
        if n.kind != Kind.IMP: continue
        tree = ast.parse(n.src)
        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    names.add(alias.name.split('.')[0])
            elif isinstance(stmt, ast.ImportFrom) and stmt.module:
                names.add(stmt.module.split('.')[0])
    return names

def pep723_header(deps):
    "Generate PEP 723 inline script metadata."
    deps_str = ', '.join(f'"{d}"' for d in sorted(deps))
    return f'# /// script\n# dependencies = [{deps_str}]\n# ///\n'

def bundle(root='.', name=None):
    "Bundle all notebooks into a single Python file with PEP 723 dependencies."
    cfg = read_config(root)
    meta, mods = scan(root)
    
    # Get notebook filenames to filter out local imports
    nbs_dir = Path(root) / cfg.nbs
    nb_names = {f.stem for f in nbs_dir.glob('*.py')}
    
    # Collect all nodes
    all_nodes = [n for _, nodes in mods for n in nodes]
    
    # Extract dependencies
    import_names = extract_import_names(all_nodes)
    mod_names = [m for m, _ in mods]
    
    # Filter out local modules, notebook names, and stdlib
    external = {get_pypi_name(n) for n in import_names 
                if n not in mod_names 
                and n not in nb_names 
                and n not in sys.stdlib_module_names}
    
    # Build output
    header = pep723_header(external)

    # Filter out local imports, dedupe externals
    seen = set()
    filtered_imports = []
    for n in all_nodes:
        if n.kind != Kind.IMP: continue
        # Skip if it's a local notebook import
        if any(nb in n.src for nb in nb_names): continue
        if n.src not in seen:
            seen.add(n.src)
            filtered_imports.append(n.src)
    
    imports = '\n'.join(filtered_imports)
    
    consts = '\n'.join(n.src for n in all_nodes if n.kind == Kind.CONST)
    exports = '\n\n'.join(clean(n.src) for n in all_nodes if n.kind == Kind.EXP)
    
    content = '\n\n'.join(p for p in [header, imports, consts, exports] if p.strip())
    
    # Determine output path
    if name:
        out_path = Path(root) / name
    else:
        out_path = Path(root) / cfg.out / meta['name'].replace('-', '_') / '__init__.py'
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    return f"Bundled to {out_path}"
