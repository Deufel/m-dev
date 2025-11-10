import numpy as np

def calculate_statistics(data):
    """Calculate basic statistics for a dataset"""
    return {'mean': np.mean(data), 'median': np.median(data), 'std': np.std(data)}

def add(a: int, b: int) -> int:
    """Add `a` to `b`

Returns:
    int: The result is calculated using Python's builtin `+` operator."""
    return a + b

