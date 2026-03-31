from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

EXPORT_DECORATORS = ('app.function', 'app.class_definition')

def rename(
    name: str,         # original function/class name
    renames: dict,     # prefix substitution map from config
) -> str:              # renamed identifier
    "Apply prefix substitutions to a name. Dunder prefixes wrap both sides."
    for prefix, replacement in renames.items():
        if not name.startswith(prefix): continue
        stem = name[len(prefix):]
        if replacement.startswith('__'): return replacement + stem + '__'
        return replacement + stem
    return name

@dataclass(frozen=True)
class Config:
    "Project configuration from pyproject.toml [tool.marimo-dev]."
    nbs: str              = 'notebooks'   # notebook source directory
    out: str              = 'src'         # package output directory
    docs: str             = 'docs'        # documentation output directory
    root: str             = '.'           # project root
    skip_prefixes: tuple  = ('XX_', 'test_')  # filename prefixes to ignore
    renames: dict         = field(default_factory=dict)  # name prefix substitutions
    application: str|None = None          # entry point e.g. "module:obj" or "module:obj:runner"
 
    @property
    def app_parts(
        self, # Config instance
    ) -> tuple[str, str, str|None]|None:  # (module, object, runner) or None
        "Parse application string into (module, object, optional runner)."
        if not self.application: return None
        parts = self.application.split(':')
        if len(parts) < 2: return None
        return (parts[0], parts[1], parts[2] if len(parts) > 2 else None)

@dataclass
class Param:
    "A function parameter with optional inline documentation."
    name: str               # parameter name
    anno: str = ''          # type annotation
    default: str = ''       # default value
    doc: str = ''           # inline comment

@dataclass
class Return:
    "A return annotation with optional inline documentation."
    anno: str               # return type
    doc: str = ''           # inline comment after ->

@dataclass
class Method:
    "A class method with parameters and return info."
    name: str               # method name
    doc: str = ''           # docstring
    params: list[Param]  = field(default_factory=list)
    ret: Return|None     = None

@dataclass
class Import:
    "An import statement from a setup cell."
    src: str                # e.g. "from pathlib import Path"

@dataclass
class Const:
    "A constant assignment from a setup cell."
    name: str               # variable name
    src: str                # e.g. "MAX_SIZE = 1024"

@dataclass
class Setup:
    "Arbitrary setup code that is not an import or constant."
    src: str                # source text

class ExportKind(Enum):
    "Classification of an exported definition."
    FUNC  = 'func'
    ASYNC = 'async'
    CLASS = 'class'

@dataclass
class Export:
    "A decorated function or class marked for export."
    name: str                            # original name in notebook
    final_name: str = ''                 # name after renames (set by parser)
    public: bool = True                  # part of public API (set by parser)
    kind: ExportKind = ExportKind.FUNC   # func | async | class
    src: str = ''                        # source WITH decorators (original)
    clean_src: str = ''                  # source WITHOUT marimo decorators
    doc: str = ''                        # docstring
    params: list[Param]  = field(default_factory=list)
    methods: list[Method]= field(default_factory=list)
    ret: Return|None     = None
    lineno: int          = 0

@dataclass
class Module:
    "A parsed notebook file containing imports, setup, and exports."
    name: str              # e.g. 'core' (prefix stripped)
    nb_stem: str = ''      # e.g. 'a_core' (original filename stem)
    imports: list[Import]  = field(default_factory=list)
    consts: list[Const]    = field(default_factory=list)
    setup: list[Setup]     = field(default_factory=list)
    exports: list[Export]  = field(default_factory=list)
 
    @property
    def has_exports(self) -> bool:
        "True if module contains any exported definitions."
        return len(self.exports) > 0
 
    @property
    def public_exports(
        self, # Module instance
    ) -> list[Export]:  # exports visible in __init__.py
        "Exports that are part of the public API."
        return [e for e in self.exports if e.public]
 
    @property
    def documented_exports(
        self, # Module instance
    ) -> list[Export]:  # exports included in documentation
        "Exports that should appear in docs."
        return [e for e in self.exports if e.public]

@dataclass
class Meta:
    "Project metadata from pyproject.toml [project]."
    name: str = ''
    version: str = '0.0.0'
    desc: str = ''
    license: str = ''
    author: str = ''
    urls: dict = field(default_factory=dict)
 
    @property
    def repo_url(self) -> str:
        "Repository URL from project.urls."
        return self.urls.get('Repository', '')
 
    @property
    def pkg_name(self) -> str:
        "Python package name (hyphens replaced with underscores)."
        return self.name.replace('-', '_')

@dataclass
class Project:
    "A complete parsed marimo-dev project."
    meta: Meta
    config: Config
    modules: list[Module] = field(default_factory=list)
 
    @property
    def mod_names(
        self, # Project instance
    ) -> list[str]:  # list of module names
        "All module names in build order."
        return [m.name for m in self.modules]
 
    @property
    def nonempty_modules(
        self, # Project instance
    ) -> list[Module]:  # modules that have exports
        "Modules that contain at least one export."
        return [m for m in self.modules if m.has_exports]
