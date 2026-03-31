import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is currently a very helpful package for me to get work done but it has some major problems.

    1. Docs the Documentation Generation in need of a significant overhaul.
        - git links
        - datastar search with cross module search (i think i can juse brute force this for now)
        - require the css core to be finalised first.
    2. Documentation LLMgenerator I think worth keeping but need to clean it up.
    3. **docstring -> google doc**
    4. clean up pyproject.toml settings
    5. update readme documentation
    6. Add support for building aplications bundle Kind of already does this
    7. End to end test not really worried about this untill things are stable.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
