import re, ast, tomllib, io

from pathlib import Path

from tokenize import tokenize, COMMENT

from typing import TypedDict

def greet(
    name:str,
    excited:bool=False
)->str:
"""
Create a friendly greeting

Args:
    name (str): person's name
    excited (bool): add exclamation?
    str: final greeting

Returns:
    str: final greeting
"""
    "Create a friendly greeting"
    s = f"Hello {name}"
    return s + "!!!" if excited else s + "!"

def add(
    a:int,
    b:int=0
)->int:
"""
Add two numbers

Args:
    a (int): first number
    b (int): second number (optional)
    int: sum of a and b

Returns:
    int: sum of a and b
"""
    "Add two numbers"
    return a + b

class Calculator:
    "Simple calculator with memory"
    def __init__(self, start=0):
        self.memory = start
    
    def accum(self, x:int)->int:
        "Add `x` to memory and return new total"
        self.memory += x
        return self.memory

