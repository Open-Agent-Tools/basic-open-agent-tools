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
