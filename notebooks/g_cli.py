import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full")

with app.setup:
    from e_build import build, tidy, nuke, bundle
    from f_publish import publish
    from d_docs import build_docs

    import sys, subprocess
    from pathlib import Path


@app.function
def main():
    if len(sys.argv) < 2: print("Usage: md [build|publish|docs|tidy|nuke]"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'build':
        print(f"Built package at: {build()}")
        print(build_docs())
    elif cmd == 'publish':
        test = '--test' in sys.argv or '-t' in sys.argv
        target = "TestPyPI" if test else "PyPI"
        if input(f"Publish to {target}? [y/N] ").lower() != 'y': print("Aborted"); sys.exit(0)
        publish(test=test)
    elif cmd == 'docs': build_docs()
    elif cmd == 'tidy': tidy()
    elif cmd == 'nuke': nuke()
    elif cmd == 'bundle':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        print(bundle(name=name))

    else: print(f"Unknown command: {cmd}"); sys.exit(1)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
