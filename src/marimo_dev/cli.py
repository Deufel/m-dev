from marimo_dev.build import build, tidy, nuke
from marimo_dev.publish import publish
import sys, subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2: print("Usage: md [build|publish|tidy|nuke]"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'build':
        print(f"Built package at: {build()}")
    elif cmd == 'publish':
        test = '--test' in sys.argv or '-t' in sys.argv
        target = "TestPyPI" if test else "PyPI"
        if input(f"Publish to {target}? [y/N] ").lower() != 'y': print("Aborted"); sys.exit(0)
        publish(test=test)
    elif cmd == 'tidy': tidy()
    elif cmd == 'nuke': nuke()
    else: print(f"Unknown command: {cmd}"); sys.exit(1)
