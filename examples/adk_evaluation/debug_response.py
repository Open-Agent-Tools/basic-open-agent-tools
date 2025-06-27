#!/usr/bin/env python3
"""Simple debug script to capture agent response."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.adk_evaluation.tree_agent.example_agent import root_agent
from basic_open_agent_tools.file_system.tree import generate_directory_tree

def test_direct_tool():
    """Test the tool directly first."""
    print("🔧 Testing tool directly:")
    try:
        # Test with both max_depth=1 and max_depth=2 to see the difference
        print("With max_depth=1:")
        result1 = generate_directory_tree(".", 1, False)
        print(result1)
        print("\n" + "-"*40)
        
        print("With max_depth=2:")
        result2 = generate_directory_tree(".", 2, False)
        print(result2)
        print("\n" + "="*60)
        return result2
    except Exception as e:
        print(f"❌ Tool error: {e}")
        return None

def test_agent_info():
    """Check agent configuration."""
    print("🤖 Agent info:")
    print(f"Name: {root_agent.name}")
    print(f"Model: {root_agent.model}")
    print(f"Tools: {[tool.__name__ for tool in root_agent.tools]}")
    print(f"Description: {root_agent.description}")
    print("\n" + "="*60)

if __name__ == "__main__":
    test_agent_info()
    tool_result = test_direct_tool()
    
    if tool_result:
        print("✅ Tool is working!")
        print(f"📋 Actual directory tree output:\n{repr(tool_result)}")
        
        # Suggest a reasonable expected response substring
        lines = tool_result.split('\n')
        if len(lines) > 0:
            first_line = lines[0].strip()
            print(f"\n📝 Suggested test expectation: \"{first_line}\"")
    else:
        print("❌ Tool test failed")