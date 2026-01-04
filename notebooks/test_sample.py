import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.function
def greet(name:str="World"):
    "Return a greeting"
    return f"Hello, {name}!"


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
