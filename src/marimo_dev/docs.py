from .core import Kind, Param, Node, Config
from pathlib import Path
import ast
import marimo as mo
from functools import partial

def cls_sig(
    n:Node,           # the node to generate signature for
    dataclass=False,  # whether to include @dataclass decorator
)->str:               # formatted class signature
    "Generate a class signature string."
    header = f"@dataclass\nclass {n.name}:" if dataclass else f"class {n.name}:"
    lines = [header]
    if n.doc: lines.append(f'    """{n.doc}"""')
    for p in n.params:
        attr = f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}"
        if p.doc: attr += f"  # {p.doc}"
        lines.append(attr)
    for m in n.methods:
        ps = ', '.join(f"{p.name}{f': {p.anno}' if p.anno else ''}{f'={p.default}' if p.default else ''}" for p in m['params'])
        ret = f" -> {m['ret'][0]}" if m['ret'] else ""
        lines.append(f"    def {m['name']}({ps}){ret}:")
        if m['doc']: lines.append(f'        """{m["doc"]}"""')
    return '\n'.join(lines)

def fn_sig(n, is_async=False):
    "Generate a function signature string with inline parameter documentation."
    prefix = 'async def' if is_async else 'def'
    ret = f" -> {n.ret[0]}" if n.ret else ""
    if not n.params:
        sig = f"{prefix} {n.name}(){ret}:"
        return f'{sig}\n    """{n.doc}"""' if n.doc else sig
    params = [f"    {p.name}{f': {p.anno}' if p.anno else ''}{f'={p.default}' if p.default else ''},{f'  # {p.doc}' if p.doc else ''}" for p in n.params]
    params[-1] = params[-1].replace(',', '')
    lines = [f"{prefix} {n.name}("] + params + [f"){ret}:"]
    if n.doc: lines.append(f'    """{n.doc}"""')
    return '\n'.join(lines)

def sig(
    n:Node, # the node to generate signature for
)->str:     # formatted signature string
    "Generate a signature string for a class or function node."
    src = n.src.lstrip()
    if n.methods or src.startswith('class ') or src.startswith('@dataclass'):
        return cls_sig(n, dataclass=src.startswith('@dataclass'))
    return fn_sig(n, is_async=src.startswith('async def'))

def write_llms(
    meta:dict,    # project metadata from pyproject.toml
    nodes:list,   # list of Node objects to document
    out='docs',   # output directory path
):
    "Write API signatures to llms.txt file for LLM consumption."
    sigs = '\n\n'.join(sig(n) for n in nodes if not n.name.startswith('__') and 'nodoc' not in n.hash_pipes)
    content = f"# {meta['name']}\n\n> {meta['desc']}\n\nVersion: {meta['version']}\n\n## API\n\n```python\n{sigs}\n```"
    Path(out).mkdir(exist_ok=True)
    (Path(out)/'llms.txt').write_text(content)
