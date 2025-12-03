import re, ast, tomllib
from pathlib import Path
from typing import TypedDict

def __hi(name:str='Mikkke'):
    return print(f"Hi there {name}")

def greet(name: str, excited: bool=False) -> str:
    """
    Create a friendly greeting

    Args:
        name (str): person's name
        excited (bool): add exclamation?

    Returns:
        str: final greeting

    """
    s = f"Hello {name}"
    return s + "!!!" if excited else s + "!"

def add(a: int, b: int=0) -> int:
    """
    Add two numbers

    Args:
        a (int): first number
        b (int): second number (optional)

    Returns:
        int: sum of a and b

    """
    return a + b

class Calculator:
    "Simple calculator with memory"
    def __init__(self, start=0):
        self.memory = start

    def accum(self, x:int)->int:
        "Add `x` to memory and return new total"
        self.memory += x
        return self.memory
