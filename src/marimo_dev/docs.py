from marimo_dev.core import Kind, Param, Node
from pathlib import Path
import ast

def cls_sig(
    n:Node,           # the node to generate signature for
    dataclass=False,  # whether to include @dataclass decorator
)->str:               # formatted class signature
    "Generate a class signature string."
    header = f"@dataclass\nclass {n.name}:" if dataclass else f"class {n.name}:"
    lines = [header]
    if n.doc: lines.append(f'    """{n.doc}"""')
    lines.extend(f"    {p.name}{f': {p.anno}' if p.anno else ''}{f' = {p.default}' if p.default else ''}" for p in n.params)
    return '\n'.join(lines)

def fn_sig(
    n:Node,         # the node to generate signature for
    is_async=False, # whether function is async
)->str:             # formatted function signature
    "Generate a function signature string."
    ps = ', '.join(f"{p.name}{f': {p.anno}' if p.anno else ''}{f'={p.default}' if p.default else ''}" for p in n.params)
    ret = f" -> {n.ret[0]}" if n.ret else ""
    s = f"{'async def' if is_async else 'def'} {n.name}({ps}){ret}:"
    return f"{s}\n    \"\"\"{n.doc}\"\"\"" if n.doc else s

def sig(
    n:Node, # the node to generate signature for
)->str:     # formatted signature string
    "Generate a signature string for a class or function node."
    src = n.src.lstrip()
    if src.startswith('@dataclass'): return cls_sig(n, dataclass=True)
    if src.startswith('class '): return cls_sig(n)
    return fn_sig(n, is_async=src.startswith('async def'))

def write_llms(
    meta:dict,    # project metadata from pyproject.toml
    nodes:list,   # list of Node objects to document
    out='docs',   # output directory path
):
    "Write API signatures to llms.txt file for LLM consumption."
    sigs = '\n\n'.join(sig(n) for n in nodes if not n.name.startswith('__'))
    content = f"# {meta['name']}\n\n> {meta['desc']}\n\nVersion: {meta['version']}\n\n## API\n\n```python\n{sigs}\n```"
    Path(out).mkdir(exist_ok=True)
    (Path(out)/'llms.txt').write_text(content)
