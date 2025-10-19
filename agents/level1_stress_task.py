# /agents/level1_stress_task.py
from utils.safe_runner import execute_code  # A utility for safe code execution

from .green_agent_base import MechGAIABaseGreenAgent


class Level1StressTask(MechGAIABaseGreenAgent):
    def setup_task(self):
        """Defines the prompt for the white agent."""
        prompt = {
            "task_id": self.task_id,
            "level": 1,
            "description": "Calculate the maximum bending stress in a 1-meter long, 20mm diameter steel rod supported at both ends with a 100N point load in the center. Return your answer in Pascals (Pa).",
            "submission_format": {
                "answer_pa": "YOUR_NUMERICAL_ANSWER",
                "reasoning_code": "YOUR_PYTHON_CODE_AS_A_STRING",
            },
        }
        return prompt

    def verify_submission(self, submission_data):
        """Verifies the numerical result from the white agent."""
        score_details = {"numerical_accuracy": 0.0, "code_executes": 0.0}

        # 1. Safely execute the agent's code
        submitted_code = submission_data.get("reasoning_code", "")
        execution_result = execute_code(
            submitted_code
        )  # This should return the script's output

        if execution_result["success"]:
            score_details["code_executes"] = 1.0
        else:
            score_details["error"] = execution_result["error"]
            return score_details  # Stop if code fails

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
