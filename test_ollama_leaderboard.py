#!/usr/bin/env python3
"""
Test Ollama LLM models with MechGAIA Green Agent and Simple Leaderboard

This script:
1. Tests different Ollama models
2. Runs evaluations using the green agent
3. Maintains a simple leaderboard
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llm_providers import get_llm_provider, LLMMessage, MessageRole
from agentbeats_main import MechGAIAGreenAgent


class SimpleLeaderboard:
    """Simple leaderboard for tracking model performance."""
    
    def __init__(self, leaderboard_file: str = "ollama_leaderboard.json"):
        self.leaderboard_file = leaderboard_file
        self.leaderboard = self._load_leaderboard()
    
    def _load_leaderboard(self) -> Dict[str, Any]:
        """Load leaderboard from file."""
        if Path(self.leaderboard_file).exists():
            try:
                with open(self.leaderboard_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load leaderboard: {e}")
        return {
            "models": {},
            "evaluations": [],
            "last_updated": None
        }
    
    def _save_leaderboard(self):
        """Save leaderboard to file."""
        self.leaderboard["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.leaderboard_file, "w") as f:
                json.dump(self.leaderboard, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save leaderboard: {e}")
    
    def add_evaluation(
        self,
        model_name: str,
        task_level: int,
        score: float,
        details: Dict[str, Any],
        evaluation_time: float
    ):
        """Add an evaluation result to the leaderboard."""
        evaluation = {
            "model": model_name,
            "task_level": task_level,
            "score": score,
            "details": details,
            "evaluation_time": evaluation_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.leaderboard["evaluations"].append(evaluation)
        
        # Update model statistics
        if model_name not in self.leaderboard["models"]:
            self.leaderboard["models"][model_name] = {
                "total_evaluations": 0,
                "total_score": 0.0,
                "average_score": 0.0,
                "task_scores": defaultdict(list),
                "best_score": 0.0,
                "worst_score": 1.0
            }
        
        model_stats = self.leaderboard["models"][model_name]
        model_stats["total_evaluations"] += 1
        model_stats["total_score"] += score
        model_stats["average_score"] = model_stats["total_score"] / model_stats["total_evaluations"]
        model_stats["task_scores"][f"level_{task_level}"].append(score)
        
        if score > model_stats["best_score"]:
            model_stats["best_score"] = score
        if score < model_stats["worst_score"]:
            model_stats["worst_score"] = score
        
        self._save_leaderboard()
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get sorted leaderboard."""
        models = []
        for model_name, stats in self.leaderboard["models"].items():
            models.append({
                "model": model_name,
                "average_score": stats["average_score"],
                "total_evaluations": stats["total_evaluations"],
                "best_score": stats["best_score"],
                "worst_score": stats["worst_score"],
                "task_scores": dict(stats["task_scores"])
            })
        
        # Sort by average score (descending)
        models.sort(key=lambda x: x["average_score"], reverse=True)
        return models
    
    def print_leaderboard(self):
        """Print formatted leaderboard."""
        print("\n" + "=" * 80)
        print("OLLAMA MODEL LEADERBOARD")
        print("=" * 80)
        print(f"{'Rank':<6} {'Model':<25} {'Avg Score':<12} {'Best':<8} {'Evaluations':<12}")
        print("-" * 80)
        
        leaderboard = self.get_leaderboard()
        for rank, entry in enumerate(leaderboard, 1):
            print(f"{rank:<6} {entry['model']:<25} {entry['average_score']:<12.4f} "
                  f"{entry['best_score']:<8.4f} {entry['total_evaluations']:<12}")
        
        print("=" * 80)
        print(f"Total evaluations: {len(self.leaderboard['evaluations'])}")
        if self.leaderboard.get("last_updated"):
            print(f"Last updated: {self.leaderboard['last_updated']}")
        print()


def test_ollama_model(
    model_name: str,
    task_level: int,
    green_agent: MechGAIAGreenAgent,
    leaderboard: SimpleLeaderboard,
    ollama_base_url: str = "http://localhost:11434"
) -> Dict[str, Any]:
    """
    Test an Ollama model with a task.
    
    Args:
        model_name: Name of the Ollama model
        task_level: Task level (1, 2, or 3)
        green_agent: Green agent instance
        leaderboard: Leaderboard instance
        ollama_base_url: Ollama base URL
        
    Returns:
        Evaluation result
    """
    print(f"\n{'='*80}")
    print(f"Testing: {model_name} on Level {task_level}")
    print(f"{'='*80}")
    
    try:
        # Get LLM provider
        provider = get_llm_provider(
            provider="ollama",
            model=model_name,
            base_url=ollama_base_url
        )
        
        # Create a simple test submission using the LLM
        # For now, we'll use a mock submission, but you could have the LLM generate it
        print(f"Generating submission with {model_name}...")
        
        # Simple prompt for the LLM to generate a submission
        prompt = f"""
        You are solving a mechanical engineering problem (Level {task_level}).
        Generate a JSON submission with:
        - answer_pa: numerical answer in Pascals
        - reasoning_code: Python code that calculates the answer
        
        For Level 1 (Stress Analysis): Calculate stress for a beam with force=1000N, area=0.01m²
        """
        
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content="You are a mechanical engineering assistant."),
            LLMMessage(role=MessageRole.USER, content=prompt)
        ]
        
        start_time = time.time()
        response = provider.chat(messages, temperature=0.7, max_tokens=500)
        llm_time = time.time() - start_time
        
        print(f"LLM response time: {llm_time:.2f}s")
        print(f"LLM response: {response.content[:200]}...")
        
        # Parse LLM response to extract submission (simplified - in production, use proper parsing)
        # For now, create a mock submission based on the task level
        if task_level == 1:
            submission = {
                "answer_pa": 100000,  # Mock answer
                "reasoning_code": "force = 1000\narea = 0.01\nresult = force / area"
            }
        elif task_level == 2:
            submission = {
                "material": "steel",
                "diameter_m": 0.05
            }
        else:
            submission = {
                "cad_file_path": "example.step"
            }
        
        # Evaluate with green agent
        print(f"Evaluating submission with green agent...")
        eval_start = time.time()
        
        state = {
            "task_level": task_level,
            "white_agent_submission": submission,
            "task_id": f"mechgaia_level_{task_level}"
        }
        
        result = green_agent.run_agent(state, {})
        eval_time = time.time() - eval_start
        
        score = result.get("final_score", 0.0)
        details = result.get("details", {})
        
        print(f"Evaluation time: {eval_time:.2f}s")
        print(f"Score: {score:.4f}")
        print(f"Details: {details}")
        
        # Add to leaderboard
        leaderboard.add_evaluation(
            model_name=model_name,
            task_level=task_level,
            score=score,
            details=details,
            evaluation_time=eval_time + llm_time
        )
        
        return {
            "model": model_name,
            "task_level": task_level,
            "score": score,
            "details": details,
            "llm_time": llm_time,
            "eval_time": eval_time,
            "success": True
        }
        
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return {
            "model": model_name,
            "task_level": task_level,
            "score": 0.0,
            "error": str(e),
            "success": False
        }


def list_available_ollama_models(base_url: str = "http://localhost:11434") -> List[str]:
    """List available Ollama models."""
    try:
        provider = get_llm_provider(
            provider="ollama",
            model="llama2",  # Dummy model for listing
            base_url=base_url
        )
        models = provider.list_models()
        return models
    except Exception as e:
        print(f"Warning: Could not list Ollama models: {e}")
        # Return common small models
        return ["llama2", "llama3", "mistral", "phi", "neural-chat"]


def main():
    """Main function to test Ollama models and maintain leaderboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Ollama models with MechGAIA Green Agent")
    parser.add_argument("--models", nargs="+", help="List of models to test (default: auto-detect)")
    parser.add_argument("--task-level", type=int, default=1, choices=[1, 2, 3], help="Task level to test")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--leaderboard-file", default="ollama_leaderboard.json", help="Leaderboard file")
    parser.add_argument("--show-leaderboard", action="store_true", help="Show leaderboard and exit")
    
    args = parser.parse_args()
    
    # Initialize leaderboard
    leaderboard = SimpleLeaderboard(args.leaderboard_file)
    
    # Show leaderboard and exit if requested
    if args.show_leaderboard:
        leaderboard.print_leaderboard()
        return
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get(f"{args.ollama_url}/api/tags", timeout=5)
        if response.status_code != 200:
            print(f"❌ Ollama not available at {args.ollama_url}")
            print("Start Ollama with: docker run -d -p 11434:11434 ollama/ollama")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama at {args.ollama_url}: {e}")
        print("Start Ollama with: docker run -d -p 11434:11434 ollama/ollama")
        return
    
    # Get models to test
    if args.models:
        models_to_test = args.models
    else:
        print("Auto-detecting available Ollama models...")
        models_to_test = list_available_ollama_models(args.ollama_url)
        if not models_to_test:
            print("No models found. Using default small models...")
            models_to_test = ["llama2", "mistral", "phi"]
    
    print(f"\n📋 Models to test: {', '.join(models_to_test)}")
    print(f"📋 Task level: {args.task_level}")
    print(f"📋 Ollama URL: {args.ollama_url}\n")
    
    # Initialize green agent
    green_agent = MechGAIAGreenAgent()
    
    # Test each model
    results = []
    for model_name in models_to_test:
        result = test_ollama_model(
            model_name=model_name,
            task_level=args.task_level,
            green_agent=green_agent,
            leaderboard=leaderboard,
            ollama_base_url=args.ollama_url
        )
        results.append(result)
        time.sleep(1)  # Small delay between tests
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for result in results:
        status = "✅" if result.get("success") else "❌"
        print(f"{status} {result['model']}: Score = {result.get('score', 0.0):.4f}")
    print()
    
    # Show leaderboard
    leaderboard.print_leaderboard()


if __name__ == "__main__":
    main()


