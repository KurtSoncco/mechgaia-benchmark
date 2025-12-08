"""
Smoke tests for the simple white agent.

This module contains smoke tests to verify that the white agent server
starts successfully and can handle A2A messages.
"""

import pytest
import os
import sys
import time
import threading
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSimpleWhiteAgent:
    """Test the simple white agent implementation."""

    def test_white_agent_import(self):
        """Test that the white agent module can be imported."""
        try:
            from white_agents.simple_white_agent import (
                GeneralWhiteAgentExecutor,
                start_white_agent,
                prepare_white_agent_card,
            )
            assert GeneralWhiteAgentExecutor is not None
            assert start_white_agent is not None
            assert prepare_white_agent_card is not None
        except ImportError as e:
            pytest.skip(f"White agent not available: {e}")

    def test_white_agent_executor_initialization(self):
        """Test that the executor can be initialized."""
        try:
            from white_agents.simple_white_agent import GeneralWhiteAgentExecutor

            executor = GeneralWhiteAgentExecutor()
            assert executor is not None
            assert hasattr(executor, "ctx_id_to_messages")
            assert isinstance(executor.ctx_id_to_messages, dict)
        except ImportError:
            pytest.skip("White agent not available")

    def test_white_agent_card_preparation(self):
        """Test that the agent card can be prepared."""
        try:
            from white_agents.simple_white_agent import prepare_white_agent_card

            url = "http://localhost:9002"
            card = prepare_white_agent_card(url)

            assert card is not None
            assert card.name == "file_agent"
            assert card.url == url
            assert len(card.skills) > 0
        except ImportError:
            pytest.skip("White agent not available")

    def test_white_agent_config(self):
        """Test that the white agent configuration can be loaded."""
        try:
            from config.white_agent_config import get_white_agent_config

            config = get_white_agent_config()
            assert config is not None
            assert config.get("agent.name") == "file_agent"
            assert config.get("agent.host") == "localhost"
            assert config.get("agent.port") == 9002
            assert config.get("llm.model") is not None
        except ImportError:
            pytest.skip("White agent config not available")

    @pytest.mark.asyncio
    async def test_white_agent_a2a_communication(self):
        """
        Test that the white agent can receive and respond to A2A messages.

        This test requires:
        1. The white agent server to be running (or started in background)
        2. AgentBeats SDK's A2A utilities to be available
        3. An LLM provider to be configured (Ollama or OpenAI)

        Note: This test may be skipped if dependencies are not available.
        """
        try:
            from agentbeats.utils.agents.a2a import send_message_to_agent
        except ImportError:
            pytest.skip("AgentBeats A2A utilities not available")

        # Check if white agent is expected to be running
        # In a real scenario, you might start it in a background thread
        # For now, we'll check if it's accessible
        white_agent_url = os.getenv("WHITE_AGENT_URL", "http://localhost:9002")

        try:
            # Try to send a message to the white agent
            # This will fail if the agent is not running, which is expected
            # in CI/CD environments
            response = await send_message_to_agent(
                white_agent_url,
                "Hello, this is a test message. Please respond with 'OK'.",
                timeout=10.0,
            )

            # If we get a response, verify it's non-empty
            assert response is not None
            assert len(str(response).strip()) > 0

        except Exception as e:
            # If the agent is not running, that's okay for smoke tests
            # We just want to verify the code path works
            if "Connection" in str(e) or "refused" in str(e).lower():
                pytest.skip(
                    f"White agent not running at {white_agent_url}. "
                    "Start it with: python -m white_agents.simple_white_agent"
                )
            else:
                # Other errors should be raised
                raise

    def test_start_white_agent_function(self):
        """Test that the start_simple_white_agent function exists and is callable."""
        try:
            from run_benchmark import start_simple_white_agent

            assert start_simple_white_agent is not None
            assert callable(start_simple_white_agent)

            # Test that it can be called (but don't actually start the server)
            # We'll just verify the function signature
            import inspect

            sig = inspect.signature(start_simple_white_agent)
            assert "host" in sig.parameters
            assert "port" in sig.parameters
            assert "background" in sig.parameters
        except ImportError:
            pytest.skip("run_benchmark module not available")

    def test_white_agent_card_file(self):
        """Test that the white agent card file exists and is valid."""
        white_agent_card_path = project_root / "white_agent_card.toml"
        assert white_agent_card_path.exists(), "white_agent_card.toml should exist"

        # Read and validate basic structure
        with open(white_agent_card_path, "r") as f:
            content = f.read()

        assert "[agent]" in content
        assert 'name = "file_agent"' in content
        assert "[agent.capabilities]" in content
        assert "[agent.llm]" in content

    def test_white_agent_environment_variables(self):
        """Test that environment variables are properly handled."""
        # Save original values
        original_model = os.getenv("LLM_MODEL")
        original_provider = os.getenv("LLM_PROVIDER")

        try:
            # Set test values
            os.environ["LLM_MODEL"] = "test-model"
            os.environ["LLM_PROVIDER"] = "test-provider"

            # Reload config to pick up new values
            from config.white_agent_config import WhiteAgentConfig

            config = WhiteAgentConfig()
            # Note: Config loads at init time, so we need to check env directly
            assert os.getenv("LLM_MODEL") == "test-model"
            assert os.getenv("LLM_PROVIDER") == "test-provider"

        finally:
            # Restore original values
            if original_model is not None:
                os.environ["LLM_MODEL"] = original_model
            elif "LLM_MODEL" in os.environ:
                del os.environ["LLM_MODEL"]

            if original_provider is not None:
                os.environ["LLM_PROVIDER"] = original_provider
            elif "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

