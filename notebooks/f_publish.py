import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full")

with app.setup:
    import subprocess, configparser, shutil
    from pathlib import Path
    from e_build import build

    CREDENTIALS = {
        'testpypi': {'file': '~/.pypirc', 'section': 'testpypi', 'key_field': 'password', 'prefix': 'pypi-', 'url': 'https://test.pypi.org/manage/account/'},
        'pypi':     {'file': '~/.pypirc', 'section': 'pypi',     'key_field': 'password', 'prefix': 'pypi-', 'url': 'https://pypi.org/manage/account/'},
        'github':   {'cmd': 'gh auth status', 'url': 'https://github.com/settings/tokens'},
    }


@app.cell
def _():
    # publish(test=1)
    # publish(test=0)
    return


@app.function
def check_credentials(platform='testpypi'):
    "Check if credentials exist for a platform and return status info."
    cred = CREDENTIALS.get(platform)
    if not cred: return {'found': False, 'msg': f"Unknown platform: {platform}"}

    url = cred['url']

    # Command-based check (e.g. GitHub)
    if 'cmd' in cred:
        try:
            r = subprocess.run(cred['cmd'].split(), capture_output=True, text=True)
            if r.returncode == 0:
                return {'found': True, 'platform': platform, 'msg': r.stdout.strip(), 'source': cred['cmd']}
            return {'found': False, 'msg': f"Not authenticated. Set up at {url}"}
        except FileNotFoundError:
            return {'found': False, 'msg': f"CLI not installed. Get it at {url}"}

    # File-based check (e.g. PyPI)
    path = Path(cred['file']).expanduser()
    if not path.exists():
        return {'found': False, 'msg': f"No {cred['file']} found. Create a token at {url}"}

    config = configparser.ConfigParser()
    config.read(path)
    section = cred['section']

    if section not in config:
        return {'found': False, 'msg': f"No [{section}] section in {cred['file']}. Create a token at {url}"}

    password = config[section].get(cred['key_field'], '')
    if not password:
        return {'found': False, 'msg': f"No {cred['key_field']} in [{section}]. Create a token at {url}"}

    prefix = cred.get('prefix', '')
    preview = password[:len(prefix)+4] + '...' if password.startswith(prefix) else '****'
    return {'found': True, 'platform': platform, 'username': config[section].get('username', ''), 'preview': preview, 'source': str(path)}


@app.cell
def _():
    check_credentials(platform="testpypi")
    check_credentials(platform="github")
    return


@app.function
def check_pypi_auth(test=True):
    "Check if PyPI credentials exist and return status info."
    pypirc = Path.home() / '.pypirc'
    section = 'testpypi' if test else 'pypi'
    target = 'Test PyPI' if test else 'PyPI'
    url = 'https://test.pypi.org/manage/account/' if test else 'https://pypi.org/manage/account/'

    if not pypirc.exists():
        return {'found': False, 'msg': f"No ~/.pypirc found. Create a token at {url}"}

    config = configparser.ConfigParser()
    config.read(pypirc)

    if section not in config:
        return {'found': False, 'msg': f"No [{section}] section in ~/.pypirc. Create a token at {url}"}

    password = config[section].get('password', '')
    if not password:
        return {'found': False, 'msg': f"No password in [{section}]. Create a token at {url}"}

    preview = password[:9] + '...' if password.startswith('pypi-') else '****'
    return {'found': True, 'section': section, 'username': config[section].get('username', ''), 'preview': preview, 'source': str(pypirc)}


@app.cell
def _():
    check_pypi_auth()
    return


@app.cell
def _():
    check_pypi_auth(test=0)
    return


@app.function
def publish(
    test=True  # When ready to upload to PyPi change this to false
):
    "Build and publish package to PyPI."
    platform = 'testpypi' if test else 'pypi'
    auth = check_credentials(platform)
    if not auth['found']:
        print(f"❌ {auth['msg']}")
        return

    print(f"✅ Authenticated as {auth['username']} ({auth['preview']}) from {auth['source']}")
    print("Rebuilding package from notebooks...")
    build()

    shutil.rmtree('dist', ignore_errors=True)
    print("Building distribution...")
    subprocess.run(['uv', 'build'], check=True)

    cmd = ['uv', 'publish']
    if test: cmd.extend(['--publish-url', 'https://test.pypi.org/legacy/'])
    else: cmd.extend(['--publish-url', 'https://upload.pypi.org/legacy/'])

    config = configparser.ConfigParser()
    config.read(Path.home() / '.pypirc')
    section = auth['section'] if 'section' in auth else platform
    username = config[section].get('username', '__token__')
    password = config[section].get('password', '')
    cmd.extend(['--username', username, '--password', password])

    target = 'Test PyPI' if test else 'PyPI'
    print(f"Publishing to {target}...")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Published to {target}!")
    except subprocess.CalledProcessError as e:
        if '403' in (e.stderr or ''):
            print(f"❌ Auth failed. Token may be expired. Regenerate at {CREDENTIALS[platform]['url']}")
        else:
            print(f"❌ Publish failed: {e.stderr}")


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
