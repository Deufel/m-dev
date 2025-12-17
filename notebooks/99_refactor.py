import marimo

__generated_with = "0.18.3"
app = marimo.App(width="full")

with app.setup:
    import ast, re
    from pathlib import Path
    from dataclasses import dataclass


@app.cell
def _():
    # Parse a Python file
    with open('./notebooks/01_core.py', 'r') as f:
        tree = ast.parse(f.read())

    # Walk through the tree
    for node in ast.walk(tree):
        # Check for function or class definitions
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            # Check decorators
            for decorator in node.decorator_list:
                print(f"{node.name} has decorator: {ast.unparse(decorator)}")
    return (tree,)


@app.cell
def _(tree):
    tree
    return


@app.cell
def _():
    return


@app.cell
def _():
    def extract_sources(nb_path):
        with open(nb_path, 'r') as f: source = f.read()
        tree = ast.parse(source)
        results = [node for node in ast.walk(tree) 
                   if isinstance(node, (ast.FunctionDef, ast.ClassDef)) 
                   and any(isinstance(d, ast.Attribute) and d.value.id == 'app' and d.attr in ['function', 'class_definition'] 
                           for d in node.decorator_list)]
        def get_source(node):
            src = ast.get_source_segment(source, node)
            lines = src.split('\n')
            filtered = []
            for l in lines:
                stripped = l.strip()
                if stripped.startswith('@app.function') or stripped.startswith('@app.class_definition'): continue
                filtered.append(l)
            return '\n'.join(filtered)
        return [get_source(node) for node in results]

    extract_sources('./notebooks/01_core.py')

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
