"""
AgentBeats Green Agent - Coordination and Orchestration Agent

This is an AgentBeats-compliant Green Agent that acts as a coordinator/judge agent
for managing state and orchestrating communication between multiple agents.

Based on the AgentBeats specification, a Green Agent:
- Maintains shared state across agents
- Coordinates agent-to-agent (A2A) communication  
- Orchestrates turn-taking between multiple agents
- Acts as a judge/referee in multi-agent scenarios

Example use case: Chess game coordination between GPT-4o and GPT-5 agents
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
from datetime import datetime


class AgentStatus(Enum):
    """Status of an agent in the system."""
    WAITING = "waiting"
    ACTIVE = "active" 
    THINKING = "thinking"
    DONE = "done"
    ERROR = "error"


@dataclass
class Message:
    """Represents a message in agent-to-agent communication."""
    sender_id: str
    recipient_id: str
    message_type: str
    content: Any
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class AgentInfo:
    """Information about an agent in the system."""
    agent_id: str
    agent_type: str
    status: AgentStatus
    capabilities: List[str]
    last_activity: float
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = time.time()


class GreenAgent:
    """
    AgentBeats Green Agent - Multi-Agent Coordination and Orchestration
    
    The Green Agent acts as a central coordinator that:
    - Manages multiple agent instances and their states
    - Orchestrates turn-taking and communication between agents
    - Maintains shared state across all agents
    - Acts as a judge/referee for multi-agent interactions
    - Provides agent-to-agent (A2A) communication infrastructure
    """
    
    def __init__(self, name: str = "GreenCoordinator"):
        """Initialize the Green Agent coordinator."""
        self.name = name
        self.agents: Dict[str, AgentInfo] = {}
        self.shared_state: Dict[str, Any] = {}
        self.message_queue: queue.Queue = queue.Queue()
        self.turn_order: List[str] = []
        self.current_turn_index: int = 0
        self.session_active: bool = False
        self.session_log: List[Dict] = []
        self.coordination_rules: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        
        # Initialize coordination system
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Set up default coordination rules."""
        self.coordination_rules = {
            "turn_timeout": self._handle_turn_timeout,
            "agent_error": self._handle_agent_error,
            "state_conflict": self._handle_state_conflict,
            "communication_filter": self._filter_communication
        }
    
    def register_agent(self, agent_id: str, agent_type: str, 
                      capabilities: List[str] = None) -> bool:
        """Register a new agent with the coordinator."""
        if capabilities is None:
            capabilities = []
        
        with self.lock:
            if agent_id in self.agents:
                return False
            
            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_type=agent_type,
                status=AgentStatus.WAITING,
                capabilities=capabilities,
                last_activity=time.time()
            )
            
            self.agents[agent_id] = agent_info
            self.turn_order.append(agent_id)
            
            self._log_event("agent_registered", {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities
            })
            
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the coordination system."""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            del self.agents[agent_id]
            if agent_id in self.turn_order:
                self.turn_order.remove(agent_id)
            
            self._log_event("agent_unregistered", {"agent_id": agent_id})
            return True
    
    def update_shared_state(self, key: str, value: Any, 
                           requesting_agent: str = None) -> bool:
        """Update shared state that all agents can access."""
        with self.lock:
            old_value = self.shared_state.get(key)
            self.shared_state[key] = value
            
            self._log_event("state_updated", {
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "requesting_agent": requesting_agent
            })
            
            # Notify all agents of state change
            self._broadcast_state_change(key, value, requesting_agent)
            return True
    
    def get_shared_state(self, key: str = None) -> Any:
        """Get shared state value(s)."""
        with self.lock:
            if key is None:
                return dict(self.shared_state)
            return self.shared_state.get(key)
    
    def send_message(self, sender_id: str, recipient_id: str, 
                    message_type: str, content: Any) -> bool:
        """Send a message between agents through the coordinator."""
        # Allow coordinator to send messages to agents
        if (sender_id != self.name and sender_id not in self.agents) or recipient_id not in self.agents:
            return False
        
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content
        )
        
        # Apply communication filter
        if not self.coordination_rules["communication_filter"](message):
            return False
        
        self.message_queue.put(message)
        
        self._log_event("message_sent", {
            "sender": sender_id,
            "recipient": recipient_id,
            "type": message_type,
            "timestamp": message.timestamp
        })
        
        return True
    
    def get_messages_for_agent(self, agent_id: str) -> List[Message]:
        """Get all pending messages for a specific agent."""
        messages = []
        temp_messages = []
        
        # Collect all messages and filter for this agent
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message.recipient_id == agent_id:
                    messages.append(message)
                else:
                    temp_messages.append(message)
        except queue.Empty:
            pass
        
        # Put back messages not for this agent
        for msg in temp_messages:
            self.message_queue.put(msg)
        
        return messages
    
    def start_coordination_session(self) -> bool:
        """Start a new coordination session."""
        with self.lock:
            if self.session_active:
                return False
            
            self.session_active = True
            self.current_turn_index = 0
            self.session_log.clear()
            
            # Set all agents to waiting status
            for agent_info in self.agents.values():
                agent_info.status = AgentStatus.WAITING
            
            self._log_event("session_started", {
                "total_agents": len(self.agents),
                "turn_order": self.turn_order
            })
            
            return True
    
    def end_coordination_session(self) -> Dict:
        """End the current coordination session and return summary."""
        with self.lock:
            if not self.session_active:
                return {}
            
            self.session_active = False
            
            summary = {
                "session_duration": time.time() - self.session_log[0]["timestamp"] if self.session_log else 0,
                "total_events": len(self.session_log),
                "participating_agents": list(self.agents.keys()),
                "final_state": dict(self.shared_state),
                "session_log": self.session_log.copy()
            }
            
            self._log_event("session_ended", summary)
            return summary
    
    def get_current_turn_agent(self) -> Optional[str]:
        """Get the agent whose turn it currently is."""
        if not self.session_active or not self.turn_order:
            return None
        return self.turn_order[self.current_turn_index % len(self.turn_order)]
    
    def advance_turn(self) -> str:
        """Advance to the next agent's turn."""
        with self.lock:
            if not self.session_active or not self.turn_order:
                return None
            
            # Mark current agent as done
            current_agent = self.get_current_turn_agent()
            if current_agent and current_agent in self.agents:
                self.agents[current_agent].status = AgentStatus.WAITING
            
            # Advance turn
            self.current_turn_index += 1
            next_agent = self.get_current_turn_agent()
            
            if next_agent and next_agent in self.agents:
                self.agents[next_agent].status = AgentStatus.ACTIVE
            
            self._log_event("turn_advanced", {
                "from_agent": current_agent,
                "to_agent": next_agent,
                "turn_number": self.current_turn_index
            })
            
            return next_agent
    
    def request_agent_action(self, agent_id: str, action_type: str, 
                           parameters: Dict = None) -> bool:
        """Request an action from a specific agent."""
        if agent_id not in self.agents:
            return False
        
        with self.lock:
            self.agents[agent_id].status = AgentStatus.THINKING
            self.agents[agent_id].last_activity = time.time()
        
        # Send action request through message system
        return self.send_message(
            sender_id=self.name,
            recipient_id=agent_id,
            message_type="action_request",
            content={
                "action_type": action_type,
                "parameters": parameters or {}
            }
        )
    
    def agent_response_received(self, agent_id: str, response: Any) -> bool:
        """Handle response from an agent."""
        if agent_id not in self.agents:
            return False
        
        with self.lock:
            self.agents[agent_id].status = AgentStatus.DONE
            self.agents[agent_id].last_activity = time.time()
        
        self._log_event("agent_response", {
            "agent_id": agent_id,
            "response": response
        })
        
        return True
    
    def get_coordination_status(self) -> Dict:
        """Get current status of all agents and coordination state."""
        with self.lock:
            return {
                "coordinator_name": self.name,
                "session_active": self.session_active,
                "current_turn": self.get_current_turn_agent(),
                "turn_number": self.current_turn_index,
                "agents": {
                    agent_id: {
                        "type": info.agent_type,
                        "status": info.status.value,
                        "capabilities": info.capabilities,
                        "last_activity": info.last_activity
                    }
                    for agent_id, info in self.agents.items()
                },
                "shared_state_keys": list(self.shared_state.keys()),
                "pending_messages": self.message_queue.qsize()
            }
    
    def save_session_log(self, filename: str = None) -> str:
        """Save the session log to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"coordination_session_{timestamp}.json"
        
        log_data = {
            "coordinator": self.name,
            "session_log": self.session_log,
            "final_state": self.shared_state,
            "agent_summary": {
                agent_id: asdict(info) for agent_id, info in self.agents.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        return filename
    
    def _log_event(self, event_type: str, data: Dict):
        """Log an event in the coordination session."""
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        }
        self.session_log.append(log_entry)
    
    def _broadcast_state_change(self, key: str, value: Any, originator: str):
        """Notify all agents about shared state changes."""
        for agent_id in self.agents:
            if agent_id != originator:
                self.send_message(
                    sender_id=self.name,
                    recipient_id=agent_id,
                    message_type="state_change",
                    content={"key": key, "value": value}
                )
    
    def _handle_turn_timeout(self, agent_id: str) -> bool:
        """Handle agent turn timeout."""
        if agent_id in self.agents:
            self.agents[agent_id].status = AgentStatus.ERROR
            self._log_event("turn_timeout", {"agent_id": agent_id})
            return True
        return False
    
    def _handle_agent_error(self, agent_id: str, error: str) -> bool:
        """Handle agent error."""
        if agent_id in self.agents:
            self.agents[agent_id].status = AgentStatus.ERROR
            self._log_event("agent_error", {"agent_id": agent_id, "error": error})
            return True
        return False
    
    def _handle_state_conflict(self, key: str, conflicting_values: List) -> Any:
        """Handle conflicts in shared state."""
        # Default resolution: use the most recent value
        self._log_event("state_conflict", {
            "key": key,
            "conflicting_values": conflicting_values
        })
        return conflicting_values[-1] if conflicting_values else None
    
    def _filter_communication(self, message: Message) -> bool:
        """Filter agent-to-agent communication."""
        # Default: allow all communication
        # Can be overridden for specific coordination needs
        return True
    
    def __str__(self) -> str:
        """String representation of the Green Agent."""
        status = "Active" if self.session_active else "Inactive"
        return (f"Green Agent '{self.name}' - Status: {status}, "
                f"Agents: {len(self.agents)}, "
                f"Turn: {self.get_current_turn_agent()}")


# Example usage for chess game coordination
if __name__ == "__main__":
    print("🎮 AgentBeats Green Agent - Chess Game Coordination Example")
    print("="*60)
    
    # Create the Green Agent coordinator
    coordinator = GreenAgent("ChessCoordinator")
    
    # Register the chess agents
    coordinator.register_agent("gpt4o_player", "chess_agent", ["chess_playing", "strategic_thinking"])
    coordinator.register_agent("gpt5_player", "chess_agent", ["chess_playing", "advanced_reasoning"])
    
    # Initialize chess game state
    coordinator.update_shared_state("board", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    coordinator.update_shared_state("game_status", "active")
    coordinator.update_shared_state("move_count", 0)
    
    # Start coordination session
    coordinator.start_coordination_session()
    
    print(f"Coordinator Status: {coordinator}")
    print(f"Current Turn: {coordinator.get_current_turn_agent()}")
    
    # Simulate a few moves
    for move_num in range(3):
        current_player = coordinator.get_current_turn_agent()
        print(f"\nMove {move_num + 1}: {current_player}'s turn")
        
        # Request move from current player
        coordinator.request_agent_action(
            current_player, 
            "make_move", 
            {"board_state": coordinator.get_shared_state("board")}
        )
        
        # Simulate agent response (in real scenario, this would come from the actual agent)
        simulated_move = f"e{2 if move_num % 2 == 0 else '7'}-e{4 if move_num % 2 == 0 else '5'}"
        coordinator.agent_response_received(current_player, {"move": simulated_move})
        
        # Update game state
        coordinator.update_shared_state("move_count", move_num + 1)
        coordinator.update_shared_state("last_move", simulated_move)
        
        print(f"  Move played: {simulated_move}")
        
        # Advance turn
        next_player = coordinator.advance_turn()
        print(f"  Next player: {next_player}")
    
    # Show final coordination status
    print(f"\n📊 Final Status:")
    status = coordinator.get_coordination_status()
    print(f"Session Active: {status['session_active']}")
    print(f"Total Moves: {coordinator.get_shared_state('move_count')}")
    print(f"Agents: {list(status['agents'].keys())}")
    
    # End session and save log
    summary = coordinator.end_coordination_session()
    log_file = coordinator.save_session_log()
    
    print(f"\n✅ Session completed!")
    print(f"📄 Session log saved to: {log_file}")
    print(f"Total events: {summary['total_events']}")
    print(f"Session duration: {summary['session_duration']:.2f} seconds")