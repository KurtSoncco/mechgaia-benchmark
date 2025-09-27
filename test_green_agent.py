#!/usr/bin/env python3
"""
Test Suite for Green Agent

This module contains tests to validate the functionality of the Green Agent.
"""

import unittest
from datetime import datetime
import json
import os
import tempfile
from green_agent import GreenAgent, EnergyUsage, CarbonFootprint, GreenRecommendation


class TestGreenAgent(unittest.TestCase):
    """Test cases for the Green Agent class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.agent = GreenAgent("TestAgent")
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up any generated files
        test_files = ["green_report.json", "test_report.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
    
    def test_agent_initialization(self):
        """Test Green Agent initialization."""
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(len(self.agent.energy_data), 0)
        self.assertEqual(len(self.agent.carbon_data), 0)
        self.assertEqual(len(self.agent.recommendations), 0)
    
    def test_add_energy_usage(self):
        """Test adding energy usage data."""
        self.agent.add_energy_usage("test_device", 10.0, "renewable")
        
        self.assertEqual(len(self.agent.energy_data), 1)
        self.assertEqual(len(self.agent.carbon_data), 1)  # Should auto-generate carbon data
        
        energy_entry = self.agent.energy_data[0]
        self.assertEqual(energy_entry.device_id, "test_device")
        self.assertEqual(energy_entry.power_consumption, 10.0)
        self.assertEqual(energy_entry.source, "renewable")
    
    def test_add_carbon_footprint(self):
        """Test adding carbon footprint data."""
        self.agent.add_carbon_footprint("test_activity", 5.0, "transport")
        
        self.assertEqual(len(self.agent.carbon_data), 1)
        
        carbon_entry = self.agent.carbon_data[0]
        self.assertEqual(carbon_entry.activity, "test_activity")
        self.assertEqual(carbon_entry.co2_emissions, 5.0)
        self.assertEqual(carbon_entry.category, "transport")
    
    def test_calculate_total_carbon_footprint(self):
        """Test carbon footprint calculation."""
        self.agent.add_carbon_footprint("activity1", 10.0, "transport")
        self.agent.add_carbon_footprint("activity2", 5.0, "energy")
        
        total = self.agent.calculate_total_carbon_footprint()
        self.assertEqual(total, 15.0)
    
    def test_calculate_energy_efficiency_score(self):
        """Test energy efficiency score calculation."""
        # Test with no data
        score = self.agent.calculate_energy_efficiency_score()
        self.assertEqual(score, 0.0)
        
        # Test with mixed energy sources
        self.agent.add_energy_usage("device1", 20.0, "renewable")
        self.agent.add_energy_usage("device2", 30.0, "fossil")
        
        score = self.agent.calculate_energy_efficiency_score()
        self.assertEqual(score, 40.0)  # 20/(20+30) * 100 = 40%
        
        # Test with 100% renewable
        agent2 = GreenAgent("TestAgent2")
        agent2.add_energy_usage("device1", 10.0, "renewable")
        
        score = agent2.calculate_energy_efficiency_score()
        self.assertEqual(score, 100.0)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Add data that should trigger recommendations
        self.agent.add_energy_usage("high_consumption_device", 15.0, "fossil")
        
        recommendations = self.agent.generate_recommendations()
        
        # Should generate at least the basic recommendations
        self.assertGreater(len(recommendations), 0)
        
        # Check if renewable energy recommendation is generated (efficiency < 50%)
        renewable_rec = any(rec.title == "Switch to Renewable Energy" for rec in recommendations)
        self.assertTrue(renewable_rec)
        
        # Check if high consumption warning is generated
        consumption_rec = any(rec.title == "Reduce Energy Consumption" for rec in recommendations)
        self.assertTrue(consumption_rec)
    
    def test_environmental_report(self):
        """Test environmental report generation."""
        # Add some test data
        self.agent.add_energy_usage("device1", 10.0, "renewable")
        self.agent.add_carbon_footprint("transport", 5.0, "transport")
        
        report = self.agent.get_environmental_report()
        
        # Check report structure
        self.assertIn("agent_name", report)
        self.assertIn("timestamp", report)
        self.assertIn("summary", report)
        self.assertIn("carbon_by_category", report)
        self.assertIn("energy_sources", report)
        self.assertIn("recommendations", report)
        
        # Check summary data
        summary = report["summary"]
        self.assertEqual(summary["total_carbon_footprint_kg"], 5.0)
        self.assertEqual(summary["total_energy_consumption_kwh"], 10.0)
        self.assertEqual(summary["energy_efficiency_score"], 100.0)
    
    def test_save_report(self):
        """Test saving report to file."""
        self.agent.add_energy_usage("device1", 5.0, "mixed")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            self.agent.save_report(temp_filename)
            
            # Check if file was created
            self.assertTrue(os.path.exists(temp_filename))
            
            # Check if file contains valid JSON
            with open(temp_filename, 'r') as f:
                data = json.load(f)
                self.assertIn("agent_name", data)
                self.assertEqual(data["agent_name"], "TestAgent")
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    
    def test_carbon_intensity_calculation(self):
        """Test carbon intensity calculations for different energy sources."""
        # Test renewable energy (should have 0 emissions)
        self.agent.add_energy_usage("solar", 10.0, "renewable")
        carbon_renewable = [c for c in self.agent.carbon_data if "solar" in c.activity][0]
        self.assertEqual(carbon_renewable.co2_emissions, 0.0)
        
        # Test fossil energy
        agent2 = GreenAgent("TestAgent2")
        agent2.add_energy_usage("coal", 10.0, "fossil")
        carbon_fossil = [c for c in agent2.carbon_data if "coal" in c.activity][0]
        self.assertEqual(carbon_fossil.co2_emissions, 10.0 * 0.82)  # 8.2 kg CO2
        
        # Test mixed energy
        agent3 = GreenAgent("TestAgent3")
        agent3.add_energy_usage("grid", 10.0, "mixed")
        carbon_mixed = [c for c in agent3.carbon_data if "grid" in c.activity][0]
        self.assertEqual(carbon_mixed.co2_emissions, 10.0 * 0.41)  # 4.1 kg CO2
    
    def test_str_representation(self):
        """Test string representation of the agent."""
        self.agent.add_energy_usage("device1", 10.0, "fossil")
        self.agent.add_carbon_footprint("transport", 5.0, "transport")
        
        agent_str = str(self.agent)
        self.assertIn("TestAgent", agent_str)
        self.assertIn("Carbon Footprint", agent_str)
        self.assertIn("Energy Efficiency", agent_str)


class TestDataClasses(unittest.TestCase):
    """Test cases for data classes used by Green Agent."""
    
    def test_energy_usage_dataclass(self):
        """Test EnergyUsage dataclass."""
        timestamp = datetime.now()
        usage = EnergyUsage(
            timestamp=timestamp,
            device_id="test_device",
            power_consumption=15.5,
            source="renewable"
        )
        
        self.assertEqual(usage.timestamp, timestamp)
        self.assertEqual(usage.device_id, "test_device")
        self.assertEqual(usage.power_consumption, 15.5)
        self.assertEqual(usage.source, "renewable")
    
    def test_carbon_footprint_dataclass(self):
        """Test CarbonFootprint dataclass."""
        timestamp = datetime.now()
        footprint = CarbonFootprint(
            activity="test_activity",
            co2_emissions=25.7,
            timestamp=timestamp,
            category="transport"
        )
        
        self.assertEqual(footprint.activity, "test_activity")
        self.assertEqual(footprint.co2_emissions, 25.7)
        self.assertEqual(footprint.timestamp, timestamp)
        self.assertEqual(footprint.category, "transport")
    
    def test_green_recommendation_dataclass(self):
        """Test GreenRecommendation dataclass."""
        recommendation = GreenRecommendation(
            title="Test Recommendation",
            description="Test description",
            impact="high",
            category="energy",
            estimated_savings=10.5
        )
        
        self.assertEqual(recommendation.title, "Test Recommendation")
        self.assertEqual(recommendation.description, "Test description")
        self.assertEqual(recommendation.impact, "high")
        self.assertEqual(recommendation.category, "energy")
        self.assertEqual(recommendation.estimated_savings, 10.5)


if __name__ == "__main__":
    print("Running Green Agent Test Suite...")
    print("="*50)
    
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
    print("\n" + "="*50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    print(f"Tests run: {result.testsRun}")
    print("="*50)