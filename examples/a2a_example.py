"""
Example usage of A2A (Agent-to-Agent) communication with MechGAIA.

This example demonstrates how to set up agents that can communicate
with each other using the A2A protocol.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from a2a import A2AAgent, HTTPTransport, A2ARequest, A2AResponse
from llm_providers import get_llm_provider, LLMMessage, MessageRole


async def example_basic_a2a():
    """Basic A2A agent communication example."""
    print("=== Basic A2A Example ===")
    
    # Create first agent
    agent1 = A2AAgent(
        agent_id="agent-1",
        agent_name="Engineering Agent",
        transport=HTTPTransport(base_url="http://localhost:8080", port=8080),
        capabilities=["stress_analysis", "calculations"],
    )
    
    # Register action handler
    async def handle_calculate(request: A2ARequest) -> dict:
        """Handle calculation request."""
        params = request.payload.get("parameters", {})
        expression = params.get("expression", "")
        try:
            result = eval(expression)  # In production, use a safe evaluator
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    agent1.register_action_handler("calculate", handle_calculate)
    
    # Create second agent
    agent2 = A2AAgent(
        agent_id="agent-2",
        agent_name="Analysis Agent",
        transport=HTTPTransport(base_url="http://localhost:8081", port=8081),
        capabilities=["data_analysis"],
    )
    
    # Start agents
    await agent1.start()
    await agent2.start()
    
    print("Agents started. Waiting for requests...")
    
    # Agent 2 sends a request to Agent 1
    try:
        response = await agent2.send_request(
            receiver_id="agent-1",
            action="calculate",
            parameters={"expression": "2 + 2 * 3"},
        )
        print(f"Response from agent-1: {response.payload}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Cleanup
    await agent1.stop()
    await agent2.stop()


async def example_llm_agent():
    """Example of an agent that uses LLM for processing."""
    print("\n=== LLM Agent Example ===")
    
    # Create an LLM-powered agent
    llm_agent = A2AAgent(
        agent_id="llm-agent",
        agent_name="LLM Assistant Agent",
        transport=HTTPTransport(base_url="http://localhost:8082", port=8082),
        capabilities=["llm_processing", "reasoning"],
    )
    
    # Initialize LLM provider
    try:
        provider = get_llm_provider(provider="openai", model="gpt-4")
    except Exception as e:
        print(f"LLM provider not available: {e}")
        return
    
    # Register LLM action handler
    async def handle_llm_request(request: A2ARequest) -> dict:
        """Handle LLM processing request."""
        params = request.payload.get("parameters", {})
        prompt = params.get("prompt", "")
        
        messages = [
            LLMMessage(role=MessageRole.USER, content=prompt),
        ]
        
        response = provider.chat(messages)
        return {"response": response.content, "model": response.model}
    
    llm_agent.register_action_handler("process", handle_llm_request)
    
    await llm_agent.start()
    print("LLM agent started.")
    
    # Another agent can now send requests to the LLM agent
    # response = await other_agent.send_request(
    #     receiver_id="llm-agent",
    #     action="process",
    #     parameters={"prompt": "What is 2+2?"}
    # )
    
    await llm_agent.stop()


async def example_collaborative_agents():
    """Example of multiple agents collaborating on a task."""
    print("\n=== Collaborative Agents Example ===")
    
    # Create specialized agents
    calculator_agent = A2AAgent(
        agent_id="calculator",
        agent_name="Calculator Agent",
        transport=HTTPTransport(base_url="http://localhost:8083", port=8083),
        capabilities=["arithmetic"],
    )
    
    async def handle_calc(request: A2ARequest) -> dict:
        params = request.payload.get("parameters", {})
        op = params.get("operation")
        a = params.get("a", 0)
        b = params.get("b", 0)
        
        if op == "add":
            return {"result": a + b}
        elif op == "multiply":
            return {"result": a * b}
        else:
            return {"error": "Unknown operation"}
    
    calculator_agent.register_action_handler("calculate", handle_calc)
    
    coordinator_agent = A2AAgent(
        agent_id="coordinator",
        agent_name="Coordinator Agent",
        transport=HTTPTransport(base_url="http://localhost:8084", port=8084),
        capabilities=["coordination"],
    )
    
    async def handle_coordinate(request: A2ARequest) -> dict:
        """Coordinate multiple calculations."""
        params = request.payload.get("parameters", {})
        tasks = params.get("tasks", [])
        
        results = []
        for task in tasks:
            # Send request to calculator agent
            response = await coordinator_agent.send_request(
                receiver_id="calculator",
                action="calculate",
                parameters=task,
            )
            results.append(response.payload.get("result"))
        
        return {"results": results}
    
    coordinator_agent.register_action_handler("coordinate", handle_coordinate)
    
    await calculator_agent.start()
    await coordinator_agent.start()
    
    print("Collaborative agents started.")
    
    # Coordinator can now coordinate multiple calculations
    # response = await coordinator_agent.send_request(
    #     receiver_id="coordinator",
    #     action="coordinate",
    #     parameters={
    #         "tasks": [
    #             {"operation": "add", "a": 5, "b": 3},
    #             {"operation": "multiply", "a": 4, "b": 7},
    #         ]
    #     }
    # )
    
    await calculator_agent.stop()
    await coordinator_agent.stop()


if __name__ == "__main__":
    print("A2A Usage Examples\n")
    print("Note: These examples require async execution.\n")
    
    # Uncomment to run examples:
    # asyncio.run(example_basic_a2a())
    # asyncio.run(example_llm_agent())
    # asyncio.run(example_collaborative_agents())
    
    print("To run examples, uncomment the desired function call above.")

