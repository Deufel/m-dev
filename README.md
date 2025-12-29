# m_dev

A literate programming build system that converts Marimo notebooks into distributable Python packages.

## What it does

Write code in numbered notebook files in a `notebooks/` directory. Mark functions and classes for export by making them purely functional with references from the setup cell—Marimo detects these automatically. Run `md build` to generate a proper Python package with `__init__.py`, module files, and `llms.txt` API documentation.

## Project structure

```
my-project/
├── pyproject.toml
├── notebooks/
│   ├── 00_core.py
│   ├── 01_read.py
│   ├── 02_pkg.py
│   ├── 03_docs.py
│   └── 04_build.py
└── src/
    └── my_package/
        ├── __init__.py
        ├── core.py
        ├── read.py
        └── ...
```

## How it works

The build system parses notebooks via AST, extracts decorated exports (`@app.function`, `@app.class_definition`), and writes clean module files. It reads metadata from `pyproject.toml` and generates `__init__.py` with proper imports and `__all__` exports.

The `llms.txt` file contains function signatures with inline documentation extracted from comments, formatted for LLM consumption. This provides a compact API reference.

## CLI usage

```bash
md build              # build package from notebooks/
md publish            # publish to PyPI
md publish --test     # publish to Test PyPI
```

## Requirements

- Python 3.10+
- Marimo for notebook management
- uv for dependency management
- pyproject.toml with project metadata

Marimo manages your `pyproject.toml` through its package tab, making dependencies visible and easy to update.

## Install

```bash
uv add m-dev --index testpypi=https://test.pypi.org/simple --index pypi=https://pypi.org/simple --index-strategy unsafe-best-match
```

## Module structure

- `core.py` - Data model: `Kind`, `Param`, `Node`
- `read.py` - Parse notebooks, extract exports, scan project
- `pkg.py` - Write module files and `__init__.py`
- `docs.py` - Generate signatures and `llms.txt`
- `build.py` - Orchestrate the build
- `cli.py` - Command-line interface