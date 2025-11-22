''' <summary>
''' Provides torque and bolted joint calculation functions.
''' Includes basic torque calculations and VDI 2230 standard calculations for systematic design of highly stressed bolted joints.
''' </summary>
''' <remarks>
''' VDI 2230 calculations based on VDI 2230 Part 1 (2015) - Systematic calculation of highly stressed bolted joints.
''' </remarks>
Public Class TorqueCalc

    ''' <summary>
    ''' Calculates the stress area of a threaded fastener according to ISO 898-1.
    ''' </summary>
    ''' <param name="d2">Pitch diameter in mm</param>
    ''' <param name="d3">Minor diameter (core diameter) in mm</param>
    ''' <returns>Stress area in mm²</returns>
    ''' <remarks>Formula: As = (π/4) × ((d2 + d3)/2)²</remarks>
    Public Shared Function StressArea(ByVal d2 As Double, ByVal d3 As Double) As Double
        Dim dAvg As Double = (d2 + d3) / 2
        StressArea = (Math.PI / 4) * dAvg * dAvg
    End Function

    ''' <summary>
    ''' Calculates the required tightening torque using the general torque equation.
    ''' </summary>
    ''' <param name="LoadAxial">Axial preload force in N</param>
    ''' <param name="d2">Pitch diameter in mm</param>
    ''' <param name="d0">Bearing surface inner diameter in mm</param>
    ''' <param name="b0">Bearing surface outer diameter in mm</param>
    ''' <param name="u1">Thread friction coefficient (typically 0.12-0.18)</param>
    ''' <param name="u2">Head/nut bearing friction coefficient (typically 0.10-0.16)</param>
    ''' <param name="alpha">Thread flank angle in degrees (typically 30° for metric threads)</param>
    ''' <param name="P">Thread pitch in mm</param>
    ''' <returns>Tightening torque in Nm</returns>
    ''' <remarks>M = F × (P/(2π) + (μ_thread × d2)/(2×cos(α)) + μ_head × d_bearing/2)</remarks>
    Public Shared Function Torque1(ByVal LoadAxial As Double, _
                                   ByVal d2 As Double, _
                                   ByVal d0 As Double, _
                                   ByVal b0 As Double, _
                                   ByVal u1 As Double, _
                                   ByVal u2 As Double, _
                                   ByVal alpha As Double, _
                                   ByVal P As Double) As Double

        ' Thread torque component
        Dim threadTorque As Double = (P / (2 * Math.PI)) + (d2 * u1) / (2 * Math.Cos(alpha * Math.PI / 180))
        
        ' Head/nut bearing torque component (mean bearing diameter)
        Dim dKm As Double = (d0 + b0) / 2
        Dim headTorque As Double = u2 * dKm / 2
        
        ' Total torque in Nm (LoadAxial is in N, diameters in mm, result converted to Nm)
        Torque1 = LoadAxial * (threadTorque + headTorque) / 1000
    End Function

    ''' <summary>
    ''' Calculates the axial load from allowed stress and stress area.
    ''' </summary>
    ''' <param name="deltaAllowed">Allowed stress in MPa</param>
    ''' <param name="stressArea">Stress area in mm²</param>
    ''' <returns>Axial load in N</returns>
    Public Shared Function LoadAxial(ByVal deltaAllowed As Double, ByVal stressArea As Double) As Double
        LoadAxial = deltaAllowed * stressArea
    End Function

    ''' <summary>
    ''' Validates bolt strength using surface failure criteria.
    ''' </summary>
    Public Shared Function validateBolt(ByVal fclamp As Double, ByVal fx As Double, ByVal fy As Double, ByVal fz As Double, ByVal uts As Double, ByVal ys As Double, ByVal bolt_diameter As Double, ByVal uts_factor As Boolean, ByVal ys_factor As Boolean) As String

        Dim tensile_failure As Double
        Dim shear_failure As Double

        If uts_factor = True Then
            tensile_failure = Math.Pow((((fclamp + fz) * 4) / (Math.PI * bolt_diameter * bolt_diameter)) / uts, 2)
            shear_failure = Math.Pow(((Math.Sqrt((fx * fx) + (fy * fy))) * 4 / (Math.PI * bolt_diameter * bolt_diameter)) / (0.577 * uts), 2)
        Else
            tensile_failure = Math.Pow((((fclamp + fz) * 4) / (Math.PI * bolt_diameter * bolt_diameter)) / ys, 2)
            shear_failure = Math.Pow(((Math.Sqrt((fx * fx) + (fy * fy))) * 4 / (Math.PI * bolt_diameter * bolt_diameter)) / (0.577 * ys), 2)
        End If

        Dim answer As Double = tensile_failure + shear_failure
        Dim temp As String = "Surface Failure Criteria by iCat" & vbCrLf & vbCrLf & _
            "ForceX : " & fx & " N" & vbCrLf & _
            "ForceY : " & fy & " N" & vbCrLf & _
            "ForceZ : " & fz & " N" & vbCrLf & vbCrLf & _
            "Calculated Clamping Force : " & fclamp & " N" & vbCrLf & vbCrLf & _
            "Yield Strength/UTS : " & ys & "/" & uts & " MPa" & vbCrLf & _
            "Bolt Diameter : M" & bolt_diameter & " mm" & vbCrLf & vbCrLf & _
            "Tensile/Max Stress : " & Math.Round(tensile_failure, 3) & vbCrLf & _
            "Shear/Max Stress : " & Math.Round(shear_failure, 3) & vbCrLf & vbCrLf

        If answer > 1 Then
            temp = temp & "Surface Failure Criteria : NG"
        Else
            temp = temp & "Surface Failure Criteria : OK"
        End If

        Return temp
    End Function

    ''' <summary>
    ''' Calculates clamping force from torque using simplified formula.
    ''' </summary>
    ''' <param name="Torque">Applied torque in Nm</param>
    ''' <param name="Coef">Torque coefficient (typically 0.15-0.20)</param>
    ''' <param name="BoltSize">Nominal bolt diameter in mm</param>
    ''' <returns>Clamping force in N</returns>
    Public Shared Function CalculateClamping(ByVal Torque As Double, ByVal Coef As Double, ByVal BoltSize As Double) As Double
        CalculateClamping = Torque / (Coef * BoltSize * 0.001)
    End Function

#Region "VDI 2230 Standard Calculations"

    ''' <summary>
    ''' Calculates the resilience (compliance) of the bolt according to VDI 2230.
    ''' </summary>
    ''' <param name="lK">Clamped length in mm</param>
    ''' <param name="A">Cross-sectional area in mm²</param>
    ''' <param name="E">Modulus of elasticity in N/mm²</param>
    ''' <returns>Bolt resilience in mm/N</returns>
    Public Shared Function VDI_BoltResilience(ByVal lK As Double, ByVal A As Double, ByVal E As Double) As Double
        VDI_BoltResilience = lK / (A * E)
    End Function

    ''' <summary>
    ''' Calculates the resilience of clamped parts according to VDI 2230.
    ''' Uses the substitute area approach for complex geometries.
    ''' </summary>
    ''' <param name="lK">Clamped length in mm</param>
    ''' <param name="dW">Washer diameter or bearing surface diameter in mm</param>
    ''' <param name="dh">Hole diameter in mm</param>
    ''' <param name="E">Modulus of elasticity of clamped material in N/mm²</param>
    ''' <returns>Clamped parts resilience in mm/N</returns>
    Public Shared Function VDI_ClampedPartsResilience(ByVal lK As Double, ByVal dW As Double, ByVal dh As Double, ByVal E As Double) As Double
        Dim DA As Double = dW + lK * Math.Tan(33 * Math.PI / 180)
        VDI_ClampedPartsResilience = (lK / E) * Math.Log((DA * DA + dW * dW - dh * dh) / (DA * DA - dW * dW + dh * dh)) / (Math.PI * dW)
    End Function

    ''' <summary>
    ''' Calculates the load factor (load introduction factor) according to VDI 2230.
    ''' </summary>
    ''' <param name="deltaBolt">Bolt resilience in mm/N</param>
    ''' <param name="deltaClampedParts">Clamped parts resilience in mm/N</param>
    ''' <returns>Load factor Phi (dimensionless, 0-1)</returns>
    Public Shared Function VDI_LoadFactor(ByVal deltaBolt As Double, ByVal deltaClampedParts As Double) As Double
        VDI_LoadFactor = deltaBolt / (deltaBolt + deltaClampedParts)
    End Function

    ''' <summary>
    ''' Calculates the bolt force under working load according to VDI 2230.
    ''' </summary>
    ''' <param name="FV">Preload force in N</param>
    ''' <param name="FA">Working (operating) load in N</param>
    ''' <param name="Phi">Load factor (0-1)</param>
    ''' <returns>Bolt force under working load in N</returns>
    Public Shared Function VDI_BoltForceWorking(ByVal FV As Double, ByVal FA As Double, ByVal Phi As Double) As Double
        VDI_BoltForceWorking = FV + Phi * FA
    End Function

    ''' <summary>
    ''' Calculates the clamping force under working load according to VDI 2230.
    ''' </summary>
    ''' <param name="FV">Preload force in N</param>
    ''' <param name="FA">Working (operating) load in N</param>
    ''' <param name="Phi">Load factor (0-1)</param>
    ''' <returns>Clamping force under working load in N</returns>
    Public Shared Function VDI_ClampingForceWorking(ByVal FV As Double, ByVal FA As Double, ByVal Phi As Double) As Double
        VDI_ClampingForceWorking = FV - (1 - Phi) * FA
    End Function

    ''' <summary>
    ''' Calculates the assembly preload force according to VDI 2230.
    ''' </summary>
    ''' <param name="FMTab">Assembly preload from torque tables in N</param>
    ''' <param name="alphaA">Thermal expansion coefficient of bolt (1/K)</param>
    ''' <param name="alphaP">Thermal expansion coefficient of clamped parts (1/K)</param>
    ''' <param name="deltaT">Temperature change in K</param>
    ''' <param name="lK">Clamped length in mm</param>
    ''' <param name="deltaBolt">Bolt resilience in mm/N</param>
    ''' <param name="deltaClampedParts">Clamped parts resilience in mm/N</param>
    ''' <returns>Assembly preload force in N</returns>
    Public Shared Function VDI_AssemblyPreload(ByVal FMTab As Double, ByVal alphaA As Double, ByVal alphaP As Double, ByVal deltaT As Double, ByVal lK As Double, ByVal deltaBolt As Double, ByVal deltaClampedParts As Double) As Double
        Dim thermalEffect As Double = (alphaP - alphaA) * deltaT * lK / (deltaBolt + deltaClampedParts)
        VDI_AssemblyPreload = FMTab + thermalEffect
    End Function

    ''' <summary>
    ''' Calculates the tightening torque according to VDI 2230.
    ''' </summary>
    ''' <param name="FV">Target preload force in N</param>
    ''' <param name="d">Nominal bolt diameter in mm</param>
    ''' <param name="P">Thread pitch in mm</param>
    ''' <param name="d2">Pitch diameter in mm</param>
    ''' <param name="muG">Thread friction coefficient</param>
    ''' <param name="muK">Head/nut friction coefficient</param>
    ''' <param name="dKm">Mean bearing diameter in mm</param>
    ''' <returns>Tightening torque in Nm</returns>
    Public Shared Function VDI_TighteningTorque(ByVal FV As Double, ByVal d As Double, ByVal P As Double, ByVal d2 As Double, ByVal muG As Double, ByVal muK As Double, ByVal dKm As Double) As Double
        Dim threadTorque As Double = FV * d2 * 0.5 * ((P / (Math.PI * d2)) + (muG / Math.Cos(30 * Math.PI / 180)))
        Dim headTorque As Double = FV * muK * dKm * 0.5
        VDI_TighteningTorque = (threadTorque + headTorque) / 1000
    End Function

    ''' <summary>
    ''' Calculates the minimum required preload force according to VDI 2230.
    ''' </summary>
    ''' <param name="FA">Working (operating) load in N</param>
    ''' <param name="FZ">Additional external load in N</param>
    ''' <param name="Phi">Load factor (0-1)</param>
    ''' <param name="n">Number of interfaces</param>
    ''' <returns>Minimum required preload in N</returns>
    Public Shared Function VDI_MinimumPreload(ByVal FA As Double, ByVal FZ As Double, ByVal Phi As Double, ByVal n As Double) As Double
        VDI_MinimumPreload = (FA + FZ) / (n * (1 - Phi))
    End Function

    ''' <summary>
    ''' Calculates the stress in the bolt at the thread according to VDI 2230.
    ''' </summary>
    ''' <param name="FSB">Bolt force in N</param>
    ''' <param name="AS">Stress area in mm²</param>
    ''' <returns>Bolt stress in N/mm² (MPa)</returns>
    Public Shared Function VDI_BoltStress(ByVal FSB As Double, ByVal AS As Double) As Double
        VDI_BoltStress = FSB / AS
    End Function

    ''' <summary>
    ''' Calculates the utilization factor (safety factor) according to VDI 2230.
    ''' </summary>
    ''' <param name="sigmaBolt">Actual bolt stress in MPa</param>
    ''' <param name="Rp02">Yield strength (0.2% proof stress) in MPa</param>
    ''' <returns>Utilization factor (should be less than 0.9 for static loads)</returns>
    Public Shared Function VDI_UtilizationFactor(ByVal sigmaBolt As Double, ByVal Rp02 As Double) As Double
        VDI_UtilizationFactor = sigmaBolt / Rp02
    End Function

    ''' <summary>
    ''' Calculates the eccentric loading factor according to VDI 2230.
    ''' </summary>
    ''' <param name="n">Exponent based on load type (n=1 for pressure, n=4-8 for bending)</param>
    ''' <param name="dA">Outer diameter of load introduction in mm</param>
    ''' <param name="dW">Washer/bearing diameter in mm</param>
    ''' <returns>Eccentric loading factor Phi_n</returns>
    Public Shared Function VDI_EccentricLoadingFactor(ByVal n As Double, ByVal dA As Double, ByVal dW As Double) As Double
        VDI_EccentricLoadingFactor = 1 - Math.Pow(dW / dA, n)
    End Function

    ''' <summary>
    ''' Calculates the embedding/settling loss according to VDI 2230.
    ''' </summary>
    ''' <param name="fZ">Embedding factor (typically 3-5 µm for fine machined surfaces)</param>
    ''' <param name="deltaBolt">Bolt resilience in mm/N</param>
    ''' <param name="deltaClampedParts">Clamped parts resilience in mm/N</param>
    ''' <returns>Preload loss due to embedding in N</returns>
    Public Shared Function VDI_EmbeddingLoss(ByVal fZ As Double, ByVal deltaBolt As Double, ByVal deltaClampedParts As Double) As Double
        VDI_EmbeddingLoss = fZ / (deltaBolt + deltaClampedParts)
    End Function

    ''' <summary>
    ''' Calculates the prevailing torque for locking elements according to VDI 2230.
    ''' </summary>
    ''' <param name="MGF">Prevailing torque moment in Nm</param>
    ''' <param name="MA">Assembly torque in Nm</param>
    ''' <returns>Effective preload torque in Nm</returns>
    Public Shared Function VDI_EffectivePreloadTorque(ByVal MGF As Double, ByVal MA As Double) As Double
        VDI_EffectivePreloadTorque = MA - MGF
    End Function

#End Region

End Class