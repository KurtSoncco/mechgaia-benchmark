# MechGAIA Green Agent - AgentBeats Setup Documentation

## 🎯 **Agent Overview**

**Agent Name**: MechGAIA-Green-Agent  
**Version**: 0.1.0  
**Type**: Green Agent (Evaluator)  
**Domain**: Mechanical Engineering  
**Author**: Kurt Walter Soncco Sinchi  
**Email**: kurtwal98@berkeley.edu  

## 🌐 **Deployment URLs**

- **Agent URL**: `https://your-agent-project-production.up.railway.app`
- **Launcher URL**: `https://your-launcher-project-production.up.railway.app`
- **Health Check**: `/health`
- **Agent Info**: `/info`

## 🔧 **Technical Setup**

### **Agent Architecture**
- **Main Entry Point**: `agentbeats_main.py`
- **Agent Function**: `run_agent(state, tools) -> Dict[str, Any]`
- **Protocol**: JSON over HTTP/stdin
- **Health Monitoring**: Built-in health endpoints
- **Error Handling**: Comprehensive error handling and graceful degradation

### **Supported Interfaces**
- **AgentBeats Protocol**: Full compliance with AgentBeats communication protocol
- **HTTP Endpoints**: Health check and agent information endpoints
- **JSON I/O**: Standard JSON input/output format

### **Dependencies**
- **Python**: 3.11+
- **Core Libraries**: pandas, numpy, sympy, cadquery
- **AgentBeats SDK**: agentbeats
- **Web Framework**: Built-in HTTP server
- **Database**: SQLite (with Redis optional)

## 📋 **Task Index**

### **Level 1: Stress Analysis**
- **Task ID**: `mechgaia_level_1`
- **Description**: Calculate maximum bending stress in a steel rod
- **Problem**: 1-meter long, 20mm diameter steel rod, supported at both ends, 100N point load at center
- **Expected Output**: Numerical answer in Pascals (Pa)
- **Evaluation Criteria**: Numerical accuracy, code execution
- **Difficulty**: Beginner

### **Level 2: Shaft Design**
- **Task ID**: `mechgaia_level_2`
- **Description**: Material selection and diameter calculation for power transmission shaft
- **Problem**: Design shaft to transmit 10kW at 1500 RPM with safety factor of 2
- **Expected Output**: Material choice and minimum diameter
- **Evaluation Criteria**: Material selection, calculation accuracy, constraint satisfaction
- **Difficulty**: Intermediate

### **Level 3: Plate Optimization**
- **Task ID**: `mechgaia_level_3`
- **Description**: CAD-based plate optimization for reduced deflection
- **Problem**: Reduce max deflection by 25% while limiting mass increase to 15%
- **Expected Output**: Modified CAD file path
- **Evaluation Criteria**: Deflection constraint, mass constraint, design optimization
- **Difficulty**: Advanced

## 👥 **Participant Requirements**

### **Technical Requirements**
- **Programming Language**: Python 3.10+
- **Allowed Libraries**: 
  - Standard library modules
  - numpy, pandas, sympy, math
  - matplotlib (for visualization)
  - json, datetime, pathlib
- **Restricted Functions**: 
  - File I/O operations
  - Network access
  - System calls
  - Import restrictions

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
    "assumptions": "list_of_assumptions_made"
  }
}
```

### **Evaluation Process**
1. **Submission Validation**: Verify submission format and completeness
2. **Code Execution**: Safely execute participant's reasoning code
3. **Numerical Verification**: Compare answers against analytical solutions
4. **Constraint Checking**: Verify design constraints are satisfied
5. **Scoring**: Calculate composite score based on accuracy and constraints

### **Scoring System**
- **Level 1**: 
  - Numerical accuracy: 70%
  - Code execution: 30%
- **Level 2**: 
  - Material selection: 40%
  - Calculation accuracy: 40%
  - Constraint satisfaction: 20%
- **Level 3**: 
  - Deflection constraint: 50%
  - Mass constraint: 30%
  - Design optimization: 20%

### **Time Limits**
- **Level 1**: 5 minutes
- **Level 2**: 10 minutes
- **Level 3**: 15 minutes

### **Resource Constraints**
- **Memory Limit**: 1GB
- **CPU Time**: As per time limits above
- **Storage**: Temporary files only

## 🔒 **Security and Safety**

### **Code Execution**
- **Sandboxed Environment**: All code execution in isolated environment
- **Limited Scope**: Restricted global namespace
- **Resource Monitoring**: Memory and CPU usage tracking
- **Timeout Protection**: Automatic termination of long-running code

### **Input Validation**
- **Format Checking**: Strict JSON schema validation
- **Type Validation**: Parameter type checking
- **Range Validation**: Numerical bounds checking
- **Sanitization**: Input sanitization for safety

## 📊 **Metrics and Monitoring**

### **Performance Metrics**
- **Evaluation Time**: Time to complete evaluation
- **Accuracy Scores**: Detailed accuracy breakdown
- **Resource Usage**: Memory and CPU utilization
- **Error Rates**: Failure and timeout statistics

### **Leaderboard**
- **Real-time Updates**: Live leaderboard updates
- **Historical Data**: Performance trends over time
- **Detailed Analytics**: Comprehensive performance analysis
- **Export Capabilities**: Data export for analysis

## 🚀 **Deployment Instructions**

### **Railway Deployment**
1. **Agent Service**: Deploy main agent using `Dockerfile.uv`
2. **Launcher Service**: Deploy launcher using `agentbeats/launcher:latest`
3. **Environment Variables**: Set required environment variables
4. **Health Checks**: Verify health endpoints are accessible

### **Environment Variables**
```
AGENTBEATS_HOST=0.0.0.0
AGENTBEATS_PORT=8080
LAUNCHER_HOST=launcher
LAUNCHER_PORT=8081
PYTHONPATH=/app
REDIS_URL=redis://localhost:6379
```

## 📞 **Support and Contact**

- **GitHub Repository**: [Your Repository URL]
- **Documentation**: [Your Documentation URL]
- **Issues**: GitHub Issues for bug reports
- **Contact**: kurtwal98@berkeley.edu

---

**Last Updated**: October 2024  
**Version**: 0.1.0  
**Status**: Production Ready
