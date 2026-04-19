from .server import app
from py_sse import serve
serve(app)
