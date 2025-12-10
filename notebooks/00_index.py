import marimo

__generated_with = "0.18.3"
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
    return


app._unparsable_cell(
    r"""
    mo.md(rf\"\"\"
    <!-- #| README  -->

    Package Name: {__package_name__}  
    Version: {__version__}  
    Description: {__description__}  
    Author: {__author__}  
    License: {__license__}  

    **Build Python packages marimo notebooks.**

    ## CAUTION early release software; brittle.

    # marimo-dev

    Goal
    - make it easy to write python software
        - uv for package management
        - marimo for editor
        - pytest for testing 

    What 
    -parses nbdev notebooks and extracts the \"selfcontained functions into a sanatized python file\"
    -originally I build in toml modification but I think that this is better handled by uv (and marimo).
    -You can mnually modify your pyproject.toml for your usecase.

    * designed to wirk with uv *
    1. uv run marimo dev (must run this way to take full advantage of the marimo package manager)
    2. Write modules in notebooks (`##_` will get stripped)
       - `./notebooks/##_index.py  ->    ./README.md`
       - `./notebooks/##_test*.py  ->    will not be exported`
    3. working out how docs will work still I am looking for something similar to nbdev docs site without using quarto.

    How
    # Write code in modules
    ensure proper pyproject.toml
    ```toml
    # In pyproject.toml
    [project]
    name = \"my-package\"
    version = \"1.0.0\"
    description = \"My package\"
    authors = [{name = \"Name\", email = \"email\"}]
    license = {text = \"MIT\"}
    ```

    Quirks
    ```python
    _func # are local to marimo cell so to export a function and keep it \"internal\"
    __fun # must be used keep inmind the __methode has actual meaning in python
    ```

    TODO

    ```
    [X] function extraction
    [X] src/moduly.py file structure
    [ ] index -> readme
    [ ] skip ##_test*.py modules
    [ ] database build
    [ ] readme file format
    [ ] Docs output
    [ ] llms.txt output
    [ ] UI Polish
    [ ] FUT: Export clean (no docstring modification)
    [ ] FUT: |# export suport
    ```



    ---
    \"\"\")
    """,
    name="_"
)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
