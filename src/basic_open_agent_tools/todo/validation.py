"""Validation functions for TODO list operations.

Provides input validation and constraint enforcement for the todo module.
"""

from typing import Any


def validate_title(title: str) -> None:
    """Validate task title.

    Args:
        title: Task title to validate

    Raises:
        ValueError: If title is invalid
        TypeError: If title is not a string
    """
    if not isinstance(title, str):
        raise TypeError("Title must be a string")

    if not title.strip():
        raise ValueError("Title cannot be empty or whitespace only")

    if len(title) > 500:
        raise ValueError("Title cannot exceed 500 characters")


def validate_status(status: str) -> None:
    """Validate task status.

    Args:
        status: Status to validate

    Raises:
        ValueError: If status is invalid
        TypeError: If status is not a string
    """
    if not isinstance(status, str):
        raise TypeError("Status must be a string")

    valid_statuses = [
        "open",
        "in_progress",
        "blocked",
        "deferred",
        "completed",
        "cancelled",
    ]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")


def validate_priority(priority: str) -> None:
    """Validate task priority.

    Args:
        priority: Priority to validate

    Raises:
        ValueError: If priority is invalid
        TypeError: If priority is not a string
    """
    if not isinstance(priority, str):
        raise TypeError("Priority must be a string")

    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        raise ValueError(
            f"Invalid priority '{priority}'. Must be one of: {valid_priorities}"
        )


def validate_task_count(current_count: int) -> None:
    """Validate that task count doesn't exceed maximum.

    Args:
        current_count: Current number of tasks

    Raises:
        ValueError: If task limit would be exceeded
    """
    max_tasks = 50
    if current_count >= max_tasks:
        raise ValueError(f"Maximum task limit of {max_tasks} reached")


def validate_task_exists(task_id: int, tasks: dict[int, dict[str, Any]]) -> None:
    """Validate that a task exists.

    Args:
        task_id: Task ID to check
        tasks: Dictionary of existing tasks

    Raises:
        ValueError: If task doesn't exist
        TypeError: If task_id is not an integer
    """
    if not isinstance(task_id, int):
        raise TypeError("Task ID must be an integer")

    if task_id not in tasks:
        raise ValueError(f"Task with ID {task_id} not found")


def validate_dependencies(
    dependencies: list[int],
    tasks: dict[int, dict[str, Any]],
    exclude_task_id: int,
) -> None:
    """Validate task dependencies.

    Args:
        dependencies: List of task IDs this task depends on
        tasks: Dictionary of existing tasks
        exclude_task_id: Task ID to exclude from circular dependency check (use 0 for no exclusion)

    Raises:
        ValueError: If dependencies are invalid
        TypeError: If dependencies is not a list
    """
    if not isinstance(dependencies, list):
        raise TypeError("Dependencies must be a list")

    # Check each dependency exists
    for dep_id in dependencies:
        if not isinstance(dep_id, int):
            raise TypeError(f"Dependency ID {dep_id} must be an integer")

        if dep_id not in tasks:
            raise ValueError(f"Dependency task {dep_id} not found")

        # Prevent self-dependency (exclude_task_id=0 means no exclusion)
        if exclude_task_id > 0 and dep_id == exclude_task_id:
            raise ValueError("Task cannot depend on itself")

    # Check for circular dependencies (exclude_task_id=0 means no check needed)
    if exclude_task_id > 0:
        _check_circular_dependencies(exclude_task_id, dependencies, tasks)


def _check_circular_dependencies(
    task_id: int, dependencies: list[int], tasks: dict[int, dict[str, Any]]
) -> None:
    """Check for circular dependency chains.

    Args:
        task_id: The task being updated
        dependencies: New dependencies for the task
        tasks: All existing tasks

    Raises:
        ValueError: If circular dependency detected
    """

    def has_path_to_task(from_task: int, to_task: int, visited: set) -> bool:
        """Check if there's a dependency path from one task to another."""
        if from_task == to_task:
            return True

        if from_task in visited:
            return False

        visited.add(from_task)

        if from_task not in tasks:
            return False

        task_deps = tasks[from_task].get("dependencies", [])
        for dep in task_deps:
            if has_path_to_task(dep, to_task, visited.copy()):
                return True

        return False

    # Check if any dependency has a path back to this task
    for dep_id in dependencies:
        if has_path_to_task(dep_id, task_id, set()):
            raise ValueError(
                f"Circular dependency detected: task {task_id} -> {dep_id}"
            )


def validate_tags(tags: list[str]) -> None:
    """Validate task tags.

    Args:
        tags: List of tags to validate

    Raises:
        ValueError: If tags are invalid
        TypeError: If tags is not a list or contains non-strings
    """
    if not isinstance(tags, list):
        raise TypeError("Tags must be a list")

    for tag in tags:
        if not isinstance(tag, str):
            raise TypeError("All tags must be strings")

        if not tag.strip():
            raise ValueError("Tags cannot be empty or whitespace only")

        if len(tag) > 50:
            raise ValueError("Tags cannot exceed 50 characters")

    # Check for duplicates
    if len(tags) != len(set(tags)):
        raise ValueError("Duplicate tags are not allowed")

    if len(tags) > 20:
        raise ValueError("Maximum 20 tags allowed per task")


def validate_estimated_duration(estimated_duration: str) -> None:
    """Validate estimated duration string.

    Args:
        estimated_duration: Duration estimate to validate

    Raises:
        TypeError: If not a string
        ValueError: If duration format is invalid
    """
    if not isinstance(estimated_duration, str):
        raise TypeError("Estimated duration must be a string")

    # Allow empty duration
    if not estimated_duration.strip():
        return

    if len(estimated_duration) > 100:
        raise ValueError("Estimated duration cannot exceed 100 characters")


def validate_notes(notes: str) -> None:
    """Validate task notes.

    Args:
        notes: Notes to validate

    Raises:
        TypeError: If notes is not a string
        ValueError: If notes exceed length limit
    """
    if not isinstance(notes, str):
        raise TypeError("Notes must be a string")

    if len(notes) > 2000:
        raise ValueError("Notes cannot exceed 2000 characters")
