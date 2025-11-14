"""
A2A Broker for managing agent discovery and routing.
"""

from typing import Dict, List, Optional
from .protocol import A2ACapabilities


class A2ABroker:
    """
    A2A Broker for agent discovery and message routing.
    """
    
    def __init__(self):
        """Initialize the broker."""
        self.agents: Dict[str, A2ACapabilities] = {}
        self.agent_endpoints: Dict[str, str] = {}
    
    def register_agent(
        self, agent_id: str, capabilities: A2ACapabilities, endpoint: str
    ) -> None:
        """
        Register an agent with the broker.
        
        Args:
            agent_id: Agent identifier
            capabilities: Agent capabilities
            endpoint: Agent endpoint URL
        """
        self.agents[agent_id] = capabilities
        self.agent_endpoints[agent_id] = endpoint
    
    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
        if agent_id in self.agent_endpoints:
            del self.agent_endpoints[agent_id]
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """
        Find agents with a specific capability.
        
        Args:
            capability: Capability name
            
        Returns:
            List of agent IDs
        """
        return [
            agent_id
            for agent_id, caps in self.agents.items()
            if capability in caps.capabilities
        ]
    
    def find_agents_by_action(self, action: str) -> List[str]:
        """
        Find agents that support a specific action.
        
        Args:
            action: Action name
            
        Returns:
            List of agent IDs
        """
        return [
            agent_id
            for agent_id, caps in self.agents.items()
            if action in caps.supported_actions
        ]
    
    def get_agent_endpoint(self, agent_id: str) -> Optional[str]:
        """
        Get the endpoint for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Endpoint URL or None
        """
        return self.agent_endpoints.get(agent_id)
    
    def list_agents(self) -> List[A2ACapabilities]:
        """
        List all registered agents.
        
        Returns:
            List of agent capabilities
        """
        return list(self.agents.values())

