# nbuild

Extract Python modules from marimo notebooks.

## Install
pip install m_dev

Copied!
## Usage
```python
from nbuild import build
build() # notebooks/ -> src/package_name/
```

Extracts functions/classes decorated with `@app.function` or `@app.class_definition`. Generates:
- Module files with Google-style docstrings
- `__init__.py` with version and exports
- Datastar-powered searchable docs

## Configuration

All metadata lives in `pyproject.toml`:
```toml
[project] 
  name = "your-package" 
  version = "0.1.0" 
  description = "What it does" 
  authors = [{name = "You", email = "you@example.com"}]
```
  
## Inline Documentation

Document parameters and returns with inline comments:
```python
def process( 
    data: list,      # Input records 
    limit: int = 10  # Max results
)-> dict:            # Processed output 
"Transform data records"
```

These become Google docstrings automatically.

## Publish
```python
from m_dev import publish

publish(test=True) # Test PyPI publish(test=False) # Real PyPI
```

## Preview Docs
```prthon
from m_dev import preview

preview() # http://localhost:8000
```