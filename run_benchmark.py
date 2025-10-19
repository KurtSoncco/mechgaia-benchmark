#!/usr/bin/env python3
"""
MechGAIA Benchmark Runner

This script orchestrates the evaluation of white agents against the MechGAIA benchmark tasks.
It loads the appropriate green agent for each task level and evaluates the white agent's submission.
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.level1_stress_task import Level1StressTask
from agents.level2_shaft_design_task import Level2ShaftDesignTask
from agents.level3_plate_optimization_task import Level3PlateOptimizationTask


def load_white_agent(agent_path: str) -> dict:
    """
    Loads a white agent submission from a JSON file.
    
    Args:
        agent_path: Path to the white agent's submission file
        
    Returns:
        Dictionary containing the agent's submission data
    """
    try:
        with open(agent_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"White agent submission file not found: {agent_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in white agent submission: {e}")


def run_benchmark(task_level: int, white_agent_path: str, output_path: str = None) -> dict:
    """
    Runs the MechGAIA benchmark for a specific task level.
    
    Args:
        task_level: The task level to run (1, 2, or 3)
        white_agent_path: Path to the white agent's submission file
        output_path: Optional path to save the results
        
    Returns:
        Dictionary containing the evaluation results
    """
    # Initialize the appropriate green agent
    task_id = f"mechgaia_level_{task_level}"
    
    if task_level == 1:
        green_agent = Level1StressTask(task_id)
    elif task_level == 2:
        green_agent = Level2ShaftDesignTask(task_id)
    elif task_level == 3:
        green_agent = Level3PlateOptimizationTask(task_id)
    else:
        raise ValueError(f"Invalid task level: {task_level}. Must be 1, 2, or 3.")
    
    # Load the white agent submission
    try:
        white_agent_data = load_white_agent(white_agent_path)
    except Exception as e:
        return {
            "error": f"Failed to load white agent submission: {str(e)}",
            "score": 0.0,
            "task_level": task_level,
            "task_id": task_id
        }
    
    # Run the evaluation
    try:
        # The run_evaluation method expects a file path, but we already loaded the data
        # So we'll call verify_submission directly and then calculate the score
        score_details = green_agent.verify_submission(white_agent_data)
        results = green_agent.calculate_final_score(score_details)
        results["task_level"] = task_level
        results["task_id"] = task_id
        results["white_agent_path"] = white_agent_path
        
        # Save results if output path is specified
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to: {output_path}")
        
        return results
        
    except Exception as e:
        return {
            "error": f"Evaluation failed: {str(e)}",
            "score": 0.0,
            "task_level": task_level,
            "task_id": task_id,
            "white_agent_path": white_agent_path
        }


def main():
    """Main entry point for the benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Run the MechGAIA benchmark evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Level 1 stress analysis task
  python run_benchmark.py --task-level 1 --white-agent-path submissions/agent1_level1.json
  
  # Run Level 2 shaft design task with output file
  python run_benchmark.py --task-level 2 --white-agent-path submissions/agent1_level2.json --output results.json
  
  # Run Level 3 plate optimization task
  python run_benchmark.py --task-level 3 --white-agent-path submissions/agent1_level3.json
        """
    )
    
    parser.add_argument(
        "--task-level",
        type=int,
        choices=[1, 2, 3],
        required=True,
        help="The task level to run (1: Stress Analysis, 2: Shaft Design, 3: Plate Optimization)"
    )
    
    parser.add_argument(
        "--white-agent-path",
        type=str,
        required=True,
        help="Path to the white agent's submission JSON file"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Optional path to save the evaluation results"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate that the white agent file exists
    if not os.path.exists(args.white_agent_path):
        print(f"Error: White agent submission file not found: {args.white_agent_path}")
        sys.exit(1)
    
    # Run the benchmark
    print(f"Running MechGAIA Level {args.task_level} benchmark...")
    print(f"White agent submission: {args.white_agent_path}")
    
    results = run_benchmark(
        task_level=args.task_level,
        white_agent_path=args.white_agent_path,
        output_path=args.output
    )
    
    # Display results
    if args.verbose:
        print("\n" + "="*50)
        print("EVALUATION RESULTS")
        print("="*50)
        print(json.dumps(results, indent=2))
    else:
        print(f"\nFinal Score: {results.get('final_score', 0.0):.3f}")
        if 'error' in results:
            print(f"Error: {results['error']}")
        elif 'details' in results:
            print("Score Details:")
            for key, value in results['details'].items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.3f}")


if __name__ == "__main__":
    main()
