# m-dev

**WORK IN PROGRESS**

Build Python packages from a single [marimo](https://marimo.io) notebook, inspired by [nbdev](https://nbdev.fast.ai).

## What

> `m-dev` is a tool for converting a marimo notebook into a Python package. 


- Export self-contained functions/classes auto-detected by marimo into a clean module. [marimo self-contained functions](https://docs.marimo.io/guides/reusing_functions/)
- Generate `pyproject.toml` from metadata and dependencies in the `app.setup` cell and script block 
- Copying the README for PyPI compatibility. **thinking of changing to an in notebook readme generation**
- Build docstring from nbdev styly parameter documentation **May modify this to jsut use docstring...  

The notebook is your IDE, dev environment for coding, testing, and demos. The exported package is marimo-free, importable, and PyPI-ready. Marimo’s self-contained detection ensures reusable, isolated code with early error catching.

## Goals

1. Self-contained and reproducable development enviorment notebook.
2. UV package management via marimo
3. Single source of Truth (Source Code, Documents, Testing)
4. Minimal Dpendencie (core libraries + Marimo + Pytest)

## Usage

1. `uv add m-dev...` 
2. In a single marimo notebook, run `uvx marimo edit --sandbox <notebook_name>`
  - ** important to use sandbox as devenviorment enviorment to let marimo track dependencies** 


## ToDo

1. Intergrate CLI for init, and test, and mkdocs
2. Static Docs Generation with no dependencies
3. better testing
4. better pypi integreation 
5. multi notebook support
6. Github Actions Support


## Contributing

### Naming Convention


Submit issues/PRs on [GitHub](https://github.com/deufel/m-dev).
