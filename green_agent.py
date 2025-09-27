"""
Green Agent - An AI agent focused on environmental sustainability and eco-friendly practices.

This agent helps organizations and individuals make environmentally conscious decisions
by providing insights on energy efficiency, carbon footprint, and sustainable practices.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


@dataclass
class EnergyUsage:
    """Represents energy usage data."""
    timestamp: datetime
    device_id: str
    power_consumption: float  # in kWh
    source: str  # renewable, fossil, mixed


@dataclass
class CarbonFootprint:
    """Represents carbon footprint data."""
    activity: str
    co2_emissions: float  # in kg CO2
    timestamp: datetime
    category: str  # transport, energy, waste, etc.


@dataclass
class GreenRecommendation:
    """Represents an environmental recommendation."""
    title: str
    description: str
    impact: str  # low, medium, high
    category: str
    estimated_savings: Optional[float] = None  # in kg CO2 or kWh


class GreenAgent:
    """
    A Green Agent that provides environmental insights and recommendations.
    
    This agent focuses on:
    - Energy efficiency monitoring and optimization
    - Carbon footprint calculation and reduction strategies
    - Sustainable resource management
    - Environmental impact assessment
    - Green recommendations and best practices
    """
    
    def __init__(self, name: str = "EcoGuardian"):
        """Initialize the Green Agent."""
        self.name = name
        self.energy_data: List[EnergyUsage] = []
        self.carbon_data: List[CarbonFootprint] = []
        self.recommendations: List[GreenRecommendation] = []
        
        # Carbon intensity factors (kg CO2 per kWh)
        self.carbon_intensity = {
            "renewable": 0.0,
            "fossil": 0.82,  # Average for fossil fuels
            "mixed": 0.41    # Average grid mix
        }
    
    def add_energy_usage(self, device_id: str, power_consumption: float, 
                        source: str = "mixed") -> None:
        """Add energy usage data to the agent."""
        usage = EnergyUsage(
            timestamp=datetime.now(),
            device_id=device_id,
            power_consumption=power_consumption,
            source=source
        )
        self.energy_data.append(usage)
        
        # Calculate and add corresponding carbon footprint
        co2_emissions = power_consumption * self.carbon_intensity.get(source, 0.41)
        carbon_data = CarbonFootprint(
            activity=f"Energy consumption - {device_id}",
            co2_emissions=co2_emissions,
            timestamp=datetime.now(),
            category="energy"
        )
        self.carbon_data.append(carbon_data)
    
    def add_carbon_footprint(self, activity: str, co2_emissions: float, 
                           category: str) -> None:
        """Add carbon footprint data to the agent."""
        footprint = CarbonFootprint(
            activity=activity,
            co2_emissions=co2_emissions,
            timestamp=datetime.now(),
            category=category
        )
        self.carbon_data.append(footprint)
    
    def calculate_total_carbon_footprint(self) -> float:
        """Calculate total carbon footprint."""
        return sum(data.co2_emissions for data in self.carbon_data)
    
    def calculate_energy_efficiency_score(self) -> float:
        """Calculate energy efficiency score (0-100)."""
        if not self.energy_data:
            return 0.0
        
        renewable_usage = sum(
            usage.power_consumption for usage in self.energy_data 
            if usage.source == "renewable"
        )
        total_usage = sum(usage.power_consumption for usage in self.energy_data)
        
        if total_usage == 0:
            return 0.0
        
        return (renewable_usage / total_usage) * 100
    
    def generate_recommendations(self) -> List[GreenRecommendation]:
        """Generate environmental recommendations based on current data."""
        recommendations = []
        
        # Energy efficiency recommendations
        efficiency_score = self.calculate_energy_efficiency_score()
        if efficiency_score < 50:
            recommendations.append(GreenRecommendation(
                title="Switch to Renewable Energy",
                description="Consider switching to renewable energy sources like solar or wind power to reduce your carbon footprint.",
                impact="high",
                category="energy",
                estimated_savings=self.calculate_total_carbon_footprint() * 0.6
            ))
        
        # High energy consumption warning
        if self.energy_data:
            avg_consumption = sum(usage.power_consumption for usage in self.energy_data) / len(self.energy_data)
            if avg_consumption > 10:  # Above 10 kWh average
                recommendations.append(GreenRecommendation(
                    title="Reduce Energy Consumption",
                    description="Your average energy consumption is high. Consider using energy-efficient appliances and turning off devices when not in use.",
                    impact="medium",
                    category="energy",
                    estimated_savings=avg_consumption * 0.2 * self.carbon_intensity["mixed"]
                ))
        
        # General sustainability recommendations
        recommendations.extend([
            GreenRecommendation(
                title="Use Public Transportation",
                description="Replace car trips with public transportation, cycling, or walking to reduce transportation emissions.",
                impact="medium",
                category="transport"
            ),
            GreenRecommendation(
                title="Implement Recycling Program",
                description="Set up comprehensive recycling for paper, plastic, glass, and electronic waste.",
                impact="medium",
                category="waste"
            ),
            GreenRecommendation(
                title="Optimize Heating and Cooling",
                description="Use programmable thermostats and improve insulation to reduce heating and cooling energy consumption.",
                impact="high",
                category="energy"
            )
        ])
        
        self.recommendations = recommendations
        return recommendations
    
    def get_environmental_report(self) -> Dict:
        """Generate a comprehensive environmental report."""
        total_carbon = self.calculate_total_carbon_footprint()
        efficiency_score = self.calculate_energy_efficiency_score()
        total_energy = sum(usage.power_consumption for usage in self.energy_data)
        
        # Categorize carbon emissions
        carbon_by_category = {}
        for data in self.carbon_data:
            if data.category not in carbon_by_category:
                carbon_by_category[data.category] = 0
            carbon_by_category[data.category] += data.co2_emissions
        
        return {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_carbon_footprint_kg": round(total_carbon, 2),
                "total_energy_consumption_kwh": round(total_energy, 2),
                "energy_efficiency_score": round(efficiency_score, 2),
                "number_of_recommendations": len(self.generate_recommendations())
            },
            "carbon_by_category": carbon_by_category,
            "energy_sources": self._analyze_energy_sources(),
            "recommendations": [
                {
                    "title": rec.title,
                    "description": rec.description,
                    "impact": rec.impact,
                    "category": rec.category,
                    "estimated_savings": rec.estimated_savings
                }
                for rec in self.generate_recommendations()
            ]
        }
    
    def _analyze_energy_sources(self) -> Dict[str, float]:
        """Analyze energy consumption by source."""
        sources = {}
        for usage in self.energy_data:
            if usage.source not in sources:
                sources[usage.source] = 0
            sources[usage.source] += usage.power_consumption
        return sources
    
    def save_report(self, filename: str = "green_report.json") -> None:
        """Save the environmental report to a JSON file."""
        report = self.get_environmental_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Environmental report saved to {filename}")
    
    def __str__(self) -> str:
        """String representation of the Green Agent."""
        return (f"Green Agent '{self.name}' - "
                f"Carbon Footprint: {self.calculate_total_carbon_footprint():.2f} kg CO2, "
                f"Energy Efficiency: {self.calculate_energy_efficiency_score():.1f}%")


if __name__ == "__main__":
    # Example usage
    agent = GreenAgent("EcoGuardian")
    
    # Add some sample data
    agent.add_energy_usage("office_computer", 2.5, "mixed")
    agent.add_energy_usage("home_heating", 15.0, "fossil")
    agent.add_energy_usage("solar_panels", 8.0, "renewable")
    
    agent.add_carbon_footprint("Daily commute", 5.2, "transport")
    agent.add_carbon_footprint("Waste disposal", 1.1, "waste")
    
    # Generate and display report
    print(agent)
    print(f"\nTotal Carbon Footprint: {agent.calculate_total_carbon_footprint():.2f} kg CO2")
    print(f"Energy Efficiency Score: {agent.calculate_energy_efficiency_score():.1f}%")
    
    print("\n=== Environmental Recommendations ===")
    for rec in agent.generate_recommendations():
        print(f"• {rec.title} ({rec.impact} impact)")
        print(f"  {rec.description}")
        if rec.estimated_savings:
            print(f"  Estimated savings: {rec.estimated_savings:.2f} kg CO2")
        print()
    
    # Save report
    agent.save_report()