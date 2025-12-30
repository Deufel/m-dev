# marimo-dev

Build Python packages from Marimo notebooks.

## Quick start

```bash
uv init --lib my-project
cd my-project
uv add marimo marimo-dev
mkdir notebooks
```

Create `notebooks/a_core.py`:

```python
import marimo
app = marimo.App()

@app.function
def greet(name:str="World"):
    "Return a greeting"
    return f"Hello, {name}!"
```

Build and publish:

```bash
md build
md publish --test
```

## How it works

marimo-dev extracts self-contained functions and classes from your notebooks and writes them to clean Python modules. It generates `__init__.py` with proper exports and creates `llms.txt` API documentation.

## Project structure

```
my-project/
├── pyproject.toml
├── notebooks/
│   ├── a_core.py      # letter prefix avoids import collisions
│   ├── b_utils.py
│   └── XX_draft.py    # XX_ prefix = ignored
├── src/               # generated
│   └── my_project/
│       ├── __init__.py 
│       ├── core.py    # prefix stripped
│       └── utils.py
└── docs/              # generated
    └── llms.txt
```

## Module naming

Prefix notebooks with letters (`a_`, `b_`, `c_`) to avoid import collisions during development. The prefix is stripped in the built package.

In notebooks, import from other notebooks directly:
```python
from a_core import greet
```

marimo-dev rewrites these to relative imports in the built package:
```python
from .core import greet
```

## Configuration

Add to `pyproject.toml`:

```toml
[tool.marimo-dev]
nbs = "notebooks"           # notebook directory
out = "src"                 # output directory
docs = "docs"               # docs directory
decorators = ["app.function", "app.class_definition"]
skip_prefixes = ["XX_", "test_"]
```

All settings are optional. Defaults shown above.

## Hash pipes

Control exports and documentation with directives:

```python
@app.function
#| nodoc
def helper(): pass         # exported but not documented

@app.function
#| internal
def _internal(): pass      # not exported to __all__

@app.function
#| nodoc internal
def _helper(): pass        # neither exported nor documented
```

## Documentation style

Use [fastcore.docments](https://fastcore.fast.ai/docments.html) style for best results:

```python
@app.function
def add(
    a:int, # first number
    b:int, # second number
)->int:    # sum
    "Add two numbers"
    return a + b
```

Comments become inline parameter documentation in `llms.txt`.

## Commands

```bash
md build              # build package
md publish --test     # publish to Test PyPI
md publish            # publish to PyPI
md tidy               # remove cache files
md nuke               # remove all build artifacts
```

## Requirements

Python 3.12+, marimo, uv

## Tips

- Let marimo manage dependencies through its package tab
- Update version manually in `pyproject.toml` before publishing
- Use `uv sync --upgrade` to update all dependencies
- Use `uv cache clean` for troubleshooting
- To test built code during development, add `pythonpath = ["src"]` to `[tool.marimo.runtime]` in `pyproject.toml`