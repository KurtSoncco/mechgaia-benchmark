"""
A2A Agent implementation.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from .protocol import (
    A2AMessage,
    A2ARequest,
    A2AResponse,
    A2ACapabilities,
    A2AMessageType,
)
from .transport import A2ATransport


class A2AAgent:
    """
    A2A Agent for agent-to-agent communication.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        transport: Optional[A2ATransport] = None,
        capabilities: Optional[List[str]] = None,
    ):
        """
        Initialize the A2A agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            transport: Transport layer for communication
            capabilities: List of agent capabilities
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.transport = transport
        self.capabilities = capabilities or []
        self.action_handlers: Dict[str, Callable] = {}
        self.message_handlers: Dict[A2AMessageType, List[Callable]] = {}
        self.connected_agents: Dict[str, A2ACapabilities] = {}
        self._running = False
    
    def register_action_handler(self, action: str, handler: Callable) -> None:
        """
        Register a handler for a specific action.
        
        Args:
            action: Action name
            handler: Handler function that takes (request: A2ARequest) -> A2AResponse
        """
        self.action_handlers[action] = handler
    
    def register_message_handler(
        self, message_type: A2AMessageType, handler: Callable
    ) -> None:
        """
        Register a handler for a message type.
        
        Args:
            message_type: Message type
            handler: Handler function
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    async def send_request(
        self,
        receiver_id: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> A2AResponse:
        """
        Send a request to another agent.
        
        Args:
            receiver_id: Target agent ID
            action: Action to request
            parameters: Action parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response from the agent
        """
        if not self.transport:
            raise RuntimeError("No transport configured")
        
        request = A2ARequest.create(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            action=action,
            parameters=parameters or {},
        )
        
        # Send request
        response_data = await self.transport.send_request(
            request.to_dict(),
            receiver_id,
            timeout=timeout,
        )
        
        return A2AResponse.from_dict(response_data)
    
    async def send_notification(
        self,
        receiver_id: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send a notification to another agent.
        
        Args:
            receiver_id: Target agent ID
            payload: Notification payload
            metadata: Optional metadata
        """
        if not self.transport:
            raise RuntimeError("No transport configured")
        
        message = A2AMessage(
            message_type=A2AMessageType.NOTIFICATION,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            payload=payload,
            metadata=metadata or {},
        )
        
        await self.transport.send_message(message.to_dict(), receiver_id)
    
    async def handle_message(self, message: A2AMessage) -> Optional[A2AResponse]:
        """
        Handle an incoming message.
        
        Args:
            message: Incoming message
            
        Returns:
            Response if applicable
        """
        # Call message type handlers
        if message.message_type in self.message_handlers:
            for handler in self.message_handlers[message.message_type]:
                await handler(message)
        
        # Handle requests
        if message.message_type == A2AMessageType.REQUEST:
            request = A2ARequest.from_dict(message.to_dict())
            action = request.payload.get("action")
            
            if action in self.action_handlers:
                handler = self.action_handlers[action]
                try:
                    result = await handler(request)
                    return A2AResponse.create(
                        sender_id=self.agent_id,
                        receiver_id=request.sender_id,
                        request_id=request.message_id,
                        success=True,
                        result=result,
                    )
                except Exception as e:
                    return A2AResponse.create(
                        sender_id=self.agent_id,
                        receiver_id=request.sender_id,
                        request_id=request.message_id,
                        success=False,
                        error=str(e),
                    )
            else:
                return A2AResponse.create(
                    sender_id=self.agent_id,
                    receiver_id=request.sender_id,
                    request_id=request.message_id,
                    success=False,
                    error=f"Unknown action: {action}",
                )
        
        return None
    
    def get_capabilities(self) -> A2ACapabilities:
        """Get agent capabilities."""
        return A2ACapabilities(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            capabilities=self.capabilities,
            supported_actions=list(self.action_handlers.keys()),
        )
    
    async def start(self) -> None:
        """Start the agent."""
        if self._running:
            return
        
        self._running = True
        if self.transport:
            await self.transport.start(self)
    
    async def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        if self.transport:
            await self.transport.stop()

