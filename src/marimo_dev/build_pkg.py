from pathlib import Path
import re, shutil, sys
from .types import Project, Module

def _apply_renames(
    src: str,          # source code text
    name: str,         # original function/class name
    final_name: str,   # resolved name from parser
) -> str:              # source with def/class name replaced
    "Rename a function/class definition in source."
    if final_name == name: return src
    return re.sub(
        rf'(?m)^(\s*(?:async\s+)?(?:def|class)\s+){re.escape(name)}\b',
        rf'\g<1>{final_name}', src, count=1
    )

def _rewrite_import(
    src: str,              # import statement source
    mod_names: list[str],  # module names in this project
) -> str:                  # rewritten import with relative path
    "Rewrite cross-notebook imports to relative package imports."
    if not src.strip().startswith('from '): return src
    parts = src.split()
    if len(parts) < 2: return src
    module = parts[1]
    if module.startswith('.'): return src
    stripped = re.sub(r'^[a-z]_', '', module)
    if stripped in mod_names:
        return src.replace(f'from {module}', f'from .{stripped}')
    return src

def _write(
    path: Path,    # file path to write
    *parts: str,   # content parts to join with blank lines
):
    "Write non-empty parts joined by blank lines."
    path.write_text('\n\n'.join(p for p in parts if p and p.strip()) + '\n')

def _write_module(
    path: Path,            # output .py file path
    mod: Module,           # parsed module data
    mod_names: list[str],  # all module names for import rewriting
):
    "Write a single .py module file from a Module."
    imports = '\n'.join(_rewrite_import(i.src, mod_names) for i in mod.imports)
    consts  = '\n'.join(c.src for c in mod.consts)
    setup   = '\n'.join(s.src for s in mod.setup)

    exp_src = '\n\n'.join(
        _apply_renames(e.clean_src, e.name, e.final_name) for e in mod.exports
    )

    # Fix cross-references to renamed symbols
    rename_map = {
        e.name: e.final_name
        for e in mod.exports
        if e.final_name != e.name
    }
    for old, new in rename_map.items():
        exp_src = re.sub(rf'\b{re.escape(old)}\b', new, exp_src)

    _write(path, imports, consts, setup, exp_src)

def _write_init(
    path: Path,     # path to write __init__.py
    proj: Project,  # complete parsed project
):
    "Generate __init__.py with metadata and re-exports."
    meta = proj.meta
    lines = [f'"""{meta.desc}"""', f"__version__ = '{meta.version}'"]
    if meta.author:
        lines.append(f"__author__ = '{meta.author.split('<')[0].strip()}'")

    all_exports = []
    for mod in proj.modules:
        pub = [e.final_name for e in mod.public_exports]
        if pub:
            lines.append(f"from .{mod.name} import {', '.join(pub)}")
            all_exports.extend(pub)

    if all_exports:
        entries = '\n'.join(f'    "{n}",' for n in sorted(all_exports))
        lines.append(f'__all__ = [\n{entries}\n]')

    _write(path, '\n'.join(lines))

def _write_main(
    path: Path,                            # path to write __main__.py
    app_parts: tuple[str, str, str|None],  # (module, object, optional runner)
):
    "Generate __main__.py entry point for application mode."
    mod, obj, runner = app_parts
    if runner:
        pkg, func = runner.rsplit('.', 1)
        code = f"from .{mod} import {obj}\nfrom {pkg} import {func}\n{func}({obj})\n"
    else:
        code = f"from .{mod} import {obj}\n{obj}()\n"
    path.write_text(code)

def _entry_point_src(
    app_parts: tuple[str, str, str|None], # (module, object, optional runner)
) -> str:                                  # source code for entry point block
    "Generate entry point source for bundle mode (no relative imports)."
    _, obj, runner = app_parts
    if runner:
        _, func = runner.rsplit('.', 1)
        return f"\n{func}({obj})\n"
    else:
        return f"\n{obj}()\n"

def build(
    proj: Project, # complete parsed project
) -> str:          # path to built package directory
    "Build a Python package from a parsed Project."
    cfg, meta = proj.config, proj.meta
    pkg = Path(cfg.root) / cfg.out / meta.pkg_name
    if pkg.exists(): shutil.rmtree(pkg)
    pkg.mkdir(parents=True, exist_ok=True)

    mod_names = proj.mod_names
    for mod in proj.modules:
        if mod.name != 'index' and mod.has_exports:
            _write_module(pkg / f'{mod.name}.py', mod, mod_names)

    _write_init(pkg / '__init__.py', proj)
    if cfg.app_parts:
        _write_main(pkg / '__main__.py', cfg.app_parts)

    return str(pkg)

def bundle(
    proj: Project,           # complete parsed project
    name: str | None = None, # output filename (None for default)
) -> str:                    # path to bundled file
    "Bundle all modules into a single Python file with PEP 723 deps."
    cfg, meta = proj.config, proj.meta
    mod_names = set(proj.mod_names)
 
    # Collect external imports, deduplicate
    seen_imports: set[str] = set()
    external_imports: list[str] = []
    dep_modules: set[str] = set()
 
    for mod in proj.modules:
        for imp in mod.imports:
            is_local = False
            if imp.src.startswith('from '):
                parts = imp.src.split()
                if len(parts) >= 2:
                    root_mod = re.sub(r'^[a-z]_', '', parts[1]).split('.')[0]
                    if root_mod in mod_names: is_local = True
                    elif parts[1].split('.')[0] not in sys.stdlib_module_names:
                        dep_modules.add(parts[1].split('.')[0])
            elif imp.src.startswith('import '):
                parts = imp.src.split()
                if len(parts) >= 2:
                    root_mod = parts[1].split('.')[0]
                    if root_mod not in sys.stdlib_module_names:
                        dep_modules.add(root_mod)
 
            if not is_local and imp.src not in seen_imports:
                seen_imports.add(imp.src)
                external_imports.append(imp.src)
 
    # PEP 723 header
    deps_str = ', '.join(f'"{d}"' for d in sorted(dep_modules))
    header = f'# /// script\n# dependencies = [{deps_str}]\n# ///'
 
    imports = '\n'.join(external_imports)
    consts  = '\n'.join(c.src for m in proj.modules for c in m.consts)
    setup   = '\n'.join(s.src for m in proj.modules for s in m.setup)
 
    # Apply renames to exports and fix cross-references
    exports = '\n\n'.join(
        _apply_renames(e.clean_src, e.name, e.final_name)
        for m in proj.modules for e in m.exports
    )
    rename_map = {
        e.name: e.final_name
        for m in proj.modules for e in m.exports
        if e.final_name != e.name
    }
    for old, new in rename_map.items():
        exports = re.sub(rf'\b{re.escape(old)}\b', new, exports)
 
    sections = [header, imports, consts, setup, exports]
 
    if cfg.app_parts:
        sections.append(_entry_point_src(cfg.app_parts))
 
    content = '\n\n'.join(p for p in sections if p.strip())
 
    if name:
        out = Path(cfg.root) / name
    else:
        out = Path(cfg.root) / cfg.out / meta.pkg_name / '__init__.py'
 
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    return str(out)
