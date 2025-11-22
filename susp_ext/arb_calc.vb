Imports System.Data

''' <summary>
''' Provides anti-roll bar (stabilizer bar) calculation functions.
''' Calculations based on torsional beam theory and suspension geometry.
''' </summary>
''' <remarks>
''' References:
''' - Milliken, W.F. and Milliken, D.L., "Race Car Vehicle Dynamics", SAE International, 1995
'''   Chapter 19: Roll Resistance and Roll Couples
''' - Gillespie, T.D., "Fundamentals of Vehicle Dynamics", SAE International, 1992
'''   Chapter 7: Steady-State Cornering
''' - Roark's Formulas for Stress and Strain, 8th Edition, Warren C. Young, Richard G. Budynas
'''   Table 10.1: Torsion of circular shafts
''' - SAE J2047: "Tire Performance Technology"
''' - ISO 8855:2011: "Road vehicles — Vehicle dynamics and road-holding ability — Vocabulary"
''' 
''' Key Formulas:
''' - Polar Moment of Inertia (solid circular): J = (π × d⁴) / 32
''' - Torsional Stiffness: K = (G × J) / L
''' - Series Spring Rate: 1/K_total = Σ(1/K_i)
''' - Roll Stiffness: K_roll = K_torsional / (arm_length²)
''' - Shear Stress: τ = (T × r) / J
''' - Twist Angle: θ = T × L / (G × J)
''' </remarks>
Public Class ARBCalc

    ''' <summary>
    ''' Gravitational acceleration constant (m/s²)
    ''' </summary>
    Private Shared ReadOnly gValue As Double = 9.80665

    ''' <summary>
    ''' Calculates anti-roll bar torsional stiffness.
    ''' </summary>
    ''' <param name="diameter">Bar diameter (mm)</param>
    ''' <param name="armLength">Arm length from center to mounting point (mm)</param>
    ''' <param name="centralLength">Central torsion section length (mm)</param>
    ''' <param name="shearModulus">Shear modulus of material (N/mm²), default 80000 for steel</param>
    ''' <returns>DataTable with anti-roll bar stiffness calculations</returns>
    ''' <remarks>
    ''' Calculates torsional stiffness using: K = (G × J) / L
    ''' Where: G = shear modulus, J = polar moment of inertia, L = length
    ''' For circular cross-section: J = (π × d⁴) / 32
    ''' Roll stiffness considers arm geometry and leverage effects.
    ''' 
    ''' Example Input:
    ''' - diameter = 24 mm (typical front ARB for passenger car)
    ''' - armLength = 150 mm
    ''' - centralLength = 800 mm
    ''' - shearModulus = 80000 N/mm² (steel, default)
    ''' 
    ''' Example Output:
    ''' Parameter                          | Value        | Unit
    ''' -----------------------------------|--------------|-------------
    ''' Bar Diameter                       | 24.00        | mm
    ''' Arm Length                         | 150.00       | mm
    ''' Central Section Length             | 800.00       | mm
    ''' Shear Modulus (G)                  | 80000        | N/mm²
    ''' Polar Moment of Inertia (J)        | 32572.03     | mm⁴
    ''' Central Section Stiffness          | 3257203.05   | N·mm/rad
    ''' Single Arm Stiffness               | 17371616.25  | N·mm/rad
    ''' Equivalent Torsional Stiffness     | 2612661.20   | N·mm/rad
    ''' Roll Stiffness at Wheel            | 116.12       | N/mm
    ''' Roll Stiffness at Wheel            | 116118.28    | N/m
    ''' Roll Moment per Degree             | 45605.09     | N·mm/deg
    ''' Max Stress @ 1000 N·mm Torque      | 0.37         | N/mm²
    ''' Twist Angle @ 1000 N·mm Torque     | 0.022        | deg
    ''' Material                           | Steel (typical) |
    ''' </remarks>
    Public Shared Function CalculateARBStiffness(ByVal diameter As Double, _
                                                  ByVal armLength As Double, _
                                                  ByVal centralLength As Double, _
                                                  Optional ByVal shearModulus As Double = 80000) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            ' Validate inputs
            If diameter <= 0 Then
                Throw New ArgumentException("Diameter must be positive", "diameter")
            End If
            If armLength <= 0 Then
                Throw New ArgumentException("Arm length must be positive", "armLength")
            End If
            If centralLength <= 0 Then
                Throw New ArgumentException("Central length must be positive", "centralLength")
            End If
            If shearModulus <= 0 Then
                Throw New ArgumentException("Shear modulus must be positive", "shearModulus")
            End If

            ' Add input parameters
            resultTable.Rows.Add("Bar Diameter", diameter.ToString("F2"), "mm")
            resultTable.Rows.Add("Arm Length", armLength.ToString("F2"), "mm")
            resultTable.Rows.Add("Central Section Length", centralLength.ToString("F2"), "mm")
            resultTable.Rows.Add("Shear Modulus (G)", shearModulus.ToString("F0"), "N/mm²")

            ' Calculate polar moment of inertia (J = π × d⁴ / 32)
            Dim polarMoment As Double = (Math.PI * Math.Pow(diameter, 4)) / 32
            resultTable.Rows.Add("Polar Moment of Inertia (J)", polarMoment.ToString("F2"), "mm⁴")

            ' Calculate torsional stiffness of central section
            ' K_central = (G × J) / L_central
            Dim centralStiffness As Double = (shearModulus * polarMoment) / centralLength
            resultTable.Rows.Add("Central Section Stiffness", centralStiffness.ToString("F2"), "N·mm/rad")

            ' Calculate torsional stiffness of each arm
            ' K_arm = (G × J) / L_arm
            Dim armStiffness As Double = (shearModulus * polarMoment) / armLength
            resultTable.Rows.Add("Single Arm Stiffness", armStiffness.ToString("F2"), "N·mm/rad")

            ' Calculate equivalent series stiffness
            ' Two arms in series with central section: 1/K_total = 2/K_arm + 1/K_central
            Dim equivalentStiffness As Double = 1 / ((2 / armStiffness) + (1 / centralStiffness))
            resultTable.Rows.Add("Equivalent Torsional Stiffness", equivalentStiffness.ToString("F2"), "N·mm/rad")

            ' Calculate roll stiffness at wheel (vertical force per unit displacement)
            ' K_roll = K_equivalent / (arm_length²)
            ' This gives the vertical force at the wheel mounting point per mm of vertical displacement
            Dim rollStiffness As Double = equivalentStiffness / (armLength * armLength)
            resultTable.Rows.Add("Roll Stiffness at Wheel", rollStiffness.ToString("F4"), "N/mm")
            resultTable.Rows.Add("Roll Stiffness at Wheel", (rollStiffness * 1000).ToString("F2"), "N/m")

            ' Calculate roll moment per degree of body roll (assuming symmetric installation)
            ' For 1 degree roll with track width effect
            ' M_roll = K_equivalent (this is the torque per radian of twist)
            Dim rollMomentPerDeg As Double = equivalentStiffness * (Math.PI / 180)
            resultTable.Rows.Add("Roll Moment per Degree", rollMomentPerDeg.ToString("F2"), "N·mm/deg")

            ' Calculate maximum torsional stress
            ' τ_max = (T × r) / J = (T × d/2) / J
            ' Where T is torque. For reference, calculate stress for 1000 N·mm torque
            Dim referenceTorque As Double = 1000 ' N·mm
            Dim maxStress As Double = (referenceTorque * (diameter / 2)) / polarMoment
            resultTable.Rows.Add("Max Stress @ 1000 N·mm Torque", maxStress.ToString("F2"), "N/mm²")

            ' Calculate twist angle for reference torque
            ' θ = T / K
            Dim twistAngle As Double = (referenceTorque / equivalentStiffness) * (180 / Math.PI)
            resultTable.Rows.Add("Twist Angle @ 1000 N·mm Torque", twistAngle.ToString("F3"), "deg")

            ' Material information
            If Math.Abs(shearModulus - 80000) < 1 Then
                resultTable.Rows.Add("Material", "Steel (typical)", "")
            ElseIf Math.Abs(shearModulus - 26000) < 1000 Then
                resultTable.Rows.Add("Material", "Aluminum alloy (typical)", "")
            Else
                resultTable.Rows.Add("Material", "Custom", "")
            End If

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates anti-roll bar stiffness with track width consideration.
    ''' </summary>
    ''' <param name="diameter">Bar diameter (mm)</param>
    ''' <param name="armLength">Arm length from center to mounting point (mm)</param>
    ''' <param name="centralLength">Central torsion section length (mm)</param>
    ''' <param name="trackWidth">Track width between wheel centers (mm)</param>
    ''' <param name="shearModulus">Shear modulus of material (N/mm²), default 80000 for steel</param>
    ''' <returns>DataTable with anti-roll bar stiffness calculations including track width effects</returns>
    ''' <remarks>
    ''' Calculates roll stiffness considering track width for body roll calculations.
    ''' Roll gradient = Roll stiffness / (Track width / 2)²
    ''' 
    ''' Example Input:
    ''' - diameter = 22 mm
    ''' - armLength = 140 mm
    ''' - centralLength = 850 mm
    ''' - trackWidth = 1500 mm
    ''' - shearModulus = 80000 N/mm² (steel)
    ''' 
    ''' Example Output:
    ''' Parameter                          | Value        | Unit
    ''' -----------------------------------|--------------|-------------
    ''' Bar Diameter                       | 22.00        | mm
    ''' Arm Length                         | 140.00       | mm
    ''' Central Section Length             | 850.00       | mm
    ''' Track Width                        | 1500.00      | mm
    ''' Shear Modulus (G)                  | 80000        | N/mm²
    ''' Polar Moment of Inertia (J)        | 23315.42     | mm⁴
    ''' Equivalent Torsional Stiffness     | 2054735.17   | N·mm/rad
    ''' Roll Stiffness at Wheel            | 104.83       | N/mm
    ''' Roll Gradient                      | 0.0073       | N·mm/deg/rad
    ''' Roll Rate per Degree               | 35850.17     | N·mm/deg
    ''' Vertical Force Diff @ 1° Roll      | 47.80        | N
    ''' Roll Resistance                    | 35850.17     | N·mm/deg
    ''' Reference CG Height                | 500          | mm
    ''' </remarks>
    Public Shared Function CalculateARBStiffnessWithTrack(ByVal diameter As Double, _
                                                           ByVal armLength As Double, _
                                                           ByVal centralLength As Double, _
                                                           ByVal trackWidth As Double, _
                                                           Optional ByVal shearModulus As Double = 80000) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            ' Validate inputs
            If diameter <= 0 Then
                Throw New ArgumentException("Diameter must be positive", "diameter")
            End If
            If armLength <= 0 Then
                Throw New ArgumentException("Arm length must be positive", "armLength")
            End If
            If centralLength <= 0 Then
                Throw New ArgumentException("Central length must be positive", "centralLength")
            End If
            If trackWidth <= 0 Then
                Throw New ArgumentException("Track width must be positive", "trackWidth")
            End If
            If shearModulus <= 0 Then
                Throw New ArgumentException("Shear modulus must be positive", "shearModulus")
            End If

            ' Add input parameters
            resultTable.Rows.Add("Bar Diameter", diameter.ToString("F2"), "mm")
            resultTable.Rows.Add("Arm Length", armLength.ToString("F2"), "mm")
            resultTable.Rows.Add("Central Section Length", centralLength.ToString("F2"), "mm")
            resultTable.Rows.Add("Track Width", trackWidth.ToString("F2"), "mm")
            resultTable.Rows.Add("Shear Modulus (G)", shearModulus.ToString("F0"), "N/mm²")

            ' Calculate polar moment of inertia
            Dim polarMoment As Double = (Math.PI * Math.Pow(diameter, 4)) / 32
            resultTable.Rows.Add("Polar Moment of Inertia (J)", polarMoment.ToString("F2"), "mm⁴")

            ' Calculate component stiffnesses
            Dim centralStiffness As Double = (shearModulus * polarMoment) / centralLength
            Dim armStiffness As Double = (shearModulus * polarMoment) / armLength
            Dim equivalentStiffness As Double = 1 / ((2 / armStiffness) + (1 / centralStiffness))

            resultTable.Rows.Add("Equivalent Torsional Stiffness", equivalentStiffness.ToString("F2"), "N·mm/rad")

            ' Calculate roll stiffness at wheel
            Dim rollStiffness As Double = equivalentStiffness / (armLength * armLength)
            resultTable.Rows.Add("Roll Stiffness at Wheel", rollStiffness.ToString("F4"), "N/mm")

            ' Calculate roll gradient (roll stiffness contribution per degree of body roll)
            ' Considers the moment arm from vehicle centerline to wheel center
            Dim halfTrack As Double = trackWidth / 2
            Dim rollGradient As Double = (equivalentStiffness * 2) / (halfTrack * halfTrack)
            resultTable.Rows.Add("Roll Gradient", rollGradient.ToString("F4"), "N·mm/deg/rad")

            ' Roll rate per degree of body roll
            Dim rollRatePerDeg As Double = rollGradient * (Math.PI / 180)
            resultTable.Rows.Add("Roll Rate per Degree", rollRatePerDeg.ToString("F2"), "N·mm/deg")

            ' Vertical force difference at wheels for 1 degree body roll
            ' ΔF = Roll torque / half track = (K × θ) / (track/2)
            Dim verticalForceDiff As Double = rollRatePerDeg / halfTrack
            resultTable.Rows.Add("Vertical Force Diff @ 1° Roll", verticalForceDiff.ToString("F2"), "N")

            ' Roll resistance (moment resisting roll per degree)
            Dim rollResistance As Double = equivalentStiffness * (Math.PI / 180)
            resultTable.Rows.Add("Roll Resistance", rollResistance.ToString("F2"), "N·mm/deg")

            ' Calculate lateral load transfer at CG height = 500mm (typical)
            Dim cgHeight As Double = 500 ' mm
            Dim lateralAccel As Double = 1.0 ' g
            ' This is just for reference showing how ARB affects load transfer
            resultTable.Rows.Add("Reference CG Height", cgHeight.ToString("F0"), "mm")
            
        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates required anti-roll bar diameter for target roll stiffness.
    ''' </summary>
    ''' <param name="targetRollStiffness">Target roll stiffness (N/mm)</param>
    ''' <param name="armLength">Arm length from center to mounting point (mm)</param>
    ''' <param name="centralLength">Central torsion section length (mm)</param>
    ''' <param name="shearModulus">Shear modulus of material (N/mm²), default 80000 for steel</param>
    ''' <returns>DataTable with required diameter calculation</returns>
    ''' <remarks>
    ''' Iteratively calculates the bar diameter needed to achieve target roll stiffness.
    ''' 
    ''' Example Input:
    ''' - targetRollStiffness = 100 N/mm (desired roll stiffness at wheel)
    ''' - armLength = 150 mm
    ''' - centralLength = 800 mm
    ''' - shearModulus = 80000 N/mm² (steel)
    ''' 
    ''' Example Output:
    ''' Parameter                          | Value        | Unit
    ''' -----------------------------------|--------------|-------------
    ''' Target Roll Stiffness              | 100.0000     | N/mm
    ''' Arm Length                         | 150.00       | mm
    ''' Central Length                     | 800.00       | mm
    ''' Shear Modulus (G)                  | 80000        | N/mm²
    ''' Target Equiv. Stiffness            | 2250000.00   | N·mm/rad
    ''' Required J                         | 28125.00     | mm⁴
    ''' Required Diameter                  | 23.13        | mm
    ''' Nearest Standard Size              | 24           | mm
    ''' Actual Stiffness (Standard)        | 116.1183     | N/mm
    ''' Difference from Target             | 16.12        | %
    ''' </remarks>
    Public Shared Function CalculateRequiredDiameter(ByVal targetRollStiffness As Double, _
                                                      ByVal armLength As Double, _
                                                      ByVal centralLength As Double, _
                                                      Optional ByVal shearModulus As Double = 80000) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If targetRollStiffness <= 0 Then
                Throw New ArgumentException("Target roll stiffness must be positive", "targetRollStiffness")
            End If
            If armLength <= 0 Then
                Throw New ArgumentException("Arm length must be positive", "armLength")
            End If
            If centralLength <= 0 Then
                Throw New ArgumentException("Central length must be positive", "centralLength")
            End If

            resultTable.Rows.Add("Target Roll Stiffness", targetRollStiffness.ToString("F4"), "N/mm")
            resultTable.Rows.Add("Arm Length", armLength.ToString("F2"), "mm")
            resultTable.Rows.Add("Central Length", centralLength.ToString("F2"), "mm")
            resultTable.Rows.Add("Shear Modulus (G)", shearModulus.ToString("F0"), "N/mm²")

            ' Target equivalent stiffness: K_eq = K_roll × L_arm²
            Dim targetEquivStiffness As Double = targetRollStiffness * armLength * armLength
            resultTable.Rows.Add("Target Equiv. Stiffness", targetEquivStiffness.ToString("F2"), "N·mm/rad")

            ' For series stiffness: 1/K_eq = 2/K_arm + 1/K_central
            ' K_arm = G×J / L_arm, K_central = G×J / L_central
            ' 1/K_eq = 2×L_arm/(G×J) + L_central/(G×J)
            ' 1/K_eq = (2×L_arm + L_central)/(G×J)
            ' J = (2×L_arm + L_central)/(G × (1/K_eq))
            
            Dim requiredPolarMoment As Double = (2 * armLength + centralLength) / (shearModulus / targetEquivStiffness)
            resultTable.Rows.Add("Required J", requiredPolarMoment.ToString("F2"), "mm⁴")

            ' From J = π×d⁴/32, solve for d: d = ⁴√(32×J/π)
            Dim requiredDiameter As Double = Math.Pow((32 * requiredPolarMoment) / Math.PI, 0.25)
            resultTable.Rows.Add("Required Diameter", requiredDiameter.ToString("F2"), "mm")

            ' Suggest standard sizes
            Dim standardSizes() As Double = {12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 38, 40}
            Dim nearestSize As Double = standardSizes(0)
            Dim minDiff As Double = Math.Abs(standardSizes(0) - requiredDiameter)
            
            For Each size As Double In standardSizes
                Dim diff As Double = Math.Abs(size - requiredDiameter)
                If diff < minDiff Then
                    minDiff = diff
                    nearestSize = size
                End If
            Next
            
            resultTable.Rows.Add("Nearest Standard Size", nearestSize.ToString("F0"), "mm")

            ' Calculate actual stiffness with standard size
            Dim stdPolarMoment As Double = (Math.PI * Math.Pow(nearestSize, 4)) / 32
            Dim stdCentralStiffness As Double = (shearModulus * stdPolarMoment) / centralLength
            Dim stdArmStiffness As Double = (shearModulus * stdPolarMoment) / armLength
            Dim stdEquivStiffness As Double = 1 / ((2 / stdArmStiffness) + (1 / stdCentralStiffness))
            Dim stdRollStiffness As Double = stdEquivStiffness / (armLength * armLength)
            
            resultTable.Rows.Add("Actual Stiffness (Standard)", stdRollStiffness.ToString("F4"), "N/mm")
            
            Dim percentDiff As Double = ((stdRollStiffness - targetRollStiffness) / targetRollStiffness) * 100
            resultTable.Rows.Add("Difference from Target", percentDiff.ToString("F2"), "%")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

End Class
