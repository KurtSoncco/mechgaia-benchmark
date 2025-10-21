#!/usr/bin/env python3
"""
Setup script for Simple Green Agent Demo
Uses the actual A2A protocol from the /agents/ folder.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required Python packages using uv."""
    print("📦 Installing Python dependencies using uv...")
    try:
        # Try uv first
        subprocess.check_call(["uv", "sync"])
        print("✅ Dependencies installed successfully with uv!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to pip if uv is not available
        print("⚠️  uv not found, falling back to pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully with pip!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            return False

def test_agents():
    """Test that the actual agents work correctly."""
    print("🧪 Testing A2A protocol agents...")
    
    try:
        # Test Level 1 Stress Task
        from agents.level1_stress_task import Level1StressTask
        agent1 = Level1StressTask("test_level1")
        print("   ✅ Level 1 Stress Task working")
        
        # Test Level 2 Shaft Design Task
        from agents.level2_shaft_design_task import Level2ShaftDesignTask
        agent2 = Level2ShaftDesignTask("test_level2")
        print("   ✅ Level 2 Shaft Design Task working")
        
        # Test Level 3 Plate Optimization Task
        from agents.level3_plate_optimization_task import Level3PlateOptimizationTask
        agent3 = Level3PlateOptimizationTask("test_level3")
        print("   ✅ Level 3 Plate Optimization Task working")
        
        # Test Demo White Agent
        from demo_white_agent import DemoWhiteAgent
        demo_agent = DemoWhiteAgent()
        submissions = demo_agent.generate_all_submissions()
        assert len(submissions) > 0
        print("   ✅ Demo White Agent working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent test failed: {e}")
        return False

def run_quick_demo():
    """Run a quick demo to verify everything works."""
    print("🚀 Running quick A2A protocol demo...")
    
    try:
        from agents.level1_stress_task import Level1StressTask
        from demo_white_agent import DemoWhiteAgent
        
        # Create demo submissions
        demo_agent = DemoWhiteAgent()
        submissions = demo_agent.generate_all_submissions()
        
        # Create submission files
        os.makedirs("demo_submissions", exist_ok=True)
        for name, submission in submissions.items():
            filename = f"demo_submissions/{name}.json"
            with open(filename, 'w') as f:
                import json
                json.dump(submission, f, indent=2)
        
        # Test Level 1 evaluation
        level1_agent = Level1StressTask("demo_test")
        
        # Test correct submission
        correct_result = level1_agent.run_evaluation("demo_submissions/level1_correct.json")
        print(f"   📊 Correct submission score: {correct_result.get('final_score', 0):.2f}")
        
        # Test incorrect submission
        incorrect_result = level1_agent.run_evaluation("demo_submissions/level1_incorrect.json")
        print(f"   📊 Incorrect submission score: {incorrect_result.get('final_score', 0):.2f}")
        
        print("   ✅ Quick A2A protocol demo completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Quick demo failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🤖 MechGAIA Benchmark - A2A Protocol Demo Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Test agents
    if not test_agents():
        print("❌ Agent tests failed. Please check the error messages above.")
        sys.exit(1)
    
    # Run quick demo
    if not run_quick_demo():
        print("❌ Quick demo failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run the MechGAIA A2A demo: python simple_demo_server.py")
    print("   2. Open your browser to: http://localhost:5001")
    print("   3. The demo uses the actual MechGAIA benchmark agents from /agents/ folder")
    print("   4. For full benchmark participation, see PARTICIPANT_REQUIREMENTS.md")
    print("\n🎬 Ready for MechGAIA A2A protocol demo recording!")

if __name__ == "__main__":
    main()
