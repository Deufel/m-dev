import re, ast, tomllib, io

from pathlib import Path

from tokenize import tokenize, COMMENT

from typing import TypedDict

class ModuleInfo(TypedDict):
    name:str                # module name without .py
    imports:list[str]       # raw import lines from setup cell
    exports:list[str]       # cleaned source of exported functions/classes
    export_names:list[str]

class ScanResult(TypedDict):
    metadata:dict             # from setup cell
    modules:list[ModuleInfo]  # all modules found
    index_path:str|None

def u_is_export(dec):
"""
"""
    "True if `dec` is marimo `@app.function` or `@app.class_definition`"
    n = ast.unparse(dec.func if isinstance(dec,ast.Call) else dec)
    return n in {'app.function','app.class_definition'}

def u_clean(src:str)->str:
"""
"""
    "Remove `@app.function` / `@app.class_definition` decorator lines"
    return '\n'.join(l for l in src.splitlines()
                     if not l.strip().startswith(('@app.function','@app.class_definition')))

def u_param_docs(src:str)->dict:
"""
"""
    "Extract param → {anno,doc} from inline # comments – only functions"
    tree = ast.parse(src); node = tree.body[0]
    if not isinstance(node, ast.FunctionDef): return {}

    locs = {a.lineno:(a.arg, ast.unparse(a.annotation) if a.annotation else None)
            for a in node.args.args}

    readline = io.BytesIO(src.encode('utf-8')).readline
    comments = {t.start[0]:re.sub(r'^\s*#\s?', '', t.string)
                for t in tokenize(readline) if t.type == COMMENT}

    return {n:{'anno':a, 'doc':comments.get(ln,'')}
            for ln,(n,a) in locs.items()}

def u_google(src:str)->str:
"""
"""
    "Convert inline # comments → Google docstring (functions only)"
    docs = u_param_docs(src)
    if not docs:  # likely a class → return cleaned source only
        return src

    lines = ['"""']
    if main:=(ast.get_docstring(ast.parse(src)) or '').strip():
        lines += [main, '']
    args = [(n,d) for n,d in docs.items() if n!='return' and d.get('doc')]
    if args:
        lines += ['Args:']
        for n,d in args:
            t = f" ({d['anno']})" if d['anno'] else ''
            lines.append(f"    {n}{t}: {d['doc']}")
    if (r:=docs.get('return')) and r.get('doc'):
        lines += ['', 'Returns:', f"    {r.get('anno','')}: {r['doc']}"]
    lines += ['"""']

    sig, body = src.split('\n', 1)
    return f"{sig}\n{'\n'.join(lines)}\n{body}"

def u_2google(src:str)->str:
"""
"""
    "Convert nbdev inline # comments → Google docstring"
    docs = u_param_docs(src)
    if not docs: return src  # class or no inline docs → leave as-is

    lines = ['"""']
    main = (ast.get_docstring(ast.parse(src)) or '').strip()
    if main: lines += [main, '']

    args = [(n,d) for n,d in docs.items() if n!='return' and d.get('doc')]
    if args:
        lines.append('Args:')
        for n,d in args:
            typ = f" ({d['anno']})" if d['anno'] else ''
            lines.append(f"    {n}{typ}: {d['doc']}")

    if (r:=docs.get('return')) and r.get('doc'):
        lines.append('')
        lines.append('Returns:')
        typ = f"{r['anno']}: " if r['anno'] else ''
        lines.append(f"    {typ}{r['doc']}")

    lines.append('"""')
    sig, body = src.split('\n', 1)
    return f"{sig}\n{'\n'.join(lines)}\n{body}"

def validate_meta(
"""
Args:
    meta (dict): project metadata from setup cell
"""
    meta:dict,  # project metadata from setup cell
):
    "Raise `ValueError` if required keys missing"
    req = '__version__ __description__ __author__ __license__'.split()
    if miss:=[k for k in req if k not in meta]:
        raise ValueError(f"Missing metadata: {', '.join(miss)}")

def scan(
"""
Args:
    nb_dir (str): directory with .py notebooks
    style (str): output style: 'google' or 'nbdev'
"""
    nb_dir:str='notebooks',  # directory with .py notebooks
    style:str='google'       # output style: 'google' or 'nbdev'
)->ScanResult:               # Full scan result
    "Scan notebooks → metadata + exports"
    p = Path(nb_dir)
    meta, idx_path, mods = None, None, []

    for f in sorted(p.glob('*.py')):
        if f.name.startswith('.'): continue
        m, imps, exps, names = u_extract(f, style)
        if m: meta, idx_path = m, str(f)
        name = re.sub(r'^\d+_', '', f.stem)
        mods.append({'name':name, 'imports':imps, 'exports':exps, 'export_names':names})

    if not meta: raise ValueError('No metadata cell found')
    return {'metadata':meta, 'modules':mods, 'index_path':idx_path}

def u_extract(
"""
Args:
    path (Path | str): notebook to extract from
    style (str): currently ignored — we always emit nbdev style
"""
    path:Path|str,  # notebook to extract from
    style:str       # currently ignored — we always emit nbdev style
):
    src = Path(path).read_text(); tree = ast.parse(src)
    meta, imps, exps, names = {}, [], [], []

    for n in tree.body:
        if isinstance(n, ast.With):
            for s in n.body:
                if isinstance(s, ast.Assign) and isinstance(s.targets[0], ast.Name):
                    meta[s.targets[0].id] = ast.literal_eval(s.value)
                if isinstance(s, (ast.Import, ast.ImportFrom)):
                    imps.append(ast.unparse(s))

        elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            if any(u_is_export(d) for d in n.decorator_list):
                if n.name.startswith('test_'): continue
                raw = ast.get_source_segment(src, n)
                clean = u_clean(raw)
                final = u_2google(clean) if style == 'google' else clean
                exps.append(final); names.append(n.name)

    return meta, imps, exps, names

def write_mod(
"""
Args:
    name (str): module name (no .py)
    imps (list[str]): import lines
    exps (list[str]): exported source strings
    path (str): full path to write
"""
    name:str,      # module name (no .py)
    imps:list[str],# import lines
    exps:list[str],# exported source strings
    path:str,      # full path to write
):
    "Write a single `.py` module"
    Path(path).write_text('\n\n'.join(imps + exps + ['']))

def write_init(
"""
Args:
    pkg (str): package name (e.g. m_dev)
    meta (dict): project metadata
    mods (list[ModuleInfo]): scanned modules
    path (str): path to __init__.py
"""
    pkg:str,               # package name (e.g. m_dev)
    meta:dict,             # project metadata
    mods:list[ModuleInfo], # scanned modules
    path:str,              # path to __init__.py
):
    "Generate `__init__.py` with relative imports and `__all__`"
    exports = []
    with Path(path).open('w') as f:
        f.write(f'"""{meta.get("__description__","")}"""\n\n')
        f.write(f"__version__ = '{meta['__version__']}'\n")
        if a:=meta.get('__author__'): f.write(f"__author__ = '{a.split('<')[0].strip()}'\n\n")
        for m in mods:
            if m['name'].startswith('00_') or not m['export_names']: continue
            names = ', '.join(m['export_names'])
            f.write(f"from .{m['name']} import {names}\n")
            exports += m['export_names']
        if exports:
            f.write('\n__all__ = [\n')
            for n in exports: f.write(f'    "{n}",\n')
            f.write(']\n')

def extract_readme(
"""
Args:
    meta (dict): metadata for {{var}} substitution
    idx (str | None): path to index notebook
"""
    meta:dict,      # metadata for {{var}} substitution
    idx:str|None,   # path to index notebook
)->str:             # path to written README.md (or empty)
    "Generate `README.md` from `mo.md()` calls in index"
    if not idx: return ''
    src = Path(idx).read_text()
    parts = re.findall(r'mo\.md\((?:[rf]|rf)?"""([\s\S]*?)"""', src)
    if not parts: return ''
    txt = '\n\n'.join(parts)
    for k,v in meta.items(): txt = txt.replace(f'{{{k}}}', str(v))
    Path('README.md').write_text(txt)
    return 'README.md'

def build(
"""
Args:
    style (str): ← now defaults to Google!
"""
    nb_dir:str='notebooks',
    out:str='src',
    style:str='google'  # ← now defaults to Google!
)->str:
    "Build package with Google-style docstrings"
    res = scan(nb_dir, style)
    name = (res['metadata'].get('__package_name__') or
            tomllib.load(open('pyproject.toml','rb'))['project']['name']).replace('-','_')
    pkg = Path(out)/name; pkg.mkdir(parents=True, exist_ok=True)

    for m in res['modules']:
        if m['name']=='index' or not m['export_names']: continue
        write_mod(m['name'], m['imports'], m['exports'], pkg/f"{m['name']}.py")

    write_init(name, res['metadata'], res['modules'], pkg/'__init__.py')
    extract_readme(res['metadata'], res['index_path'])
    return str(pkg)

