"""
Tests for MechGAIA Benchmark Components

This module contains comprehensive tests for all components of the MechGAIA benchmark.
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

from green_agents.level1_stress_task import Level1StressTask
from green_agents.level2_shaft_design_task import Level2ShaftDesignTask
from green_agents.level3_plate_optimization_task import Level3PlateOptimizationTask
from utils.safe_runner import execute_code
from utils.cad_verifier import CADAnalysisTool


class TestSafeRunner:
    """Test the safe code execution utility."""
    
    def test_successful_execution(self):
        """Test successful code execution."""
        code = "result = 2 + 2"
        result = execute_code(code)
        assert result["success"] is True
        assert result["result"] == 4
        assert result["error"] is None
    
    def test_failed_execution(self):
        """Test failed code execution."""
        code = "result = 1 / 0"  # Division by zero
        result = execute_code(code)
        assert result["success"] is False
        assert result["result"] is None
        assert result["error"] is not None
    
    def test_missing_result_variable(self):
        """Test execution without result variable."""
        code = "x = 5"  # No 'result' variable
        result = execute_code(code)
        assert result["success"] is False
        assert "no 'result' variable was found" in result["error"]
    
    def test_numpy_access(self):
        """Test numpy library access."""
        code = "result = np.pi"
        result = execute_code(code)
        assert result["success"] is True
        assert abs(result["result"] - 3.141592653589793) < 1e-10
    
    def test_math_library_access(self):
        """Test math library access."""
        code = "result = math.sqrt(16)"
        result = execute_code(code)
        assert result["success"] is True
        assert result["result"] == 4.0


class TestCADAnalysisTool:
    """Test the CAD analysis tool."""
    
    def test_initial_file_analysis(self):
        """Test analysis of initial CAD file."""
        tool = CADAnalysisTool()
        load_conditions = {"force_N": 1000, "type": "off-axis"}
        
        result = tool.run_analysis("tasks/level3/mounting_plate_initial.step", load_conditions)
        
        assert result["analysis_successful"] is True
        assert result["mass_kg"] == 1.5
        assert result["max_deflection_mm"] == 2.1
    
    def test_modified_file_analysis(self):
        """Test analysis of modified CAD file."""
        tool = CADAnalysisTool()
        load_conditions = {"force_N": 1000, "type": "off-axis"}
        
        result = tool.run_analysis("tasks/level3/mounting_plate_modified.step", load_conditions)
        
        assert result["analysis_successful"] is True
        assert result["mass_kg"] == 1.7
        assert result["max_deflection_mm"] == 1.5
    
    def test_unknown_file_analysis(self):
        """Test analysis of unknown CAD file."""
        tool = CADAnalysisTool()
        load_conditions = {"force_N": 1000, "type": "off-axis"}
        
        result = tool.run_analysis("unknown_file.step", load_conditions)
        
        assert result["analysis_successful"] is False
        assert result["mass_kg"] == -1
        assert result["max_deflection_mm"] == -1


class TestLevel1StressTask:
    """Test Level 1 stress analysis task."""
    
    def test_setup_task(self):
        """Test task setup."""
        agent = Level1StressTask("test_task")
        prompt = agent.setup_task()
        
        assert prompt["task_id"] == "test_task"
        assert prompt["level"] == 1
        assert "bending stress" in prompt["description"]
        assert "answer_pa" in prompt["submission_format"]
        assert "reasoning_code" in prompt["submission_format"]
    
    def test_correct_submission(self):
        """Test verification of correct submission."""
        agent = Level1StressTask("test_task")
        
        # Correct answer within tolerance
        submission = {
            "answer_pa": 31830000,  # Within 5% of ground truth
            "reasoning_code": "result = 31830000"
        }
        
        result = agent.verify_submission(submission)
        assert result["numerical_accuracy"] == 1.0
        assert result["code_executes"] == 1.0
    
    def test_incorrect_submission(self):
        """Test verification of incorrect submission."""
        agent = Level1StressTask("test_task")
        
        # Incorrect answer outside tolerance
        submission = {
            "answer_pa": 10000000,  # Way off from ground truth
            "reasoning_code": "result = 10000000"
        }
        
        result = agent.verify_submission(submission)
        assert result["numerical_accuracy"] == 0.0
        assert result["code_executes"] == 1.0
    
    def test_failed_code_execution(self):
        """Test verification with failed code execution."""
        agent = Level1StressTask("test_task")
        
        submission = {
            "answer_pa": 31830000,
            "reasoning_code": "result = 1 / 0"  # Division by zero
        }
        
        result = agent.verify_submission(submission)
        assert result["code_executes"] == 0.0
        assert "error" in result


class TestLevel2ShaftDesignTask:
    """Test Level 2 shaft design task."""
    
    def test_setup_task(self):
        """Test task setup."""
        agent = Level2ShaftDesignTask("test_task")
        prompt = agent.setup_task()
        
        assert prompt["task_id"] == "test_task"
        assert prompt["level"] == 2
        assert "shaft" in prompt["description"]
        assert "chosen_material" in prompt["submission_format"]
        assert "calculated_diameter_m" in prompt["submission_format"]
    
    def test_valid_material_choice(self):
        """Test verification with valid material choice."""
        agent = Level2ShaftDesignTask("test_task")
        
        submission = {
            "chosen_material": "Steel_1020",
            "calculated_diameter_m": 0.025
        }
        
        result = agent.verify_submission(submission)
        assert result["valid_material_choice"] == 1.0
    
    def test_invalid_material_choice(self):
        """Test verification with invalid material choice."""
        agent = Level2ShaftDesignTask("test_task")
        
        submission = {
            "chosen_material": "Invalid_Material",
            "calculated_diameter_m": 0.025
        }
        
        result = agent.verify_submission(submission)
        assert result["valid_material_choice"] == 0.0
        assert result["constraint_satisfied"] == 0.0


class TestLevel3PlateOptimizationTask:
    """Test Level 3 plate optimization task."""
    
    def test_setup_task(self):
        """Test task setup."""
        agent = Level3PlateOptimizationTask("test_task")
        prompt = agent.setup_task()
        
        assert prompt["task_id"] == "test_task"
        assert prompt["level"] == 3
        assert "mounting plate" in prompt["description"]
        assert "modified_cad_file_path" in prompt["submission_format"]
        assert "max_deflection_reduction" in prompt["constraints"]
        assert "max_mass_increase" in prompt["constraints"]
    
    def test_constraint_satisfaction(self):
        """Test verification with constraints satisfied."""
        agent = Level3PlateOptimizationTask("test_task")
        
        submission = {
            "modified_cad_file_path": "tasks/level3/mounting_plate_modified.step"
        }
        
        result = agent.verify_submission(submission)
        assert result["deflection_constraint_met"] == 1.0
        assert result["mass_constraint_met"] == 1.0


class TestIntegration:
    """Integration tests for the complete benchmark system."""
    
    def test_level1_complete_evaluation(self):
        """Test complete Level 1 evaluation pipeline."""
        agent = Level1StressTask("integration_test")
        
        submission = {
            "answer_pa": 31830000,
            "reasoning_code": "result = 31830000"
        }
        
        # Test the verification and scoring pipeline directly
        score_details = agent.verify_submission(submission)
        result = agent.calculate_final_score(score_details)
        assert "final_score" in result
        assert result["final_score"] > 0.0
        assert "details" in result
    
    def test_level2_complete_evaluation(self):
        """Test complete Level 2 evaluation pipeline."""
        agent = Level2ShaftDesignTask("integration_test")
        
        submission = {
            "chosen_material": "Steel_1020",
            "calculated_diameter_m": 0.025
        }
        
        # Test the verification and scoring pipeline directly
        score_details = agent.verify_submission(submission)
        result = agent.calculate_final_score(score_details)
        assert "final_score" in result
        assert result["final_score"] > 0.0
        assert "details" in result
    
    def test_level3_complete_evaluation(self):
        """Test complete Level 3 evaluation pipeline."""
        agent = Level3PlateOptimizationTask("integration_test")
        
        submission = {
            "modified_cad_file_path": "tasks/level3/mounting_plate_modified.step"
        }
        
        # Test the verification and scoring pipeline directly
        score_details = agent.verify_submission(submission)
        result = agent.calculate_final_score(score_details)
        assert "final_score" in result
        assert result["final_score"] > 0.0
        assert "details" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
