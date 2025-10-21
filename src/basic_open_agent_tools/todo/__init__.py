"""Simple in-memory TODO list tool for AI agents.

Provides task management capabilities for agents to track their own
workflow during a session. Tasks can be persisted to files for
sharing between agents and sessions.
"""

from .operations import (
    add_task,
    clear_all_tasks,
    complete_task,
    delete_task,
    get_task,
    get_task_stats,
    list_tasks,
    update_task,
)
from .persistence import (
    load_tasks_from_file,
    save_tasks_to_file,
    validate_task_file,
)

__all__ = [
    "add_task",
    "list_tasks",
    "get_task",
    "update_task",
    "delete_task",
    "complete_task",
    "get_task_stats",
    "clear_all_tasks",
    "save_tasks_to_file",
    "load_tasks_from_file",
    "validate_task_file",
]
