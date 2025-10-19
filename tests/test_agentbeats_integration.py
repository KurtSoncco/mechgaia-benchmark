"""
Tests for AgentBeats SDK Integration

This module contains tests for the AgentBeats SDK integration components.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentbeats_main import MechGAIAGreenAgent
from agentbeats_config import AgentBeatsConfig


class TestAgentBeatsConfig:
    """Test the AgentBeats configuration system."""
    
    def test_default_config(self):
        """Test default configuration loading."""
        config = AgentBeatsConfig()
        
        assert config.get("agent.name") == "MechGAIA-Green-Agent"
        assert config.get("agent.version") == "0.1.0"
        assert config.get("benchmark.levels") == 3
        assert config.get("evaluation.timeout_seconds") == 300
    
    def test_config_get_set(self):
        """Test configuration get/set operations."""
        config = AgentBeatsConfig()
        
        # Test setting and getting values
        config.set("test.value", "test_data")
        assert config.get("test.value") == "test_data"
        
        # Test default value
        assert config.get("nonexistent.key", "default") == "default"
    
    def test_agent_info(self):
        """Test agent information generation."""
        config = AgentBeatsConfig()
        info = config.get_agent_info()
        
        assert info["name"] == "MechGAIA-Green-Agent"
        assert info["version"] == "0.1.0"
        assert "capabilities" in info
        assert "supported_levels" in info
        assert len(info["supported_levels"]) == 3
    
    def test_evaluation_config(self):
        """Test evaluation configuration."""
        config = AgentBeatsConfig()
        eval_config = config.get_evaluation_config()
        
        assert "timeout_seconds" in eval_config
        assert "max_memory_mb" in eval_config
        assert "allowed_libraries" in eval_config
        assert "blocked_functions" in eval_config


class TestMechGAIAGreenAgent:
    """Test the main MechGAIA green agent for AgentBeats."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MechGAIAGreenAgent()
        
        assert agent.agent_name == "MechGAIA-Green-Agent"
        assert agent.version == "0.1.0"
        assert agent.supported_levels == [1, 2, 3]
    
    def test_get_agent_info(self):
        """Test agent information retrieval."""
        agent = MechGAIAGreenAgent()
        info = agent.get_agent_info()
        
        assert info["name"] == "MechGAIA-Green-Agent"
        assert info["version"] == "0.1.0"
        assert "capabilities" in info
        assert "supported_levels" in info
    
    def test_level1_evaluation(self):
        """Test Level 1 evaluation through AgentBeats interface."""
        agent = MechGAIAGreenAgent()
        
        state = {
            "task_level": 1,
            "white_agent_submission": {
                "answer_pa": 31830000,
                "reasoning_code": "result = 31830000"
            },
            "task_id": "mechgaia_level_1"
        }
        
        result = agent.run_agent(state, {})
        
        assert "final_score" in result
        assert result["final_score"] > 0.0
        assert result["agent_name"] == "MechGAIA-Green-Agent"
        assert result["platform"] == "AgentBeats"
        assert result["task_level"] == 1
    
    def test_level2_evaluation(self):
        """Test Level 2 evaluation through AgentBeats interface."""
        agent = MechGAIAGreenAgent()
        
        state = {
            "task_level": 2,
            "white_agent_submission": {
                "chosen_material": "Steel_1020",
                "calculated_diameter_m": 0.025
            },
            "task_id": "mechgaia_level_2"
        }
        
        result = agent.run_agent(state, {})
        
        assert "final_score" in result
        assert result["final_score"] > 0.0
        assert result["agent_name"] == "MechGAIA-Green-Agent"
        assert result["platform"] == "AgentBeats"
        assert result["task_level"] == 2
    
    def test_level3_evaluation(self):
        """Test Level 3 evaluation through AgentBeats interface."""
        agent = MechGAIAGreenAgent()
        
        state = {
            "task_level": 3,
            "white_agent_submission": {
                "modified_cad_file_path": "tasks/level3/mounting_plate_modified.step"
            },
            "task_id": "mechgaia_level_3"
        }
        
        result = agent.run_agent(state, {})
        
        assert "final_score" in result
        assert result["final_score"] > 0.0
        assert result["agent_name"] == "MechGAIA-Green-Agent"
        assert result["platform"] == "AgentBeats"
        assert result["task_level"] == 3
    
    def test_invalid_task_level(self):
        """Test handling of invalid task level."""
        agent = MechGAIAGreenAgent()
        
        state = {
            "task_level": 99,
            "white_agent_submission": {},
            "task_id": "invalid_task"
        }
        
        result = agent.run_agent(state, {})
        
        assert "error" in result
        assert result["score"] == 0.0
        assert "Unsupported task level" in result["error"]
    
    def test_missing_submission(self):
        """Test handling of missing submission data."""
        agent = MechGAIAGreenAgent()
        
        state = {
            "task_level": 1,
            "task_id": "mechgaia_level_1"
            # Missing white_agent_submission
        }
        
        result = agent.run_agent(state, {})
        
        # Should handle gracefully
        assert "final_score" in result or "error" in result
    
    def test_error_handling(self):
        """Test error handling in agent execution."""
        agent = MechGAIAGreenAgent()
        
        # Test with malformed state
        state = "invalid_state"
        
        result = agent.run_agent(state, {})
        
        assert "error" in result
        assert result["score"] == 0.0
        assert "Agent execution failed" in result["error"]


class TestAgentBeatsIntegration:
    """Integration tests for AgentBeats platform."""
    
    def test_agent_card_validation(self):
        """Test that agent_card.toml is valid."""
        agent_card_path = Path(__file__).parent.parent / "agent_card.toml"
        assert agent_card_path.exists()
        
        # Read and validate basic structure
        with open(agent_card_path, 'r') as f:
            content = f.read()
            
        assert "[agent]" in content
        assert "name = \"MechGAIA-Green-Agent\"" in content
        assert "[agent.capabilities]" in content
        assert "[agent.benchmark]" in content
    
    def test_main_entry_point(self):
        """Test that the main entry point works."""
        agentbeats_main_path = Path(__file__).parent.parent / "agentbeats_main.py"
        assert agentbeats_main_path.exists()
        
        # Test that the module can be imported
        import agentbeats_main
        assert hasattr(agentbeats_main, 'MechGAIAGreenAgent')
        assert hasattr(agentbeats_main, 'main')
    
    def test_deployment_files(self):
        """Test that deployment files exist."""
        project_root = Path(__file__).parent.parent
        
        # Check deployment files
        assert (project_root / "Dockerfile").exists()
        assert (project_root / "docker-compose.yml").exists()
        assert (project_root / "scripts" / "deploy.sh").exists()
        
        # Check that deploy script is executable
        deploy_script = project_root / "scripts" / "deploy.sh"
        assert deploy_script.stat().st_mode & 0o111  # Check executable bit
    
    def test_configuration_files(self):
        """Test that configuration files exist and are valid."""
        project_root = Path(__file__).parent.parent
        
        # Check configuration files
        assert (project_root / "agentbeats_config.py").exists()
        
        # Test configuration loading
        from agentbeats_config import config
        assert config.get("agent.name") == "MechGAIA-Green-Agent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
