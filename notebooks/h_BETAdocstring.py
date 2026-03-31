import marimo

__generated_with = "0.21.1"
app = marimo.App()

with app.setup:
    import inspect
    import re
    from textwrap import dedent
    from typing import Any, Callable, Dict, Optional, Tuple


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Marimo-dev.docstring
    > reformatt Docments style to google style docstring
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Primitive extractors
    """)
    return


@app.function
def internal_get_source_lines(func: Callable) -> list[str]:
    unwrapped = inspect.unwrap(func)
    return dedent(inspect.getsource(unwrapped)).splitlines()


@app.function
def internal_get_summary(func: Callable) -> str:
    doc = inspect.getdoc(func) or ""
    return doc.splitlines()[0].strip() if doc else func.__name__.replace('_', ' ').title()


@app.function
def internal_get_extra_doc(func: Callable) -> str:
    doc = inspect.getdoc(func) or ""
    lines = doc.splitlines()
    return "\n".join(lines[1:]).strip() if len(lines) > 1 else ""


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Comment Extractors
    """)
    return


@app.function
def internal_find_def_line(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            return i
    return 0


@app.function
def internal_extract_inline_comment(line: str) -> Optional[str]:
    if '#' not in line:
        return None
    comment = line.split('#', 1)[1].strip()
    return comment or None


@app.function
def internal_extract_param_name(code_part: str) -> Optional[str]:
    match = re.search(r'\b(\w+)\s*[:\*=]', code_part)
    return match.group(1) if match else None


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Comment parsing
    """)
    return


@app.function
def internal_parse_param_comments(lines: list[str], def_line_idx: int) -> Tuple[Dict[str, str], Optional[str]]:
    param_comments: Dict[str, str] = {}
    return_comment: Optional[str] = None

    for line in lines[def_line_idx + 1:]:
        stripped = line.strip()
        if stripped.startswith(('"""', "'''")):
            continue
        if stripped.startswith(')'):
            return_comment = internal_extract_inline_comment(line)
            break
        if not stripped:
            continue
        comment = internal_extract_inline_comment(line)
        if comment:
            name = internal_extract_param_name(line.split('#')[0])
            if name:
                param_comments[name] = comment

    return param_comments, return_comment


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Section builders
    """)
    return


@app.function
def internal_format_param(name: str, param: inspect.Parameter, comment: str) -> str:
    anno = param.annotation
    anno_str  = f" ({anno.__name__ if hasattr(anno, '__name__') else anno})" \
                if anno is not inspect.Parameter.empty else ""
    default   = param.default
    dflt_str  = f" (default: {default!r})" \
                if default is not inspect.Parameter.empty else ""
    return f"    {name}{anno_str}{dflt_str}: {comment}"


@app.function
def internal_build_args_section(sig: inspect.Signature, param_comments: Dict[str, str]) -> list[str]:
    lines = []
    for name, param in sig.parameters.items():
        if name in ('self', 'cls'):
            continue
        comment = param_comments.get(name, "No description provided.")
        lines.append(internal_format_param(name, param, comment))
    return lines


@app.function
def internal_build_returns_section(sig: inspect.Signature, return_comment: Optional[str]) -> str:
    ret = sig.return_annotation
    ret_str = f" ({ret.__name__ if hasattr(ret, '__name__') else ret})" \
              if ret is not inspect.Signature.empty else ""
    desc = return_comment or "No description provided."
    return f"Returns{ret_str}: {desc}"


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Assembler
    """)
    return


@app.function
def internal_assemble_docstring(summary: str, args: list[str], returns: str, extra: str) -> str:
    sections = [summary, ""]
    if args:
        sections += ["Args:"] + args + [""]
    sections += [returns, ""]
    if extra:
        sections += [extra, ""]
    return "\n".join(sections).rstrip()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Orchastrator
    """)
    return


@app.function
def docments_to_google_docstring(
    func: Callable,
    include_existing_doc: bool = True
) -> str:
    """Convert fast-core style docstrings to Google style."""
    if not callable(func):
        raise TypeError("func must be a callable")
    
    # Handle decorated functions ONCE at the entry point
    func = inspect.unwrap(func)
    
    # Now everything below works exactly as before with the unwrapped function
    try:
        lines = internal_get_source_lines(func)
    except (OSError, TypeError):
        return inspect.getdoc(func) or ""

    sig            = inspect.signature(func)
    summary        = internal_get_summary(func)
    extra          = internal_get_extra_doc(func) if include_existing_doc else ""
    def_idx        = internal_find_def_line(lines)
    param_comments, return_comment = internal_parse_param_comments(lines, def_idx)
    args_section   = internal_build_args_section(sig, param_comments)
    returns_line   = internal_build_returns_section(sig, return_comment)

    return internal_assemble_docstring(summary, args_section, returns_line, extra)


if __name__ == "__main__":
    app.run()
