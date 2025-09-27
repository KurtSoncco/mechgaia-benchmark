#!/usr/bin/env python3
"""
Setup and Quick Start Script for Green Agent

This script helps you get started with the Green Agent quickly.
"""

import sys
import os

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if optional dependencies are available."""
    optional_deps = ['requests', 'pandas', 'numpy']
    available = []
    missing = []
    
    for dep in optional_deps:
        try:
            __import__(dep)
            available.append(dep)
        except ImportError:
            missing.append(dep)
    
    if available:
        print(f"✅ Available dependencies: {', '.join(available)}")
    if missing:
        print(f"ℹ️  Optional dependencies not found: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
    
    return len(available) > 0

def run_demo():
    """Run a quick demonstration of the Green Agent."""
    print("\n🌱 Running Green Agent Demo...")
    print("="*50)
    
    try:
        from green_agent import GreenAgent
        
        # Create and configure agent
        agent = GreenAgent("QuickDemo")
        
        # Add some sample data
        agent.add_energy_usage("laptop", 1.5, "mixed")
        agent.add_energy_usage("home_solar", 5.0, "renewable")
        agent.add_carbon_footprint("commute", 8.5, "transport")
        
        # Show results
        print(f"Agent Status: {agent}")
        print(f"\nCarbon Footprint: {agent.calculate_total_carbon_footprint():.2f} kg CO2")
        print(f"Energy Efficiency: {agent.calculate_energy_efficiency_score():.1f}%")
        
        # Show recommendations
        print("\nTop Recommendations:")
        recommendations = agent.generate_recommendations()
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec.title} ({rec.impact} impact)")
        
        print("\n✅ Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🔧 Green Agent Setup & Quick Start")
    print("="*40)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    check_dependencies()
    
    # Run demo
    if run_demo():
        print("\n" + "="*40)
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("• Run: python3 example_usage.py")
        print("• Run tests: python3 test_green_agent.py")
        print("• Check README.md for detailed documentation")
    else:
        print("\n❌ Setup encountered issues. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()