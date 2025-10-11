# m-dev

Build and publish Python packages directly from marimo notebooks.

## What it does

Extracts functions/classes marked with `@app.function` and `@app.class_definition` from marimo notebooks and generates:
- Importable Python modules
- `pyproject.toml` for PyPI publishing

## Usage

Copy
from m_dev import build_package build_package("notebook.py", output_dir="dist")


## Current Limitations

Dependencies from `# /// script` block are included in package, even dev-only ones (marimo, pytest). Workaround: manually edit generated `pyproject.toml`.

## Requirements

Python >=3.13