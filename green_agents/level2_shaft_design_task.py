# /agents/level2_shaft_design_task.py
try:
    import numpy as np
    import pandas as pd
    NUMPY_PANDAS_AVAILABLE = True
except ImportError:
    print("Warning: numpy/pandas not available")
    NUMPY_PANDAS_AVAILABLE = False

from .green_agent_base import MechGAIABaseGreenAgent
from typing import Optional


class Level2ShaftDesignTask(MechGAIABaseGreenAgent):
    
    # Reference solution for reasoning evaluation
    REFERENCE_REASONING = """
For shaft design under torsional loading, I need to select a material and determine 
the minimum diameter while satisfying the stress constraint.

Given:
- Power: P = 10 kW = 10,000 W
- Speed: N = 1500 RPM
- Safety Factor: SF = 2
- Shaft type: solid circular cross-section
- Materials available: Steel_1020 (Sy=350 MPa), Aluminum_6061-T6 (Sy=270 MPa), Titanium_Ti-6Al-4V (Sy=830 MPa)

Step 1: Determine the torque
Angular velocity: ω = 1500 RPM × (2π / 60) = 157.08 rad/s
Torque: T = P / ω = 10,000 W / 157.08 rad/s = 63.66 Nm

Step 2: Calculate allowable shear stress
For ductile materials under torsion, using von Mises theory:
τ_allowable = (S_y / SF) × 0.5 = (S_y / 4)

Material analysis:
- Steel_1020: τ_allow = 350 MPa / 4 = 87.5 MPa (good strength)
- Aluminum_6061-T6: τ_allow = 270 MPa / 4 = 67.5 MPa (lowest)
- Titanium_Ti-6Al-4V: τ_allow = 830 MPa / 4 = 207.5 MPa (highest strength)

Step 3: Calculate minimum diameter
For a solid circular shaft: τ = (T × r) / J, where J = π × d^4 / 32
Rearranging: d³ = (16 × T) / (π × τ_allowable)

For each material:
- Steel_1020: d_min = ∛((16 × 63.66) / (π × 87.5 × 10^6)) ≈ 0.012 m = 12 mm
- Aluminum: d_min ≈ 0.014 m = 14 mm
- Titanium: d_min ≈ 0.009 m = 9 mm

Step 4: Material selection
Steel_1020 is selected as it provides good strength-to-weight ratio and is commonly 
available for shaft applications. The minimum required diameter is approximately 12 mm.

This approach applies fundamental torsional mechanics and respects the material 
safety limits while providing a practical engineering solution.
    """
    
    # Key concepts for reasoning evaluation
    KEY_CONCEPTS = [
        "torque calculation",
        "power transmission",
        "material selection",
        "shear stress",
        "safety factor",
        "torsion formula",
        "polar moment of inertia",
        "stress constraint",
        "angular velocity",
        "ductile material"
    ]
    
    def setup_task(self):
        """Provides the task and path to the material database."""
        # Create a simple material database for the task
        if NUMPY_PANDAS_AVAILABLE:
            materials = {
                "Material": ["Steel_1020", "Aluminum_6061-T6", "Titanium_Ti-6Al-4V"],
                "Yield_Strength_Pa": [3.5e8, 2.7e8, 8.3e8],
            }
            pd.DataFrame(materials).to_csv(
                "tasks/level2/material_database.csv", index=False
            )
        else:
            # Create a simple CSV manually if pandas is not available
            import os
            os.makedirs("tasks/level2", exist_ok=True)
            with open("tasks/level2/material_database.csv", "w") as f:
                f.write("Material,Yield_Strength_Pa\n")
                f.write("Steel_1020,350000000\n")
                f.write("Aluminum_6061-T6,270000000\n")
                f.write("Titanium_Ti-6Al-4V,830000000\n")

        prompt = {
            "task_id": self.task_id,
            "level": 2,
            "description": "Select a suitable material and determine the minimum required diameter for a solid circular shaft to transmit 10kW of power at 1500 RPM. The maximum shear stress must not exceed the material's yield strength divided by a safety factor of 2.",
            "tool_path": "tasks/level2/material_database.csv",
            "submission_format": {
                "chosen_material": "MATERIAL_NAME",
                "calculated_diameter_m": "YOUR_NUMERICAL_ANSWER",
            },
        }
        return prompt
    
    def get_reference_reasoning(self) -> Optional[str]:
        """Returns the reference reasoning for this task."""
        return self.REFERENCE_REASONING
    
    def get_key_concepts(self) -> list[str]:
        """Returns key concepts to evaluate in the agent's reasoning."""
        return self.KEY_CONCEPTS

    def verify_submission(self, submission_data):
        """Verifies material choice and constraint satisfaction."""
        score_details = {"valid_material_choice": 0.0, "constraint_satisfied": 0.0}
        db = pd.read_csv("tasks/level2/material_database.csv")

        # 1. Verify the material choice
        material_name = submission_data.get("chosen_material")
        if material_name not in db["Material"].values:
            return score_details  # Fail if material is not from the database
        score_details["valid_material_choice"] = 1.0

        # 2. Verify constraint satisfaction
        material_yield_strength = db[db["Material"] == material_name][
            "Yield_Strength_Pa"
        ].iloc[0]
        allowable_shear_stress = (
            material_yield_strength / 2
        ) * 0.5  # Von Mises for shear

        # Calculation from fundamentals
        power_W = 10000  # 10 kW
        speed_rad_s = 1500 * (2 * np.pi / 60)
        torque_Nm = power_W / speed_rad_s  # T = P / omega

        # T = (tau * J) / r, so r^3 = (2 * T) / (pi * tau)
        required_radius_cubed = (2 * torque_Nm) / (np.pi * allowable_shear_stress)
        min_required_radius_m = required_radius_cubed ** (1 / 3)
        min_required_diameter_m = min_required_radius_m * 2

        agent_diameter_m = float(submission_data.get("calculated_diameter_m", 0))

        # Agent's diameter must be >= the minimum required diameter
        if agent_diameter_m >= min_required_diameter_m:
            score_details["constraint_satisfied"] = 1.0

        return score_details
