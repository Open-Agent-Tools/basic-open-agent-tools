# Testing Guide

This project uses a dual testing strategy with both traditional unit tests and agent evaluation tests.

## Running Tests

### All Tests (Recommended for CI)
```bash
# Run all tests including agent evaluations (sequentially)
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=src/basic_open_agent_tools --cov-report=term-missing
```

### Traditional Unit Tests Only (Fast)
```bash
# Skip agent evaluation tests (faster, no API calls)
python3 -m pytest tests/ -v -m "not agent_evaluation"
```

### Agent Evaluation Tests Only (Requires Google API Key)
```bash
# Run only agent evaluation tests (sequential, rate-limited)
python3 -m pytest tests/ -v -m "agent_evaluation"
```

### Specific Test Categories
```bash
# File system tests only
python3 -m pytest tests/file_system/ -v

# Data processing tests only  
python3 -m pytest tests/data/ -v

# Text processing tests only
python3 -m pytest tests/text/ -v
```

## Test Types

### Traditional Unit Tests
- **Purpose**: Test individual functions and modules
- **Speed**: Fast (no API calls)
- **Coverage**: 96% code coverage
- **Location**: `tests/*/test_*.py` (not ending in `_agent_evaluation.py`)

### Agent Evaluation Tests  
- **Purpose**: Test functions work correctly when called by AI agents
- **Speed**: Slow (requires Google API calls)
- **Requirements**: `GOOGLE_API_KEY` environment variable
- **Location**: `tests/*/*_agent_evaluation.py`
- **Behavior**: Run sequentially with rate limiting to prevent API quota issues

## Environment Setup

### For Traditional Tests
No additional setup required.

### For Agent Evaluation Tests
1. Set Google API key:
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```
2. Ensure sufficient API quota (free tier: 15 requests/minute)

## Sequential Execution

Agent evaluation tests automatically run sequentially to prevent API rate limiting:

- **Rate Limiting**: 2-second delay between tests
- **Sequential Order**: Agent tests run after all traditional tests
- **Isolation**: Each agent test is isolated with async locks
- **Error Handling**: API quota errors don't affect traditional tests

## Troubleshooting

### API Quota Exceeded
```
google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED
```
**Solution**: Wait for quota reset or run traditional tests only:
```bash
python3 -m pytest tests/ -v -m "not agent_evaluation"
```

### Missing API Key
**Solution**: Set the `GOOGLE_API_KEY` environment variable or skip agent tests:
```bash
python3 -m pytest tests/ -v -m "not agent_evaluation"
```

## Coverage Reports

HTML coverage reports are generated in `htmlcov/` directory:
```bash
python3 -m pytest tests/ --cov=src/basic_open_agent_tools --cov-report=html
open htmlcov/index.html
```