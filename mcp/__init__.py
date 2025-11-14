"""
Model Context Protocol (MCP) Implementation

MCP provides a standardized way for LLMs to interact with external tools,
data sources, and resources.
"""

from .server import MCPServer, MCPTool, MCPResource
from .client import MCPClient
from .protocol import MCPRequest, MCPResponse, MCPError

__all__ = [
    "MCPServer",
    "MCPTool",
    "MCPResource",
    "MCPClient",
    "MCPRequest",
    "MCPResponse",
    "MCPError",
]

