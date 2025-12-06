# /agents/level3_plate_optimization_task.py
try:
    from utils.cad_verifier import CADAnalysisTool  # A utility for CAD/FEA analysis
    CAD_VERIFIER_AVAILABLE = True
except ImportError:
    print("Warning: CAD verifier not available")
    CAD_VERIFIER_AVAILABLE = False

from .green_agent_base import MechGAIABaseGreenAgent
from typing import Optional


class Level3PlateOptimizationTask(MechGAIABaseGreenAgent):
    
    # Reference solution for reasoning evaluation
    REFERENCE_REASONING = """
Mounting plate optimization requires a systematic approach to reduce deflection 
while managing weight constraints.

Given:
- Initial plate loaded with 1 kN off-axis force
- Objective: reduce deflection by ≥25%
- Constraint: mass increase ≤15%

Step 1: Analyze the baseline deflection
Using finite element analysis on the initial geometry, identify:
- Maximum deflection location and magnitude
- Stress concentration zones
- Load path and stiffness distribution
- Critical failure modes

Step 2: Identify optimization strategies
Several approaches can reduce deflection:
a) Increase material thickness in high-stress areas (local reinforcement)
b) Add ribs or stiffeners perpendicular to loading direction
c) Modify geometry to improve load distribution
d) Use material with higher stiffness if mass allows
e) Combine multiple approaches for efficiency

Step 3: Evaluate design modifications
For each proposed change, consider:
- Deflection reduction effectiveness
- Mass impact
- Manufacturability
- Stress concentration effects

Step 4: Parametric optimization
Perform iterative design cycles:
- Modify geometry parameters systematically
- Run FEA analysis to quantify deflection change
- Track mass increase
- Select design that meets both constraints with margin

Step 5: Validate the solution
Final design verification:
- Ensure 25% deflection reduction is achieved
- Confirm mass increase doesn't exceed 15%
- Check for stress concentration or failure modes
- Verify structural integrity under load

The recommended approach is to add stiffening ribs in the load transfer region,
which provides high deflection reduction per unit mass increase. Combined with
selective thickness increases, this typically achieves the targets efficiently.
    """
    
    # Key concepts for reasoning evaluation
    KEY_CONCEPTS = [
        "finite element analysis",
        "deflection reduction",
        "stress concentration",
        "optimization",
        "parametric study",
        "design iteration",
        "load path",
        "stiffness improvement",
        "mass constraint",
        "design trade-off"
    ]
    
    def setup_task(self):
        """Provides the initial CAD file and constraints."""
        prompt = {
            "task_id": self.task_id,
            "level": 3,
            "description": "Modify the provided mounting plate to reduce max deflection by at least 25% while increasing total mass by no more than 15%. An off-axis load of 1kN will be applied for the test.",
            "initial_cad_file": "tasks/level3/mounting_plate_initial.step",
            "constraints": {
                "max_deflection_reduction": 0.25,  # 25%
                "max_mass_increase": 0.15,  # 15%
            },
            "submission_format": {
                "modified_cad_file_path": "path/to/your/modified_plate.step"
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
        """Runs CAD analysis on both files and checks constraints."""
        score_details = {"deflection_constraint_met": 0.0, "mass_constraint_met": 0.0}

        if not CAD_VERIFIER_AVAILABLE:
            score_details["error"] = "CAD verifier not available"
            return score_details

        # Initialize the CAD analysis tool
        cad_tool = CADAnalysisTool()
        load_conditions = {"force_N": 1000, "type": "off-axis"}

        # 1. Analyze the original file to get baseline metrics
        original_file = self.prompt["initial_cad_file"]
        baseline_metrics = cad_tool.run_analysis(original_file, load_conditions)

        # 2. Analyze the agent's submitted file
        submitted_file = submission_data.get("modified_cad_file_path")
        if not submitted_file:
            return score_details
        modified_metrics = cad_tool.run_analysis(submitted_file, load_conditions)

        # 3. Check deflection constraint
        deflection_reduction = (
            baseline_metrics["max_deflection_mm"]
            - modified_metrics["max_deflection_mm"]
        ) / baseline_metrics["max_deflection_mm"]
        if (
            deflection_reduction
            >= self.prompt["constraints"]["max_deflection_reduction"]
        ):
            score_details["deflection_constraint_met"] = 1.0

        # 4. Check mass constraint
        mass_increase = (
            modified_metrics["mass_kg"] - baseline_metrics["mass_kg"]
        ) / baseline_metrics["mass_kg"]
        if mass_increase <= self.prompt["constraints"]["max_mass_increase"]:
            score_details["mass_constraint_met"] = 1.0

        return score_details
