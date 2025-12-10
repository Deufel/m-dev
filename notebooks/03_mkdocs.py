import marimo

__generated_with = "0.18.3"
app = marimo.App(width="full", css_file="")

with app.setup:
    import re,ast
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Optional


@app.cell
def _():
    ## Simple data structures
    return


@app.class_definition
@dataclass
class DocItem:
    """Single documentable item (function/class/constant)"""
    name:str
    module:str
    kind:str  # 'function', 'class', 'constant'
    nbdev_signature:str  # NBDEV-style with inline comments
    full_source:str      # Complete source code
    searchable:str       # All searchable text concatenated


@app.cell
def _():
    # Extract items from notebook
    return


@app.function
def extract_nbdev_signature(node,src:str)->str:
    """Extract NBDEV-style signature with inline comments"""
    if isinstance(node,ast.FunctionDef):
        return ast.get_source_segment(src,node).split('\n')[0:10]  # Get signature lines
    elif isinstance(node,ast.ClassDef):
        lines = ast.get_source_segment(src,node).split('\n')
        # Get class definition + __init__ if present
        sig_lines = [lines[0]]
        in_init = False
        for line in lines[1:]:
            if 'def __init__' in line:
                in_init = True
            if in_init:
                sig_lines.append(line)
                if line.strip() and not line.strip().startswith('#') and ':' in line:
                    break
        return '\n'.join(sig_lines)
    else:
        return ast.get_source_segment(src,node) or ''


@app.function
def make_searchable(
    name:str, 
    sig:str, 
    src:str, 
    module:str
)->str:
    """Create searchable string from all text"""
    # Extract words from signature and source
    words = []
    
    # Name and module
    words.extend(name.split('_'))
    words.extend(module.split('_'))
    
    # Extract from signature
    sig_words = re.findall(r'\w+',sig)
    words.extend(sig_words)
    
    # Extract from comments
    comments = re.findall(r'#\s*(.+)',src)
    for comment in comments:
        words.extend(re.findall(r'\w+',comment))
    
    # Extract docstring
    if '"""' in src or "'''" in src:
        doc_match = re.search(r'["\']{{3}}(.+?)["\']{{3}}',src,re.DOTALL)
        if doc_match:
            words.extend(re.findall(r'\w+',doc_match.group(1)))
    
    # Deduplicate and join
    unique_words = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        if w_lower not in seen and len(w) > 1:
            seen.add(w_lower)
            unique_words.append(w)
    
    return ' '.join(unique_words)


@app.function
def extract_doc_items(
    notebook_path:str
)->list[DocItem]:
    """Extract all documentable items from notebook"""
    p = Path(notebook_path)
    src = p.read_text()
    tree = ast.parse(src)
    module = p.stem.lstrip('0123456789_')
    
    items = []
    
    for node in tree.body:
        # Handle with blocks (marimo)
        if isinstance(node,ast.With):
            for item in node.body:
                # Constants
                if isinstance(item,ast.Assign):
                    for target in item.targets:
                        if isinstance(target,ast.Name):
                            name = target.id
                            if name.startswith('__') and not name.endswith('__'):
                                full_src = ast.unparse(item)
                                items.append(DocItem(
                                    name=name,
                                    module=module,
                                    kind='constant',
                                    nbdev_signature=full_src,
                                    full_source=full_src,
                                    searchable=make_searchable(name,full_src,full_src,module)
                                ))
        
        # Functions
        elif isinstance(node,ast.FunctionDef):
            # Check for export decorator
            if any(ast.unparse(d.func if isinstance(d,ast.Call) else d) in 
                   {'app.function','app.class_definition'} for d in node.decorator_list):
                if not node.name.startswith('test_'):
                    full_src = ast.get_source_segment(src,node) or ''
                    
                    # Get NBDEV signature (def line through first body line)
                    lines = full_src.split('\n')
                    sig_lines = []
                    for i,line in enumerate(lines):
                        sig_lines.append(line)
                        # Stop after the colon and docstring
                        if i > 0 and line.strip() and not line.strip().startswith('#'):
                            if not line.strip().startswith(('@','def','"""',"'''")):
                                break
                    nbdev_sig = '\n'.join(sig_lines)
                    
                    items.append(DocItem(
                        name=node.name,
                        module=module,
                        kind='function',
                        nbdev_signature=nbdev_sig,
                        full_source=full_src,
                        searchable=make_searchable(node.name,nbdev_sig,full_src,module)
                    ))
        
        # Classes
        elif isinstance(node,ast.ClassDef):
            if any(ast.unparse(d.func if isinstance(d,ast.Call) else d) in 
                   {'app.function','app.class_definition'} for d in node.decorator_list):
                full_src = ast.get_source_segment(src,node) or ''
                
                # Get class definition + __init__ signature
                lines = full_src.split('\n')
                sig_lines = [lines[0]]
                in_init = False
                for line in lines[1:]:
                    if 'def __init__' in line:
                        in_init = True
                    if in_init:
                        sig_lines.append(line)
                        if ')' in line and ':' in line:
                            break
                nbdev_sig = '\n'.join(sig_lines)
                
                items.append(DocItem(
                    name=node.name,
                    module=module,
                    kind='class',
                    nbdev_signature=nbdev_sig,
                    full_source=full_src,
                    searchable=make_searchable(node.name,nbdev_sig,full_src,module)
                ))
    
    return items


@app.cell
def _():
    # Generate HTML with data-star attributes
    return


@app.function
def generate_doc_html(
    items:list[DocItem]
)->str:
    """Generate HTML with data-star searchable attributes"""
    html_items = []
    
    for item in items:
        # Escape for HTML
        name_html = item.name.replace('<','&lt;').replace('>','&gt;')
        sig_html = item.nbdev_signature.replace('<','&lt;').replace('>','&gt;')
        src_html = item.full_source.replace('<','&lt;').replace('>','&gt;')
        
        # Create HTML item
        html = f'''<div class="{item.kind}" 
     data-signals="{{searchable{item.name}: '{item.searchable}', matchCount{item.name}: 0}}" 
     data-effect="$matchCount{item.name} = [...$tags, $search.trim()].filter(tag => tag.length > 0 && $searchable{item.name}.toLowerCase().includes(tag.toLowerCase())).length"
     data-show="($tags.length === 0 && $search.trim().length === 0) || $matchCount{item.name} > 0"
     data-style:order="($tags.length === 0 && $search.trim().length === 0) ? 0 : -$matchCount{item.name}">
  
  <span class="match-badge" 
        data-show="$tags.length > 0 || $search.trim().length > 0" 
        data-text="$matchCount{item.name}"></span>
  
  <div class="item-name">
    <code>{name_html}</code>
    <span class="module-badge">{item.module}</span>
  </div>
  
  <div class="signature">
    <pre><code>{sig_html}</code></pre>
  </div>
  
  <details class="source-viewer">
    <summary>View Source</summary>
    <pre><code>{src_html}</code></pre>
  </details>
  
</div>'''
        
        html_items.append(html)
    
    return '\n\n'.join(html_items)


@app.cell
def _():
    # Generate complete docs page
    return


@app.function
def generate_docs_page(
    notebooks_dir:str, 
    output_file:str='docs.html'
):
    """Generate single-page documentation with data-star search"""
    nbs_path = Path(notebooks_dir)
    all_items = []
    
    # Extract from all notebooks
    for nb_file in sorted(nbs_path.glob('*.py')):
        if nb_file.stem.startswith('.') or nb_file.stem.startswith('test'):
            continue
        items = extract_doc_items(nb_file)
        all_items.extend(items)
    
    # Generate HTML items
    items_html = generate_doc_html(all_items)
    
    # Complete page
    html = f'''<!DOCTYPE html>
<html>
<head>
  <title>Documentation</title>
  <script type="module" src="https://cdn.jsdelivr.net/npm/@sudodevnull/datastar"></script>
</head>
<body>

<div id="docs-container">
  
  <!-- Search Box -->
  <div class="search-controls">
    <input type="text" 
           placeholder="Search..." 
           data-model="$search">
  </div>
  
  <!-- Documentation Items -->
  <div class="docs-items">
{items_html}
  </div>
  
</div>

</body>
</html>'''
    
    Path(output_file).write_text(html)
    print(f"✅ Generated: {output_file}")
    return output_file


@app.cell
def _():
    # Testing

    return


@app.cell
def _():
    if __name__ == '__main__':
        # Test extraction
        test_nb = '''
    import marimo as app

    with app():
        import sys
    
        __API_URL = "https://api.example.com"

    @app.function
    def process_data(
        items:list,      # list of items to process
        batch_sz:int=10  # size of each batch
    )->list:             # processed items
        "Process items in batches"
        results = []
        for i in range(0,len(items),batch_sz):
            batch = items[i:i+batch_sz]
            results.extend([x*2 for x in batch])
        return results

    @app.class_definition
    class DataProcessor:
        "Processes data in configurable batches"
    
        def __init__(
            self,
            batch_sz:int=10  # default batch size
        ):
            self.batch_sz = batch_sz
    '''
    
        Path('test_nb.py').write_text(test_nb)
    
        items = extract_doc_items('test_nb.py')
    
        print("=" * 70)
        print("EXTRACTED DOC ITEMS")
        print("=" * 70)
    
        for item in items:
            print(f"\n{item.kind.upper()}: {item.name}")
            print(f"Module: {item.module}")
            print(f"Signature:\n{item.nbdev_signature}")
            print(f"Searchable: {item.searchable[:100]}...")
    
        # Generate HTML
        html = generate_doc_html(items)
        Path('test_docs.html').write_text(f'''<!DOCTYPE html>
    <html>
    <head>
      <script type="module" src="https://cdn.jsdelivr.net/npm/@sudodevnull/datastar"></script>
    </head>
    <body>
    <input type="text" placeholder="Search..." data-model="$search">
    {html}
    </body>
    </html>''')
    
        print("\n✅ Generated test_docs.html")
    
        # Cleanup
        Path('test_nb.py').unlink()
    return


app._unparsable_cell(
    r"""
    items = extract_doc_items('')
    
        print(\"=\" * 70)
        print(\"EXTRACTED DOC ITEMS\")
        print(\"=\" * 70)
    
        for item in items:
            print(f\"\n{item.kind.upper()}: {item.name}\")
            print(f\"Module: {item.module}\")
            print(f\"Signature:\n{item.nbdev_signature}\")
            print(f\"Searchable: {item.searchable[:100]}...\")
    
        # Generate HTML
        html = generate_doc_html(items)
    """,
    name="_"
)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
