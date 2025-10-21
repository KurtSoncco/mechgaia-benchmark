#!/usr/bin/env python3
"""
Demo White Agent - Simulates White Agent submissions for the mechanical engineering tasks.
This creates realistic submissions that the Green Agent can evaluate.
"""

import json
import os
from typing import Dict, Any
import numpy as np


class DemoWhiteAgent:
    """Simulates White Agent submissions for mechanical engineering tasks."""
    
    def __init__(self):
        self.name = "DemoWhiteAgent"
        self.version = "1.0.0"
    
    def create_level1_submission(self, correct: bool = False) -> Dict[str, Any]:
        """Create a submission for Level 1 Stress Task."""
        if correct:
            # Correct submission
            return {
                "answer_pa": 31.83e6,  # Correct answer
                "reasoning_code": """
import math

# Given parameters
P = 100  # N (point load)
L = 1.0  # m (length)
d = 0.02  # m (diameter)

# Calculate moment
M = (P * L) / 4  # Nm

# Calculate moment of inertia
I = (math.pi * d**4) / 64  # m^4

# Calculate distance to neutral axis
c = d / 2  # m

# Calculate stress
stress = (M * c) / I  # Pa

print(f"Maximum bending stress: {stress:.2e} Pa")
"""
            }
        else:
            # Incorrect submission - wrong formula
            return {
                "answer_pa": 15.92e6,  # Wrong answer (half of correct)
                "reasoning_code": """
import math

# Given parameters
P = 100  # N (point load)
L = 1.0  # m (length)
d = 0.02  # m (diameter)

# WRONG: Using L/2 instead of L/4 for moment
M = (P * L) / 2  # Nm (This is wrong!)

# Calculate moment of inertia
I = (math.pi * d**4) / 64  # m^4

# Calculate distance to neutral axis
c = d / 2  # m

# Calculate stress
stress = (M * c) / I  # Pa

print(f"Maximum bending stress: {stress:.2e} Pa")
"""
            }
    
    def create_level2_submission(self, correct: bool = False) -> Dict[str, Any]:
        """Create a submission for Level 2 Shaft Design Task."""
        if correct:
            # Correct submission
            return {
                "chosen_material": "Steel_1020",
                "calculated_diameter_m": 0.045  # Correct diameter
            }
        else:
            # Incorrect submission - wrong material choice
            return {
                "chosen_material": "Aluminum_6061-T6",  # Wrong material choice
                "calculated_diameter_m": 0.040  # Too small diameter
            }
    
    def create_level3_submission(self, correct: bool = False) -> Dict[str, Any]:
        """Create a submission for Level 3 Plate Optimization Task."""
        if correct:
            return {
                "modified_cad_file_path": "tasks/level3/optimized_plate_correct.step"
            }
        else:
            return {
                "modified_cad_file_path": "tasks/level3/optimized_plate_incorrect.step"
            }
    
    def generate_all_submissions(self) -> Dict[str, Any]:
        """Generate all test submissions."""
        return {
            "level1_correct": self.create_level1_submission(correct=True),
            "level1_incorrect": self.create_level1_submission(correct=False),
            "level2_correct": self.create_level2_submission(correct=True),
            "level2_incorrect": self.create_level2_submission(correct=False),
            "level3_correct": self.create_level3_submission(correct=True),
            "level3_incorrect": self.create_level3_submission(correct=False)
        }


def create_demo_submission_files():
    """Create demo submission files for testing."""
    demo_agent = DemoWhiteAgent()
    submissions = demo_agent.generate_all_submissions()
    
    # Create directories
    os.makedirs("demo_submissions", exist_ok=True)
    
    # Create submission files
    for name, submission in submissions.items():
        filename = f"demo_submissions/{name}.json"
        with open(filename, 'w') as f:
            json.dump(submission, f, indent=2)
        print(f"Created: {filename}")
    
    return submissions


if __name__ == "__main__":
    create_demo_submission_files()
