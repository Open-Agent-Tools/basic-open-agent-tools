# Security Policy

## Supported Versions

The following versions of basic-open-agent-tools are currently supported with security updates:

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 1.3.x   | :white_check_mark: | Current stable release |
| 1.2.x   | :white_check_mark: | Previous stable release |
| < 1.2   | :x:                | Legacy versions, please upgrade |

## Security Considerations for AI Agent Tools

This toolkit is designed for AI agent frameworks and includes security considerations specific to agent deployments:

### File System Operations
- **Path Validation**: All file operations validate paths to prevent directory traversal attacks
- **Safe Defaults**: Operations default to current working directory when no path specified
- **Input Sanitization**: File content and paths are validated before processing
- **No Arbitrary Execution**: File operations do not execute content as code

### Data Processing
- **Input Validation**: All data processing functions validate input types and formats
- **Size Limits**: Functions include safeguards against processing extremely large data sets
- **Safe Parsing**: JSON, CSV, and other parsers use safe parsing methods
- **No Code Execution**: Data processing does not evaluate or execute user input as code

### Agent Framework Integration
- **Type Safety**: All functions use JSON-serializable types for secure agent integration
- **Parameter Validation**: Function parameters are validated for type and format
- **Error Handling**: Consistent error patterns prevent information leakage
- **No Network Operations**: Core toolkit avoids network operations to prevent SSRF attacks

### Best Practices for Agent Deployments
1. **Validate Input**: Always validate data before passing to toolkit functions
2. **Limit Permissions**: Run agents with minimal necessary file system permissions
3. **Monitor Usage**: Log and monitor agent tool usage in production
4. **Sandbox Environment**: Consider running agents in sandboxed environments
5. **Regular Updates**: Keep the toolkit updated to receive security patches

## Known Vulnerabilities in Development Dependencies

### CVE-2025-53000: nbconvert Arbitrary Code Execution (Windows)

**Status**: Open - No patch available yet
**Severity**: HIGH (CVSS 8.5)
**Affected**: Windows users only
**Risk Level**: LOW (development-only dependency)

**Details**:
- **Vulnerability**: Uncontrolled search path in nbconvert allows arbitrary code execution via malicious `inkscape.bat` file
- **Attack Vector**: Only triggered when converting Jupyter notebooks with SVG output to PDF on Windows
- **Dependency Chain**: requirements.txt → jupyter/notebook → nbconvert (transitive)
- **Production Impact**: None (not a production dependency, not in pyproject.toml)
- **Development Impact**: Limited to Windows developers using `jupyter nbconvert --to pdf`

**Mitigation**:
- Avoid running `jupyter nbconvert --to pdf` on untrusted notebooks on Windows
- Use Linux/macOS for notebook conversion workflows
- Wait for upstream patch release from Jupyter project

**Monitoring**:
- GitHub Advisory: https://github.com/advisories/GHSA-xm59-rqc7-hhvf
- Project Alert: https://github.com/Open-Agent-Tools/basic-open-agent-tools/security/dependabot/12

**Why We're Not Removing Jupyter**:
- Development convenience for experimentation
- Clearly marked as optional in requirements.txt
- Not included in production dependencies
- Low risk given limited scope

We monitor this advisory and will update when a patch becomes available.

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Where to Report
- **Email**: Send details to unseriousai@gmail.com with subject "SECURITY: basic-open-agent-tools"
- **GitHub**: For non-critical issues, you may create a private security advisory on GitHub

### What to Include
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)
- Your contact information for follow-up

### Response Timeline
- **Initial Response**: Within 48 hours
- **Investigation**: 1-7 days depending on complexity
- **Fix Release**: Target within 14 days for critical issues
- **Public Disclosure**: After fix is released and users have time to update

### Process
1. **Report Received**: We acknowledge receipt and begin investigation
2. **Validation**: We reproduce and assess the vulnerability
3. **Fix Development**: We develop and test a fix
4. **Release**: We release a patched version
5. **Disclosure**: We publicly disclose details after users can update

### Security Updates
Security fixes are released as patch versions (e.g., 0.9.1 → 0.9.2) and are immediately available via:
- PyPI package updates
- GitHub releases with security tags
- Security advisories on GitHub

Thank you for helping keep basic-open-agent-tools secure!
