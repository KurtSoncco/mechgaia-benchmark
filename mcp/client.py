"""
MCP Client implementation for connecting to MCP servers.
"""

import json
import requests
from typing import Any, Dict, List, Optional
from .protocol import MCPRequest, MCPResponse, MCPErrorCode


class MCPClient:
    """
    MCP Client for connecting to MCP servers.
    """
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            server_url: URL of the MCP server
            api_key: Optional API key for authentication
        """
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.initialized = False
        self.server_info: Optional[Dict[str, Any]] = None
    
    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an MCP request to the server.
        
        Args:
            method: MCP method name
            params: Request parameters
            
        Returns:
            Response result
        """
        request = MCPRequest(method=method, params=params)
        
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                f"{self.server_url}/mcp",
                json=request.to_dict(),
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise RuntimeError(f"MCP error: {result['error']}")
            
            return result.get("result", {})
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"MCP request failed: {e}")
    
    def initialize(self, client_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize the connection to the MCP server.
        
        Args:
            client_info: Client information
            
        Returns:
            Server capabilities and info
        """
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": client_info or {
                "name": "MCP Client",
                "version": "1.0.0",
            },
        }
        
        result = self._make_request("initialize", params)
        self.initialized = True
        self.server_info = result.get("serverInfo", {})
        return result
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the server.
        
        Returns:
            List of tool definitions
        """
        if not self.initialized:
            self.initialize()
        
        result = self._make_request("tools/list")
        return result.get("tools", [])
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the server.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.initialized:
            self.initialize()
        
        result = self._make_request("tools/call", {
            "name": name,
            "arguments": arguments,
        })
        return result
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources from the server.
        
        Returns:
            List of resource definitions
        """
        if not self.initialized:
            self.initialize()
        
        result = self._make_request("resources/list")
        return result.get("resources", [])
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource from the server.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource contents
        """
        if not self.initialized:
            self.initialize()
        
        result = self._make_request("resources/read", {"uri": uri})
        return result

