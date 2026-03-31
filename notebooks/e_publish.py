import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    """
    marimo-dev publish.

    Build distribution and upload to PyPI.
    Reads credentials from ~/.pypirc, calls uv build + uv publish.

    Public API:
        publish(project, test) -> None
    """

    from pathlib import Path
    import configparser, shutil, subprocess

    from a_types import Project
    from c_build_pkg import build

    PYPI_URLS = {
        'testpypi': 'https://test.pypi.org/legacy/',
        'pypi':     'https://upload.pypi.org/legacy/',
    }
    TOKEN_URLS = {
        'testpypi': 'https://test.pypi.org/manage/account/',
        'pypi':     'https://pypi.org/manage/account/',
    }


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Credentials
    """)
    return


@app.function
def internal_read_pypirc(
    section: str, # 'testpypi' or 'pypi'
) -> tuple[str, str]|None:  # (username, password) or None on failure
    "Read credentials from ~/.pypirc. Prints error and returns None on failure."
    pypirc = Path.home() / '.pypirc'
    url = TOKEN_URLS[section]

    if not pypirc.exists():
        print(f"No ~/.pypirc found. Create a token at {url}"); return None

    cfg = configparser.ConfigParser()
    cfg.read(pypirc)

    if section not in cfg:
        print(f"No [{section}] in ~/.pypirc. Create a token at {url}"); return None

    password = cfg[section].get('password', '')
    if not password:
        print(f"No password in [{section}]. Create a token at {url}"); return None

    username = cfg[section].get('username', '__token__')
    return (username, password)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Public API
    """)
    return


@app.function
def publish(
    proj: Project,  # complete parsed project
    test: bool = True, # True for TestPyPI, False for PyPI
):
    "Build package and publish to PyPI."
    section = 'testpypi' if test else 'pypi'
    target  = 'TestPyPI' if test else 'PyPI'

    creds = internal_read_pypirc(section)
    if not creds: return
    username, password = creds

    preview = password[:9] + '...' if password.startswith('pypi-') else '****'
    print(f"Authenticated as {username} ({preview})")

    print("Building package from notebooks...")
    build(proj)

    shutil.rmtree('dist', ignore_errors=True)
    print("Building distribution...")
    subprocess.run(['uv', 'build'], check=True)

    print(f"Publishing to {target}...")
    try:
        subprocess.run([
            'uv', 'publish',
            '--publish-url', PYPI_URLS[section],
            '--username', username,
            '--password', password,
        ], capture_output=True, text=True, check=True)
        print(f"Published to {target}!")
    except subprocess.CalledProcessError as e:
        if '403' in (e.stderr or ''):
            print(f"Auth failed. Token may be expired. Regenerate at {TOKEN_URLS[section]}")
        else:
            print(f"Publish failed: {e.stderr}")


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
