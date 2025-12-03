"""A tiny test package"""

__version__ = '0.1.0'
__author__ = 'You'

from .test_nb import greet, add, Calculator
from .write_docs import write_to_docs

__all__ = [
    "greet",
    "add",
    "Calculator",
    "write_to_docs",
]
