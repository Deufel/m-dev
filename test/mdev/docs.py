from mdev.ft_ds import setup_tags, Html, show
from pathlib import Path
import subprocess
import time
from contextlib import contextmanager
from typing import Any

:
    """
    Args:
        a: 
        b: 

    """
def add(a,b): return a+b

def write_doc(s: str, fname: str="index.html"):
    """
    Write string `s` to file `fname` in docs folder

    Args:
        s (str): string to write into file
        fname (str): file name

    """
    p = Path('./docs'); p.mkdir(exist_ok=True)
    (p/fname).write_text(s)
