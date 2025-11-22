''' <summary>
''' Provides spring calculation functions for helical compression springs.
''' Includes calculations for spring rate, stress, buckling, and dimensional parameters.
''' </summary>
''' <remarks>
''' Calculations based on ISO 11891:2012 - Hot formed helical compression springs — Technical specifications.
''' </remarks>
Public Class SpringCalc
    ''' <summary>
    ''' Standard gravity acceleration value in m/s²
    ''' </summary>
    Public Shared ReadOnly gValue As Double = 9.80665

    ''' <summary>
    ''' Calculates the number of active coils from spring properties.
    ''' </summary>
    ''' <param name="YoungModulus">Young's Modulus (E) in N/mm²</param>
    ''' <param name="WireDiameter">Wire diameter (d) in mm</param>
    ''' <param name="CoilMeanDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="SpringRate">Spring rate (k) in N/mm</param>
    ''' <returns>Number of active coils</returns>
    Public Shared Function NumberOfActiveCoil(ByVal YoungModulus As Double, ByVal WireDiameter As Double, ByVal CoilMeanDiameter As Double, ByVal SpringRate As Double) As Double
        NumberOfActiveCoil = (YoungModulus * Math.Pow(WireDiameter, 4)) / (8 * Math.Pow(CoilMeanDiameter, 3) * SpringRate)
    End Function

    ''' <summary>
    ''' Calculates the required wire diameter from spring properties.
    ''' </summary>
    ''' <param name="YoungModulus">Young's Modulus (E) in N/mm²</param>
    ''' <param name="NumberOfActiveCoil">Number of active coils</param>
    ''' <param name="CoilMeanDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="SpringRate">Spring rate (k) in N/mm</param>
    ''' <returns>Wire diameter in mm</returns>
    Public Shared Function WireDiameter(ByVal YoungModulus As Double, ByVal NumberOfActiveCoil As Double, ByVal CoilMeanDiameter As Double, ByVal SpringRate As Double) As Double
        WireDiameter = RootN((NumberOfActiveCoil * (8 * Math.Pow(CoilMeanDiameter, 3) * SpringRate)) / YoungModulus, 4)
    End Function

    ''' <summary>
    ''' Calculates the spring rate using Young's Modulus.
    ''' </summary>
    ''' <param name="YoungModulus">Young's Modulus (E) in N/mm²</param>
    ''' <param name="NumberOfTotalCoil">Total number of coils</param>
    ''' <param name="CoilMeanDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="WireDiameter">Wire diameter (d) in mm</param>
    ''' <returns>Spring rate in N/mm</returns>
    Public Shared Function SpringRate3(ByVal YoungModulus As Double, ByVal NumberOfTotalCoil As Double, ByVal CoilMeanDiameter As Double, ByVal WireDiameter As Double) As Double
        SpringRate3 = (YoungModulus * Math.Pow(WireDiameter, 4)) / (8 * Math.Pow(CoilMeanDiameter, 3) * NumberOfTotalCoil)
    End Function

    ''' <summary>
    ''' Calculates the spring rate using Modulus of Rigidity (Shear Modulus).
    ''' </summary>
    ''' <param name="ModulusOfRigidity">Modulus of Rigidity (G) in N/mm²</param>
    ''' <param name="MeanCoilDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="WireDiameter">Wire diameter (d) in mm</param>
    ''' <param name="TotalNumberOfCoil">Total number of coils</param>
    ''' <returns>Spring rate in N/mm</returns>
    Public Shared Function SpringRate(ByVal ModulusOfRigidity As Double, ByVal MeanCoilDiameter As Double, ByVal WireDiameter As Double, ByVal TotalNumberOfCoil As Double) As Double
        SpringRate = (ModulusOfRigidity * Math.Pow(WireDiameter, 4)) / (8 * Math.Pow(MeanCoilDiameter, 3) * TotalNumberOfCoil)
    End Function

    ''' <summary>
    ''' Calculates the spring index (ratio of mean coil diameter to wire diameter).
    ''' Typical values range from 4 to 12.
    ''' </summary>
    ''' <param name="WireDiameter">Wire diameter (d) in mm</param>
    ''' <param name="CoilMeanDiameter">Mean coil diameter (D) in mm</param>
    ''' <returns>Spring index (C = D/d)</returns>
    Public Shared Function SpringIndex(ByVal WireDiameter As Double, ByVal CoilMeanDiameter As Double) As Double
        SpringIndex = CoilMeanDiameter / WireDiameter
    End Function

    ''' <summary>
    ''' Calculates the Wahl stress correction factor for curvature and direct shear effects.
    ''' </summary>
    ''' <param name="SpringIndex">Spring index (C = D/d)</param>
    ''' <returns>Wahl correction factor</returns>
    Public Shared Function WahlFactor(ByVal SpringIndex As Double) As Double
        WahlFactor = (((4 * SpringIndex) - 1) / ((4 * SpringIndex) - 4)) + (0.615 / SpringIndex)
    End Function

    ''' <summary>
    ''' Calculates the free height of the spring (unloaded length).
    ''' </summary>
    ''' <param name="DesignLoad">Design load in N</param>
    ''' <param name="SpringRate">Spring rate in N/mm</param>
    ''' <param name="DesignHeight">Design height (loaded height) in mm</param>
    ''' <returns>Free height in mm</returns>
    Public Shared Function FreeHeight(ByVal DesignLoad As Double, ByVal SpringRate As Double, ByVal DesignHeight As Double) As Double
        FreeHeight = (DesignLoad / SpringRate) + DesignHeight
    End Function

    ''' <summary>
    ''' Calculates the corrected torsional stress using the Wahl factor.
    ''' </summary>
    ''' <param name="CoilMeanDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="DesignLoad">Design load in N</param>
    ''' <param name="WireDiameter">Wire diameter (d) in mm</param>
    ''' <param name="WahlFactor">Wahl correction factor</param>
    ''' <returns>Corrected torsional stress in N/mm²</returns>
    Public Shared Function TorsionalStressCorrected(ByVal CoilMeanDiameter As Double, ByVal DesignLoad As Double, ByVal WireDiameter As Double, ByVal WahlFactor As Double) As Double
        TorsionalStressCorrected = TorsionalStress(CoilMeanDiameter, DesignLoad, WireDiameter) * WahlFactor
    End Function

    ''' <summary>
    ''' Calculates the uncorrected torsional stress in the spring wire.
    ''' </summary>
    ''' <param name="CoilMeanDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="DesignLoad">Design load in N</param>
    ''' <param name="WireDiameter">Wire diameter (d) in mm</param>
    ''' <returns>Torsional stress in N/mm²</returns>
    Public Shared Function TorsionalStress(ByVal CoilMeanDiameter As Double, ByVal DesignLoad As Double, ByVal WireDiameter As Double) As Double
        TorsionalStress = (8 * CoilMeanDiameter * DesignLoad) / (Math.PI * Math.Pow(WireDiameter, 3))
    End Function

    ''' <summary>
    ''' Calculates the Z-value (stress per unit load).
    ''' </summary>
    ''' <param name="CoilMeanDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="WahlFactor">Wahl correction factor</param>
    ''' <param name="WireDiameter">Wire diameter (d) in mm</param>
    ''' <returns>Z-value in 1/mm²</returns>
    Public Shared Function Zvalue(ByVal CoilMeanDiameter As Double, ByVal WahlFactor As Double, ByVal WireDiameter As Double) As Double
        Zvalue = (8 * CoilMeanDiameter * WahlFactor) / (Math.PI * Math.Pow(WireDiameter, 3))
    End Function

    ''' <summary>
    ''' Calculates the nth root of a number.
    ''' </summary>
    ''' <param name="Number">The number to find the root of</param>
    ''' <param name="Power">The root power (e.g., 2 for square root, 3 for cube root)</param>
    ''' <returns>The nth root of the number</returns>
    Public Shared Function RootN(ByVal Number As Double, ByVal Power As Double) As Double
        RootN = Math.Pow(Number, (1 / Power))
    End Function

    ''' <summary>
    ''' Calculates the optimum wire diameter for a given load and stress.
    ''' </summary>
    ''' <param name="MeanCoilDiameter">Mean coil diameter (D) in mm</param>
    ''' <param name="Load">Applied load in N</param>
    ''' <param name="Stress">Target stress in N/mm²</param>
    ''' <returns>Optimum wire diameter in mm</returns>
    Public Shared Function OptimumWireDiameter(ByVal MeanCoilDiameter As Double, ByVal Load As Double, ByVal Stress As Double) As Double
        OptimumWireDiameter = RootN((8 * Load * MeanCoilDiameter) / (Math.PI * Stress), 3)
    End Function

    ''' <summary>
    ''' Returns the number of end coils based on spring end condition.
    ''' </summary>
    ''' <param name="SpringEndCondition">Spring end condition type (e.g., "CLOSED GROUND", "OPEN NON GROUND")</param>
    ''' <returns>Number of end coils</returns>
    Public Shared Function NoOfEndCoil(ByVal SpringEndCondition As String) As Double
        If SpringEndCondition = "CLOSED NON-GROUND" Then
            NoOfEndCoil = 1.5
        ElseIf SpringEndCondition = "CLOSED GROUND" Then
            NoOfEndCoil = 1.5
        ElseIf SpringEndCondition = "CLOSED TAPERED" Then
            NoOfEndCoil = 1.5
        ElseIf SpringEndCondition = "OPEN NON GROUND" Then
            NoOfEndCoil = 2
        ElseIf SpringEndCondition = "OPEN GROUND" Then
            NoOfEndCoil = 2
        ElseIf SpringEndCondition = "OPEN TAPERED" Then
            NoOfEndCoil = 2
        ElseIf SpringEndCondition = "OPEN 3/4 TURN NON GROUND" Then
            NoOfEndCoil = 1.5
        ElseIf SpringEndCondition = "PROTON EXORA" Then
            NoOfEndCoil = 1.5
        End If
    End Function

    ''' <summary>
    ''' Calculates the minimum length of the spring assembly.
    ''' </summary>
    ''' <param name="SolidLength">Solid length (fully compressed) in mm</param>
    ''' <param name="SumOfMinimumGap">Sum of minimum gaps in mm</param>
    ''' <returns>Minimum length in mm</returns>
    Public Shared Function MinLength(ByVal SolidLength As Double, ByVal SumOfMinimumGap As Double) As Double
        MinLength = SolidLength + SumOfMinimumGap
    End Function

    ''' <summary>
    ''' Calculates the solid length (fully compressed length) based on end condition and manufacturing method.
    ''' </summary>
    ''' <param name="TotalNoOfCoil">Total number of coils</param>
    ''' <param name="WireDiameter">Wire diameter in mm</param>
    ''' <param name="SpringEndCondition">Spring end condition (e.g., "CLOSED GROUND", "OPEN NON GROUND")</param>
    ''' <param name="ManufacturingMethod">Manufacturing method ("COLD COILED" or "HOT COILED")</param>
    ''' <returns>Solid length in mm</returns>
    Public Shared Function SolidLength(ByVal TotalNoOfCoil As Double, ByVal WireDiameter As Double, ByVal SpringEndCondition As String, ByVal ManufacturingMethod As String) As Double
        If SpringEndCondition = "CLOSED NON-GROUND" And ManufacturingMethod = "COLD COILED" Then
            SolidLength = (TotalNoOfCoil + 1.5) * WireDiameter
        ElseIf SpringEndCondition = "CLOSED GROUND" And ManufacturingMethod = "COLD COILED" Then
            SolidLength = TotalNoOfCoil * WireDiameter
        ElseIf SpringEndCondition = "CLOSED GROUND" And ManufacturingMethod = "HOT COILED" Then
            SolidLength = (TotalNoOfCoil - 0.3) * WireDiameter
        ElseIf SpringEndCondition = "OPEN NON GROUND" And ManufacturingMethod = "HOT COILED" Then
            SolidLength = (TotalNoOfCoil + 1.1) * WireDiameter
        ElseIf SpringEndCondition = "OPEN 3/4 TURN NON GROUND" And ManufacturingMethod = "HOT COILED" Then
            SolidLength = (TotalNoOfCoil + 1.1) * WireDiameter
        Else
            SolidLength = 9999999999999
        End If
    End Function

    ''' <summary>
    ''' Calculates the maximum spring load at solid length.
    ''' </summary>
    ''' <param name="SpringRate">Spring rate in N/mm</param>
    ''' <param name="FreeHeight">Free height in mm</param>
    ''' <param name="SolidLength">Solid length in mm</param>
    ''' <returns>Maximum spring load in N</returns>
    Public Shared Function MaxSpringLoad(ByVal SpringRate As Double, ByVal FreeHeight As Double, ByVal SolidLength As Double) As Double
        MaxSpringLoad = SpringRate * (FreeHeight - SolidLength)
    End Function

    ''' <summary>
    ''' Calculates the ride frequency (natural frequency) of the suspension system.
    ''' </summary>
    ''' <param name="SpringRate">Spring rate in N/mm</param>
    ''' <param name="SuspensionRatio">Suspension motion ratio</param>
    ''' <param name="DesignLoad">Design load in N</param>
    ''' <returns>Ride frequency in Hz</returns>
    Public Shared Function RideFrequency(ByVal SpringRate As Double, ByVal SuspensionRatio As Double, ByVal DesignLoad As Double) As Double
        RideFrequency = Math.Sqrt((SpringRate * 1000) / (Math.Pow(SuspensionRatio, 2) * 4 * Math.Pow(Math.PI, 2) * (DesignLoad / 9.80665)))
    End Function

    ''' <summary>
    ''' Calculates the total length of wire required for the spring.
    ''' </summary>
    ''' <param name="CoilMeanDiameter">Mean coil diameter in mm</param>
    ''' <param name="DesignHeight">Design height in mm</param>
    ''' <param name="NumberOfActiveCoil">Number of active coils</param>
    ''' <param name="NumberOfTotalCoil">Total number of coils</param>
    ''' <returns>Wire length in mm</returns>
    Public Shared Function WireLength(ByVal CoilMeanDiameter As Double, ByVal DesignHeight As Double, ByVal NumberOfActiveCoil As Double, ByVal NumberOfTotalCoil As Double) As Double
        WireLength = NumberOfTotalCoil * Math.Pow((Math.Pow(CoilMeanDiameter * Math.PI, 2) + Math.Pow(DesignHeight / NumberOfActiveCoil, 2)), 0.5)
    End Function

    ''' <summary>
    ''' Checks if the spring will buckle under the maximum deflection.
    ''' </summary>
    ''' <param name="ModulusOfRigidity">Modulus of Rigidity (G) in N/mm²</param>
    ''' <param name="ModulusOfElasticity">Modulus of Elasticity (E) in N/mm²</param>
    ''' <param name="MeanCoilDiameter">Mean coil diameter in mm</param>
    ''' <param name="SeatingCoefficient">Seating coefficient (typically 0.5 for fixed ends, 1.0 for one end free)</param>
    ''' <param name="FreeHeight">Free height in mm</param>
    ''' <param name="MaximumDeflection">Maximum deflection in mm</param>
    ''' <returns>True if spring will not buckle, False if buckling will occur</returns>
    Public Shared Function checkBuckling(ByVal ModulusOfRigidity As Double, ByVal ModulusOfElasticity As Double, ByVal MeanCoilDiameter As Double, ByVal SeatingCoefficient As Double, ByVal FreeHeight As Double, ByVal MaximumDeflection As Double) As Boolean
        Dim EquationB As Double = FreeHeight * 0.5
        Dim EquationD As Double = 1 - (ModulusOfRigidity / ModulusOfElasticity)
        Dim EquationE As Double = 0.5 + (ModulusOfRigidity / ModulusOfElasticity)
        Dim EquationF As Double = Math.Pow((Math.PI * MeanCoilDiameter) / (SeatingCoefficient * FreeHeight), 2)
        Dim sk As Double = (EquationB / EquationD) * (1 - Math.Sqrt((EquationD * EquationF) / EquationE))

        If (sk / -MaximumDeflection) > 1 Then
            checkBuckling = True
        Else
            checkBuckling = False
        End If
    End Function
End Class
