"""Secret pattern definitions for code scanning.

This module contains regex patterns for detecting various types of secrets
and credentials in source code.
"""

# Secret pattern definitions with severity levels
SECRET_PATTERNS: list[dict[str, str]] = [
    # AWS Keys
    {
        "name": "AWS Access Key ID",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": "high",
        "description": "AWS Access Key ID detected",
    },
    {
        "name": "AWS Secret Access Key",
        "pattern": r"aws_secret_access_key\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]",
        "severity": "high",
        "description": "AWS Secret Access Key detected",
    },
    # OpenAI API Keys
    {
        "name": "OpenAI API Key",
        "pattern": r"sk-[A-Za-z0-9]{48}",
        "severity": "high",
        "description": "OpenAI API key detected",
    },
    # Anthropic API Keys
    {
        "name": "Anthropic API Key",
        "pattern": r"sk-ant-[A-Za-z0-9_-]{95,}",
        "severity": "high",
        "description": "Anthropic API key detected",
    },
    # Generic API Keys
    {
        "name": "Generic API Key",
        "pattern": r"api[_-]?key\s*[:=]\s*['\"]([A-Za-z0-9_\-]{20,})['\"]",
        "severity": "medium",
        "description": "Generic API key pattern detected",
    },
    # Private Keys
    {
        "name": "RSA Private Key",
        "pattern": r"-----BEGIN RSA PRIVATE KEY-----",
        "severity": "high",
        "description": "RSA private key header detected",
    },
    {
        "name": "SSH Private Key",
        "pattern": r"-----BEGIN OPENSSH PRIVATE KEY-----",
        "severity": "high",
        "description": "OpenSSH private key header detected",
    },
    {
        "name": "PGP Private Key",
        "pattern": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
        "severity": "high",
        "description": "PGP private key block detected",
    },
    # Passwords
    {
        "name": "Password in Code",
        "pattern": r"password\s*[:=]\s*['\"]([^'\"]{8,})['\"]",
        "severity": "high",
        "description": "Password assignment detected",
    },
    {
        "name": "Database Password",
        "pattern": r"db_pass(?:word)?\s*[:=]\s*['\"]([^'\"]{6,})['\"]",
        "severity": "high",
        "description": "Database password detected",
    },
    # Connection Strings
    {
        "name": "Database Connection String",
        "pattern": r"(?:mysql|postgresql|mongodb)://[^:]+:[^@]+@",
        "severity": "high",
        "description": "Database connection string with credentials",
    },
    {
        "name": "JDBC Connection String",
        "pattern": r"jdbc:[^:]+://[^:]+:[^@]+@",
        "severity": "high",
        "description": "JDBC connection string with credentials",
    },
    # OAuth Tokens
    {
        "name": "OAuth Token",
        "pattern": r"oauth[_-]?token\s*[:=]\s*['\"]([A-Za-z0-9_\-\.]{20,})['\"]",
        "severity": "high",
        "description": "OAuth token detected",
    },
    {
        "name": "Bearer Token",
        "pattern": r"bearer\s+[A-Za-z0-9_\-\.=]{20,}",
        "severity": "high",
        "description": "Bearer token detected",
    },
    # JWT Tokens
    {
        "name": "JWT Token",
        "pattern": r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
        "severity": "medium",
        "description": "JWT token detected",
    },
    # GitHub Tokens
    {
        "name": "GitHub Token",
        "pattern": r"gh[pousr]_[A-Za-z0-9]{36,}",
        "severity": "high",
        "description": "GitHub personal access token detected",
    },
    # Slack Tokens
    {
        "name": "Slack Token",
        "pattern": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,}",
        "severity": "high",
        "description": "Slack token detected",
    },
    # Google API Keys
    {
        "name": "Google API Key",
        "pattern": r"AIza[0-9A-Za-z_-]{35}",
        "severity": "high",
        "description": "Google API key detected",
    },
    # Stripe Keys
    {
        "name": "Stripe API Key",
        "pattern": r"sk_live_[0-9a-zA-Z]{24,}",
        "severity": "high",
        "description": "Stripe live API key detected",
    },
    {
        "name": "Stripe Publishable Key",
        "pattern": r"pk_live_[0-9a-zA-Z]{24,}",
        "severity": "medium",
        "description": "Stripe live publishable key detected",
    },
    # Twilio Keys
    {
        "name": "Twilio API Key",
        "pattern": r"SK[0-9a-fA-F]{32}",
        "severity": "high",
        "description": "Twilio API key detected",
    },
    # SendGrid Keys
    {
        "name": "SendGrid API Key",
        "pattern": r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}",
        "severity": "high",
        "description": "SendGrid API key detected",
    },
    # Mailgun Keys
    {
        "name": "Mailgun API Key",
        "pattern": r"key-[0-9a-zA-Z]{32}",
        "severity": "high",
        "description": "Mailgun API key detected",
    },
    # Heroku Keys
    {
        "name": "Heroku API Key",
        "pattern": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        "severity": "medium",
        "description": "Heroku API key (UUID format) detected",
    },
    # Generic High Entropy Strings (potential secrets)
    {
        "name": "High Entropy String",
        "pattern": r"['\"]([A-Za-z0-9+/=]{40,})['\"]",
        "severity": "low",
        "description": "High entropy string (potential secret)",
    },
]


def get_all_patterns() -> list[dict[str, str]]:
    """Get all secret patterns.

    Returns:
        List of pattern dictionaries with name, pattern, severity, description
    """
    return SECRET_PATTERNS.copy()


def get_patterns_by_severity(severity: str) -> list[dict[str, str]]:
    """Get secret patterns filtered by severity level.

    Args:
        severity: Severity level to filter by ("high", "medium", "low")

    Returns:
        List of pattern dictionaries matching the severity level

    Raises:
        ValueError: If severity is not "high", "medium", or "low"
    """
    if severity not in ["high", "medium", "low"]:
        raise ValueError(f"Invalid severity: {severity}. Must be high, medium, or low")

    return [p for p in SECRET_PATTERNS if p["severity"] == severity]


def get_high_severity_patterns() -> list[dict[str, str]]:
    """Get only high severity secret patterns.

    Returns:
        List of high severity pattern dictionaries
    """
    return get_patterns_by_severity("high")
