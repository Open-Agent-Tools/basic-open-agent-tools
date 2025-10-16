"""Tests for todo operations."""

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.todo.operations import (
    add_task,
    clear_all_tasks,
    complete_task,
    delete_task,
    get_task,
    get_task_stats,
    list_tasks,
    update_task,
)


class TestAddTask:
    """Test add_task function."""

    def setup_method(self):
        """Clear tasks before each test."""
        clear_all_tasks()

    def test_add_task_success(self):
        """Test successful task creation."""
        result = add_task(
            title="Test task",
            priority="medium",
            notes="Test notes",
            tags=["test", "work"],
            estimated_duration="1 hour",
            dependencies=[],
        )

        assert result["success"] is True
        assert result["task"]["id"] == 1
        assert result["task"]["title"] == "Test task"
        assert result["task"]["priority"] == "medium"
        assert result["task"]["status"] == "open"
        assert result["task"]["notes"] == "Test notes"
        assert result["task"]["tags"] == ["test", "work"]
        assert result["task"]["estimated_duration"] == "1 hour"
        assert result["task"]["dependencies"] == []
        assert "created_at" in result["task"]
        assert "updated_at" in result["task"]

    def test_add_task_invalid_title(self):
        """Test add_task with invalid title."""
        with pytest.raises(BasicAgentToolsError):
            add_task(
                title="",
                priority="medium",
                notes="",
                tags=[],
                estimated_duration="",
                dependencies=[],
            )

    def test_add_task_invalid_priority(self):
        """Test add_task with invalid priority."""
        with pytest.raises(BasicAgentToolsError):
            add_task(
                title="Test task",
                priority="invalid",
                notes="",
                tags=[],
                estimated_duration="",
                dependencies=[],
            )

    def test_add_task_auto_increment_id(self):
        """Test that task IDs auto-increment."""
        task1 = add_task("Task 1", "low", "", [], "", [])
        task2 = add_task("Task 2", "low", "", [], "", [])

        assert task1["task"]["id"] == 1
        assert task2["task"]["id"] == 2

    def test_add_task_with_dependencies(self):
        """Test adding task with dependencies."""
        # Create dependency task
        dep_task = add_task("Dependency", "low", "", [], "", [])
        dep_id = dep_task["task"]["id"]

        # Create task with dependency
        result = add_task(
            title="Main task",
            priority="high",
            notes="",
            tags=[],
            estimated_duration="",
            dependencies=[dep_id],
        )

        assert result["success"] is True
        assert result["task"]["dependencies"] == [dep_id]

    def test_add_task_invalid_dependency(self):
        """Test adding task with non-existent dependency."""
        with pytest.raises(BasicAgentToolsError):
            add_task(
                title="Test task",
                priority="medium",
                notes="",
                tags=[],
                estimated_duration="",
                dependencies=[999],  # Non-existent task
            )


class TestListTasks:
    """Test list_tasks function."""

    def setup_method(self):
        """Clear tasks and add test data."""
        clear_all_tasks()

        # Add test tasks
        add_task("Open task", "low", "", ["work"], "", [])
        add_task("Progress task", "medium", "", ["personal"], "", [])
        update_task(
            2, "Progress task", "in_progress", "medium", "", ["personal"], "", []
        )

    def test_list_all_tasks(self):
        """Test listing all tasks."""
        result = list_tasks(status="", tag="")

        assert result["success"] is True
        assert result["count"] == 2
        assert result["total_tasks"] == 2
        assert len(result["tasks"]) == 2

    def test_list_tasks_by_status(self):
        """Test filtering tasks by status."""
        result = list_tasks(status="open", tag="")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["tasks"][0]["status"] == "open"

    def test_list_tasks_by_tag(self):
        """Test filtering tasks by tag."""
        result = list_tasks(status="", tag="work")

        assert result["success"] is True
        assert result["count"] == 1
        assert "work" in result["tasks"][0]["tags"]

    def test_list_tasks_combined_filters(self):
        """Test filtering by both status and tag."""
        result = list_tasks(status="in_progress", tag="personal")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["tasks"][0]["status"] == "in_progress"
        assert "personal" in result["tasks"][0]["tags"]

    def test_list_tasks_no_matches(self):
        """Test filtering with no matches."""
        result = list_tasks(status="completed", tag="")

        assert result["success"] is True
        assert result["count"] == 0
        assert result["tasks"] == []

    def test_list_tasks_invalid_status(self):
        """Test listing with invalid status."""
        with pytest.raises(BasicAgentToolsError):
            list_tasks(status="invalid", tag="")


class TestGetTask:
    """Test get_task function."""

    def setup_method(self):
        """Clear tasks and add test data."""
        clear_all_tasks()
        self.task = add_task("Test task", "medium", "Notes", ["tag"], "1h", [])

    def test_get_task_success(self):
        """Test successfully getting a task."""
        task_id = self.task["task"]["id"]
        result = get_task(task_id)

        assert result["success"] is True
        assert result["task"]["id"] == task_id
        assert result["task"]["title"] == "Test task"

    def test_get_task_not_found(self):
        """Test getting non-existent task."""
        with pytest.raises(BasicAgentToolsError):
            get_task(999)

    def test_get_task_invalid_id_type(self):
        """Test getting task with invalid ID type."""
        with pytest.raises(BasicAgentToolsError):
            get_task("invalid")


class TestUpdateTask:
    """Test update_task function."""

    def setup_method(self):
        """Clear tasks and add test data."""
        clear_all_tasks()
        self.task = add_task("Original", "low", "", [], "", [])
        self.task_id = self.task["task"]["id"]

    def test_update_task_success(self):
        """Test successful task update."""
        result = update_task(
            task_id=self.task_id,
            title="Updated title",
            status="in_progress",
            priority="high",
            notes="Updated notes",
            tags=["updated"],
            estimated_duration="2 hours",
            dependencies=[],
        )

        assert result["success"] is True
        assert result["task"]["title"] == "Updated title"
        assert result["task"]["status"] == "in_progress"
        assert result["task"]["priority"] == "high"
        assert result["task"]["notes"] == "Updated notes"
        assert result["task"]["tags"] == ["updated"]
        assert result["task"]["estimated_duration"] == "2 hours"

    def test_update_task_not_found(self):
        """Test updating non-existent task."""
        with pytest.raises(BasicAgentToolsError):
            update_task(999, "Title", "open", "low", "", [], "", [])

    def test_update_task_invalid_status(self):
        """Test updating with invalid status."""
        with pytest.raises(BasicAgentToolsError):
            update_task(self.task_id, "Title", "invalid", "low", "", [], "", [])

    def test_update_task_with_dependencies(self):
        """Test updating task with dependencies."""
        # Create dependency
        dep_task = add_task("Dependency", "low", "", [], "", [])
        dep_id = dep_task["task"]["id"]

        result = update_task(
            task_id=self.task_id,
            title="With dependency",
            status="blocked",
            priority="medium",
            notes="",
            tags=[],
            estimated_duration="",
            dependencies=[dep_id],
        )

        assert result["success"] is True
        assert result["task"]["dependencies"] == [dep_id]
        assert result["task"]["status"] == "blocked"

    def test_update_task_circular_dependency(self):
        """Test preventing circular dependencies."""
        # Create two tasks
        task_a = add_task("Task A", "low", "", [], "", [])
        task_b = add_task("Task B", "low", "", [], "", [task_a["task"]["id"]])

        # Try to make task_a depend on task_b (circular)
        with pytest.raises(BasicAgentToolsError):
            update_task(
                task_id=task_a["task"]["id"],
                title="Task A",
                status="open",
                priority="low",
                notes="",
                tags=[],
                estimated_duration="",
                dependencies=[task_b["task"]["id"]],
            )


class TestDeleteTask:
    """Test delete_task function."""

    def setup_method(self):
        """Clear tasks and add test data."""
        clear_all_tasks()
        self.task = add_task("Test task", "medium", "", [], "", [])
        self.task_id = self.task["task"]["id"]

    def test_delete_task_success(self):
        """Test successful task deletion."""
        result = delete_task(self.task_id, skip_confirm=True)

        assert isinstance(result, str)
        assert "deleted" in result.lower()
        assert str(self.task_id) in result

        # Verify task is deleted
        with pytest.raises(BasicAgentToolsError):
            get_task(self.task_id)

    def test_delete_task_not_found(self):
        """Test deleting non-existent task."""
        with pytest.raises(BasicAgentToolsError):
            delete_task(999, skip_confirm=True)


class TestCompleteTask:
    """Test complete_task function."""

    def setup_method(self):
        """Clear tasks and add test data."""
        clear_all_tasks()
        self.task = add_task("Test task", "medium", "", [], "", [])
        self.task_id = self.task["task"]["id"]

    def test_complete_task_success(self):
        """Test marking task as completed."""
        result = complete_task(self.task_id)

        assert result["success"] is True
        assert result["task"]["status"] == "completed"
        assert result["task"]["id"] == self.task_id

    def test_complete_task_not_found(self):
        """Test completing non-existent task."""
        with pytest.raises(BasicAgentToolsError):
            complete_task(999)


class TestGetTaskStats:
    """Test get_task_stats function."""

    def setup_method(self):
        """Clear tasks and add test data."""
        clear_all_tasks()

        # Add various tasks
        add_task("Open task 1", "low", "", [], "", [])
        add_task("Open task 2", "medium", "", [], "", [])
        add_task("Progress task", "high", "", [], "", [])
        update_task(3, "Progress task", "in_progress", "high", "", [], "", [])
        complete_task(1)

    def test_get_task_stats(self):
        """Test getting task statistics."""
        result = get_task_stats()

        assert result["success"] is True
        assert result["total_tasks"] == 3
        assert result["total_created"] == 3
        assert result["status_counts"]["open"] == 1
        assert result["status_counts"]["in_progress"] == 1
        assert result["status_counts"]["completed"] == 1
        assert result["priority_counts"]["low"] == 1
        assert result["priority_counts"]["medium"] == 1
        assert result["priority_counts"]["high"] == 1
        assert result["tasks_with_dependencies"] == 0
        assert result["next_id"] == 4


class TestClearAllTasks:
    """Test clear_all_tasks function."""

    def setup_method(self):
        """Clear tasks before each test."""
        clear_all_tasks()

    def test_clear_all_tasks(self):
        """Test clearing all tasks."""
        # Add some tasks
        add_task("Task 1", "low", "", [], "", [])
        add_task("Task 2", "medium", "", [], "", [])

        result = clear_all_tasks()

        assert result["success"] is True
        assert result["cleared_count"] == 2

        # Verify all tasks are cleared
        stats = get_task_stats()
        assert stats["total_tasks"] == 0
        assert stats["next_id"] == 1


class TestTaskConstraints:
    """Test task limits and constraints."""

    def setup_method(self):
        """Clear tasks before each test."""
        clear_all_tasks()

    def test_task_limit_enforcement(self):
        """Test that task limit is enforced."""
        # Add maximum allowed tasks (50)
        for i in range(50):
            add_task(f"Task {i + 1}", "low", "", [], "", [])

        # Verify we can't add more
        with pytest.raises(BasicAgentToolsError, match="Maximum task limit"):
            add_task("Overflow task", "low", "", [], "", [])

    def test_title_length_validation(self):
        """Test title length constraints."""
        # Valid title
        result = add_task("A" * 500, "low", "", [], "", [])
        assert result["success"] is True

        # Invalid title (too long)
        with pytest.raises(BasicAgentToolsError):
            add_task("A" * 501, "low", "", [], "", [])

    def test_notes_length_validation(self):
        """Test notes length constraints."""
        # Valid notes
        result = add_task("Title", "low", "A" * 2000, [], "", [])
        assert result["success"] is True

        # Invalid notes (too long)
        with pytest.raises(BasicAgentToolsError):
            add_task("Title", "low", "A" * 2001, [], "", [])


class TestIntegrationWorkflows:
    """Test realistic agent workflow scenarios."""

    def setup_method(self):
        """Clear tasks before each test."""
        clear_all_tasks()

    def test_agent_workflow_scenario(self):
        """Test a realistic agent workflow."""
        # Agent creates main task
        main_task = add_task(
            title="Build user dashboard",
            priority="high",
            notes="Include charts and data visualization",
            tags=["frontend", "dashboard"],
            estimated_duration="4 hours",
            dependencies=[],
        )
        main_task["task"]["id"]

        # Agent breaks down into subtasks
        api_task = add_task(
            title="Create API endpoints",
            priority="high",
            notes="REST API for dashboard data",
            tags=["backend", "api"],
            estimated_duration="2 hours",
            dependencies=[],
        )
        api_id = api_task["task"]["id"]

        charts_task = add_task(
            title="Implement chart components",
            priority="medium",
            notes="Use Chart.js library",
            tags=["frontend", "charts"],
            estimated_duration="1.5 hours",
            dependencies=[api_id],
        )
        charts_id = charts_task["task"]["id"]

        # Agent starts working
        update_task(
            api_id,
            "Create API endpoints",
            "in_progress",
            "high",
            "Working on user data endpoint",
            ["backend", "api"],
            "2 hours",
            [],
        )

        # Complete API task
        complete_task(api_id)

        # Start charts task (dependency resolved)
        update_task(
            charts_id,
            "Implement chart components",
            "in_progress",
            "medium",
            "Charts library integrated",
            ["frontend", "charts"],
            "1 hour",
            [api_id],
        )

        # Get progress report
        stats = get_task_stats()
        in_progress = list_tasks("in_progress", "")
        completed = list_tasks("completed", "")

        assert stats["total_tasks"] == 3
        assert stats["status_counts"]["completed"] == 1
        assert stats["status_counts"]["in_progress"] == 1
        assert stats["status_counts"]["open"] == 1
        assert in_progress["count"] == 1
        assert completed["count"] == 1

    def test_dependency_chain_workflow(self):
        """Test complex dependency chains."""
        # Create dependency chain: A -> B -> C -> D
        task_a = add_task("Task A", "high", "", [], "", [])
        task_b = add_task("Task B", "high", "", [], "", [task_a["task"]["id"]])
        task_c = add_task("Task C", "medium", "", [], "", [task_b["task"]["id"]])
        task_d = add_task("Task D", "low", "", [], "", [task_c["task"]["id"]])

        # Complete in order
        complete_task(task_a["task"]["id"])
        complete_task(task_b["task"]["id"])
        complete_task(task_c["task"]["id"])
        complete_task(task_d["task"]["id"])

        # Verify all completed
        completed_tasks = list_tasks("completed", "")
        assert completed_tasks["count"] == 4

    def test_blocked_task_workflow(self):
        """Test handling blocked tasks."""
        # Create task that gets blocked
        task = add_task("Implement feature", "high", "", [], "", [])
        task_id = task["task"]["id"]

        # Mark as blocked
        update_task(
            task_id,
            "Implement feature",
            "blocked",
            "high",
            "Waiting for external API documentation",
            [],
            "",
            [],
        )

        # Later, unblock and continue
        update_task(
            task_id,
            "Implement feature",
            "in_progress",
            "high",
            "API docs received, implementing now",
            [],
            "3 hours",
            [],
        )

        # Complete
        complete_task(task_id)

        final_task = get_task(task_id)
        assert final_task["task"]["status"] == "completed"
