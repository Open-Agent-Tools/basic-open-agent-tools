"""Core TODO list operations for AI agents.

Provides in-memory task management capabilities for agents to track
their own workflow during a session.
"""

from datetime import datetime
from typing import Any

from .._logging import get_logger
from ..confirmation import check_user_confirmation
from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError
from .validation import (
    validate_dependencies,
    validate_estimated_duration,
    validate_notes,
    validate_priority,
    validate_status,
    validate_tags,
    validate_task_count,
    validate_task_exists,
    validate_title,
)

# Global in-memory storage
_task_storage: dict[str, Any] = {
    "tasks": {},  # Dict[int, Dict] - task_id -> task_data
    "next_id": 1,  # Auto-incrementing counter
    "total_count": 0,  # Total tasks created (for stats)
}


logger = get_logger("todo.operations")


def _get_current_timestamp() -> str:
    """Get current ISO timestamp."""
    return datetime.now().isoformat()


@strands_tool
def add_task(
    title: str,
    priority: str,
    notes: str,
    tags: list[str],
    estimated_duration: str,
    dependencies: list[int],
) -> dict[str, Any]:
    """Create a new task with auto-incrementing ID.

    Creates a new task and adds it to the in-memory storage. The task
    starts with 'open' status and gets a unique auto-incrementing ID.

    Args:
        title: Task description or title
        priority: Priority level ('low', 'medium', 'high', 'urgent')
        notes: Additional task details or notes
        tags: List of tags for categorization
        estimated_duration: Optional time estimate as string
        dependencies: List of task IDs this task depends on

    Returns:
        Dictionary containing:
        - success: True if task created successfully
        - task: The created task dictionary
        - message: Success message with task ID

    Raises:
        BasicAgentToolsError: If validation fails or task limit exceeded

    Example:
        >>> result = add_task(
        ...     title="Implement user auth",
        ...     priority="high",
        ...     notes="Use OAuth2",
        ...     tags=["security", "backend"],
        ...     estimated_duration="2 hours",
        ...     dependencies=[]
        ... )
        >>> result["success"]
        True
    """
    try:
        # Validate inputs
        validate_title(title)
        validate_priority(priority)
        validate_notes(notes)
        validate_tags(tags)
        validate_estimated_duration(estimated_duration)
        validate_task_count(len(_task_storage["tasks"]))
        validate_dependencies(dependencies, _task_storage["tasks"], 0)

        # Create new task
        task_id = _task_storage["next_id"]
        timestamp = _get_current_timestamp()

        task = {
            "id": task_id,
            "title": title,
            "status": "open",
            "priority": priority,
            "created_at": timestamp,
            "updated_at": timestamp,
            "notes": notes,
            "tags": tags,
            "estimated_duration": estimated_duration,
            "dependencies": dependencies,
        }

        # Store task
        _task_storage["tasks"][task_id] = task
        _task_storage["next_id"] += 1
        _task_storage["total_count"] += 1

        # Log task creation
        logger.info(
            f"[TODO] Created task #{task_id}: '{title}' "
            f"(priority: {priority}, tags: {tags or 'none'}, "
            f"dependencies: {dependencies or 'none'})"
        )

        return {
            "success": True,
            "task": task,
            "message": f"Task created with ID {task_id}",
        }

    except (ValueError, TypeError) as e:
        logger.error(f"[TODO] Failed to create task: {e}")
        raise BasicAgentToolsError(f"Failed to create task: {e}") from e


@strands_tool
def list_tasks(status: str, tag: str) -> dict[str, Any]:
    """List all tasks or filter by status and/or tag.

    Returns all tasks or filters them based on status and tag criteria.
    If no filters are provided, returns all tasks.

    Args:
        status: Filter by task status (empty string for no filter)
        tag: Filter by tag (empty string for no filter)

    Returns:
        Dictionary containing:
        - success: True if operation successful
        - tasks: List of task dictionaries matching criteria
        - count: Number of tasks returned
        - filters_applied: Dictionary of applied filters

    Raises:
        BasicAgentToolsError: If status validation fails

    Example:
        >>> result = list_tasks(status="in_progress", tag="")
        >>> len(result["tasks"])
        2
    """
    try:
        # Validate status filter if provided
        if status:
            validate_status(status)

        tasks = list(_task_storage["tasks"].values())
        original_count = len(tasks)

        # Apply filters
        if status:
            tasks = [task for task in tasks if task["status"] == status]

        if tag:
            tasks = [task for task in tasks if tag in task["tags"]]

        # Sort by ID for consistent ordering
        tasks.sort(key=lambda x: x["id"])

        # Log task listing with filters
        filter_desc = []
        if status:
            filter_desc.append(f"status={status}")
        if tag:
            filter_desc.append(f"tag={tag}")
        filter_str = ", ".join(filter_desc) if filter_desc else "no filters"

        logger.info(
            f"[TODO] Listed {len(tasks)} task(s) ({filter_str}) - "
            f"Total tasks in storage: {original_count}"
        )

        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
            "total_tasks": original_count,
            "filters_applied": {
                "status": status if status else None,
                "tag": tag if tag else None,
            },
        }

    except ValueError as e:
        logger.error(f"[TODO] Failed to list tasks: {e}")
        raise BasicAgentToolsError(f"Failed to list tasks: {e}") from e


@strands_tool
def get_task(task_id: int) -> dict[str, Any]:
    """Retrieve a single task by ID.

    Gets the complete task data for the specified task ID.

    Args:
        task_id: The unique task identifier

    Returns:
        Dictionary containing:
        - success: True if task found
        - task: The task dictionary
        - message: Success message

    Raises:
        BasicAgentToolsError: If task not found

    Example:
        >>> result = get_task(1)
        >>> result["task"]["title"]
        "Implement user auth"
    """
    try:
        validate_task_exists(task_id, _task_storage["tasks"])

        task = _task_storage["tasks"][task_id]

        logger.info(
            f"[TODO] Retrieved task #{task_id}: '{task['title']}' "
            f"(status: {task['status']}, priority: {task['priority']})"
        )

        return {
            "success": True,
            "task": task,
            "message": f"Task {task_id} retrieved successfully",
        }

    except (ValueError, TypeError) as e:
        logger.error(f"[TODO] Failed to get task {task_id}: {e}")
        raise BasicAgentToolsError(f"Failed to get task: {e}") from e


@strands_tool
def update_task(
    task_id: int,
    title: str,
    status: str,
    priority: str,
    notes: str,
    tags: list[str],
    estimated_duration: str,
    dependencies: list[int],
) -> dict[str, Any]:
    """Update any field of an existing task.

    Updates the specified task with new values and refreshes the
    updated_at timestamp.

    Args:
        task_id: The unique task identifier
        title: New task title
        status: New task status
        priority: New priority level
        notes: New notes
        tags: New tags list
        estimated_duration: New time estimate
        dependencies: New dependencies list

    Returns:
        Dictionary containing:
        - success: True if task updated
        - task: The updated task dictionary
        - message: Success message

    Raises:
        BasicAgentToolsError: If task not found or validation fails

    Example:
        >>> result = update_task(
        ...     task_id=1,
        ...     title="Updated title",
        ...     status="in_progress",
        ...     priority="urgent",
        ...     notes="Updated notes",
        ...     tags=["new_tag"],
        ...     estimated_duration="3 hours",
        ...     dependencies=[]
        ... )
        >>> result["task"]["status"]
        "in_progress"
    """
    try:
        validate_task_exists(task_id, _task_storage["tasks"])
        validate_title(title)
        validate_status(status)
        validate_priority(priority)
        validate_notes(notes)
        validate_tags(tags)
        validate_estimated_duration(estimated_duration)
        validate_dependencies(
            dependencies, _task_storage["tasks"], exclude_task_id=task_id
        )

        # Get current task for logging changes
        task = _task_storage["tasks"][task_id]
        old_status = task["status"]
        old_priority = task["priority"]

        # Update task
        task.update(
            {
                "title": title,
                "status": status,
                "priority": priority,
                "notes": notes,
                "tags": tags,
                "estimated_duration": estimated_duration,
                "dependencies": dependencies,
                "updated_at": _get_current_timestamp(),
            }
        )

        # Log changes
        changes = []
        if old_status != status:
            changes.append(f"status: {old_status} → {status}")
        if old_priority != priority:
            changes.append(f"priority: {old_priority} → {priority}")

        change_desc = ", ".join(changes) if changes else "metadata updated"
        logger.info(f"[TODO] Updated task #{task_id}: '{title}' ({change_desc})")

        return {
            "success": True,
            "task": task,
            "message": f"Task {task_id} updated successfully",
        }

    except ValueError as e:
        logger.error(f"[TODO] Failed to update task {task_id}: {e}")
        raise BasicAgentToolsError(f"Failed to update task: {e}") from e


@strands_tool
def delete_task(task_id: int, skip_confirm: bool) -> str:
    """Remove a task from memory with permission checking.

    Permanently deletes the specified task from storage.

    Args:
        task_id: The unique task identifier
        skip_confirm: If True, skip confirmation and proceed with deletion. IMPORTANT: Agents should default to skip_confirm=False for safety.

    Returns:
        String describing the operation result

    Raises:
        BasicAgentToolsError: If task not found or deletion not allowed without skip_confirm

    Example:
        >>> result = delete_task(1, skip_confirm=True)
        "Deleted task 1: 'Complete project setup' (was 'in_progress')"
    """
    try:
        validate_task_exists(task_id, _task_storage["tasks"])

        # Get task info before deletion for feedback
        task = _task_storage["tasks"][task_id]
        task_title = task.get("title", "Untitled")
        task_status = task.get("status", "unknown")

        # Check if task is important (e.g., in_progress) and require confirmation
        if task_status == "in_progress":
            # Check user confirmation
            confirmed = check_user_confirmation(
                operation="delete in-progress task",
                target=f"Task {task_id}: {task_title}",
                skip_confirm=skip_confirm,
                preview_info=f"Status: {task_status}",
            )

            if not confirmed:
                logger.info(f"[TODO] Task deletion cancelled by user: #{task_id}")
                return f"Operation cancelled by user: Task {task_id}"

        # Remove task
        del _task_storage["tasks"][task_id]

        logger.info(
            f"[TODO] Deleted task #{task_id}: '{task_title}' (was '{task_status}')"
        )

        return f"Deleted task {task_id}: '{task_title}' (was '{task_status}')"

    except ValueError as e:
        logger.error(f"[TODO] Failed to delete task {task_id}: {e}")
        raise BasicAgentToolsError(f"Failed to delete task: {e}") from e


@strands_tool
def complete_task(task_id: int) -> dict[str, Any]:
    """Mark a task as completed.

    Convenience method to set task status to 'completed' and update
    the timestamp.

    Args:
        task_id: The unique task identifier

    Returns:
        Dictionary containing:
        - success: True if task completed
        - task: The updated task dictionary
        - message: Success message

    Raises:
        BasicAgentToolsError: If task not found

    Example:
        >>> result = complete_task(1)
        >>> result["task"]["status"]
        "completed"
    """
    try:
        validate_task_exists(task_id, _task_storage["tasks"])

        # Update status and timestamp
        task = _task_storage["tasks"][task_id]
        old_status = task["status"]
        task["status"] = "completed"
        task["updated_at"] = _get_current_timestamp()

        logger.info(
            f"[TODO] Completed task #{task_id}: '{task['title']}' (was '{old_status}')"
        )

        return {
            "success": True,
            "task": task,
            "message": f"Task {task_id} marked as completed",
        }

    except ValueError as e:
        logger.error(f"[TODO] Failed to complete task {task_id}: {e}")
        raise BasicAgentToolsError(f"Failed to complete task: {e}") from e


@strands_tool
def get_task_stats() -> dict[str, Any]:
    """Get summary statistics about all tasks.

    Returns counts and statistics about the current task list.

    Returns:
        Dictionary containing:
        - success: True
        - total_tasks: Total number of tasks
        - status_counts: Count by status
        - priority_counts: Count by priority
        - tasks_with_dependencies: Number of tasks with dependencies
        - average_tasks_per_status: Average distribution

    Example:
        >>> result = get_task_stats()
        >>> result["status_counts"]["completed"]
        5
    """
    try:
        tasks = list(_task_storage["tasks"].values())
        total = len(tasks)

        # Count by status
        status_counts = {}
        for status in [
            "open",
            "in_progress",
            "blocked",
            "deferred",
            "completed",
            "cancelled",
        ]:
            status_counts[status] = len([t for t in tasks if t["status"] == status])

        # Count by priority
        priority_counts = {}
        for priority in ["low", "medium", "high", "urgent"]:
            priority_counts[priority] = len(
                [t for t in tasks if t["priority"] == priority]
            )

        # Other stats
        tasks_with_dependencies = len([t for t in tasks if t["dependencies"]])

        logger.info(
            f"[TODO] Task statistics: {total} total tasks "
            f"(open: {status_counts['open']}, in_progress: {status_counts['in_progress']}, "
            f"completed: {status_counts['completed']})"
        )

        return {
            "success": True,
            "total_tasks": total,
            "total_created": _task_storage["total_count"],
            "status_counts": status_counts,
            "priority_counts": priority_counts,
            "tasks_with_dependencies": tasks_with_dependencies,
            "next_id": _task_storage["next_id"],
        }

    except Exception as e:
        logger.error(f"[TODO] Failed to get task statistics: {e}")
        raise BasicAgentToolsError(f"Failed to get task statistics: {e}") from e


@strands_tool
def clear_all_tasks() -> dict[str, Any]:
    """Clear all tasks from memory (for testing/reset).

    WARNING: This permanently deletes all tasks. Use with caution.

    Returns:
        Dictionary containing:
        - success: True
        - message: Confirmation message
        - cleared_count: Number of tasks that were cleared

    Example:
        >>> result = clear_all_tasks()
        >>> result["cleared_count"]
        10
    """
    try:
        cleared_count = len(_task_storage["tasks"])

        # Reset storage
        _task_storage["tasks"] = {}
        _task_storage["next_id"] = 1
        _task_storage["total_count"] = 0

        logger.info(
            f"[TODO] Cleared all tasks from memory ({cleared_count} tasks removed)"
        )

        return {
            "success": True,
            "message": f"Cleared {cleared_count} tasks from memory",
            "cleared_count": cleared_count,
        }

    except Exception as e:
        logger.error(f"[TODO] Failed to clear tasks: {e}")
        raise BasicAgentToolsError(f"Failed to clear tasks: {e}") from e
