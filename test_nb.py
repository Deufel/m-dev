import marimo

__generated_with = "0.18.1"
app = marimo.App(width="full")

with app.setup:
    __version__ = "0.1.0"
    __description__ = "A tiny test package"
    __author__ = "You <you@example.com>"
    __license__ = "MIT"
    __package_name__ = "mdev_test"


    # import re, ast, tomllib, io
    # from pathlib import Path
    # from tokenize import tokenize, COMMENT
    # from typing import TypedDict


    import re, ast, tomllib
    from pathlib import Path
    from typing import TypedDict


@app.function
def __hi(name:str='Mikkke'):
    return print(f"Hi there {name}")


@app.function
def greet(
    name:str,      # person's name
    excited:bool=False  # add exclamation?
)->str:            # final greeting
    "Create a friendly greeting"
    s = f"Hello {name}"
    return s + "!!!" if excited else s + "!"


@app.function
def add(
    a:int,     # first number
    b:int=0    # second number (optional)
)->int:        # sum of a and b
    "Add two numbers"
    return a + b


@app.class_definition
class Calculator:
    "Simple calculator with memory"
    def __init__(self, start=0):
        self.memory = start

    def accum(self, x:int)->int:
        "Add `x` to memory and return new total"
        self.memory += x
        return self.memory


@app.cell
def _():
    # --- types ---
    class ModuleInfo(TypedDict):
        name: str; imports: list[str]; exports: list[str]; export_names: list[str]

    class ScanResult(TypedDict):
        metadata: dict; modules: list[ModuleInfo]; index_path: str | None

    # --- internal utilities ---
    def __is_export(dec):
        n = ast.unparse(dec.func if isinstance(dec, ast.Call) else dec)
        return n in {'app.function', 'app.class_definition'}

    def __clean(src: str) -> str:
        return '\n'.join(l for l in src.splitlines() if not l.strip().startswith(('@app.function', '@app.class_definition')))

    def __param_docs(src: str) -> dict:
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

    def __to_google(src: str) -> str:
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

    # --- public API ---
    def validate_meta(meta: dict):
        req = '__version__ __description__ __author__ __license__'.split()
        if miss := [k for k in req if k not in meta]: raise ValueError(f"Missing metadata: {', '.join(miss)}")

    def scan(nb_dir: str = 'notebooks', style: str = 'google') -> ScanResult:
        p,meta,idx_path,mods = Path(nb_dir),None,None,[]
        for f in sorted(p.glob('*.py')):
            if f.name.startswith('.'): continue
            m,imps,exps,names = __extract(f, style)
            if m: meta,idx_path = m,str(f)
            name = re.sub(r'^\d+_', '', f.stem)
            mods.append({'name': name, 'imports': imps, 'exports': exps, 'export_names': names})
        if not meta: raise ValueError('No metadata cell found')
        return {'metadata': meta, 'modules': mods, 'index_path': idx_path}

    def __extract(path: Path | str, style: str):
        src,tree = Path(path).read_text(),ast.parse(Path(path).read_text())
        meta,imps,exps,names = {},[],[],[]
        for n in tree.body:
            if isinstance(n, ast.With):
                for s in n.body:
                    if isinstance(s, ast.Assign) and isinstance(s.targets[0], ast.Name):
                        meta[s.targets[0].id] = ast.literal_eval(s.value)
                    if isinstance(s, (ast.Import, ast.ImportFrom)): imps.append(ast.unparse(s))
            elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                if any(__is_export(d) for d in n.decorator_list):
                    if n.name.startswith('test_'): continue
                    raw,clean = ast.get_source_segment(src, n),__clean(ast.get_source_segment(src, n))
                    final = __to_google(clean) if style == 'google' else clean
                    exps.append(final); names.append(n.name)
        return meta,imps,exps,names

    def write_mod(name: str, imps: list[str], exps: list[str], path: str):
        parts = ['\n'.join(imps)] if imps else []
        parts.extend(exps)
        Path(path).write_text('\n\n'.join(parts) + '\n')

    def write_init(pkg: str, meta: dict, mods: list[ModuleInfo], path: str):
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

    def extract_readme(meta: dict, idx: str | None) -> str:
        if not idx: return ''
        src = Path(idx).read_text()
        if not (parts := re.findall(r'mo\.md\((?:[rf]|rf)?"""([\s\S]*?)"""', src)): return ''
        txt = '\n\n'.join(parts)
        for k,v in meta.items(): txt = txt.replace(f'{{{k}}}', str(v))
        Path('README.md').write_text(txt)
        return 'README.md'

    def build(nb_dir: str = 'notebooks', out: str = 'src', style: str = 'google') -> str:
        res = scan(nb_dir, style)
        name = (res['metadata'].get('__package_name__') or 
                tomllib.load(open('pyproject.toml', 'rb'))['project']['name']).replace('-', '_')
        pkg = Path(out)/name
        pkg.mkdir(parents=True, exist_ok=True)
        for m in res['modules']:
            if m['name'] == 'index' or not m['export_names']: continue
            write_mod(m['name'], m['imports'], m['exports'], pkg/f"{m['name']}.py")
        write_init(name, res['metadata'], res['modules'], pkg/'__init__.py')
        extract_readme(res['metadata'], res['index_path'])
        return str(pkg)
    return __to_google, build


@app.cell
def _(build):
    build(nb_dir="./", out="test", style="google")
    return


@app.cell
def _():
    return


@app.cell
def _(__to_google):
    input_src = """@app.function
    def greet(
        name:str,      # person's name
        excited:bool=False  # add exclamation?
    )->str:            # final greeting
        "Create a friendly greeting"
        s = f"Hello {name}"
        return s + "!!!" if excited else s + "!"
    """

    print(__to_google(input_src))
    return


@app.cell
def _(mo):
    mo.md(r"""
    Will this update?
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
