"""Read-only git repository information and analysis tools.

This module provides functions to query git repository information using
read-only operations. No write operations (commit, push, merge) are included
for safety.
"""

from basic_open_agent_tools.git.branches import (
    get_branch_info,
    list_branches,
)
from basic_open_agent_tools.git.history import (
    get_file_at_commit,
    get_file_history,
    get_git_blame,
    get_git_log,
)
from basic_open_agent_tools.git.status import (
    get_current_branch,
    get_git_diff,
    get_git_status,
)

__all__ = [
    # Status and diff operations
    "get_git_status",
    "get_current_branch",
    "get_git_diff",
    # Log and blame operations
    "get_git_log",
    "get_git_blame",
    "get_file_history",
    "get_file_at_commit",
    # Branch information
    "list_branches",
    "get_branch_info",
]
