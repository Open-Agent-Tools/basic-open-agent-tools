"""Task persistence operations for saving and loading tasks from files.

This module provides functionality to save and load tasks from JSON files,
enabling persistence across agent sessions and task sharing between agents.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .._logging import get_logger
from ..confirmation import check_user_confirmation
from ..decorators import strands_tool
from ..exceptions import BasicAgentToolsError

# Import validation functions
from .validation import (
    validate_estimated_duration,
    validate_notes,
    validate_priority,
    validate_status,
    validate_tags,
    validate_title,
)

logger = get_logger("todo.persistence")

# Import the internal storage from operations module after logger setup
# This is needed to access shared state _task_storage
from . import operations  # noqa: E402


def _create_file_metadata(task_count: int) -> dict[str, Any]:
    """Create metadata section for task file.

    Args:
        task_count: Number of tasks being saved

    Returns:
        Dictionary with metadata fields
    """
    now = datetime.now().isoformat()
    return {
        "version": "1.0",
        "created_at": now,
        "updated_at": now,
        "source": "basic-open-agent-tools",
        "task_count": task_count,
    }


def _validate_file_structure(data: dict[str, Any]) -> list[str]:
    """Validate complete file structure.

    Args:
        data: Parsed JSON data from file

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check top-level keys
    if "metadata" not in data:
        errors.append("Missing required key: metadata")
    if "storage" not in data:
        errors.append("Missing required key: storage")

    if errors:
        return errors

    # Validate metadata
    metadata = data["metadata"]
    if "version" not in metadata:
        errors.append("Missing metadata.version")
    elif metadata["version"] != "1.0":
        errors.append(f"Unsupported version: {metadata['version']} (need 1.0)")

    if "task_count" not in metadata:
        errors.append("Missing metadata.task_count")

    # Validate storage structure
    storage = data["storage"]
    if "tasks" not in storage:
        errors.append("Missing storage.tasks")
    if "next_id" not in storage:
        errors.append("Missing storage.next_id")
    if "total_count" not in storage:
        errors.append("Missing storage.total_count")

    if errors:
        return errors

    # Validate storage types
    if not isinstance(storage["tasks"], dict):
        errors.append("storage.tasks must be a dictionary")
    if not isinstance(storage["next_id"], int):
        errors.append("storage.next_id must be an integer")
    if not isinstance(storage["total_count"], int):
        errors.append("storage.total_count must be an integer")

    # Validate task count matches
    actual_count = len(storage["tasks"])
    declared_count = metadata["task_count"]
    if actual_count != declared_count:
        errors.append(
            f"Task count mismatch: metadata says {declared_count}, found {actual_count}"
        )

    return errors


def _validate_task_data(task: dict[str, Any], all_task_ids: set[int]) -> list[str]:
    """Validate individual task data.

    Args:
        task: Task dictionary to validate
        all_task_ids: Set of all task IDs in the file for dependency validation

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    task_id = task.get("id", "unknown")

    # Check required fields
    required_fields = [
        "id",
        "title",
        "status",
        "priority",
        "created_at",
        "updated_at",
        "notes",
        "tags",
        "estimated_duration",
        "dependencies",
    ]

    for field in required_fields:
        if field not in task:
            errors.append(f"Task {task_id}: Missing required field '{field}'")

    if errors:
        return errors

    # Validate field types and values
    try:
        validate_title(task["title"])
    except (ValueError, TypeError) as e:
        errors.append(f"Task {task_id}: Invalid title - {e}")

    try:
        validate_status(task["status"])
    except (ValueError, TypeError) as e:
        errors.append(f"Task {task_id}: Invalid status - {e}")

    try:
        validate_priority(task["priority"])
    except (ValueError, TypeError) as e:
        errors.append(f"Task {task_id}: Invalid priority - {e}")

    try:
        validate_notes(task["notes"])
    except (ValueError, TypeError) as e:
        errors.append(f"Task {task_id}: Invalid notes - {e}")

    try:
        validate_tags(task["tags"])
    except (ValueError, TypeError) as e:
        errors.append(f"Task {task_id}: Invalid tags - {e}")

    try:
        validate_estimated_duration(task["estimated_duration"])
    except (ValueError, TypeError) as e:
        errors.append(f"Task {task_id}: Invalid estimated_duration - {e}")

    # Validate dependencies
    if not isinstance(task["dependencies"], list):
        errors.append(f"Task {task_id}: dependencies must be a list")
    else:
        for dep_id in task["dependencies"]:
            if not isinstance(dep_id, int):
                errors.append(f"Task {task_id}: Dependency {dep_id} must be integer")
            elif dep_id not in all_task_ids:
                errors.append(
                    f"Task {task_id}: Dependency {dep_id} references non-existent task"
                )
            elif dep_id == task["id"]:
                errors.append(f"Task {task_id}: Cannot depend on itself")

    # Validate ID type
    if not isinstance(task["id"], int):
        errors.append(f"Task {task_id}: ID must be an integer")

    return errors


def _check_circular_dependencies_in_file(tasks: dict[int, dict[str, Any]]) -> list[str]:
    """Check for circular dependencies in task set.

    Args:
        tasks: Dictionary of task_id -> task_data

    Returns:
        List of error messages describing circular dependencies
    """
    errors = []

    def has_path(from_id: int, to_id: int, visited: set[int]) -> bool:
        """Check if there's a dependency path from from_id to to_id."""
        if from_id == to_id:
            return True
        if from_id in visited:
            return False
        if from_id not in tasks:
            return False

        visited.add(from_id)
        for dep in tasks[from_id].get("dependencies", []):
            if has_path(dep, to_id, visited.copy()):
                return True
        return False

    # Check each task's dependencies
    for task_id, task in tasks.items():
        for dep_id in task.get("dependencies", []):
            if has_path(dep_id, task_id, set()):
                errors.append(
                    f"Circular dependency detected: task {task_id} -> {dep_id}"
                )
                break  # Only report once per task

    return errors


def _build_id_mapping(
    file_tasks: dict[int, dict[str, Any]],
    current_tasks: dict[int, dict[str, Any]],
    next_id: int,
) -> dict[int, int]:
    """Build mapping of old IDs to new IDs for renumbering.

    Args:
        file_tasks: Tasks from file (keyed by task ID)
        current_tasks: Current tasks in memory (keyed by task ID)
        next_id: Current next_id counter

    Returns:
        Dictionary mapping old_id -> new_id
    """
    id_mapping = {}
    current_next_id = next_id

    # Sort file tasks by ID for consistent numbering
    for old_id in sorted(file_tasks.keys()):
        if old_id in current_tasks:
            # Conflict - assign new ID
            id_mapping[old_id] = current_next_id
            current_next_id += 1
        else:
            # No conflict - keep original ID
            id_mapping[old_id] = old_id
            # Update next_id if we're using a higher ID
            if old_id >= current_next_id:
                current_next_id = old_id + 1

    return id_mapping


def _update_task_dependencies(
    task: dict[str, Any], id_mapping: dict[int, int]
) -> dict[str, Any]:
    """Update task dependencies based on ID mapping.

    Args:
        task: Task to update
        id_mapping: Mapping of old_id -> new_id

    Returns:
        Updated task with remapped dependencies
    """
    updated_task = task.copy()
    updated_deps = [id_mapping.get(dep, dep) for dep in task["dependencies"]]
    updated_task["dependencies"] = updated_deps
    return updated_task


@strands_tool
def save_tasks_to_file(file_path: str, skip_confirm: bool) -> dict[str, Any]:
    """Save all current tasks to a JSON file for persistence.

    Exports the complete task list including metadata, task data, and
    internal state (next_id, total_count) to a JSON file. This enables
    persistence across agent sessions and task sharing.

    Args:
        file_path: Absolute path to save the JSON file
        skip_confirm: If True, skip confirmation and proceed with save.
                     If False, requires user confirmation before overwriting
                     existing files. IMPORTANT: Agents should default to
                     skip_confirm=False for safety.

    Returns:
        Dictionary containing:
        - success: True if save completed
        - file_path: Absolute path to saved file
        - task_count: Number of tasks saved
        - message: Success message

    Raises:
        BasicAgentToolsError: If file path invalid, permission denied,
                             or disk write fails

    Example:
        >>> result = save_tasks_to_file(
        ...     file_path="/path/to/tasks.json",
        ...     skip_confirm=False
        ... )
        >>> result["task_count"]
        5
    """
    logger.info(f"[TODO] Saving tasks to file: {file_path}")

    try:
        # Convert to Path object for easier manipulation
        file_path_obj = Path(file_path)

        # Check if file exists and handle confirmation
        if file_path_obj.exists():
            current_count = len(operations._task_storage["tasks"])
            confirmed, decline_reason = check_user_confirmation(
                operation="overwrite existing task file",
                target=str(file_path_obj),
                skip_confirm=skip_confirm,
                preview_info=f"Current file will be replaced. Saving {current_count} tasks.",
            )

            if not confirmed:
                reason_msg = f" (reason: {decline_reason})" if decline_reason else ""
                logger.info(f"[TODO] Save cancelled by user: {file_path}{reason_msg}")
                return {
                    "success": False,
                    "file_path": str(file_path_obj),
                    "task_count": 0,
                    "message": f"Save cancelled by user{reason_msg}",
                }

        # Create parent directories if they don't exist
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Build the file data structure
        task_count = len(operations._task_storage["tasks"])
        file_data = {
            "metadata": _create_file_metadata(task_count),
            "storage": {
                "tasks": {
                    str(task_id): task
                    for task_id, task in operations._task_storage["tasks"].items()
                },
                "next_id": operations._task_storage["next_id"],
                "total_count": operations._task_storage["total_count"],
            },
        }

        # Atomic write: write to temp file first
        temp_path = file_path_obj.with_suffix(file_path_obj.suffix + ".tmp")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)

            # Rename temp file to final destination (atomic on most systems)
            temp_path.replace(file_path_obj)

            logger.info(f"[TODO] Successfully saved {task_count} tasks to {file_path}")

            return {
                "success": True,
                "file_path": str(file_path_obj.absolute()),
                "task_count": task_count,
                "message": f"Saved {task_count} tasks to {file_path_obj.name}",
            }

        except Exception:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise

    except PermissionError as e:
        logger.error(f"[TODO] Permission denied saving to {file_path}: {e}")
        raise BasicAgentToolsError(f"Permission denied writing to {file_path}") from e
    except OSError as e:
        logger.error(f"[TODO] OS error saving to {file_path}: {e}")
        raise BasicAgentToolsError(f"Failed to save tasks: {e}") from e
    except Exception as e:
        logger.error(f"[TODO] Unexpected error saving to {file_path}: {e}")
        raise BasicAgentToolsError(f"Failed to save tasks: {e}") from e


@strands_tool
def validate_task_file(file_path: str) -> dict[str, Any]:
    """Validate a task file without loading it.

    Checks if a file exists, has valid JSON structure, correct metadata,
    and valid task data. Useful for checking files before loading.

    Args:
        file_path: Absolute path to the file to validate

    Returns:
        Dictionary containing:
        - valid: True if file is valid
        - file_path: Path to validated file
        - task_count: Number of tasks in file
        - metadata: File metadata (version, created_at, etc.)
        - errors: List of validation error messages (empty if valid)
        - warnings: List of non-critical issues

    Raises:
        BasicAgentToolsError: If file doesn't exist or can't be read

    Example:
        >>> result = validate_task_file("/path/to/tasks.json")
        >>> result["valid"]
        True
        >>> result["task_count"]
        5
    """
    logger.info(f"[TODO] Validating task file: {file_path}")

    file_path_obj = Path(file_path)

    # Check if file exists
    if not file_path_obj.exists():
        raise BasicAgentToolsError(f"File not found: {file_path}")

    if not file_path_obj.is_file():
        raise BasicAgentToolsError(f"Path is not a file: {file_path}")

    errors: list[str] = []
    warnings: list[str] = []
    metadata: dict[str, Any] = {}
    task_count = 0

    try:
        # Try to parse JSON
        with open(file_path_obj, encoding="utf-8") as f:
            data = json.load(f)

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return {
            "valid": False,
            "file_path": str(file_path_obj.absolute()),
            "task_count": 0,
            "metadata": {},
            "errors": errors,
            "warnings": warnings,
        }
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to read file: {e}") from e

    # Validate file structure
    structure_errors = _validate_file_structure(data)
    errors.extend(structure_errors)

    if structure_errors:
        return {
            "valid": False,
            "file_path": str(file_path_obj.absolute()),
            "task_count": 0,
            "metadata": data.get("metadata", {}),
            "errors": errors,
            "warnings": warnings,
        }

    # Extract metadata
    metadata = data["metadata"]
    task_count = metadata["task_count"]

    # Validate each task
    tasks = data["storage"]["tasks"]
    task_ids = set()

    # First pass: collect IDs and validate task structure
    for task_id_str, task in tasks.items():
        # Validate that task ID matches key
        try:
            task_id = int(task_id_str)
            task_ids.add(task_id)

            if task.get("id") != task_id:
                errors.append(
                    f"Task ID mismatch: key is {task_id}, task.id is {task.get('id')}"
                )
        except ValueError:
            errors.append(f"Invalid task ID key: {task_id_str} (not an integer)")

    # Second pass: validate task data with all IDs known
    for _task_id_str, task in tasks.items():
        task_errors = _validate_task_data(task, task_ids)
        errors.extend(task_errors)

    # Check for circular dependencies
    int_tasks = {int(k): v for k, v in tasks.items()}
    circular_errors = _check_circular_dependencies_in_file(int_tasks)
    errors.extend(circular_errors)

    # Check for warnings (non-critical issues)
    if task_count == 0:
        warnings.append("File contains no tasks")

    # Determine validity
    is_valid = len(errors) == 0

    logger.info(
        f"[TODO] Validation {'passed' if is_valid else 'failed'} for {file_path} "
        f"({task_count} tasks, {len(errors)} errors, {len(warnings)} warnings)"
    )

    return {
        "valid": is_valid,
        "file_path": str(file_path_obj.absolute()),
        "task_count": task_count,
        "metadata": metadata,
        "errors": errors,
        "warnings": warnings,
    }


@strands_tool
def load_tasks_from_file(file_path: str, merge_mode: str) -> dict[str, Any]:
    """Load tasks from a JSON file into current session.

    Imports tasks from a saved JSON file with configurable merge behavior.
    Validates file structure and task data before loading.

    Args:
        file_path: Absolute path to the JSON file to load
        merge_mode: How to handle loading tasks. Options:
                   - "replace": Clear existing tasks, load from file
                   - "merge": Add tasks from file, skip ID conflicts
                   - "merge_renumber": Add tasks from file, renumber conflicting IDs

    Returns:
        Dictionary containing:
        - success: True if load completed
        - file_path: Path to loaded file
        - tasks_loaded: Number of tasks loaded
        - tasks_skipped: Number of tasks skipped (merge mode only)
        - tasks_renumbered: List of old_id -> new_id mappings (merge_renumber only)
        - message: Success message
        - mode_used: The merge_mode that was applied

    Raises:
        BasicAgentToolsError: If file not found, invalid format,
                             corrupt data, or validation fails

    Example:
        >>> result = load_tasks_from_file(
        ...     file_path="/path/to/tasks.json",
        ...     merge_mode="replace"
        ... )
        >>> result["tasks_loaded"]
        5
    """
    logger.info(f"[TODO] Loading tasks from file: {file_path} (mode: {merge_mode})")

    # Validate merge_mode parameter
    valid_modes = ["replace", "merge", "merge_renumber"]
    if merge_mode not in valid_modes:
        raise BasicAgentToolsError(
            f"Invalid merge_mode '{merge_mode}'. Must be one of: {valid_modes}"
        )

    # First, validate the file
    validation_result = validate_task_file(file_path)

    if not validation_result["valid"]:
        error_msg = "; ".join(validation_result["errors"])
        logger.error(f"[TODO] File validation failed: {error_msg}")
        raise BasicAgentToolsError(f"Invalid task file: {error_msg}")

    # Load the file
    file_path_obj = Path(file_path)
    try:
        with open(file_path_obj, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise BasicAgentToolsError(f"Failed to read file: {e}") from e

    # Extract file data
    file_storage = data["storage"]
    file_tasks = {int(k): v for k, v in file_storage["tasks"].items()}
    file_next_id = file_storage["next_id"]

    # Handle different merge modes
    tasks_loaded = 0
    tasks_skipped = 0
    tasks_renumbered = []

    if merge_mode == "replace":
        # Backup current state in case of error
        backup = operations._task_storage.copy()

        try:
            # Clear existing tasks
            operations._task_storage["tasks"] = {}
            operations._task_storage["next_id"] = file_next_id
            operations._task_storage["total_count"] = file_storage["total_count"]

            # Load all tasks from file
            for task_id, task in file_tasks.items():
                operations._task_storage["tasks"][task_id] = task
                tasks_loaded += 1

            logger.info(
                f"[TODO] Replaced all tasks with {tasks_loaded} tasks from file"
            )

        except Exception as e:
            # Restore backup on error
            operations._task_storage = backup
            logger.error(f"[TODO] Load failed, restored backup: {e}")
            raise BasicAgentToolsError(f"Failed to load tasks: {e}") from e

    elif merge_mode == "merge":
        # Add tasks that don't conflict
        current_tasks = operations._task_storage["tasks"]

        for task_id, task in file_tasks.items():
            if task_id in current_tasks:
                # Skip conflicting task
                tasks_skipped += 1
                logger.debug(f"[TODO] Skipped task {task_id} (ID conflict)")
            else:
                # Add non-conflicting task
                current_tasks[task_id] = task
                tasks_loaded += 1

        # Update next_id to be safe
        operations._task_storage["next_id"] = max(
            operations._task_storage["next_id"], file_next_id
        )
        operations._task_storage["total_count"] += tasks_loaded

        logger.info(
            f"[TODO] Merged {tasks_loaded} tasks (skipped {tasks_skipped} conflicts)"
        )

    elif merge_mode == "merge_renumber":
        # Build ID mapping for renumbering
        current_tasks = operations._task_storage["tasks"]
        id_mapping = _build_id_mapping(
            file_tasks, current_tasks, operations._task_storage["next_id"]
        )

        # Add tasks with updated IDs and dependencies
        for old_id, task in file_tasks.items():
            new_id = id_mapping[old_id]

            # Update task ID
            updated_task = task.copy()
            updated_task["id"] = new_id

            # Update dependencies
            updated_task = _update_task_dependencies(updated_task, id_mapping)

            # Add to storage
            current_tasks[new_id] = updated_task
            tasks_loaded += 1

            # Track renumbering
            if old_id != new_id:
                tasks_renumbered.append({"old_id": old_id, "new_id": new_id})

        # Update next_id to account for new tasks
        all_ids = list(current_tasks.keys())
        operations._task_storage["next_id"] = max(all_ids) + 1 if all_ids else 1
        operations._task_storage["total_count"] += tasks_loaded

        logger.info(
            f"[TODO] Merged and renumbered {tasks_loaded} tasks "
            f"({len(tasks_renumbered)} renumbered)"
        )

    # Build result
    result = {
        "success": True,
        "file_path": str(file_path_obj.absolute()),
        "tasks_loaded": tasks_loaded,
        "tasks_skipped": tasks_skipped,
        "mode_used": merge_mode,
        "message": f"Loaded {tasks_loaded} tasks from {file_path_obj.name}",
    }

    if merge_mode == "merge_renumber":
        result["tasks_renumbered"] = tasks_renumbered

    return result
