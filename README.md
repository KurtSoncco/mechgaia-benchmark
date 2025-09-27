# Green Agent - Agentic AI for Environmental Sustainability 🌱

An intelligent environmental sustainability agent designed for the Agentic AI class. The Green Agent helps organizations and individuals make environmentally conscious decisions by providing insights on energy efficiency, carbon footprint reduction, and sustainable practices.

## 🎯 Purpose

This project implements a **Green Agent** - an AI system focused on:
- **Energy Efficiency Monitoring**: Track and optimize energy consumption patterns
- **Carbon Footprint Analysis**: Calculate and reduce CO2 emissions across different activities
- **Sustainable Resource Management**: Provide recommendations for eco-friendly practices
- **Environmental Impact Assessment**: Generate comprehensive sustainability reports
- **Green Recommendations**: Suggest actionable steps to improve environmental performance

## 🚀 Features

### Core Functionality
- **Energy Usage Tracking**: Monitor power consumption across different devices and energy sources
- **Carbon Footprint Calculation**: Automatic CO2 emissions calculation based on energy usage and activities
- **Efficiency Scoring**: Calculate energy efficiency scores (0-100%) based on renewable energy usage
- **Smart Recommendations**: Generate personalized environmental recommendations based on usage patterns
- **Comprehensive Reporting**: Create detailed environmental impact reports in JSON format

### Supported Energy Sources
- Renewable (solar, wind, hydro)
- Fossil fuels (coal, natural gas, oil)
- Mixed grid energy
- Nuclear power

### Categories Tracked
- **Energy**: Electricity consumption, heating, cooling
- **Transport**: Commuting, flights, public transportation
- **Waste**: Disposal, recycling activities
- **Consumption**: Food, goods, services
- **Digital**: Cloud services, data usage

## 📁 Project Structure

```
agentic-1-unit/
├── green_agent.py          # Main Green Agent implementation
├── config.py               # Configuration settings and constants
├── example_usage.py        # Comprehensive usage examples
├── test_green_agent.py     # Test suite for validation
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
└── LICENSE                # MIT License
```

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/KurtSoncco/agentic-1-unit.git
cd agentic-1-unit
```

2. **Install dependencies** (optional, the agent works with standard Python):
```bash
pip install -r requirements.txt
```

3. **Run the example**:
```bash
python3 example_usage.py
```

## 📖 Quick Start

### Basic Usage

```python
from green_agent import GreenAgent

# Create the agent
agent = GreenAgent("MyEcoAgent")

# Add energy usage data
agent.add_energy_usage("office_computer", 2.5, "mixed")
agent.add_energy_usage("solar_panels", 8.0, "renewable")
agent.add_energy_usage("home_heating", 15.0, "fossil")

# Add other carbon footprint activities
agent.add_carbon_footprint("Daily commute", 5.2, "transport")
agent.add_carbon_footprint("Waste disposal", 1.1, "waste")

# Get environmental insights
print(f"Total Carbon Footprint: {agent.calculate_total_carbon_footprint():.2f} kg CO2")
print(f"Energy Efficiency Score: {agent.calculate_energy_efficiency_score():.1f}%")

# Generate recommendations
recommendations = agent.generate_recommendations()
for rec in recommendations:
    print(f"• {rec.title} - {rec.impact} impact")

# Generate and save comprehensive report
report = agent.get_environmental_report()
agent.save_report("my_environmental_report.json")
```

### Advanced Example

```python
from green_agent import GreenAgent
from datetime import datetime

# Create agent with custom name
agent = GreenAgent("EcoGuardian")

# Simulate a week of energy data
devices = [
    ("office_computer", "mixed", 3.0),
    ("home_heating", "fossil", 12.0),
    ("solar_panels", "renewable", 9.0),
    ("electric_vehicle", "mixed", 20.0)
]

for device_id, source, consumption in devices:
    agent.add_energy_usage(device_id, consumption, source)

# Add transportation and lifestyle data
agent.add_carbon_footprint("Weekly commute", 25.0, "transport")
agent.add_carbon_footprint("Household activities", 10.0, "consumption")

# Get detailed analysis
report = agent.get_environmental_report()
print(f"Agent: {report['agent_name']}")
print(f"Total Emissions: {report['summary']['total_carbon_footprint_kg']} kg CO2")
print(f"Efficiency Score: {report['summary']['energy_efficiency_score']}%")

# Show top recommendations
for rec in report['recommendations'][:3]:
    print(f"• {rec['title']}: {rec['description']}")
```

## 🧪 Testing

Run the comprehensive test suite to validate functionality:

```bash
python3 test_green_agent.py
```

The test suite includes:
- Agent initialization and configuration
- Energy usage and carbon footprint tracking
- Efficiency score calculations
- Recommendation generation
- Report creation and file I/O
- Data validation and edge cases

## 📊 Report Example

The Green Agent generates comprehensive environmental reports:

```json
{
  "agent_name": "EcoGuardian",
  "timestamp": "2025-01-15T10:30:00",
  "summary": {
    "total_carbon_footprint_kg": 501.94,
    "total_energy_consumption_kwh": 453.12,
    "energy_efficiency_score": 12.94,
    "number_of_recommendations": 4
  },
  "carbon_by_category": {
    "transport": 223.50,
    "energy": 212.14,
    "consumption": 45.30,
    "waste": 18.90
  },
  "energy_sources": {
    "mixed": 293.30,
    "fossil": 101.20,
    "renewable": 58.62
  },
  "recommendations": [
    {
      "title": "Switch to Renewable Energy",
      "description": "Consider switching to renewable energy sources...",
      "impact": "high",
      "category": "energy",
      "estimated_savings": 301.16
    }
  ]
}
```

## 🎓 Educational Value

This Green Agent is designed for the **Agentic AI class** and demonstrates:

### AI Agent Concepts
- **Autonomous Decision Making**: The agent independently generates recommendations
- **Environmental Sensing**: Processes energy and emission data to understand environmental state
- **Goal-Oriented Behavior**: Focuses on sustainability and carbon reduction goals
- **Learning from Data**: Adapts recommendations based on usage patterns
- **Multi-Domain Integration**: Combines energy, transport, and consumption data

### Sustainability Focus
- **Environmental Awareness**: Promotes eco-friendly practices
- **Data-Driven Insights**: Uses real metrics for environmental impact
- **Actionable Intelligence**: Provides specific, implementable recommendations
- **Progress Tracking**: Enables monitoring of environmental improvements over time

## 🌍 Environmental Impact

The Green Agent promotes:
- **Renewable Energy Adoption**: Encourages switching to clean energy sources
- **Energy Efficiency**: Identifies opportunities to reduce consumption
- **Carbon Footprint Reduction**: Provides clear metrics and improvement strategies
- **Sustainable Transportation**: Promotes eco-friendly travel options
- **Waste Reduction**: Encourages recycling and waste minimization

## 🔧 Configuration

Customize the agent behavior through `config.py`:

```python
# Carbon intensity factors (kg CO2 per kWh)
DEFAULT_CARBON_INTENSITY = {
    "renewable": 0.0,
    "fossil": 0.82,
    "mixed": 0.41,
    "nuclear": 0.006,
    "solar": 0.041,
    "wind": 0.011
}

# Efficiency thresholds for rating
EFFICIENCY_THRESHOLDS = {
    "excellent": 90,
    "good": 70,
    "average": 50,
    "poor": 30
}
```

## 🤝 Contributing

This project is part of an educational assignment, but suggestions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎖️ Author

**Kurt Walter Soncco Sinchi**  
*Agentic AI Class Project*

---

*Made with 🌱 for a more sustainable future*