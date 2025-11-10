import numpy as np

def calculate_statistics(data):
    """Calculate basic statistics for a dataset"""
    return {
        "mean": np.mean(data),
        "median": np.median(data),
        "std": np.std(data)
    }

def add(
    # The first operand
    a:int,
    # This is the second of the operands to the *addition* operator.
    # Note that passing a negative value here is the equivalent of the *subtraction* operator.
    b:int,
)->int: # The result is calculated using Python's builtin `+` operator.
    "Add `a` to `b`"
    return a+b

