import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")

with app.setup:
    import numpy as np


@app.function
def calculate_statistics(data):
    """Calculate basic statistics for a dataset"""
    return {
        "mean": np.mean(data),
        "median": np.median(data),
        "std": np.std(data)
    }


@app.cell
def _():
    def func2(x): return x

    def func3(): return "nothing"
    return


@app.function
def add(
    # The first operand
    a:int,
    # This is the second of the operands to the *addition* operator.
    # Note that passing a negative value here is the equivalent of the *subtraction* operator.
    b:int,
)->int: # The result is calculated using Python's builtin `+` operator.
    "Add `a` to `b`"
    return a+b


@app.cell
def _():
    import marimo as mo
    return


if __name__ == "__main__":
    app.run()
