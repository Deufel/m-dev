import ast, re, tomllib, json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field

@dataclass
class Config:
    nbs: str = 'notebooks'
    out: str = 'src'
    docs: str = 'docs'
    root: str = '.'
    decorators: list[str] = field(default_factory=lambda: ['app.function', 'app.class_definition'])
    skip_prefixes: list[str] = field(default_factory=lambda: ['XX_', 'test_'])

def read_config(root='.'):
    "Read config from pyproject.toml [tool.marimo-dev] section with defaults"
    try:
        with open(Path(root)/'pyproject.toml', 'rb') as f: cfg = tomllib.load(f).get('tool', {}).get('marimo-dev', {})
        return Config(**{k: v for k, v in cfg.items() if k in Config.__dataclass_fields__})
    except FileNotFoundError: return Config()

class Kind(Enum):
    "Types of nodes in parsed code"
    IMP='import'    # Import statement
    CONST='const'   # Constant definition
    EXP='export'

@dataclass
class Param:
    name: str                # parameter name
    anno: str|None = None    # type annotation
    default: str|None = None # default value
    doc: str = ''

@dataclass 
class Node:
    "A parsed code node representing an import, constant, or exported function/class."
    kind: Kind
    name: str
    src: str
    doc: str = ''
    params: list[Param] = field(default_factory=list)
    methods: list = field(default_factory=list)
    ret: tuple[str,str]|None = None
    hash_pipes: list[str] = field(default_factory=list)
    module: str = ''
    lineno: int = 0
