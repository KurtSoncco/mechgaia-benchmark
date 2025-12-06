#!/usr/bin/env python3
"""
Example script demonstrating reasoning evaluation for MechGAIA tasks.

This script shows how to:
1. Set up the reasoning evaluator
2. Evaluate agent reasoning vs reference solutions
3. Compare LLM-based vs semantic-based evaluation
4. Integrate with the scoring system
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from green_agents.level1_stress_task import Level1StressTask
from green_agents.level2_shaft_design_task import Level2ShaftDesignTask
from utils.reasoning_evaluator import get_reasoning_evaluator
from utils.semantic_similarity import get_semantic_evaluator


def example_1_semantic_evaluation():
    """
    Example 1: Use semantic similarity evaluator (no LLM required, fast)
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Semantic-Only Reasoning Evaluation")
    print("="*70)
    
    task = Level1StressTask("example_level1")
    evaluator = get_semantic_evaluator()
    
    # Good reasoning (matches reference approach)
    good_reasoning = """
    I need to find the maximum bending stress in a simply supported beam with a 
    point load at the center.
    
    Given:
    - Length L = 1 m
    - Diameter d = 20 mm = 0.02 m
    - Point load P = 100 N
    
    For a simply supported beam with center load:
    Maximum moment M = P*L/4 = 100*1/4 = 25 Nm
    
    For a circular cross-section:
    I = π*d^4/64 = π*(0.02)^4/64 = 7.854e-9 m^4
    
    Maximum stress occurs at extreme fiber:
    c = d/2 = 0.01 m
    
    Using flexure formula: σ = M*c/I
    σ = 25 * 0.01 / 7.854e-9 = 31.83 MPa
    """
    
    # Poor reasoning (lacks key concepts)
    poor_reasoning = """
    I calculated the answer to be 31.83 MPa by doing some stress calculations
    on the beam. The length and diameter were given, and I used the loading
    information to get the result.
    """
    
    print("\n--- Evaluating GOOD reasoning ---")
    score_good = evaluator.evaluate_similarity(
        good_reasoning,
        task.REFERENCE_REASONING,
        task_level=1,
        key_concepts=task.KEY_CONCEPTS
    )
    
    print(f"Score: {score_good.score:.2f}")
    print(f"Concept Coverage: {score_good.concept_coverage:.2f}")
    print(f"Keyword Overlap: {score_good.keyword_overlap:.2f}")
    print(f"Structure Similarity: {score_good.structure_similarity:.2f}")
    print(f"Feedback: {score_good.feedback}")
    print(f"Found Concepts: {[c for c, found in score_good.found_concepts.items() if found]}")
    
    print("\n--- Evaluating POOR reasoning ---")
    score_poor = evaluator.evaluate_similarity(
        poor_reasoning,
        task.REFERENCE_REASONING,
        task_level=1,
        key_concepts=task.KEY_CONCEPTS
    )
    
    print(f"Score: {score_poor.score:.2f}")
    print(f"Concept Coverage: {score_poor.concept_coverage:.2f}")
    print(f"Keyword Overlap: {score_poor.keyword_overlap:.2f}")
    print(f"Structure Similarity: {score_poor.structure_similarity:.2f}")
    print(f"Feedback: {score_poor.feedback}")
    print(f"Found Concepts: {[c for c, found in score_poor.found_concepts.items() if found]}")


def example_2_llm_based_evaluation():
    """
    Example 2: Use LLM-based reasoning evaluator (requires Ollama or API)
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: LLM-Based Reasoning Evaluation")
    print("="*70)
    
    try:
        evaluator = get_reasoning_evaluator()
        
        if not evaluator.enabled:
            print("⚠ LLM-based evaluation is disabled. Configure environment variables:")
            print("  export REASONING_EVAL_ENABLED=true")
            print("  export REASONING_EVAL_PROVIDER=ollama")
            print("  export REASONING_EVAL_MODEL=neural-chat")
            print("  export REASONING_EVAL_BASE_URL=http://localhost:11434")
            return
        
        task = Level1StressTask("example_level1")
        
        agent_reasoning = """
        For this bending stress problem, I'll use beam theory.
        
        The beam is simply supported with a center point load.
        Maximum moment = P*L/4 = 100*1/4 = 25 Nm
        
        For circular cross-section, I = π*d^4/64
        Distance to extreme fiber c = d/2
        
        Bending stress σ = M*c/I = 25*0.01/7.854e-9 = 31.83 MPa
        """
        
        print(f"\nUsing LLM provider: {evaluator.provider} ({evaluator.model})")
        print("Evaluating reasoning... (this may take 10-30 seconds)")
        
        score = evaluator.evaluate_reasoning(
            agent_reasoning=agent_reasoning,
            reference_reasoning=task.REFERENCE_REASONING,
            task_description=task.prompt["description"],
            key_concepts=task.KEY_CONCEPTS,
            task_level=1
        )
        
        print(f"\n✓ Evaluation complete!")
        print(f"Overall Score: {score.score:.2f}")
        print(f"Conceptual Alignment: {score.conceptual_alignment:.2f}")
        print(f"Reasoning Quality: {score.reasoning_quality:.2f}")
        print(f"Feedback: {score.feedback}")
        print(f"\nKey Concepts Found:")
        for concept, found in score.key_concepts.items():
            status = "✓" if found else "✗"
            print(f"  {status} {concept}")
        
    except Exception as e:
        print(f"⚠ Error during LLM evaluation: {e}")
        print("Make sure Ollama is running: ollama serve")
        print("And a model is pulled: ollama pull neural-chat")


def example_3_full_task_evaluation():
    """
    Example 3: Full task evaluation with both numerical and reasoning components
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Full Task Evaluation (Numerical + Reasoning)")
    print("="*70)
    
    # Create a submission for Level 1
    submission = {
        "answer_pa": 31.83e6,  # Correct numerical answer
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
    
    task = Level1StressTask("example_full_eval")
    
    print("\nRunning full evaluation...")
    result = task.run_evaluation(submission)
    
    print(f"\n✓ Evaluation Results:")
    print(f"  Final Score: {result['final_score']:.3f}")
    
    if 'numerical_score' in result:
        print(f"  Numerical Score: {result['numerical_score']:.3f}")
    
    if 'reasoning_score' in result:
        print(f"  Reasoning Score: {result['reasoning_score']:.3f}")
    
    print(f"\nDetailed Breakdown:")
    details = result['details']
    for key, value in details.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                if isinstance(subvalue, (int, float)):
                    print(f"    - {subkey}: {subvalue:.3f}")
                elif isinstance(subvalue, dict):
                    print(f"    - {subkey}: {len(subvalue)} items")
                else:
                    print(f"    - {subkey}: {str(subvalue)[:50]}...")
        elif isinstance(value, (int, float)):
            print(f"  {key}: {value:.3f}")


def example_4_batch_evaluation():
    """
    Example 4: Batch evaluation of multiple reasoning samples
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Batch Reasoning Evaluation")
    print("="*70)
    
    evaluator = get_semantic_evaluator()
    task = Level1StressTask("example_batch")
    
    # Multiple reasoning samples to evaluate
    reasoning_samples = [
        {
            "name": "Excellent",
            "reasoning": """
            For simply supported beam with center load:
            M = PL/4 = 25 Nm
            I = π*d^4/64 = 7.854e-9 m^4
            σ = Mc/I = 31.83 MPa
            Using flexure formula from mechanics of materials.
            """
        },
        {
            "name": "Good",
            "reasoning": """
            Moment at center = 100*1/4 = 25 Nm
            For circular section: I = π*0.02^4/64
            Stress = moment * radius / I = 31.83 MPa
            """
        },
        {
            "name": "Adequate",
            "reasoning": """
            Calculated the bending stress using the standard formula.
            Result: 31.83 MPa
            """
        },
        {
            "name": "Poor",
            "reasoning": """
            31.83 MPa is the answer.
            """
        }
    ]
    
    print("\nEvaluating multiple reasoning samples...\n")
    
    results = []
    for sample in reasoning_samples:
        score = evaluator.evaluate_similarity(
            sample["reasoning"],
            task.REFERENCE_REASONING,
            task_level=1,
            key_concepts=task.KEY_CONCEPTS
        )
        results.append((sample["name"], score))
        
        print(f"{sample['name']:12} | Score: {score.score:.2f} | "
              f"Concepts: {sum(score.found_concepts.values())}/{len(score.found_concepts)}")
    
    # Rank results
    print("\nRanking:")
    sorted_results = sorted(results, key=lambda x: x[1].score, reverse=True)
    for rank, (name, score) in enumerate(sorted_results, 1):
        print(f"  {rank}. {name:12} - {score.score:.2f}")


def example_5_custom_weights():
    """
    Example 5: Custom scoring weights for different applications
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Custom Scoring Weights")
    print("="*70)
    
    class CustomLevel1(Level1StressTask):
        """Custom task with different scoring weights"""
        
        def __init__(self, task_id):
            super().__init__(task_id)
            self.numerical_weight = 0.5  # 50% numerical
            self.reasoning_weight = 0.5   # 50% reasoning
        
        def calculate_final_score(self, score_details):
            # Extract scores
            numerical_scores = [
                v for k, v in score_details.items()
                if isinstance(v, (int, float)) and k != "reasoning"
            ]
            numerical_score = sum(numerical_scores) / len(numerical_scores) if numerical_scores else 0.0
            
            reasoning_data = score_details.get("reasoning")
            reasoning_score = reasoning_data.get("score", 1.0) if reasoning_data else 1.0
            
            # Apply custom weights
            final_score = (self.numerical_weight * numerical_score + 
                          self.reasoning_weight * reasoning_score)
            
            return {
                "final_score": final_score,
                "numerical_score": numerical_score,
                "reasoning_score": reasoning_score,
                "details": score_details,
                "weights": {
                    "numerical": self.numerical_weight,
                    "reasoning": self.reasoning_weight
                }
            }
    
    submission = {
        "answer_pa": 31.83e6,
        "reasoning_code": "print(31.83e6)"
    }
    
    # Standard weights (70% numerical, 30% reasoning)
    task_standard = Level1StressTask("standard")
    result_standard = task_standard.run_evaluation(submission)
    
    # Custom weights (50% numerical, 50% reasoning)
    task_custom = CustomLevel1("custom")
    result_custom = task_custom.run_evaluation(submission)
    
    print("\nComparison of different weight configurations:\n")
    print(f"{'Config':<20} | {'Numerical':<10} | {'Reasoning':<10} | {'Final':<10}")
    print("-" * 60)
    print(f"{'Standard (70/30)':<20} | "
          f"{result_standard.get('numerical_score', 1.0):<10.3f} | "
          f"{result_standard.get('reasoning_score', 1.0):<10.3f} | "
          f"{result_standard['final_score']:<10.3f}")
    print(f"{'Custom (50/50)':<20} | "
          f"{result_custom.get('numerical_score', 1.0):<10.3f} | "
          f"{result_custom.get('reasoning_score', 1.0):<10.3f} | "
          f"{result_custom['final_score']:<10.3f}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("MechGAIA Reasoning Evaluation - Example Scripts")
    print("="*70)
    
    try:
        # Run all examples
        example_1_semantic_evaluation()
        example_2_llm_based_evaluation()
        example_3_full_task_evaluation()
        example_4_batch_evaluation()
        example_5_custom_weights()
        
        print("\n" + "="*70)
        print("✓ All examples completed!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
