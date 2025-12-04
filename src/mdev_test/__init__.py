"""A tiny test package"""

__version__ = '0.1.0'
__author__ = 'You'

from .core import ModuleInfo, ScanResult, validate_meta, scan, write_mod, write_init, extract_readme, build

__all__ = [
    "ModuleInfo",
    "ScanResult",
    "build",
    "extract_readme",
    "scan",
    "validate_meta",
    "write_init",
    "write_mod",
]
