# TODO List Module ✅

**Simple in-memory task management for AI agents**

A minimal todo list tool that allows AI agents to track tasks during a single session. Tasks exist only in memory and are designed for the agent's own workflow management and self-organization.

## Features

- **In-Memory Storage**: Tasks persist only for the current session
- **Auto-Incrementing IDs**: Simple sequential task identification (1, 2, 3...)
- **Rich Task Data**: Priority, tags, dependencies, notes, timestamps
- **Status Management**: 6 status types from open to completed
- **Dependency Tracking**: Link tasks with circular dependency prevention
- **Agent-Friendly**: Google ADK compatible function signatures
- **No Persistence**: Clean slate every session, no external dependencies

## Quick Start

```python
from basic_open_agent_tools.todo import (
    add_task, list_tasks, update_task, complete_task, get_task_stats
)

# Create a new task
result = add_task(
    title="Implement user authentication",
    priority="high",
    notes="Use OAuth2 with JWT tokens",
    tags=["security", "backend"],
    estimated_duration="2 hours",
    dependencies=[]
)
task_id = result["task"]["id"]

# List all tasks
all_tasks = list_tasks(status="", tag="")

# Update task status
update_task(
    task_id=task_id,
    title="Implement OAuth2 authentication",
    status="in_progress",
    priority="urgent",
    notes="Updated requirements - use Auth0",
    tags=["security", "backend", "auth0"],
    estimated_duration="3 hours",
    dependencies=[]
)

# Mark as completed
complete_task(task_id)

# Get statistics
stats = get_task_stats()
print(f"Total tasks: {stats['total_tasks']}")
```

## Task Data Structure

Each task contains:

```python
{
    "id": 1,                           # Auto-incrementing unique ID
    "title": "Implement feature X",    # Task description
    "status": "in_progress",           # Current status
    "priority": "high",                # Priority level
    "created_at": "2024-01-15T...",    # ISO timestamp
    "updated_at": "2024-01-15T...",    # Last modified timestamp
    "notes": "Additional details",     # Extended description
    "tags": ["feature", "api"],        # Categorization tags
    "estimated_duration": "2 hours",   # Time estimate
    "dependencies": [2, 3]             # Task IDs this depends on
}
```

## Task Statuses

- **open** - Newly created, not started
- **in_progress** - Currently being worked on
- **blocked** - Waiting on external dependency
- **deferred** - Intentionally postponed
- **completed** - Successfully finished
- **cancelled** - Abandoned/no longer needed

## Available Functions

### Core Operations

#### `add_task(title, priority, notes, tags, estimated_duration, dependencies) -> Dict`
Create a new task with auto-incrementing ID.

**Parameters:**
- `title: str` - Task description (required, max 500 chars)
- `priority: str` - Priority level ('low', 'medium', 'high', 'urgent')
- `notes: str` - Additional details (max 2000 chars)
- `tags: List[str]` - Categorization tags (max 20 tags, 50 chars each)
- `estimated_duration: str` - Time estimate (max 100 chars)
- `dependencies: List[int]` - Task IDs this task depends on

**Returns:**
```python
{
    "success": True,
    "task": {...},  # Full task object
    "message": "Task created with ID 1"
}
```

#### `list_tasks(status, tag) -> Dict`
List all tasks or filter by status and/or tag.

**Parameters:**
- `status: str` - Filter by status (empty string for no filter)
- `tag: str` - Filter by tag (empty string for no filter)

**Returns:**
```python
{
    "success": True,
    "tasks": [...],  # Array of task objects
    "count": 5,
    "total_tasks": 10,
    "filters_applied": {"status": "open", "tag": "api"}
}
```

#### `get_task(task_id) -> Dict`
Retrieve a single task by ID.

**Parameters:**
- `task_id: int` - Unique task identifier

**Returns:**
```python
{
    "success": True,
    "task": {...},  # Full task object
    "message": "Task 1 retrieved successfully"
}
```

#### `update_task(task_id, title, status, priority, notes, tags, estimated_duration, dependencies) -> Dict`
Update any field of an existing task.

**Parameters:**
- `task_id: int` - Task to update
- All other parameters same as `add_task`

**Returns:**
```python
{
    "success": True,
    "task": {...},  # Updated task object
    "message": "Task 1 updated successfully"
}
```

#### `delete_task(task_id) -> Dict`
Remove a task from memory.

**Parameters:**
- `task_id: int` - Task to delete

**Returns:**
```python
{
    "success": True,
    "message": "Task 1 deleted successfully",
    "deleted_task_id": 1
}
```

#### `complete_task(task_id) -> Dict`
Convenience method to mark task as completed.

**Parameters:**
- `task_id: int` - Task to complete

**Returns:**
```python
{
    "success": True,
    "task": {...},  # Updated task with status="completed"
    "message": "Task 1 marked as completed"
}
```

### Utility Functions

#### `get_task_stats() -> Dict`
Get summary statistics about all tasks.

**Returns:**
```python
{
    "success": True,
    "total_tasks": 10,
    "total_created": 15,  # Including deleted tasks
    "status_counts": {
        "open": 3,
        "in_progress": 2,
        "completed": 5,
        ...
    },
    "priority_counts": {
        "low": 2,
        "medium": 4,
        "high": 3,
        "urgent": 1
    },
    "tasks_with_dependencies": 3,
    "next_id": 16
}
```

#### `clear_all_tasks() -> Dict`
Clear all tasks from memory (for testing/reset).

**Returns:**
```python
{
    "success": True,
    "message": "Cleared 10 tasks from memory",
    "cleared_count": 10
}
```

## Usage Patterns

### Agent Workflow Management
```python
# Agent starts a complex task
add_task(
    title="Build user dashboard",
    priority="high",
    notes="Include charts and data tables",
    tags=["frontend", "dashboard"],
    estimated_duration="4 hours",
    dependencies=[]
)

# Break down into subtasks
add_task(
    title="Create chart components",
    priority="medium",
    notes="Use Chart.js library",
    tags=["frontend", "charts"],
    estimated_duration="1 hour",
    dependencies=[1]  # Depends on main task
)

# Track progress
update_task(2, "Create chart components", "in_progress", ...)
complete_task(2)
```

### Dependency Management
```python
# Create dependent tasks
api_task = add_task("Build API endpoints", "high", ..., [], ..., [])
frontend_task = add_task("Build frontend", "medium", ..., [], ..., [api_task["task"]["id"]])

# System prevents circular dependencies automatically
# This would raise an error:
# update_task(api_task["task"]["id"], ..., dependencies=[frontend_task["task"]["id"]])
```

### Status Filtering
```python
# Get all active work
active_tasks = list_tasks(status="in_progress", tag="")

# Get blocked items for review
blocked_tasks = list_tasks(status="blocked", tag="")

# Filter by category
backend_tasks = list_tasks(status="", tag="backend")
```

## Constraints and Limits

- **Maximum Tasks**: 50 tasks at any time
- **Task IDs**: Auto-increment, never reused within session
- **Title Length**: 500 characters maximum
- **Notes Length**: 2000 characters maximum
- **Tags**: Maximum 20 tags per task, 50 characters each
- **No Persistence**: Tasks cleared when session ends
- **Circular Dependencies**: Automatically prevented

## Error Handling

All functions use `BasicAgentToolsError` for consistent error handling:

```python
from basic_open_agent_tools.exceptions import BasicAgentToolsError

try:
    result = add_task("", "invalid_priority", "", [], "", [])
except BasicAgentToolsError as e:
    print(f"Validation failed: {e}")
```

Common errors:
- **Task not found**: Invalid task ID
- **Validation errors**: Invalid status, priority, or data
- **Task limit exceeded**: More than 50 tasks
- **Circular dependency**: Task depends on itself indirectly

## Integration with Agents

### Google ADK
```python
from google.adk.agents import Agent
import basic_open_agent_tools as boat

# Load todo tools
todo_tools = boat.load_all_todo_tools()

agent = Agent(
    name="TaskManagerAgent",
    tools=todo_tools,
    instruction="You can manage your own tasks using the todo functions..."
)
```

### LangChain
```python
from langchain.tools import StructuredTool
from basic_open_agent_tools.todo import add_task, list_tasks

tools = [
    StructuredTool.from_function(func=add_task),
    StructuredTool.from_function(func=list_tasks),
    # ... other todo functions
]
```

## Design Philosophy

This module follows the basic-open-agent-tools design principles:

- **Agent-Friendly Signatures**: Simple types, no defaults, clear parameters
- **Structured Returns**: Consistent dictionary responses with success indicators
- **Minimal Dependencies**: Pure Python, no external requirements
- **Session Scoped**: Clean state for each agent session
- **Self-Organization**: Agents manage their own workflow autonomously

## Use Cases

1. **Multi-Step Workflows**: Break complex tasks into manageable pieces
2. **Dependency Tracking**: Ensure prerequisites are completed first
3. **Progress Monitoring**: Track what's done vs. what's pending
4. **Context Switching**: Remember tasks when jumping between activities
5. **Workload Management**: Prioritize and organize agent activities
6. **Session Planning**: Structure agent work sessions effectively

The TODO module enables agents to operate more systematically and maintain better context awareness during complex operations.