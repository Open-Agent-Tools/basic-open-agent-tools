# ADK Evaluation Example

This directory demonstrates how to use Google ADK (Agent Development Kit) evaluation with `basic_open_agent_tools`. It provides a complete working example that tests agent functionality using the official ADK evaluation methodology.

## Overview

ADK evaluation allows you to test agents using predefined test cases that specify:
- User queries
- Expected tool usage (function calls with specific parameters)
- Expected agent responses
- Evaluation criteria for success/failure

This example tests the `generate_directory_tree` function from `basic_open_agent_tools.file_system.tree`.

## File Structure

```
examples/adk_evaluation/
├── README.md                           # This documentation
├── __init__.py                         # Package marker
├── test_config.json                    # Evaluation criteria configuration
├── test_tree_agent_evaluation.py      # Pytest test runner
├── tree_agent/
│   ├── __init__.py                     # Agent module structure for ADK
│   └── example_agent.py                # Agent with tools
└── tree_generation.test.json          # ADK test case definition
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API Key**:
   Create a `.env` file in the project root with your Google AI API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Run the Evaluation**:
   ```bash
   pytest examples/adk_evaluation/test_tree_agent_evaluation.py -v
   ```

## Key Components

### 1. Agent Module (`tree_agent/`)

**`example_agent.py`**: Contains the ADK agent with tools
```python
from google.adk.agents import Agent
from basic_open_agent_tools.file_system.tree import generate_directory_tree

root_agent = Agent(
    name="tree_agent",
    model="gemini-2.0-flash", 
    tools=[generate_directory_tree],
    # ... configuration
)
```

**`__init__.py`**: Required ADK structure
```python
from . import example_agent as agent
```

### 2. Test Case Definition (`tree_generation.test.json`)

Follows ADK EvalSet schema:
```json
{
  "eval_set_id": "tree_generation_test_set",
  "eval_cases": [
    {
      "eval_id": "simple_tree_generation",
      "conversation": [
        {
          "user_content": {...},           // User query
          "final_response": {...},         // Expected response
          "intermediate_data": {
            "tool_uses": [...]             // Expected tool calls
          }
        }
      ],
      "session_input": {...}              // Initial session state
    }
  ]
}
```

### 3. Pytest Integration (`test_tree_agent_evaluation.py`)

Uses official ADK evaluation API:
```python
@pytest.mark.asyncio
async def test_with_single_test_file():
    await AgentEvaluator.evaluate(
        agent_module="examples.adk_evaluation.tree_agent",
        eval_dataset_file_path_or_dir="examples/adk_evaluation/tree_generation.test.json",
    )
```

### 4. Evaluation Configuration (`test_config.json`)

Controls evaluation thresholds:
```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0,     // Tool usage accuracy (0-1)
    "response_match_score": 0          // Response text similarity (0-1)
  }
}
```

## Evaluation Criteria

ADK evaluates two main aspects:

1. **Tool Trajectory Score**: How well the agent's actual tool calls match expected tool calls
   - 1.0 = Perfect match of function names, parameters, and order
   - 0.5 = Partial match (e.g., correct function, some parameters wrong)
   - 0.0 = No match

2. **Response Match Score**: Text similarity between actual and expected responses using ROUGE metrics
   - Uses semantic similarity, not exact string matching
   - Higher scores indicate better response quality

## Configuration Options

### Strict Evaluation (Production)
```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,   // Require perfect tool usage
    "response_match_score": 0.8        // Require high response similarity
  }
}
```

### Lenient Evaluation (Development)
```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.5,   // Allow partial tool matches
    "response_match_score": 0.3        // More flexible response matching
  }
}
```

### Smoke Test (CI/Basic Validation)
```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0,     // Just verify tools run without error
    "response_match_score": 0          // Any response is acceptable
  }
}
```

## Creating New Evaluations

### Step 1: Create Agent Module
```python
# my_agent/example_agent.py
from google.adk.agents import Agent
from basic_open_agent_tools.my_module import my_function

root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    tools=[my_function],
    instruction="Agent instructions here..."
)
```

### Step 2: Define Test Cases
```json
{
  "eval_set_id": "my_test_set",
  "eval_cases": [
    {
      "eval_id": "test_case_1",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "User query here"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "Expected response"}],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "my_function",
                "args": {"param1": "value1"}
              }
            ]
          }
        }
      ],
      "session_input": {
        "app_name": "my_agent",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

### Step 3: Create Pytest Test
```python
@pytest.mark.asyncio
async def test_my_agent():
    await AgentEvaluator.evaluate(
        agent_module="path.to.my_agent",
        eval_dataset_file_path_or_dir="path/to/my_test.test.json",
    )
```

## Best Practices

### Test Design
- **Start Simple**: Begin with basic single-tool interactions
- **Explicit Instructions**: Be very specific in user queries about expected tool parameters
- **Realistic Expectations**: Set evaluation criteria based on your testing needs

### Tool Integration
- **Function Signatures**: Ensure tools follow Google ADK standards (JSON-serializable types only)
- **Error Handling**: Tools should handle edge cases gracefully
- **Documentation**: Use comprehensive docstrings for LLM understanding

### Debugging Failed Evaluations
1. **Check Tool Trajectory**: Verify agent calls expected functions with correct parameters
2. **Examine Responses**: Compare actual vs expected response text
3. **Adjust Criteria**: Lower thresholds during development, raise for production
4. **Iterate on Instructions**: Refine agent instructions and user queries

## Common Issues

### Tool Trajectory Mismatches
- **Cause**: Agent calls different function or wrong parameters
- **Solution**: Make user queries more explicit about expected tool usage

### Response Match Failures  
- **Cause**: Agent response text doesn't match expected text
- **Solution**: Use more generic expected responses or lower response_match_score

### Import Errors
- **Cause**: Incorrect agent module structure
- **Solution**: Ensure `agent_module.agent.root_agent` structure is followed

### API Authentication
- **Cause**: Missing or incorrect Google AI API key
- **Solution**: Verify `.env` file contains valid `GOOGLE_API_KEY`

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run ADK Evaluations
  run: |
    pytest examples/adk_evaluation/ -v
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

### Coverage Integration
ADK evaluations automatically contribute to code coverage metrics, helping identify which tools are being tested.

## Further Reading

- [Google ADK Documentation](https://docs.google.com/document/d/1worsJdl5ysBVVHhLlAaAoU2jKYHLOPhzGxz-8zqZZc0)
- [ADK Evaluation Schema](https://github.com/google/adk/blob/main/schemas/)
- [Basic Open Agent Tools Documentation](../../README.md)

## Contributing

When adding new evaluation examples:
1. Follow the existing directory structure
2. Include comprehensive test cases
3. Document any special requirements
4. Update this README with new patterns or lessons learned