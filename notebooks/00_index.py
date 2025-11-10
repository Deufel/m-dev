import marimo

__generated_with = "0.17.5"
app = marimo.App(width="full")

with app.setup:
    __version__ = "0.0.1"
    __package_name__ = "m-dev"
    __description__ = "Build and publish python packages from marimo notebooks"
    __author__ = "Deufel <MDeufel13@gmail.com>"
    __license__ = "MIT"


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(rf"""
    <!-- #| README  -->



    Package Name: {__package_name__}  
    Version: {__version__}  
    Description: {__description__}  
    Author: {__author__}  
    License: {__license__}  

    ## NEED TO UPDATE out of date 

    MIKE DEUFEL
    **Build Python packages from a single marimo notebook.**

    ## CAUTION UNDER CONSTRUCTION 
    ---

    ## What it does

    `m-dev` lets you use marimo to write **clean, installable Python packages, and applications**

    - Exports **self-contained functions/classes** (auto-detected via marimo’s `@function` / `@class_definition`)

    - Copies `#| readme` cell → `README.md`
    - Builds docstrings from `#| param` comments (nbdev-style)
    - Final package: **marimo-free, PyPI-ready**

    Your notebook is your **IDE, test runner, demo, and source of truth**.

    ---

    ## Problems it solves

    | Problem | How `m-dev` helps |
    |--------|------------------|
    | "I deleted a cell / variable and didn’t notice" | With marimo, **downstream cells break immediately** — you *can’t* miss it |
    | "I don’t know what packages I need" | marimo + UV **tracks every import** and suggests missing ones |
    | "Jupyter execution order is fragile" | marimo runs via **DAG** — no hidden state, no out-of-order surprises |

    ---

    ## How it works
    ...

    ## Design choices

     - No #| export needed → Exports auto-detected from marimo decorators via AST - **ensures functions are selfcontained** 
     - Manage Dependencies via UV add, uv remove ect and let uv take care of package resolution.
     **TIP: Use a group for development packages**  

    ```bash
    uv add --group dev marimo anthropic pytest
    ```

     - Unused imports? Still require manual cleanup → Not perfect, but: if you delete all deps, marimo detects missing imports and prompts to install
     - Testing stays in notebook → Use marimo’s built-in pytest support — runs live, never exported

    ## Troubleshooting tips
    - can not open; clear uv cache
    -
    """)
    return


@app.function
def say_something(): return print("something")


@app.cell
def _():
    say_something()
    return


@app.cell
def _(mo):
    mo.md(r"""
    r (ie latex) markdown cell
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    normal markdown cell
    """)
    return


@app.cell
def _(mo):
    mo.md(rf"""
    latex and f string markdown cell

    {__author__}
    """)
    return


@app.cell
def _(mo):
    mo.md(f"""
    i am a f sting markdown cell
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    and this is when the code is hidden (we want these variations aswell)
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
