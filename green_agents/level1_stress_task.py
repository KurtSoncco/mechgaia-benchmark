# /agents/level1_stress_task.py
from .green_agent_base import MechGAIABaseGreenAgent
from typing import Optional

try:
    from utils.safe_runner import execute_code # A utility for safe code execution
    SAFE_RUNNER_AVAILABLE = True
except ImportError:
    print("Warning: safe_runner not available")
    SAFE_RUNNER_AVAILABLE = False

class Level1StressTask(MechGAIABaseGreenAgent):

    # Reference solution for reasoning evaluation
    REFERENCE_REASONING = """
To solve this bending stress problem, I need to apply beam theory and the flexure formula.

Given:
- Length L = 1 m
- Diameter d = 20 mm = 0.02 m
- Point load P = 100 N at center
- Both ends supported (simply supported beam)

Step 1: Determine the bending moment
For a simply supported beam with a point load at midspan:
M_max = (P * L) / 4 = (100 N * 1 m) / 4 = 25 Nm

Step 2: Calculate the moment of inertia
For a circular cross-section: I = (π * d^4) / 64
I = (3.14159 * (0.02)^4) / 64 = 7.854 × 10^-9 m^4

Step 3: Determine distance from neutral axis
For a circular section, the maximum stress occurs at the extreme fiber:
c = d/2 = 0.01 m (distance to extreme fiber)

Step 4: Apply the flexure formula
The bending stress is given by: σ = (M * c) / I
σ_max = (25 Nm * 0.01 m) / (7.854 × 10^-9 m^4) = 31.83 × 10^6 Pa = 31.83 MPa

This uses fundamental mechanics of materials principles and assumes elastic deformation,
which is valid for typical steel under these loads.
    """
    
    # Key concepts for reasoning evaluation
    KEY_CONCEPTS = [
        "bending stress",
        "moment of inertia",
        "flexure formula",
        "simply supported beam",
        "neutral axis",
        "extreme fiber",
        "circular cross-section",
        "point load at midspan"
    ]

    def setup_task(self):
        """Defines the prompt for the white agent."""
        prompt = {
            "task_id": self.task_id,
            "level": 1,
            "description": "Calculate the maximum bending stress in a 1-meter long, 20mm diameter steel rod supported at both ends with a 100N point load in the center. Return your answer in Pascals (Pa).",
            "submission_format": {
                "answer_pa": "YOUR_NUMERICAL_ANSWER",
                "reasoning_code": "YOUR_PYTHON_CODE_AS_A_STRING"
            }
        }
        return prompt
    
    def get_reference_reasoning(self) -> Optional[str]:
        """Returns the reference reasoning for this task."""
        return self.REFERENCE_REASONING
    
    def get_key_concepts(self) -> list[str]:
        """Returns key concepts to evaluate in the agent's reasoning."""
        return self.KEY_CONCEPTS

    def verify_submission(self, submission_data):
        """Verifies the numerical result from the white agent."""
        score_details = {"numerical_accuracy": 0.0, "code_executes": 0.0}
        
        # 1. Safely execute the agent's code
        submitted_code = submission_data.get("reasoning_code", "")
        
        if not SAFE_RUNNER_AVAILABLE:
            score_details["code_executes"] = 0.0
            score_details["error"] = "Safe runner not available"
            return score_details
        
        execution_result = execute_code(submitted_code) # This should return the script's output
        
        if execution_result["success"]:
            score_details["code_executes"] = 1.0
        else:
            score_details["error"] = execution_result["error"]
            return score_details # Stop if code fails

        # 2. Check numerical accuracy against the ground truth
        # Ground Truth Calculation:
        # M = (P * L) / 4 = (100 N * 1 m) / 4 = 25 Nm
        # I = (pi * d^4) / 64 = (pi * (0.02 m)^4) / 64 = 7.854e-9 m^4
        # c = d / 2 = 0.01 m
        # sigma = (M * c) / I = (25 * 0.01) / 7.854e-9 = 31.83 MPa
        ground_truth_stress = 31.83e6  # Pascals
        tolerance = 0.05  # 5% tolerance
        
        agent_answer = float(submission_data.get("answer_pa", 0))
        
        lower_bound = ground_truth_stress * (1 - tolerance)
        upper_bound = ground_truth_stress * (1 + tolerance)
        
        if lower_bound <= agent_answer <= upper_bound:
            score_details["numerical_accuracy"] = 1.0
        
        return score_details