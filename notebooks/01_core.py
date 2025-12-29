import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    import ast, re, tomllib, json
    from pathlib import Path
    from enum import Enum
    from dataclasses import dataclass, field



@app.class_definition
class Kind(Enum):
    "Types of nodes in parsed code"
    IMP='import'    # Import statement
    CONST='const'   # Constant definition
    EXP='export'    # Exported function or class


@app.class_definition
@dataclass
class Param:
    name: str                # parameter name
    anno: str|None = None    # type annotation
    default: str|None = None # default value
    doc: str = ''            # inline documentation


@app.class_definition
@dataclass 
class Node:
    "A parsed code node representing an import, constant, or exported function/class."
    kind: Kind       # type of node (import/const/export)
    name: str        # identifier name
    src: str         # source code
    doc: str = ''    # docstring text
    params: list[Param] = field(default_factory=list)    # function/class parameters
    ret: tuple[str,str]|None = None                      # return type annotation and doc


@app.cell
def _():
    import marimo as mo
    return


if __name__ == "__main__":
    app.run()
