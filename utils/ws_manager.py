import asyncio
from collections import defaultdict
from typing import DefaultDict, Set

from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: DefaultDict[int, Set[WebSocket]] = defaultdict(set)
        self.loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].add(websocket)
        if self.loop is None:
            self.loop = asyncio.get_running_loop()

    def disconnect(self, user_id: int, websocket: WebSocket):
        user_connections = self.active_connections.get(user_id)
        if not user_connections:
            return
        user_connections.discard(websocket)
        if not user_connections:
            self.active_connections.pop(user_id, None)

    async def send_personal_message(self, user_id: int, message: str):
        user_connections = self.active_connections.get(user_id, set()).copy()
        stale: set[WebSocket] = set()
        for websocket in user_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                stale.add(websocket)

        if stale:
            current = self.active_connections.get(user_id, set())
            current.difference_update(stale)
            if not current:
                self.active_connections.pop(user_id, None)

    def schedule_send(self, user_id: int, message: str):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.send_personal_message(user_id, message), self.loop
            )

manager = ConnectionManager()
