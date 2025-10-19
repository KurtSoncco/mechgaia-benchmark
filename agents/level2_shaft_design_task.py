# /agents/level2_shaft_design_task.py
import pandas as pd
import numpy as np
from .green_agent_base import MechGAIABaseGreenAgent

class Level2ShaftDesignTask(MechGAIABaseGreenAgent):

    def setup_task(self):
        """Provides the task and path to the material database."""
        # Create a simple material database for the task
        materials = {
            'Material': ['Steel_1020', 'Aluminum_6061-T6', 'Titanium_Ti-6Al-4V'],
            'Yield_Strength_Pa': [3.5e8, 2.7e8, 8.3e8]
        }
        pd.DataFrame(materials).to_csv('tasks/level2/material_database.csv', index=False)

        prompt = {
            "task_id": self.task_id,
            "level": 2,
            "description": "Select a suitable material and determine the minimum required diameter for a solid circular shaft to transmit 10kW of power at 1500 RPM. The maximum shear stress must not exceed the material's yield strength divided by a safety factor of 2.",
            "tool_path": "tasks/level2/material_database.csv",
            "submission_format": {
                "chosen_material": "MATERIAL_NAME",
                "calculated_diameter_m": "YOUR_NUMERICAL_ANSWER"
            }
        }
        return prompt

    def verify_submission(self, submission_data):
        """Verifies material choice and constraint satisfaction."""
        score_details = {"valid_material_choice": 0.0, "constraint_satisfied": 0.0}
        db = pd.read_csv('tasks/level2/material_database.csv')

        # 1. Verify the material choice
        material_name = submission_data.get("chosen_material")
        if material_name not in db['Material'].values:
            return score_details # Fail if material is not from the database
        score_details["valid_material_choice"] = 1.0
        
        # 2. Verify constraint satisfaction
        material_yield_strength = db[db['Material'] == material_name]['Yield_Strength_Pa'].iloc[0]
        allowable_shear_stress = (material_yield_strength / 2) * 0.5 # Von Mises for shear
        
        # Calculation from fundamentals
        power_W = 10000  # 10 kW
        speed_rad_s = 1500 * (2 * np.pi / 60)
        torque_Nm = power_W / speed_rad_s # T = P / omega
        
        # T = (tau * J) / r, so r^3 = (2 * T) / (pi * tau)
        required_radius_cubed = (2 * torque_Nm) / (np.pi * allowable_shear_stress)
        min_required_radius_m = required_radius_cubed ** (1/3)
        min_required_diameter_m = min_required_radius_m * 2
        
        agent_diameter_m = float(submission_data.get("calculated_diameter_m", 0))

        # Agent's diameter must be >= the minimum required diameter
        if agent_diameter_m >= min_required_diameter_m:
            score_details["constraint_satisfied"] = 1.0
            
        return score_details