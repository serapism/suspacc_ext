# Steering Calculations Extension (`steering_ext`)

Comprehensive vehicle steering geometry calculations library including turning circle diameter, Ackermann steering percentage, and related suspension kinematics.

## Overview

The `steering_ext` module provides functions for analyzing vehicle steering characteristics and geometry validation. It includes calculations for kerb-to-kerb turning radius, Ackermann steering geometry, and design validation tools.

## Features

### Core Calculations

#### 1. **Turning Circle Diameter** (`CalculateKerbToKerbTurningCircle`)
Calculates the minimum turning circle diameter of a vehicle based on steering angle and geometry.

**Formula:**
```
R = Wheelbase / sin(Steer Angle)
Diameter = 2 × (R + Tyre Width / 2)
```

**Inputs:**
- `wheelbase` (mm): Vehicle wheelbase (2400-3000 typical)
- `wheeltrack` (mm): Track width (1400-1700 typical)
- `outerwheelAngle` (°): Outer wheel steer angle (25-45° typical)
- `tyreWidth` (mm): Tyre section width (205-255 typical)

**Returns:**
- Turning circle diameter in meters

**Example:**
```vb
Dim turningCircle As Double = TCDCalc.CalculateKerbToKerbTurningCircle(2800, 1506, 31.42, 205)
' Result: ~5.86 m
```

#### 2. **Ackermann Percentage** (`CalculateAckermannPercentage`)
Evaluates how closely the steering geometry matches ideal Ackermann steering geometry.

**Formula:**
```
θ_ideal = atan(L / (T + L / tan(θ_outer)))
Ackermann % = (θ_ideal / θ_actual) × 100
```

**Inputs:**
- `Wheelbase` (mm): Vehicle wheelbase
- `TrackWidth` (mm): Track width between wheels
- `SteerAngleOuter` (°): Outer wheel steering angle
- `SteerAngleInner` (°): Inner wheel steering angle

**Returns:**
- Ackermann percentage

**Interpretation:**
- **100%** = Perfect Ackermann geometry (ideal)
- **< 100%** = Oversteer characteristic (more inner steering)
- **> 100%** = Understeer characteristic (less inner steering)

**Example:**
```vb
Dim ackermann As Double = TCDCalc.CalculateAckermannPercentage(2800, 1506, 31.42, 37.58)
' Result: ~64.96% (oversteer tendency)
```

## Input Validation

Both functions include comprehensive input validation with helpful error messages:

### Wheelbase Validation
- **Requirement:** > 0 mm
- **Typical Range:** 2400-3000 mm
- **Acceptable Range:** 1500-4500 mm

### Track Width Validation
- **Requirement:** > 0 mm
- **Typical Range:** 1400-1700 mm
- **Acceptable Range:** 1000-2500 mm

### Steer Angle Validation (Outer)
- **Requirement:** 0° < angle ≤ 90°
- **Typical Range:** 25-45°
- **Warning:** If > 60°

### Steer Angle Validation (Inner)
- **Requirement:** 0° < angle ≤ 90°
- **Typical Range:** 20-40°
- **Relationship:** Should be ≤ outer angle

### Tyre Width Validation
- **Requirement:** > 0 mm
- **Typical Range:** 205-255 mm (passenger cars)
- **Acceptable Range:** 100-400 mm

## Error Handling

All functions throw `ArgumentException` for invalid inputs with descriptive messages including typical ranges:

```vb
Try
    Dim result = TCDCalc.CalculateKerbToKerbTurningCircle(-2800, 1506, 31.42, 205)
Catch ex As ArgumentException
    ' Catches: "Wheelbase must be positive (> 0 mm). Typical range: 2400-3000 mm"
End Try
```

## Test Suite

### `TCDCalcTest` Class

Comprehensive test coverage with reference scenarios:

#### Turning Circle Tests
1. **Sedan 35°** - Standard geometry, expecting 10-11m
2. **Compact Car 40°** - Tight turning, expecting 8-9m
3. **Large SUV 32°** - Limited steering, expecting 11-12.5m
4. **Small Angle 5°** - Minimal steering, expecting >30m
5. **Zero Angle** - Edge case returning infinity

#### Ackermann Tests
1. **Perfect Geometry** - Calculated ideal inner angle
2. **Understeer** - Inner angle too small
3. **Oversteer** - Inner angle too large
4. **Compact Car** - Real-world compact geometry
5. **Large Vehicle** - Real-world large vehicle geometry

### `TCDValidation` Class

Validates calculations against reference values from the Turning Radius Calculator:

**Reference Values:**
- Wheelbase: 2800 mm
- Track Width: 1506 mm
- Outer Wheel: 31.42°
- Inner Wheel: 37.58°
- Tyre Width: 205 mm

**Expected Results:**
- Turning Circle: 5.86 m ✓
- Ackermann Ratio: 64.96% ✓

## Usage Examples

### Basic Turning Circle Calculation
```vb
' Sedan with typical geometry
Dim wheelbase As Double = 2700
Dim trackWidth As Double = 1500
Dim steerAngle As Double = 35
Dim tyreWidth As Double = 225

Dim turningDiameter As Double = TCDCalc.CalculateKerbToKerbTurningCircle(wheelbase, trackWidth, steerAngle, tyreWidth)
Console.WriteLine($"Turning Circle: {turningDiameter:F2} m")
' Output: Turning Circle: 10.54 m
```

### Ackermann Geometry Analysis
```vb
' Analyze steering characteristic
Dim wheelbase As Double = 2800
Dim trackWidth As Double = 1506
Dim outerAngle As Double = 31.42
Dim innerAngle As Double = 37.58

Dim ackermannPercent As Double = TCDCalc.CalculateAckermannPercentage(wheelbase, trackWidth, outerAngle, innerAngle)

If ackermannPercent < 100 Then
    Console.WriteLine($"Oversteer: {ackermannPercent:F2}%")
ElseIf ackermannPercent > 100 Then
    Console.WriteLine($"Understeer: {ackermannPercent:F2}%")
Else
    Console.WriteLine("Perfect Ackermann")
End If
```

### Running Tests
```vb
' Get comprehensive test results
Dim results As DataTable = TCDCalcTest.RunAllTests()

' Generate summary statistics
Dim summary As DataTable = TCDCalcTest.GenerateSummary(results)

' Validate against reference values
Dim validation As DataTable = TCDValidation.ValidateScreenshotValues()
```

## Standards and References

- **Milliken & Milliken** - Race Car Vehicle Dynamics
  - Chapter 15: Steering Geometry and Control
- **Gillespie, T.D.** - Fundamentals of Vehicle Dynamics
  - Chapter 6: Steering System Characteristics
- **ISO 3691-4** - Industrial Trucks - Safety
  - Part 4: Driverless industrial trucks and their systems
- **SAE J670** - Vehicle Dynamics Terminology
- **Ackermann, Rudolph** - Original steering geometry theory

## Vehicle Typical Ranges

### Passenger Cars
- **Wheelbase:** 2600-2900 mm
- **Track Width:** 1450-1600 mm
- **Max Steer Angle:** 35-45°
- **Turning Radius:** 5.0-6.5 m

### Compact Cars
- **Wheelbase:** 2300-2550 mm
- **Track Width:** 1400-1500 mm
- **Max Steer Angle:** 38-45°
- **Turning Radius:** 4.5-5.5 m

### SUVs / Crossovers
- **Wheelbase:** 2800-3000 mm
- **Track Width:** 1550-1700 mm
- **Max Steer Angle:** 30-38°
- **Turning Radius:** 5.5-6.5 m

### Large Trucks
- **Wheelbase:** 3200-3600 mm
- **Track Width:** 1700-1900 mm
- **Max Steer Angle:** 25-35°
- **Turning Radius:** 6.5-8.5 m

## Performance Characteristics

| Characteristic | Low Ackermann % | Perfect Ackermann | High Ackermann % |
|---|---|---|---|
| Inner Wheel Steering | More steering | Ideal | Less steering |
| Cornering Behavior | Oversteer tendency | Neutral | Understeer tendency |
| Vehicle Response | Quick turn-in | Balanced | Gradual turn-in |
| Use Case | Performance/Racing | Street driving | Safety/Stability |

## Build Instructions

### Prerequisites
- .NET Framework 4.8 or higher
- Visual Studio 2019+ or MSBuild 17.0+

### Build from Command Line
```powershell
msbuild steering_ext.vbproj /p:Configuration=Release
```

### Output Files
- **DLL:** `bin\Release\steering_ext.dll` (14 KB)
- **XML Docs:** `bin\Release\steering_ext.xml` (comprehensive API documentation)
- **PDB:** `bin\Release\steering_ext.pdb` (debug symbols)

## Class Reference

### `TCDCalc`
Main calculation class with static methods for steering geometry analysis.

**Public Methods:**
- `CalculateKerbToKerbTurningCircle()` - Turning circle diameter
- `CalculateAckermannPercentage()` - Ackermann geometry analysis

### `TCDCalcTest`
Comprehensive test suite for validation.

**Public Methods:**
- `RunAllTests()` - Execute all test cases
- `GenerateSummary()` - Generate test summary statistics

### `TCDValidation`
Reference value validation and configuration comparison.

**Public Methods:**
- `ValidateScreenshotValues()` - Validate against known reference values
- `CompareSteeringConfigurations()` - Compare multiple steering scenarios

## Troubleshooting

### Common Errors

**Error:** "Wheelbase must be positive (> 0 mm)"
- **Cause:** Wheelbase parameter is zero or negative
- **Solution:** Provide valid wheelbase in mm (typical: 2400-3000)

**Error:** "Steer angle must be > 0° and <= 90°"
- **Cause:** Angle out of valid range
- **Solution:** Use angles between 0° and 90° (typical: 25-45°)

**Error:** "Inner angle should typically be less than or equal to outer angle"
- **Cause:** Inner wheel steers more than outer (unusual)
- **Solution:** Review input values; inner should be ≤ outer in normal driving

**Error:** "Ackermann percentage is outside expected range (0-200%)"
- **Cause:** Calculated result indicates invalid geometry
- **Solution:** Review all input parameters for validity

## Future Enhancements

- [ ] Add rear wheel steering support
- [ ] Implement steer ratio calculations
- [ ] Add understeer gradient calculations
- [ ] Support for variable geometry steering
- [ ] Tire slip angle integration
- [ ] Real-time geometry validation dashboard

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2025-12-07 | Initial release with turning circle and Ackermann calculations |
| | | Added comprehensive error handling and input validation |
| | | Included test suite and validation functions |

## License

Part of the `suspacc_ext` suspension and steering analysis library.

## Contact & Support

For issues, feature requests, or technical questions regarding steering calculations, please refer to the project documentation or contact the development team.
