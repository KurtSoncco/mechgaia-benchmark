# /agents/green_agent_base.py
import json

class MechGAIABaseGreenAgent:
    """A base class for all MechGAIA green agents."""
    
    def __init__(self, task_id):
        self.task_id = task_id
        self.prompt = self.setup_task()

    def setup_task(self):
        """Prepares the task prompt and data. Must be implemented by subclasses."""
        raise NotImplementedError

    def run_evaluation(self, white_agent_submission_path):
        """
        Runs the full evaluation pipeline.
        1. Reads the white agent's submission.
        2. Verifies the submission against success criteria.
        3. Returns a final score.
        """
        try:
            with open(white_agent_submission_path, 'r') as f:
                submission_data = json.load(f)
            
            score_details = self.verify_submission(submission_data)
            return self.calculate_final_score(score_details)

        except Exception as e:
            return {"error": str(e), "score": 0.0}

    def verify_submission(self, submission_data):
        """Verifies the agent's output. Must be implemented by subclasses."""
        raise NotImplementedError

    def calculate_final_score(self, score_details):
        """Calculates a composite score. Can be overridden for complex rubrics."""
        # Simple scoring: average of all checks that passed (1.0) or failed (0.0)
        scores = [v for k, v in score_details.items() if isinstance(v, (int, float))]
        final_score = sum(scores) / len(scores) if scores else 0.0
        return {"final_score": final_score, "details": score_details}