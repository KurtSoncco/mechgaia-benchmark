import subprocess
import json
import sys
import time

def verify_agent():
    print("Starting verification...")
    
    # Mock submission data
    submission = {
        "task_level": 1,
        "white_agent_submission": {
            "answer_pa": 31830000,
            "reasoning_code": "result = 31830000"
        },
        "task_id": "mechgaia_level_1"
    }
    
    # Start the agent process
    process = subprocess.Popen(
        [sys.executable, "agentbeats_main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"AGENTBEATS_HOST": "localhost", "AGENTBEATS_PORT": "8080"}
    )
    
    try:
        # Wait for startup
        time.sleep(3)
        
        # Send submission
        print("Sending submission...")
        submission_str = json.dumps(submission) + "\n"
        process.stdin.write(submission_str)
        process.stdin.flush()
        print("Submission sent.")
        
        # Read response
        print("Waiting for response...")
        # Read line by line until we get valid JSON or timeout
        start_wait = time.time()
        while time.time() - start_wait < 10:
            line = process.stdout.readline()
            if line:
                print(f"Received line: {line.strip()}")
                try:
                    response = json.loads(line)
                    print(f"Received valid JSON response: {json.dumps(response, indent=2)}")
                    if response.get("final_score") == 1.0:
                        print("SUCCESS: Agent returned expected score.")
                    else:
                        print("FAILURE: Agent returned unexpected score.")
                    return
                except json.JSONDecodeError:
                    continue
            else:
                time.sleep(0.1)
        
        print("FAILURE: Timed out waiting for response.")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print("Terminating process...")
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=2)
            print("Agent Stdout (remaining):", stdout)
            print("Agent Stderr:", stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            print("Process killed.")

if __name__ == "__main__":
    verify_agent()
