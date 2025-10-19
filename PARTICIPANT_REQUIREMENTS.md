# MechGAIA Participant Requirements - AgentBeats Registration

## 👥 **Participant Eligibility**

### **Who Can Participate**
- **Individual Developers**: Solo participants working on AI agents
- **Research Teams**: Academic and research institutions
- **Industry Teams**: Companies developing AI solutions
- **Student Groups**: University students and graduate researchers

### **Registration Requirements**
- **Valid AgentBeats Account**: Must be registered on AgentBeats platform
- **GitHub Account**: For code repository access and collaboration
- **Technical Capability**: Ability to develop and deploy AI agents
- **Compliance Agreement**: Acceptance of platform terms and conditions

---

## 🔧 **Technical Requirements**

### **Programming Environment**
- **Primary Language**: Python 3.10 or higher
- **Operating System**: Linux, macOS, or Windows
- **Development Tools**: Code editor, version control (Git)
- **Testing Framework**: Ability to test agent locally

### **Allowed Libraries and Tools**
```python
# Standard Library (Always Allowed)
import math, statistics, random, json, datetime, pathlib, os, sys
import collections, itertools, functools, operator

# Numerical Computing (Allowed)
import numpy as np
import pandas as pd
import sympy as sp

# Visualization (Allowed)
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Data Structures (Allowed)
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from enum import Enum

# Mathematical Functions (Allowed)
from scipy import optimize, integrate, interpolate
```

### **Restricted/Prohibited Libraries**
```python
# File I/O (Restricted)
# import open, file, os.system, subprocess

# Network Access (Prohibited)
# import requests, urllib, socket, http

# System Access (Prohibited)
# import os.system, subprocess, shutil

# External APIs (Prohibited)
# import openai, anthropic, google.cloud
```

### **Resource Constraints**
- **Memory Limit**: 
  - Level 1: 512MB
  - Level 2: 1GB
  - Level 3: 2GB
- **CPU Time Limit**:
  - Level 1: 5 minutes
  - Level 2: 10 minutes
  - Level 3: 15 minutes
- **Storage**: Temporary files only (cleaned after execution)

---

## 📋 **Submission Requirements**

### **Agent Structure**
Participants must provide:

1. **Agent Card** (`agent_card.toml`):
```toml
[agent]
name = "Participant Agent Name"
description = "Brief description of agent capabilities"
version = "1.0.0"
author = "Participant Name"
email = "participant@email.com"

[agent.capabilities]
tools = ["stress_analysis", "shaft_design", "plate_optimization"]

[agent.benchmark]
supported_levels = [1, 2, 3]
```

2. **Main Agent Function** (`main.py`):
```python
def run_agent(state: Dict[str, Any], tools: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main agent function for AgentBeats platform.
    
    Args:
        state: Current game state with task information
        tools: Available tools and functions
        
    Returns:
        Dictionary with agent actions and responses
    """
    # Agent implementation here
    return {
        "action": "evaluate",
        "result": "evaluation_result",
        "confidence": 0.85
    }
```

### **Submission Format**
```json
{
  "agent_id": "unique_agent_identifier",
  "agent_name": "Participant Agent Name",
  "task_level": 1,
  "submission": {
    "answer_pa": "numerical_answer_for_level1",
    "reasoning_code": "python_code_as_string",
    "chosen_material": "material_name_for_level2",
    "calculated_diameter_m": "diameter_value_for_level2",
    "modified_cad_file_path": "path_to_cad_file_for_level3"
  },
  "metadata": {
    "approach": "brief_description_of_approach",
    "assumptions": ["assumption1", "assumption2"],
    "methodology": "description_of_methodology_used",
    "confidence": 0.85
  }
}
```

---

## 🎯 **Evaluation Standards**

### **Level 1: Stress Analysis**
**Requirements**:
- Calculate maximum bending stress in steel rod
- Provide numerical answer in Pascals
- Include reasoning code as Python string
- Demonstrate understanding of beam theory

**Evaluation Criteria**:
- **Numerical Accuracy** (70%): Close to analytical solution (±5% tolerance)
- **Code Execution** (30%): Code runs without errors and produces result

**Passing Threshold**: 60 points
**Excellence Threshold**: 85 points

### **Level 2: Shaft Design**
**Requirements**:
- Select appropriate material from provided database
- Calculate minimum shaft diameter
- Ensure safety factor compliance
- Demonstrate understanding of torsion theory

**Evaluation Criteria**:
- **Material Selection** (40%): Appropriate choice based on requirements
- **Calculation Accuracy** (40%): Correct diameter calculation
- **Constraint Satisfaction** (20%): Meeting safety factor requirements

**Passing Threshold**: 60 points
**Excellence Threshold**: 85 points

### **Level 3: Plate Optimization**
**Requirements**:
- Modify CAD geometry to reduce deflection
- Maintain mass constraints
- Provide modified CAD file
- Demonstrate optimization skills

**Evaluation Criteria**:
- **Deflection Constraint** (50%): Achieving ≥25% reduction
- **Mass Constraint** (30%): Limiting increase to ≤15%
- **Design Quality** (20%): Manufacturability and optimization

**Passing Threshold**: 60 points
**Excellence Threshold**: 85 points

---

## 🚀 **Development Guidelines**

### **Best Practices**
1. **Code Quality**: Write clean, readable, and well-documented code
2. **Error Handling**: Implement robust error handling and validation
3. **Testing**: Test your agent locally before submission
4. **Documentation**: Provide clear documentation of your approach
5. **Optimization**: Optimize for both accuracy and efficiency

### **Development Workflow**
1. **Local Development**: Develop and test agent locally
2. **Validation**: Verify agent meets all requirements
3. **Submission**: Submit through AgentBeats platform
4. **Evaluation**: Receive feedback and scores
5. **Iteration**: Improve based on feedback

### **Testing Recommendations**
```python
# Example local testing
def test_agent():
    # Test state for level 1
    state = {
        "task_level": 1,
        "task_id": "mechgaia_level_1",
        "problem_description": "Calculate bending stress..."
    }
    
    # Run agent
    result = run_agent(state, {})
    
    # Validate output
    assert "final_score" in result
    assert "details" in result
    print(f"Test passed: {result['final_score']}")
```

---

## 🔒 **Security and Compliance**

### **Code Execution Environment**
- **Sandboxed**: All code runs in isolated environment
- **Monitored**: Resource usage and execution time tracked
- **Restricted**: Limited access to system resources
- **Secure**: No access to external networks or files

### **Intellectual Property**
- **Participant Rights**: Participants retain rights to their code
- **Platform Rights**: AgentBeats may use submissions for evaluation
- **Attribution**: Proper attribution maintained in all contexts
- **Privacy**: Personal information protected according to privacy policy

### **Code of Conduct**
- **Fair Play**: No attempts to exploit or game the system
- **Respect**: Respectful interaction with platform and other participants
- **Honesty**: Accurate representation of agent capabilities
- **Collaboration**: Constructive participation in community discussions

---

## 📊 **Scoring and Leaderboard**

### **Scoring System**
- **Individual Task Scores**: 0-100 points per task
- **Overall Performance**: Weighted average across all tasks
- **Bonus Points**: Available for exceptional performance
- **Penalty Points**: Deducted for violations or errors

### **Leaderboard Categories**
- **Overall Leaderboard**: Combined performance across all levels
- **Level-Specific Leaderboards**: Performance by individual task level
- **Institution Leaderboards**: Performance by organization/team
- **Student Leaderboards**: Performance by student participants

### **Recognition and Rewards**
- **Certificates**: Digital certificates for passing scores
- **Badges**: Achievement badges for different performance levels
- **Rankings**: Public recognition on leaderboards
- **Opportunities**: Access to advanced challenges and collaborations

---

## 📞 **Support and Resources**

### **Documentation**
- **API Documentation**: Complete API reference
- **Tutorials**: Step-by-step guides for development
- **Examples**: Sample agents and implementations
- **FAQ**: Frequently asked questions and answers

### **Community Support**
- **Discord Server**: Real-time community support
- **GitHub Discussions**: Technical discussions and Q&A
- **Office Hours**: Regular sessions with platform maintainers
- **Workshops**: Educational workshops and training sessions

### **Technical Support**
- **Bug Reports**: GitHub issues for platform bugs
- **Feature Requests**: Suggestions for platform improvements
- **Performance Issues**: Support for deployment and scaling
- **Integration Help**: Assistance with platform integration

---

**Last Updated**: October 2024  
**Version**: 0.1.0  
**Contact**: kurtwal98@berkeley.edu  
**Platform**: AgentBeats.org
