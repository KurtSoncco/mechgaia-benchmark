# /agents/level3_plate_optimization_task.py
from .green_agent_base import MechGAIABaseGreenAgent
from utils.cad_verifier import CADAnalysisTool # A utility for CAD/FEA analysis

class Level3PlateOptimizationTask(MechGAIABaseGreenAgent):

    def setup_task(self):
        """Provides the initial CAD file and constraints."""
        prompt = {
            "task_id": self.task_id,
            "level": 3,
            "description": "Modify the provided mounting plate to reduce max deflection by at least 25% while increasing total mass by no more than 15%. An off-axis load of 1kN will be applied for the test.",
            "initial_cad_file": "tasks/level3/mounting_plate_initial.step",
            "constraints": {
                "max_deflection_reduction": 0.25, # 25%
                "max_mass_increase": 0.15 # 15%
            },
            "submission_format": {
                "modified_cad_file_path": "path/to/your/modified_plate.step"
            }
        }
        return prompt

    def verify_submission(self, submission_data):
        """Runs CAD analysis on both files and checks constraints."""
        score_details = {"deflection_constraint_met": 0.0, "mass_constraint_met": 0.0}
        
        # Initialize the CAD analysis tool
        cad_tool = CADAnalysisTool()
        load_conditions = {"force_N": 1000, "type": "off-axis"}
        
        # 1. Analyze the original file to get baseline metrics
        original_file = self.prompt["initial_cad_file"]
        baseline_metrics = cad_tool.run_analysis(original_file, load_conditions)

        # 2. Analyze the agent's submitted file
        submitted_file = submission_data.get("modified_cad_file_path")
        if not submitted_file: return score_details
        modified_metrics = cad_tool.run_analysis(submitted_file, load_conditions)

        # 3. Check deflection constraint
        deflection_reduction = (baseline_metrics["max_deflection"] - modified_metrics["max_deflection"]) / baseline_metrics["max_deflection"]
        if deflection_reduction >= self.prompt["constraints"]["max_deflection_reduction"]:
            score_details["deflection_constraint_met"] = 1.0

        # 4. Check mass constraint
        mass_increase = (modified_metrics["mass_kg"] - baseline_metrics["mass_kg"]) / baseline_metrics["mass_kg"]
        if mass_increase <= self.prompt["constraints"]["max_mass_increase"]:
            score_details["mass_constraint_met"] = 1.0

        return score_details