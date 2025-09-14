Create a Simple In-Memory Agent TO DO List Tool Requirements

# Tool Overview

Create a minimal todo_list tool that allows an AI agent to track tasks during a single session. Tasks exist only in memory and are meant for the agent's own reference. This should be a dict/json in memory. All functions should be minimalist designed for agentic use in frameworks like LagnGraph, Google ADK and AWS Strands.
Core Requirements

# Basic Operations
add_list: create a new list
add_task: Create a new task
list_task: Get all tasks or by status
update_task: Modify a task
delete_task: Remove a task
delete_list: remove list
complete_task: Mark task as done


Use a simple dictionary to store tasks in memory
Auto-increment task IDs (1, 2, 3...)
No validation beyond required parameters
Return raw data structures (no formatting)
No persistence between sessions

# Constraints
Maximum of 10 active lists
Maximum 100 tasks at a time per list
No task persistence beyond session
No formatting or display logic
Single-threaded (no concurrency handling needed)

# Success Criteria
The agent can:
Track multiple tasks during a conversation
Reference lists and task tasks by ID
Know what's pending vs completed
Manage its own workflow without human intervention