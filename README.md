# marimo_dev

A literate programming build system that converts Marimo notebooks into distributable Python packages. Inspired by nbdev.


## What it does

Looks in `/notebooks` dir for [self contained functions and classes](https://docs.marimo.io/guides/reusing_functions/) and extracts them into a PyPI ready directory. Each notebook will be striped of the leading `##_`, and `XX_` and `test` notebooks will be ignored. Run `md build` to generate a proper Python package with `__init__.py`, module files, and `llms.txt` API documentation.

## What it does not

An intentional effort to minimise magic project set up. You are responsible for setting up your pyproject.toml, and even `mkdir notebooks`. 
  **Note:** *I highly reccommend that you use uv my main motivation for making this was the dependency harmony betwwen marimo and uv*



## Project structure

```
my-project/
├── README.md
├── pyproject.toml
├── notebooks/
│   ├── 01_core.py
│   ├── 02_read.py
│   ├── ...
├── src/                 # auto created
│   └── my_package/
│       ├── __init__.py 
│       ├── core.py    
│       ├── read.py
│       └── ...
├── docs/                # auto created
│   ├── index.html       # Fut ver. 0.2
│   └── llms.txt
└── dist/                # auto created
    └──...
```

## How it works

The build system parses notebooks via AST, extracts decorated exports (`@app.function`, `@app.class_definition`), and writes clean module files. It reads metadata from `pyproject.toml` and generates `__init__.py` with proper imports and `__all__` exports.

The `llms.txt` file contains function signatures with inline documentation extracted from comments, formatted for LLM consumption. This provides a compact API reference.
  **Note:** *this will work much better with [fastcore.docments](https://fastcore.fast.ai/docments.html) style function definitions*

## CLI usage

```bash
md build              # build package from notebooks/
md publish            # publish to PyPI
md publish --test     # publish to Test PyPI
```

## Requirements

- Python 3.12+, Marimo, uv, pyproject.toml
  - for relative imports to work in multi module libraries add the following to your pyproject.tml
  - ``` [tool.marimo.runtime]
   pythonpath = ["src"]  ```

**Tip** *let marimo manages your `pyproject.toml` through its package tab, making dependencies visible and easy to update. When you add packages and remove them from the marimo package tab marimo will automaticly update your pyproject.toml*

## Install

```bash
uv add marimo-dev
```

## Helpful
```bash
uv sync --upgrade` # to update uv.lock and pyroject.toml in one go...
uv cache clean     # General Trouble Shooting Tip
```
- you need to manually update the version in pyproject.toml

## Module structure

- `core.py`  - Data model: `Kind`, `Param`, `Node`
- `read.py`  - Parse notebooks, extract exports, scan project
- `pkg.py`   - Write module files and `__init__.py`
- `docs.py`  - Generate signatures and `llms.txt`
- `build.py` - Orchestrate the build
- `cli.py`   - Command-line interface