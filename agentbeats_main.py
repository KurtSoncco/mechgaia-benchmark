#!/usr/bin/env python3
"""
MechGAIA Green Agent - AgentBeats SDK Integration (Robust Version)

This is the main entry point for the MechGAIA green agent when running on the AgentBeats platform.
It handles the communication with the AgentBeats SDK and orchestrates the evaluation of white agents.

This version includes comprehensive error handling and robustness improvements.
"""

import json
import os
import sys
import time
import signal
import threading
from pathlib import Path
from typing import Any, Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Safe imports with error handling
try:
    from agents.level1_stress_task import Level1StressTask
    LEVEL1_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Level1 agent not available: {e}")
    LEVEL1_AVAILABLE = False

try:
    from agents.level2_shaft_design_task import Level2ShaftDesignTask
    LEVEL2_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Level2 agent not available: {e}")
    LEVEL2_AVAILABLE = False

try:
    from agents.level3_plate_optimization_task import Level3PlateOptimizationTask
    LEVEL3_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Level3 agent not available: {e}")
    LEVEL3_AVAILABLE = False

try:
    from metrics_system import EvaluationResult, get_metrics_collector
    METRICS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Metrics system not available: {e}")
    METRICS_AVAILABLE = False


class MechGAIAGreenAgent:
    """
    Main green agent class that integrates with AgentBeats SDK.

    This agent evaluates white agent submissions against the MechGAIA benchmark tasks.
    """

    def __init__(self):
        self.agent_name = "MechGAIA-Green-Agent"
        self.version = "0.1.0"
        self.supported_levels = []
        
        # Determine available levels based on successful imports
        if LEVEL1_AVAILABLE:
            self.supported_levels.append(1)
        if LEVEL2_AVAILABLE:
            self.supported_levels.append(2)
        if LEVEL3_AVAILABLE:
            self.supported_levels.append(3)

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
        try:
            if task_level == 1 and LEVEL1_AVAILABLE:
                return Level1StressTask(task_id)
            elif task_level == 2 and LEVEL2_AVAILABLE:
                return Level2ShaftDesignTask(task_id)
            elif task_level == 3 and LEVEL3_AVAILABLE:
                return Level3PlateOptimizationTask(task_id)
            else:
                raise ValueError(f"Invalid or unavailable task level: {task_level}")
        except Exception as e:
            raise ValueError(f"Failed to initialize green agent for level {task_level}: {str(e)}")

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

            # Record metrics if available
            evaluation_time_ms = int((time.time() - start_time) * 1000)

            # Extract agent information from submission or use defaults
            agent_id = submission_data.get("agent_id", f"agent_{int(time.time())}")
            agent_name = submission_data.get("agent_name", "Unknown Agent")

            # Create evaluation result for metrics
            eval_result = EvaluationResult(
                agent_id=agent_id,
                agent_name=agent_name,
                task_level=str(green_agent.task_id.split("_")[-1]) if hasattr(green_agent, 'task_id') else "1",
                task_id=getattr(green_agent, 'task_id', 'unknown'),
                final_score=results.get("final_score", 0.0),
                details=results.get("details", {}),
                timestamp=datetime.now(timezone.utc),
                submission_data=submission_data,
                evaluation_time_ms=evaluation_time_ms,
                platform="AgentBeats",
            )

            # Record the evaluation in metrics system if available
            if METRICS_AVAILABLE:
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
            "available_agents": {
                "level1": LEVEL1_AVAILABLE,
                "level2": LEVEL2_AVAILABLE,
                "level3": LEVEL3_AVAILABLE,
                "metrics": METRICS_AVAILABLE,
            }
        }


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks and agent info."""
    
    def __init__(self, agent, *args, **kwargs):
        self.agent = agent
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        try:
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "healthy",
                    "agent_name": self.agent.agent_name,
                    "version": self.agent.version,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "supported_levels": self.agent.supported_levels
                }
                self.wfile.write(json.dumps(response).encode())
            elif self.path == '/info':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                info = self.agent.get_agent_info()
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


def get_port() -> int:
    """Get the port number from environment variables with proper fallback."""
    try:
        # Try AGENTBEATS_PORT first, then PORT, then default to 8080
        port_str = os.environ.get('AGENTBEATS_PORT') or os.environ.get('PORT', '8080')
        
        # Handle empty strings and whitespace
        if not port_str or not port_str.strip():
            port_str = '8080'
        
        port_str = port_str.strip()
        port = int(port_str)
        
        # Validate port range
        if not (1 <= port <= 65535):
            print(f"Warning: Port {port} out of range, using 8080")
            port = 8080
            
        return port
    except (ValueError, TypeError) as e:
        print(f"Warning: Invalid port configuration: {e}, using 8080")
        return 8080


def start_health_server(agent, port: int) -> Optional[threading.Thread]:
    """Start the health check server in a separate thread."""
    try:
        # Create a custom handler class with the agent instance
        class AgentHealthHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.agent = agent
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                try:
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = {
                            "status": "healthy",
                            "agent_name": self.agent.agent_name,
                            "version": self.agent.version,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "supported_levels": self.agent.supported_levels
                        }
                        self.wfile.write(json.dumps(response).encode())
                    elif self.path == '/info':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        info = self.agent.get_agent_info()
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

        def serve():
            try:
                server = HTTPServer(('0.0.0.0', port), AgentHealthHandler)
                print(f"Health server starting on port {port}")
                server.serve_forever()
            except Exception as e:
                print(f"Health server failed to start: {e}")
                import traceback
                traceback.print_exc()

        health_thread = threading.Thread(target=serve, daemon=True)
        health_thread.start()
        return health_thread
        
    except Exception as e:
        print(f"Failed to start health server: {e}")
        return None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """
    Main entry point for AgentBeats SDK integration.

    This function handles the communication with the AgentBeats platform
    and processes incoming evaluation requests.
    """
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize the agent
    try:
        agent = MechGAIAGreenAgent()
        print(f"Initialized {agent.agent_name} v{agent.version}")
        print(f"Supported levels: {agent.supported_levels}")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        sys.exit(1)
    
    # Start health server
    port = get_port()
    health_thread = start_health_server(agent, port)
    
    if health_thread:
        # Give the health server time to start
        time.sleep(2)
        print("MechGAIA Green Agent started successfully")
        print(f"Health endpoint available at: http://0.0.0.0:{port}/health")
        print(f"Agent info available at: http://0.0.0.0:{port}/info")
    else:
        print("Warning: Health server failed to start")

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
        print("Waiting for AgentBeats platform input...")
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
            except Exception as e:
                error_result = {"error": f"Processing error: {str(e)}", "score": 0.0}
                print(json.dumps(error_result))
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("MechGAIA Green Agent shutting down")


if __name__ == "__main__":
    main()
