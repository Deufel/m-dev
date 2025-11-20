import marimo

__generated_with = "0.17.8"
app = marimo.App(width="full")

with app.setup:
    from fastcore.xml import Head, Script, Body, Html, Iframe, to_xml, Div, Title, Style
    import marimo as mo
    from pathlib import Path


@app.function
def write_to_docs(
    content,                             # FTs
    filepath: str = "./docs/index.html", # filepath
    title: str = "docs"                  # document title
) -> str:                                # file:// URI string
    """Save content as a standalone Datastar-ready HTML file and return the absolute path as string"""
    
    html_string = to_xml(
        Html(
            Head(
                Title(title),
                Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.6/bundles/datastar.js"),
                Style("""
      * {
        scrollbar-gutter: stable;
      }
      body{
        font-family:sans-serif;
        max-width:1400px;
        margin:1rem auto;
        padding:0 1rem;
        line-height:1.5;
      }
      .header{
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        margin-bottom:1rem;
        gap:2rem;
      }
      .title-section{
        flex:1;
      }
      .search-section{
        position:fixed;
        top:1rem;
        right:1rem;
        z-index:100;
        display:flex;
        gap:0.5rem;
        align-items:center;
        background:white;
        padding:0.75rem;
        border-radius:0.5rem;
        box-shadow:0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
      }
      .content-wrapper{
        display:grid;
        grid-template-columns:250px 1fr;
        gap:2rem;
      }
      .main-content{
        min-width:0;
      }
      .sidenav{
        position:sticky;
        top:1rem;
        height:fit-content;
        max-height:calc(100vh - 2rem);
        overflow-y:auto;
        padding:1rem;
        background:#f9fafb;
        border-radius:0.375rem;
        border:1px solid #e5e7eb;
      }
      .sidenav h3{
        margin:0 0 0.75rem 0;
        font-size:0.875rem;
        font-weight:600;
        color:#6b7280;
        text-transform:uppercase;
      }
      .nav-item{
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding:0.5rem;
        margin-bottom:0.25rem;
        border-radius:0.25rem;
        font-size:0.875rem;
        color:#374151;
        text-decoration:none;
        transition:all 0.15s;
      }
      .nav-item:hover{
        background:#e5e7eb;
      }
      .nav-item.disabled{
        opacity:0.4;
        cursor:not-allowed;
        pointer-events:none;
      }
      .nav-badge{
        background:#3b82f6;
        color:white;
        padding:0.125rem 0.5rem;
        border-radius:9999px;
        font-size:0.7rem;
        font-weight:600;
        min-width:1.5rem;
        text-align:center;
      }
      .attribute-name{font-weight:bold;font-size:1.25rem;margin-bottom:0.25rem;color:#1e40af}
      .description{margin:0.5rem 0;color:#374151;font-size:0.9rem}
      .attributes{display:flex;flex-direction:column;gap:1rem}
      .attribute{
        position:relative;
        padding:1rem;
        border:1px solid #e5e7eb;
        border-radius:0.375rem;
        background:#fff;
        scroll-margin-top:3rem;
        transition: order 0.5s cubic-bezier(0.4, 0, 0.2, 1), 
                    transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
                    opacity 0.3s ease-in-out;
      }
      .attribute:hover{box-shadow:0 2px 4px rgba(0,0,0,0.1)}
      input{padding:0.625rem;border:1px solid #d1d5db;border-radius:0.375rem;min-width:250px;font-size:0.95rem}
      input:focus{outline:2px solid #3b82f6;outline-offset:0}
      .debug{
        margin-bottom:1rem;
        padding:0.75rem;
        background:#f3f4f6;
        font-family:monospace;
        font-size:0.8rem;
        border-radius:0.375rem;
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:1rem;
      }
      .debug-info{
        flex:1;
      }
      .match-badge{
        position:absolute;
        top:1rem;
        right:1rem;
        background:#3b82f6;
        color:white;
        padding:0.25rem 0.75rem;
        border-radius:9999px;
        font-size:0.8rem;
        font-weight:600;
      }
      button{
        padding:0.625rem 1.25rem;
        background:#3b82f6;
        color:white;
        border:none;
        border-radius:0.375rem;
        cursor:pointer;
        font-size:0.95rem;
        transition:background 0.15s;
        white-space:nowrap;
      }
      button:hover{background:#2563eb}
      button:active{background:#1d4ed8}
      button.clear-btn{
        background:#dc2626;
      }
      button.clear-btn:hover{
        background:#b91c1c;
      }
      code{background:#f3f4f6;color:#1f2937;padding:0.125rem 0.375rem;border-radius:0.25rem;font-size:0.85rem;font-family:monospace}
      h1{color:#111827;margin:0 0 0.25rem 0;font-size:1.75rem}
      .subtitle{color:#6b7280;margin:0;font-size:0.9rem}
      pre{background:#1f2937;color:#f9fafb;padding:0.75rem;border-radius:0.375rem;overflow-x:auto;font-size:0.8rem;margin:0.375rem 0}
      pre code{background:transparent;color:#f9fafb;padding:0}
      """
        )
            ),
            Body(content)
        )
    )
    
    path = Path(filepath).resolve()           # clean absolute Path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_string, encoding="utf-8")
    
    return path.as_uri()


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
