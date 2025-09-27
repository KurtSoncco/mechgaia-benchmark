#!/usr/bin/env python3
"""
Test Suite for AgentBeats Green Agent

This module contains tests to validate the functionality of the AgentBeats-compliant
Green Agent coordination system.
"""

import unittest
import time
import json
import os
import tempfile
from green_agent import GreenAgent, AgentStatus, Message, AgentInfo


class TestGreenAgent(unittest.TestCase):
    """Test cases for the Green Agent coordination system."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.coordinator = GreenAgent("TestCoordinator")
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up any generated files
        test_files = ["coordination_session_*.json"]
        for file_pattern in test_files:
            import glob
            for file in glob.glob(file_pattern):
                if os.path.exists(file):
                    os.remove(file)
    
    def test_coordinator_initialization(self):
        """Test Green Agent coordinator initialization."""
        self.assertEqual(self.coordinator.name, "TestCoordinator")
        self.assertEqual(len(self.coordinator.agents), 0)
        self.assertEqual(len(self.coordinator.shared_state), 0)
        self.assertFalse(self.coordinator.session_active)
        self.assertEqual(len(self.coordinator.turn_order), 0)
    
    def test_agent_registration(self):
        """Test registering agents with the coordinator."""
        # Register first agent
        success = self.coordinator.register_agent("agent1", "test_agent", ["capability1"])
        self.assertTrue(success)
        self.assertIn("agent1", self.coordinator.agents)
        self.assertEqual(self.coordinator.agents["agent1"].agent_type, "test_agent")
        self.assertEqual(self.coordinator.agents["agent1"].capabilities, ["capability1"])
        
        # Register second agent
        success = self.coordinator.register_agent("agent2", "chess_agent", ["chess_playing"])
        self.assertTrue(success)
        self.assertEqual(len(self.coordinator.agents), 2)
        
        # Try to register duplicate agent
        success = self.coordinator.register_agent("agent1", "duplicate", [])
        self.assertFalse(success)
        self.assertEqual(len(self.coordinator.agents), 2)
    
    def test_agent_unregistration(self):
        """Test unregistering agents from the coordinator."""
        # Register and then unregister agent
        self.coordinator.register_agent("agent1", "test_agent")
        self.coordinator.register_agent("agent2", "test_agent")
        
        success = self.coordinator.unregister_agent("agent1")
        self.assertTrue(success)
        self.assertNotIn("agent1", self.coordinator.agents)
        self.assertEqual(len(self.coordinator.agents), 1)
        
        # Try to unregister non-existent agent
        success = self.coordinator.unregister_agent("nonexistent")
        self.assertFalse(success)
    
    def test_shared_state_management(self):
        """Test shared state update and retrieval."""
        # Update shared state
        success = self.coordinator.update_shared_state("key1", "value1")
        self.assertTrue(success)
        
        # Get specific key
        value = self.coordinator.get_shared_state("key1")
        self.assertEqual(value, "value1")
        
        # Get all state
        all_state = self.coordinator.get_shared_state()
        self.assertIn("key1", all_state)
        self.assertEqual(all_state["key1"], "value1")
        
        # Update existing key
        self.coordinator.update_shared_state("key1", "updated_value")
        value = self.coordinator.get_shared_state("key1")
        self.assertEqual(value, "updated_value")
    
    def test_message_passing(self):
        """Test agent-to-agent message passing."""
        # Register agents
        self.coordinator.register_agent("agent1", "test_agent")
        self.coordinator.register_agent("agent2", "test_agent")
        
        # Send message
        success = self.coordinator.send_message("agent1", "agent2", "test_msg", {"data": "test"})
        self.assertTrue(success)
        
        # Retrieve messages for agent2
        messages = self.coordinator.get_messages_for_agent("agent2")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].sender_id, "agent1")
        self.assertEqual(messages[0].recipient_id, "agent2")
        self.assertEqual(messages[0].message_type, "test_msg")
        self.assertEqual(messages[0].content["data"], "test")
        
        # No messages for agent1
        messages = self.coordinator.get_messages_for_agent("agent1")
        self.assertEqual(len(messages), 0)
    
    def test_session_management(self):
        """Test coordination session start/end."""
        # Register agents
        self.coordinator.register_agent("agent1", "test_agent")
        self.coordinator.register_agent("agent2", "test_agent")
        
        # Start session
        success = self.coordinator.start_coordination_session()
        self.assertTrue(success)
        self.assertTrue(self.coordinator.session_active)
        
        # Can't start another session while one is active
        success = self.coordinator.start_coordination_session()
        self.assertFalse(success)
        
        # End session
        summary = self.coordinator.end_coordination_session()
        self.assertFalse(self.coordinator.session_active)
        self.assertIn("session_duration", summary)
        self.assertIn("total_events", summary)
        self.assertIn("participating_agents", summary)
    
    def test_turn_management(self):
        """Test turn-based coordination."""
        # Register agents
        self.coordinator.register_agent("agent1", "test_agent")
        self.coordinator.register_agent("agent2", "test_agent")
        
        # Start session
        self.coordinator.start_coordination_session()
        
        # Check initial turn
        current_agent = self.coordinator.get_current_turn_agent()
        self.assertEqual(current_agent, "agent1")
        
        # Advance turn
        next_agent = self.coordinator.advance_turn()
        self.assertEqual(next_agent, "agent2")
        
        # Advance turn again (should cycle back)
        next_agent = self.coordinator.advance_turn()
        self.assertEqual(next_agent, "agent1")
    
    def test_agent_action_request(self):
        """Test requesting actions from agents."""
        # Register agent
        self.coordinator.register_agent("agent1", "test_agent")
        
        # Request action
        success = self.coordinator.request_agent_action("agent1", "test_action", {"param": "value"})
        self.assertTrue(success)
        
        # Check agent status changed
        self.assertEqual(self.coordinator.agents["agent1"].status, AgentStatus.THINKING)
        
        # Receive response
        success = self.coordinator.agent_response_received("agent1", {"result": "success"})
        self.assertTrue(success)
        
        # Check agent status changed
        self.assertEqual(self.coordinator.agents["agent1"].status, AgentStatus.DONE)
    
    def test_coordination_status(self):
        """Test getting coordination status."""
        # Register agents and start session
        self.coordinator.register_agent("agent1", "chess_agent", ["chess_playing"])
        self.coordinator.register_agent("agent2", "chess_agent", ["chess_playing"])
        self.coordinator.start_coordination_session()
        
        status = self.coordinator.get_coordination_status()
        
        # Check status structure
        self.assertIn("coordinator_name", status)
        self.assertIn("session_active", status)
        self.assertIn("current_turn", status)
        self.assertIn("agents", status)
        self.assertIn("shared_state_keys", status)
        
        # Check status values
        self.assertEqual(status["coordinator_name"], "TestCoordinator")
        self.assertTrue(status["session_active"])
        self.assertEqual(len(status["agents"]), 2)
    
    def test_session_log_saving(self):
        """Test saving session logs to file."""
        # Register agents and do some activities
        self.coordinator.register_agent("agent1", "test_agent")
        self.coordinator.update_shared_state("test_key", "test_value")
        self.coordinator.start_coordination_session()
        self.coordinator.advance_turn()
        
        # Save session log
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            saved_file = self.coordinator.save_session_log(temp_filename)
            self.assertEqual(saved_file, temp_filename)
            
            # Check if file was created and contains valid JSON
            self.assertTrue(os.path.exists(temp_filename))
            
            with open(temp_filename, 'r') as f:
                data = json.load(f)
                self.assertIn("coordinator", data)
                self.assertIn("session_log", data)
                self.assertIn("final_state", data)
                self.assertIn("agent_summary", data)
                self.assertEqual(data["coordinator"], "TestCoordinator")
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    
    def test_chess_game_simulation(self):
        """Test a complete chess game coordination scenario."""
        # Register chess agents
        self.coordinator.register_agent("gpt4o_player", "chess_agent", ["chess_playing"])
        self.coordinator.register_agent("gpt5_player", "chess_agent", ["chess_playing"])
        
        # Initialize chess game state
        self.coordinator.update_shared_state("board", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.coordinator.update_shared_state("game_status", "active")
        self.coordinator.update_shared_state("move_count", 0)
        
        # Start coordination
        success = self.coordinator.start_coordination_session()
        self.assertTrue(success)
        
        # Simulate several moves
        for move_num in range(3):
            current_player = self.coordinator.get_current_turn_agent()
            self.assertIn(current_player, ["gpt4o_player", "gpt5_player"])
            
            # Request move
            success = self.coordinator.request_agent_action(
                current_player, 
                "make_move", 
                {"board_state": self.coordinator.get_shared_state("board")}
            )
            self.assertTrue(success)
            
            # Simulate response
            success = self.coordinator.agent_response_received(
                current_player, 
                {"move": f"move_{move_num + 1}"}
            )
            self.assertTrue(success)
            
            # Update state
            self.coordinator.update_shared_state("move_count", move_num + 1)
            
            # Advance turn
            next_player = self.coordinator.advance_turn()
            
        # Verify final state
        self.assertEqual(self.coordinator.get_shared_state("move_count"), 3)
        
        # End session
        summary = self.coordinator.end_coordination_session()
        self.assertGreater(summary["total_events"], 5)  # Should have multiple events
    
    def test_str_representation(self):
        """Test string representation of the coordinator."""
        coordinator_str = str(self.coordinator)
        self.assertIn("TestCoordinator", coordinator_str)
        self.assertIn("Status:", coordinator_str)
        self.assertIn("Agents:", coordinator_str)


class TestDataClasses(unittest.TestCase):
    """Test cases for data classes used by Green Agent."""
    
    def test_message_dataclass(self):
        """Test Message dataclass."""
        message = Message(
            sender_id="agent1",
            recipient_id="agent2",
            message_type="test",
            content={"data": "test"}
        )
        
        self.assertEqual(message.sender_id, "agent1")
        self.assertEqual(message.recipient_id, "agent2")
        self.assertEqual(message.message_type, "test")
        self.assertEqual(message.content["data"], "test")
        self.assertIsNotNone(message.timestamp)
    
    def test_agent_info_dataclass(self):
        """Test AgentInfo dataclass."""
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="chess_agent",
            status=AgentStatus.WAITING,
            capabilities=["chess_playing"],
            last_activity=None
        )
        
        self.assertEqual(agent_info.agent_id, "test_agent")
        self.assertEqual(agent_info.agent_type, "chess_agent")
        self.assertEqual(agent_info.status, AgentStatus.WAITING)
        self.assertEqual(agent_info.capabilities, ["chess_playing"])
        self.assertIsNotNone(agent_info.last_activity)


if __name__ == "__main__":
    print("Running AgentBeats Green Agent Test Suite...")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGreenAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestDataClasses))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    print(f"Tests run: {result.testsRun}")
    print("="*60)