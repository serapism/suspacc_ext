''' <summary>
''' Provides tyre and rim calculation functions for automotive applications.
''' All calculations follow standard tyre sizing conventions and ETRTO standards.
''' </summary>
Public Class TyreCalc

    ''' <summary>
    ''' Calculates the nominal design diameter of a tyre including rim width correction.
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm (e.g., "205")</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage (e.g., "55")</param>
    ''' <param name="RimSize">Rim diameter code (e.g., "R16")</param>
    ''' <param name="rimWidth">Rim width in inches (e.g., "7.0")</param>
    ''' <returns>Nominal design diameter in mm</returns>
    Public Shared Function NominalDesignDiameter(ByVal TyreWidth As String, ByVal AspectRatio As String, ByVal RimSize As String, ByVal rimWidth As String) As Double
        NominalDesignDiameter = ((CDbl(TyreWidth) * (CDbl(AspectRatio) / 100)) * 2) + (CDbl(RimSize.Remove(0, 1)) * 25.4) + RimWidthCorrection(TyreWidth, AspectRatio, rimWidth)
    End Function

    ''' <summary>
    ''' Calculates the rolling circumference of a tyre.
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage</param>
    ''' <param name="RimSize">Rim diameter code (e.g., "R16")</param>
    ''' <param name="rimWidth">Rim width in inches</param>
    ''' <returns>Rolling circumference in mm</returns>
    Public Shared Function RollingCircumference(ByVal TyreWidth As String, ByVal AspectRatio As String, ByVal RimSize As String, ByVal rimWidth As String) As Double
        RollingCircumference = ((CDbl(TyreWidth) * (CDbl(AspectRatio) / 100)) * 2) + (CDbl(RimSize.Remove(0, 1)) * 25.4) + RimWidthCorrection(TyreWidth, AspectRatio, rimWidth) * 3.05
    End Function

    ''' <summary>
    ''' Calculates the static loaded radius of a tyre (78% of unloaded radius).
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage</param>
    ''' <param name="RimSize">Rim diameter code (e.g., "R16")</param>
    ''' <param name="rimWidth">Rim width in inches</param>
    ''' <returns>Static loaded radius in mm</returns>
    Public Shared Function StaticLoadedRadius(ByVal TyreWidth As String, ByVal AspectRatio As String, ByVal RimSize As String, ByVal rimWidth As String) As Double
        Dim tempDR As Double = (CDbl(RimSize.Remove(0, 1)) * 25.4)
        StaticLoadedRadius = (tempDR / 2) + (0.78 * ((NominalDesignDiameter(TyreWidth, AspectRatio, RimSize, rimWidth) - tempDR) / 2))
    End Function

    ''' <summary>
    ''' Calculates the maximum diameter in service (104% of nominal diameter).
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage</param>
    ''' <param name="RimSize">Rim diameter code (e.g., "R16")</param>
    ''' <param name="rimWidth">Rim width in inches</param>
    ''' <returns>Maximum diameter in service in mm</returns>
    Public Shared Function MaxDiameterInService(ByVal TyreWidth As String, ByVal AspectRatio As String, ByVal RimSize As String, ByVal rimWidth As String) As Double
        MaxDiameterInService = Math.Round(Math.Round((CDbl(TyreWidth) * (CDbl(AspectRatio) / 100)) * 2 * 1.04, 0) + (CDbl(RimSize.Remove(0, 1)) * 25.4), 0) + RimWidthCorrection(TyreWidth, AspectRatio, rimWidth)
    End Function

    ''' <summary>
    ''' Calculates the rim width correction factor for diameter adjustments.
    ''' Applies 5mm correction per 0.5 inch deviation from standard rim width.
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage</param>
    ''' <param name="RimWidth">Actual rim width in inches</param>
    ''' <returns>Correction factor in mm</returns>
    Public Shared Function RimWidthCorrection(ByVal TyreWidth As String, ByVal AspectRatio As String, ByVal RimWidth As String) As Double
        Dim StdValue As Double = iCHASSIS.TyreCalc.CalcRimWidth(TyreWidth:=CDbl(TyreWidth), AspectRatio:=CDbl(AspectRatio))
        Dim factor As Double
        Try
            factor = (StdValue - CDbl(RimWidth)) / 0.5
        Catch ex As Exception
            factor = 0
        End Try

        RimWidthCorrection = 5 * factor
    End Function

    ''' <summary>
    ''' Converts rim width from inches to millimeters.
    ''' </summary>
    ''' <param name="RimWidth">Rim width in inches</param>
    ''' <returns>Rim width in mm</returns>
    Public Shared Function MeasuringRimWidth(ByVal RimWidth As String) As Double
        MeasuringRimWidth = (CDbl(RimWidth) * 25.4)
    End Function

    ''' <summary>
    ''' Converts rim diameter from rim size code to millimeters.
    ''' </summary>
    ''' <param name="RimSize">Rim diameter code (e.g., "R16")</param>
    ''' <returns>Rim diameter in mm</returns>
    Public Shared Function SpecifiedRimDiameter(ByVal RimSize As String) As Double
        SpecifiedRimDiameter = (CDbl(RimSize.Remove(0, 1)) * 25.4)
    End Function

    ''' <summary>
    ''' Calculates the maximum width in service (104% of design section width).
    ''' </summary>
    ''' <param name="DesignSectionWidth">Design section width in mm</param>
    ''' <returns>Maximum width in service in mm</returns>
    Public Shared Function MaxWidthInService(ByVal DesignSectionWidth As Double) As Double
        MaxWidthInService = Math.Round(1.04 * DesignSectionWidth, 0)
    End Function

    ''' <summary>
    ''' Calculates the design section width based on tyre specifications and rim width.
    ''' Accounts for rim width variance from theoretical width.
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage</param>
    ''' <param name="RimWidth">Rim width in inches</param>
    ''' <returns>Design section width in mm</returns>
    Public Shared Function DesignSectionWidth(ByVal TyreWidth As String, ByVal AspectRatio As String, ByVal RimWidth As String) As Double
        Dim TyreWidthDbl As Double = CDbl(TyreWidth)
        Dim AspectRatioDbl As Double = CDbl(AspectRatio)
        Dim RimWidthDbl As Double = CDbl(RimWidth) * 25.4

        Dim TheoreticalRimWidth As Double
        If AspectRatioDbl >= 50 Then
            TheoreticalRimWidth = 0.7 * TyreWidthDbl
        Else
            TheoreticalRimWidth = 0.85 * TyreWidthDbl
        End If

        Dim MeasuringRimWidth As Double
        If AspectRatioDbl >= 70 Then
            MeasuringRimWidth = 0.7
        ElseIf AspectRatioDbl >= 60 Then
            MeasuringRimWidth = 0.75
        ElseIf AspectRatioDbl > 49 Then
            MeasuringRimWidth = 0.8
        ElseIf AspectRatioDbl = 45 Then
            MeasuringRimWidth = 0.85
        ElseIf AspectRatioDbl > 29 Then
            MeasuringRimWidth = 0.9
        Else
            MeasuringRimWidth = 0.92
        End If

        DesignSectionWidth = Math.Round(TyreWidthDbl + (0.4 * (RimWidthDbl - TheoreticalRimWidth)), 0)
    End Function

    ''' <summary>
    ''' Generates a DataTable containing all calculated tyre parameters.
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage</param>
    ''' <param name="RimSize">Rim diameter code (e.g., "R16")</param>
    ''' <param name="RimWidth">Rim width in inches</param>
    ''' <param name="MaxInService">If True, uses max in-service values; otherwise uses design values</param>
    ''' <returns>DataTable with Parameter, Value, and Unit columns</returns>
    Public Shared Function PublishValue(ByVal TyreWidth As String, ByVal AspectRatio As String, ByVal RimSize As String, ByVal RimWidth As String, Optional ByVal MaxInService As Boolean = True) As DataTable
        Dim dt As New DataTable()
        dt.Columns.Add("Parameter", GetType(String))
        dt.Columns.Add("Value", GetType(String))
        dt.Columns.Add("Unit", GetType(String))

        Dim nomenclature As String
        Dim overallWidth As Double
        Dim overallDiameter As Double

        If MaxInService = True Then
            overallWidth = MaxWidthInService(DesignSectionWidth(TyreWidth, AspectRatio, RimWidth))
            overallDiameter = MaxDiameterInService(TyreWidth, AspectRatio, RimSize, RimWidth)
            nomenclature = "TYRE " & TyreWidth & "-" & AspectRatio & " " & RimSize & " " & RimWidth.Replace(".", ",") & "J MAX IN SERVICE"
        Else
            overallWidth = DesignSectionWidth(TyreWidth, AspectRatio, RimWidth)
            overallDiameter = NominalDesignDiameter(TyreWidth, AspectRatio, RimSize, RimWidth)
            nomenclature = "TYRE " & TyreWidth & "-" & AspectRatio & " " & RimSize & " " & RimWidth.Replace(".", ",") & "J DESIGN"
        End If

        dt.Rows.Add("Overall Width Max in Service", overallWidth.ToString(), "mm")
        dt.Rows.Add("Overall Diameter Max in Service", overallDiameter.ToString(), "mm")
        dt.Rows.Add("Nomenclature", nomenclature, "")
        dt.Rows.Add("S, Design section width on measuring rim", DesignSectionWidth(TyreWidth, AspectRatio, RimWidth).ToString(), "mm")
        dt.Rows.Add("dr, Specified Rim Diameter", (CDbl(RimSize.Remove(0, 1)) * 25.4).ToString(), "mm")
        dt.Rows.Add("A max, intended rim width + max tolerance", (CDbl(RimWidth) * 25.4).ToString(), "mm")
        dt.Rows.Add("Designation", TyreWidth & "/" & AspectRatio & " " & RimSize, "")
        dt.Rows.Add("Part Number", "TYRE " & TyreWidth & "-" & AspectRatio & " " & RimSize & " " & RimWidth.Replace(".", ",") & "J", "")
        dt.Rows.Add("Nominal aspect ratio (ar)", AspectRatio, "")
        dt.Rows.Add("Measuring Rim Width Code", RimWidth.Replace(".", ","), "")
        dt.Rows.Add("Intended / Applied Rim Width Code", RimWidth.Replace(".", ","), "")

        Return dt
    End Function

    ''' <summary>
    ''' Generates a DataTable containing all calculated rim/wheel parameters.
    ''' </summary>
    ''' <param name="RimSize">Rim diameter code (e.g., "R16")</param>
    ''' <param name="RimWidth">Rim width in inches</param>
    ''' <param name="WheelOffset">Wheel offset (ET) in mm</param>
    ''' <param name="PCD">Pitch circle diameter in mm</param>
    ''' <param name="NoOfLug">Number of lug holes</param>
    ''' <returns>DataTable with Parameter, Value, and Unit columns</returns>
    Public Shared Function PublishRimValue(ByVal RimSize As String, ByVal RimWidth As String, ByVal WheelOffset As String, ByVal PCD As String, ByVal NoOfLug As String) As DataTable
        Dim dt As New DataTable()
        dt.Columns.Add("Parameter", GetType(String))
        dt.Columns.Add("Value", GetType(String))
        dt.Columns.Add("Unit", GetType(String))

        Dim specifiedRimDiameter As Double = CDbl(RimSize.Remove(0, 1)) * 25.4
        Dim intendedRimWidth As Double = CDbl(RimWidth) * 25.4
        Dim angleForHole As Double = 360 / CDbl(NoOfLug)
        Dim nomenclature As String = "WHEEL-ALUMINIUM " & RimSize & "X" & RimWidth.Replace(".", ",") & "J ET" & WheelOffset
        Dim partNumber As String = "WHEEL-ALUMINIUM " & RimSize & "X" & RimWidth.Replace(".", ",") & "J ET" & WheelOffset

        dt.Rows.Add("dr, Specified Rim Diameter", specifiedRimDiameter.ToString(), "mm")
        dt.Rows.Add("A", intendedRimWidth.ToString(), "mm")
        dt.Rows.Add("Part Number", partNumber, "")
        dt.Rows.Add("Nomenclature", nomenclature, "")
        dt.Rows.Add("Measuring Rim Width Code", RimWidth.Replace(".", ","), "")
        dt.Rows.Add("Offset, Wheel", CDbl(WheelOffset).ToString(), "mm")
        dt.Rows.Add("Pcd", CDbl(PCD).ToString(), "mm")
        dt.Rows.Add("Number of Lug Hole", CDbl(NoOfLug).ToString(), "")
        dt.Rows.Add("Angle for Hole", angleForHole.ToString(), "deg")
        dt.Rows.Add("E", "21", "mm")
        dt.Rows.Add("Dh", specifiedRimDiameter.ToString(), "mm")

        Return dt
    End Function

    ''' <summary>
    ''' Calculates the standard measuring rim width for a given tyre specification.
    ''' Based on ETRTO standards for aspect ratio to rim width ratios.
    ''' </summary>
    ''' <param name="TyreWidth">Nominal section width in mm</param>
    ''' <param name="AspectRatio">Aspect ratio as percentage</param>
    ''' <returns>Standard rim width in inches</returns>
    Public Shared Function CalcRimWidth(ByVal TyreWidth As Double, ByVal AspectRatio As Double) As Double
        Dim TheoreticalRimWidth As Double
        If AspectRatio >= 50 Then
            TheoreticalRimWidth = 0.7 * TyreWidth
        Else
            TheoreticalRimWidth = 0.85 * TyreWidth
        End If

        Dim MeasuringRimWidth As Double
        If AspectRatio >= 70 Then
            MeasuringRimWidth = 0.7
        ElseIf AspectRatio >= 60 Then
            MeasuringRimWidth = 0.75
        ElseIf AspectRatio > 49 Then
            MeasuringRimWidth = 0.8
        ElseIf AspectRatio = 45 Then
            MeasuringRimWidth = 0.85
        ElseIf AspectRatio > 29 Then
            MeasuringRimWidth = 0.9
        Else
            MeasuringRimWidth = 0.92
        End If

        Dim temp As Double = CInt(((MeasuringRimWidth * TyreWidth) / 25.4) / 0.5) * 0.5
        CalcRimWidth = Math.Round(CDbl(Math.Round(temp, 1)), 1)
    End Function
End Class
