# AgentBeats Green Agent - Multi-Agent Coordination System 🤖

An **AgentBeats-compliant Green Agent** implementation for the Agentic AI class. This Green Agent acts as a coordinator/orchestrator that manages multi-agent interactions, maintains shared state, and facilitates agent-to-agent (A2A) communication.

## 🎯 What is an AgentBeats Green Agent?

In the **AgentBeats framework**, a Green Agent serves as a **coordination and orchestration system** that:

- **🎮 Acts as a Judge/Referee**: Maintains game/task state and ensures rules are followed
- **🔄 Orchestrates Turn-Taking**: Manages which agent acts when in multi-agent scenarios
- **📡 Enables A2A Communication**: Facilitates secure agent-to-agent message passing
- **🗃️ Maintains Shared State**: Keeps synchronized state across all participating agents
- **📊 Provides Monitoring**: Tracks agent status, performance, and coordination metrics

### Example Use Case: Chess Game
```
Green Agent: Chess match coordinator that maintains board state and manages turns
White Agents: GPT-4o and GPT-5 based chess-playing agents

The Green Agent:
1. Maintains the chess board state
2. Asks each agent for their move when it's their turn
3. Validates moves and updates the board
4. Handles game rules and end conditions
5. Logs the complete game session
```

## 🚀 Key Features

### 🎯 Multi-Agent Coordination
- **Agent Registration**: Dynamic registration/unregistration of participating agents
- **Turn Management**: Round-robin and custom turn-taking patterns
- **Status Tracking**: Monitor agent states (waiting, active, thinking, done, error)
- **Session Management**: Start/stop coordination sessions with comprehensive logging

### 📡 Communication Infrastructure
- **A2A Messaging**: Secure agent-to-agent message passing through the coordinator
- **Message Filtering**: Configurable communication rules and content filtering
- **Broadcast Capabilities**: Send state updates to all or specific agents
- **Message Queuing**: Reliable message delivery with queuing system

### 🗃️ Shared State Management
- **Centralized State**: Single source of truth for shared information
- **State Synchronization**: Automatic state updates across all agents
- **Conflict Resolution**: Built-in handling of state conflicts
- **State History**: Complete audit trail of state changes

### 📊 Monitoring and Logging
- **Real-time Status**: Live coordination status and agent monitoring
- **Session Logging**: Complete session logs with timestamps and events
- **Performance Metrics**: Track response times, turn durations, and system health
- **JSON Export**: Export session data for analysis and replay

## 📁 Project Structure

```
agentic-1-unit/
├── green_agent.py          # Main AgentBeats Green Agent implementation
├── example_usage.py        # Comprehensive usage examples and demos
├── test_green_agent.py     # Complete test suite
├── README.md              # This documentation
├── LICENSE                # MIT License
└── .gitignore            # Git ignore rules
```

## 🛠️ Quick Start

### Basic Coordination Setup

```python
from green_agent import GreenAgent

# Create the Green Agent coordinator
coordinator = GreenAgent("MyCoordinator")

# Register participating agents
coordinator.register_agent("agent1", "chess_player", ["chess_playing"])
coordinator.register_agent("agent2", "chess_player", ["chess_playing"])

# Initialize shared state
coordinator.update_shared_state("board", "initial_board_state")
coordinator.update_shared_state("game_status", "active")

# Start coordination session
coordinator.start_coordination_session()

print(f"Current turn: {coordinator.get_current_turn_agent()}")
```

### Agent-to-Agent Communication

```python
# Send message between agents
coordinator.send_message(
    sender_id="agent1",
    recipient_id="agent2", 
    message_type="move_announcement",
    content={"move": "e2-e4", "confidence": 0.95}
)

# Retrieve messages for an agent
messages = coordinator.get_messages_for_agent("agent2")
for msg in messages:
    print(f"From {msg.sender_id}: {msg.content}")
```

### Turn-Based Coordination

```python
# Request action from current agent
current_player = coordinator.get_current_turn_agent()
coordinator.request_agent_action(
    current_player,
    "make_move",
    {"board_state": coordinator.get_shared_state("board")}
)

# Handle agent response
coordinator.agent_response_received(current_player, {"move": "Nf3"})

# Advance to next agent
next_player = coordinator.advance_turn()
print(f"Next turn: {next_player}")
```

## 🎮 Example Scenarios

### 1. Chess Game Coordination

```python
coordinator = GreenAgent("ChessCoordinator")

# Register chess agents
coordinator.register_agent("gpt4o_white", "chess_agent", ["chess_playing"])
coordinator.register_agent("gpt5_black", "chess_agent", ["chess_playing"])

# Initialize chess game
coordinator.update_shared_state("board", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
coordinator.update_shared_state("move_count", 0)

# Start and coordinate game
coordinator.start_coordination_session()

for move_num in range(10):  # 10 moves
    current_player = coordinator.get_current_turn_agent()
    
    # Request move
    coordinator.request_agent_action(current_player, "make_move", {
        "board": coordinator.get_shared_state("board")
    })
    
    # Simulate response (in real implementation, comes from actual agent)
    coordinator.agent_response_received(current_player, {"move": "e2-e4"})
    
    # Update state and advance turn
    coordinator.update_shared_state("move_count", move_num + 1)
    coordinator.advance_turn()
```

### 2. Debate Moderation

```python
coordinator = GreenAgent("DebateModerator")

# Register debate participants
coordinator.register_agent("pro_bot", "debate_agent", ["argumentation"])
coordinator.register_agent("con_bot", "debate_agent", ["counter_arguments"])
coordinator.register_agent("moderator", "moderator_agent", ["fact_checking"])

# Coordinate debate rounds
coordinator.update_shared_state("topic", "AI Regulation")
coordinator.start_coordination_session()

# Each agent gets turns to present arguments
# Moderator can interject for fact-checking
```

### 3. Collaborative Development

```python
coordinator = GreenAgent("DevTeamCoordinator") 

# Register development team
coordinator.register_agent("architect", "dev_agent", ["system_design"])
coordinator.register_agent("frontend_dev", "dev_agent", ["ui_development"])  
coordinator.register_agent("backend_dev", "dev_agent", ["api_development"])
coordinator.register_agent("qa_engineer", "dev_agent", ["testing"])

# Coordinate development phases
# Each specialist contributes to shared project state
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_green_agent.py
```

The test suite validates:
- ✅ Agent registration/unregistration
- ✅ Shared state management
- ✅ Message passing system
- ✅ Turn-based coordination
- ✅ Session management
- ✅ Status monitoring
- ✅ Complete coordination scenarios

## 🎓 Educational Value for Agentic AI

This AgentBeats Green Agent demonstrates key **Agentic AI concepts**:

### 🤖 Multi-Agent Systems
- **Agent Coordination**: How multiple AI agents work together
- **Distributed Decision Making**: Agents collaborate while maintaining autonomy
- **Communication Protocols**: Structured agent-to-agent interaction patterns

### 🎮 Game Theory and Strategy
- **Turn-Based Systems**: Managing sequential decision making
- **State Management**: Maintaining consistent world state across agents
- **Rule Enforcement**: Acting as neutral arbiter in agent interactions

### 🏗️ System Architecture
- **Coordination Patterns**: Different approaches to multi-agent orchestration
- **Event-Driven Systems**: Reactive coordination based on agent actions
- **Scalable Design**: Framework that supports various agent types and scenarios

### 📊 Monitoring and Analysis
- **System Observability**: Real-time insights into agent behavior
- **Session Recording**: Complete audit trails for analysis and replay
- **Performance Metrics**: Understanding coordination efficiency

## 🔧 Advanced Configuration

### Custom Coordination Rules

```python
def custom_turn_logic(coordinator, current_agent):
    """Custom logic for turn advancement."""
    # Implement priority-based turns, time limits, etc.
    pass

coordinator.coordination_rules["turn_logic"] = custom_turn_logic
```

### Communication Filtering

```python
def message_filter(message):
    """Filter inappropriate or malformed messages."""
    # Implement content filtering, rate limiting, etc.
    return message.message_type in ["valid_types"]

coordinator.coordination_rules["communication_filter"] = message_filter
```

## 📊 Monitoring and Analytics

### Real-Time Status

```python
status = coordinator.get_coordination_status()
print(f"Active session: {status['session_active']}")
print(f"Current turn: {status['current_turn']}")
print(f"Agent count: {len(status['agents'])}")
```

### Session Logging

```python
# End session and get comprehensive summary
summary = coordinator.end_coordination_session()
print(f"Session duration: {summary['session_duration']}")
print(f"Total events: {summary['total_events']}")

# Save detailed logs
log_file = coordinator.save_session_log()
print(f"Session log saved to: {log_file}")
```

## 🤝 Contributing

This project is part of an educational assignment for the Agentic AI class. Contributions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎖️ Author

**Kurt Walter Soncco Sinchi**  
*Agentic AI Class Project*

---

*AgentBeats Green Agent - Enabling seamless multi-agent coordination and collaboration* 🤖✨