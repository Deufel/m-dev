"""
Marimo notebook demonstrating documentation database.
Learn how databases work with reactive UI!
"""

import marimo

__generated_with = "0.18.3"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import re,ast
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Optional

    import apsw
    from pathlib import Path


@app.cell
def _():
    mo.md("""
    # 📚 Documentation Database Demo

    This notebook demonstrates how to use SQLite with apsw in marimo.
    We'll store documentation in an in-memory database and query it reactively!
    """)
    return


@app.cell
def _():
    """
    Simple documentation extraction for data-star searchable docs.
    No fancy styling - just the data you need.
    """


    # ============================================================================
    # Simple data structures
    # ============================================================================

    @dataclass
    class DocItem:
        """Single documentable item (function/class/constant)"""
        name:str
        module:str
        kind:str  # 'function', 'class', 'constant'
        nbdev_signature:str  # NBDEV-style with inline comments
        full_source:str      # Complete source code
        searchable:str       # All searchable text concatenated

    # ============================================================================
    # Extract items from notebook
    # ============================================================================

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

    def make_searchable(name:str, sig:str, src:str, module:str)->str:
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

    def extract_doc_items(notebook_path:str)->list[DocItem]:
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

    # ============================================================================
    # Generate HTML with data-star attributes
    # ============================================================================

    def generate_doc_html(items:list[DocItem])->str:
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

    # ============================================================================
    # Generate complete docs page
    # ============================================================================

    def generate_docs_page(notebooks_dir:str, output_file:str='docs.html'):
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

    # ============================================================================
    # Testing
    # ============================================================================

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
    return DocItem, extract_doc_items


@app.cell
def _(DocItem, extract_doc_items):
    """
    Store documentation in SQLite in-memory database using apsw.
    Perfect for learning how databases work in marimo!
    """


    # ============================================================================
    # Database Schema
    # ============================================================================

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        module TEXT NOT NULL,
        kind TEXT NOT NULL,
        nbdev_signature TEXT NOT NULL,
        full_source TEXT NOT NULL,
        searchable TEXT NOT NULL,
        UNIQUE(name, module)
    )
    """

    CREATE_INDEX_SQL = """
    CREATE INDEX IF NOT EXISTS idx_docs_searchable ON docs(searchable)
    """

    CREATE_FTS_SQL = """
    CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
        name, 
        module, 
        searchable,
        content='docs',
        content_rowid='id'
    )
    """

    # Trigger to keep FTS in sync
    CREATE_FTS_TRIGGER_INSERT = """
    CREATE TRIGGER IF NOT EXISTS docs_fts_insert AFTER INSERT ON docs BEGIN
        INSERT INTO docs_fts(rowid, name, module, searchable)
        VALUES (new.id, new.name, new.module, new.searchable);
    END
    """

    CREATE_FTS_TRIGGER_UPDATE = """
    CREATE TRIGGER IF NOT EXISTS docs_fts_update AFTER UPDATE ON docs BEGIN
        UPDATE docs_fts 
        SET name=new.name, module=new.module, searchable=new.searchable
        WHERE rowid=old.id;
    END
    """

    CREATE_FTS_TRIGGER_DELETE = """
    CREATE TRIGGER IF NOT EXISTS docs_fts_delete AFTER DELETE ON docs BEGIN
        DELETE FROM docs_fts WHERE rowid=old.id;
    END
    """

    # ============================================================================
    # Database Operations
    # ============================================================================

    def create_docs_db(in_memory:bool=True)->apsw.Connection:
        """
        Create documentation database with schema.
    
        Args:
            in_memory: If True, creates in-memory database. Otherwise saves to disk.
    
        Returns:
            apsw.Connection: Database connection
        """
        # Create connection
        if in_memory:
            conn = apsw.Connection(":memory:")
        else:
            conn = apsw.Connection("docs.db")
    
        cursor = conn.cursor()
    
        # Create tables
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(CREATE_INDEX_SQL)
        cursor.execute(CREATE_FTS_SQL)
    
        # Create triggers for FTS sync
        cursor.execute(CREATE_FTS_TRIGGER_INSERT)
        cursor.execute(CREATE_FTS_TRIGGER_UPDATE)
        cursor.execute(CREATE_FTS_TRIGGER_DELETE)
    
        return conn

    def insert_doc_item(conn:apsw.Connection, item:DocItem):
        """Insert a single DocItem into the database"""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO docs (name, module, kind, nbdev_signature, full_source, searchable)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item.name, item.module, item.kind, item.nbdev_signature, item.full_source, item.searchable))

    def insert_doc_items(conn:apsw.Connection, items:list[DocItem]):
        """Insert multiple DocItems into the database"""
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR REPLACE INTO docs (name, module, kind, nbdev_signature, full_source, searchable)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [(i.name, i.module, i.kind, i.nbdev_signature, i.full_source, i.searchable) for i in items])

    def load_notebooks_to_db(conn:apsw.Connection, notebooks_dir:str):
        """Load all notebooks from directory into database"""
        nbs_path = Path(notebooks_dir)
        all_items = []
    
        for nb_file in sorted(nbs_path.glob('*.py')):
            if nb_file.stem.startswith('.') or nb_file.stem.startswith('test'):
                continue
            items = extract_doc_items(nb_file)
            all_items.extend(items)
    
        insert_doc_items(conn, all_items)
        return len(all_items)

    # ============================================================================
    # Query Functions
    # ============================================================================

    def get_all_docs(conn:apsw.Connection)->list[dict]:
        """Get all documentation items"""
        cursor = conn.cursor()
        results = cursor.execute("SELECT * FROM docs ORDER BY module, kind, name").fetchall()
    
        columns = ['id', 'name', 'module', 'kind', 'nbdev_signature', 'full_source', 'searchable']
        return [dict(zip(columns, row)) for row in results]

    def search_docs(conn:apsw.Connection, query:str)->list[dict]:
        """
        Full-text search across documentation.
    
        Args:
            query: Search query (can use FTS5 syntax like "process AND batch")
    
        Returns:
            List of matching documents with rank
        """
        cursor = conn.cursor()
        results = cursor.execute("""
            SELECT 
                d.id,
                d.name,
                d.module,
                d.kind,
                d.nbdev_signature,
                d.full_source,
                d.searchable,
                rank
            FROM docs_fts
            JOIN docs d ON docs_fts.rowid = d.id
            WHERE docs_fts MATCH ?
            ORDER BY rank
        """, (query,)).fetchall()
    
        columns = ['id', 'name', 'module', 'kind', 'nbdev_signature', 'full_source', 'searchable', 'rank']
        return [dict(zip(columns, row)) for row in results]

    def get_docs_by_module(conn:apsw.Connection, module:str)->list[dict]:
        """Get all docs from a specific module"""
        cursor = conn.cursor()
        results = cursor.execute("""
            SELECT * FROM docs 
            WHERE module = ?
            ORDER BY kind, name
        """, (module,)).fetchall()
    
        columns = ['id', 'name', 'module', 'kind', 'nbdev_signature', 'full_source', 'searchable']
        return [dict(zip(columns, row)) for row in results]

    def get_docs_by_kind(conn:apsw.Connection, kind:str)->list[dict]:
        """Get all docs of a specific kind (function/class/constant)"""
        cursor = conn.cursor()
        results = cursor.execute("""
            SELECT * FROM docs 
            WHERE kind = ?
            ORDER BY module, name
        """, (kind,)).fetchall()
    
        columns = ['id', 'name', 'module', 'kind', 'nbdev_signature', 'full_source', 'searchable']
        return [dict(zip(columns, row)) for row in results]

    def get_stats(conn:apsw.Connection)->dict:
        """Get statistics about the documentation database"""
        cursor = conn.cursor()
    
        total = cursor.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
    
        by_kind = cursor.execute("""
            SELECT kind, COUNT(*) as count
            FROM docs
            GROUP BY kind
            ORDER BY count DESC
        """).fetchall()
    
        by_module = cursor.execute("""
            SELECT module, COUNT(*) as count
            FROM docs
            GROUP BY module
            ORDER BY count DESC
        """).fetchall()
    
        return {
            'total': total,
            'by_kind': dict(by_kind),
            'by_module': dict(by_module)
        }

    # ============================================================================
    # Marimo-Friendly Functions
    # ============================================================================

    def create_and_load_db(notebooks_dir:str, in_memory:bool=True)->tuple[apsw.Connection, dict]:
        """
        Create database and load notebooks.
        Returns connection and stats - perfect for marimo!
    
        Usage in marimo:
            conn, stats = create_and_load_db('notebooks')
            mo.md(f"Loaded {stats['total']} items")
        """
        conn = create_docs_db(in_memory)
        count = load_notebooks_to_db(conn, notebooks_dir)
        stats = get_stats(conn)
        return conn, stats

    def search_to_html(conn:apsw.Connection, query:str)->str:
        """
        Search and return HTML for marimo display.
    
        Usage in marimo:
            search_input = mo.ui.text(label="Search")
            results_html = search_to_html(conn, search_input.value)
            mo.Html(results_html)
        """
        if not query or not query.strip():
            docs = get_all_docs(conn)
        else:
            docs = search_docs(conn, query)
    
        html_parts = []
        for doc in docs:
            html_parts.append(f"""
    <div class="{doc['kind']}">
        <div class="item-name">
            <code>{doc['name']}</code>
            <span class="module-badge">{doc['module']}</span>
        </div>
        <div class="signature">
            <pre><code>{doc['nbdev_signature']}</code></pre>
        </div>
        <details class="source-viewer">
            <summary>View Source</summary>
            <pre><code>{doc['full_source']}</code></pre>
        </details>
    </div>
            """)
    
        return '\n'.join(html_parts)


    return create_and_load_db, get_all_docs, get_docs_by_kind, search_docs


@app.cell
def _(create_and_load_db):
    mo.md("## 1. Create Database and Load Data")

    # Create database and load notebooks
    conn, stats = create_and_load_db('./notebooks', in_memory=True)

    mo.md(f"""
    ✅ **Database created!**

    - Total items: **{stats['total']}**
    - Functions: **{stats['by_kind'].get('function', 0)}**
    - Classes: **{stats['by_kind'].get('class', 0)}**
    - Constants: **{stats['by_kind'].get('constant', 0)}**
    - Modules: **{list(stats['by_module'].keys())}**
    """)
    return conn, stats


@app.cell
def _():
    mo.md("## 2. Interactive Search")

    # Create search input
    search_input = mo.ui.text(
        label="Search documentation",
        placeholder="Try: batch, process, data, validate...",
        full_width=True
    )
    search_input
    return (search_input,)


@app.cell
def _(conn, get_all_docs, search_docs, search_input):
    # Get search results
    if search_input.value and search_input.value.strip():
        search_results = search_docs(conn, search_input.value)
    else:
        search_results = get_all_docs(conn)

    mo.md(f"**Found {len(search_results)} items**")
    return (search_results,)


@app.cell
def _(search_results):
    # Display results
    if not search_results:
        mo.md("*No results found*")
    else:
        result_cards = []
        for doc in search_results:
            rank_info = f" (rank: {doc['rank']:.2f})" if 'rank' in doc else ""

            card_html = f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
        <div style="font-weight: bold; margin-bottom: 8px;">
            {doc['name']} - {doc['module']}{rank_info}
        </div>
    
        <div style="margin-bottom: 8px;">
            <strong>Kind:</strong> <code>{doc['kind']}</code><br>
            <strong>Module:</strong> <code>{doc['module']}</code>
        </div>
    
        <details>
            <summary style="cursor: pointer; font-weight: bold; margin-bottom: 8px;">
                View Signature
            </summary>
            <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto;"><code>{doc['nbdev_signature']}</code></pre>
        </details>
    
        <details>
            <summary style="cursor: pointer; font-weight: bold; margin-top: 8px;">
                View Full Source
            </summary>
            <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto;"><code>{doc['full_source']}</code></pre>
        </details>
    </div>
    """
            result_cards.append(mo.Html(card_html))

    mo.vstack(result_cards)
    return


@app.cell
def _():
    mo.md("## 3. Filter by Kind")

    # Create kind selector
    kind_selector = mo.ui.dropdown(
        options=['all', 'function', 'class', 'constant'],
        value='all',
        label="Filter by type"
    )
    kind_selector
    return (kind_selector,)


@app.cell
def _(conn, get_all_docs, get_docs_by_kind, kind_selector):
    # Get filtered docs
    if kind_selector.value == 'all':
        kind_filtered = get_all_docs(conn)
    else:
        kind_filtered = get_docs_by_kind(conn, kind_selector.value)

    mo.md(f"**{len(kind_filtered)} {kind_selector.value}(s)**")
    return (kind_filtered,)


@app.cell
def _(kind_filtered):
    # Display as table
    if kind_filtered:
        table_data = [
            {
                'Name': doc['name'],
                'Module': doc['module'],
                'Kind': doc['kind']
            }
            for doc in kind_filtered
        ]
        mo.ui.table(table_data)
    else:
        mo.md("*No items*")
    return


@app.cell
def _(stats):
    mo.md("## 4. Module Statistics")

    # Show module breakdown
    module_stats = []
    for module, _count in stats['by_module'].items():
        module_stats.append(f"- **{module}**: {_count} items")

    mo.md('\n'.join(module_stats))
    return


@app.cell
def _():
    mo.md("## 5. Direct SQL Queries")

    # Create SQL input
    sql_input = mo.ui.text_area(
        label="Run custom SQL",
        value="SELECT name, module, kind FROM docs WHERE kind = 'function' LIMIT 5",
        full_width=True
    )

    sql_button = mo.ui.button(label="Execute Query")

    mo.vstack([sql_input, sql_button])
    return sql_button, sql_input


@app.cell
def _(conn, sql_button, sql_input):
    # Execute custom SQL
    if sql_button.value:
        try:
            cursor = conn.cursor()
            results = cursor.execute(sql_input.value).fetchall()

            if results:
                # Convert to list of dicts
                if results[0]:
                    # Get column names from cursor description
                    columns = [desc[0] for desc in cursor.getdescription()]
                    _table_data = [dict(zip(columns, row)) for row in results]
                    mo.ui.table(_table_data)
                else:
                    mo.md("*Query returned no results*")
            else:
                mo.md("*Query executed successfully (no results)*")
        except Exception as e:
            mo.md(f"**Error:** {str(e)}")
    return


@app.cell
def _():
    mo.md("""
    ## 6. Key Concepts Learned

    ### Database Operations:
    - ✅ Creating in-memory SQLite database with `apsw`
    - ✅ Defining schema with tables and indexes
    - ✅ Using FTS5 (Full-Text Search) for fast searching
    - ✅ INSERT, SELECT, and complex queries
    - ✅ Triggers to keep FTS index in sync

    ### Marimo Integration:
    - ✅ Reactive queries based on UI inputs
    - ✅ Database persists across cell re-runs
    - ✅ Interactive search and filtering
    - ✅ Custom SQL execution

    ### Advanced Features:
    - ✅ Full-text search with ranking
    - ✅ Indexes for fast lookups
    - ✅ Aggregation queries (stats)
    - ✅ Filtering and sorting
    """)
    return


@app.cell
def _():
    mo.md("""
    ## 💡 Try These Queries:

    **Search:**
    - `batch` - Find items mentioning batch processing
    - `process AND data` - Boolean search
    - `validate` - Find validation functions

    **SQL:**
    ```sql
    -- Count by module
    SELECT module, COUNT(*) as count
    FROM docs
    GROUP BY module;

    -- Search in searchable text
    SELECT name, module
    FROM docs
    WHERE searchable LIKE '%process%';

    -- Get all functions
    SELECT name, module
    FROM docs
    WHERE kind = 'function';
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
