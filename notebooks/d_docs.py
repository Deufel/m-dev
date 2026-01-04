import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    from a_core import Kind, Param, Node, Config, read_config
    from pathlib import Path
    import ast
    import marimo as mo
    from functools import partial


@app.function
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


@app.function
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


@app.function
def sig(
    n:Node, # the node to generate signature for
)->str:     # formatted signature string
    "Generate a signature string for a class or function node."
    src = n.src.lstrip()
    if n.methods or src.startswith('class ') or src.startswith('@dataclass'):
        return cls_sig(n, dataclass=src.startswith('@dataclass'))
    return fn_sig(n, is_async=src.startswith('async def'))


@app.function
def write_llms(
    meta: dict,    # project metadata from pyproject.toml
    nodes: list,   # list of Node objects to document
    root: str='.'  # root directory containing pyproject.toml
):
    "Write API signatures to llms.txt file for LLM consumption."
    cfg = read_config(root)
    sigs = '\n\n'.join(sig(n) for n in nodes if not n.name.startswith('__') and 'nodoc' not in n.hash_pipes)
    content = f"# {meta['name']}\n\n> {meta['desc']}\n\nVersion: {meta['version']}\n\n## API\n\n```python\n{sigs}\n```"
    Path(cfg.docs).mkdir(exist_ok=True)
    (Path(cfg.docs)/'llms.txt').write_text(content)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Micro Html Template lib
    """)
    return


@app.cell
def _():
    # Void elements (self-closing)
    _v = 'area base br col embed hr img input link meta source track wbr'.split()

    def t(tag, *c, **a):
        """HTML element. Auto-detects void tags."""
        attrs = ''.join(f' {k.rstrip("_").replace("_","-")}{"" if v is True else f"={chr(34)}{v}{chr(34)}"}'
                        for k,v in a.items() if v is not False and v is not None)
        if tag in _v: return f'<{tag}{attrs}>'
        return f'<{tag}{attrs}>{"".join(str(x) for x in c)}</{tag}>'

    # Common tags via lambda with default arg binding
    div,span,p,a,h1,h2,h3,ul,ol,li,b,i,strong,em = \
        [lambda *c,tag=x,**a: t(tag,*c,**a) for x in 'div span p a h1 h2 h3 ul ol li b i strong em'.split()]
    section,article,header,footer,nav,main,aside = \
        [lambda *c,tag=x,**a: t(tag,*c,**a) for x in 'section article header footer nav main aside'.split()]
    img,br,hr,input_,meta,link = \
        [lambda tag=x,**a: t(tag,**a) for x in 'img br hr input meta link'.split()]

    # Helpers
    html = lambda head,body: f'<!DOCTYPE html><html><head>{head}</head><body>{body}</body></html>'
    css = lambda s: t('style',s)
    script = lambda s,**a: t('script',s,**a)
    raw = lambda s: s  # Pass-through for pre-rendered HTML
    return


@app.cell
def _():
    def _join(c): return ''.join(str(x) for x in c)
    def _attrs(a): return ''.join(f' {k.rstrip("_").replace("_","-")}="{v}"' for k,v in a.items() if v)
    def tag(t,*c,**a): return f'<{t}{_attrs(a)}>{_join(c)}</{t}>'
    def void(t,**a): return f'<{t}{_attrs(a)}>'
    def join(*els): return ''.join(els) 

    div,span,p,a,h1,h2,h3,ul,ol,li = [partial(tag,t) for t in 'div span p a h1 h2 h3 ul ol li'.split()]
    section,article,header,footer,nav,main = [partial(tag,t) for t in 'section article header footer nav main'.split()]
    img,br,hr,input_,meta = [partial(void,t) for t in ['img','br','hr','input','meta']]

    def html(head,body): return f'<!DOCTYPE html><html><head>{head}</head><body>{body}</body></html>'
    def css(s): return tag('style',s)
    def script(s): return tag('script',s)

    page = html(
        head=join(tag('title','My Site'), css('body { margin: 0; }')),
        body=join(
            header(h1('Welcome')),
            main(
                section(
                    h2('About'),
                    p('Lorem ipsum', class_='intro'),
                    ul(li('One'), li('Two'))
                ),
                div(img(src='pic.jpg', alt='Photo'), class_='gallery')
            )
        )
    )
    return (page,)


@app.cell
def _(page):
    page
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
