import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    from m_dev.core import Kind, Param, Node
    from m_dev.read import scan
    from m_dev.pkg import write_mod, write_init
    from m_dev.docs import write_llms
    from pathlib import Path
    import ast


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _(shutil):
    def build(
        nbs='notebooks', # directory containing notebook files
        out='src',       # output directory for built package
        root='.',        # root directory containing pyproject.toml
        rebuild=True,   # remove existing package directory before building
    )->str:              # path to built package
        "Build a Python package from notebooks."
        meta, mods = scan(nbs, root)
        pkg = Path(out) / meta['name'].replace('-', '_')
        if rebuild and pkg.exists(): shutil.rmtree(pkg)
        pkg.mkdir(parents=True, exist_ok=True)
        for name, nodes in mods:
            if name != 'index' and any(n.kind == Kind.EXP for n in nodes): write_mod(pkg/f'{name}.py', nodes)
        write_init(pkg/'__init__.py', meta, mods)
        all_exp = [n for _, nodes in mods for n in nodes if n.kind == Kind.EXP]
        if all_exp: write_llms(meta, all_exp)
        return str(pkg)

    return (build,)


@app.cell
def _(build):
    build(out="src")
    return


@app.function
def publish(
    test:bool=True, # Use Test PyPI if True, real PyPI if False
):
    "Build and publish package to PyPI. Looks for ~/.pypirc for credentials, otherwise prompts."
    import subprocess, configparser, shutil
    from pathlib import Path

    shutil.rmtree('dist', ignore_errors=True)
    print("Building package...")
    subprocess.run(['uv', 'build'], check=True)

    pypirc, cmd = Path.home() / '.pypirc', ['uv', 'publish']
    section = 'testpypi' if test else 'pypi'

    if test: cmd.extend(['--publish-url', 'https://test.pypi.org/legacy/'])
    else: cmd.extend(['--publish-url', 'https://upload.pypi.org/legacy/'])

    if pypirc.exists():
        config = configparser.ConfigParser()
        config.read(pypirc)
        if section in config:
            username, password = config[section].get('username', '__token__'), config[section].get('password', '')
            cmd.extend(['--username', username, '--password', password])

    print(f"Publishing to {'Test ' if test else ''}PyPI...")
    subprocess.run(cmd, check=True)


@app.cell
def _():
    publish(test=False)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
