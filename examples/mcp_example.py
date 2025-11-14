"""
Example usage of MCP (Model Context Protocol) with MechGAIA.

This example demonstrates how to set up an MCP server and client
for tool integration with LLMs.
"""

import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp import MCPServer, MCPTool, MCPClient
from llm_providers import get_llm_provider, LLMMessage, MessageRole


def create_mcp_server():
    """Create an example MCP server with tools."""
    server = MCPServer(name="MechGAIA MCP Server", version="1.0.0")
    
    # Register a calculator tool
    def calculator_handler(args: dict) -> dict:
        """Calculate a mathematical expression."""
        expression = args.get("expression", "")
        try:
            result = eval(expression)  # In production, use a safe evaluator
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": str(e)}
    
    calculator_tool = MCPTool(
        name="calculator",
        description="Evaluate a mathematical expression",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
        handler=calculator_handler,
    )
    server.register_tool(calculator_tool)
    
    # Register a stress analysis tool
    def stress_analysis_handler(args: dict) -> dict:
        """Calculate stress in a beam."""
        force = args.get("force", 0)
        area = args.get("area", 1)
        stress = force / area if area > 0 else 0
        return {
            "stress": stress,
            "force": force,
            "area": area,
            "unit": "Pa",
        }
    
    stress_tool = MCPTool(
        name="stress_analysis",
        description="Calculate stress in a structural element",
        input_schema={
            "type": "object",
            "properties": {
                "force": {"type": "number", "description": "Applied force in Newtons"},
                "area": {"type": "number", "description": "Cross-sectional area in m²"},
            },
            "required": ["force", "area"],
        },
        handler=stress_analysis_handler,
    )
    server.register_tool(stress_tool)
    
    return server


class MCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP server."""
    
    def __init__(self, server, *args, **kwargs):
        self.mcp_server = server
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/mcp":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            
            try:
                response_json = self.mcp_server.handle_json(post_data.decode("utf-8"))
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(response_json.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                error_response = json.dumps({"error": str(e)})
                self.wfile.write(error_response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Disable logging


def run_mcp_server(port=8000):
    """Run the MCP server."""
    server = create_mcp_server()
    
    def handler_factory(*args, **kwargs):
        return MCPHandler(server, *args, **kwargs)
    
    httpd = HTTPServer(("localhost", port), handler_factory)
    print(f"MCP Server running on http://localhost:{port}")
    httpd.serve_forever()


def example_mcp_client():
    """Example using MCP client to interact with tools."""
    print("=== MCP Client Example ===")
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_mcp_server, daemon=True)
    server_thread.start()
    
    import time
    time.sleep(1)  # Wait for server to start
    
    try:
        client = MCPClient("http://localhost:8000")
        
        # Initialize connection
        init_result = client.initialize()
        print(f"Initialized: {init_result}")
        
        # List available tools
        tools = client.list_tools()
        print(f"\nAvailable tools: {[tool['name'] for tool in tools]}")
        
        # Call calculator tool
        result = client.call_tool("calculator", {"expression": "2 + 2 * 3"})
        print(f"\nCalculator result: {result}")
        
        # Call stress analysis tool
        stress_result = client.call_tool(
            "stress_analysis", {"force": 1000, "area": 0.01}
        )
        print(f"Stress analysis result: {stress_result}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_llm_with_mcp():
    """Example using LLM with MCP tools."""
    print("\n=== LLM with MCP Example ===")
    
    # This would integrate MCP tools with an LLM provider
    # The LLM can call MCP tools as functions
    
    try:
        # Get tools from MCP server
        client = MCPClient("http://localhost:8000")
        client.initialize()
        tools = client.list_tools()
        
        # Convert MCP tools to LLM function format
        llm_tools = []
        for tool in tools:
            llm_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"],
                }
            })
        
        # Use LLM with tools
        provider = get_llm_provider(provider="openai", model="gpt-4")
        
        messages = [
            LLMMessage(
                role=MessageRole.USER,
                content="Calculate the stress for a force of 5000N on an area of 0.02m²",
            ),
        ]
        
        response = provider.chat(messages, tools=llm_tools)
        print(f"LLM Response: {response.content}")
        
        # If LLM calls a tool, execute it via MCP
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                result = client.call_tool(tool_name, tool_args)
                print(f"Tool {tool_name} result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("MCP Usage Examples\n")
    
    # Uncomment to run examples:
    # example_mcp_client()
    # example_llm_with_mcp()
    
    print("To run examples, uncomment the desired function call above.")

