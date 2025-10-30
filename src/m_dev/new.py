import numpy as np

def calculate_statistics(data):
    """Calculate basic statistics for a dataset

    Args:
        data: 

    """
    return {'mean': np.mean(data), 'median': np.median(data), 'std': np.std(data)}

def add(a: int, b: int) -> int:
    """Add `a` to `b`

    Args:
        a (int): The first operand
        b (int): This is the second of the operands to the *addition* operator.
Note that passing a negative value here is the equivalent of the *subtraction* operator.

    Returns:
        int: The result is calculated using Python's builtin `+` operator.
    """
    return a + b

