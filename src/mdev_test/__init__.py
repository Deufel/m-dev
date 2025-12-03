"""A tiny test package"""

__version__ = '0.1.0'
__author__ = 'You'

from .test_nb import greet, add, Calculator

__all__ = [
    "Calculator",
    "add",
    "greet",
]
