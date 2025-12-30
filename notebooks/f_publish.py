import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    import subprocess, configparser, shutil
    from pathlib import Path
    from e_build import build


@app.function
def publish(
    test:bool=True, # Use Test PyPI if True, real PyPI if False
):
    "Build and publish package to PyPI. Looks for ~/.pypirc for credentials, otherwise prompts."

    print("Rebuilding package from notebooks...")
    build(rebuild=True)

    shutil.rmtree('dist', ignore_errors=True)
    print("Building distribution...")
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
    publish(test=0)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
