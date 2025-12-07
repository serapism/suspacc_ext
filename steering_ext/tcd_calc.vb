Imports System
Imports System.Data

    ''' <summary>
    ''' Calculates the kerb-to-kerb turning circle diameter of a vehicle.
    ''' This is the diameter of the smallest circle the outer front tyre can make.
    ''' </summary>
    ''' <param name="wheelbase">Vehicle wheelbase in mm. Must be positive.</param>
    ''' <param name="wheeltrack">Vehicle track width in mm. Must be positive.</param>
    ''' <param name="outerwheelAngle">Steer angle of the outer wheel in degrees. Must be between 0 and 90.</param>
    ''' <param name="tyreWidth">The section width of the tyre in mm. Must be positive.</param>
    ''' <returns>The kerb-to-kerb turning circle diameter in meters.</returns>
    ''' <remarks>
    ''' The calculation is based on the outer wheel's steering angle, as this defines the largest radius.
    ''' Formula: R = L / sin(θ_outer), where L is wheelbase and θ_outer is the outer wheel angle.
    ''' The turning circle diameter is 2 * (R + TyreWidth/2).
    ''' 
    ''' Throws ArgumentException for invalid inputs:
    ''' - Wheelbase must be > 0 mm (typical: 2400-3000 mm)
    ''' - Track width must be > 0 mm (typical: 1400-1700 mm)
    ''' - Steer angle must be > 0° and <= 90° (typical: 25-45°)
    ''' - Tyre width must be > 0 mm (typical: 205-255 mm)
    ''' </remarks>
    ''' <exception cref="ArgumentException">Thrown when input parameters are invalid</exception>
    Public Shared Function CalculateKerbToKerbTurningCircle(ByVal wheelbase As Double, ByVal wheeltrack As Double, ByVal outerwheelAngle As Double, ByVal tyreWidth As Double) As Double
        Try
            ' Validate wheelbase
            If wheelbase <= 0 Then
                Throw New ArgumentException("Wheelbase must be positive (> 0 mm). Typical range: 2400-3000 mm", "wheelbase")
            End If
            If wheelbase < 1500 Or wheelbase > 4500 Then
                Throw New ArgumentException($"Wheelbase {wheelbase}mm is outside typical range (1500-4500 mm)", "wheelbase")
            End If

            ' Validate track width
            If wheeltrack <= 0 Then
                Throw New ArgumentException("Track width must be positive (> 0 mm). Typical range: 1400-1700 mm", "wheeltrack")
            End If
            If wheeltrack < 1000 Or wheeltrack > 2500 Then
                Throw New ArgumentException($"Track width {wheeltrack}mm is outside typical range (1000-2500 mm)", "wheeltrack")
            End If

            ' Validate steer angle
            If outerwheelAngle <= 0 Or outerwheelAngle > 90 Then
                Throw New ArgumentException("Steer angle must be > 0° and <= 90°. Typical range: 25-45°", "outerwheelAngle")
            End If
            If outerwheelAngle > 60 Then
                Throw New ArgumentException($"Steer angle {outerwheelAngle}° is unusually high (typical max: 50°)", "outerwheelAngle")
            End If

            ' Validate tyre width
            If tyreWidth <= 0 Then
                Throw New ArgumentException("Tyre width must be positive (> 0 mm). Typical range: 155-295 mm", "tyreWidth")
            End If
            If tyreWidth < 100 Or tyreWidth > 400 Then
                Throw New ArgumentException($"Tyre width {tyreWidth}mm is outside typical range (100-400 mm)", "tyreWidth")
            End If

            ' Convert outer wheel angle from degrees to radians
            Dim outerAngleRad As Double = outerwheelAngle * Math.PI / 180.0

            ' Calculate the turning radius to the center of the outer front wheel
            Dim radiusToWheelCenter As Double = wheelbase / Math.Sin(outerAngleRad)

            ' The kerb-to-kerb radius is from the turning center to the outermost edge of the outer tyre
            Dim kerbRadius As Double = radiusToWheelCenter + (tyreWidth / 2.0)

            ' Return the diameter in meters (inputs are in mm)
            Return (kerbRadius * 2.0) / 1000.0

        Catch ex As ArgumentException
            Throw
        Catch ex As Exception
            Throw New InvalidOperationException($"Error calculating turning circle: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Calculates the Ackermann percentage for steering geometry.
    ''' Ackermann percentage indicates how close the steering geometry is to ideal Ackermann steering.
    ''' </summary>
    ''' <param name="Wheelbase">Vehicle wheelbase in mm. Must be positive.</param>
    ''' <param name="TrackWidth">Vehicle track width in mm. Must be positive.</param>
    ''' <param name="SteerAngleOuter">Steer angle of the outer wheel in degrees. Must be between 0 and 90.</param>
    ''' <param name="SteerAngleInner">Steer angle of the inner wheel in degrees. Must be positive.</param>
    ''' <returns>Ackermann percentage (typically 50-150%, where 100% is perfect Ackermann)</returns>
    ''' <remarks>
    ''' Formula: Ackermann % = (Ideal Inner Angle / Actual Inner Angle) * 100
    ''' 
    ''' Interpretation:
    ''' - 100% = Perfect Ackermann steering geometry
    ''' - < 100% = Oversteer characteristic (inner wheel steers more than ideal)
    ''' - > 100% = Understeer characteristic (inner wheel steers less than ideal)
    ''' 
    ''' Throws ArgumentException for invalid inputs:
    ''' - Wheelbase must be > 0 mm (typical: 2400-3000 mm)
    ''' - Track width must be > 0 mm (typical: 1400-1700 mm)
    ''' - Outer steer angle must be > 0° and <= 90° (typical: 25-45°)
    ''' - Inner steer angle must be > 0° and <= 90° (typical: 20-40°)
    ''' - Inner angle should be typically less than outer angle
    ''' </remarks>
    ''' <exception cref="ArgumentException">Thrown when input parameters are invalid</exception>
    Public Shared Function CalculateAckermannPercentage(ByVal Wheelbase As Double, ByVal TrackWidth As Double, ByVal SteerAngleOuter As Double, ByVal SteerAngleInner As Double) As Double
        Try
            ' Validate wheelbase
            If Wheelbase <= 0 Then
                Throw New ArgumentException("Wheelbase must be positive (> 0 mm). Typical range: 2400-3000 mm", "Wheelbase")
            End If
            If Wheelbase < 1500 Or Wheelbase > 4500 Then
                Throw New ArgumentException($"Wheelbase {Wheelbase}mm is outside typical range (1500-4500 mm)", "Wheelbase")
            End If

            ' Validate track width
            If TrackWidth <= 0 Then
                Throw New ArgumentException("Track width must be positive (> 0 mm). Typical range: 1400-1700 mm", "TrackWidth")
            End If
            If TrackWidth < 1000 Or TrackWidth > 2500 Then
                Throw New ArgumentException($"Track width {TrackWidth}mm is outside typical range (1000-2500 mm)", "TrackWidth")
            End If

            ' Validate outer steer angle
            If SteerAngleOuter <= 0 Or SteerAngleOuter > 90 Then
                Throw New ArgumentException("Outer steer angle must be > 0° and <= 90°. Typical range: 25-45°", "SteerAngleOuter")
            End If
            If SteerAngleOuter > 60 Then
                Throw New ArgumentException($"Outer steer angle {SteerAngleOuter}° is unusually high (typical max: 50°)", "SteerAngleOuter")
            End If

            ' Validate inner steer angle
            If SteerAngleInner <= 0 Or SteerAngleInner > 90 Then
                Throw New ArgumentException("Inner steer angle must be > 0° and <= 90°. Typical range: 20-40°", "SteerAngleInner")
            End If
            If SteerAngleInner > 60 Then
                Throw New ArgumentException($"Inner steer angle {SteerAngleInner}° is unusually high (typical max: 50°)", "SteerAngleInner")
            End If

            ' Validate angle relationship
            If SteerAngleInner > SteerAngleOuter Then
                Throw New ArgumentException($"Inner angle ({SteerAngleInner}°) should typically be less than or equal to outer angle ({SteerAngleOuter}°)", "SteerAngleInner")
            End If

            ' Convert degrees to radians for trigonometric functions
            Dim steerAngleOuterRad As Double = SteerAngleOuter * (Math.PI / 180)

            ' Calculate ideal inner steer angle for perfect Ackermann
            ' theta_inner_ideal = atan(L / (W + L / tan(theta_outer)))
            Dim idealInnerSteerAngleRad As Double = Math.Atan(Wheelbase / (TrackWidth + (Wheelbase / Math.Tan(steerAngleOuterRad))))
            Dim idealInnerSteerAngleDeg As Double = idealInnerSteerAngleRad * (180 / Math.PI)

            ' Validate ideal angle calculation
            If Double.IsNaN(idealInnerSteerAngleDeg) Or Double.IsInfinity(idealInnerSteerAngleDeg) Then
                Throw New InvalidOperationException("Failed to calculate ideal inner steer angle. Check input parameters for validity.")
            End If

            ' Calculate Ackermann percentage
            ' Percentage = (Ideal Inner Angle / Actual Inner Angle) * 100
            Dim ackermannPercentage As Double = (idealInnerSteerAngleDeg / SteerAngleInner) * 100

            ' Validate result
            If ackermannPercentage < 0 Or ackermannPercentage > 200 Then
                Throw New InvalidOperationException($"Ackermann percentage {ackermannPercentage:F2}% is outside expected range (0-200%)", New ArgumentException("Calculated Ackermann percentage is unrealistic"))
            End If

            Return ackermannPercentage

        Catch ex As ArgumentException
            Throw
        Catch ex As InvalidOperationException
            Throw
        Catch ex As Exception
            Throw New InvalidOperationException($"Error calculating Ackermann percentage: {ex.Message}", ex)
        End Try
    End Function
