#!/usr/bin/env python3
"""
Test script for connecting to the white agent via AgentBeats A2A protocol.

This script demonstrates how to test the connection between the green agent
and white agent using the AgentBeats SDK's A2A utilities.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_white_agent_connection(white_agent_url: str = None):
    """
    Test connection to white agent using A2A protocol.

    Args:
        white_agent_url: URL of the white agent (defaults to localhost:9002)
    """
    try:
        from agentbeats.utils.agents.a2a import send_message_to_agent
    except ImportError:
        print("❌ Error: AgentBeats SDK not available")
        print("   Install with: uv sync")
        return False

    if white_agent_url is None:
        white_agent_url = os.getenv("WHITE_AGENT_URL", "http://localhost:9002")

    print(f"🔗 Testing connection to white agent at: {white_agent_url}")
    print("-" * 60)

    # Test message
    test_message = "Hello! This is a test message from the green agent. Please respond with 'OK' to confirm you can receive messages."

    try:
        print(f"📤 Sending message: {test_message[:50]}...")
        response = await send_message_to_agent(
            white_agent_url,
            test_message,
            timeout=60.0,
        )

        print(f"✅ Connection successful!")
        print(f"📥 Response received: {response[:200]}...")
        print("-" * 60)
        return True

    except ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Make sure the white agent is running:")
        print(f"      python -m white_agents.simple_white_agent")
        print(f"   2. Check the URL is correct: {white_agent_url}")
        print(f"   3. Verify the agent is accessible:")
        print(f"      curl {white_agent_url}/health")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\n💡 This might indicate:")
        print(f"   - White agent is not responding")
        print(f"   - Network connectivity issues")
        print(f"   - LLM provider is not configured correctly")
        return False


async def test_white_agent_with_problem():
    """
    Test white agent with an actual problem statement.

    This simulates how the green agent would send a problem to the white agent.
    """
    try:
        from agentbeats.utils.agents.a2a import send_message_to_agent
    except ImportError:
        print("❌ Error: AgentBeats SDK not available")
        return False

    white_agent_url = os.getenv("WHITE_AGENT_URL", "http://localhost:9002")

    # Example problem statement (Level 1)
    problem = """
    Please solve the following MechGAIA Level 1 task:
    
    Calculate the maximum bending stress in a steel rod with the following properties:
    - Point load: 100 N
    - Length: 1.0 m
    - Diameter: 0.02 m
    
    Provide your answer in Pascals (Pa) and include your reasoning code.
    """

    print(f"🧪 Testing white agent with problem statement")
    print("-" * 60)

    try:
        print(f"📤 Sending problem to: {white_agent_url}")
        response = await send_message_to_agent(
            white_agent_url,
            problem,
            timeout=120.0,  # Longer timeout for problem solving
        )

        print(f"✅ Problem sent successfully!")
        print(f"📥 Response received:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test connection to white agent via AgentBeats A2A protocol"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL of the white agent (default: http://localhost:9002)",
    )
    parser.add_argument(
        "--problem",
        action="store_true",
        help="Test with an actual problem statement",
    )

    args = parser.parse_args()

    white_agent_url = args.url or os.getenv("WHITE_AGENT_URL", "http://localhost:9002")

    print("🤖 White Agent Connection Test")
    print("=" * 60)
    print()

    if args.problem:
        # Test with problem statement
        success = asyncio.run(test_white_agent_with_problem())
    else:
        # Simple connection test
        success = asyncio.run(test_white_agent_connection(white_agent_url))

    print()
    if success:
        print("✅ All tests passed!")
        print("\n💡 Next steps:")
        print("   1. Deploy your white agent to make it publicly accessible")
        print("   2. Update white_agent_card.toml with your deployment URL")
        print("   3. Register on agentbeats.org")
        print("   4. See docs/WHITE_AGENT_AGENTBEATS_CONNECTION.md for details")
        sys.exit(0)
    else:
        print("❌ Tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()


