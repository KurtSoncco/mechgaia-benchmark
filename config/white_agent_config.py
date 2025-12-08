"""
Configuration for the simple white agent.

This module provides configuration management for the white agent server,
including host, port, name, and LLM settings.
"""

import os
from typing import Any, Dict, Optional


class WhiteAgentConfig:
    """Configuration manager for the white agent."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize white agent configuration.

        Args:
            config_file: Optional path to configuration file (not used yet, for future expansion)
        """
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "agent": {
                "name": os.getenv("WHITE_AGENT_NAME", "file_agent"),
                "host": os.getenv("WHITE_AGENT_HOST", "localhost"),
                "port": int(os.getenv("WHITE_AGENT_PORT", "9002")),
                "description": "Test agent from file",
                "version": "1.0.0",
            },
            "skill": {
                "id": "task_fulfillment",
                "name": "Task Fulfillment",
                "description": "Handles user requests and completes tasks",
                "tags": ["general"],
            },
            "llm": {
                "model": os.getenv("LLM_MODEL", "ollama/llama3"),
                "provider": os.getenv("LLM_PROVIDER", "ollama"),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.0")),
                "api_base": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            },
        }

    def get_agent_url(self) -> str:
        """Get the full URL for the white agent."""
        host = self.config["agent"]["host"]
        port = self.config["agent"]["port"]
        return f"http://{host}:{port}"

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., "agent.name")
            default: Default value if not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key (e.g., "agent.name")
            value: Configuration value
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value


# Global configuration instance
_global_config: Optional[WhiteAgentConfig] = None


def get_white_agent_config(config_file: Optional[str] = None) -> WhiteAgentConfig:
    """
    Get the global white agent configuration instance.

    Args:
        config_file: Optional config file path

    Returns:
        WhiteAgentConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = WhiteAgentConfig(config_file)
    return _global_config
