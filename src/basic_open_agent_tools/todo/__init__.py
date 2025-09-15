"""Simple in-memory TODO list tool for AI agents.

Provides task management capabilities for agents to track their own
workflow during a session. Tasks exist only in memory and are designed
for agent self-organization.
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

__all__ = [
    "add_task",
    "list_tasks",
    "get_task",
    "update_task",
    "delete_task",
    "complete_task",
    "get_task_stats",
    "clear_all_tasks",
]
