"""Common exceptions for basic-open-agent-tools."""


class BasicAgentToolsError(Exception):
    """Base exception for all basic-open-agent-tools errors."""

    pass


class FileSystemError(BasicAgentToolsError):
    """Exception for file system operations."""

    pass


class DataError(BasicAgentToolsError):
    """Exception for data operations."""

    pass


class ValidationError(DataError):
    """Exception for data validation operations."""

    pass


class SerializationError(DataError):
    """Exception for data serialization/deserialization operations."""

    pass


class DateTimeError(BasicAgentToolsError):
    """Exception for date and time operations."""

    pass


class CodeAnalysisError(BasicAgentToolsError):
    """Exception for code analysis operations."""

    pass


class ProfilingError(BasicAgentToolsError):
    """Exception for profiling and performance analysis operations."""

    pass


class StaticAnalysisError(BasicAgentToolsError):
    """Exception for static analysis output parsing operations."""

    pass


class GitError(BasicAgentToolsError):
    """Exception for git repository operations."""

    pass
