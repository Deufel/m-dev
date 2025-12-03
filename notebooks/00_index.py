import marimo

__generated_with = "0.18.1"
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

    **Build Python packages marimo notebooks.**

    ## CAUTION early release software; brittle.




    ---


    """)
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
