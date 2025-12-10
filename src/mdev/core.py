import re, ast, tomllib
from pathlib import Path
from typing import TypedDict
from dataclasses import dataclass, asdict
from enum import Enum

class NodeKind(Enum):
    """All the types of things we extract from notebooks"""
    IMP = 'import'
    CONST = 'constant'
    EXP = 'export'

class Param:
    name: str
    anno: str | None = None  # Type annotation
    default: any = None      # Default value
    doc: str = ''

class CodeNode:
    kind: NodeKind
    name: str
    src: str
    params: list[Param] | None = None
    ret_anno: str | None = None
    ret_doc: str = ''
    docstring: str = ''

class Extracted:
    """Everything extracted from one notebook"""
    imports:list[str]
    exports:list[str]
    exp_names:list[str]
    consts:list[str]

class ScanResult(TypedDict):
    meta:dict; mods:list[dict]; idx_path:str|None

def read_metadata(project_root: str='.') -> dict:
    """
    Read package metadata from pyproject.toml.
    This is the ONLY source of truth for package metadata. 
    This should always be in the root folder.

    Args:
        project_root (str): location of pyproject.toml

    Returns:
        dict: [package_name, version, description, license]

    """
    toml_path = Path(project_root)/'pyproject.toml'
    if not toml_path.exists():
        raise ValueError(f"pyproject.toml not found at {toml_path}")

    with open(toml_path,'rb') as f:
        data = tomllib.load(f)

    # Extract project metadata
    proj = data.get('project',{})

    meta = {
        '__package_name__': proj.get('name',''),
        '__version__': proj.get('version','0.0.0'),
        '__description__': proj.get('description',''),
        '__license__': proj.get('license',{}).get('text','') if isinstance(proj.get('license'),dict) else proj.get('license',''),
    }

    # Handle authors (can be list of dicts or simple string)
    authors = proj.get('authors',[])
    if authors and isinstance(authors,list) and len(authors) > 0:
        author = authors[0]
        if isinstance(author,dict):
            name = author.get('name','')
            email = author.get('email','')
            meta['__author__'] = f"{name} <{email}>" if email else name
        else:
            meta['__author__'] = str(author)
    else:
        meta['__author__'] = ''

    return meta

def check_meta(meta: dict):
    """
    Validate that required metadata fields are present

    Args:
        meta (dict): from read_metadata() [package_name, version, description, license]

    """
    req = ['__package_name__','__version__','__description__']
    if miss := [k for k in req if not meta.get(k)]:
        raise ValueError(f"Missing required fields in pyproject.toml: {', '.join(miss)}")

def __is_export(dec):
    """
    Check marimo export decorators

    Args:
        dec: 

    """
    n = ast.unparse(dec.func if isinstance(dec,ast.Call) else dec)
    return n in {'app.function','app.class_definition'}

def classify_node(n, src) -> list[CodeNode]:
    """
    Classify AST nodes into imports, constants, and exports.

    Args:
        n: 
        src: 

    Returns:
        list[CodeNode]: import | constant | export

    """
    results = []

    if isinstance(n,ast.With):
        for s in n.body:
            # Imports
            if isinstance(s,(ast.Import,ast.ImportFrom)):
                results.append(CodeNode(NodeKind.IMP,'',ast.unparse(s)))

            # Constants (private variables starting with __)
            elif isinstance(s,ast.Assign):
                for tgt in s.targets:
                    if isinstance(tgt,ast.Name):
                        name = tgt.id
                        # Only private constants, not metadata
                        if name.startswith('__') and not name.endswith('__'):
                            results.append(CodeNode(NodeKind.CONST,name,ast.unparse(s)))

    # Exports (functions/classes with decorators)
    elif isinstance(n,(ast.FunctionDef,ast.ClassDef)):
        if any(__is_export(d) for d in n.decorator_list):
            if not n.name.startswith('test_'):
                src_seg = ast.get_source_segment(src,n)
                if src_seg:
                    results.append(CodeNode(NodeKind.EXP,n.name,src_seg))

    return results

def group_nodes(nodes: list[CodeNode]) -> dict[NodeKind,list[CodeNode]]:
    """
    Group nodes by their kind

    Args:
        nodes (list[CodeNode]): 

    Returns:
        dict[NodeKind, list[CodeNode]]: 

    """
    groups = {k:[] for k in NodeKind}
    for n in nodes:
        groups[n.kind].append(n)
    return groups

def __clean(src: str) -> str:
    """
    Remove marimo decorator lines

    Args:
        src (str): 

    Returns:
        str: 

    """
    return '\n'.join(l for l in src.splitlines() 
                     if not l.strip().startswith(('@app.function','@app.class_definition')))

def __param_docs(src: str) -> dict:
    """
    Extract ALL parameters and their docs (empty string if no comment)

    Args:
        src (str): 

    Returns:
        dict: 

    """
    tree = ast.parse(src); n = tree.body[0]
    if not isinstance(n,ast.FunctionDef): return {}
    res,lines = {},src.splitlines()

    # STEP 1: Get ALL parameters from AST (with empty docs)
    for arg in n.args.args:
        anno = ast.unparse(arg.annotation) if arg.annotation else None
        res[arg.arg] = {'anno':anno,'doc':''}

    # STEP 2: Fill in comments where they exist
    sig_start,sig_end = n.lineno-1, n.body[0].lineno-1 if n.body else len(lines)
    for l in lines[sig_start:sig_end]:
        if ')->' in l: continue
        if m := re.search(r'(\w+)[:=].*#\s*(.+)',l):
            name,doc = m.groups()
            if name in res: res[name]['doc'] = doc.strip()

    # STEP 3: Always include return if it exists
    if n.returns:
        anno = ast.unparse(n.returns) if not isinstance(n.returns,ast.Constant) else None
        res['return'] = {'anno':anno,'doc':''}
        if n.returns.lineno:
            ret_line = lines[n.returns.lineno-1]
            if m := re.search(r'->[^#]*#\s*(.+)',ret_line):
                res['return']['doc'] = m.group(1).strip()
    return res

def __to_google(src: str) -> str:
    """
    Convert nbdev inline comments to Google docstring format

    Args:
        src (str): 

    Returns:
        str: 

    """
    docs = __param_docs(src)
    if not docs: return src

    try:
        tree = ast.parse(src)
        n = tree.body[0]
    except Exception:  # ← Still catches all errors, but not system exits
        return src
    
    summary = (ast.get_docstring(n) or "").strip()
    lines = ['"""']
    if summary: lines.extend([summary,''])
    if args := [(name,d) for name,d in docs.items() if name!='return']: 
        lines.append('Args:')
        for name,d in args:
            typ = f" ({d['anno']})" if d.get('anno') else ''
            lines.append(f"    {name}{typ}: {d['doc']}")
        lines.append('')
    if docs.get('return'):
        lines.append('Returns:')
        r = docs['return']
        typ = f"{r['anno']}: " if r.get('anno') else ''
        lines.append(f"    {typ}{r['doc']}")
        lines.append('')
    lines.append('"""')

    src_lines = src.splitlines()
    sig_start = n.lineno - 1
    sig_end = n.body[0].lineno - 1 if n.body and hasattr(n.body[0],'lineno') else len(src_lines)

    sig_lines = []
    for l in src_lines[sig_start:sig_end]:
        if cleaned := re.sub(r'\s*#.*$','',l).rstrip(): 
            sig_lines.append(cleaned)

    sig = ' '.join(sig_lines).strip()
    sig = re.sub(r'\s*:\s*',': ',sig)
    sig = re.sub(r'\s*=\s*','=',sig)
    sig = re.sub(r'\s*->\s*',' -> ',sig)
    sig = re.sub(r'\s+',' ',sig)
    sig = re.sub(r'\(\s+','(',sig)
    sig = re.sub(r'\s+\)',')',sig)
    sig = sig.rstrip(': ')

    body_start = n.body[0].lineno - 1 if n.body and hasattr(n.body[0],'lineno') else len(src_lines)
    body_lines = src_lines[body_start:]
    if n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant):
        skip = n.body[0].end_lineno - n.body[0].lineno + 1
        body_lines = body_lines[skip:]
    body = '\n'.join(body_lines)

    docstring = '\n'.join(lines)
    indented = '\n'.join('    '+l if l else '' for l in docstring.splitlines())
    return f"{sig}:\n{indented}\n{body}"

def transform_src(src: str, doc_style: str) -> str:
    """
    Apply doc_style transformation to cleaned source

    Args:
        src (str): 
        doc_style (str): 

    Returns:
        str: 

    """
    cleaned = __clean(src)
    if   doc_style=='google':     return __to_google(cleaned)
    elif doc_style=='unmodified': return cleaned
    else:                         return cleaned

def __extract(p: Path|str, doc_style: str) -> Extracted:
    """
    Extract imports, constants, and exports from one notebook

    Args:
        p (Path | str): 
        doc_style (str): 

    Returns:
        Extracted: 

    """
    src = Path(p).read_text()
    tree = ast.parse(src)

    # Classify all nodes
    all_nodes = []
    for n in tree.body:
        all_nodes.extend(classify_node(n,src))

    # Group by kind
    groups = group_nodes(all_nodes)

    # Extract (no more meta!)
    return Extracted(
        imports = [n.src for n in groups[NodeKind.IMP]],
        exports = [transform_src(n.src,doc_style) for n in groups[NodeKind.EXP]],
        exp_names = [n.name for n in groups[NodeKind.EXP]],
        consts = [n.src for n in groups[NodeKind.CONST]]
    )

def nb_name(f: Path) -> str|None:
    """
    Extract notebook name, None if should skip

    Args:
        f (Path): 

    Returns:
        str | None: 

    """
    if f.name.startswith('.'): return None
    name = re.sub(r'^\d+_','',f.stem)
    return None if name.startswith('test') else name

def scan(nbs: str='notebooks', doc_style: str='google', project_root: str='.') -> ScanResult:
    """
    Scan notebooks and read metadata from pyproject.toml.
    No more metadata cells in notebooks!

    Args:
        nbs (str): 
        doc_style (str): 
        project_root (str): 

    Returns:
        ScanResult: 

    """
    # Read metadata from pyproject.toml (single source of truth!)
    meta = read_metadata(project_root)
    check_meta(meta)

    # Scan notebooks
    p = Path(nbs)
    files = [(f,nb_name(f)) for f in sorted(p.glob('*.py'))]
    files = [(f,name) for f,name in files if name]

    # Extract from all files
    extracts = [(name,__extract(f,doc_style)) for f,name in files]

    # Build module list
    mods = [{'name':name,**asdict(ex)} for name,ex in extracts]

    # No more idx_path - we don't need to find metadata in notebooks
    return {'meta':meta,'mods':mods,'idx_path':None}

def write_file(p: str, parts: list[str]):
    """
    General file writer

    Args:
        p (str): 
        parts (list[str]): 

    """
    Path(p).write_text('\n\n'.join(filter(None,parts))+'\n')

def write_mod(name: str, imps: list[str], consts: list[str], exps: list[str], p: str):
    """
    Write single module file

    Args:
        name (str): 
        imps (list[str]): 
        consts (list[str]): 
        exps (list[str]): 
        p (str): 

    """
    parts = [
        '\n'.join(imps) if imps else None,
        '\n'.join(consts) if consts else None,
        *exps
    ]
    write_file(p,parts)

def write_init(pkg: str, meta: dict, mods: list[dict], p: str):
    """
    Generate __init__.py with package metadata from pyproject.toml

    Args:
        pkg (str): 
        meta (dict): 
        mods (list[dict]): 
        p (str): 

    """
    exports = []
    parts = [f'"""{meta.get("__description__","")}"""']
    parts.append(f"__version__ = '{meta['__version__']}'")
    if a := meta.get('__author__'): 
        parts.append(f"__author__ = '{a.split('<')[0].strip()}'")

    imports = []
    for m in mods:
        if m['name'].startswith('00_') or not m['exp_names']: continue
        if public := [n for n in m['exp_names'] if not n.startswith('__')]:
            names = ', '.join(public)
            imports.append(f"from .{m['name']} import {names}")
            exports.extend(public)

    if imports: parts.append('\n'.join(imports))
    if exports:
        all_lines = ['__all__ = ['] + [f'    "{n}",' for n in sorted(exports)] + [']']
        parts.append('\n'.join(all_lines))

    write_file(p,parts)

def extract_readme(meta: dict, nbs: str) -> str:
    """
    Generate README.md from any notebook with mo.md() cells

    Args:
        meta (dict): 
        nbs (str): 

    Returns:
        str: 

    """
    # Look for any notebook with README content
    for f in sorted(Path(nbs).glob('*.py')):
        src = f.read_text()
        if parts := re.findall(r'mo\.md\((?:[rf]|rf)?"""([\s\S]*?)"""',src):
            txt = '\n\n'.join(parts)
            for k,v in meta.items(): txt = txt.replace(f'{{{k}}}',str(v))
            Path('README.md').write_text(txt)
            return 'README.md'
    return ''

def build(nbs: str='notebooks', out: str='src', doc_style: str='google', project_root: str='.') -> str:
    """
    Build installable package from marimo notebooks

    Args:
        nbs (str): this param
        out (str): that param
        doc_style (str): 
        project_root (str): 

    Returns:
        str: 

    """
    res = scan(nbs,doc_style,project_root)
    name = res['meta']['__package_name__'].replace('-','_')

    pkg = Path(out)/name
    pkg.mkdir(parents=True,exist_ok=True)

    for m in res['mods']:
        if m['name']=='index' or not m['exp_names']: continue
        write_mod(m['name'],m['imports'],m['consts'],m['exports'],pkg/f"{m['name']}.py")

    write_init(name,res['meta'],res['mods'],pkg/'__init__.py')
    extract_readme(res['meta'],nbs)

    return str(pkg)
