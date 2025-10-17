"""Integration tests for todo module."""

import pytest

from basic_open_agent_tools.exceptions import BasicAgentToolsError
from basic_open_agent_tools.todo import (
    add_task,
    clear_all_tasks,
    complete_task,
    delete_task,
    get_task,
    get_task_stats,
    list_tasks,
    update_task,
)


class TestTodoModuleIntegration:
    """Test todo module integration with package system."""

    def setup_method(self):
        """Clear tasks before each test."""
        clear_all_tasks()

    def test_module_imports(self):
        """Test that all functions can be imported from module."""
        # Test direct import from module
        from basic_open_agent_tools.todo import (
            add_task as imported_add_task,
        )
        from basic_open_agent_tools.todo import (
            clear_all_tasks as imported_clear_all_tasks,
        )
        from basic_open_agent_tools.todo import (
            complete_task as imported_complete_task,
        )
        from basic_open_agent_tools.todo import (
            delete_task as imported_delete_task,
        )
        from basic_open_agent_tools.todo import (
            get_task as imported_get_task,
        )
        from basic_open_agent_tools.todo import (
            get_task_stats as imported_get_task_stats,
        )
        from basic_open_agent_tools.todo import (
            list_tasks as imported_list_tasks,
        )
        from basic_open_agent_tools.todo import (
            update_task as imported_update_task,
        )

        # Verify functions are callable
        assert callable(imported_add_task)
        assert callable(imported_list_tasks)
        assert callable(imported_get_task)
        assert callable(imported_update_task)
        assert callable(imported_delete_task)
        assert callable(imported_complete_task)
        assert callable(imported_get_task_stats)
        assert callable(imported_clear_all_tasks)

    def test_helper_function_integration(self):
        """Test integration with helper functions."""
        from basic_open_agent_tools import load_all_todo_tools

        todo_tools = load_all_todo_tools()

        # Should have 8 functions
        assert len(todo_tools) == 8

        # All should be callable
        for tool in todo_tools:
            assert callable(tool)

        # Check specific functions are included
        function_names = [tool.__name__ for tool in todo_tools]
        expected_functions = [
            "add_task",
            "list_tasks",
            "get_task",
            "update_task",
            "delete_task",
            "complete_task",
            "get_task_stats",
            "clear_all_tasks",
        ]

        for expected in expected_functions:
            assert expected in function_names

    def test_load_all_tools_integration(self):
        """Test that todo tools are included in load_all_tools."""
        from basic_open_agent_tools import load_all_tools

        all_tools = load_all_tools()

        # Find todo functions in the complete tool list
        todo_function_names = [
            "add_task",
            "list_tasks",
            "get_task",
            "update_task",
            "delete_task",
            "complete_task",
            "get_task_stats",
            "clear_all_tasks",
        ]

        all_function_names = [tool.__name__ for tool in all_tools]

        for todo_func in todo_function_names:
            assert todo_func in all_function_names

    def test_package_level_import(self):
        """Test that todo module is accessible from package level."""
        import basic_open_agent_tools

        # Should be able to access todo module
        assert hasattr(basic_open_agent_tools, "todo")

        # Should be able to access functions through module
        assert hasattr(basic_open_agent_tools.todo, "add_task")
        assert hasattr(basic_open_agent_tools.todo, "list_tasks")


class TestRealisticAgentWorkflows:
    """Test realistic agent workflow scenarios end-to-end."""

    def setup_method(self):
        """Clear tasks before each test."""
        clear_all_tasks()

    def test_software_development_workflow(self):
        """Test a realistic software development workflow."""
        # Agent planning phase
        epic = add_task(
            title="Implement user management system",
            priority="high",
            notes="Complete user registration, login, and profile management",
            tags=["epic", "user-management", "backend"],
            estimated_duration="2 weeks",
            dependencies=[],
        )
        epic_id = epic["task"]["id"]

        # Break down into user stories
        auth_task = add_task(
            title="Implement user authentication",
            priority="high",
            notes="JWT-based auth with login/logout endpoints",
            tags=["auth", "security", "backend"],
            estimated_duration="3 days",
            dependencies=[],
        )
        auth_id = auth_task["task"]["id"]

        profile_task = add_task(
            title="Create user profile management",
            priority="medium",
            notes="CRUD operations for user profiles",
            tags=["profile", "backend", "crud"],
            estimated_duration="2 days",
            dependencies=[auth_id],
        )
        profile_id = profile_task["task"]["id"]

        frontend_task = add_task(
            title="Build user interface components",
            priority="medium",
            notes="React components for auth and profile",
            tags=["frontend", "react", "ui"],
            estimated_duration="4 days",
            dependencies=[auth_id, profile_id],
        )
        frontend_id = frontend_task["task"]["id"]

        # Agent starts execution
        update_task(
            auth_id,
            "Implement user authentication",
            "in_progress",
            "high",
            "Setting up JWT library and auth middleware",
            ["auth", "security", "backend"],
            "3 days",
            [],
        )

        # Complete auth task
        complete_task(auth_id)

        # Start profile task (dependency met)
        update_task(
            profile_id,
            "Create user profile management",
            "in_progress",
            "medium",
            "Implementing profile CRUD endpoints",
            ["profile", "backend", "crud"],
            "2 days",
            [auth_id],
        )

        # Complete profile task
        complete_task(profile_id)

        # Start frontend (all dependencies met)
        update_task(
            frontend_id,
            "Build user interface components",
            "in_progress",
            "medium",
            "Creating auth forms and profile components",
            ["frontend", "react", "ui"],
            "3 days",
            [auth_id, profile_id],
        )

        # Agent reviews progress
        stats = get_task_stats()
        assert stats["total_tasks"] == 4
        assert stats["status_counts"]["completed"] == 2
        assert stats["status_counts"]["in_progress"] == 1
        assert stats["status_counts"]["open"] == 1

        # Get work in progress
        in_progress_tasks = list_tasks("in_progress", "")
        assert in_progress_tasks["count"] == 1
        assert (
            in_progress_tasks["tasks"][0]["title"] == "Build user interface components"
        )

        # Complete remaining tasks
        complete_task(frontend_id)
        complete_task(epic_id)

        # Final verification
        final_stats = get_task_stats()
        assert final_stats["status_counts"]["completed"] == 4
        assert final_stats["status_counts"]["open"] == 0
        assert final_stats["status_counts"]["in_progress"] == 0

    def test_research_and_analysis_workflow(self):
        """Test a research and analysis workflow."""
        # Agent receives research task
        research_task = add_task(
            title="Analyze competitor landscape",
            priority="high",
            notes="Research top 5 competitors and their feature sets",
            tags=["research", "analysis", "competitive"],
            estimated_duration="1 week",
            dependencies=[],
        )
        research_id = research_task["task"]["id"]

        # Agent breaks down research
        data_collection = add_task(
            title="Collect competitor data",
            priority="high",
            notes="Gather public information on competitor products",
            tags=["research", "data-collection"],
            estimated_duration="2 days",
            dependencies=[],
        )
        data_id = data_collection["task"]["id"]

        feature_analysis = add_task(
            title="Analyze feature comparisons",
            priority="medium",
            notes="Compare features across competitors",
            tags=["analysis", "features"],
            estimated_duration="2 days",
            dependencies=[data_id],
        )
        feature_id = feature_analysis["task"]["id"]

        report_task = add_task(
            title="Generate competitive analysis report",
            priority="medium",
            notes="Synthesize findings into actionable report",
            tags=["reporting", "synthesis"],
            estimated_duration="1 day",
            dependencies=[feature_id],
        )
        report_id = report_task["task"]["id"]

        # Execute research workflow
        update_task(
            data_id,
            "Collect competitor data",
            "in_progress",
            "high",
            "Gathering data from websites and public APIs",
            ["research", "data-collection"],
            "2 days",
            [],
        )

        # Hit a roadblock
        update_task(
            data_id,
            "Collect competitor data",
            "blocked",
            "high",
            "Waiting for API access approval",
            ["research", "data-collection"],
            "2 days",
            [],
        )

        # Find alternative approach
        update_task(
            data_id,
            "Collect competitor data",
            "in_progress",
            "high",
            "Using web scraping and manual research as alternative",
            ["research", "data-collection", "web-scraping"],
            "3 days",
            [],
        )

        complete_task(data_id)

        # Continue workflow
        update_task(
            feature_id,
            "Analyze feature comparisons",
            "in_progress",
            "medium",
            "Creating feature comparison matrix",
            ["analysis", "features", "comparison"],
            "2 days",
            [data_id],
        )

        complete_task(feature_id)
        complete_task(report_id)
        complete_task(research_id)

        # Verify completed workflow
        completed_tasks = list_tasks("completed", "")
        assert completed_tasks["count"] == 4

        # Check for research tags
        research_tasks = list_tasks("", "research")
        assert research_tasks["count"] == 2

    def test_bug_fixing_workflow(self):
        """Test a bug fixing and testing workflow."""
        # Bug reported
        bug_task = add_task(
            title="Fix authentication timeout issue",
            priority="urgent",
            notes="Users experiencing session timeouts after 5 minutes",
            tags=["bug", "authentication", "urgent"],
            estimated_duration="1 day",
            dependencies=[],
        )
        bug_id = bug_task["task"]["id"]

        # Investigation phase
        investigation = add_task(
            title="Investigate timeout root cause",
            priority="urgent",
            notes="Analyze logs and identify timeout source",
            tags=["investigation", "debugging"],
            estimated_duration="4 hours",
            dependencies=[],
        )
        invest_id = investigation["task"]["id"]

        # Fix implementation
        fix_task = add_task(
            title="Implement timeout fix",
            priority="urgent",
            notes="Adjust session configuration and token refresh",
            tags=["fix", "implementation"],
            estimated_duration="2 hours",
            dependencies=[invest_id],
        )
        fix_id = fix_task["task"]["id"]

        # Testing
        test_task = add_task(
            title="Test authentication timeout fix",
            priority="high",
            notes="Verify fix works and doesn't break other functionality",
            tags=["testing", "verification"],
            estimated_duration="2 hours",
            dependencies=[fix_id],
        )
        test_id = test_task["task"]["id"]

        # Execute bug fix workflow
        update_task(
            invest_id,
            "Investigate timeout root cause",
            "in_progress",
            "urgent",
            "Analyzing server logs and session management code",
            ["investigation", "debugging", "logs"],
            "4 hours",
            [],
        )

        complete_task(invest_id)

        update_task(
            fix_id,
            "Implement timeout fix",
            "in_progress",
            "urgent",
            "Updating session timeout from 5 to 30 minutes",
            ["fix", "implementation", "session"],
            "2 hours",
            [invest_id],
        )

        complete_task(fix_id)

        update_task(
            test_id,
            "Test authentication timeout fix",
            "in_progress",
            "high",
            "Running automated and manual tests",
            ["testing", "verification", "qa"],
            "2 hours",
            [fix_id],
        )

        complete_task(test_id)
        complete_task(bug_id)

        # Verify urgent tasks completed
        urgent_tasks = list_tasks("", "urgent")
        completed_urgent = [
            t for t in urgent_tasks["tasks"] if t["status"] == "completed"
        ]
        assert len(completed_urgent) == 1

    def test_multi_agent_collaboration_simulation(self):
        """Test workflow that simulates multiple agents working together."""
        # Shared project setup
        add_task(
            title="Build e-commerce platform",
            priority="high",
            notes="Multi-team project with backend, frontend, and DevOps",
            tags=["project", "ecommerce", "collaboration"],
            estimated_duration="6 weeks",
            dependencies=[],
        )

        # Backend agent tasks
        backend_tasks = []
        for i, task_name in enumerate(
            ["API design", "Database schema", "Auth service", "Product service"]
        ):
            task = add_task(
                title=f"Backend: {task_name}",
                priority="high" if i < 2 else "medium",
                notes=f"Backend team task: {task_name}",
                tags=["backend", "api"]
                if "API" in task_name
                else ["backend", "database"]
                if "Database" in task_name
                else ["backend", "service"],
                estimated_duration="1 week",
                dependencies=backend_tasks[-1:] if backend_tasks else [],
            )
            backend_tasks.append(task["task"]["id"])

        # Frontend agent tasks
        frontend_tasks = []
        for task_name in [
            "Component library",
            "Product catalog",
            "Shopping cart",
            "Checkout flow",
        ]:
            deps = [backend_tasks[0]] if task_name != "Component library" else []
            task = add_task(
                title=f"Frontend: {task_name}",
                priority="medium",
                notes=f"Frontend team task: {task_name}",
                tags=["frontend", "react"],
                estimated_duration="1 week",
                dependencies=deps,
            )
            frontend_tasks.append(task["task"]["id"])

        # DevOps agent tasks
        devops_tasks = []
        for task_name in [
            "Infrastructure setup",
            "CI/CD pipeline",
            "Monitoring",
            "Deployment",
        ]:
            task = add_task(
                title=f"DevOps: {task_name}",
                priority="medium",
                notes=f"DevOps team task: {task_name}",
                tags=["devops", "infrastructure"],
                estimated_duration="3 days",
                dependencies=[],
            )
            devops_tasks.append(task["task"]["id"])

        # Simulate parallel work
        # Backend starts
        update_task(
            backend_tasks[0],
            "Backend: API design",
            "in_progress",
            "high",
            "Designing REST API specification",
            ["backend", "api"],
            "1 week",
            [],
        )

        # DevOps starts in parallel
        update_task(
            devops_tasks[0],
            "DevOps: Infrastructure setup",
            "in_progress",
            "medium",
            "Setting up AWS infrastructure",
            ["devops", "aws"],
            "3 days",
            [],
        )

        # Frontend starts component work (no dependencies)
        update_task(
            frontend_tasks[0],
            "Frontend: Component library",
            "in_progress",
            "medium",
            "Building reusable React components",
            ["frontend", "react", "components"],
            "1 week",
            [],
        )

        # Check parallel work
        in_progress = list_tasks("in_progress", "")
        assert in_progress["count"] == 3

        # Complete some tasks and cascade work
        complete_task(backend_tasks[0])  # API design done
        complete_task(devops_tasks[0])  # Infrastructure ready

        # Start dependent tasks
        update_task(
            backend_tasks[1],
            "Backend: Database schema",
            "in_progress",
            "high",
            "Implementing PostgreSQL schema",
            ["backend", "database"],
            "1 week",
            [backend_tasks[0]],
        )

        update_task(
            frontend_tasks[1],
            "Frontend: Product catalog",
            "in_progress",
            "medium",
            "Building product listing components",
            ["frontend", "products"],
            "1 week",
            [backend_tasks[0]],
        )

        # Get progress by team
        backend_progress = list_tasks("", "backend")
        frontend_progress = list_tasks("", "frontend")
        devops_progress = list_tasks("", "devops")

        assert backend_progress["count"] == 4
        assert frontend_progress["count"] == 4
        assert devops_progress["count"] == 4

        # Check project coordination
        stats = get_task_stats()
        assert (
            stats["total_tasks"] == 13
        )  # 1 project + 4 backend + 4 frontend + 4 devops
        assert stats["tasks_with_dependencies"] > 0


class TestErrorHandlingIntegration:
    """Test error handling across the todo system."""

    def setup_method(self):
        """Clear tasks before each test."""
        clear_all_tasks()

    def test_cascading_error_scenarios(self):
        """Test how errors cascade through the system."""
        # Create task with invalid data should fail completely
        with pytest.raises(BasicAgentToolsError):
            add_task("", "invalid_priority", "", [], "", [])

        # System should remain in consistent state
        stats = get_task_stats()
        assert stats["total_tasks"] == 0

        # Valid task should still work
        task = add_task("Valid task", "medium", "", [], "", [])
        assert task["success"] is True

    def test_dependency_error_handling(self):
        """Test error handling with dependencies."""
        # Create task
        task = add_task("Task 1", "medium", "", [], "", [])
        task_id = task["task"]["id"]

        # Try to create circular dependency should fail
        with pytest.raises(BasicAgentToolsError):
            update_task(task_id, "Task 1", "open", "medium", "", [], "", [task_id])

        # Original task should be unchanged
        original = get_task(task_id)
        assert original["task"]["dependencies"] == []

    def test_state_consistency_after_errors(self):
        """Test that system state remains consistent after errors."""
        # Add several tasks
        for i in range(5):
            add_task(f"Task {i + 1}", "medium", "", [], "", [])

        initial_stats = get_task_stats()
        assert initial_stats["total_tasks"] == 5

        # Try invalid operations
        with pytest.raises(BasicAgentToolsError):
            get_task(999)  # Non-existent task

        with pytest.raises(BasicAgentToolsError):
            delete_task(999, skip_confirm=True)  # Non-existent task

        with pytest.raises(BasicAgentToolsError):
            update_task(1, "", "open", "medium", "", [], "", [])  # Empty title

        # State should be unchanged
        final_stats = get_task_stats()
        assert final_stats["total_tasks"] == 5
        assert final_stats["status_counts"]["open"] == 5
