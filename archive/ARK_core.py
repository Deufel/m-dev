import marimo

__generated_with = "0.18.2"
app = marimo.App(width="full")

with app.setup:
    __version__ = "0.1.0"
    __description__ = "Make functional libraries with notebooks"
    __author__ = "Michael Deufel<MDeufel13@gmail.com>"
    __license__ = "MIT"
    __package_name__ = "mdev"

    import re, ast, tomllib
    from pathlib import Path
    from typing import TypedDict


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## types
    """)
    return


@app.class_definition
class ModuleInfo(TypedDict):
    name: str; imports: list[str]; exports: list[str]; export_names: list[str]; constants: list[str]


@app.class_definition
class ScanResult(TypedDict):
    metadata: dict; modules: list[ModuleInfo]; index_path: str | None


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##  internal utilities
    """)
    return


@app.function
def __is_export(
    dec  # decorator node to check
):
    "True if decorator is marimo `@app.function` or `@app.class_definition`"
    n = ast.unparse(dec.func if isinstance(dec, ast.Call) else dec)
    return n in {'app.function', 'app.class_definition'}


@app.function
def __clean(
    src:str  # source code with decorators
)->str:      # source code without decorators
    "Remove marimo decorator lines from source"
    return '\n'.join(l for l in src.splitlines() if not l.strip().startswith(('@app.function', '@app.class_definition')))


@app.function
def __param_docs(
    src:str  # function source code with inline comments
)->dict:     # dict mapping param names to {anno, doc} dicts
    "Extract parameter and return documentation from nbdev-style inline comments"
    tree = ast.parse(src); node = tree.body[0]
    if not isinstance(node, ast.FunctionDef): return {}

    result,lines = {},src.splitlines()
    sig_start,sig_end = node.lineno - 1, node.body[0].lineno - 1 if node.body else len(lines)

    for line in lines[sig_start:sig_end]:
        if ')->' in line: continue  # Skip return type lines to avoid capturing return as param
        if m := re.search(r'(\w+)[:=].*#\s*(.+)', line):
            name,doc = m.groups()
            anno = next((ast.unparse(arg.annotation) for arg in node.args.args 
                        if arg.arg == name and arg.annotation), None)
            result[name] = {'anno': anno, 'doc': doc.strip()}

    if node.returns and node.returns.lineno:
        ret_line = lines[node.returns.lineno - 1]
        if m := re.search(r'->[^#]*#\s*(.+)', ret_line):
            doc = m.group(1).strip()
            anno = ast.unparse(node.returns) if not isinstance(node.returns, ast.Constant) else None
            result['return'] = {'anno': anno, 'doc': doc}

    return result


@app.function
def __to_google(
    src:str  # nbdev-style function source
)->str:      # Google-style function source
    "Convert nbdev inline comments to Google docstring format"
    docs = __param_docs(src)
    if not docs: return src

    tree = ast.parse(src); node = tree.body[0]
    summary = (ast.get_docstring(node) or "").strip()

    # Build Google docstring
    lines = ['"""']
    if summary: lines.extend([summary, ''])

    # Args section (exclude 'return')
    if args := [(n,d) for n,d in docs.items() if n != 'return' and d.get('doc')]:
        lines.append('Args:')
        for n,d in args:
            typ = f" ({d['anno']})" if d.get('anno') else ''
            lines.append(f"    {n}{typ}: {d['doc']}")
        lines.append('')

    # Returns section
    if docs.get('return') and docs['return'].get('doc'):
        lines.append('Returns:')
        r = docs['return']
        typ = f"{r['anno']}: " if r.get('anno') else ''
        lines.append(f"    {typ}{r['doc']}")
        lines.append('')

    lines.append('"""')

    # Clean signature: single line, no comments
    sig_lines = []
    for line in src.splitlines()[node.lineno-1:node.body[0].lineno-1]:
        if cleaned := re.sub(r'\s*#.*$', '', line).rstrip(): sig_lines.append(cleaned)

    sig = ' '.join(sig_lines).strip()
    sig = re.sub(r'\s*:\s*', ': ', sig)        # type hints
    sig = re.sub(r'\s*=\s*', '=', sig)         # defaults
    sig = re.sub(r'\s*->\s*', ' -> ', sig)     # return arrow
    sig = re.sub(r'\s+', ' ', sig)             # collapse spaces
    sig = re.sub(r'\(\s+', '(', sig)           # no space after (
    sig = re.sub(r'\s+\)', ')', sig)           # no space before )
    sig = sig.rstrip(': ')                     # remove trailing colon+space

    # Remove old docstring from body
    body_lines = src.splitlines()[node.body[0].lineno-1:]
    if body_lines and body_lines[0].strip().startswith('"') and body_lines[0].strip().endswith('"'):
        body_lines = body_lines[1:]
    body = '\n'.join(body_lines)

    # Assemble: signature + indented docstring + body
    docstring_block = '\n'.join(lines)
    indented_doc = '\n'.join('    ' + l if l else '' for l in docstring_block.splitlines())
    return f"{sig}:\n{indented_doc}\n{body}"


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## public API
    """)
    return


@app.function
def validate_meta(
    meta:dict  # metadata dictionary from notebook
):
    "Raise ValueError if required metadata keys are missing"
    req = '__version__ __description__ __author__ __license__'.split()
    if miss := [k for k in req if k not in meta]: raise ValueError(f"Missing metadata: {', '.join(miss)}")


@app.function
def scan(
    nb_dir:str = 'notebooks',  # directory containing marimo notebooks
    style:str = 'google'       # output style: 'google' or 'nbdev'
)->ScanResult:                 # metadata, modules list, and index path
    "Scan all notebooks and extract metadata plus exports"
    p,meta,idx_path,mods = Path(nb_dir),None,None,[]
    for f in sorted(p.glob('*.py')):
        if f.name.startswith('.'): continue
        m,imps,exps,names,consts = __extract(f, style)
        if m: meta,idx_path = m,str(f)
        name = re.sub(r'^\d+_', '', f.stem)
        mods.append({'name': name, 'imports': imps, 'exports': exps, 'export_names': names, 'constants': consts})
    if not meta: raise ValueError('No metadata cell found')
    return {'metadata': meta, 'modules': mods, 'index_path': idx_path}


@app.function
def __extract(
    path:Path | str,  # path to notebook file
    style:str         # output style for docstrings
    ):
    """Extract metadata, imports, exports, names, and constants from a single notebook"""
    src,tree = Path(path).read_text(),ast.parse(Path(path).read_text())
    meta,imps,exps,names,consts = {},[],[],[],[]

    for n in tree.body:
        if isinstance(n, ast.With):
            for s in n.body:
                # Extract imports
                if isinstance(s, (ast.Import, ast.ImportFrom)): 
                    imps.append(ast.unparse(s))
                # Extract assignments (both metadata and constants)
                elif isinstance(s, ast.Assign):
                    for tgt in s.targets:
                        if isinstance(tgt, ast.Name):
                            name = tgt.id
                            # Metadata: starts AND ends with __
                            if name.startswith('__') and name.endswith('__'):
                                try:
                                    meta[name] = ast.literal_eval(s.value)
                                except (ValueError, SyntaxError):
                                    # If it can't be literally evaluated, skip it
                                    pass
                            # Private constants: starts with __ but doesn't end with __
                            elif name.startswith('__'):
                                consts.append(ast.unparse(s))

        elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            if any(__is_export(d) for d in n.decorator_list):
                if n.name.startswith('test_'): continue
                raw,clean = ast.get_source_segment(src, n),__clean(ast.get_source_segment(src, n))
                final = __to_google(clean) if style == 'google' else clean
                exps.append(final); names.append(n.name)

    return meta,imps,exps,names,consts


@app.function
def write_mod(
    name:str,         # module name
    imps:list[str],   # import statements
    consts:list[str], # private constants
    exps:list[str],   # exported functions/classes
    path:str          # output file path
):
    "Write a single module file with imports, constants, then exports"
    parts = []
    if imps: parts.append('\n'.join(imps))
    if consts: parts.append('\n'.join(consts))
    parts.extend(exps)
    Path(path).write_text('\n\n'.join(parts) + '\n')


@app.function
def write_init(
    pkg:str,               # package name
    meta:dict,             # metadata dictionary
    mods:list[ModuleInfo], # list of module info dicts
    path:str               # output __init__.py path
):
    "Generate __init__.py with only public names in __all__"
    exports = []
    with Path(path).open('w') as f:
        f.write(f'"""{meta.get("__description__","")}"""\n\n')
        f.write(f"__version__ = '{meta['__version__']}'\n")
        if a := meta.get('__author__'): f.write(f"__author__ = '{a.split('<')[0].strip()}'\n\n")
        for m in mods:
            if m['name'].startswith('00_') or not m['export_names']: continue
            if public := [n for n in m['export_names'] if not n.startswith('__')]:
                names = ', '.join(public)
                f.write(f"from .{m['name']} import {names}\n")
                exports.extend(public)
        if exports:
            f.write('\n__all__ = [\n')
            for n in sorted(exports): f.write(f'    "{n}",\n')
            f.write(']\n')


@app.function
def extract_readme(
    meta:dict,        # metadata for template substitution
    idx:str | None    # path to index notebook or None
)->str:               # path to generated README.md or empty string
    "Generate README.md from mo.md() cells in index notebook"
    if not idx: return ''
    src = Path(idx).read_text()
    if not (parts := re.findall(r'mo\.md\((?:[rf]|rf)?"""([\s\S]*?)"""', src)): return ''
    txt = '\n\n'.join(parts)
    for k,v in meta.items(): txt = txt.replace(f'{{{k}}}', str(v))
    Path('README.md').write_text(txt)
    return 'README.md'


@app.function
def build(
    nb_dir:str = 'notebooks',  # directory containing source notebooks
    out:str = 'src',           # output directory for package
    style:str = 'google'       # docstring style for exports
)->str:                        # path to created package directory
    "Build installable package from marimo notebooks"
    res = scan(nb_dir, style)
    name = (res['metadata'].get('__package_name__') or 
            tomllib.load(open('pyproject.toml', 'rb'))['project']['name']).replace('-', '_')
    pkg = Path(out)/name
    pkg.mkdir(parents=True, exist_ok=True)
    for m in res['modules']:
        if m['name'] == 'index' or not m['export_names']: continue
        write_mod(m['name'], m['imports'], m['constants'], m['exports'], pkg/f"{m['name']}.py")
    write_init(name, res['metadata'], res['modules'], pkg/'__init__.py')
    extract_readme(res['metadata'], res['index_path'])
    return str(pkg)


@app.cell
def _():
    build(nb_dir="./notebooks/", out="src", style="nbdev")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tests
    """)
    return


@app.function(hide_code=True)
def test_doc_conversion():
    input_src = '''@app.function
def greet(
    name:str,      # person's name
    excited:bool=False  # add exclamation?
)->str:            # final greeting
    "Create a friendly greeting"
    s = f"Hello {name}"
    return s + "!!!" if excited else s + "!"
'''
    res = '''def greet(name: str, excited: bool=False) -> str:
    """
    Create a friendly greeting

    Args:
        name (str): person's name
        excited (bool): add exclamation?

    Returns:
        str: final greeting

    """
    s = f"Hello {name}"
    return s + "!!!" if excited else s + "!"'''
    assert res == __to_google(input_src)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
