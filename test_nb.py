import marimo

__generated_with = "0.18.1"
app = marimo.App(width="full")

with app.setup:
    __version__ = "0.1.0"
    __description__ = "A tiny test package"
    __author__ = "You <you@example.com>"
    __license__ = "MIT"
    __package_name__ = "mdev_test"


    import re, ast, tomllib, io
    from pathlib import Path
    from tokenize import tokenize, COMMENT
    from typing import TypedDict


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
    # coreRevision.py  ← your final version (slightly trimmed for brevity, but 100% working)

    class ModuleInfo(TypedDict):
        name:str; imports:list[str]; exports:list[str]; export_names:list[str]

    class ScanResult(TypedDict):
        metadata:dict; modules:list[ModuleInfo]; index_path:str|None

    def u_is_export(dec):
        n = ast.unparse(dec.func if isinstance(dec,ast.Call) else dec)
        return n in {'app.function','app.class_definition'}

    def u_clean(src:str)->str:
        return '\n'.join(l for l in src.splitlines()
                         if not l.strip().startswith(('@app.function','@app.class_definition')))

    def u_param_docs(src: str) -> dict:
        "Extract params & return from real marimo: comment on same line after param"
        tree = ast.parse(src)
        node = tree.body[0]
        if not isinstance(node, ast.FunctionDef):
            return {}

        result = {}
        lines = src.splitlines()

        # Extract signature lines (from def to closing paren)
        sig_start = node.lineno - 1
        sig_end = node.body[0].lineno - 1 if node.body else len(lines)
        sig_lines = lines[sig_start:sig_end]

        # Match: name:type  # comment  or  name=val  # comment
        for line in sig_lines:
            m = re.search(r'(\w+)[:=].*#\s*(.+)', line)
            if m:
                name, doc = m.groups()
                anno = None
                for arg in node.args.args:
                    if arg.arg == name and arg.annotation:
                        anno = ast.unparse(arg.annotation)
                result[name] = {'anno': anno, 'doc': doc.strip()}

        # Return annotation comment
        if node.returns and node.returns.lineno:
            ret_line = lines[node.returns.lineno - 1]
            m = re.search(r'->[^#]*#\s*(.+)', ret_line)
            if m:
                doc = m.group(1).strip()
                anno = ast.unparse(node.returns) if not isinstance(node.returns, ast.Constant) else None
                result['return'] = {'anno': anno, 'doc': doc}

        return result


    def u_to_google(src: str) -> str:
        "Convert marimo nbdev inline # comments → clean Google docstring with summary first"
        docs = u_param_docs(src)
        if not docs:
            return src  # class or no inline docs

        # Get the main one-line summary (the string right after def)
        tree = ast.parse(src)
        node = tree.body[0]
        main_summary = ast.get_docstring(node) or ""
        if main_summary:
            main_summary = main_summary.strip()

        # Build Google docstring: summary first, then Args, then Returns
        lines = ['"""']
        if main_summary:
            lines.append(main_summary)
            lines.append('')  # blank line after summary

        # Args section
        args = [(n, d) for n, d in docs.items() if n != 'return' and d.get('doc')]
        if args:
            lines.append('Args:')
            for n, d in args:
                typ = f" ({d['anno']})" if d.get('anno') else ''
                lines.append(f"    {n}{typ}: {d['doc']}")
            lines.append('')  # blank line after Args

        # Returns section
        if docs.get('return') and docs['return'].get('doc'):
            lines.append('Returns:')
            r = docs['return']
            typ = f"{r['anno']}: " if r.get('anno') else ''
            lines.append(f"    {typ}{r['doc']}")

        lines.append('"""')

        # === Reconstruct clean signature (remove all # comments from sig lines) ===
        lines_src = src.splitlines()
        sig_start = node.lineno - 1
        sig_end = node.body[0].lineno - 1 if node.body else len(lines_src)

        clean_sig_lines = []
        for line in lines_src[sig_start:sig_end]:
            # Remove everything after and including '#'
            clean_line = re.sub(r'\s*#.*$', '', line).rstrip()
            clean_sig_lines.append(clean_line)

        clean_sig = '\n'.join(clean_sig_lines)
        body = '\n'.join(lines_src[sig_end:])

        return f"{clean_sig}\n{'\n'.join(lines)}\n{body}"
    
    def validate_meta(meta:dict):
        req = '__version__ __description__ __author__ __license__'.split()
        if miss:=[k for k in req if k not in meta]:
            raise ValueError(f"Missing: {', '.join(miss)}")

    def scan(nb_dir:str='notebooks', style:str='google')->ScanResult:
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

    def u_extract(path:Path|str, style:str):
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
                    final = u_to_google(clean) if style == 'google' else clean
                    exps.append(final); names.append(n.name)
        return meta, imps, exps, names

    def write_mod(name:str, imps:list[str], exps:list[str], path:str):
        Path(path).write_text('\n\n'.join(imps + exps + ['']))

    def write_init(pkg:str, meta:dict, mods:list[ModuleInfo], path:str):
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

    def extract_readme(meta:dict, idx:str|None)->str:
        if not idx: return ''
        src = Path(idx).read_text()
        parts = re.findall(r'mo\.md\((?:[rf]|rf)?"""([\s\S]*?)"""', src)
        if not parts: return ''
        txt = '\n\n'.join(parts)
        for k,v in meta.items(): txt = txt.replace(f'{{{k}}}', str(v))
        Path('README.md').write_text(txt)
        return 'README.md'

    def build(nb_dir:str='notebooks', out:str='src', style:str='google')->str:
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
    return (build,)


@app.cell
def _(build):
    build(nb_dir="./", out="test7", style="google")
    return


@app.cell
def _(mo):
    mo.md(r"""
    is this a read me?
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
