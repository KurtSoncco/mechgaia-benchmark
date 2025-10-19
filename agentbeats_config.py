"""
AgentBeats Configuration Module

This module handles configuration and environment setup for the MechGAIA green agent
when running on the AgentBeats platform.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class AgentBeatsConfig:
    """Configuration manager for AgentBeats integration."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or "agentbeats_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "agent": {
                "name": "MechGAIA-Green-Agent",
                "version": "0.1.0",
                "description": "Green agent for MechGAIA benchmark",
                "author": "Kurt Walter Soncco Sinchi",
                "email": "kurtwal98@berkeley.edu"
            },
            "benchmark": {
                "name": "MechGAIA",
                "domain": "mechanical_engineering",
                "levels": 3,
                "description": "Mechanical engineering design and analysis benchmark"
            },
            "evaluation": {
                "timeout_seconds": 300,
                "max_memory_mb": 1024,
                "allowed_libraries": ["numpy", "pandas", "sympy", "math"],
                "blocked_functions": ["open", "file", "exec", "eval", "__import__"]
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "agentbeats.log"
            },
            "platform": {
                "agentbeats_host": os.getenv("AGENTBEATS_HOST", "localhost"),
                "agentbeats_port": int(os.getenv("AGENTBEATS_PORT", "8080")),
                "launcher_host": os.getenv("LAUNCHER_HOST", "localhost"),
                "launcher_port": int(os.getenv("LAUNCHER_PORT", "8081"))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for AgentBeats platform."""
        return {
            "name": self.get("agent.name"),
            "version": self.get("agent.version"),
            "description": self.get("agent.description"),
            "author": self.get("agent.author"),
            "email": self.get("agent.email"),
            "capabilities": [
                "stress_analysis",
                "shaft_design", 
                "plate_optimization",
                "cad_analysis",
                "material_selection",
                "numerical_verification"
            ],
            "supported_levels": list(range(1, self.get("benchmark.levels", 3) + 1))
        }
    
    def get_evaluation_config(self) -> Dict[str, Any]:
        """Get evaluation configuration."""
        return {
            "timeout_seconds": self.get("evaluation.timeout_seconds", 300),
            "max_memory_mb": self.get("evaluation.max_memory_mb", 1024),
            "allowed_libraries": self.get("evaluation.allowed_libraries", []),
            "blocked_functions": self.get("evaluation.blocked_functions", [])
        }


# Global configuration instance
config = AgentBeatsConfig()
