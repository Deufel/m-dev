# m-dev

    Version: 0.0.1

    **Build Python packages from a single marimo notebook.**

    Version: `0.0.1` | **Work in progress**

    ---

    ## What it does

    `m-dev` turns **one marimo notebook** into a **clean, installable Python package**.

    - Exports **self-contained functions/classes** (auto-detected via marimo’s `@function` / `@class_definition`)
    - Generates `pyproject.toml` from `/// script` and `app.setup`
    - Tracks **real dependencies** using marimo + UV in `--sandbox` mode
    - Copies `#| readme` cell → `README.md`
    - Builds docstrings from `#| param` comments (nbdev-style)
    - Final package: **marimo-free, PyPI-ready**

    Your notebook is your **IDE, test runner, demo, and source of truth**.

    ---

    ## Problems it solves

    | Problem | How `m-dev` helps |
    |--------|------------------|
    | "I deleted a cell and didn’t notice" | With marimo, **downstream cells break immediately** — you *can’t* miss it |
    | "I don’t know what packages I need" | marimo + UV in `--sandbox` **tracks every import** and suggests missing ones |
    | "My package has wrong/outdated deps" | Only **deps from `app.setup` cell** go into `pyproject.toml` — versions pulled from **current UV environment** |
    | "Jupyter execution order is fragile" | marimo runs via **DAG** — no hidden state, no out-of-order surprises |

    ---

    ## How it works

    1. Write in a marimo notebook:
        - TODO Build an init CLI
    2. Run in a Sandbox (required for accurate dependency tracking)
        - uvx marimo edit --sandbox mypkg.py
    3. Build the Package
       ```python
        import m_dev (need  anew name wont let me use this.. ?)
        m_dev.build("mypkg.py", "dist/")
        ```
    4. Output
       ```bash
        dist/
        ├── src/mypkg/
        │   ├── __init__.py
        │   └── core.py
        ├── pyproject.toml
        └── README.md
        ```
    5. install
        ```python
        pip install dist/mypkg-0.1.0.tar.gz
        ```

    ## Design choices

     - No #| export needed → Exports auto-detected from marimo decorators via AST
     - Self-containment via marimo’s DAG → If a function uses a variable from another cell, it won’t export
     - Dependencies = only what’s in app.setup → Version numbers pulled from current UV lockfile → tests run on exact versions that ship
     - Unused imports? Still require manual cleanup → Not perfect, but: if you delete all deps, marimo detects missing imports and prompts to install
     - Testing stays in notebook → Use marimo’s built-in pytest support — runs live, never exported