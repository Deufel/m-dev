import marimo

__generated_with = "0.18.2"
app = marimo.App(width="full")

with app.setup:
    import apsw
    import threading
    import queue

    from dataclasses import dataclass
    from typing import Protocol, Any, ClassVar, Callable
    from abc import ABC, abstractmethod
    from collections import defaultdict
    from time import time
    import weakref

    from dataclasses import dataclass, field
    from time import time

    from fasthtml.core import FastHTML

    from mdev.ft_ds import setup_tags
    from fastcore.xml import attrmap, to_xml, FT




@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CQRS Test Notebook
    """)
    return


@app.cell
def _():
    import marimo as mo
    setup_tags() # Get HTML tags
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Commands
    Things that change state
    """)
    return


@app.cell
def _():
    @dataclass
    class Command:
        """Base command"""
        pass

    @dataclass
    class CreateUser(Command):
        name: str
        email: str

    @dataclass
    class UpdateUserStatus(Command):
        user_id: int
        status: str

    @dataclass
    class DeleteUser(Command):
        user_id: int
    return Command, CreateUser, DeleteUser, UpdateUserStatus


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Events
    Things the happened
    """)
    return


@app.cell
def _():
    @dataclass
    class Event:
        """Base event - timestamp auto-generated"""
        timestamp: float = field(default_factory=time, init=False)

    @dataclass
    class UserCreated(Event):
        user_id: int
        name: str
        email: str
        status: str = 'active'

    @dataclass
    class UserStatusUpdated(Event):
        user_id: int
        old_status: str
        new_status: str

    @dataclass
    class UserDeleted(Event):
        user_id: int

    # Usage - timestamp is automatic:
    event = UserCreated(user_id=123, name="Mike", email="mike@ex.com")
    print(event.timestamp)  # Auto-generated
    return Event, UserCreated, UserDeleted, UserStatusUpdated


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simpel Connection Pool
    """)
    return


@app.cell
def _():
    class ConnectionPool:
        """Thread-safe APSW connection pool"""
    
        def __init__(
            self, 
            db_path: str, 
            pool_size: int = 5,
            timeout: float = 5.0,
            wal_mode: bool = True
        ):
            self._db_path = db_path
            self._pool_size = pool_size
            self._timeout = timeout
            self._wal_mode = wal_mode
        
            # Pool management
            self._available: queue.Queue[apsw.Connection] = queue.Queue(maxsize=pool_size)
            self._all_connections: weakref.WeakSet[apsw.Connection] = weakref.WeakSet()
            self._lock = threading.Lock()
            self._closed = False
        
            # Initialize pool
            self._initialize_pool()
    
        def _initialize_pool(self):
            """Private: Create initial connections"""
            for _ in range(self._pool_size):
                conn = self._create_connection()
                self._available.put(conn)
                self._all_connections.add(conn)
    
        def _create_connection(self) -> apsw.Connection:
            """Private: Create a new APSW connection"""
            conn = apsw.Connection(self._db_path)
        
            # Enable WAL mode for better concurrency
            if self._wal_mode:
                conn.execute("PRAGMA journal_mode=WAL")
        
            # Performance tuning
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            conn.execute("PRAGMA temp_store=MEMORY")
        
            # Foreign keys
            conn.execute("PRAGMA foreign_keys=ON")
        
            return conn
    
        def acquire(self) -> apsw.Connection:
            """Public: Get connection from pool"""
            if self._closed:
                raise RuntimeError("Pool is closed")
        
            try:
                conn = self._available.get(timeout=self._timeout)
                return conn
            except queue.Empty:
                raise RuntimeError(
                    f"Failed to acquire connection within {self._timeout}s. "
                    f"Pool exhausted (size={self._pool_size})"
                )
    
        def release(self, conn: apsw.Connection):
            """Public: Return connection to pool"""
            if self._closed:
                conn.close()
                return
        
            # Check if connection is still valid
            try:
                conn.execute("SELECT 1")
                self._available.put(conn, block=False)
            except (apsw.Error, queue.Full):
                # Connection broken or pool full - close it
                conn.close()
                self._all_connections.discard(conn)
            
                # Create a new one if pool not full
                if not self._closed and self._available.qsize() < self._pool_size:
                    new_conn = self._create_connection()
                    self._available.put(new_conn)
                    self._all_connections.add(new_conn)
    
        def close(self):
            """Public: Close all connections"""
            with self._lock:
                self._closed = True
            
                # Close all available connections
                while not self._available.empty():
                    try:
                        conn = self._available.get_nowait()
                        conn.close()
                    except queue.Empty:
                        break
            
                # Close any remaining connections
                for conn in list(self._all_connections):
                    try:
                        conn.close()
                    except:
                        pass
    
        def __enter__(self):
            """Context manager: acquire connection"""
            return self.acquire()
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            """Context manager: release connection"""
            # Note: This only works if you store the connection
            # Better to use the connection() context manager below
            pass
    
        def connection(self):
            """Public: Get a context manager for a connection"""
            return _ConnectionContext(self)
    
        def execute(self, sql: str, bindings=None):
            """Public: Execute SQL with automatic connection management"""
            with self.connection() as conn:
                return conn.execute(sql, bindings or ())
    
        def __del__(self):
            """Cleanup on deletion"""
            self.close()

    class _ConnectionContext:
        """Context manager for connections"""
    
        def __init__(self, pool: ConnectionPool):
            self._pool = pool
            self._conn = None
    
        def __enter__(self) -> apsw.Connection:
            self._conn = self._pool.acquire()
            return self._conn
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._conn:
                self._pool.release(self._conn)
            return False
    return (ConnectionPool,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Event Bus
    """)
    return


@app.cell
def _():
    @dataclass
    class DBEvent:
        """Database change event (for backwards compatibility)"""
        table: str
        operation: str
        record_id: int
        data: dict | None = None
        timestamp: float = field(default_factory=time)

    class EventBus:
        """Thread-safe event bus for pub/sub"""
    
        def __init__(self):
            self._subscribers: defaultdict[str, list[Callable]] = defaultdict(list)
            self._queue: queue.Queue[DBEvent] = queue.Queue()
            self._lock = threading.Lock()
    
        def subscribe(self, event_type: str, callback: Callable[[DBEvent], None]):
            """Public: Subscribe to event type pattern
        
            Examples:
                bus.subscribe('users.update', handler)  # Specific event
                bus.subscribe('users.*', handler)        # All user events
                bus.subscribe('*', handler)              # All events
            """
            with self._lock:
                self._subscribers[event_type].append(callback)
    
        def unsubscribe(self, event_type: str, callback: Callable):
            """Public: Unsubscribe from event type"""
            with self._lock:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
    
        def publish(self, event: DBEvent):
            """Public: Publish event to subscribers"""
            # Match against patterns
            event_types = [
                f"{event.table}.{event.operation.lower()}",  # users.update
                f"{event.table}.*",                           # users.*
                "*"                                           # *
            ]
        
            with self._lock:
                callbacks = []
                for event_type in event_types:
                    callbacks.extend(self._subscribers[event_type])
        
            # Execute callbacks outside lock to avoid deadlock
            for callback in callbacks:
                try:
                    callback(event)
                except Exception as e:
                    # Log but don't crash
                    print(f"Error in event subscriber: {e}")
    
        def emit(self, table: str, operation: str, record_id: int, data: dict = None):
            """Public: Convenience method to create and publish event"""
            event = DBEvent(table, operation, record_id, data)
            self.publish(event)
            self._queue.put(event)
    
        def get_event(self, timeout: float = None) -> DBEvent | None:
            """Public: Get next event from queue (blocking)"""
            try:
                return self._queue.get(timeout=timeout)
            except queue.Empty:
                return None
    
        def clear_subscribers(self):
            """Public: Remove all subscribers (useful for testing)"""
            with self._lock:
                self._subscribers.clear()
    return (EventBus,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Command Handlers
    execute commands, emit events
    """)
    return


@app.cell
def _(
    Command,
    ConnectionPool,
    CreateUser,
    DeleteUser,
    Event,
    UpdateUserStatus,
    UserCreated,
    UserDeleted,
    UserStatusUpdated,
):
    class CommandHandler(Protocol):
        """Protocol for command handlers"""
        def handle(self, command: Command) -> list[Event]:
            """Execute command, return events"""
            ...

    class UserCommandHandler:
        """Handles all user commands"""
    
        def __init__(self, pool: ConnectionPool):
            self._pool = pool
    
        def handle(self, command: Command) -> list[Event]:
            """Route to specific handler"""
            if isinstance(command, CreateUser):
                return self._handle_create(command)
            elif isinstance(command, UpdateUserStatus):
                return self._handle_update_status(command)
            elif isinstance(command, DeleteUser):
                return self._handle_delete(command)
            raise ValueError(f"Unknown command: {type(command)}")
    
        def _handle_create(self, cmd: CreateUser) -> list[Event]:
            """Private: Handle user creation"""
            conn = self._pool.acquire()
            try:
                conn.execute("BEGIN")
                conn.execute(
                    "INSERT INTO users (name, email, status) VALUES (?, ?, ?)",
                    (cmd.name, cmd.email, 'active')
                )
                user_id = conn.last_insert_rowid()
                conn.execute("COMMIT")
            
                return [UserCreated(user_id, cmd.name, cmd.email)]
            except Exception as e:
                conn.execute("ROLLBACK")
                raise
            finally:
                self._pool.release(conn)
    
        def _handle_update_status(self, cmd: UpdateUserStatus) -> list[Event]:
            """Private: Handle status update"""
            conn = self._pool.acquire()
            try:
                # Get old status first
                old_status = conn.execute(
                    "SELECT status FROM users WHERE id = ?",
                    (cmd.user_id,)
                ).fetchone()
            
                if not old_status:
                    return []  # User doesn't exist
            
                conn.execute("BEGIN")
                conn.execute(
                    "UPDATE users SET status = ? WHERE id = ?",
                    (cmd.status, cmd.user_id)
                )
                conn.execute("COMMIT")
            
                return [UserStatusUpdated(cmd.user_id, old_status[0], cmd.status)]
            except Exception as e:
                conn.execute("ROLLBACK")
                raise
            finally:
                self._pool.release(conn)
    
        def _handle_delete(self, cmd: DeleteUser) -> list[Event]:
            """Private: Handle deletion"""
            conn = self._pool.acquire()
            try:
                conn.execute("BEGIN")
                conn.execute("DELETE FROM users WHERE id = ?", (cmd.user_id,))
                success = conn.changes() > 0
                conn.execute("COMMIT")
            
                return [UserDeleted(cmd.user_id)] if success else []
            finally:
                self._pool.release(conn)
    return CommandHandler, UserCommandHandler


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Queries
    read-only, optimized for display
    """)
    return


@app.cell
def _():
    @dataclass
    class Query:
        """Base query"""
        pass

    @dataclass
    class GetUser(Query):
        user_id: int

    @dataclass
    class ListUsers(Query):
        status: str | None = None
        limit: int = 10
        offset: int = 0

    @dataclass
    class GetUserStats(Query):
        user_id: int
    return GetUser, GetUserStats, ListUsers, Query


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Query Handlers
    fast reads, no writes
    """)
    return


@app.cell
def _(ConnectionPool, GetUser, GetUserStats, ListUsers, Query):
    class QueryHandler(Protocol):
        """Protocol for query handlers"""
        def handle(self, query: Query) -> Any:
            """Execute query, return result"""
            ...

    class UserQueryHandler:
        """Handles all user queries"""
    
        def __init__(self, pool: ConnectionPool):
            self._pool = pool
    
        def handle(self, query: Query) -> Any:
            """Route to specific handler"""
            if isinstance(query, GetUser):
                return self._handle_get(query)
            elif isinstance(query, ListUsers):
                return self._handle_list(query)
            elif isinstance(query, GetUserStats):
                return self._handle_stats(query)
            raise ValueError(f"Unknown query: {type(query)}")
    
        def _handle_get(self, qry: GetUser) -> dict | None:
            """Private: Get single user"""
            conn = self._pool.acquire()
            try:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE id = ?",
                    (qry.user_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [col[0] for col in cursor.getdescription()]
                return dict(zip(cols, row))
            finally:
                self._pool.release(conn)
    
        def _handle_list(self, qry: ListUsers) -> list[dict]:
            """Private: List users"""
            conn = self._pool.acquire()
            try:
                query = "SELECT * FROM users"
                params = []
            
                if qry.status:
                    query += " WHERE status = ?"
                    params.append(qry.status)
            
                query += " LIMIT ? OFFSET ?"
                params.extend([qry.limit, qry.offset])
            
                cursor = conn.execute(query, params)
                cols = [col[0] for col in cursor.getdescription()]
                return [dict(zip(cols, row)) for row in cursor]
            finally:
                self._pool.release(conn)
    
        def _handle_stats(self, qry: GetUserStats) -> dict:
            """Private: Get user statistics"""
            conn = self._pool.acquire()
            try:
                posts = conn.execute(
                    "SELECT COUNT(*) FROM posts WHERE user_id = ?",
                    (qry.user_id,)
                ).fetchone()[0]
            
                comments = conn.execute(
                    "SELECT COUNT(*) FROM comments WHERE user_id = ?",
                    (qry.user_id,)
                ).fetchone()[0]
            
                return {'posts': posts, 'comments': comments}
            finally:
                self._pool.release(conn)
    return QueryHandler, UserQueryHandler


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## COMMAND BUS
    Central dispatcher
    """)
    return


@app.cell
def _(
    Command,
    CommandHandler,
    Event,
    EventBus,
    UserCreated,
    UserDeleted,
    UserStatusUpdated,
):
    class CommandBus:
        """Executes commands and publishes events"""
    
        def __init__(self, handler: CommandHandler, event_bus: EventBus):
            self._handler = handler
            self._event_bus = event_bus
    
        def execute(self, command: Command) -> list[Event]:
            """Public: Execute command and publish events"""
            events = self._handler.handle(command)
        
            # Publish all events
            for event in events:
                self._publish_event(event)
        
            return events
    
        def _publish_event(self, event: Event):
            """Private: Publish event to subscribers"""
            # Convert to DBEvent for compatibility
            if isinstance(event, UserCreated):
                self._event_bus.emit_sync('users', 'INSERT', event.user_id, {
                    'name': event.name,
                    'email': event.email,
                    'status': event.status
                })
            elif isinstance(event, UserStatusUpdated):
                self._event_bus.emit_sync('users', 'UPDATE', event.user_id, {
                    'status': event.new_status
                })
            elif isinstance(event, UserDeleted):
                self._event_bus.emit_sync('users', 'DELETE', event.user_id)
    return (CommandBus,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## QUERY BUS
    Central dispatcher
    """)
    return


@app.cell
def _(Query, QueryHandler):
    class QueryBus:
        """Executes queries"""
    
        def __init__(self, handler: QueryHandler):
            self._handler = handler
    
        def execute(self, query: Query) -> Any:
            """Public: Execute query and return result"""
            return self._handler.handle(query)

    return (QueryBus,)


@app.cell
def _(mo):
    mo.md(r"""
    ## FT COMPONENTS
    Now super clean!
    """)
    return


@app.cell
def _(Button, Div, GetUser, H3, ListUsers, P, QueryBus, Span):
    class LiveUserCard:
        """Render user card - only needs QueryBus"""
    
        def __init__(self, query_bus: QueryBus, user_id: int):
            self._query_bus = query_bus
            self._user_id = user_id
    
        def __ft__(self) -> FT:
            """Public: Render with live updates"""
            # Just execute a query - no confusion about side effects
            user = self._query_bus.execute(GetUser(self._user_id))
        
            if not user:
                return Div("User not found", cls="error")
        
            return Div(
                H3(user['name']),
                P(user['email']),
                Span(user['status'], cls=f"badge badge-{user['status']}"),
            
                # Commands via buttons - clear intent
                Button(
                    "Activate",
                    data_on_click=f"$$post('/cmd/user/activate', {{userId: {user['id']}}})"
                ),
                Button(
                    "Deactivate",
                    data_on_click=f"$$post('/cmd/user/deactivate', {{userId: {user['id']}}})"
                ),
            
                # SSE for live updates
                data_on_load=f"$$get('/sse/user/{user['id']}')",
                id=f"user-{user['id']}",
                cls="user-card live"
            )

    class LiveUserList:
        """Render user list - only needs QueryBus"""
    
        def __init__(self, query_bus: QueryBus, status: str = None, limit: int = 10):
            self._query_bus = query_bus
            self._status = status
            self._limit = limit
    
        def __ft__(self) -> FT:
            """Public: Render list"""
            users = self._query_bus.execute(
                ListUsers(status=self._status, limit=self._limit)
            )
        
            if not users:
                return Div("No users found", cls="empty")
        
            return Div(
                *[LiveUserCard(self._query_bus, user['id']) for user in users],
                data_on_load="$$get('/sse/users')",
                id="user-list",
                cls="user-list live"
            )
    return LiveUserCard, LiveUserList


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## FASTHTML APP
    Crystal clear routes
    """)
    return


@app.cell
def _(
    Body,
    Button,
    CommandBus,
    ConnectionPool,
    CreateUser,
    DeleteUser,
    EventBus,
    Form,
    GetUser,
    H1,
    Head,
    Html,
    Input,
    LiveUserCard,
    LiveUserList,
    QueryBus,
    SSEManager,
    Script,
    StreamingResponse,
    Title,
    UpdateUserStatus,
    UserCommandHandler,
    UserQueryHandler,
    uuid,
):
    app = FastHTML()

    # Setup
    pool = ConnectionPool("app.db")
    event_bus = EventBus()

    command_handler = UserCommandHandler(pool)
    query_handler = UserQueryHandler(pool)

    command_bus = CommandBus(command_handler, event_bus)
    query_bus = QueryBus(query_handler)

    sse_manager = SSEManager(event_bus)
    sse_manager.start_event_listener()

    # ============================================================================
    # QUERY ROUTES - Read-only
    # ============================================================================

    @app.get('/')
    def home():
        """Query: Display page"""
        return Html(
            Head(
                Title("CQRS Dashboard"),
                Script(src="https://cdn.jsdelivr.net/npm/@sudodevnull/datastar")
            ),
            Body(
                H1("Live User Dashboard"),
                LiveUserList(query_bus, status='active'),
            
                # Command form
                Form(
                    Input(placeholder="Name", data_bind_value="$new.name"),
                    Input(placeholder="Email", data_bind_value="$new.email"),
                    Button("Create User", type="submit"),
                    data_signals_new='{"name":"","email":""}',
                    data_on_submit__prevent="$$post('/cmd/user/create', $new)"
                )
            )
        )

    @app.get('/user/{user_id}')
    def user_page(user_id: int):
        """Query: Display user"""
        return LiveUserCard(query_bus, user_id)

    # ============================================================================
    # COMMAND ROUTES - Write-only
    # ============================================================================

    @app.post('/cmd/user/create')
    def create_user_cmd(name: str, email: str):
        """Command: Create user"""
        events = command_bus.execute(CreateUser(name, email))
    
        # Return created user card
        user_created = events[0]  # UserCreated event
        return LiveUserCard(query_bus, user_created.user_id)

    @app.post('/cmd/user/activate')
    def activate_user_cmd(userId: int):
        """Command: Activate user"""
        command_bus.execute(UpdateUserStatus(userId, 'active'))
    
        # Return updated card
        return LiveUserCard(query_bus, userId)

    @app.post('/cmd/user/deactivate')
    def deactivate_user_cmd(userId: int):
        """Command: Deactivate user"""
        command_bus.execute(UpdateUserStatus(userId, 'inactive'))
    
        # Return updated card
        return LiveUserCard(query_bus, userId)

    @app.delete('/cmd/user/{user_id}')
    def delete_user_cmd(user_id: int):
        """Command: Delete user"""
        command_bus.execute(DeleteUser(user_id))
        return ""

    # ============================================================================
    # SSE ROUTES - Event streaming
    # ============================================================================

    @app.get('/sse/user/{user_id}')
    async def sse_user(user_id: int):
        """SSE: Stream updates for specific user"""
        client_id = f"user-{user_id}-{uuid.uuid4()}"
        conn = await sse_manager.add_connection(
            client_id,
            filters={'table': 'users', 'record_id': user_id}
        )
    
        async def stream():
            try:
                async for message in conn.stream():
                    # Re-query and re-render on each event
                    user = query_bus.execute(GetUser(user_id))
                    if user:
                        card = LiveUserCard(query_bus, user_id)
                        html = to_xml(card)
                        yield f"event: update\ndata: {html}\n\n"
            finally:
                await sse_manager.remove_connection(client_id)
    
        return StreamingResponse(stream(), media_type="text/event-stream")

    @app.get('/sse/users')
    async def sse_users():
        """SSE: Stream updates for user list"""
        client_id = f"users-{uuid.uuid4()}"
        conn = await sse_manager.add_connection(client_id, filters={'table': 'users'})
    
        async def stream():
            try:
                async for message in conn.stream():
                    # Re-query and re-render list
                    user_list = LiveUserList(query_bus)
                    html = to_xml(user_list)
                    yield f"event: update\ndata: {html}\n\n"
            finally:
                await sse_manager.remove_connection(client_id)
    
        return StreamingResponse(stream(), media_type="text/event-stream")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
