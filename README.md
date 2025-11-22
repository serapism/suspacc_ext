# SuspAccApps

Suspension and Accessories Engineering Calculation Library for .NET Framework 4.8

## Overview

This library provides comprehensive engineering calculations for automotive suspension systems, tyre specifications, spring design, and bolted joint analysis. All calculations follow industry standards including ISO, VDI, and ETRTO specifications.

## Project Structure

```
suspacc_ext/
├── susp_ext/           # Suspension calculations
│   ├── tyre_calc.vb   # Tyre dimension and parameter calculations
│   └── spring_calc.vb # Helical compression spring calculations
├── joints_ext/         # Bolted joint calculations
│   └── torque_calc.vb # Torque and VDI 2230 calculations
└── acc_ext/           # Accessories calculations
```

## Modules

### 1. Tyre Calculations (`susp_ext/tyre_calc.vb`)

Provides comprehensive tyre dimension calculations following ETRTO standards.

**Key Functions:**
- `NominalDesignDiameter` - Calculates nominal tyre diameter with rim width correction
- `MaxDiameterInService` - Maximum diameter at 104% of nominal (service conditions)
- `DesignSectionWidth` - Design section width accounting for rim width variance
- `StaticLoadedRadius` - Static loaded radius (78% of unloaded radius)
- `RollingCircumference` - Rolling circumference for speed calculations
- `RimWidthCorrection` - 5mm correction per 0.5" deviation from standard rim width
- `PublishValue` - Returns DataTable with all calculated tyre parameters
- `PublishRimValue` - Returns DataTable with all wheel/rim specifications
- `CalcRimWidth` - Standard measuring rim width per ETRTO

**Usage Example:**
```vb
' Calculate tyre parameters
Dim tyreData As DataTable = TyreCalc.PublishValue("205", "55", "R16", "7.0", True)

' Calculate nominal diameter
Dim diameter As Double = TyreCalc.NominalDesignDiameter("205", "55", "R16", "7.0")
```

**Output DataTable Columns:**
- Parameter (String): Parameter name
- Value (String): Calculated value
- Unit (String): Unit of measurement

---

### 2. Spring Calculations (`susp_ext/spring_calc.vb`)

Helical compression spring calculations based on **ISO 11891:2012** (Hot formed helical compression springs — Technical specifications).

**Key Functions:**

**Spring Rate & Geometry:**
- `SpringRate` - Spring rate using Modulus of Rigidity: k = (G×d⁴)/(8×D³×n)
- `SpringRate3` - Spring rate using Young's Modulus
- `NumberOfActiveCoil` - Calculate active coils from spring properties
- `WireDiameter` - Required wire diameter for target spring rate
- `SpringIndex` - Spring index C = D/d (typical range: 4-12)

**Stress Analysis:**
- `TorsionalStress` - Uncorrected torsional stress in wire
- `TorsionalStressCorrected` - Stress with Wahl correction factor
- `WahlFactor` - Wahl stress correction factor: K = (4C-1)/(4C-4) + 0.615/C
- `Zvalue` - Stress per unit load (1/mm²)
- `OptimumWireDiameter` - Optimal wire diameter for given load and stress

**Dimensional Calculations:**
- `FreeHeight` - Unloaded spring length
- `SolidLength` - Fully compressed length (varies by end condition and manufacturing)
- `MinLength` - Minimum assembly length
- `WireLength` - Total wire length required
- `NoOfEndCoil` - Number of end coils by end condition type

**Performance:**
- `MaxSpringLoad` - Maximum load at solid height
- `RideFrequency` - Natural frequency of suspension system (Hz)
- `checkBuckling` - Validates spring stability under maximum deflection

**Usage Example:**
```vb
' Calculate spring rate
Dim rate As Double = SpringCalc.SpringRate(80000, 50, 3.5, 8.5)

' Check buckling
Dim isSafe As Boolean = SpringCalc.checkBuckling(80000, 210000, 50, 0.5, 200, 80)

' Calculate stress with Wahl factor
Dim springIndex As Double = SpringCalc.SpringIndex(3.5, 50)
Dim wahlFactor As Double = SpringCalc.WahlFactor(springIndex)
Dim stress As Double = SpringCalc.TorsionalStressCorrected(50, 500, 3.5, wahlFactor)
```

**Spring End Conditions Supported:**
- CLOSED NON-GROUND
- CLOSED GROUND
- CLOSED TAPERED
- OPEN NON GROUND
- OPEN GROUND
- OPEN TAPERED
- OPEN 3/4 TURN NON GROUND

---

### 3. Bolted Joint Calculations (`joints_ext/torque_calc.vb`)

Comprehensive bolted joint analysis with basic calculations and **VDI 2230 Part 1 (2015)** standard calculations for systematic design of highly stressed bolted joints.

#### Basic Functions

**Core Calculations:**
- `StressArea` - Thread stress area per ISO 898-1: As = (π/4)×((d₂+d₃)/2)²
- `Torque1` - Tightening torque: M = F×(P/(2π) + (μ×d₂)/(2×cos(α)) + μ×d_bearing/2)
- `LoadAxial` - Axial load from stress: F = σ × As
- `CalculateClamping` - Clamping force from torque: F = M/(k×d)
- `validateBolt` - Surface failure criteria validation (tensile + shear)

**Usage Example:**
```vb
' Calculate stress area
Dim As_area As Double = TorqueCalc.StressArea(9.026, 7.938) ' M10 thread

' Calculate tightening torque
Dim torque As Double = TorqueCalc.Torque1(15000, 9.026, 10, 16, 0.14, 0.12, 30, 1.5)

' Validate bolt strength
Dim result As String = TorqueCalc.validateBolt(15000, 500, 300, 200, 1040, 940, 10, False, True)
```

#### VDI 2230 Standard Functions

**Resilience & Load Distribution:**
- `VDI_BoltResilience` - Bolt compliance: δS = lK/(A×E)
- `VDI_ClampedPartsResilience` - Clamped parts compliance using substitute area method
- `VDI_LoadFactor` - Load factor Φ: δS/(δS+δP) (0-1 range)

**Force Analysis:**
- `VDI_BoltForceWorking` - Bolt force under load: FSB = FV + Φ×FA
- `VDI_ClampingForceWorking` - Clamping force under load: FKB = FV - (1-Φ)×FA
- `VDI_AssemblyPreload` - Preload with thermal effects
- `VDI_MinimumPreload` - Minimum required preload for joint security

**Stress & Safety:**
- `VDI_BoltStress` - Bolt stress: σ = FSB/AS
- `VDI_UtilizationFactor` - Safety factor: σ/Rp0.2 (should be < 0.9 for static loads)
- `VDI_TighteningTorque` - Precise torque calculation with thread and head friction

**Special Factors:**
- `VDI_EccentricLoadingFactor` - For non-uniform load distribution
- `VDI_EmbeddingLoss` - Preload loss due to surface settling (typically 3-5 µm)
- `VDI_EffectivePreloadTorque` - Accounts for prevailing torque in locking elements

**VDI 2230 Usage Example:**
```vb
' Calculate resiliences
Dim deltaBolt As Double = TorqueCalc.VDI_BoltResilience(40, 58, 210000)
Dim deltaPlate As Double = TorqueCalc.VDI_ClampedPartsResilience(40, 20, 14, 210000)

' Calculate load factor
Dim phi As Double = TorqueCalc.VDI_LoadFactor(deltaBolt, deltaPlate)

' Determine forces under working load
Dim preload As Double = 15000
Dim workingLoad As Double = 5000
Dim boltForce As Double = TorqueCalc.VDI_BoltForceWorking(preload, workingLoad, phi)
Dim clampForce As Double = TorqueCalc.VDI_ClampingForceWorking(preload, workingLoad, phi)

' Check utilization
Dim stress As Double = TorqueCalc.VDI_BoltStress(boltForce, 58)
Dim utilization As Double = TorqueCalc.VDI_UtilizationFactor(stress, 940)
' utilization should be < 0.9 for static loads
```

---

## Standards & References

- **ISO 898-1** - Mechanical properties of fasteners (stress area calculation)
- **ISO 11891:2012** - Hot formed helical compression springs — Technical specifications
- **VDI 2230 Part 1 (2015)** - Systematic calculation of highly stressed bolted joints
- **ETRTO** - European Tyre and Rim Technical Organisation standards

## Technical Notes

### Tyre Calculations
- All dimensions in millimeters unless specified
- Rim width correction: 5mm per 0.5" deviation from standard
- MaxInService uses 104% factor per ETRTO standards

### Spring Calculations
- **Standard gravity**: g = 9.80665 m/s²
- **Typical spring index**: 4 ≤ C ≤ 12
- **Wahl factor**: Accounts for curvature and direct shear effects
- **Buckling check**: Critical for springs with high free height to diameter ratio

### Bolted Joint Calculations
- **Typical friction coefficients**:
  - Thread friction (μG): 0.12-0.18
  - Head/nut friction (μK): 0.10-0.16
- **Load factor Φ**: 
  - Φ → 0: Very rigid clamped parts (most load to bolt)
  - Φ → 1: Very flexible clamped parts (most load to joint)
- **Utilization limits**:
  - Static load: < 0.9
  - Dynamic load: Requires fatigue analysis per VDI 2230

## Building

The library targets .NET Framework 4.8 and is written in Visual Basic.

```powershell
# Build the project
msbuild susp_ext\susp_ext.vbproj /p:Configuration=Release

# Or open in Visual Studio and build
```

## Output

All calculation functions return either:
- **Double values** for single calculations
- **DataTable** for comprehensive parameter sets (tyre/rim functions)

DataTable structure:
- Column 1: Parameter name (String)
- Column 2: Value (String)
- Column 3: Unit (String)

## License

Engineering calculation library for automotive applications.

## Contributing

When adding new calculations:
1. Include XML documentation summaries
2. Specify units in parameter descriptions
3. Reference applicable standards
4. Add usage examples to README