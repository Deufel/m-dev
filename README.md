
    <!-- #| README  -->



    Package Name: m-dev  
    Version: 0.0.1  
    Description: Build and publish python packages from marimo notebooks  
    Author: Deufel <MDeufel13@gmail.com>  
    License: MIT  

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
    


    r (ie latex) markdown cell
    


    normal markdown cell
    


    latex and f string markdown cell

    Deufel <MDeufel13@gmail.com>
    


    i am a f sting markdown cell
    


    and this is when the code is hidden (we want these variations aswell)
    