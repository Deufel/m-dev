import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium", app_title="MD.e_cli")

with app.setup:
    import sys, shutil
    from pathlib import Path

    from b_parse import read_project
    from c_build_pkg import build, bundle
    from d_build_docs import build_docs
    from e_publish import publish
    from g_build_docs_html import build_docs_html


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # marimo-dev CLI

    Thin dispatch. read_project() once, pass to the right builder.

    ```
        Usage: md [build|docs|bundle|publish|tidy|nuke]
    ```
    """)
    return


@app.function
def tidy():
    "Remove cache and temporary files."
    for pattern in ('__pycache__', '__marimo__', '.pytest_cache'):
        for p in Path('.').rglob(pattern): shutil.rmtree(p, ignore_errors=True)
    for p in Path('.').rglob('*.pyc'): p.unlink(missing_ok=True)
    print("Cleaned cache files")


@app.function
def nuke():
    "Remove all build artifacts and cache files."
    tidy()
    for d in ('dist', 'docs', 'src', 'temp'):
        shutil.rmtree(d, ignore_errors=True)
    print("Nuked build artifacts")


@app.function
def main():
    "Entry point for the md command."
    if len(sys.argv) < 2:
        print("Usage: md [build|docs|bundle|publish|tidy|nuke]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'tidy':  tidy(); return
    if cmd == 'nuke':  nuke(); return

    # Everything else needs the project
    proj = read_project()

    
    if cmd == 'build':
        pkg = build(proj)
        build_docs(proj)
        print(f"Built package at: {pkg}")

    elif cmd == 'docs':
        print(build_docs(proj))
        print(build_docs_html(proj))

    elif cmd == 'bundle':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        print(bundle(proj, name=name))

    elif cmd == 'publish':
        test = '--test' in sys.argv or '-t' in sys.argv
        target = "TestPyPI" if test else "PyPI"
        if input(f"Publish to {target}? [y/N] ").lower() != 'y':
            print("Aborted"); sys.exit(0)
        publish(proj, test=test)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
