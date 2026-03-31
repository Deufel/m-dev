import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full")

with app.setup:
    from e_build import build, tidy, nuke, bundle
    from f_publish import publish
    from d_docs import build_docs, write_highlighter

    import sys, subprocess
    from pathlib import Path


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Package: Marimo-dev
    ## Module: .cli
    > the cli module
    """)
    return


@app.function
def main():
    if len(sys.argv) < 2: print("Usage: md [build|publish|docs|tidy|nuke]"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'build':
        print(f"Built package at: {build()}")
    elif cmd == 'publish':
        test = '--test' in sys.argv or '-t' in sys.argv
        target = "TestPyPI" if test else "PyPI"
        if input(f"Publish to {target}? [y/N] ").lower() != 'y': print("Aborted"); sys.exit(0)
        publish(test=test)
    elif cmd == 'docs':  
        write_highlighter() 
        build_docs()
    elif cmd == 'tidy': tidy()
    elif cmd == 'nuke': nuke()
    elif cmd == 'bundle':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        print(bundle(name=name))

    else: print(f"Unknown command: {cmd}"); sys.exit(1)


@app.cell
def _():
    def app(sdf):
        return

    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
