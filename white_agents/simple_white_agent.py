#!/usr/bin/env python3
"""
White agent implementation - the target agent being tested.

This agent implements the A2A protocol and can be used for testing against
the MechGAIA green agent benchmark.
"""

import os
import uvicorn
import dotenv
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.utils import new_agent_text_message
from litellm import completion


dotenv.load_dotenv()


def prepare_white_agent_card(url):
    """Prepare the agent card for the white agent."""
    skill = AgentSkill(
        id="task_fulfillment",
        name="Task Fulfillment",
        description="Handles user requests and completes tasks",
        tags=["general"],
        examples=[],
    )
    card = AgentCard(
        name="file_agent",
        description="Test agent from file",
        url=url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(),
        skills=[skill],
    )
    return card


class GeneralWhiteAgentExecutor(AgentExecutor):
    """General white agent executor that uses LLM to handle requests."""

    def __init__(self):
        self.ctx_id_to_messages = {}
        # Get LLM configuration from environment variables
        self.llm_model = os.getenv("LLM_MODEL", "ollama/llama3")
        self.llm_provider = os.getenv("LLM_PROVIDER", "ollama")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the agent request using LLM."""
        # Parse the task
        user_input = context.get_user_input()
        if context.context_id not in self.ctx_id_to_messages:
            self.ctx_id_to_messages[context.context_id] = []
        messages = self.ctx_id_to_messages[context.context_id]
        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        # Prepare litellm completion call
        # For Ollama, use format: "ollama/model_name"
        # For OpenAI, use format: "openai/gpt-4o" or just "gpt-4o"
        model = self.llm_model

        # Configure API base URL for Ollama if needed
        api_base = None
        if self.llm_provider == "ollama" or model.startswith("ollama/"):
            api_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            # Remove "ollama/" prefix if present, litellm handles it
            if model.startswith("ollama/"):
                model = model.replace("ollama/", "")

        try:
            response = completion(
                messages=messages,
                model=model,
                custom_llm_provider=self.llm_provider if self.llm_provider != "ollama" else None,
                api_base=api_base,
                temperature=self.temperature,
            )
            next_message = response.choices[0].message.model_dump()  # type: ignore
            messages.append(
                {
                    "role": "assistant",
                    "content": next_message["content"],
                }
            )
            await event_queue.enqueue_event(
                new_agent_text_message(
                    next_message["content"], context_id=context.context_id
                )
            )
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error processing request: {str(e)}"
            await event_queue.enqueue_event(
                new_agent_text_message(
                    error_message, context_id=context.context_id
                )
            )

    async def cancel(self, context, event_queue) -> None:
        """Cancel the current execution."""
        raise NotImplementedError


def start_white_agent(agent_name="general_white_agent", host="localhost", port=9002):
    """
    Start the white agent server.

    Args:
        agent_name: Name of the agent
        host: Host to bind to
        port: Port to bind to
    """
    print("Starting white agent...")
    print(f"LLM Model: {os.getenv('LLM_MODEL', 'ollama/llama3')}")
    print(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'ollama')}")
    url = f"http://{host}:{port}"
    card = prepare_white_agent_card(url)

    request_handler = DefaultRequestHandler(
        agent_executor=GeneralWhiteAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler,
    )

    print(f"White agent starting on {url}")
    uvicorn.run(app.build(), host=host, port=port)


if __name__ == "__main__":
    # Allow configuration via environment variables
    host = os.getenv("WHITE_AGENT_HOST", "localhost")
    port = int(os.getenv("WHITE_AGENT_PORT", "9002"))
    start_white_agent(host=host, port=port)

