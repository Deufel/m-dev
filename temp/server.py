import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    from sse_starlette import EventSourceResponse
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import HTMLResponse
    import asyncio
    from datetime import datetime
    import uvicorn
    import multiprocessing
    import json
    from fastcore.xml import to_xml, Div, __all__

    import marimo as mo
    return (
        Div,
        EventSourceResponse,
        HTMLResponse,
        Route,
        Starlette,
        asyncio,
        datetime,
        json,
        mo,
        to_xml,
    )


@app.cell
def _(Div, to_xml):
    def ds_patch_elements(*elms): return {"event": "datastar-patch-elements", "data": f"elements {to_xml(elms[0] if len(elms)==1 else Div(*elms))}"}
    return (ds_patch_elements,)


@app.cell
def _(json):
    def ds_patch_signals(sigs): return {"event": "datastar-patch-signals", "data": f"signals {json.dumps(sigs) if isinstance(sigs, dict) else sigs}"}
    return (ds_patch_signals,)


@app.cell
def _(Body, Button, Div, H1, HTMLResponse, Head, Hr, Html, Script, Title):
    async def home(request):
        page = Html(
            Head(
                Title("Datastar + SSE"),
                Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-RC.7/bundles/datastar.js")
            ),
            Body(**{"data-signals": "{time: '--:--:--'}"})(
                H1("Datastar SSE Demo"),
                Div(
                    Button(**{"data-on:click": "@get('/counter')"})("Start Counter"),
                    Div(id="counter")("Ready"),
                    Hr(),
                    Button(**{"data-on:click": "@get('/time')"})("Live Time"),
                    Div(**{"data-text": "$time"}),
                    Button(**{"data-on:click": "window.location.reload()"})("Stop")
                )
            )
        )
        return HTMLResponse(page)
    return (home,)


@app.cell
def _(Div, EventSourceResponse, asyncio, ds_patch_elements):
    async def counter(request):
        async def gen():
            for i in range(10):
                if await request.is_disconnected(): break
                yield ds_patch_elements(Div(id="counter")(f"Count: {i}"))
                await asyncio.sleep(1)
        return EventSourceResponse(gen(), ping=15)
    return (counter,)


@app.cell
def _(EventSourceResponse, asyncio, datetime, ds_patch_signals):
    async def time_stream(request):
        async def gen():
            while True:
                if await request.is_disconnected(): break
                yield ds_patch_signals(dict(time=datetime.now().strftime('%H:%M:%S')))
                await asyncio.sleep(1)
        return EventSourceResponse(gen(), ping=15)
    return (time_stream,)


@app.cell
def _(Route, Starlette, counter, home, time_stream):
    myapp = Starlette(routes=[
        Route('/', home),
        Route('/counter', counter),
        Route('/time', time_stream)
    ])
    return (myapp,)


@app.cell
def _():
    from fasthtml.jupyter import JupyUvi, JupyUviAsync
    return (JupyUvi,)


@app.cell
def _(mo):
    server_switch = mo.ui.switch(label="FastHTML Server")
    get_server, set_server = mo.state(None)

    return get_server, server_switch, set_server


@app.cell
def _(JupyUvi, get_server, myapp, server_switch, set_server):
    if server_switch.value:
        # Start server only if not already running
        if get_server() is None:
            server = JupyUvi(myapp, port=8000)
            set_server(server)
            status = "Server started at http://localhost:8000"
        else:
            status = "Server already running at http://localhost:8000"
    else:
        # Stop server if running
        current_server = get_server()
        if current_server is not None:
            current_server.stop()
            set_server(None)
            status = "Server stopped"
        else:
            status = "Server already stopped"
    return (status,)


@app.cell
def _(mo, server_switch, status):
    _status = mo.md(f"**Status:** {status}")
    mo.vstack([ server_switch, _status])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
