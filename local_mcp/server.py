"""
MCP Server implementation.
"""

import json
import asyncio
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from .protocol import MCPRequest, MCPResponse, MCPError, MCPErrorCode


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool definition."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


@dataclass
class MCPResource:
    """Represents an MCP resource."""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP resource definition."""
        result = {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
        }
        if self.mime_type:
            result["mimeType"] = self.mime_type
        return result


class MCPServer:
    """
    MCP Server for exposing tools and resources to LLMs.
    """
    
    def __init__(self, name: str = "MCP Server", version: str = "1.0.0"):
        """
        Initialize the MCP server.
        
        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.handlers: Dict[str, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Set up default MCP protocol handlers."""
        self.handlers["initialize"] = self._handle_initialize
        self.handlers["tools/list"] = self._handle_tools_list
        self.handlers["tools/call"] = self._handle_tools_call
        self.handlers["resources/list"] = self._handle_resources_list
        self.handlers["resources/read"] = self._handle_resources_read
    
    def register_tool(self, tool: MCPTool) -> None:
        """
        Register a tool with the server.
        
        Args:
            tool: MCPTool instance
        """
        self.tools[tool.name] = tool
    
    def register_resource(self, resource: MCPResource) -> None:
        """
        Register a resource with the server.
        
        Args:
            resource: MCPResource instance
        """
        self.resources[resource.uri] = resource
    
    def register_handler(self, method: str, handler: Callable) -> None:
        """
        Register a custom handler for an MCP method.
        
        Args:
            method: MCP method name
            handler: Handler function
        """
        self.handlers[method] = handler
    
    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle an MCP request.
        
        Args:
            request: MCP request
            
        Returns:
            MCP response
        """
        try:
            if request.method in self.handlers:
                handler = self.handlers[request.method]
                result = handler(request.params or {})
                return MCPResponse(result=result, id=request.id)
            else:
                return MCPResponse(
                    error={
                        "code": MCPErrorCode.METHOD_NOT_FOUND,
                        "message": f"Method not found: {request.method}",
                    },
                    id=request.id,
                )
        except Exception as e:
            return MCPResponse(
                error={
                    "code": MCPErrorCode.INTERNAL_ERROR,
                    "message": str(e),
                },
                id=request.id,
            )
    
    def handle_json(self, json_str: str) -> str:
        """
        Handle a JSON-RPC request string.
        
        Args:
            json_str: JSON-RPC request string
            
        Returns:
            JSON-RPC response string
        """
        try:
            data = json.loads(json_str)
            request = MCPRequest(
                method=data.get("method"),
                params=data.get("params"),
                id=data.get("id"),
            )
            response = self.handle_request(request)
            return response.to_json()
        except json.JSONDecodeError:
            error_response = MCPResponse(
                error={
                    "code": MCPErrorCode.PARSE_ERROR,
                    "message": "Invalid JSON",
                }
            )
            return error_response.to_json()
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version,
            },
        }
    
    def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": [tool.to_dict() for tool in self.tools.values()],
        }
    
    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        try:
            result = tool.handler(arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result) if not isinstance(result, str) else result,
                    }
                ],
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}",
                    }
                ],
                "isError": True,
            }
    
    def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request."""
        return {
            "resources": [resource.to_dict() for resource in self.resources.values()],
        }
    
    def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request."""
        uri = params.get("uri")
        if uri not in self.resources:
            raise ValueError(f"Resource not found: {uri}")
        
        resource = self.resources[uri]
        return {
            "contents": [
                {
                    "uri": resource.uri,
                    "mimeType": resource.mime_type or "text/plain",
                    "text": f"Resource: {resource.name}\n{resource.description}",
                }
            ],
        }

