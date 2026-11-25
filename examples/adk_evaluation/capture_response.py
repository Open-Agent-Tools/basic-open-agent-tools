#!/usr/bin/env python3
"""Script to capture the actual agent response for updating test expectations."""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.adk_evaluation.tree_agent.example_agent import root_agent


async def capture_agent_response():
    """Capture the agent's actual response to update test expectations."""

    query = "Use the generate_directory_tree function with directory_path='.', max_depth=1, and include_hidden=false."

    print("🤖 Running agent with query:")
    print(f"   '{query}'")
    print("\n" + "=" * 80)

    try:
        response_generator = root_agent.run_live(query)

        full_response = ""
        async for chunk in response_generator:
            print(chunk, end="", flush=True)
            full_response += str(chunk)

        print("\n" + "=" * 80)
        print("\n📋 CAPTURED RESPONSE FOR TEST UPDATE:")
        print("-" * 40)
        print(repr(full_response))
        print("-" * 40)

        print("\n📝 SUGGESTED TEST EXPECTATION:")
        print("-" * 40)
        response_words = full_response.lower().split()

        key_words = []
        for word in ["directory", "tree", "structure", "files", "folders", "contents"]:
            if word in response_words:
                key_words.append(word)

        if key_words:
            suggested_expectation = key_words[0]
            print(f'"{suggested_expectation}"')
        else:
            significant_words = [
                w for w in response_words if len(w) > 3 and w.isalpha()
            ]
            if significant_words:
                suggested_expectation = significant_words[0]
                print(f'"{suggested_expectation}"')
            else:
                print('"tree"  # fallback')

        print("-" * 40)

        return full_response

    except Exception as e:
        print(f"❌ Error running agent: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(capture_agent_response())
