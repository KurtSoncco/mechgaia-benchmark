# Green Agent Configuration

# Default carbon intensity factors (kg CO2 per kWh)
DEFAULT_CARBON_INTENSITY = {
    "renewable": 0.0,
    "fossil": 0.82,
    "mixed": 0.41,
    "nuclear": 0.006,
    "hydro": 0.024,
    "solar": 0.041,
    "wind": 0.011
}

# Energy efficiency thresholds
EFFICIENCY_THRESHOLDS = {
    "excellent": 90,
    "good": 70,
    "average": 50,
    "poor": 30,
    "very_poor": 0
}

# High consumption warning threshold (kWh)
HIGH_CONSUMPTION_THRESHOLD = 10.0

# Recommendation impact weights
IMPACT_WEIGHTS = {
    "high": 3,
    "medium": 2,
    "low": 1
}

# Default report file name
DEFAULT_REPORT_FILENAME = "green_report.json"