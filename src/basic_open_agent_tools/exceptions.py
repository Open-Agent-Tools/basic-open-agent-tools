"""Common exceptions for basic-open-agent-tools."""


class BasicAgentToolsError(Exception):
    """Base exception for all basic-open-agent-tools errors."""

    pass


class FileSystemError(BasicAgentToolsError):
    """Exception for file system operations."""

    pass
