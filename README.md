# m-dev

**WORK IN PROGRESS**

Build Python packages from a single [marimo](https://marimo.io) notebook, inspired by [nbdev](https://nbdev.fast.ai).

## What it does

`m-dev` converts a marimo notebook (run in `edit --sandbox` mode) into a Python package by:
- Exporting self-contained functions/classes auto-detected by marimo into a clean module.
- Generating `pyproject.toml` from metadata and dependencies in the `app.setup` cell and script block.
- Copying the README for PyPI compatibility.
- Rendering API docs in-notebook via `format_function_doc`.

The notebook is your dev environment for coding, testing, and demos. The exported package is marimo-free, importable, and PyPI-ready. Marimo’s self-contained detection ensures reusable, isolated code with early error catching.

## Usage

1. In a single marimo notebook, run `marimo edit --sandbox` to auto-detect self-contained functions/classes ([see marimo docs](https://docs.marimo.io/guides/reusing_functions/)).
   - In the `app.setup` cell, define production dependencies and required metadata:
     - `__version__`: Package version (e.g., "1.0.0").
     - `__package_name__`: Package name (e.g., "my-lib").
     - `__description__`: Short description (e.g., "My library").
     - `__author__`: Author name and email (e.g., "Name <email@example.com>").
     - `__license__`: License (e.g., "MIT").
   - Import dev dependencies (e.g., `marimo`, `pytest`) elsewhere.
   - Write functions/classes in separate cells for self-contained detection.
2. Build the package:
   ```python
   from m_dev import build_package
   build_package("notebook.py", output_dir="dist")
   ```
3. Install or publish:
   ```bash
   cd dist
   pip install -e .
   python -m build
   ```

Output:
- `dist/{package_name}/__init__.py`: Module with setup imports and self-contained functions/classes.
- `dist/pyproject.toml`: Metadata and production dependencies.
- `dist/README.md`: Copied README.

## Self-Contained Exports

Marimo’s `--sandbox` mode auto-detects self-contained functions/classes, marking them for export ([see marimo docs](https://docs.marimo.io/guides/reusing_functions/)). Benefits:
- **Isolation**: No dependency on notebook globals or cell order.
- **Early error catching**: Non-self-contained code fails to export.
- **Reusability**: Clean, importable code for libraries.
- **Flexibility**: Test and demo in the notebook without affecting the package.

*Note*: Marimo auto-applies decorators to self-contained code in `--sandbox` mode.

## Features

- Exports only marimo-detected self-contained functions/classes.
- Filters dependencies to `app.setup` imports and script block, excluding dev deps (e.g., `marimo`, `pytest`).
- Generates `pyproject.toml` with `[build-system]` for `hatchling` and package structure (`dist/{package_name}/__init__.py`).
- Renders API docs with `format_function_doc`.
- Supports literate programming: develop, test, document, and build in one notebook.

## Limitations

- Single notebook only (multi-notebook support planned).
- AST parsing may break if marimo’s syntax changes.
- Complex classes (e.g., nested) need testing.
- No async function or top-level await support.

## Requirements

- Python >=3.13
- `marimo` (dev only, not in exported package)
- `hatchling` (for building, in `pyproject.toml`)

## Contributing

Submit issues/PRs on [GitHub](https://github.com/your-repo/m-dev).
