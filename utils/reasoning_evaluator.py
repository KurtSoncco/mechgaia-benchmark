"""
Reasoning Evaluator for MechGAIA Benchmark

This module evaluates the quality of agent reasoning strings by comparing them
against reference solutions using a small LLM instance (e.g., Ollama) or 
cloud-based models (OpenAI, Anthropic).

The evaluator measures:
- Conceptual correctness of the reasoning
- Alignment with reference approach and methodology
- Tone and explanation clarity
- Key engineering concepts and principles mentioned
"""

import json
import logging
import os
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReasoningScore:
    """Result of reasoning evaluation."""
    score: float  # 0.0 to 1.0
    reasoning_quality: float  # Measures explanation clarity and rigor
    conceptual_alignment: float  # Measures alignment with reference approach
    key_concepts: Dict[str, bool]  # Which key concepts were identified
    feedback: str  # Human-readable feedback
    raw_evaluation: str  # Raw LLM output for debugging


class ReasoningEvaluator:
    """
    Evaluates reasoning strings using an LLM.
    
    Supports multiple backends:
    - Ollama (local small models)
    - OpenAI
    - Anthropic
    - Generic HTTP endpoints
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the reasoning evaluator.
        
        Args:
            config: Configuration dict with keys:
                - provider: 'ollama', 'openai', 'anthropic', 'generic' (default: ollama)
                - model: Model identifier (default: 'neural-chat' for Ollama)
                - api_key: API key for cloud providers
                - base_url: Base URL for custom endpoints
                - enabled: Whether reasoning evaluation is enabled (default: True)
                - temperature: Model temperature (default: 0.3 for consistency)
                - max_tokens: Max tokens for response (default: 500)
        """
        self.config = config or self._get_default_config()
        self.enabled = self.config.get("enabled", True)
        self.provider = self.config.get("provider", "ollama")
        self.model = self.config.get("model", "neural-chat")
        self.api_key = self.config.get("api_key")
        self.base_url = self.config.get("base_url")
        self.temperature = self.config.get("temperature", 0.3)
        self.max_tokens = self.config.get("max_tokens", 500)
        
        self._validate_config()
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get configuration from environment variables."""
        return {
            "enabled": os.getenv("REASONING_EVAL_ENABLED", "true").lower() == "true",
            "provider": os.getenv("REASONING_EVAL_PROVIDER", "ollama"),
            "model": os.getenv("REASONING_EVAL_MODEL", "neural-chat"),
            "api_key": os.getenv("REASONING_EVAL_API_KEY"),
            "base_url": os.getenv("REASONING_EVAL_BASE_URL"),
            "temperature": float(os.getenv("REASONING_EVAL_TEMPERATURE", "0.3")),
            "max_tokens": int(os.getenv("REASONING_EVAL_MAX_TOKENS", "500")),
        }
    
    def _validate_config(self):
        """Validate configuration."""
        if not self.enabled:
            logger.info("Reasoning evaluation is disabled")
            return
        
        if self.provider == "ollama":
            if not self.base_url:
                self.base_url = "http://localhost:11434"
            logger.info(f"Reasoning evaluator configured for Ollama: {self.base_url} ({self.model})")
        elif self.provider in ["openai", "anthropic"]:
            if not self.api_key:
                logger.warning(f"No API key configured for {self.provider}")
        elif self.provider == "generic":
            if not self.base_url:
                logger.warning("No base_url configured for generic provider")
    
    def evaluate_reasoning(
        self,
        agent_reasoning: str,
        reference_reasoning: str,
        task_description: str,
        key_concepts: list[str],
        task_level: int = 1
    ) -> ReasoningScore:
        """
        Evaluate agent reasoning against a reference solution.
        
        Args:
            agent_reasoning: The reasoning/explanation provided by the agent
            reference_reasoning: The reference/ground-truth reasoning
            task_description: Description of the task for context
            key_concepts: List of key concepts/terms to check for
            task_level: Difficulty level (1-3) for context
        
        Returns:
            ReasoningScore with evaluation results
        """
        if not self.enabled:
            logger.warning("Reasoning evaluation disabled, returning neutral score")
            return ReasoningScore(
                score=1.0,
                reasoning_quality=1.0,
                conceptual_alignment=1.0,
                key_concepts={concept: True for concept in key_concepts},
                feedback="Reasoning evaluation disabled",
                raw_evaluation=""
            )
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            agent_reasoning,
            reference_reasoning,
            task_description,
            key_concepts,
            task_level
        )
        
        try:
            # Get LLM evaluation
            raw_response = self._query_llm(prompt)
            
            # Parse response
            score_data = self._parse_evaluation_response(raw_response, key_concepts)
            
            return score_data
        
        except Exception as e:
            logger.error(f"Error evaluating reasoning: {e}")
            # Return neutral score on error
            return ReasoningScore(
                score=0.5,
                reasoning_quality=0.5,
                conceptual_alignment=0.5,
                key_concepts={concept: False for concept in key_concepts},
                feedback=f"Evaluation error: {str(e)}",
                raw_evaluation=""
            )
    
    def _build_evaluation_prompt(
        self,
        agent_reasoning: str,
        reference_reasoning: str,
        task_description: str,
        key_concepts: list[str],
        task_level: int
    ) -> str:
        """Build the prompt for the LLM evaluator."""
        
        concepts_str = ", ".join(key_concepts)
        
        prompt = f"""You are an expert mechanical engineering evaluator. 
Evaluate the quality of the following agent's reasoning against a reference solution.

TASK DESCRIPTION:
{task_description}

DIFFICULTY LEVEL: {task_level}/3

KEY CONCEPTS TO LOOK FOR:
{concepts_str}

REFERENCE REASONING (Ground Truth):
{reference_reasoning}

AGENT'S REASONING:
{agent_reasoning}

---

Please evaluate the agent's reasoning on the following criteria:

1. CONCEPTUAL ALIGNMENT (0.0-1.0): How well does the agent's approach align with the reference solution?
   - Consider the methodology, assumptions, and problem-solving approach
   - Both should arrive at similar intermediate steps and conclusions

2. REASONING QUALITY (0.0-1.0): How clear, rigorous, and complete is the explanation?
   - Is the logic sound and well-articulated?
   - Are steps clearly justified?
   - Is the reasoning appropriate for the task level?

3. KEY CONCEPTS: Which of these concepts are clearly demonstrated in the agent's reasoning?
   - For each concept, indicate: FOUND or NOT FOUND

Provide your evaluation in JSON format ONLY:
{{
    "conceptual_alignment": <float 0-1>,
    "reasoning_quality": <float 0-1>,
    "key_concepts": {{
        "concept1": "FOUND" or "NOT FOUND",
        "concept2": "FOUND" or "NOT FOUND"
    }},
    "brief_feedback": "<one sentence summary of evaluation>"
}}

Output ONLY valid JSON, no other text."""
        
        return prompt
    
    def _query_llm(self, prompt: str) -> str:
        """Query the LLM with the evaluation prompt."""
        
        if self.provider == "ollama":
            return self._query_ollama(prompt)
        elif self.provider == "openai":
            return self._query_openai(prompt)
        elif self.provider == "anthropic":
            return self._query_anthropic(prompt)
        elif self.provider == "generic":
            return self._query_generic(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _query_ollama(self, prompt: str) -> str:
        """Query Ollama local instance."""
        import requests
        
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False,
            "num_predict": self.max_tokens,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            raise
    
    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI query failed: {e}")
            raise
    
    def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic Claude API."""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic query failed: {e}")
            raise
    
    def _query_generic(self, prompt: str) -> str:
        """Query generic HTTP endpoint."""
        import requests
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            # Adapt to your endpoint's response format
            return result.get("response") or result.get("text", "")
        except Exception as e:
            logger.error(f"Generic endpoint query failed: {e}")
            raise
    
    def _parse_evaluation_response(
        self,
        response: str,
        key_concepts: list[str]
    ) -> ReasoningScore:
        """Parse the LLM's evaluation response."""
        
        try:
            # Extract JSON from response (handle cases where LLM adds extra text)
            json_str = response
            if "{" in response:
                json_str = response[response.index("{"):response.rindex("}")+1]
            
            data = json.loads(json_str)
            
            # Extract scores
            conceptual_alignment = float(data.get("conceptual_alignment", 0.5))
            reasoning_quality = float(data.get("reasoning_quality", 0.5))
            
            # Clamp values to [0, 1]
            conceptual_alignment = max(0.0, min(1.0, conceptual_alignment))
            reasoning_quality = max(0.0, min(1.0, reasoning_quality))
            
            # Combine into overall score (weighted average)
            overall_score = 0.6 * conceptual_alignment + 0.4 * reasoning_quality
            
            # Extract key concepts
            found_concepts = {}
            if "key_concepts" in data:
                concepts_data = data["key_concepts"]
                for concept in key_concepts:
                    found = concepts_data.get(concept, "NOT FOUND").upper() == "FOUND"
                    found_concepts[concept] = found
            else:
                found_concepts = {concept: False for concept in key_concepts}
            
            feedback = data.get("brief_feedback", "Evaluation complete")
            
            return ReasoningScore(
                score=overall_score,
                reasoning_quality=reasoning_quality,
                conceptual_alignment=conceptual_alignment,
                key_concepts=found_concepts,
                feedback=feedback,
                raw_evaluation=response
            )
        
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}\nResponse: {response}")
            # Return neutral score on parse error
            return ReasoningScore(
                score=0.5,
                reasoning_quality=0.5,
                conceptual_alignment=0.5,
                key_concepts={concept: False for concept in key_concepts},
                feedback="Failed to parse evaluation response",
                raw_evaluation=response
            )
    
    def batch_evaluate(
        self,
        evaluations: list[Dict[str, Any]]
    ) -> list[ReasoningScore]:
        """
        Evaluate multiple reasoning pairs (useful for batch processing).
        
        Args:
            evaluations: List of dicts with keys:
                - agent_reasoning
                - reference_reasoning
                - task_description
                - key_concepts
                - task_level (optional)
        
        Returns:
            List of ReasoningScore objects
        """
        results = []
        for eval_data in evaluations:
            score = self.evaluate_reasoning(
                agent_reasoning=eval_data["agent_reasoning"],
                reference_reasoning=eval_data["reference_reasoning"],
                task_description=eval_data["task_description"],
                key_concepts=eval_data["key_concepts"],
                task_level=eval_data.get("task_level", 1)
            )
            results.append(score)
        
        return results


def get_reasoning_evaluator(config: Optional[Dict[str, Any]] = None) -> ReasoningEvaluator:
    """Factory function to get a configured ReasoningEvaluator instance."""
    return ReasoningEvaluator(config)
