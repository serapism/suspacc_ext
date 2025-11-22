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

    ''' <summary>
    ''' Performs anti-roll bar design validation and geometry checks.
    ''' </summary>
    ''' <param name="hardpointsTable">DataTable containing hardpoint coordinates with columns: PointName, X, Y, Z</param>
    ''' <returns>DataTable with design check results and recommendations</returns>
    ''' <remarks>
    ''' Required hardpoints:
    ''' - droplink_to_mount: Upper droplink mounting point
    ''' - droplink_to_arb: Lower droplink to ARB connection point
    ''' - arb_bush: ARB bushing mounting point
    ''' - wheel_ctr: Wheel center point
    ''' 
    ''' Validates:
    ''' - Droplink angles (should be within 5° of vertical)
    ''' - ARB arm length (recommended 240-260mm)
    ''' - Load transfer efficiency (target >99.25%)
    ''' - Geometry optimization recommendations
    ''' </remarks>
    Public Shared Function DesignCheck(hardpointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))
        resultTable.Columns.Add("Status", GetType(String))

        Try
            ' Validate input table structure
            If hardpointsTable Is Nothing Then
                Throw New ArgumentNullException("hardpointsTable", "Input DataTable cannot be null")
            End If

            If Not (hardpointsTable.Columns.Contains("PointName") AndAlso _
                    hardpointsTable.Columns.Contains("X") AndAlso _
                    hardpointsTable.Columns.Contains("Y") AndAlso _
                    hardpointsTable.Columns.Contains("Z")) Then
                Throw New ArgumentException("DataTable must contain columns: PointName, X, Y, Z")
            End If

            ' Validate required hardpoints exist
            Dim requiredPoints As String() = {"droplink_to_mount", "droplink_to_arb", "arb_bush", "wheel_ctr"}
            For Each pointName As String In requiredPoints
                Dim rows() As DataRow = hardpointsTable.Select($"PointName = '{pointName}'")
                If rows.Length = 0 Then
                    Throw New ArgumentException($"Required hardpoint '{pointName}' is missing from DataTable")
                End If
                
                ' Validate coordinates are numeric
                Dim row As DataRow = rows(0)
                Dim x, y, z As Double
                If Not (Double.TryParse(row("X").ToString(), x) AndAlso _
                        Double.TryParse(row("Y").ToString(), y) AndAlso _
                        Double.TryParse(row("Z").ToString(), z)) Then
                    Throw New ArgumentException($"Coordinates for point '{pointName}' must be numeric")
                End If
            Next

            ' Add header information
            resultTable.Rows.Add("Design Check Report", "Anti-Roll Bar Geometry Validation", "", "INFO")
            resultTable.Rows.Add("Chart Version", hardpointsTable.TableName, "", "INFO")
            resultTable.Rows.Add("Check Date", Date.Today.ToString("yyyy-MM-dd"), "", "INFO")
            resultTable.Rows.Add("", "", "", "")

            ' Extract hardpoint coordinates
            Dim droplinkMount As DataRow = hardpointsTable.Select("PointName = 'droplink_to_mount'")(0)
            Dim droplinkARB As DataRow = hardpointsTable.Select("PointName = 'droplink_to_arb'")(0)
            Dim arbBush As DataRow = hardpointsTable.Select("PointName = 'arb_bush'")(0)
            Dim wheelCenter As DataRow = hardpointsTable.Select("PointName = 'wheel_ctr'")(0)

            Dim ptDroplinkMount As Double() = {CDbl(droplinkMount("X")), CDbl(droplinkMount("Y")), CDbl(droplinkMount("Z"))}
            Dim ptDroplinkARB As Double() = {CDbl(droplinkARB("X")), CDbl(droplinkARB("Y")), CDbl(droplinkARB("Z"))}
            Dim ptARBBush As Double() = {CDbl(arbBush("X")), CDbl(arbBush("Y")), CDbl(arbBush("Z"))}
            Dim ptWheelCenter As Double() = {CDbl(wheelCenter("X")), CDbl(wheelCenter("Y")), CDbl(wheelCenter("Z"))}

            ' Calculate droplink length
            Dim droplinkLength As Double = Math.Sqrt( _
                Math.Pow(ptDroplinkMount(0) - ptDroplinkARB(0), 2) + _
                Math.Pow(ptDroplinkMount(1) - ptDroplinkARB(1), 2) + _
                Math.Pow(ptDroplinkMount(2) - ptDroplinkARB(2), 2))
            resultTable.Rows.Add("Droplink Length", droplinkLength.ToString("F2"), "mm", "MEASURED")

            ' Calculate droplink 3D angle from vertical
            Dim verticalRef As Double() = {ptDroplinkARB(0), ptDroplinkARB(1), ptDroplinkMount(2) - 100}
            If ptDroplinkMount(2) > ptDroplinkARB(2) Then
                verticalRef = {ptDroplinkMount(0), ptDroplinkMount(1), ptDroplinkMount(2) - 100}
            End If

            Dim droplink3DAngle As Double = CalculateAngleBetween3Points(ptDroplinkMount, ptDroplinkARB, verticalRef)
            Dim angleStatus As String = If(droplink3DAngle > 5, "WARNING", "OK")
            resultTable.Rows.Add("Droplink 3D Angle", droplink3DAngle.ToString("F2"), "deg", angleStatus)
            
            If droplink3DAngle > 5 Then
                resultTable.Rows.Add("Recommendation", "Angle deviation exceeds 5°. Review droplink geometry", "", "WARNING")
            End If

            ' Calculate 2D projections (XZ plane, Y=0)
            Dim ptDroplinkMount2D As Double() = {ptDroplinkMount(0), ptDroplinkMount(2)}
            Dim ptDroplinkARB2D As Double() = {ptDroplinkARB(0), ptDroplinkARB(2)}
            Dim ptARBBush2D As Double() = {ptARBBush(0), ptARBBush(2)}

            ' Calculate droplink angle to vertical in 2D
            Dim deltaZ As Double = ptDroplinkMount2D(1) - ptDroplinkARB2D(1)
            Dim deltaX As Double = ptDroplinkMount2D(0) - ptDroplinkARB2D(0)
            Dim droplinkAngle2D As Double = Math.Abs(Math.Atan2(deltaX, deltaZ) * (180 / Math.PI))
            resultTable.Rows.Add("Droplink Angle (2D Vertical)", droplinkAngle2D.ToString("F2"), "deg", "MEASURED")

            ' Calculate optimized droplink mount position (perpendicular to ARB arm)
            Dim arbArmVectorX As Double = ptDroplinkARB2D(0) - ptARBBush2D(0)
            Dim arbArmVectorZ As Double = ptDroplinkARB2D(1) - ptARBBush2D(1)
            Dim perpVectorX As Double = -arbArmVectorZ
            Dim perpVectorZ As Double = arbArmVectorX
            Dim perpLength As Double = Math.Sqrt(perpVectorX * perpVectorX + perpVectorZ * perpVectorZ)
            Dim optimalMountX As Double = ptDroplinkARB2D(0) + (perpVectorX / perpLength) * 100
            Dim optimalMountZ As Double = ptDroplinkARB2D(1) + (perpVectorZ / perpLength) * 100
            Dim ptOptimalMount2D As Double() = {optimalMountX, optimalMountZ}

            Dim optimalAngle As Double = Math.Abs(Math.Atan2((optimalMountX - ptDroplinkARB2D(0)), (optimalMountZ - ptDroplinkARB2D(1))) * (180 / Math.PI))
            resultTable.Rows.Add("Optimized Droplink Angle", optimalAngle.ToString("F2"), "deg", "OPTIMAL")

            Dim angleDelta As Double = Math.Abs(droplinkAngle2D - optimalAngle)
            Dim optimizationStatus As String = If(angleDelta > 5, "WARNING", "OK")
            resultTable.Rows.Add("Angle Delta (Actual vs Optimal)", angleDelta.ToString("F2"), "deg", optimizationStatus)

            ' ARB arm geometry
            resultTable.Rows.Add("", "", "", "")
            resultTable.Rows.Add("ARB Arm Geometry", "Analysis", "", "SECTION")
            
            Dim armLength As Double = Math.Sqrt( _
                Math.Pow(ptARBBush2D(0) - ptDroplinkARB2D(0), 2) + _
                Math.Pow(ptARBBush2D(1) - ptDroplinkARB2D(1), 2))
            Dim armStatus As String = If(armLength >= 240 AndAlso armLength <= 260, "OK", "INFO")
            resultTable.Rows.Add("ARB Arm Length", armLength.ToString("F1"), "mm", armStatus)
            resultTable.Rows.Add("Recommended Range", "240 - 260", "mm", "GUIDELINE")

            Dim armAngle As Double = Math.Abs(Math.Atan2(ptDroplinkARB2D(1) - ptARBBush2D(1), ptDroplinkARB2D(0) - ptARBBush2D(0)) * (180 / Math.PI))
            resultTable.Rows.Add("ARB Arm Angle (Horizontal)", armAngle.ToString("F1"), "deg", "MEASURED")

            ' Span lengths
            Dim bushSpan As Double = Math.Abs(ptARBBush(1) * 2)
            Dim endToEndSpan As Double = Math.Abs(ptDroplinkARB(1) * 2)
            resultTable.Rows.Add("ARB Bush Span Length", bushSpan.ToString("F1"), "mm", "MEASURED")
            resultTable.Rows.Add("ARB End-to-End Span", endToEndSpan.ToString("F1"), "mm", "MEASURED")

            ' Load transfer efficiency
            resultTable.Rows.Add("", "", "", "")
            resultTable.Rows.Add("Load Transfer Efficiency", "Analysis", "", "SECTION")
            
            Dim loadTransferMount As Double = Math.Cos(droplinkAngle2D * Math.PI / 180)
            Dim loadTransferARB As Double = Math.Cos(angleDelta * Math.PI / 180)
            Dim totalEfficiency As Double = loadTransferMount * loadTransferARB * 100
            
            resultTable.Rows.Add("Efficiency Droplink to Mount", (loadTransferMount * 100).ToString("F2"), "%", "CALCULATED")
            resultTable.Rows.Add("Efficiency Droplink to ARB", (loadTransferARB * 100).ToString("F2"), "%", "CALCULATED")
            
            Dim efficiencyStatus As String = If(totalEfficiency >= 99.25, "OK", "WARNING")
            resultTable.Rows.Add("Total Load Transfer Efficiency", totalEfficiency.ToString("F2"), "%", efficiencyStatus)
            resultTable.Rows.Add("Target Efficiency", ">= 99.25", "%", "GUIDELINE")

            ' ARB stiffness estimation (using default 32mm diameter)
            resultTable.Rows.Add("", "", "", "")
            resultTable.Rows.Add("Stiffness Estimation", "32mm Diameter Steel Bar", "", "SECTION")
            
            Dim shearModulus As Double = 80000 ' N/mm² for steel
            Dim diameter As Double = 32 ' mm
            Dim polarMoment As Double = (Math.PI * Math.Pow(diameter, 4)) / 32
            Dim centralStiffness As Double = (shearModulus * polarMoment) / bushSpan
            Dim armStiffness As Double = (shearModulus * polarMoment) / armLength
            Dim equivalentStiffness As Double = 1 / ((2 / armStiffness) + (1 / centralStiffness))
            Dim rollStiffness As Double = equivalentStiffness / (armLength * armLength)
            
            resultTable.Rows.Add("Estimated Roll Stiffness", rollStiffness.ToString("F2"), "N/mm", "ESTIMATED")
            resultTable.Rows.Add("Shear Modulus (Steel)", shearModulus.ToString("F0"), "N/mm²", "ASSUMED")

            ' Track width
            Dim trackWidth As Double = Math.Abs(ptWheelCenter(1) * 2)
            resultTable.Rows.Add("Vehicle Track Width", trackWidth.ToString("F1"), "mm", "MEASURED")

            ' Summary
            resultTable.Rows.Add("", "", "", "")
            resultTable.Rows.Add("Design Check Summary", "Overall Status", "", "SUMMARY")
            
            Dim overallStatus As String = "OK"
            If droplink3DAngle > 5 OrElse angleDelta > 5 OrElse totalEfficiency < 99.25 Then
                overallStatus = "REVIEW REQUIRED"
            End If
            resultTable.Rows.Add("Overall Assessment", overallStatus, "", overallStatus)

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "", "ERROR")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates the angle between three 3D points.
    ''' </summary>
    Private Shared Function CalculateAngleBetween3Points(p1() As Double, p2() As Double, p3() As Double) As Double
        ' Vector from p2 to p1
        Dim v1() As Double = {p1(0) - p2(0), p1(1) - p2(1), p1(2) - p2(2)}
        ' Vector from p2 to p3
        Dim v2() As Double = {p3(0) - p2(0), p3(1) - p2(1), p3(2) - p2(2)}
        
        ' Dot product
        Dim dotProduct As Double = v1(0) * v2(0) + v1(1) * v2(1) + v1(2) * v2(2)
        
        ' Magnitudes
        Dim mag1 As Double = Math.Sqrt(v1(0) * v1(0) + v1(1) * v1(1) + v1(2) * v1(2))
        Dim mag2 As Double = Math.Sqrt(v2(0) * v2(0) + v2(1) * v2(1) + v2(2) * v2(2))
        
        ' Angle in radians, then convert to degrees
        Dim angleRad As Double = Math.Acos(dotProduct / (mag1 * mag2))
        Return angleRad * (180 / Math.PI)
    End Function

End Function

End Class
