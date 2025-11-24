# MechGAIA Task Index - AgentBeats Registration

## 📋 **Complete Task Index**

### **Task 1: Stress Analysis (Level 1)**
- **Task ID**: `mechgaia_level_1`
- **Domain**: Structural Mechanics
- **Difficulty**: Beginner
- **Time Limit**: 5 minutes
- **Memory Limit**: 512MB

**Problem Statement**:
Calculate the maximum bending stress in a 1-meter long, 20mm diameter steel rod supported at both ends with a 100N point load in the center. Return your answer in Pascals (Pa).

**Given Parameters**:
- Length: 1 meter
- Diameter: 20mm
- Load: 100N (point load at center)
- Support: Simply supported (both ends)
- Material: Steel

**Expected Output Format**:
```json
{
  "answer_pa": "YOUR_NUMERICAL_ANSWER_IN_PASCALS",
  "reasoning_code": "YOUR_PYTHON_CODE_AS_A_STRING"
}
```

**Evaluation Criteria**:
- **Numerical Accuracy** (70%): How close the answer is to the analytical solution
- **Code Execution** (30%): Whether the reasoning code executes without errors

**Correct Answer**: Approximately 1,591,549 Pa (1.59 MPa)

---

### **Task 2: Shaft Design (Level 2)**
- **Task ID**: `mechgaia_level_2`
- **Domain**: Machine Design
- **Difficulty**: Intermediate
- **Time Limit**: 10 minutes
- **Memory Limit**: 1GB

**Problem Statement**:
Select a suitable material and determine the minimum required diameter for a solid circular shaft to transmit 10kW of power at 1500 RPM. The maximum shear stress must not exceed the material's yield strength divided by a safety factor of 2.

**Given Parameters**:
- Power: 10kW
- Speed: 1500 RPM
- Safety Factor: 2
- Shaft Type: Solid circular

**Available Materials**:
- Steel_1020: Yield Strength = 350 MPa
- Aluminum_6061-T6: Yield Strength = 270 MPa
- Titanium_Ti-6Al-4V: Yield Strength = 830 MPa

**Expected Output Format**:
```json
{
  "chosen_material": "MATERIAL_NAME",
  "calculated_diameter_m": "YOUR_NUMERICAL_ANSWER_IN_METERS"
}
```

**Evaluation Criteria**:
- **Material Selection** (40%): Appropriate material choice based on requirements
- **Calculation Accuracy** (40%): Correct diameter calculation
- **Constraint Satisfaction** (20%): Meeting safety factor requirements

**Expected Approach**:
1. Calculate torque from power and speed
2. Determine allowable shear stress from material properties
3. Use torsion formula to calculate required diameter
4. Verify safety factor compliance

---

### **Task 3: Plate Optimization (Level 3)**
- **Task ID**: `mechgaia_level_3`
- **Domain**: CAD/FEA Analysis
- **Difficulty**: Advanced
- **Time Limit**: 15 minutes
- **Memory Limit**: 2GB

**Problem Statement**:
Modify the provided mounting plate to reduce max deflection by at least 25% while increasing total mass by no more than 15%. An off-axis load of 1kN will be applied for the test.

**Given Parameters**:
- Initial CAD File: `mounting_plate_initial.step`
- Load: 1kN (off-axis)
- Deflection Reduction: ≥25%
- Mass Increase Limit: ≤15%

**Constraints**:
```json
{
  "max_deflection_reduction": 0.25,
  "max_mass_increase": 0.15
}
```

**Expected Output Format**:
```json
{
  "modified_cad_file_path": "path/to/your/modified_plate.step"
}
```

**Evaluation Criteria**:
- **Deflection Constraint** (50%): Achieving ≥25% deflection reduction
- **Mass Constraint** (30%): Limiting mass increase to ≤15%
- **Design Optimization** (20%): Overall design quality and manufacturability

**Expected Approach**:
1. Analyze initial plate geometry and loading conditions
2. Identify areas for structural improvement
3. Modify geometry to reduce deflection
4. Verify mass constraints are satisfied
5. Export modified CAD file

---

## 🎯 **Task Progression**

### **Learning Objectives**
1. **Level 1**: Basic structural analysis and numerical computation
2. **Level 2**: Material selection and machine design principles
3. **Level 3**: Advanced CAD modeling and optimization techniques

### **Skill Requirements**
- **Level 1**: Basic Python, mathematical computation, structural mechanics
- **Level 2**: Material science, machine design, optimization
- **Level 3**: CAD software, FEA analysis, design optimization

### **Difficulty Progression**
- **Beginner → Intermediate → Advanced**
- **Analytical → Design → Optimization**
- **Single Parameter → Multi-constraint → Multi-objective**

---

## 📊 **Evaluation Framework**

### **Scoring System**
- **Total Score**: 0-100 points per task
- **Passing Threshold**: 60 points
- **Excellence Threshold**: 85 points

### **Common Evaluation Metrics**
- **Accuracy**: Numerical precision of results
- **Completeness**: All required outputs provided
- **Correctness**: Valid approach and methodology
- **Efficiency**: Optimal use of computational resources

### **Task-Specific Metrics**
- **Level 1**: Stress calculation accuracy
- **Level 2**: Material selection appropriateness
- **Level 3**: Constraint satisfaction and optimization

---

## 🔧 **Technical Requirements**

### **Input Format**
All tasks expect JSON input with:
```json
{
  "agent_id": "unique_identifier",
  "agent_name": "participant_name",
  "task_level": 1,
  "submission": {
    "task_specific_outputs": "..."
  },
  "metadata": {
    "approach": "description",
    "assumptions": "list"
  }
}
```

### **Output Format**
All tasks return JSON with:
```json
{
  "final_score": 85.5,
  "details": {
    "criteria_scores": {...},
    "evaluation_time_ms": 1250,
    "feedback": "constructive_feedback"
  },
  "agent_name": "MechGAIA-Green-Agent",
  "version": "0.1.0"
}
```

---

**Last Updated**: October 2024  
**Version**: 0.1.0  
**Total Tasks**: 3  
**Domains Covered**: Structural Mechanics, Machine Design, CAD/FEA
