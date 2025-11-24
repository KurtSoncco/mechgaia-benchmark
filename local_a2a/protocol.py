"""
A2A Protocol definitions and message types.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import json
import uuid


class A2AMessageType(str, Enum):
    """A2A message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    CAPABILITIES = "capabilities"


@dataclass
class A2AMessage:
    """Base A2A message."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: A2AMessageType = A2AMessageType.REQUEST
    sender_id: str = ""
    receiver_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create from dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            message_type=A2AMessageType(data.get("message_type", "request")),
            sender_id=data.get("sender_id", ""),
            receiver_id=data.get("receiver_id"),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
        )


@dataclass
class A2ARequest(A2AMessage):
    """A2A request message."""
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize as request message."""
        self.message_type = A2AMessageType.REQUEST
        self.payload = {
            "action": self.action,
            "parameters": self.parameters,
        }
    
    @classmethod
    def create(
        cls,
        sender_id: str,
        receiver_id: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> "A2ARequest":
        """Create a request message."""
        return cls(
            sender_id=sender_id,
            receiver_id=receiver_id,
            action=action,
            parameters=parameters or {},
        )


@dataclass
class A2AResponse(A2AMessage):
    """A2A response message."""
    request_id: str = ""
    success: bool = True
    result: Any = None
    error: Optional[str] = None
    
    def __post_init__(self):
        """Initialize as response message."""
        self.message_type = A2AMessageType.RESPONSE
        self.payload = {
            "request_id": self.request_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
        }
    
    @classmethod
    def create(
        cls,
        sender_id: str,
        receiver_id: str,
        request_id: str,
        success: bool = True,
        result: Any = None,
        error: Optional[str] = None,
    ) -> "A2AResponse":
        """Create a response message."""
        return cls(
            sender_id=sender_id,
            receiver_id=receiver_id,
            request_id=request_id,
            success=success,
            result=result,
            error=error,
        )


@dataclass
class A2ACapabilities:
    """Agent capabilities description."""
    agent_id: str
    agent_name: str
    capabilities: List[str] = field(default_factory=list)
    supported_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "capabilities": self.capabilities,
            "supported_actions": self.supported_actions,
            "metadata": self.metadata,
        }

