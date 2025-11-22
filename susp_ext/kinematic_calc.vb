''' <summary>
''' Provides suspension kinematics calculation functions.
''' Includes calculations for camber, caster, toe, and suspension geometry.
''' </summary>
Public Class KinematicCalc

    ''' <summary>
    ''' Calculates the camber angle from a DataTable containing two points with X, Y, Z coordinates.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Top point, Row 1 = Bottom point.
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 2 rows containing X, Y, Z coordinates</param>
    ''' <returns>Camber angle in degrees (positive = top leans outward)</returns>
    ''' <remarks>Uses Y (vertical) and Z (lateral) coordinates for camber calculation</remarks>
    Public Shared Function CalculateCamberFromDataTable(ByVal pointsTable As DataTable) As Double
        If pointsTable Is Nothing Then
            Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
        End If

        If pointsTable.Rows.Count < 2 Then
            Throw New ArgumentException("DataTable must contain at least 2 rows (top and bottom points)", "pointsTable")
        End If

        ' Check for required columns (case-insensitive)
        Dim hasX As Boolean = False
        Dim hasY As Boolean = False
        Dim hasZ As Boolean = False
        
        For Each col As DataColumn In pointsTable.Columns
            Dim colName As String = col.ColumnName.ToUpper()
            If colName = "X" Then hasX = True
            If colName = "Y" Then hasY = True
            If colName = "Z" Then hasZ = True
        Next

        If Not (hasX And hasY And hasZ) Then
            Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
        End If

        ' Get coordinates from first two rows
        Dim topY As Double = CDbl(pointsTable.Rows(0)("Y"))
        Dim topZ As Double = CDbl(pointsTable.Rows(0)("Z"))
        Dim bottomY As Double = CDbl(pointsTable.Rows(1)("Y"))
        Dim bottomZ As Double = CDbl(pointsTable.Rows(1)("Z"))

        ' Calculate camber using vertical (Y) and lateral (Z) components
        Dim deltaZ As Double = topZ - bottomZ
        Dim deltaY As Double = topY - bottomY
        
        ' Calculate angle from vertical
        Dim angleRad As Double = Math.Atan2(deltaZ, deltaY)
        Dim angleDeg As Double = angleRad * (180 / Math.PI)
        
        Return angleDeg
    End Function

    ''' <summary>
    ''' Calculates the toe angle from a DataTable containing two points with X, Y, Z coordinates.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Front point, Row 1 = Rear point.
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 2 rows containing X, Y, Z coordinates</param>
    ''' <returns>Toe angle in degrees (positive = toe-in, negative = toe-out)</returns>
    ''' <remarks>Uses X (longitudinal) and Z (lateral) coordinates for toe calculation</remarks>
    Public Shared Function CalculateToeFromDataTable(ByVal pointsTable As DataTable) As Double
        If pointsTable Is Nothing Then
            Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
        End If

        If pointsTable.Rows.Count < 2 Then
            Throw New ArgumentException("DataTable must contain at least 2 rows (front and rear points)", "pointsTable")
        End If

        ' Check for required columns (case-insensitive)
        Dim hasX As Boolean = False
        Dim hasY As Boolean = False
        Dim hasZ As Boolean = False
        
        For Each col As DataColumn In pointsTable.Columns
            Dim colName As String = col.ColumnName.ToUpper()
            If colName = "X" Then hasX = True
            If colName = "Y" Then hasY = True
            If colName = "Z" Then hasZ = True
        Next

        If Not (hasX And hasY And hasZ) Then
            Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
        End If

        ' Get coordinates from first two rows
        Dim frontX As Double = CDbl(pointsTable.Rows(0)("X"))
        Dim frontZ As Double = CDbl(pointsTable.Rows(0)("Z"))
        Dim rearX As Double = CDbl(pointsTable.Rows(1)("X"))
        Dim rearZ As Double = CDbl(pointsTable.Rows(1)("Z"))

        ' Calculate toe using longitudinal (X) and lateral (Z) components
        Dim deltaZ As Double = frontZ - rearZ
        Dim deltaX As Double = frontX - rearX
        
        ' Calculate angle from longitudinal axis
        ' Positive = toe-in (front points inward), Negative = toe-out (front points outward)
        Dim angleRad As Double = Math.Atan2(deltaZ, deltaX)
        Dim angleDeg As Double = angleRad * (180 / Math.PI)
        
        Return angleDeg
    End Function

    ''' <summary>
    ''' Calculates camber angle from Wheel Center and Driveshaft Outer Joint Center.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Wheel Center, Row 1 = Driveshaft Outer Joint Center.
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 2 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with camber angle calculations</returns>
    ''' <remarks>
    ''' Camber: Calculated from vertical (Y) and lateral (Z) offset between points.
    ''' </remarks>
    Public Shared Function CalculateCamberFromWheelDriveshaft(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 2 Then
                Throw New ArgumentException("DataTable must contain at least 2 rows (Wheel Center and Driveshaft Outer Joint Center)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim wheelX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim wheelY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim wheelZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim jointX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim jointY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim jointZ As Double = CDbl(pointsTable.Rows(1)("Z"))

            ' Add input data
            resultTable.Rows.Add("Wheel Center X", wheelX.ToString("F2"), "mm")
            resultTable.Rows.Add("Wheel Center Y", wheelY.ToString("F2"), "mm")
            resultTable.Rows.Add("Wheel Center Z", wheelZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint X", jointX.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint Y", jointY.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint Z", jointZ.ToString("F2"), "mm")

            ' Calculate deltas
            Dim deltaX As Double = wheelX - jointX
            Dim deltaY As Double = wheelY - jointY
            Dim deltaZ As Double = wheelZ - jointZ

            resultTable.Rows.Add("Delta X (Longitudinal)", deltaX.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Y (Vertical)", deltaY.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Z (Lateral)", deltaZ.ToString("F2"), "mm")

            ' Calculate Camber Angle (using Y and Z components)
            ' Positive camber = wheel center is more outboard (larger Z) than joint
            Dim camberAngleRad As Double = Math.Atan2(deltaZ, Math.Abs(deltaY))
            Dim camberAngle As Double = camberAngleRad * (180 / Math.PI)
            
            ' Adjust sign based on vertical position
            If deltaY < 0 Then camberAngle = -camberAngle

            resultTable.Rows.Add("Camber Angle", camberAngle.ToString("F3"), "deg")
            
            Dim camberInterpretation As String
            If Math.Abs(camberAngle) < 0.1 Then
                camberInterpretation = "Zero camber (vertical)"
            ElseIf camberAngle > 0 Then
                camberInterpretation = "Positive camber (wheel leans outward)"
            Else
                camberInterpretation = "Negative camber (wheel leans inward)"
            End If
            resultTable.Rows.Add("Camber Interpretation", camberInterpretation, "")

            ' Calculate 3D distance
            Dim distance3D As Double = Math.Sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ)
            resultTable.Rows.Add("3D Distance", distance3D.ToString("F2"), "mm")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates toe angle from Wheel Center and Driveshaft Outer Joint Center.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Wheel Center, Row 1 = Driveshaft Outer Joint Center.
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 2 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with toe angle calculations</returns>
    ''' <remarks>
    ''' Toe: Calculated from longitudinal (X) and lateral (Z) offset between points.
    ''' </remarks>
    Public Shared Function CalculateToeFromWheelDriveshaft(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 2 Then
                Throw New ArgumentException("DataTable must contain at least 2 rows (Wheel Center and Driveshaft Outer Joint Center)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim wheelX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim wheelY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim wheelZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim jointX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim jointY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim jointZ As Double = CDbl(pointsTable.Rows(1)("Z"))

            ' Add input data
            resultTable.Rows.Add("Wheel Center X", wheelX.ToString("F2"), "mm")
            resultTable.Rows.Add("Wheel Center Y", wheelY.ToString("F2"), "mm")
            resultTable.Rows.Add("Wheel Center Z", wheelZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint X", jointX.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint Y", jointY.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint Z", jointZ.ToString("F2"), "mm")

            ' Calculate deltas
            Dim deltaX As Double = wheelX - jointX
            Dim deltaY As Double = wheelY - jointY
            Dim deltaZ As Double = wheelZ - jointZ

            resultTable.Rows.Add("Delta X (Longitudinal)", deltaX.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Y (Vertical)", deltaY.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Z (Lateral)", deltaZ.ToString("F2"), "mm")

            ' Calculate Toe Angle (using X and Z components)
            ' Positive toe = wheel points inward (toward centerline)
            Dim toeAngleRad As Double = Math.Atan2(deltaZ, Math.Abs(deltaX))
            Dim toeAngle As Double = toeAngleRad * (180 / Math.PI)

            resultTable.Rows.Add("Toe Angle", toeAngle.ToString("F3"), "deg")
            
            Dim toeInterpretation As String
            If Math.Abs(toeAngle) < 0.1 Then
                toeInterpretation = "Zero toe (straight ahead)"
            ElseIf toeAngle > 0 Then
                toeInterpretation = "Toe-in (wheel points inward)"
            Else
                toeInterpretation = "Toe-out (wheel points outward)"
            End If
            resultTable.Rows.Add("Toe Interpretation", toeInterpretation, "")

            ' Calculate 3D distance
            Dim distance3D As Double = Math.Sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ)
            resultTable.Rows.Add("3D Distance", distance3D.ToString("F2"), "mm")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates camber and toe angles from Wheel Center and Driveshaft Outer Joint Center.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Wheel Center, Row 1 = Driveshaft Outer Joint Center.
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 2 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with camber and toe angle calculations</returns>
    ''' <remarks>
    ''' Combined function that calculates both camber and toe angles.
    ''' </remarks>
    Public Shared Function CalculateCamberAndToeFromWheelDriveshaft(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 2 Then
                Throw New ArgumentException("DataTable must contain at least 2 rows (Wheel Center and Driveshaft Outer Joint Center)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim wheelX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim wheelY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim wheelZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim jointX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim jointY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim jointZ As Double = CDbl(pointsTable.Rows(1)("Z"))

            ' Add input data
            resultTable.Rows.Add("Wheel Center X", wheelX.ToString("F2"), "mm")
            resultTable.Rows.Add("Wheel Center Y", wheelY.ToString("F2"), "mm")
            resultTable.Rows.Add("Wheel Center Z", wheelZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint X", jointX.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint Y", jointY.ToString("F2"), "mm")
            resultTable.Rows.Add("Driveshaft Joint Z", jointZ.ToString("F2"), "mm")

            ' Calculate deltas
            Dim deltaX As Double = wheelX - jointX
            Dim deltaY As Double = wheelY - jointY
            Dim deltaZ As Double = wheelZ - jointZ

            resultTable.Rows.Add("Delta X (Longitudinal)", deltaX.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Y (Vertical)", deltaY.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Z (Lateral)", deltaZ.ToString("F2"), "mm")

            ' Calculate Camber Angle (using Y and Z components)
            ' Positive camber = wheel center is more outboard (larger Z) than joint
            Dim camberAngleRad As Double = Math.Atan2(deltaZ, Math.Abs(deltaY))
            Dim camberAngle As Double = camberAngleRad * (180 / Math.PI)
            
            ' Adjust sign based on vertical position
            If deltaY < 0 Then camberAngle = -camberAngle

            resultTable.Rows.Add("Camber Angle", camberAngle.ToString("F3"), "deg")
            
            Dim camberInterpretation As String
            If Math.Abs(camberAngle) < 0.1 Then
                camberInterpretation = "Zero camber (vertical)"
            ElseIf camberAngle > 0 Then
                camberInterpretation = "Positive camber (wheel leans outward)"
            Else
                camberInterpretation = "Negative camber (wheel leans inward)"
            End If
            resultTable.Rows.Add("Camber Interpretation", camberInterpretation, "")

            ' Calculate Toe Angle (using X and Z components)
            ' Positive toe = wheel points inward (toward centerline)
            Dim toeAngleRad As Double = Math.Atan2(deltaZ, Math.Abs(deltaX))
            Dim toeAngle As Double = toeAngleRad * (180 / Math.PI)

            resultTable.Rows.Add("Toe Angle", toeAngle.ToString("F3"), "deg")
            
            Dim toeInterpretation As String
            If Math.Abs(toeAngle) < 0.1 Then
                toeInterpretation = "Zero toe (straight ahead)"
            ElseIf toeAngle > 0 Then
                toeInterpretation = "Toe-in (wheel points inward)"
            Else
                toeInterpretation = "Toe-out (wheel points outward)"
            End If
            resultTable.Rows.Add("Toe Interpretation", toeInterpretation, "")

            ' Calculate 3D distance
            Dim distance3D As Double = Math.Sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ)
            resultTable.Rows.Add("3D Distance", distance3D.ToString("F2"), "mm")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates kingpin (KPI) and caster angles from Upper and Lower Control Arm Outer Joint Centers.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Upper Control Arm Outer Joint Center, Row 1 = Lower Control Arm Outer Joint Center.
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 2 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with kingpin and caster angle calculations</returns>
    ''' <remarks>
    ''' Kingpin Angle (KPI): Inclination in frontal view (Y-Z plane) - angle from vertical.
    ''' Caster Angle: Inclination in side view (X-Y plane) - angle from vertical.
    ''' </remarks>
    Public Shared Function CalculateKingpinAndCasterFromControlArms(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 2 Then
                Throw New ArgumentException("DataTable must contain at least 2 rows (Upper and Lower Control Arm Outer Joint Centers)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim upperX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim upperY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim upperZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim lowerX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim lowerY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim lowerZ As Double = CDbl(pointsTable.Rows(1)("Z"))

            ' Add input data
            resultTable.Rows.Add("Upper Joint X", upperX.ToString("F2"), "mm")
            resultTable.Rows.Add("Upper Joint Y", upperY.ToString("F2"), "mm")
            resultTable.Rows.Add("Upper Joint Z", upperZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint X", lowerX.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint Y", lowerY.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint Z", lowerZ.ToString("F2"), "mm")

            ' Calculate deltas
            Dim deltaX As Double = upperX - lowerX
            Dim deltaY As Double = upperY - lowerY
            Dim deltaZ As Double = upperZ - lowerZ

            resultTable.Rows.Add("Delta X (Longitudinal)", deltaX.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Y (Vertical)", deltaY.ToString("F2"), "mm")
            resultTable.Rows.Add("Delta Z (Lateral)", deltaZ.ToString("F2"), "mm")

            ' Calculate Kingpin Inclination Angle (KPI) - Frontal view (Y-Z plane)
            ' Angle from vertical axis in the Y-Z plane
            ' Positive KPI = upper joint is more inboard (smaller Z) than lower joint
            Dim kingpinAngleRad As Double = Math.Atan2(Math.Abs(deltaZ), Math.Abs(deltaY))
            Dim kingpinAngle As Double = kingpinAngleRad * (180 / Math.PI)
            
            ' Adjust sign: positive if upper is inboard, negative if upper is outboard
            If deltaZ < 0 Then kingpinAngle = -kingpinAngle

            resultTable.Rows.Add("Kingpin Angle (KPI)", kingpinAngle.ToString("F3"), "deg")
            
            Dim kingpinInterpretation As String
            If Math.Abs(kingpinAngle) < 0.1 Then
                kingpinInterpretation = "Zero KPI (vertical steering axis)"
            ElseIf kingpinAngle > 0 Then
                kingpinInterpretation = "Positive KPI (upper joint inboard)"
            Else
                kingpinInterpretation = "Negative KPI (upper joint outboard)"
            End If
            resultTable.Rows.Add("KPI Interpretation", kingpinInterpretation, "")

            ' Calculate Caster Angle - Side view (X-Y plane)
            ' Angle from vertical axis in the X-Y plane
            ' Positive caster = upper joint is more rearward (smaller X) than lower joint
            Dim casterAngleRad As Double = Math.Atan2(Math.Abs(deltaX), Math.Abs(deltaY))
            Dim casterAngle As Double = casterAngleRad * (180 / Math.PI)
            
            ' Adjust sign: positive if upper is rearward, negative if upper is forward
            If deltaX < 0 Then casterAngle = -casterAngle

            resultTable.Rows.Add("Caster Angle", casterAngle.ToString("F3"), "deg")
            
            Dim casterInterpretation As String
            If Math.Abs(casterAngle) < 0.1 Then
                casterInterpretation = "Zero caster (vertical steering axis)"
            ElseIf casterAngle > 0 Then
                casterInterpretation = "Positive caster (upper joint rearward)"
            Else
                casterInterpretation = "Negative caster (upper joint forward)"
            End If
            resultTable.Rows.Add("Caster Interpretation", casterInterpretation, "")

            ' Calculate steering axis length (3D distance between points)
            Dim steeringAxisLength As Double = Math.Sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ)
            resultTable.Rows.Add("Steering Axis Length", steeringAxisLength.ToString("F2"), "mm")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates the steering axis intersection point at ground level.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Upper Control Arm Outer Joint Center
    ''' Row 1 = Lower Control Arm Outer Joint Center
    ''' Row 2 = Contact Patch Center (used for ground level reference)
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 3 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with steering axis intersection calculations</returns>
    Public Shared Function CalculateSteeringAxisIntersection(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 3 Then
                Throw New ArgumentException("DataTable must contain at least 3 rows (Upper Joint, Lower Joint, Contact Patch)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim upperX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim upperY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim upperZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim lowerX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim lowerY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim lowerZ As Double = CDbl(pointsTable.Rows(1)("Z"))
            Dim groundY As Double = CDbl(pointsTable.Rows(2)("Y"))

            ' Add input data
            resultTable.Rows.Add("Upper Joint X", upperX.ToString("F2"), "mm")
            resultTable.Rows.Add("Upper Joint Y", upperY.ToString("F2"), "mm")
            resultTable.Rows.Add("Upper Joint Z", upperZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint X", lowerX.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint Y", lowerY.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint Z", lowerZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Ground Level Y", groundY.ToString("F2"), "mm")

            ' Calculate steering axis intersection at ground level
            ' Using parametric line equation: P = P1 + t(P2 - P1)
            ' Solve for t when Y = groundY
            
            Dim deltaY As Double = upperY - lowerY
            Dim t As Double
            
            If Math.Abs(deltaY) < 0.001 Then
                ' Steering axis is horizontal, use lower point
                t = 0
                resultTable.Rows.Add("Warning", "Steering axis nearly horizontal", "")
            Else
                t = (groundY - lowerY) / deltaY
            End If

            ' Calculate intersection point at ground level
            Dim intersectX As Double = lowerX + t * (upperX - lowerX)
            Dim intersectZ As Double = lowerZ + t * (upperZ - lowerZ)
            
            resultTable.Rows.Add("Intersection Parameter t", t.ToString("F4"), "")
            resultTable.Rows.Add("Intersection Point X", intersectX.ToString("F2"), "mm")
            resultTable.Rows.Add("Intersection Point Y", groundY.ToString("F2"), "mm")
            resultTable.Rows.Add("Intersection Point Z", intersectZ.ToString("F2"), "mm")

            ' Calculate kingpin and caster angles
            Dim deltaXAxis As Double = upperX - lowerX
            Dim deltaYAxis As Double = upperY - lowerY
            Dim deltaZAxis As Double = upperZ - lowerZ

            Dim kingpinAngle As Double = Math.Atan2(Math.Abs(deltaZAxis), Math.Abs(deltaYAxis)) * (180 / Math.PI)
            If deltaZAxis < 0 Then kingpinAngle = -kingpinAngle
            
            Dim casterAngle As Double = Math.Atan2(Math.Abs(deltaXAxis), Math.Abs(deltaYAxis)) * (180 / Math.PI)
            If deltaXAxis < 0 Then casterAngle = -casterAngle

            resultTable.Rows.Add("Kingpin Angle (KPI)", kingpinAngle.ToString("F3"), "deg")
            resultTable.Rows.Add("Caster Angle", casterAngle.ToString("F3"), "deg")

            ' Calculate steering axis length
            Dim axisLength As Double = Math.Sqrt(deltaXAxis * deltaXAxis + deltaYAxis * deltaYAxis + deltaZAxis * deltaZAxis)
            resultTable.Rows.Add("Steering Axis Length", axisLength.ToString("F2"), "mm")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates scrub radius from steering axis and contact patch.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Upper Control Arm Outer Joint Center
    ''' Row 1 = Lower Control Arm Outer Joint Center
    ''' Row 2 = Contact Patch Center
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 3 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with scrub radius calculations</returns>
    ''' <remarks>
    ''' Scrub Radius: Lateral (Z) distance from contact patch to steering axis intersection at ground level.
    ''' Positive scrub = contact patch outboard of steering axis.
    ''' Negative scrub = contact patch inboard of steering axis (typical for FWD).
    ''' </remarks>
    Public Shared Function CalculateScrubRadius(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 3 Then
                Throw New ArgumentException("DataTable must contain at least 3 rows (Upper Joint, Lower Joint, Contact Patch)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim upperX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim upperY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim upperZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim lowerX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim lowerY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim lowerZ As Double = CDbl(pointsTable.Rows(1)("Z"))
            Dim contactX As Double = CDbl(pointsTable.Rows(2)("X"))
            Dim contactY As Double = CDbl(pointsTable.Rows(2)("Y"))
            Dim contactZ As Double = CDbl(pointsTable.Rows(2)("Z"))

            resultTable.Rows.Add("Upper Joint Z", upperZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint Z", lowerZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Contact Patch Z", contactZ.ToString("F2"), "mm")

            ' Calculate steering axis intersection at ground level
            Dim deltaY As Double = upperY - lowerY
            Dim t As Double
            
            If Math.Abs(deltaY) < 0.001 Then
                t = 0
                resultTable.Rows.Add("Warning", "Steering axis nearly horizontal", "")
            Else
                t = (contactY - lowerY) / deltaY
            End If

            Dim intersectZ As Double = lowerZ + t * (upperZ - lowerZ)
            
            resultTable.Rows.Add("Axis Intersection Z", intersectZ.ToString("F2"), "mm")

            ' Calculate Scrub Radius (lateral offset)
            Dim scrubRadius As Double = contactZ - intersectZ
            resultTable.Rows.Add("Scrub Radius", scrubRadius.ToString("F2"), "mm")
            resultTable.Rows.Add("Scrub Radius (Absolute)", Math.Abs(scrubRadius).ToString("F2"), "mm")
            
            Dim scrubInterpretation As String
            If Math.Abs(scrubRadius) < 1 Then
                scrubInterpretation = "Near zero scrub (steering axis at contact patch)"
            ElseIf scrubRadius > 0 Then
                scrubInterpretation = "Positive scrub (contact patch outboard of steering axis)"
            Else
                scrubInterpretation = "Negative scrub (contact patch inboard of steering axis - typical for FWD)"
            End If
            resultTable.Rows.Add("Interpretation", scrubInterpretation, "")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates caster offset (mechanical trail) from steering axis and contact patch.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Upper Control Arm Outer Joint Center
    ''' Row 1 = Lower Control Arm Outer Joint Center
    ''' Row 2 = Contact Patch Center
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 3 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with caster offset (mechanical trail) calculations</returns>
    ''' <remarks>
    ''' Caster Offset (Mechanical Trail): Longitudinal (X) distance from contact patch to steering axis intersection at ground level.
    ''' Positive offset = contact patch ahead of steering axis.
    ''' Negative offset = contact patch behind steering axis.
    ''' </remarks>
    Public Shared Function CalculateCasterOffset(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 3 Then
                Throw New ArgumentException("DataTable must contain at least 3 rows (Upper Joint, Lower Joint, Contact Patch)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim upperX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim upperY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim upperZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim lowerX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim lowerY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim lowerZ As Double = CDbl(pointsTable.Rows(1)("Z"))
            Dim contactX As Double = CDbl(pointsTable.Rows(2)("X"))
            Dim contactY As Double = CDbl(pointsTable.Rows(2)("Y"))
            Dim contactZ As Double = CDbl(pointsTable.Rows(2)("Z"))

            resultTable.Rows.Add("Upper Joint X", upperX.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint X", lowerX.ToString("F2"), "mm")
            resultTable.Rows.Add("Contact Patch X", contactX.ToString("F2"), "mm")

            ' Calculate steering axis intersection at ground level
            Dim deltaY As Double = upperY - lowerY
            Dim t As Double
            
            If Math.Abs(deltaY) < 0.001 Then
                t = 0
                resultTable.Rows.Add("Warning", "Steering axis nearly horizontal", "")
            Else
                t = (contactY - lowerY) / deltaY
            End If

            Dim intersectX As Double = lowerX + t * (upperX - lowerX)
            
            resultTable.Rows.Add("Axis Intersection X", intersectX.ToString("F2"), "mm")

            ' Calculate Caster Offset / Mechanical Trail (longitudinal offset)
            Dim casterOffset As Double = contactX - intersectX
            resultTable.Rows.Add("Caster Offset (Mechanical Trail)", casterOffset.ToString("F2"), "mm")
            resultTable.Rows.Add("Caster Offset (Absolute)", Math.Abs(casterOffset).ToString("F2"), "mm")
            
            Dim offsetInterpretation As String
            If Math.Abs(casterOffset) < 1 Then
                offsetInterpretation = "Near zero trail (contact patch at steering axis)"
            ElseIf casterOffset > 0 Then
                offsetInterpretation = "Positive trail (contact patch ahead of steering axis)"
            Else
                offsetInterpretation = "Negative trail (contact patch behind steering axis)"
            End If
            resultTable.Rows.Add("Interpretation", offsetInterpretation, "")

            ' Calculate caster angle for reference
            Dim deltaXAxis As Double = upperX - lowerX
            Dim deltaYAxis As Double = upperY - lowerY
            Dim casterAngle As Double = Math.Atan2(Math.Abs(deltaXAxis), Math.Abs(deltaYAxis)) * (180 / Math.PI)
            If deltaXAxis < 0 Then casterAngle = -casterAngle
            
            resultTable.Rows.Add("Caster Angle", casterAngle.ToString("F3"), "deg")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

    ''' <summary>
    ''' Calculates mechanical trail and scrub radius from steering axis and contact patch.
    ''' DataTable must have columns: X, Y, Z (case-insensitive).
    ''' Row 0 = Upper Control Arm Outer Joint Center
    ''' Row 1 = Lower Control Arm Outer Joint Center
    ''' Row 2 = Contact Patch Center
    ''' </summary>
    ''' <param name="pointsTable">DataTable with 3 rows containing X, Y, Z coordinates</param>
    ''' <returns>DataTable with mechanical trail and scrub radius calculations</returns>
    ''' <remarks>
    ''' Combined function that calculates both caster offset and scrub radius.
    ''' </remarks>
    Public Shared Function CalculateTrailAndScrubRadius(ByVal pointsTable As DataTable) As DataTable
        Dim resultTable As New DataTable()
        resultTable.Columns.Add("Parameter", GetType(String))
        resultTable.Columns.Add("Value", GetType(String))
        resultTable.Columns.Add("Unit", GetType(String))

        Try
            If pointsTable Is Nothing Then
                Throw New ArgumentNullException("pointsTable", "DataTable cannot be null")
            End If

            If pointsTable.Rows.Count < 3 Then
                Throw New ArgumentException("DataTable must contain at least 3 rows (Upper Joint, Lower Joint, Contact Patch)", "pointsTable")
            End If

            ' Check for required columns (case-insensitive)
            Dim hasX As Boolean = False
            Dim hasY As Boolean = False
            Dim hasZ As Boolean = False
            
            For Each col As DataColumn In pointsTable.Columns
                Dim colName As String = col.ColumnName.ToUpper()
                If colName = "X" Then hasX = True
                If colName = "Y" Then hasY = True
                If colName = "Z" Then hasZ = True
            Next

            If Not (hasX And hasY And hasZ) Then
                Throw New ArgumentException("DataTable must contain columns: X, Y, Z", "pointsTable")
            End If

            ' Get coordinates
            Dim upperX As Double = CDbl(pointsTable.Rows(0)("X"))
            Dim upperY As Double = CDbl(pointsTable.Rows(0)("Y"))
            Dim upperZ As Double = CDbl(pointsTable.Rows(0)("Z"))
            Dim lowerX As Double = CDbl(pointsTable.Rows(1)("X"))
            Dim lowerY As Double = CDbl(pointsTable.Rows(1)("Y"))
            Dim lowerZ As Double = CDbl(pointsTable.Rows(1)("Z"))
            Dim contactX As Double = CDbl(pointsTable.Rows(2)("X"))
            Dim contactY As Double = CDbl(pointsTable.Rows(2)("Y"))
            Dim contactZ As Double = CDbl(pointsTable.Rows(2)("Z"))

            ' Add input data
            resultTable.Rows.Add("Upper Joint X", upperX.ToString("F2"), "mm")
            resultTable.Rows.Add("Upper Joint Y", upperY.ToString("F2"), "mm")
            resultTable.Rows.Add("Upper Joint Z", upperZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint X", lowerX.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint Y", lowerY.ToString("F2"), "mm")
            resultTable.Rows.Add("Lower Joint Z", lowerZ.ToString("F2"), "mm")
            resultTable.Rows.Add("Contact Patch X", contactX.ToString("F2"), "mm")
            resultTable.Rows.Add("Contact Patch Y", contactY.ToString("F2"), "mm")
            resultTable.Rows.Add("Contact Patch Z", contactZ.ToString("F2"), "mm")

            ' Calculate steering axis intersection at ground level
            Dim deltaY As Double = upperY - lowerY
            Dim t As Double
            
            If Math.Abs(deltaY) < 0.001 Then
                t = 0
                resultTable.Rows.Add("Warning", "Steering axis nearly horizontal", "")
            Else
                t = (contactY - lowerY) / deltaY
            End If

            Dim intersectX As Double = lowerX + t * (upperX - lowerX)
            Dim intersectZ As Double = lowerZ + t * (upperZ - lowerZ)
            
            resultTable.Rows.Add("Axis Intersection X", intersectX.ToString("F2"), "mm")
            resultTable.Rows.Add("Axis Intersection Z", intersectZ.ToString("F2"), "mm")

            ' Calculate Mechanical Trail (longitudinal offset)
            Dim mechanicalTrail As Double = contactX - intersectX
            resultTable.Rows.Add("Mechanical Trail", mechanicalTrail.ToString("F2"), "mm")
            
            Dim trailInterpretation As String
            If Math.Abs(mechanicalTrail) < 1 Then
                trailInterpretation = "Near zero trail"
            ElseIf mechanicalTrail > 0 Then
                trailInterpretation = "Positive trail (contact patch ahead of axis)"
            Else
                trailInterpretation = "Negative trail (contact patch behind axis)"
            End If
            resultTable.Rows.Add("Trail Interpretation", trailInterpretation, "")

            ' Calculate Scrub Radius (lateral offset)
            Dim scrubRadius As Double = contactZ - intersectZ
            resultTable.Rows.Add("Scrub Radius", scrubRadius.ToString("F2"), "mm")
            
            Dim scrubInterpretation As String
            If Math.Abs(scrubRadius) < 1 Then
                scrubInterpretation = "Near zero scrub (axis at contact patch)"
            ElseIf scrubRadius > 0 Then
                scrubInterpretation = "Positive scrub (contact patch outboard of axis)"
            Else
                scrubInterpretation = "Negative scrub (contact patch inboard of axis)"
            End If
            resultTable.Rows.Add("Scrub Interpretation", scrubInterpretation, "")

            ' Calculate total offset distance
            Dim totalOffset As Double = Math.Sqrt(mechanicalTrail * mechanicalTrail + scrubRadius * scrubRadius)
            resultTable.Rows.Add("Total Offset Distance", totalOffset.ToString("F2"), "mm")

        Catch ex As Exception
            resultTable.Rows.Add("Error", ex.Message, "")
        End Try

        Return resultTable
    End Function

End Class
