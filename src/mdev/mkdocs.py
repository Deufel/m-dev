import re, ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class DocItem:
    """
    Single documentable item (function/class/constant)

    Attributes:
        name (str): TODO
        module (str): TODO
        kind (str): 'function', 'class', 'constant'
        nbdev_signature (str): NBDEV-style with inline comments
        full_source (str): Complete source code
        searchable (str): All searchable text concatenated

    """
    name:str
    module:str
    kind:str
    nbdev_signature:str
    full_source:str
    searchable:str

def extract_nbdev_signature(node,src: str) -> str:
    """
    Extract NBDEV-style signature with inline comments

    Args:
        node: TODO
        src (str): TODO

    Returns:
        str: The return value.

    """
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

def make_searchable(name: str, sig: str, src: str, module: str) -> str:
    """
    Create searchable string from all text

    Args:
        name (str): TODO
        sig (str): TODO
        src (str): TODO
        module (str): TODO

    Returns:
        str: The return value.

    """
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

def extract_doc_items(notebook_path: str) -> list[DocItem]:
    """
    Extract all documentable items from notebook

    Args:
        notebook_path (str): TODO

    Returns:
        list[DocItem]: The return value.

    """
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

def generate_doc_html(items: list[DocItem]) -> str:
    """
    Generate HTML with data-star searchable attributes

    Args:
        items (list[DocItem]): TODO

    Returns:
        str: The return value.

    """
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

def generate_docs_page(notebooks_dir: str, output_file: str='docs.html'):
    """
    Generate single-page documentation with data-star search

    Args:
        notebooks_dir (str): TODO
        output_file (str) (default: 'docs.html'): TODO

    """
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
