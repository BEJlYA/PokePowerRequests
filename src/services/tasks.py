from dataclasses import dataclass

GENDER_MAP = {"Б": "genderless", "М": "mars", "Ж": "venus", "Л": "any"}


@dataclass
class Task:
    kind: str
    name: str = ""
    num: str = ""
    gender: str = "Л"
    count: int = 0

    def key(self) -> tuple:
        if self.kind == "pokemon":
            return self.kind, self.name or self.num, self.gender
        return self.kind, self.name

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "name": self.name,
            "num": self.num,
            "gender": self.gender,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            kind=data.get("kind", "item"),
            name=data.get("name", ""),
            num=str(data.get("num", "") or ""),
            gender=data.get("gender", "Л") or "Л",
            count=int(data.get("count", 0)),
        )

    @property
    def search_name(self) -> str:
        return self.name or self.num


class Tasks:
    def __init__(self) -> None:
        self._tasks: list[Task] = []
        self._index: dict[tuple, Task] = {}

    def clear(self) -> None:
        self._tasks.clear()
        self._index.clear()

    def add(self, task: Task) -> None:
        if task.count <= 0:
            return
        k = task.key()
        existing = self._index.get(k)
        if existing is not None:
            existing.count += task.count
        else:
            self._index[k] = task
            self._tasks.append(task)

    def remove_completed(self) -> None:
        self._tasks = [t for t in self._tasks if t.count > 0]
        self._index = {t.key(): t for t in self._tasks}

    def all(self) -> list[Task]:
        return list(self._tasks)

    def priority(self) -> Task | None:
        return self._tasks[0] if self._tasks else None

    def __bool__(self) -> bool:
        return bool(self._tasks)

    def __iter__(self):
        return iter(self._tasks)

tasks = Tasks()
