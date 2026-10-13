from collections import defaultdict
from typing import Awaitable, Callable


class TaskEvents:
    """Простой pub/sub для событий задач."""
    def __init__(self) -> None:
        self._subs: dict[str, list[Callable[[], Awaitable[None]]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[], Awaitable[None]]) -> None:
        if handler not in self._subs[topic]:
            self._subs[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable[[], Awaitable[None]]) -> None:
        if handler in self._subs[topic]:
            self._subs[topic].remove(handler)

    def clear_topic(self, topic: str) -> None:
        self._subs[topic].clear()

    def clear_all(self) -> None:
        self._subs.clear()

    async def emit(self, topic: str) -> None:
        for handler in list(self._subs[topic]):
            try:
                await handler()
            except Exception:
                import traceback
                traceback.print_exc()


task_events = TaskEvents()