#!/usr/bin/env python3
"""
AgentBeats Green Agent - Example Usage and Demonstrations

This script demonstrates different coordination scenarios using the AgentBeats
Green Agent coordination system.
"""

from green_agent import GreenAgent, AgentStatus
import time
import json


def demo_chess_coordination():
    """Demonstrate chess game coordination scenario."""
    print("♟️  Chess Game Coordination Demo")
    print("="*40)
    
    # Create coordinator
    coordinator = GreenAgent("ChessGameCoordinator")
    
    # Register chess-playing agents
    coordinator.register_agent("gpt4o_white", "chess_agent", ["chess_playing", "opening_theory"])
    coordinator.register_agent("gpt5_black", "chess_agent", ["chess_playing", "endgame_mastery"])
    
    # Initialize chess game state
    initial_board = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    coordinator.update_shared_state("board_fen", initial_board)
    coordinator.update_shared_state("game_status", "active")
    coordinator.update_shared_state("move_count", 0)
    coordinator.update_shared_state("time_control", {"white": 600, "black": 600})
    
    print(f"Coordinator: {coordinator}")
    
    # Start coordination session
    coordinator.start_coordination_session()
    print("✅ Chess game session started")
    
    # Simulate several moves
    moves = ["e2-e4", "e7-e5", "Ng1-f3", "Nb8-c6", "Bf1-c4", "Bf8-c5"]
    
    for i, move in enumerate(moves):
        current_player = coordinator.get_current_turn_agent()
        move_number = (i // 2) + 1
        color = "White" if i % 2 == 0 else "Black"
        
        print(f"\n🎯 Move {move_number} ({color}): {current_player}")
        
        # Request move from current player
        coordinator.request_agent_action(
            current_player,
            "make_chess_move",
            {
                "board_state": coordinator.get_shared_state("board_fen"),
                "legal_moves": ["e2-e4", "d2-d4", "Ng1-f3"],  # Simplified
                "time_remaining": coordinator.get_shared_state("time_control")[color.lower()]
            }
        )
        
        # Simulate agent thinking time
        time.sleep(0.1)
        
        # Agent responds with move
        coordinator.agent_response_received(current_player, {
            "move": move,
            "evaluation": 0.15 if i % 2 == 0 else -0.12,
            "thinking_time": 2.5
        })
        
        # Update game state
        coordinator.update_shared_state("last_move", move)
        coordinator.update_shared_state("move_count", i + 1)
        
        print(f"   Move played: {move}")
        
        # Judge validates move (coordinator acting as judge)
        coordinator.update_shared_state("move_valid", True)
        
        # Advance to next player
        next_player = coordinator.advance_turn()
        print(f"   Next turn: {next_player}")
    
    # End game coordination
    summary = coordinator.end_coordination_session()
    log_file = coordinator.save_session_log("chess_game_log.json")
    
    print(f"\n✅ Chess game completed!")
    print(f"📊 Total moves: {coordinator.get_shared_state('move_count')}")
    print(f"📄 Game log: {log_file}")
    print(f"⏱️  Session duration: {summary['session_duration']:.2f}s")


def demo_debate_coordination():
    """Demonstrate debate coordination scenario."""
    print("\n💬 Debate Coordination Demo")
    print("="*40)
    
    # Create coordinator for debate
    coordinator = GreenAgent("DebateCoordinator")
    
    # Register debate participants
    coordinator.register_agent("pro_argument_bot", "debate_agent", ["argumentation", "research"])
    coordinator.register_agent("con_argument_bot", "debate_agent", ["counter_arguments", "logic"])
    coordinator.register_agent("moderator_bot", "moderator_agent", ["moderation", "fact_checking"])
    
    # Initialize debate state
    coordinator.update_shared_state("topic", "AI should be regulated by government")
    coordinator.update_shared_state("round", 0)
    coordinator.update_shared_state("time_per_round", 120)  # seconds
    coordinator.update_shared_state("debate_status", "active")
    
    print(f"Topic: {coordinator.get_shared_state('topic')}")
    print(f"Participants: {list(coordinator.agents.keys())}")
    
    # Start debate session
    coordinator.start_coordination_session()
    
    # Simulate debate rounds
    debate_rounds = [
        ("pro_argument_bot", "Opening argument for regulation"),
        ("con_argument_bot", "Opening argument against regulation"),
        ("pro_argument_bot", "Counter-argument addressing freedom concerns"),
        ("con_argument_bot", "Response about innovation stifling"),
        ("moderator_bot", "Fact-check and closing summary")
    ]
    
    for round_num, (speaker, argument_type) in enumerate(debate_rounds, 1):
        coordinator.update_shared_state("round", round_num)
        
        print(f"\n🎤 Round {round_num}: {speaker}")
        print(f"   Type: {argument_type}")
        
        # Request argument from speaker
        coordinator.request_agent_action(
            speaker,
            "present_argument",
            {
                "round_type": argument_type,
                "topic": coordinator.get_shared_state("topic"),
                "time_limit": coordinator.get_shared_state("time_per_round"),
                "previous_arguments": f"round_{round_num - 1}_summary"
            }
        )
        
        # Simulate response
        simulated_response = {
            "argument": f"Detailed argument for {argument_type}",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "sources": ["Source A", "Source B"],
            "time_used": 95
        }
        
        coordinator.agent_response_received(speaker, simulated_response)
        print(f"   ✅ Argument presented")
        
        # Moderator can fact-check
        if speaker != "moderator_bot":
            coordinator.send_message(
                "moderator_bot",
                speaker,
                "fact_check_request",
                {"argument_id": f"round_{round_num}"}
            )
    
    # End debate
    coordinator.update_shared_state("debate_status", "completed")
    summary = coordinator.end_coordination_session()
    
    print(f"\n✅ Debate completed!")
    print(f"📊 Total rounds: {coordinator.get_shared_state('round')}")
    print(f"⏱️  Session duration: {summary['session_duration']:.2f}s")


def demo_collaborative_task():
    """Demonstrate collaborative task coordination."""
    print("\n🤝 Collaborative Task Demo")
    print("="*40)
    
    # Create coordinator for collaborative coding
    coordinator = GreenAgent("CollaborativeTaskCoordinator")
    
    # Register different specialist agents
    coordinator.register_agent("architect_agent", "software_agent", ["system_design", "architecture"])
    coordinator.register_agent("frontend_agent", "software_agent", ["ui_ux", "javascript", "react"])
    coordinator.register_agent("backend_agent", "software_agent", ["api_design", "database", "python"])
    coordinator.register_agent("qa_agent", "software_agent", ["testing", "quality_assurance"])
    
    # Initialize project state
    coordinator.update_shared_state("project_name", "E-commerce Web App")
    coordinator.update_shared_state("phase", "planning")
    coordinator.update_shared_state("requirements", ["User authentication", "Product catalog", "Shopping cart", "Payment processing"])
    coordinator.update_shared_state("deliverables", {})
    
    print(f"Project: {coordinator.get_shared_state('project_name')}")
    print(f"Team: {list(coordinator.agents.keys())}")
    
    # Start collaborative session
    coordinator.start_coordination_session()
    
    # Define work phases
    work_phases = [
        ("architect_agent", "system_design", "Design overall system architecture"),
        ("frontend_agent", "ui_mockups", "Create user interface mockups"),
        ("backend_agent", "api_specification", "Define API endpoints and data models"),
        ("qa_agent", "test_planning", "Create comprehensive test plan"),
        ("architect_agent", "integration_review", "Review integration points")
    ]
    
    deliverables = {}
    
    for phase_num, (agent_id, task_type, description) in enumerate(work_phases, 1):
        coordinator.update_shared_state("current_phase", phase_num)
        
        print(f"\n📋 Phase {phase_num}: {description}")
        print(f"   Assigned to: {agent_id}")
        
        # Request work from agent
        coordinator.request_agent_action(
            agent_id,
            task_type,
            {
                "requirements": coordinator.get_shared_state("requirements"),
                "previous_deliverables": deliverables,
                "project_context": coordinator.get_shared_state("project_name")
            }
        )
        
        # Simulate work completion
        simulated_deliverable = {
            "phase": phase_num,
            "task_type": task_type,
            "deliverable": f"Completed {description.lower()}",
            "artifacts": [f"{task_type}_document.pdf", f"{task_type}_diagram.png"],
            "completion_time": "2 hours"
        }
        
        coordinator.agent_response_received(agent_id, simulated_deliverable)
        deliverables[task_type] = simulated_deliverable
        
        # Update shared deliverables
        coordinator.update_shared_state("deliverables", deliverables)
        
        print(f"   ✅ Task completed: {simulated_deliverable['deliverable']}")
        
        # Notify other agents about completion
        for other_agent in coordinator.agents:
            if other_agent != agent_id:
                coordinator.send_message(
                    coordinator.name,
                    other_agent,
                    "deliverable_ready",
                    {
                        "phase": phase_num,
                        "completed_by": agent_id,
                        "deliverable_type": task_type
                    }
                )
    
    # Project completion
    coordinator.update_shared_state("phase", "completed")
    summary = coordinator.end_coordination_session()
    
    print(f"\n✅ Collaborative project completed!")
    print(f"📦 Total deliverables: {len(deliverables)}")
    print(f"⏱️  Session duration: {summary['session_duration']:.2f}s")


def demo_coordination_status():
    """Demonstrate coordination status monitoring."""
    print("\n📊 Coordination Status Monitoring Demo")
    print("="*50)
    
    # Create coordinator
    coordinator = GreenAgent("StatusMonitorCoordinator")
    
    # Register various agents
    agents_config = [
        ("agent_1", "worker_agent", ["task_execution"]),
        ("agent_2", "analyzer_agent", ["data_analysis"]),
        ("agent_3", "reporter_agent", ["report_generation"])
    ]
    
    for agent_id, agent_type, capabilities in agents_config:
        coordinator.register_agent(agent_id, agent_type, capabilities)
    
    # Set up some shared state
    coordinator.update_shared_state("task_queue", ["task_1", "task_2", "task_3"])
    coordinator.update_shared_state("completed_tasks", [])
    
    # Start session
    coordinator.start_coordination_session()
    
    # Show initial status
    status = coordinator.get_coordination_status()
    print("📈 Initial Coordination Status:")
    print(json.dumps(status, indent=2, default=str))
    
    # Simulate some activity
    current_agent = coordinator.get_current_turn_agent()
    coordinator.request_agent_action(current_agent, "process_task", {"task": "task_1"})
    coordinator.agent_response_received(current_agent, {"result": "task_1_completed"})
    
    # Show updated status
    print("\n📈 Status After Activity:")
    updated_status = coordinator.get_coordination_status()
    print(json.dumps(updated_status, indent=2, default=str))
    
    # End session
    coordinator.end_coordination_session()


def main():
    """Main demonstration function."""
    print("🎮 AgentBeats Green Agent - Coordination System Demo")
    print("="*60)
    print("Demonstrating multi-agent coordination and orchestration capabilities")
    print()
    
    # Run different coordination scenarios
    try:
        demo_chess_coordination()
        demo_debate_coordination()
        demo_collaborative_task()
        demo_coordination_status()
        
        print("\n" + "="*60)
        print("🎉 All demonstrations completed successfully!")
        print()
        print("Key AgentBeats Green Agent capabilities demonstrated:")
        print("• Multi-agent registration and coordination")
        print("• Turn-based orchestration and state management")
        print("• Agent-to-agent (A2A) communication")
        print("• Shared state synchronization")
        print("• Session logging and monitoring")
        print("• Flexible coordination patterns (chess, debate, collaboration)")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()