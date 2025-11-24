"""
A2A Transport layer implementations.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests
from aiohttp import web, ClientSession, WSMsgType
import aiohttp


class A2ATransport(ABC):
    """Abstract base class for A2A transport."""
    
    @abstractmethod
    async def start(self, agent: Any) -> None:
        """Start the transport."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport."""
        pass
    
    @abstractmethod
    async def send_message(self, message: Dict[str, Any], receiver_id: str) -> None:
        """Send a message."""
        pass
    
    @abstractmethod
    async def send_request(
        self, request: Dict[str, Any], receiver_id: str, timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Send a request and wait for response."""
        pass


class HTTPTransport(A2ATransport):
    """HTTP-based transport for A2A."""
    
    def __init__(self, base_url: str, port: int = 8080):
        """
        Initialize HTTP transport.
        
        Args:
            base_url: Base URL for agent communication
            port: Port to listen on
        """
        self.base_url = base_url
        self.port = port
        self.agent: Optional[Any] = None
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.agent_endpoints: Dict[str, str] = {}
    
    async def start(self, agent: Any) -> None:
        """Start HTTP server."""
        self.agent = agent
        self.app = web.Application()
        self.app.router.add_post("/a2a/message", self._handle_message)
        self.app.router.add_post("/a2a/request", self._handle_request)
        self.app.router.add_get("/a2a/capabilities", self._handle_capabilities)
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await site.start()
    
    async def stop(self) -> None:
        """Stop HTTP server."""
        if self.runner:
            await self.runner.cleanup()
    
    async def _handle_message(self, request: web.Request) -> web.Response:
        """Handle incoming message."""
        try:
            data = await request.json()
            message = self.agent.__class__.__module__ + "." + "A2AMessage"
            # Import here to avoid circular dependency
            from .protocol import A2AMessage
            
            msg = A2AMessage.from_dict(data)
            response = await self.agent.handle_message(msg)
            
            if response:
                return web.json_response(response.to_dict())
            return web.json_response({"status": "ok"})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_request(self, request: web.Request) -> web.Response:
        """Handle incoming request."""
        try:
            data = await request.json()
            from .protocol import A2ARequest, A2AResponse
            
            req = A2ARequest.from_dict(data)
            response = await self.agent.handle_message(req)
            
            if response:
                return web.json_response(response.to_dict())
            return web.json_response({"error": "No response"}, status=500)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _handle_capabilities(self, request: web.Request) -> web.Response:
        """Handle capabilities request."""
        capabilities = self.agent.get_capabilities()
        return web.json_response(capabilities.to_dict())
    
    async def send_message(self, message: Dict[str, Any], receiver_id: str) -> None:
        """Send a message via HTTP."""
        endpoint = self.agent_endpoints.get(receiver_id)
        if not endpoint:
            # Try to discover endpoint
            endpoint = f"{self.base_url}/agents/{receiver_id}/a2a/message"
        
        async with ClientSession() as session:
            async with session.post(endpoint, json=message) as resp:
                resp.raise_for_status()
    
    async def send_request(
        self, request: Dict[str, Any], receiver_id: str, timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Send a request via HTTP and wait for response."""
        endpoint = self.agent_endpoints.get(receiver_id)
        if not endpoint:
            endpoint = f"{self.base_url}/agents/{receiver_id}/a2a/request"
        
        async with ClientSession() as session:
            async with session.post(
                endpoint, json=request, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                resp.raise_for_status()
                return await resp.json()


class WebSocketTransport(A2ATransport):
    """WebSocket-based transport for A2A."""
    
    def __init__(self, port: int = 8080):
        """
        Initialize WebSocket transport.
        
        Args:
            port: Port to listen on
        """
        self.port = port
        self.agent: Optional[Any] = None
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.connections: Dict[str, web.WebSocketResponse] = {}
    
    async def start(self, agent: Any) -> None:
        """Start WebSocket server."""
        self.agent = agent
        self.app = web.Application()
        self.app.router.add_get("/a2a/ws", self._handle_websocket)
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await site.start()
    
    async def stop(self) -> None:
        """Stop WebSocket server."""
        if self.runner:
            await self.runner.cleanup()
    
    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connection."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        agent_id = request.query.get("agent_id", "unknown")
        self.connections[agent_id] = ws
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    from .protocol import A2AMessage
                    
                    message = A2AMessage.from_dict(data)
                    response = await self.agent.handle_message(message)
                    
                    if response:
                        await ws.send_str(response.to_json())
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            if agent_id in self.connections:
                del self.connections[agent_id]
        
        return ws
    
    async def send_message(self, message: Dict[str, Any], receiver_id: str) -> None:
        """Send a message via WebSocket."""
        if receiver_id in self.connections:
            ws = self.connections[receiver_id]
            await ws.send_str(json.dumps(message))
    
    async def send_request(
        self, request: Dict[str, Any], receiver_id: str, timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Send a request via WebSocket and wait for response."""
        if receiver_id not in self.connections:
            raise RuntimeError(f"Agent {receiver_id} not connected")
        
        ws = self.connections[receiver_id]
        await ws.send_str(json.dumps(request))
        
        # Wait for response
        try:
            # Use asyncio.wait_for for timeout (compatible with Python 3.10+)
            async def wait_for_response():
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        if data.get("request_id") == request.get("message_id"):
                            return data
                raise TimeoutError(f"No response from {receiver_id}")
            
            return await asyncio.wait_for(wait_for_response(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"No response from {receiver_id} within {timeout}s")

