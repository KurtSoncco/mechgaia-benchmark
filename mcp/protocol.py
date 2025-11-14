"""
MCP Protocol definitions and message types.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class MCPMessageType(str, Enum):
    """MCP message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass
class MCPRequest:
    """MCP request message."""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "jsonrpc": "2.0",
            "method": self.method,
        }
        if self.params:
            result["params"] = self.params
        if self.id:
            result["id"] = self.id
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class MCPResponse:
    """MCP response message."""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"jsonrpc": "2.0"}
        if self.result is not None:
            result["result"] = self.result
        if self.error:
            result["error"] = self.error
        if self.id:
            result["id"] = self.id
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPResponse":
        """Create from dictionary."""
        return cls(
            result=data.get("result"),
            error=data.get("error"),
            id=data.get("id"),
        )


@dataclass
class MCPError:
    """MCP error."""
    code: int
    message: str
    data: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.data:
            result["data"] = self.data
        return result


# Standard MCP error codes
class MCPErrorCode:
    """Standard MCP error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000

