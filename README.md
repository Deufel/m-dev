
![PyPI version](https://img.shields.io/pypi/v/marimo-dev)

> [!WARNING]
> This project is under active development and is not an official marimo tool - Mar 2026

# marimo-dev

```md
types.py       →  what things are
parse.py       →  read notebooks into types
build_pkg.py   →  Project → Python package
build_docs.py  →  Project → documentation
publish.py     →  Project → PyPI
cli.py         →  dispatch
```

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A cool library"

[tool.marimo-dev]
nbs = "notebooks"                            # default
out = "src"                                  # default
docs = "docs"                                # default
skip_prefixes = ["XX_", "test_"]             # default
application = "server:app:py_sse.serve"      # optional, enables __main__.py

[tool.marimo-dev.renames]
internal_ = "_"                              # internal_foo → _foo (private)
dunder_   = "__"                             # dunder_init  → __init__
```

```md
notebooks/
├─ a_utils.py            → exported as "utils" (letter prefix stripped)
├─ b_database.py         → exported as "database"
├─ XX_scratch.py         → skipped (XX_ prefix)
├─ test_stuff.py         → skipped (test_ prefix)

$ md build
  src/my_project/
  ├─ __init__.py          # re-exports public symbols, __version__, __all__
  ├─ utils.py             # from a_utils.py (imports rewritten to relative)
  ├─ database.py          # from b_database.py
  └─ __main__.py          # only when application is set in config
  docs/
  ├─ llms.txt             # module index with export names
  └─ llms-full.txt        # complete cleaned source for LLM consumption

$ md bundle app.py
  app.py                  # single file, PEP 723 deps header, entry point appended
                          # → uv run app.py just works

$ md docs
  docs/
  ├─ llms.txt             # module index with export names
  └─ llms-full.txt        # complete cleaned source

$ md publish [--test]
  builds package, then uploads to PyPI (or TestPyPI with --test)
  requires ~/.pypirc with token

$ md tidy
  removes __pycache__/, __marimo__/, .pytest_cache/, *.pyc

$ md nuke
  tidy + removes dist/, docs/, src/, temp/
```