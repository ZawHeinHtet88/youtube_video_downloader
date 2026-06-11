import asyncio
import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Task:
    task_id: str
    url: str
    status: str = "pending"
    filename: str | None = None
    created_at: float = field(default_factory=time.time)
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue())
    cancelled: bool = False


class TaskManager:
    def __init__(self):
        self._tasks: dict[str, Task] = {}

    def create(self, url: str) -> Task:
        task_id = uuid.uuid4().hex[:12]
        task = Task(task_id=task_id, url=url)
        self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list_all(self) -> list[Task]:
        return sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status in ("pending", "downloading"):
            task.cancelled = True
            task.status = "cancelled"
            return True
        return False

    def remove(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


task_manager = TaskManager()
