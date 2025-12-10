"""
Store documentation in SQLite in-memory database using apsw.
Perfect for learning how databases work in marimo!
"""
import apsw
from pathlib import Path
from simple_docs import extract_doc_items, DocItem

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

# ============================================================================
# Testing / Demo
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("DOCUMENTATION DATABASE DEMO")
    print("=" * 70)
    
    # Create in-memory database
    print("\n1. Creating in-memory database...")
    conn = create_docs_db(in_memory=True)
    print("✅ Database created")
    
    # Load test data
    print("\n2. Loading test notebooks...")
    count = load_notebooks_to_db(conn, 'test_clean/notebooks')
    print(f"✅ Loaded {count} items")
    
    # Get statistics
    print("\n3. Database statistics:")
    stats = get_stats(conn)
    print(f"   Total items: {stats['total']}")
    print(f"   By kind: {stats['by_kind']}")
    print(f"   By module: {stats['by_module']}")
    
    # Get all docs
    print("\n4. All documentation items:")
    all_docs = get_all_docs(conn)
    for doc in all_docs:
        print(f"   {doc['kind']:10} {doc['module']:10} {doc['name']}")
    
    # Search examples
    print("\n5. Search examples:")
    
    print("\n   Search: 'batch'")
    results = search_docs(conn, 'batch')
    for r in results:
        print(f"   → {r['name']} (module: {r['module']}, rank: {r['rank']})")
    
    print("\n   Search: 'process'")
    results = search_docs(conn, 'process')
    for r in results:
        print(f"   → {r['name']} (module: {r['module']}, rank: {r['rank']})")
    
    print("\n   Search: 'process AND data'")
    results = search_docs(conn, 'process AND data')
    for r in results:
        print(f"   → {r['name']} (module: {r['module']}, rank: {r['rank']})")
    
    # Filter by kind
    print("\n6. Filter by kind:")
    
    print("\n   Functions:")
    funcs = get_docs_by_kind(conn, 'function')
    for f in funcs:
        print(f"   → {f['name']} (module: {f['module']})")
    
    print("\n   Constants:")
    consts = get_docs_by_kind(conn, 'constant')
    for c in consts:
        print(f"   → {c['name']} (module: {c['module']})")
    
    # Filter by module
    print("\n7. Filter by module:")
    
    print("\n   Module: core")
    core_docs = get_docs_by_module(conn, 'core')
    for d in core_docs:
        print(f"   → {d['kind']:10} {d['name']}")
    
    print("\n" + "=" * 70)
    print("✅ Database demo complete!")
    print("=" * 70)
    
    # Close connection
    conn.close()
