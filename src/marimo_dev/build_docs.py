from pathlib import Path
from .types import Project

def render_llms(
    proj: Project,          # complete parsed project
    base_url: str = '',     # base URL for links
) -> str:                   # llms.txt content
    "Render llms.txt — module index with export names."
    lines = [f"# {proj.meta.name}\n", f"> {proj.meta.desc}\n"]
    for mod in proj.nonempty_modules:
        names = ', '.join(e.final_name for e in mod.documented_exports)
        if names:
            lines.append(f"- [{mod.name}](/{mod.name}): {names}")
    lines.append(f"\n- [llms-full.txt](/llms-full.txt): Complete source code")
    return '\n'.join(lines) + '\n'

def render_llms_full(
    proj: Project, # complete parsed project
) -> str:          # llms-full.txt content
    "Render llms-full.txt — complete cleaned source."
    parts = [f"# {proj.meta.name}\n\n> {proj.meta.desc}\n"]
    for mod in proj.nonempty_modules:
        documented = mod.documented_exports
        if not documented: continue
        parts.append(f"## {mod.name}\n")
        for exp in documented:
            parts.append(exp.clean_src)
    return '\n\n'.join(parts) + '\n'

def build_docs(
    proj: Project, # complete parsed project
) -> str:          # status message
    "Write all documentation files."
    docs = Path(proj.config.root) / proj.config.docs
    docs.mkdir(parents=True, exist_ok=True)
 
    (docs / 'llms.txt').write_text(render_llms(proj))
    (docs / 'llms-full.txt').write_text(render_llms_full(proj))
 
    return f"Wrote docs to {docs}"
