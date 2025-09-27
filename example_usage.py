#!/usr/bin/env python3
"""
Green Agent Example Usage

This script demonstrates how to use the Green Agent to monitor environmental
impact and get sustainability recommendations.
"""

from green_agent import GreenAgent
from datetime import datetime, timedelta
import random


def simulate_energy_data(agent: GreenAgent, days: int = 7) -> None:
    """Simulate energy usage data for demonstration."""
    print(f"Simulating {days} days of energy usage data...")
    
    devices = [
        ("office_computer", "mixed", 2.0, 4.0),
        ("home_heating", "fossil", 10.0, 20.0),
        ("air_conditioning", "mixed", 8.0, 15.0),
        ("solar_panels", "renewable", 5.0, 12.0),
        ("electric_vehicle", "mixed", 15.0, 25.0),
        ("kitchen_appliances", "mixed", 3.0, 8.0),
        ("lighting", "mixed", 1.0, 3.0)
    ]
    
    for day in range(days):
        for device_id, source, min_consumption, max_consumption in devices:
            # Simulate some variation in daily usage
            consumption = random.uniform(min_consumption, max_consumption)
            agent.add_energy_usage(device_id, consumption, source)


def simulate_transportation_data(agent: GreenAgent) -> None:
    """Simulate transportation carbon footprint data."""
    print("Adding transportation data...")
    
    transport_activities = [
        ("Daily car commute (gasoline)", 12.5, "transport"),
        ("Weekly flight", 200.0, "transport"),
        ("Public transportation", 2.3, "transport"),
        ("Ride-sharing service", 8.7, "transport")
    ]
    
    for activity, emissions, category in transport_activities:
        agent.add_carbon_footprint(activity, emissions, category)


def simulate_other_activities(agent: GreenAgent) -> None:
    """Simulate other environmental impact activities."""
    print("Adding other environmental activities...")
    
    other_activities = [
        ("Household waste disposal", 15.2, "waste"),
        ("Water heating", 8.9, "energy"),
        ("Food consumption", 45.3, "consumption"),
        ("Paper usage", 3.7, "waste"),
        ("Digital services", 2.1, "digital")
    ]
    
    for activity, emissions, category in other_activities:
        agent.add_carbon_footprint(activity, emissions, category)


def display_detailed_report(agent: GreenAgent) -> None:
    """Display a detailed environmental report."""
    print("\n" + "="*60)
    print(f"DETAILED ENVIRONMENTAL REPORT - {agent.name}")
    print("="*60)
    
    report = agent.get_environmental_report()
    
    # Summary
    summary = report["summary"]
    print(f"\n📊 SUMMARY:")
    print(f"   Total Carbon Footprint: {summary['total_carbon_footprint_kg']} kg CO2")
    print(f"   Total Energy Consumption: {summary['total_energy_consumption_kwh']} kWh")
    print(f"   Energy Efficiency Score: {summary['energy_efficiency_score']}%")
    
    # Efficiency rating
    score = summary['energy_efficiency_score']
    if score >= 90:
        rating = "Excellent 🟢"
    elif score >= 70:
        rating = "Good 🔵"
    elif score >= 50:
        rating = "Average 🟡"
    elif score >= 30:
        rating = "Poor 🟠"
    else:
        rating = "Very Poor 🔴"
    print(f"   Efficiency Rating: {rating}")
    
    # Carbon by category
    print(f"\n🏷️  CARBON EMISSIONS BY CATEGORY:")
    carbon_by_category = report["carbon_by_category"]
    total_carbon = sum(carbon_by_category.values())
    
    for category, emissions in sorted(carbon_by_category.items(), 
                                    key=lambda x: x[1], reverse=True):
        percentage = (emissions / total_carbon * 100) if total_carbon > 0 else 0
        print(f"   {category.capitalize()}: {emissions:.2f} kg CO2 ({percentage:.1f}%)")
    
    # Energy sources
    print(f"\n⚡ ENERGY SOURCES:")
    energy_sources = report["energy_sources"]
    total_energy = sum(energy_sources.values())
    
    for source, consumption in sorted(energy_sources.items(), 
                                    key=lambda x: x[1], reverse=True):
        percentage = (consumption / total_energy * 100) if total_energy > 0 else 0
        print(f"   {source.capitalize()}: {consumption:.2f} kWh ({percentage:.1f}%)")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS ({len(report['recommendations'])} total):")
    recommendations = report["recommendations"]
    
    # Group by impact level
    high_impact = [r for r in recommendations if r["impact"] == "high"]
    medium_impact = [r for r in recommendations if r["impact"] == "medium"]
    low_impact = [r for r in recommendations if r["impact"] == "low"]
    
    for impact_level, recs in [("HIGH IMPACT", high_impact), 
                              ("MEDIUM IMPACT", medium_impact), 
                              ("LOW IMPACT", low_impact)]:
        if recs:
            print(f"\n   {impact_level}:")
            for rec in recs:
                print(f"   • {rec['title']}")
                print(f"     {rec['description']}")
                if rec['estimated_savings']:
                    print(f"     💰 Potential savings: {rec['estimated_savings']:.2f} kg CO2")
                print()


def main():
    """Main example function."""
    print("🌱 Green Agent - Environmental Sustainability Assistant")
    print("="*60)
    
    # Create the Green Agent
    agent = GreenAgent("EcoGuardian AI")
    
    print(f"Initializing {agent.name}...")
    print(f"Agent Status: {agent}")
    
    # Simulate different types of environmental data
    simulate_energy_data(agent, days=7)
    simulate_transportation_data(agent)
    simulate_other_activities(agent)
    
    print(f"\nUpdated Agent Status: {agent}")
    
    # Display detailed report
    display_detailed_report(agent)
    
    # Save report to file
    print("\n" + "="*60)
    filename = f"environmental_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    agent.save_report(filename)
    
    print(f"\n✅ Complete environmental analysis finished!")
    print(f"📄 Report saved as: {filename}")
    
    # Show quick tips
    print(f"\n🌿 QUICK TIPS:")
    print("• Monitor your energy usage regularly")
    print("• Switch to renewable energy sources when possible")
    print("• Implement the high-impact recommendations first")
    print("• Track your progress over time")
    print("• Share insights with your team or family")


if __name__ == "__main__":
    main()