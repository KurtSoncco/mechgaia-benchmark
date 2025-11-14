"""
Configuration system for LLM providers, MCP, and A2A.
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path


class LLMConfig:
    """Configuration manager for LLM providers, MCP, and A2A."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or os.getenv(
            "MECHGAIA_CONFIG", "mechgaia_config.json"
        )
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment."""
        config = {
            "llm": self._get_default_llm_config(),
            "mcp": self._get_default_mcp_config(),
            "a2a": self._get_default_a2a_config(),
        }
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables
        config = self._apply_env_overrides(config)
        
        return config
    
    def _get_default_llm_config(self) -> Dict[str, Any]:
        """Get default LLM configuration."""
        return {
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "model": os.getenv("LLM_MODEL", "gpt-4"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("LLM_BASE_URL"),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4096")) if os.getenv("LLM_MAX_TOKENS") else None,
        }
    
    def _get_default_mcp_config(self) -> Dict[str, Any]:
        """Get default MCP configuration."""
        return {
            "enabled": os.getenv("MCP_ENABLED", "false").lower() == "true",
            "server_url": os.getenv("MCP_SERVER_URL", "http://localhost:8000"),
            "api_key": os.getenv("MCP_API_KEY"),
            "tools": [],
        }
    
    def _get_default_a2a_config(self) -> Dict[str, Any]:
        """Get default A2A configuration."""
        return {
            "enabled": os.getenv("A2A_ENABLED", "false").lower() == "true",
            "agent_id": os.getenv("A2A_AGENT_ID", "mechgaia-agent"),
            "agent_name": os.getenv("A2A_AGENT_NAME", "MechGAIA Agent"),
            "transport": os.getenv("A2A_TRANSPORT", "http"),
            "port": int(os.getenv("A2A_PORT", "8080")),
            "base_url": os.getenv("A2A_BASE_URL", "http://localhost:8080"),
            "broker_url": os.getenv("A2A_BROKER_URL"),
        }
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # LLM overrides
        if os.getenv("LLM_PROVIDER"):
            config["llm"]["provider"] = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_MODEL"):
            config["llm"]["model"] = os.getenv("LLM_MODEL")
        
        # MCP overrides
        if os.getenv("MCP_ENABLED"):
            config["mcp"]["enabled"] = os.getenv("MCP_ENABLED").lower() == "true"
        
        # A2A overrides
        if os.getenv("A2A_ENABLED"):
            config["a2a"]["enabled"] = os.getenv("A2A_ENABLED").lower() == "true"
        
        return config
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config.get("llm", {})
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP configuration."""
        return self.config.get("mcp", {})
    
    def get_a2a_config(self) -> Dict[str, Any]:
        """Get A2A configuration."""
        return self.config.get("a2a", {})
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "llm.provider")
            value: Configuration value
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "llm.provider")
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


# Global configuration instance
_global_config: Optional[LLMConfig] = None


def get_config(config_file: Optional[str] = None) -> LLMConfig:
    """
    Get the global configuration instance.
    
    Args:
        config_file: Optional config file path
        
    Returns:
        LLMConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = LLMConfig(config_file)
    return _global_config

