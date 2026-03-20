import marimo

__generated_with = "0.21.1"
app = marimo.App()

with app.setup:
    import pytest, ast
    from pathlib import Path
    from a_core import Kind, Node, Config, Param
    from b_read import parse_node, parse_file, parse_params, parse_ret, parse_hash_pipe, nb_name, scan
    from c_pkg import write_mod, write_init, clean, rewrite_imports



@app.function
def parse(src, cfg=None):
    if cfg is None: cfg = Config()
    return list(n for node in ast.parse(src).body for n in parse_node(node, src, cfg))


@app.cell
def _():
    # === Imports ===

    def test_import_simple(): 
        nodes = parse("with app.setup:\n    import ast")
        assert nodes[0].kind == Kind.IMP

    def test_import_from():
        nodes = parse("with app.setup:\n    from pathlib import Path")
        assert nodes[0].kind == Kind.IMP and 'Path' in nodes[0].src

    def test_import_multiple():
        nodes = parse("with app.setup:\n    import ast, re\n    from pathlib import Path")
        assert len([n for n in nodes if n.kind == Kind.IMP]) == 2

    # === Constants ===

    def test_const_in_setup():
        nodes = parse("with app.setup:\n    X = 42")
        assert nodes[0].kind == Kind.CONST and nodes[0].name == 'X'

    # === Exports ===

    def test_export_function():
        src = '@app.function\ndef greet(name):\n    "Say hello"\n    return f"Hello, {name}!"'
        nodes = parse(src)
        assert len(nodes) == 1 and nodes[0].kind == Kind.EXP and nodes[0].name == 'greet'

    def test_export_class():
        src = '@app.class_definition\nclass Foo:\n    "A foo"\n    x: int = 0'
        nodes = parse(src)
        assert nodes[0].kind == Kind.EXP and nodes[0].name == 'Foo'

    def test_export_preserves_docstring():
        src = '@app.function\ndef add(a, b):\n    "Add two numbers"\n    return a + b'
        nodes = parse(src)
        assert nodes[0].doc == 'Add two numbers'

    def test_export_named_cell():
        src = '@app.cell\ndef export_main():\n    if __name__ == "__main__":\n        main()\n    return'
        nodes = parse(src)
        assert len(nodes) == 1 and nodes[0].kind == Kind.EXP

    def test_test_prefix_skipped():
        src = '@app.function\ndef test_something():\n    pass'
        assert parse(src) == []

    # === Hash pipes ===

    def test_hash_pipe_internal():
        src = '@app.function\n#| internal\ndef helper():\n    pass'
        nodes = parse(src)
        assert 'internal' in nodes[0].hash_pipes

    def test_hash_pipe_nodoc():
        src = '@app.function\n#| nodoc\ndef helper():\n    pass'
        nodes = parse(src)
        assert 'nodoc' in nodes[0].hash_pipes

    def test_hash_pipe_multiple():
        src = '@app.function\n#| nodoc internal\ndef helper():\n    pass'
        nodes = parse(src)
        assert 'nodoc' in nodes[0].hash_pipes and 'internal' in nodes[0].hash_pipes

    # === Raw cells ===

    def test_raw_kind_exists(): assert Kind.RAW.value == 'raw'

    def test_raw_cellparsed():
        src = '@app.cell\ndef _():\n    #| raw\n    def __getattr__(name):\n        return name\n    return'
        nodes = parse(src)
        assert len(nodes) == 1 and nodes[0].kind == Kind.RAW

    def test_raw_cell_strips_wrapper():
        src = '@app.cell\ndef _():\n    #| raw\n    def __getattr__(name):\n        return name\n    return'
        nodes = parse(src)
        assert 'def __getattr__' in nodes[0].src
        assert '@app.cell' not in nodes[0].src
        assert '#| raw' not in nodes[0].src

    def test_raw_cell_preserves_content():
        src = '@app.cell\ndef _():\n    #| raw\n    X = 42\n    Y = "hello"\n    return'
        nodes = parse(src)
        assert 'X = 42' in nodes[0].src and 'Y = "hello"' in nodes[0].src

    def test_raw_cell_empty_skipped():
        src = '@app.cell\ndef _():\n    #| raw\n    return'
        assert not any(n.kind == Kind.RAW for n in parse(src))

    def test_raw_not_triggered_without_directive():
        src = '@app.cell\ndef _():\n    x = 1\n    return'
        assert not any(n.kind == Kind.RAW for n in parse(src))

    def test_raw_not_in_exports():
        n = Node(Kind.RAW, '_raw', 'def __getattr__(name): pass')
        assert n.kind != Kind.EXP

    # === Params ===

    def test_params_with_annotations():
        src = '@app.function\ndef add(a:int, b:int):\n    return a + b'
        nodes = parse(src)
        assert len(nodes[0].params) == 2
        assert nodes[0].params[0].anno == 'int'

    def test_params_with_defaults():
        src = '@app.function\ndef greet(name:str="World"):\n    return name'
        nodes = parse(src)
        assert nodes[0].params[0].default == "'World'"

    def test_return_annotation():
        src = '@app.function\ndef add(a, b)->int:\n    return a + b'
        nodes = parse(src)
        assert nodes[0].ret[0] == 'int'

    # === Clean ===

    def test_clean_strips_decorator(): assert '@app.function' not in clean('@app.function\ndef f(): pass')

    def test_clean_strips_hash_pipe(): assert '#|' not in clean('@app.function\n#| internal\ndef f(): pass')

    def test_clean_preserves_body(): assert 'return 42' in clean('@app.function\ndef f():\n    return 42')

    # === Rewrite imports ===

    def test_rewrite_cross_notebook(): assert rewrite_imports('from a_core import greet', ['core']) == 'from .core import greet'

    def test_rewrite_leaves_external(): assert rewrite_imports('from pathlib import Path', ['core']) == 'from pathlib import Path'

    def test_rewrite_leaves_relative(): assert rewrite_imports('from .core import greet', ['core']) == 'from .core import greet'

    # === Write mod ===

    def test_write_mod_all_kinds(tmp_path):
        nodes = [
            Node(Kind.IMP, '', 'import ast'),
            Node(Kind.CONST, 'X', 'X = 42'),
            Node(Kind.EXP, 'greet', '@app.function\ndef greet(): pass'),
            Node(Kind.RAW, '_raw', 'def __getattr__(name): return name'),
        ]
        write_mod(tmp_path / 'out.py', nodes, [])
        content = (tmp_path / 'out.py').read_text()
        assert 'import ast' in content
        assert 'X = 42' in content
        assert 'def greet' in content
        assert 'def __getattr__' in content
        assert '@app.function' not in content

    # === Write init ===

    def test_write_init_exports(tmp_path):
        meta = dict(name='my-pkg', version='1.0.0', desc='test', author='Test', license='MIT', urls={})
        nodes = [Node(Kind.EXP, 'greet', 'def greet(): pass')]
        mods = [('core', nodes)]
        write_init(tmp_path / '__init__.py', meta, mods)
        content = (tmp_path / '__init__.py').read_text()
        assert 'from .core import greet' in content
        assert '"greet"' in content

    def test_write_init_skips_internal(tmp_path):
        meta = dict(name='my-pkg', version='1.0.0', desc='test', author='Test', license='MIT', urls={})
        nodes = [Node(Kind.EXP, 'helper', 'def helper(): pass', hash_pipes=['internal'])]
        mods = [('core', nodes)]
        write_init(tmp_path / '__init__.py', meta, mods)
        content = (tmp_path / '__init__.py').read_text()
        assert 'helper' not in content

    # === Notebook naming ===

    def test_nb_name_strips_prefix(): assert nb_name(Path('a_core.py')) == 'core'

    def test_nb_name_skips_xx(): assert nb_name(Path('XX_draft.py')) is None

    def test_nb_name_skips_test(): assert nb_name(Path('test_core.py')) is None

    return


if __name__ == "__main__":
    app.run()
