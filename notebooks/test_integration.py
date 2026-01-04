import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")

with app.setup:
    from pathlib import Path
    import ast, shutil, re


@app.cell
def _():
    from marimo_dev import build, scan, read_meta, read_config, nb_name
    import pytest, inspect
    return build, inspect, nb_name, read_config, read_meta, scan


@app.cell
def _(inspect, scan):
    print(inspect.getsource(scan))
    return


@app.cell
def _(build, inspect, nb_name, read_config, read_meta):
    def test_build_respects_config(tmp_path):
        # Setup: create pyproject.toml with custom config
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
    [project]
    name = "test-pkg"
    version = "0.1.0"
    description = "Test package"

    [tool.marimo-dev]
    nbs = "my_notebooks"
    out = "my_output"
    decorators = ["app.function", "app.class_definition"]
    """)

        # Create notebook directory and copy sample notebook
        nb_dir = tmp_path / "my_notebooks"
        nb_dir.mkdir()
        notebook = nb_dir / "a_core.py"
        shutil.copy("notebooks/test_sample.py", notebook)
        print(f"Notebook content:\n{notebook.read_text()}")

        test_file = tmp_path / "my_notebooks" / "a_core.py"
        print(f"nb_name result: {nb_name(test_file, str(tmp_path))}")



        print(f"Current dir: {Path.cwd()}")
        print(f"tmp_path: {tmp_path}")

        cfg = read_config(str(tmp_path))
        print(f"Config decorators: {cfg.decorators}")

        # Build the package
        result = build(root=str(tmp_path))
        print(f"meta from read_meta: {read_meta(str(tmp_path))}")

        from marimo_dev import scan
        meta, mods = scan(str(tmp_path))
        print(f"Modules found: {[(name, len(nodes)) for name, nodes in mods]}")
        for name, nodes in mods:
            print(f"Module {name}: {[n.name for n in nodes]}")



        print((tmp_path / "my_output" / "test_pkg" / "__init__.py").read_text())

        print(f"{inspect.getsource(scan) = }")


        # Debug: see what was actually created
        print(f"Result: {result}")
        print(f"tmp_path contents: {list(tmp_path.rglob('*'))}")


        # Assert output directory was created with correct name
        output_dir = tmp_path / "my_output" / "test_pkg"
        assert output_dir.exists()
        assert (output_dir / "__init__.py").exists()
        assert (output_dir / "core.py").exists()
        assert result == str(output_dir)
    return


@app.cell
def _():
    with open('src/marimo_dev/build.py') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[9:15], start=10):
            print(f"{i}: {line}", end='')
    return


@app.cell
def _():
    import marimo as mo
    return


if __name__ == "__main__":
    app.run()
