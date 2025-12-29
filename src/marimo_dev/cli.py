from marimo_dev.build import build
import sys, subprocess
from pathlib import Path

def init(
    name:str=None, # project name (defaults to current directory name)
):
    "Initialize a new m-dev project with notebooks dir and pyproject.toml."
    cmd = ['uv', 'init', '--bare', '--no-readme', '--no-pin-python', '--vcs', 'none']
    if name: cmd.append(name)
    subprocess.run(cmd, check=True)
    Path('notebooks').mkdir(exist_ok=True)
    p = Path('pyproject.toml')
    content = p.read_text()
    additions = '''
[tool.marimo.runtime]
pythonpath = ["src"]

[build-system]
requires = ["uv_build>=0.9.15,<0.10.0"]
build-backend = "uv_build"
'''
    if '[build-system]' not in content: p.write_text(content.rstrip() + '\n' + additions)

def main():
    if len(sys.argv) < 2: print("Usage: md [init|build|publish]"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'init': init(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == 'build':
        from m_dev.build import build
        print(f"Built package at: {build()}")
    elif cmd == 'publish':
        test = '--test' in sys.argv or '-t' in sys.argv
        from m_dev.publish import publish
        publish(test=test)
    else: print(f"Unknown command: {cmd}"); sys.exit(1)
