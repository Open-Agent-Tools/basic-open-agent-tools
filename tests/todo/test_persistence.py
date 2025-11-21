"""Tests for task persistence operations (save/load/validate)."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.todo import (
    add_task,
    clear_all_tasks,
    complete_task,
    load_tasks_from_file,
    save_tasks_to_file,
    validate_task_file,
)


@pytest.fixture(autouse=True)
def clear_tasks():
    """Clear all tasks before and after each test."""
    clear_all_tasks()
    yield
    clear_all_tasks()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    # Add tasks with dependencies
    # add_task(title, priority, notes, tags, estimated_duration, dependencies)
    add_task("Task 1", "high", "", ["high"], "", [])
    add_task("Task 2", "medium", "", ["medium"], "", [1])
    add_task("Task 3", "low", "", ["low"], "", [1, 2])


# === SAVE TESTS ===


def test_save_tasks_to_file_basic(temp_dir, sample_tasks):
    """Test basic save operation."""
    file_path = os.path.join(temp_dir, "tasks.json")
    result = save_tasks_to_file(file_path, skip_confirm=True)

    assert result["success"] is True
    assert result["task_count"] == 3
    assert os.path.exists(file_path)

    # Verify file structure
    with open(file_path) as f:
        data = json.load(f)

    assert "metadata" in data
    assert "storage" in data
    assert data["metadata"]["version"] == "1.0"
    assert data["metadata"]["task_count"] == 3
    assert len(data["storage"]["tasks"]) == 3


def test_save_tasks_empty(temp_dir):
    """Test saving with no tasks."""
    file_path = os.path.join(temp_dir, "empty.json")
    result = save_tasks_to_file(file_path, skip_confirm=True)

    assert result["success"] is True
    assert result["task_count"] == 0

    with open(file_path) as f:
        data = json.load(f)

    assert data["metadata"]["task_count"] == 0
    assert len(data["storage"]["tasks"]) == 0


def test_save_tasks_creates_parent_dirs(temp_dir):
    """Test that save creates parent directories if needed."""
    file_path = os.path.join(temp_dir, "nested", "dir", "tasks.json")
    result = save_tasks_to_file(file_path, skip_confirm=True)

    assert result["success"] is True
    assert os.path.exists(file_path)


def test_save_tasks_overwrite_existing(temp_dir, sample_tasks):
    """Test overwriting existing file."""
    file_path = os.path.join(temp_dir, "tasks.json")

    # Create first file
    save_tasks_to_file(file_path, skip_confirm=True)

    # Add another task
    add_task("Task 4", "low", "", [], "", [])

    # Overwrite
    result = save_tasks_to_file(file_path, skip_confirm=True)

    assert result["success"] is True
    assert result["task_count"] == 4

    # Verify new file has 4 tasks
    with open(file_path) as f:
        data = json.load(f)
    assert len(data["storage"]["tasks"]) == 4


def test_save_tasks_permission_error(temp_dir, sample_tasks):
    """Test save with permission denied."""
    file_path = os.path.join(temp_dir, "readonly.json")

    # Create file and make it readonly
    Path(file_path).touch()
    os.chmod(file_path, 0o444)

    try:
        with pytest.raises(BasicAgentToolsError, match="Permission denied"):
            save_tasks_to_file(file_path, skip_confirm=True)
    finally:
        # Clean up
        os.chmod(file_path, 0o644)


def test_save_tasks_preserves_all_fields(temp_dir):
    """Test that save preserves all task fields."""
    # Add task with all fields populated
    # add_task(title, priority, notes, tags, estimated_duration, dependencies)
    add_task("Complex Task", "medium", "Important notes", ["tag1", "tag2"], "120", [])

    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    with open(file_path) as f:
        data = json.load(f)

    task = list(data["storage"]["tasks"].values())[0]
    assert task["title"] == "Complex Task"
    assert task["priority"] == "medium"
    assert task["tags"] == ["tag1", "tag2"]
    assert task["notes"] == "Important notes"
    assert task["estimated_duration"] == "120"
    assert "created_at" in task
    assert "updated_at" in task


# === VALIDATE TESTS ===


def test_validate_task_file_valid(temp_dir, sample_tasks):
    """Test validating a valid file."""
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    result = validate_task_file(file_path)

    assert result["valid"] is True
    assert result["task_count"] == 3
    assert len(result["errors"]) == 0
    assert "metadata" in result


def test_validate_task_file_not_found(temp_dir):
    """Test validating non-existent file."""
    file_path = os.path.join(temp_dir, "missing.json")

    with pytest.raises(BasicAgentToolsError, match="File not found"):
        validate_task_file(file_path)


def test_validate_task_file_invalid_json(temp_dir):
    """Test validating file with invalid JSON."""
    file_path = os.path.join(temp_dir, "invalid.json")

    with open(file_path, "w") as f:
        f.write("not valid json {")

    result = validate_task_file(file_path)

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("Invalid JSON" in err for err in result["errors"])


def test_validate_task_file_missing_metadata(temp_dir):
    """Test validating file missing metadata."""
    file_path = os.path.join(temp_dir, "bad.json")

    data = {"storage": {"tasks": {}, "next_id": 1, "total_count": 0}}
    with open(file_path, "w") as f:
        json.dump(data, f)

    result = validate_task_file(file_path)

    assert result["valid"] is False
    assert any("metadata" in err for err in result["errors"])


def test_validate_task_file_wrong_version(temp_dir):
    """Test validating file with wrong version."""
    file_path = os.path.join(temp_dir, "bad.json")

    data = {
        "metadata": {"version": "2.0", "task_count": 0},
        "storage": {"tasks": {}, "next_id": 1, "total_count": 0},
    }
    with open(file_path, "w") as f:
        json.dump(data, f)

    result = validate_task_file(file_path)

    assert result["valid"] is False
    assert any("Unsupported version" in err for err in result["errors"])


def test_validate_task_file_task_count_mismatch(temp_dir):
    """Test validating file with task count mismatch."""
    file_path = os.path.join(temp_dir, "bad.json")

    data = {
        "metadata": {"version": "1.0", "task_count": 5},  # Says 5
        "storage": {
            "tasks": {"1": {"id": 1}},  # Only has 1
            "next_id": 2,
            "total_count": 1,
        },
    }
    with open(file_path, "w") as f:
        json.dump(data, f)

    result = validate_task_file(file_path)

    assert result["valid"] is False
    assert any("mismatch" in err for err in result["errors"])


def test_validate_task_file_missing_required_field(temp_dir):
    """Test validating task with missing required field."""
    file_path = os.path.join(temp_dir, "bad.json")

    data = {
        "metadata": {"version": "1.0", "task_count": 1},
        "storage": {
            "tasks": {
                "1": {
                    "id": 1,
                    "title": "Test",
                    # Missing status, priority, etc.
                }
            },
            "next_id": 2,
            "total_count": 1,
        },
    }
    with open(file_path, "w") as f:
        json.dump(data, f)

    result = validate_task_file(file_path)

    assert result["valid"] is False
    assert any("Missing required field" in err for err in result["errors"])


def test_validate_task_file_invalid_dependency(temp_dir):
    """Test validating task with invalid dependency reference."""
    file_path = os.path.join(temp_dir, "bad.json")

    data = {
        "metadata": {"version": "1.0", "task_count": 1},
        "storage": {
            "tasks": {
                "1": {
                    "id": 1,
                    "title": "Test",
                    "status": "open",
                    "priority": 1,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                    "notes": "",
                    "tags": [],
                    "estimated_duration": 0,
                    "dependencies": [999],  # Non-existent task
                }
            },
            "next_id": 2,
            "total_count": 1,
        },
    }
    with open(file_path, "w") as f:
        json.dump(data, f)

    result = validate_task_file(file_path)

    assert result["valid"] is False
    assert any("non-existent task" in err for err in result["errors"])


def test_validate_task_file_circular_dependency(temp_dir):
    """Test validating tasks with circular dependencies."""
    file_path = os.path.join(temp_dir, "bad.json")

    data = {
        "metadata": {"version": "1.0", "task_count": 2},
        "storage": {
            "tasks": {
                "1": {
                    "id": 1,
                    "title": "Task 1",
                    "status": "open",
                    "priority": 1,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                    "notes": "",
                    "tags": [],
                    "estimated_duration": 0,
                    "dependencies": [2],  # Depends on 2
                },
                "2": {
                    "id": 2,
                    "title": "Task 2",
                    "status": "open",
                    "priority": 1,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                    "notes": "",
                    "tags": [],
                    "estimated_duration": 0,
                    "dependencies": [1],  # Depends on 1 - circular!
                },
            },
            "next_id": 3,
            "total_count": 2,
        },
    }
    with open(file_path, "w") as f:
        json.dump(data, f)

    result = validate_task_file(file_path)

    assert result["valid"] is False
    assert any("Circular dependency" in err for err in result["errors"])


# === LOAD TESTS - REPLACE MODE ===


def test_load_tasks_replace_mode(temp_dir, sample_tasks):
    """Test loading tasks in replace mode."""
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    # Clear tasks and add a different one
    clear_all_tasks()
    add_task("Different Task", "low", "", [], "", [])

    # Load in replace mode
    result = load_tasks_from_file(file_path, merge_mode="replace")

    assert result["success"] is True
    assert result["tasks_loaded"] == 3
    assert result["mode_used"] == "replace"

    # Verify the different task is gone and original 3 are back
    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3
    assert all(t["title"] in ["Task 1", "Task 2", "Task 3"] for t in tasks)


def test_load_tasks_replace_empty(temp_dir):
    """Test loading empty file in replace mode."""
    file_path = os.path.join(temp_dir, "empty.json")

    # Save empty file
    save_tasks_to_file(file_path, skip_confirm=True)

    # Add some tasks
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [])

    # Load empty file
    result = load_tasks_from_file(file_path, merge_mode="replace")

    assert result["success"] is True
    assert result["tasks_loaded"] == 0

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 0


# === LOAD TESTS - MERGE MODE ===


def test_load_tasks_merge_mode_no_conflicts(temp_dir):
    """Test loading tasks in merge mode with ID conflicts."""
    # Create file with tasks 1, 2, 3
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [])
    add_task("Task 3", "low", "", [], "", [])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    # Clear resets next_id to 1, so adding tasks will create IDs 1 and 2
    # This means tasks 1 and 2 from the file will conflict
    clear_all_tasks()
    add_task("Task 4", "low", "", [], "", [])  # Gets ID 1
    add_task("Task 5", "low", "", [], "", [])  # Gets ID 2

    # Load in merge mode
    result = load_tasks_from_file(file_path, merge_mode="merge")

    assert result["success"] is True
    assert result["tasks_loaded"] == 1  # Only task 3 from file (no conflict)
    assert result["tasks_skipped"] == 2  # Tasks 1 and 2 from file (conflicted)

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3  # 2 current (1, 2) + 1 from file (3)


def test_load_tasks_merge_mode_with_conflicts(temp_dir, sample_tasks):
    """Test loading tasks in merge mode with ID conflicts."""
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    # Don't clear - keep existing tasks 1, 2, 3
    # Try to load file with tasks 1, 2, 3

    result = load_tasks_from_file(file_path, merge_mode="merge")

    assert result["success"] is True
    assert result["tasks_loaded"] == 0  # All skipped
    assert result["tasks_skipped"] == 3  # All conflicted

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3  # Original 3 unchanged


def test_load_tasks_merge_mode_partial_conflicts(temp_dir):
    """Test loading tasks with some ID conflicts."""
    # Create file with tasks 1, 2, 3
    add_task("File Task 1", "low", "", [], "", [])
    add_task("File Task 2", "low", "", [], "", [])
    add_task("File Task 3", "low", "", [], "", [])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    # Clear and add task 1 (conflict) and 4 (no conflict)
    clear_all_tasks()
    add_task("Current Task 1", "low", "", [], "", [])

    # This creates task ID 1 in current storage
    # File has tasks 1, 2, 3
    # So task 1 should be skipped, tasks 2 and 3 should be loaded

    result = load_tasks_from_file(file_path, merge_mode="merge")

    assert result["success"] is True
    assert result["tasks_loaded"] == 2  # Tasks 2 and 3
    assert result["tasks_skipped"] == 1  # Task 1

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3
    # Verify task 1 is the current one, not the file one
    task_1 = next(t for t in tasks if t["id"] == 1)
    assert task_1["title"] == "Current Task 1"


# === LOAD TESTS - MERGE_RENUMBER MODE ===


def test_load_tasks_merge_renumber_no_conflicts(temp_dir):
    """Test merge_renumber mode with no conflicts."""
    # Create file with tasks 1, 2, 3
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    # Clear and add different tasks
    clear_all_tasks()
    add_task("Task 10", "low", "", [], "", [])

    # Load in merge_renumber mode
    result = load_tasks_from_file(file_path, merge_mode="merge_renumber")

    assert result["success"] is True
    assert result["tasks_loaded"] == 2
    assert len(result["tasks_renumbered"]) == 0  # No conflicts

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3


def test_load_tasks_merge_renumber_with_conflicts(temp_dir):
    """Test merge_renumber mode with ID conflicts."""
    # Create file with tasks 1, 2, 3 (2 depends on 1)
    add_task("File Task 1", "low", "", [], "", [])
    add_task("File Task 2", "low", "", [], "", [1])
    add_task("File Task 3", "low", "", [], "", [2])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    # Clear and add current task 1
    clear_all_tasks()
    add_task("Current Task 1", "low", "", [], "", [])

    # Load in merge_renumber mode
    result = load_tasks_from_file(file_path, merge_mode="merge_renumber")

    assert result["success"] is True
    assert result["tasks_loaded"] == 3
    assert len(result["tasks_renumbered"]) == 1  # Task 1 renumbered

    from basic_open_agent_tools.todo import get_task, list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 4  # 1 current + 3 from file

    # Find the renumbered task
    renumbered = result["tasks_renumbered"][0]
    old_id = renumbered["old_id"]
    new_id = renumbered["new_id"]

    assert old_id == 1
    assert new_id == 2  # Should be renumbered to 2 (next available ID)

    # Verify task exists with new ID
    renumbered_task = get_task(new_id)
    assert renumbered_task["title"] == "File Task 1"

    # Verify dependencies were updated
    task_3_id = next(
        (t["id"] for t in tasks if t["title"] == "File Task 2"), None
    )  # Was task 2, depends on what's now task 2
    task_3 = get_task(task_3_id)
    assert new_id in task_3["dependencies"]  # Should depend on renumbered task


def test_load_tasks_merge_renumber_dependency_remapping(temp_dir):
    """Test that dependencies are properly remapped when renumbering."""
    # Create file with chain: 1 <- 2 <- 3
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [1])
    add_task("Task 3", "low", "", [], "", [2])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    # Clear and add tasks that conflict with 1 and 2
    clear_all_tasks()
    add_task("Current Task 1", "low", "", [], "", [])
    add_task("Current Task 2", "low", "", [], "", [1])

    # Now we have IDs 1, 2 in current storage
    # Loading should renumber file's 1 -> 3, 2 -> 4, 3 -> 5 (or similar)

    result = load_tasks_from_file(file_path, merge_mode="merge_renumber")

    assert result["success"] is True
    assert result["tasks_loaded"] == 3
    assert len(result["tasks_renumbered"]) == 2  # Tasks 1 and 2 renumbered

    from basic_open_agent_tools.todo import get_task, list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 5  # 2 current + 3 from file

    # Build mapping from renumbered list
    id_map = {r["old_id"]: r["new_id"] for r in result["tasks_renumbered"]}

    # File task 1 was renumbered
    new_task_1_id = id_map[1]
    task_1 = get_task(new_task_1_id)
    assert task_1["title"] == "Task 1"
    assert task_1["dependencies"] == []

    # File task 2 was renumbered and should depend on renumbered task 1
    new_task_2_id = id_map[2]
    task_2 = get_task(new_task_2_id)
    assert task_2["title"] == "Task 2"
    assert task_2["dependencies"] == [new_task_1_id]

    # File task 3 should depend on renumbered task 2
    # Find task 3 (was not renamed so should be ID 3 if available or higher)
    task_3 = next(t for t in tasks if t["title"] == "Task 3")
    assert task_3["dependencies"] == [new_task_2_id]


# === LOAD TESTS - ERROR HANDLING ===


def test_load_tasks_invalid_merge_mode(temp_dir, sample_tasks):
    """Test loading with invalid merge mode."""
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    with pytest.raises(BasicAgentToolsError, match="Invalid merge_mode"):
        load_tasks_from_file(file_path, merge_mode="invalid")


def test_load_tasks_file_not_found(temp_dir):
    """Test loading non-existent file."""
    file_path = os.path.join(temp_dir, "missing.json")

    with pytest.raises(BasicAgentToolsError, match="File not found"):
        load_tasks_from_file(file_path, merge_mode="replace")


def test_load_tasks_invalid_file(temp_dir):
    """Test loading invalid file."""
    file_path = os.path.join(temp_dir, "bad.json")

    with open(file_path, "w") as f:
        f.write("not valid json")

    with pytest.raises(BasicAgentToolsError, match="Invalid task file"):
        load_tasks_from_file(file_path, merge_mode="replace")


# === ROUNDTRIP TESTS ===


def test_roundtrip_save_and_load(temp_dir, sample_tasks):
    """Test that save -> load preserves all data."""
    from basic_open_agent_tools.todo import get_task_stats

    # Get initial state
    initial_stats = get_task_stats()
    file_path = os.path.join(temp_dir, "tasks.json")

    # Save
    save_tasks_to_file(file_path, skip_confirm=True)

    # Clear
    clear_all_tasks()

    # Load
    load_tasks_from_file(file_path, merge_mode="replace")

    # Compare
    final_stats = get_task_stats()
    assert final_stats["total_tasks"] == initial_stats["total_tasks"]
    assert (
        final_stats["status_counts"]["open"]
        == initial_stats["status_counts"]["open"]
    )


def test_roundtrip_preserves_dependencies(temp_dir):
    """Test that dependencies are preserved through save/load."""
    # Create tasks with complex dependencies
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [1])
    add_task("Task 3", "low", "", [], "", [1, 2])

    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    from basic_open_agent_tools.todo import get_task

    # Get original task 3
    original_task_3 = get_task(3)

    # Clear and reload
    clear_all_tasks()
    load_tasks_from_file(file_path, merge_mode="replace")

    # Verify dependencies preserved
    loaded_task_3 = get_task(3)
    assert loaded_task_3["dependencies"] == original_task_3["dependencies"]
    assert loaded_task_3["dependencies"] == [1, 2]


def test_roundtrip_preserves_completed_tasks(temp_dir):
    """Test that completed tasks are preserved."""
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [])
    complete_task(1)

    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    load_tasks_from_file(file_path, merge_mode="replace")

    from basic_open_agent_tools.todo import get_task

    task_1 = get_task(1)
    task_2 = get_task(2)

    assert task_1["status"] == "completed"
    assert task_2["status"] == "open"


# === EDGE CASES ===


def test_save_load_unicode_content(temp_dir):
    """Test saving and loading tasks with unicode content."""
    add_task("任务 1 - 中文", "low", "", ["標籤"], "", [])
    add_task("🚀 Emoji Task", "low", "", ["🏷️"], "", [])

    file_path = os.path.join(temp_dir, "unicode.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    load_tasks_from_file(file_path, merge_mode="replace")

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 2
    assert any("任务 1" in t["title"] for t in tasks)
    assert any("🚀" in t["title"] for t in tasks)


def test_save_load_large_number_of_tasks(temp_dir):
    """Test saving and loading many tasks."""
    # Create 50 tasks
    for i in range(50):
        add_task(f"Task {i}", "low", "", [], "", [])

    file_path = os.path.join(temp_dir, "many.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    result = load_tasks_from_file(file_path, merge_mode="replace")

    assert result["tasks_loaded"] == 50

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 50


def test_save_load_long_notes(temp_dir):
    """Test saving tasks with very long notes."""
    long_notes = "A" * 2000  # 2k character notes (max limit)
    # add_task(title, priority, notes, tags, estimated_duration, dependencies)
    add_task("Task with long notes", "low", long_notes, [], "", [])

    file_path = os.path.join(temp_dir, "long_notes.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    load_tasks_from_file(file_path, merge_mode="replace")

    from basic_open_agent_tools.todo import get_task

    task = get_task(1)
    assert len(task["notes"]) == 2000
    assert task["notes"] == long_notes
