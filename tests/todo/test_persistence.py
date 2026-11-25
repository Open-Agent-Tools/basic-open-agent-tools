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
    add_task("Task 1", "high", "", ["high"], "", [])
    add_task("Task 2", "medium", "", ["medium"], "", [1])
    add_task("Task 3", "low", "", ["low"], "", [1, 2])


def test_save_tasks_to_file_basic(temp_dir, sample_tasks):
    """Test basic save operation."""
    file_path = os.path.join(temp_dir, "tasks.json")
    result = save_tasks_to_file(file_path, skip_confirm=True)

    assert result["success"] is True
    assert result["task_count"] == 3
    assert os.path.exists(file_path)

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

    save_tasks_to_file(file_path, skip_confirm=True)

    add_task("Task 4", "low", "", [], "", [])

    result = save_tasks_to_file(file_path, skip_confirm=True)

    assert result["success"] is True
    assert result["task_count"] == 4

    with open(file_path) as f:
        data = json.load(f)
    assert len(data["storage"]["tasks"]) == 4


def test_save_tasks_permission_error(temp_dir, sample_tasks):
    """Test save with permission denied."""
    readonly_dir = os.path.join(temp_dir, "readonly_dir")
    os.makedirs(readonly_dir)
    file_path = os.path.join(readonly_dir, "tasks.json")

    Path(file_path).touch()

    os.chmod(readonly_dir, 0o555)

    try:
        with pytest.raises(BasicAgentToolsError, match="Permission denied"):
            save_tasks_to_file(file_path, skip_confirm=True)
    finally:
        os.chmod(readonly_dir, 0o755)


def test_save_tasks_preserves_all_fields(temp_dir):
    """Test that save preserves all task fields."""
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
        "metadata": {"version": "1.0", "task_count": 5},
        "storage": {
            "tasks": {"1": {"id": 1}},
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
                    "dependencies": [999],
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
                    "dependencies": [2],
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
                    "dependencies": [1],
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


def test_load_tasks_replace_mode(temp_dir, sample_tasks):
    """Test loading tasks in replace mode."""
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    add_task("Different Task", "low", "", [], "", [])

    result = load_tasks_from_file(file_path, merge_mode="replace")

    assert result["success"] is True
    assert result["tasks_loaded"] == 3
    assert result["mode_used"] == "replace"

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3
    assert all(t["title"] in ["Task 1", "Task 2", "Task 3"] for t in tasks)


def test_load_tasks_replace_empty(temp_dir):
    """Test loading empty file in replace mode."""
    file_path = os.path.join(temp_dir, "empty.json")

    save_tasks_to_file(file_path, skip_confirm=True)

    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [])

    result = load_tasks_from_file(file_path, merge_mode="replace")

    assert result["success"] is True
    assert result["tasks_loaded"] == 0

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 0


def test_load_tasks_merge_mode_no_conflicts(temp_dir):
    """Test loading tasks in merge mode with ID conflicts."""
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [])
    add_task("Task 3", "low", "", [], "", [])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    add_task("Task 4", "low", "", [], "", [])
    add_task("Task 5", "low", "", [], "", [])

    result = load_tasks_from_file(file_path, merge_mode="merge")

    assert result["success"] is True
    assert result["tasks_loaded"] == 1
    assert result["tasks_skipped"] == 2

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3


def test_load_tasks_merge_mode_with_conflicts(temp_dir, sample_tasks):
    """Test loading tasks in merge mode with ID conflicts."""
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    result = load_tasks_from_file(file_path, merge_mode="merge")

    assert result["success"] is True
    assert result["tasks_loaded"] == 0
    assert result["tasks_skipped"] == 3

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3


def test_load_tasks_merge_mode_partial_conflicts(temp_dir):
    """Test loading tasks with some ID conflicts."""
    add_task("File Task 1", "low", "", [], "", [])
    add_task("File Task 2", "low", "", [], "", [])
    add_task("File Task 3", "low", "", [], "", [])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    add_task("Current Task 1", "low", "", [], "", [])

    result = load_tasks_from_file(file_path, merge_mode="merge")

    assert result["success"] is True
    assert result["tasks_loaded"] == 2
    assert result["tasks_skipped"] == 1

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3
    task_1 = next(t for t in tasks if t["id"] == 1)
    assert task_1["title"] == "Current Task 1"


def test_load_tasks_merge_renumber_no_conflicts(temp_dir):
    """Test merge_renumber mode with minimal conflicts."""
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    add_task("Task 10", "low", "", [], "", [])

    result = load_tasks_from_file(file_path, merge_mode="merge_renumber")

    assert result["success"] is True
    assert result["tasks_loaded"] == 2
    assert len(result["tasks_renumbered"]) == 1
    assert result["tasks_renumbered"][0]["old_id"] == 1
    assert result["tasks_renumbered"][0]["new_id"] == 3

    from basic_open_agent_tools.todo import list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 3


def test_load_tasks_merge_renumber_with_conflicts(temp_dir):
    """Test merge_renumber mode with ID conflicts."""
    add_task("File Task 1", "low", "", [], "", [])
    add_task("File Task 2", "low", "", [], "", [1])
    add_task("File Task 3", "low", "", [], "", [2])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    add_task("Current Task 1", "low", "", [], "", [])

    result = load_tasks_from_file(file_path, merge_mode="merge_renumber")

    assert result["success"] is True
    assert result["tasks_loaded"] == 3
    assert len(result["tasks_renumbered"]) == 1

    from basic_open_agent_tools.todo import get_task, list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 4

    renumbered = result["tasks_renumbered"][0]
    old_id = renumbered["old_id"]
    new_id = renumbered["new_id"]

    assert old_id == 1
    assert new_id == 4

    renumbered_task = get_task(new_id)["task"]
    assert renumbered_task["title"] == "File Task 1"

    task_2_id = next((t["id"] for t in tasks if t["title"] == "File Task 2"), None)
    task_2 = get_task(task_2_id)["task"]
    assert new_id in task_2["dependencies"]


def test_load_tasks_merge_renumber_dependency_remapping(temp_dir):
    """Test that dependencies are properly remapped when renumbering."""
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [1])
    add_task("Task 3", "low", "", [], "", [2])
    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    add_task("Current Task 1", "low", "", [], "", [])
    add_task("Current Task 2", "low", "", [], "", [1])

    result = load_tasks_from_file(file_path, merge_mode="merge_renumber")

    assert result["success"] is True
    assert result["tasks_loaded"] == 3
    assert len(result["tasks_renumbered"]) == 2

    from basic_open_agent_tools.todo import get_task, list_tasks

    tasks = list_tasks(status="", tag="")
    tasks = tasks["tasks"]
    assert len(tasks) == 5

    id_map = {r["old_id"]: r["new_id"] for r in result["tasks_renumbered"]}

    new_task_1_id = id_map[1]
    task_1 = get_task(new_task_1_id)["task"]
    assert task_1["title"] == "Task 1"
    assert task_1["dependencies"] == []

    new_task_2_id = id_map[2]
    task_2 = get_task(new_task_2_id)["task"]
    assert task_2["title"] == "Task 2"
    assert task_2["dependencies"] == [new_task_1_id]

    task_3 = next(t for t in tasks if t["title"] == "Task 3")
    assert task_3["dependencies"] == [new_task_2_id]


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


def test_roundtrip_save_and_load(temp_dir, sample_tasks):
    """Test that save -> load preserves all data."""
    from basic_open_agent_tools.todo import get_task_stats

    initial_stats = get_task_stats()
    file_path = os.path.join(temp_dir, "tasks.json")

    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()

    load_tasks_from_file(file_path, merge_mode="replace")

    final_stats = get_task_stats()
    assert final_stats["total_tasks"] == initial_stats["total_tasks"]
    assert (
        final_stats["status_counts"]["open"] == initial_stats["status_counts"]["open"]
    )


def test_roundtrip_preserves_dependencies(temp_dir):
    """Test that dependencies are preserved through save/load."""
    add_task("Task 1", "low", "", [], "", [])
    add_task("Task 2", "low", "", [], "", [1])
    add_task("Task 3", "low", "", [], "", [1, 2])

    file_path = os.path.join(temp_dir, "tasks.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    from basic_open_agent_tools.todo import get_task

    original_task_3 = get_task(3)["task"]

    clear_all_tasks()
    load_tasks_from_file(file_path, merge_mode="replace")

    loaded_task_3 = get_task(3)["task"]
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

    task_1 = get_task(1)["task"]
    task_2 = get_task(2)["task"]

    assert task_1["status"] == "completed"
    assert task_2["status"] == "open"


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
    long_notes = "A" * 2000
    add_task("Task with long notes", "low", long_notes, [], "", [])

    file_path = os.path.join(temp_dir, "long_notes.json")
    save_tasks_to_file(file_path, skip_confirm=True)

    clear_all_tasks()
    load_tasks_from_file(file_path, merge_mode="replace")

    from basic_open_agent_tools.todo import get_task

    task = get_task(1)["task"]
    assert len(task["notes"]) == 2000
    assert task["notes"] == long_notes
