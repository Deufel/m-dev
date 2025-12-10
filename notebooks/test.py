import marimo

__generated_with = "0.18.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    from mdev.ft_ds import setup_tags, show
    return (setup_tags,)


@app.cell
def _(setup_tags):
    setup_tags()
    return


@app.cell
def _(Div):
    Div("test")
    return


@app.cell
def _():
    from mdev.ft_ds import Some_new_tag
    return (Some_new_tag,)


@app.cell
def _(Some_new_tag):
    Some_new_tag("maybe")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
