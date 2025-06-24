# basic-open-agent-tools

An open foundational toolkit providing essential components for building AI agents with minimal dependencies for local (non-HTTP/API) actions. Designed to offer core utilities and interfaces that developers can easily integrate into their own agents to avoid excess boilerplate, while being simpler than solutions requiring MCP or A2A.

## Installation

```bash
pip install basic-open-agent-tools
```

Or with UV:
```bash
uv add basic-open-agent-tools
```

## Usage

```python
from basic_open_agent_tools import file_system

# File operations
content = file_system.read_file_to_string("file.txt")
file_system.write_file_from_string("output.txt", "Hello!")

# Directory operations  
files = file_system.list_directory_contents("/path/to/dir")
file_system.create_directory("new_dir")
```




# Best Practices for Contributors and Reviewers

## Regularly Sync Your Fork/Branch:

Before starting new work or submitting a PR, git pull upstream main to get the latest changes into your local main branch, then rebase your feature branch on top of it.

## Small, Focused Pull Requests:

Break down large features into smaller, atomic PRs.

## Clear Titles and Descriptions:

Use a consistent format (e.g., "Feat: Add user profile page," "Fix: Resolve login bug"). Include context, what changed, why, and how to test. Link to related issues (e.g., "Closes #123").

## Use Draft Pull Requests:

Contributors can open PRs as "Draft" and mark them "Ready for review" when complete. Draft PRs won't trigger required status checks or reviews.

## Descriptive Commit Messages:

Add well-written commit messages (subject line + body for details).

## Self-Review First:

Contributors should review their own PRs thoroughly before requesting reviews.

## Responsive to Feedback:

Contributors should address comments and questions from reviewers promptly. If changes are requested, push new commits to the same branch; the PR will automatically update.



