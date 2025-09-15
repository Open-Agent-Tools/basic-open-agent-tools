# Simple In-Memory Agent TODO List Tool - Implementation Plan

## Overview
A minimal todo list tool for AI agents to track tasks during a single session. Tasks exist only in memory for the agent's own workflow management.

## Core Requirements

### Task Data Structure
```python
{
    "id": int,                    # Auto-incrementing ID (1, 2, 3...)
    "title": str,                 # Task description/title
    "status": str,                # Task status (see statuses below)
    "priority": str,              # Priority level ("low", "medium", "high", "urgent")
    "created_at": str,            # ISO timestamp when created
    "updated_at": str,            # ISO timestamp when last modified
    "notes": str,                 # Additional task details/notes
    "tags": List[str],            # Optional tags for categorization
    "estimated_duration": str,    # Optional time estimate
    "dependencies": List[int]     # List of task IDs this task depends on
}
```

### Supported Task Statuses
- **open** - Newly created, not started
- **in_progress** - Currently being worked on
- **blocked** - Waiting on external dependency
- **deferred** - Intentionally postponed
- **completed** - Successfully finished
- **cancelled** - Abandoned/no longer needed

### Core Operations

#### 1. `add_task(title: str, priority: str, notes: str, tags: List[str], estimated_duration: str, dependencies: List[int]) -> Dict[str, Any]`
- Creates new task with auto-incrementing ID
- Sets status to "open"
- Records creation timestamp
- Returns task dictionary

#### 2. `list_tasks(status: str, tag: str) -> Dict[str, Any]`
- Lists all tasks or filtered by status/tag
- If no filters provided, returns all tasks
- Returns dict with tasks array and count

#### 3. `get_task(task_id: int) -> Dict[str, Any]`
- Retrieves single task by ID
- Returns task dictionary or error if not found

#### 4. `update_task(task_id: int, title: str, status: str, priority: str, notes: str, tags: List[str], estimated_duration: str, dependencies: List[int]) -> Dict[str, Any]`
- Updates any field of existing task
- Updates timestamp
- Returns updated task dictionary

#### 5. `delete_task(task_id: int) -> Dict[str, Any]`
- Removes task from memory
- Returns success confirmation

#### 6. `complete_task(task_id: int) -> Dict[str, Any]`
- Convenience method to mark task as completed
- Updates status and timestamp
- Returns updated task

#### 7. `get_task_stats() -> Dict[str, Any]`
- Returns summary statistics
- Count by status, total tasks, etc.

## Implementation Details

### Data Storage
```python
# Global in-memory storage
_task_storage = {
    "tasks": {},           # Dict[int, Dict] - task_id -> task_data
    "next_id": 1,         # Auto-incrementing counter
    "total_count": 0      # Total tasks created (for stats)
}
```

### Error Handling
- Use `BasicAgentToolsError` for consistency
- Handle task not found, invalid status, dependency cycles
- Validate task limit (max 50 tasks)

### Function Signatures (Google ADK Compliant)
- All parameters use simple types (str, int, List[str], etc.)
- No default values
- Comprehensive docstrings for LLM understanding
- Return structured dictionaries with success/error info

### Constraints Enforcement
- **Task Limit**: Maximum 50 active tasks at any time
- **ID Management**: Auto-increment, never reuse IDs within session
- **Dependency Validation**: Prevent circular dependencies
- **Status Validation**: Only allow defined status values

## File Structure
```
src/basic_open_agent_tools/todo/
├── __init__.py           # Module exports
├── operations.py         # Core CRUD operations
├── validation.py         # Input validation and constraints
└── README.md            # Module documentation
```

## Function Examples

### Add Task
```python
result = add_task(
    title="Implement user authentication",
    priority="high",
    notes="Use OAuth2 with JWT tokens",
    tags=["security", "backend"],
    estimated_duration="2 hours",
    dependencies=[]
)
# Returns: {"success": True, "task": {...}, "message": "Task created with ID 1"}
```

### List Tasks
```python
# All tasks
result = list_tasks(status="", tag="")

# Filter by status
result = list_tasks(status="in_progress", tag="")

# Filter by tag
result = list_tasks(status="", tag="backend")
```

### Update Task
```python
result = update_task(
    task_id=1,
    title="Implement OAuth2 authentication",
    status="in_progress",
    priority="urgent",
    notes="Updated requirements - use Auth0",
    tags=["security", "backend", "auth0"],
    estimated_duration="3 hours",
    dependencies=[2]
)
```

## Integration with basic-open-agent-tools

### Module Loading
```python
# Add to helpers.py
def load_all_todo_tools():
    """Load all TODO list management tools."""
    return [
        add_task,
        list_tasks,
        get_task,
        update_task,
        delete_task,
        complete_task,
        get_task_stats
    ]

# Update load_all_tools() to include todo tools
```

### Agent Usage Pattern
```python
import basic_open_agent_tools as boat

# Load todo tools for agent
todo_tools = boat.load_all_todo_tools()
all_tools = boat.merge_tool_lists(
    boat.load_all_filesystem_tools(),
    todo_tools
)

# Agent can now manage its own tasks
agent = Agent(tools=all_tools)
```

## Success Criteria Validation

1. ✅ **Track multiple tasks**: `add_task()` with unique IDs
2. ✅ **Reference by ID**: `get_task(task_id)` and `update_task(task_id, ...)`
3. ✅ **Status awareness**: `list_tasks(status="pending")` vs `list_tasks(status="completed")`
4. ✅ **Workflow management**: Complete CRUD operations + status transitions
5. ✅ **Agent autonomy**: No human formatting, raw data structures returned

## Implementation Priority

1. **Core Operations** - Basic CRUD functionality
2. **Status Management** - Status validation and transitions
3. **Filtering & Search** - List operations with filters
4. **Statistics** - Task counts and summaries
5. **Validation** - Constraint enforcement and error handling
6. **Integration** - Helper functions and module loading
7. **Testing** - Comprehensive test coverage
8. **Documentation** - Module README and examples

## Testing Strategy

- **Unit Tests**: Each operation with valid/invalid inputs
- **Integration Tests**: Multi-operation workflows
- **Constraint Tests**: Task limits, circular dependencies
- **Agent Simulation**: Realistic usage patterns
- **Error Handling**: All failure modes covered

This tool will enable agents to maintain context and manage complex multi-step workflows autonomously while staying within the toolkit's design principles of simplicity and agent-friendliness.