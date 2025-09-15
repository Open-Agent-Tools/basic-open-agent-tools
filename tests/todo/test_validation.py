"""Tests for todo validation functions."""

import pytest

from basic_open_agent_tools.todo.validation import (
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


class TestValidateTitle:
    """Test validate_title function."""

    def test_valid_title(self):
        """Test valid titles pass validation."""
        validate_title("Valid title")
        validate_title("A" * 500)  # Maximum length
        validate_title("Title with numbers 123")
        validate_title("Title with symbols !@#$%")

    def test_invalid_title_type(self):
        """Test invalid title types raise TypeError."""
        with pytest.raises(TypeError, match="Title must be a string"):
            validate_title(123)

        with pytest.raises(TypeError, match="Title must be a string"):
            validate_title(None)

        with pytest.raises(TypeError, match="Title must be a string"):
            validate_title([])

    def test_empty_title(self):
        """Test empty titles raise ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_title("")

        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_title("   ")  # Whitespace only

        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_title("\t\n")  # Whitespace only

    def test_title_too_long(self):
        """Test titles exceeding length limit raise ValueError."""
        with pytest.raises(ValueError, match="Title cannot exceed 500 characters"):
            validate_title("A" * 501)


class TestValidateStatus:
    """Test validate_status function."""

    def test_valid_statuses(self):
        """Test all valid statuses pass validation."""
        valid_statuses = [
            "open",
            "in_progress",
            "blocked",
            "deferred",
            "completed",
            "cancelled",
        ]
        for status in valid_statuses:
            validate_status(status)

    def test_invalid_status_type(self):
        """Test invalid status types raise TypeError."""
        with pytest.raises(TypeError, match="Status must be a string"):
            validate_status(123)

        with pytest.raises(TypeError, match="Status must be a string"):
            validate_status(None)

    def test_invalid_status_value(self):
        """Test invalid status values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            validate_status("invalid_status")

        with pytest.raises(ValueError, match="Invalid status"):
            validate_status("pending")  # Not in our valid list

        with pytest.raises(ValueError, match="Invalid status"):
            validate_status("")


class TestValidatePriority:
    """Test validate_priority function."""

    def test_valid_priorities(self):
        """Test all valid priorities pass validation."""
        valid_priorities = ["low", "medium", "high", "urgent"]
        for priority in valid_priorities:
            validate_priority(priority)

    def test_invalid_priority_type(self):
        """Test invalid priority types raise TypeError."""
        with pytest.raises(TypeError, match="Priority must be a string"):
            validate_priority(123)

        with pytest.raises(TypeError, match="Priority must be a string"):
            validate_priority(None)

    def test_invalid_priority_value(self):
        """Test invalid priority values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid priority"):
            validate_priority("invalid_priority")

        with pytest.raises(ValueError, match="Invalid priority"):
            validate_priority("critical")  # Not in our valid list

        with pytest.raises(ValueError, match="Invalid priority"):
            validate_priority("")


class TestValidateTaskCount:
    """Test validate_task_count function."""

    def test_valid_task_counts(self):
        """Test valid task counts pass validation."""
        validate_task_count(0)
        validate_task_count(25)
        validate_task_count(49)  # Just under limit

    def test_task_limit_exceeded(self):
        """Test task count at or above limit raises ValueError."""
        with pytest.raises(ValueError, match="Maximum task limit of 50 reached"):
            validate_task_count(50)

        with pytest.raises(ValueError, match="Maximum task limit of 50 reached"):
            validate_task_count(100)


class TestValidateTaskExists:
    """Test validate_task_exists function."""

    def test_valid_task_exists(self):
        """Test existing task passes validation."""
        tasks = {1: {"title": "Task 1"}, 2: {"title": "Task 2"}}
        validate_task_exists(1, tasks)
        validate_task_exists(2, tasks)

    def test_invalid_task_id_type(self):
        """Test invalid task ID types raise TypeError."""
        tasks = {1: {"title": "Task 1"}}

        with pytest.raises(TypeError, match="Task ID must be an integer"):
            validate_task_exists("1", tasks)

        with pytest.raises(TypeError, match="Task ID must be an integer"):
            validate_task_exists(None, tasks)

        with pytest.raises(TypeError, match="Task ID must be an integer"):
            validate_task_exists(1.5, tasks)

    def test_task_not_found(self):
        """Test non-existent task raises ValueError."""
        tasks = {1: {"title": "Task 1"}}

        with pytest.raises(ValueError, match="Task with ID 999 not found"):
            validate_task_exists(999, tasks)

        with pytest.raises(ValueError, match="Task with ID 2 not found"):
            validate_task_exists(2, tasks)


class TestValidateDependencies:
    """Test validate_dependencies function."""

    def test_valid_dependencies(self):
        """Test valid dependencies pass validation."""
        tasks = {1: {"title": "Task 1"}, 2: {"title": "Task 2"}}

        validate_dependencies([], tasks)  # Empty dependencies
        validate_dependencies([1], tasks)  # Single dependency
        validate_dependencies([1, 2], tasks)  # Multiple dependencies

    def test_invalid_dependencies_type(self):
        """Test invalid dependencies type raises TypeError."""
        tasks = {1: {"title": "Task 1"}}

        with pytest.raises(TypeError, match="Dependencies must be a list"):
            validate_dependencies("not_a_list", tasks)

        with pytest.raises(TypeError, match="Dependencies must be a list"):
            validate_dependencies(None, tasks)

    def test_invalid_dependency_id_type(self):
        """Test invalid dependency ID types raise TypeError."""
        tasks = {1: {"title": "Task 1"}}

        with pytest.raises(TypeError, match="must be an integer"):
            validate_dependencies(["1"], tasks)

        with pytest.raises(TypeError, match="must be an integer"):
            validate_dependencies([1.5], tasks)

    def test_dependency_not_found(self):
        """Test non-existent dependency raises ValueError."""
        tasks = {1: {"title": "Task 1"}}

        with pytest.raises(ValueError, match="Dependency task 999 not found"):
            validate_dependencies([999], tasks)

        with pytest.raises(ValueError, match="Dependency task 2 not found"):
            validate_dependencies([1, 2], tasks)

    def test_self_dependency_prevention(self):
        """Test prevention of self-dependencies."""
        tasks = {1: {"title": "Task 1"}, 2: {"title": "Task 2"}}

        with pytest.raises(ValueError, match="Task cannot depend on itself"):
            validate_dependencies([1], tasks, exclude_task_id=1)

        with pytest.raises(ValueError, match="Task cannot depend on itself"):
            validate_dependencies([2, 1], tasks, exclude_task_id=1)

    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        # Create tasks with dependencies: 1 -> 2 -> 3
        tasks = {
            1: {"title": "Task 1", "dependencies": [2]},
            2: {"title": "Task 2", "dependencies": [3]},
            3: {"title": "Task 3", "dependencies": []},
        }

        # Try to make task 3 depend on task 1 (would create cycle)
        with pytest.raises(ValueError, match="Circular dependency detected"):
            validate_dependencies([1], tasks, exclude_task_id=3)

        # Try to make task 2 depend on task 1 (would create cycle)
        with pytest.raises(ValueError, match="Circular dependency detected"):
            validate_dependencies([1], tasks, exclude_task_id=2)

    def test_complex_circular_dependency(self):
        """Test detection of complex circular dependencies."""
        # Create complex dependency chain: 1 -> 2 -> 3 -> 4
        tasks = {
            1: {"title": "Task 1", "dependencies": [2]},
            2: {"title": "Task 2", "dependencies": [3]},
            3: {"title": "Task 3", "dependencies": [4]},
            4: {"title": "Task 4", "dependencies": []},
        }

        # Try to make task 4 depend on task 1 (would create long cycle)
        with pytest.raises(ValueError, match="Circular dependency detected"):
            validate_dependencies([1], tasks, exclude_task_id=4)


class TestValidateTags:
    """Test validate_tags function."""

    def test_valid_tags(self):
        """Test valid tags pass validation."""
        validate_tags([])  # Empty list
        validate_tags(["tag1"])  # Single tag
        validate_tags(["tag1", "tag2", "tag3"])  # Multiple tags
        validate_tags(["a" * 50])  # Maximum length tag

    def test_invalid_tags_type(self):
        """Test invalid tags type raises TypeError."""
        with pytest.raises(TypeError, match="Tags must be a list"):
            validate_tags("not_a_list")

        with pytest.raises(TypeError, match="Tags must be a list"):
            validate_tags(None)

    def test_invalid_tag_type(self):
        """Test invalid tag types raise TypeError."""
        with pytest.raises(TypeError, match="All tags must be strings"):
            validate_tags([123])

        with pytest.raises(TypeError, match="All tags must be strings"):
            validate_tags(["valid", None])

        with pytest.raises(TypeError, match="All tags must be strings"):
            validate_tags(["valid", ["nested"]])

    def test_empty_tag(self):
        """Test empty tags raise ValueError."""
        with pytest.raises(ValueError, match="Tags cannot be empty"):
            validate_tags([""])

        with pytest.raises(ValueError, match="Tags cannot be empty"):
            validate_tags(["valid", "   "])

    def test_tag_too_long(self):
        """Test tags exceeding length limit raise ValueError."""
        with pytest.raises(ValueError, match="Tags cannot exceed 50 characters"):
            validate_tags(["a" * 51])

    def test_duplicate_tags(self):
        """Test duplicate tags raise ValueError."""
        with pytest.raises(ValueError, match="Duplicate tags are not allowed"):
            validate_tags(["tag1", "tag2", "tag1"])

    def test_too_many_tags(self):
        """Test too many tags raise ValueError."""
        many_tags = [f"tag{i}" for i in range(21)]  # 21 tags
        with pytest.raises(ValueError, match="Maximum 20 tags allowed"):
            validate_tags(many_tags)


class TestValidateEstimatedDuration:
    """Test validate_estimated_duration function."""

    def test_valid_durations(self):
        """Test valid durations pass validation."""
        validate_estimated_duration("")  # Empty duration
        validate_estimated_duration("1 hour")
        validate_estimated_duration("30 minutes")
        validate_estimated_duration("2-3 days")
        validate_estimated_duration("a" * 100)  # Maximum length

    def test_invalid_duration_type(self):
        """Test invalid duration type raises TypeError."""
        with pytest.raises(TypeError, match="Estimated duration must be a string"):
            validate_estimated_duration(123)

        with pytest.raises(TypeError, match="Estimated duration must be a string"):
            validate_estimated_duration(None)

    def test_duration_too_long(self):
        """Test duration exceeding length limit raises ValueError."""
        with pytest.raises(
            ValueError, match="Estimated duration cannot exceed 100 characters"
        ):
            validate_estimated_duration("a" * 101)


class TestValidateNotes:
    """Test validate_notes function."""

    def test_valid_notes(self):
        """Test valid notes pass validation."""
        validate_notes("")  # Empty notes
        validate_notes("Short note")
        validate_notes("a" * 2000)  # Maximum length

    def test_invalid_notes_type(self):
        """Test invalid notes type raises TypeError."""
        with pytest.raises(TypeError, match="Notes must be a string"):
            validate_notes(123)

        with pytest.raises(TypeError, match="Notes must be a string"):
            validate_notes(None)

        with pytest.raises(TypeError, match="Notes must be a string"):
            validate_notes([])

    def test_notes_too_long(self):
        """Test notes exceeding length limit raise ValueError."""
        with pytest.raises(ValueError, match="Notes cannot exceed 2000 characters"):
            validate_notes("a" * 2001)


class TestValidationIntegration:
    """Test validation functions working together."""

    def test_realistic_validation_scenarios(self):
        """Test realistic combinations of validations."""
        # Valid task data
        validate_title("Implement user authentication")
        validate_status("in_progress")
        validate_priority("high")
        validate_tags(["security", "backend", "authentication"])
        validate_estimated_duration("4-6 hours")
        validate_notes(
            "Use OAuth2 with JWT tokens. Reference external API documentation."
        )

        # Valid dependencies
        tasks = {
            1: {"title": "Setup database", "dependencies": []},
            2: {"title": "Create models", "dependencies": [1]},
        }
        validate_dependencies([1], tasks, exclude_task_id=2)

    def test_edge_case_combinations(self):
        """Test edge cases and boundary conditions."""
        # Maximum length title and notes
        validate_title("A" * 500)
        validate_notes("B" * 2000)

        # Maximum tags
        max_tags = [f"tag{i}" for i in range(20)]
        validate_tags(max_tags)

        # Complex dependency validation
        tasks = {}
        for i in range(1, 11):  # 10 tasks
            tasks[i] = {"title": f"Task {i}", "dependencies": [i - 1] if i > 1 else []}

        # Validate that task 10 can depend on task 9 (valid chain)
        validate_dependencies([9], tasks, exclude_task_id=10)
