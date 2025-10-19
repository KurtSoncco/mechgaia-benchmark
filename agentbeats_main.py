#!/usr/bin/env python3
"""
MechGAIA Green Agent - AgentBeats SDK Integration

This is the main entry point for the MechGAIA green agent when running on the AgentBeats platform.
It handles the communication with the AgentBeats SDK and orchestrates the evaluation of white agents.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone

from agents.level1_stress_task import Level1StressTask
from agents.level2_shaft_design_task import Level2ShaftDesignTask
from agents.level3_plate_optimization_task import Level3PlateOptimizationTask
from metrics_system import EvaluationResult, get_metrics_collector


class MechGAIAGreenAgent:
    """
    Main green agent class that integrates with AgentBeats SDK.

    This agent evaluates white agent submissions against the MechGAIA benchmark tasks.
    """

    def __init__(self):
        self.agent_name = "MechGAIA-Green-Agent"
        self.version = "0.1.0"
        self.supported_levels = [1, 2, 3]

    def run_agent(self, state: Dict[str, Any], tools: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent function that processes the current state and returns evaluation results.

        Args:
            state: Current game state from AgentBeats platform
            tools: Available tools and functions

        Returns:
            Dictionary containing evaluation results and agent actions
        """
        try:
            # Extract task information from state
            task_level = state.get("task_level", 1)
            white_agent_submission = state.get("white_agent_submission", {})
            task_id = state.get("task_id", f"mechgaia_level_{task_level}")

            # Validate task level
            if task_level not in self.supported_levels:
                return {
                    "error": f"Unsupported task level: {task_level}. Supported levels: {self.supported_levels}",
                    "score": 0.0,
                    "task_level": task_level,
                    "task_id": task_id,
                }

            # Initialize the appropriate green agent
            green_agent = self._get_green_agent(task_level, task_id)

            # Run the evaluation
            evaluation_result = self._evaluate_submission(
                green_agent, white_agent_submission
            )

            # Add AgentBeats-specific metadata
            evaluation_result.update(
                {
                    "agent_name": self.agent_name,
                    "agent_version": self.version,
                    "platform": "AgentBeats",
                    "task_level": task_level,
                    "task_id": task_id,
                }
            )

            return evaluation_result

        except Exception as e:
            return {
                "error": f"Agent execution failed: {str(e)}",
                "score": 0.0,
                "agent_name": self.agent_name,
                "agent_version": self.version,
                "platform": "AgentBeats",
            }

    def _get_green_agent(self, task_level: int, task_id: str):
        """Get the appropriate green agent for the task level."""
        if task_level == 1:
            return Level1StressTask(task_id)
        elif task_level == 2:
            return Level2ShaftDesignTask(task_id)
        elif task_level == 3:
            return Level3PlateOptimizationTask(task_id)
        else:
            raise ValueError(f"Invalid task level: {task_level}")

    def _evaluate_submission(
        self, green_agent, submission_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a white agent submission using the green agent.

        Args:
            green_agent: The green agent instance for the specific task
            submission_data: The white agent's submission data

        Returns:
            Dictionary containing evaluation results
        """
        start_time = time.time()

        try:
            # Verify the submission
            score_details = green_agent.verify_submission(submission_data)

            # Calculate final score
            results = green_agent.calculate_final_score(score_details)

            # Record metrics
            evaluation_time_ms = int((time.time() - start_time) * 1000)

            # Extract agent information from submission or use defaults
            agent_id = submission_data.get("agent_id", f"agent_{int(time.time())}")
            agent_name = submission_data.get("agent_name", "Unknown Agent")

            # Create evaluation result for metrics
            eval_result = EvaluationResult(
                agent_id=agent_id,
                agent_name=agent_name,
                task_level=green_agent.task_id.split("_")[
                    -1
                ],  # Extract level from task_id
                task_id=green_agent.task_id,
                final_score=results.get("final_score", 0.0),
                details=results.get("details", {}),
                timestamp=datetime.now(timezone.utc),
                submission_data=submission_data,
                evaluation_time_ms=evaluation_time_ms,
                platform="AgentBeats",
            )

            # Record the evaluation in metrics system
            try:
                get_metrics_collector().record_evaluation(eval_result)
            except Exception as e:
                print(f"Warning: Failed to record metrics: {e}")

            return results

        except Exception as e:
            return {
                "error": f"Evaluation failed: {str(e)}",
                "score": 0.0,
                "details": {},
            }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this green agent."""
        return {
            "name": self.agent_name,
            "version": self.version,
            "description": "Green agent for MechGAIA benchmark evaluating mechanical engineering design AI agents",
            "supported_levels": self.supported_levels,
            "capabilities": [
                "stress_analysis",
                "shaft_design",
                "plate_optimization",
                "cad_analysis",
                "material_selection",
                "numerical_verification",
            ],
        }


def main():
    """
    Main entry point for AgentBeats SDK integration.

    This function handles the communication with the AgentBeats platform
    and processes incoming evaluation requests.
    """
    agent = MechGAIAGreenAgent()
    
    # Add health check endpoint for Railway/Render
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        "status": "healthy",
                        "agent_name": agent.agent_name,
                        "version": agent.version,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    self.wfile.write(json.dumps(response).encode())
                elif self.path == '/info':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    info = agent.get_agent_info()
                    self.wfile.write(json.dumps(info, indent=2).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'Not Found')
            except Exception as e:
                print(f"Health handler error: {e}")
                try:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b'Internal Server Error')
                except:
                    pass
        
        def log_message(self, format, *args):
            pass  # Disable logging
    
    # Start health check server in background
    def start_health_server():
        try:
            port = int(os.environ.get('AGENTBEATS_PORT', os.environ.get('PORT', 8080)))
            server = HTTPServer(('0.0.0.0', port), HealthHandler)
            print(f"Health server starting on port {port}")
            server.serve_forever()
        except Exception as e:
            print(f"Health server failed to start: {e}")
            import traceback
            traceback.print_exc()
    
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Give the health server time to start
    time.sleep(2)
    print("MechGAIA Green Agent started successfully")
    print("Health endpoint available at: /health")
    print("Agent info available at: /info")

    # Handle command line arguments for AgentBeats
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "info":
            # Return agent information
            info = agent.get_agent_info()
            print(json.dumps(info, indent=2))
            return

        elif command == "evaluate":
            # Evaluate a submission from command line
            if len(sys.argv) < 3:
                print(
                    "Usage: python agentbeats_main.py evaluate <submission_file> [task_level]"
                )
                sys.exit(1)

            submission_file = sys.argv[2]
            task_level = int(sys.argv[3]) if len(sys.argv) > 3 else 1

            # Load submission
            try:
                with open(submission_file, "r") as f:
                    submission_data = json.load(f)
            except Exception as e:
                print(f"Error loading submission: {e}")
                sys.exit(1)

            # Create state for evaluation
            state = {
                "task_level": task_level,
                "white_agent_submission": submission_data,
                "task_id": f"mechgaia_level_{task_level}",
            }

            # Run evaluation
            result = agent.run_agent(state, {})
            print(json.dumps(result, indent=2))
            return

    # Interactive mode for AgentBeats platform
    try:
        while True:
            # Read input from AgentBeats platform
            line = sys.stdin.readline()
            if not line:
                break

            try:
                # Parse the incoming state
                state = json.loads(line.strip())

                # Run the agent
                result = agent.run_agent(state, {})

                # Send result back to AgentBeats platform
                print(json.dumps(result))
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                error_result = {"error": f"Invalid JSON input: {str(e)}", "score": 0.0}
                print(json.dumps(error_result))
                sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_result = {"error": f"Agent execution error: {str(e)}", "score": 0.0}
        print(json.dumps(error_result))


if __name__ == "__main__":
    main()
