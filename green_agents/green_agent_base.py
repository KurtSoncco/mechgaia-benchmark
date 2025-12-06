# /agents/green_agent_base.py
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MechGAIABaseGreenAgent:
    """
    Base class for all MechGAIA green agents.
    
    Supports evaluation of both numerical results and reasoning quality.
    Subclasses should override:
    - setup_task(): Define the task prompt
    - verify_submission(): Implement numerical/functional verification
    - get_reference_reasoning() (optional): Provide reference reasoning for comparison
    """

    def __init__(self, task_id, enable_reasoning_eval: bool = True):
        """
        Initialize the green agent.
        
        Args:
            task_id: Unique identifier for the task
            enable_reasoning_eval: Whether to evaluate reasoning strings
        """
        self.task_id = task_id
        self.enable_reasoning_eval = enable_reasoning_eval
        self.prompt = self.setup_task()
        
        # Initialize reasoning evaluator if enabled
        self.reasoning_evaluator = None
        if self.enable_reasoning_eval:
            self._init_reasoning_evaluator()
    
    def _init_reasoning_evaluator(self):
        """Initialize the reasoning evaluator."""
        try:
            from utils.reasoning_evaluator import get_reasoning_evaluator
            self.reasoning_evaluator = get_reasoning_evaluator()
            logger.info("Reasoning evaluator initialized")
        except Exception as e:
            logger.warning(f"Could not initialize reasoning evaluator: {e}")
            self.enable_reasoning_eval = False

    def setup_task(self):
        """Prepares the task prompt and data. Must be implemented by subclasses."""
        raise NotImplementedError

    def run_evaluation(self, white_agent_submission_path):
        """
        Runs the full evaluation pipeline.
        1. Reads the white agent's submission.
        2. Verifies the submission against success criteria.
        3. Evaluates reasoning quality (if enabled).
        4. Returns a combined score.
        """
        try:
            with open(white_agent_submission_path, "r") as f:
                submission_data = json.load(f)

            # Verify numerical/functional correctness
            score_details = self.verify_submission(submission_data)
            
            # Evaluate reasoning if available and enabled
            if self.enable_reasoning_eval and self.reasoning_evaluator:
                reasoning_score = self.evaluate_reasoning(submission_data)
                if reasoning_score:
                    score_details["reasoning"] = reasoning_score
            
            # Calculate final score
            final_result = self.calculate_final_score(score_details)
            return final_result

        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return {"error": str(e), "score": 0.0}

    def verify_submission(self, submission_data):
        """Verifies the agent's output. Must be implemented by subclasses."""
        raise NotImplementedError
    
    def get_reference_reasoning(self) -> Optional[str]:
        """
        Returns reference reasoning for this task.
        Override in subclasses to provide reference solutions.
        
        Returns:
            Reference reasoning string, or None if not available
        """
        return None
    
    def get_key_concepts(self) -> list[str]:
        """
        Returns list of key concepts to evaluate in reasoning.
        Override in subclasses to customize concept checking.
        
        Returns:
            List of key concept strings
        """
        return []
    
    def evaluate_reasoning(self, submission_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate the reasoning/explanation provided by the agent.
        
        Args:
            submission_data: The agent's submission data
        
        Returns:
            Dict with reasoning evaluation results, or None if unavailable
        """
        if not self.enable_reasoning_eval or not self.reasoning_evaluator:
            return None
        
        # Extract reasoning from submission
        agent_reasoning = self._extract_reasoning(submission_data)
        if not agent_reasoning:
            logger.debug("No reasoning found in submission")
            return None
        
        # Get reference reasoning
        reference_reasoning = self.get_reference_reasoning()
        if not reference_reasoning:
            logger.debug("No reference reasoning available")
            return None
        
        # Get task description
        task_description = self.prompt.get("description", "")
        key_concepts = self.get_key_concepts()
        
        # Determine task level
        task_level = self.prompt.get("level", 1)
        
        try:
            # Evaluate reasoning
            from utils.reasoning_evaluator import ReasoningScore
            
            reasoning_score = self.reasoning_evaluator.evaluate_reasoning(
                agent_reasoning=agent_reasoning,
                reference_reasoning=reference_reasoning,
                task_description=task_description,
                key_concepts=key_concepts,
                task_level=task_level
            )
            
            # Convert to dict for storage
            return {
                "score": reasoning_score.score,
                "reasoning_quality": reasoning_score.reasoning_quality,
                "conceptual_alignment": reasoning_score.conceptual_alignment,
                "key_concepts": reasoning_score.key_concepts,
                "feedback": reasoning_score.feedback,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error evaluating reasoning: {e}")
            return None
    
    def _extract_reasoning(self, submission_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract reasoning/explanation from submission data.
        Override if reasoning is stored differently.
        
        Common keys: 'reasoning', 'reasoning_code', 'explanation', 'approach'
        """
        for key in ["reasoning", "reasoning_code", "explanation", "approach"]:
            if key in submission_data:
                value = submission_data[key]
                if isinstance(value, str) and value.strip():
                    return value
        
        return None

    def calculate_final_score(self, score_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a composite score from numerical and reasoning evaluations.
        
        Can be overridden for custom scoring rubrics.
        
        Args:
            score_details: Dict containing:
                - Numerical scores from verify_submission
                - (optional) "reasoning" dict with reasoning scores
        
        Returns:
            Dict with "final_score" and "details"
        """
        # Extract numerical scores
        numerical_scores = [
            v for k, v in score_details.items() 
            if isinstance(v, (int, float)) and k != "reasoning"
        ]
        
        numerical_score = sum(numerical_scores) / len(numerical_scores) if numerical_scores else 0.0
        
        # Extract reasoning score if available
        reasoning_data = score_details.get("reasoning")
        reasoning_score = reasoning_data.get("score", 1.0) if reasoning_data else 1.0
        
        # Combine scores: 70% numerical, 30% reasoning (default weighting)
        # Override weights in subclasses as needed
        numerical_weight = 0.7
        reasoning_weight = 0.3
        
        final_score = (numerical_weight * numerical_score) + (reasoning_weight * reasoning_score)
        
        return {
            "final_score": final_score,
            "numerical_score": numerical_score,
            "reasoning_score": reasoning_score,
            "details": score_details,
            "evaluation_time": datetime.now().isoformat()
        }
