import math
import numpy as np

class SuspensionCalculator:
    """
    Suspension & ARB Design Calculator
    Based on vehicle dynamics principles for ride frequency and roll stiffness calculations
    """
    
    def __init__(self):
        # Constants
        self.g = 9.81  # gravitational acceleration (m/s^2)
        
    def calculate_spring_stiffness(self, sprung_mass, target_ride_frequency, motion_ratio):
        """
        Calculate required spring stiffness
        
        Parameters:
        - sprung_mass: kg (mass supported by the spring)
        - target_ride_frequency: Hz (desired natural frequency)
        - motion_ratio: ratio of wheel travel to spring travel
        
        Returns:
        - spring_stiffness: N/mm
        """
        # Formula: f = (1/2π) * sqrt(K_wheel / m)
        # K_wheel = K_spring * MR^2
        # K_spring = (2π*f)^2 * m / MR^2
        
        omega = 2 * math.pi * target_ride_frequency  # rad/s
        spring_stiffness_N_m = (omega**2 * sprung_mass) / (motion_ratio**2)
        spring_stiffness_N_mm = spring_stiffness_N_m / 1000  # Convert to N/mm
        
        return spring_stiffness_N_mm
    
    def calculate_wheel_rate(self, spring_stiffness, motion_ratio):
        """
        Calculate wheel rate from spring stiffness
        
        Parameters:
        - spring_stiffness: N/mm
        - motion_ratio: ratio
        
        Returns:
        - wheel_rate: N/mm
        """
        wheel_rate = spring_stiffness * (motion_ratio**2)
        return wheel_rate
    
    def calculate_ride_rate(self, wheel_rate, tire_stiffness):
        """
        Calculate ride rate (combination of wheel rate and tire stiffness)
        
        Parameters:
        - wheel_rate: N/mm
        - tire_stiffness: N/mm
        
        Returns:
        - ride_rate: N/mm
        """
        # Springs in series: 1/K_total = 1/K_wheel + 1/K_tire
        ride_rate = 1 / (1/wheel_rate + 1/tire_stiffness)
        return ride_rate
    
    def calculate_roll_stiffness(self, spring_rate, track_width, motion_ratio):
        """
        Calculate roll stiffness from spring rate
        
        Parameters:
        - spring_rate: N/mm per spring
        - track_width: mm (front or rear track width)
        - motion_ratio: ratio
        
        Returns:
        - roll_stiffness: Nm/deg
        """
        # Roll stiffness = K_spring * MR^2 * (track/2)^2 * 2 springs * (π/180)
        # Factor of 2 for both springs on the axle
        
        track_m = track_width / 1000  # Convert to meters
        roll_stiffness_Nm_rad = 2 * spring_rate * 1000 * (motion_ratio**2) * ((track_m/2)**2)
        roll_stiffness_Nm_deg = roll_stiffness_Nm_rad * (math.pi / 180)
        
        return roll_stiffness_Nm_deg
    
    def calculate_required_roll_stiffness(self, sprung_mass, cg_height, track_width, 
                                         lateral_accel_g, target_roll_gradient_deg_g):
        """
        Calculate required total roll stiffness
        
        Parameters:
        - sprung_mass: kg
        - cg_height: mm (height of CG from ground)
        - track_width: mm
        - lateral_accel_g: g (lateral acceleration, typically 1.0-1.5g)
        - target_roll_gradient_deg_g: deg/g (target roll gradient)
        
        Returns:
        - required_roll_stiffness: Nm/deg
        """
        cg_height_m = cg_height / 1000
        track_m = track_width / 1000
        
        # Roll moment = m * g * ay * h
        roll_moment = sprung_mass * self.g * lateral_accel_g * cg_height_m
        
        # Required roll stiffness = Roll moment / target roll angle
        target_roll_angle = target_roll_gradient_deg_g * lateral_accel_g
        required_roll_stiffness = roll_moment / target_roll_angle
        
        return required_roll_stiffness
    
    def calculate_arb_stiffness(self, required_total_roll_stiffness, spring_roll_stiffness):
        """
        Calculate required ARB roll stiffness
        
        Parameters:
        - required_total_roll_stiffness: Nm/deg
        - spring_roll_stiffness: Nm/deg (from springs)
        
        Returns:
        - arb_roll_stiffness: Nm/deg
        """
        arb_roll_stiffness = required_total_roll_stiffness - spring_roll_stiffness
        return max(0, arb_roll_stiffness)  # ARB stiffness cannot be negative
    
    def calculate_arb_diameter(self, required_arb_stiffness, arm_length, half_track, 
                              arb_material_G=80000):
        """
        Calculate ARB diameter using torsion bar formula
        
        Parameters:
        - required_arb_stiffness: Nm/deg (required ARB roll stiffness)
        - arm_length: mm (ARB arm length L2)
        - half_track: mm (half of ARB track width)
        - arb_material_G: MPa (shear modulus, default 80000 MPa for steel)
        
        Returns:
        - arb_diameter: mm
        - arb_stiffness_rate: N/mm (vertical stiffness at wheel)
        """
        # Convert to meters
        arm_length_m = arm_length / 1000
        half_track_m = half_track / 1000
        
        # Convert required roll stiffness to Nm/rad
        required_arb_stiffness_Nm_rad = required_arb_stiffness * (180 / math.pi)
        
        # ARB Roll Stiffness = (G * d^4 * arm_length^2) / (32 * L * track^2) * 2
        # where L is the active length of the torsion bar (half_track)
        # Solving for d^4:
        # d^4 = (K_roll * 32 * L * track^2) / (G * arm_length^2 * 2)
        
        d_4 = (required_arb_stiffness_Nm_rad * 32 * half_track_m * (2*half_track_m)**2) / \
              (arb_material_G * 1e6 * (arm_length_m**2) * 2)
        
        arb_diameter_m = d_4 ** 0.25
        arb_diameter_mm = arb_diameter_m * 1000
        
        # Calculate ARB vertical stiffness rate at wheel
        # K_arb_wheel = (G * π * d^4) / (32 * L) * (arm_length / (track/2))^2
        arb_stiffness_N_m = (arb_material_G * 1e6 * math.pi * (arb_diameter_m**4)) / \
                            (32 * half_track_m) * ((arm_length_m / half_track_m)**2)
        arb_stiffness_N_mm = arb_stiffness_N_m / 1000
        
        return arb_diameter_mm, arb_stiffness_N_mm
    
    def calculate_arb_stiffness_from_diameter(self, diameter, arm_length, half_track, 
                                             arb_material_G=80000):
        """
        Calculate ARB stiffness from given diameter
        
        Parameters:
        - diameter: mm (ARB diameter)
        - arm_length: mm (ARB arm length)
        - half_track: mm (half of ARB track width)
        - arb_material_G: MPa (shear modulus)
        
        Returns:
        - arb_roll_stiffness: Nm/deg
        - arb_wheel_rate: N/mm
        """
        # Convert to meters
        diameter_m = diameter / 1000
        arm_length_m = arm_length / 1000
        half_track_m = half_track / 1000
        
        # ARB vertical stiffness at wheel
        arb_stiffness_N_m = (arb_material_G * 1e6 * math.pi * (diameter_m**4)) / \
                            (32 * half_track_m) * ((arm_length_m / half_track_m)**2)
        arb_wheel_rate = arb_stiffness_N_m / 1000  # N/mm
        
        # ARB roll stiffness
        track_m = 2 * half_track_m
        arb_roll_stiffness_Nm_rad = 2 * arb_stiffness_N_m * ((track_m/2)**2)
        arb_roll_stiffness_Nm_deg = arb_roll_stiffness_Nm_rad * (math.pi / 180)
        
        return arb_roll_stiffness_Nm_deg, arb_wheel_rate


def example_calculation():
    """
    Example calculation based on the images provided
    """
    calc = SuspensionCalculator()
    
    print("="*70)
    print("SUSPENSION & ARB DESIGN CALCULATOR")
    print("="*70)
    
    # Input parameters from Image 1
    print("\n--- VEHICLE INPUTS ---")
    design_mass = 2075  # kg
    unsprung_mass_front = 123.2  # kg
    unsprung_mass_rear = 107.2  # kg
    
    sprung_mass_front = design_mass * 0.5 - unsprung_mass_front  # Assuming 50/50 weight dist
    sprung_mass_rear = design_mass * 0.5 - unsprung_mass_rear
    
    print(f"Design Mass: {design_mass} kg")
    print(f"Sprung Mass Front: {sprung_mass_front:.1f} kg")
    print(f"Sprung Mass Rear: {sprung_mass_rear:.1f} kg")
    
    # Tire stiffness
    tire_stiffness_front = 246.8  # N/mm
    tire_stiffness_rear = 246.8   # N/mm
    
    # Target ride frequencies
    target_freq_front = 1.21  # Hz
    target_freq_rear = 1.29   # Hz
    
    # Motion ratios
    motion_ratio_front = 1.665
    motion_ratio_rear = 1.498
    
    # Track widths
    track_front = 1630  # mm
    track_rear = 1630   # mm
    
    print("\n--- SPRING STIFFNESS CALCULATION ---")
    
    # Calculate front spring stiffness
    spring_stiff_front = calc.calculate_spring_stiffness(
        sprung_mass_front, target_freq_front, motion_ratio_front
    )
    print(f"Front Spring Stiffness: {spring_stiff_front:.2f} N/mm")
    
    # Calculate rear spring stiffness
    spring_stiff_rear = calc.calculate_spring_stiffness(
        sprung_mass_rear, target_freq_rear, motion_ratio_rear
    )
    print(f"Rear Spring Stiffness: {spring_stiff_rear:.2f} N/mm")
    
    # Calculate wheel rates
    wheel_rate_front = calc.calculate_wheel_rate(spring_stiff_front, motion_ratio_front)
    wheel_rate_rear = calc.calculate_wheel_rate(spring_stiff_rear, motion_ratio_rear)
    
    print(f"\nFront Wheel Rate: {wheel_rate_front:.2f} N/mm")
    print(f"Rear Wheel Rate: {wheel_rate_rear:.2f} N/mm")
    
    # Calculate ride rates
    ride_rate_front = calc.calculate_ride_rate(wheel_rate_front, tire_stiffness_front)
    ride_rate_rear = calc.calculate_ride_rate(wheel_rate_rear, tire_stiffness_rear)
    
    print(f"\nFront Ride Rate: {ride_rate_front:.2f} N/mm")
    print(f"Rear Ride Rate: {ride_rate_rear:.2f} N/mm")
    
    print("\n--- ROLL STIFFNESS CALCULATION ---")
    
    # Calculate spring roll stiffness
    roll_stiff_front = calc.calculate_roll_stiffness(
        spring_stiff_front, track_front, motion_ratio_front
    )
    roll_stiff_rear = calc.calculate_roll_stiffness(
        spring_stiff_rear, track_rear, motion_ratio_rear
    )
    
    print(f"Front Roll Stiffness (springs): {roll_stiff_front:.1f} Nm/deg")
    print(f"Rear Roll Stiffness (springs): {roll_stiff_rear:.1f} Nm/deg")
    print(f"Total Roll Stiffness (springs): {roll_stiff_front + roll_stiff_rear:.1f} Nm/deg")
    
    # From Image 2: Required suspension roll stiffness
    required_roll_stiff_front = 2183  # Nm/deg
    required_roll_stiff_rear = 798.1  # Nm/deg (from image)
    
    print(f"\nRequired Front Roll Stiffness: {required_roll_stiff_front} Nm/deg")
    print(f"Required Rear Roll Stiffness: {required_roll_stiff_rear} Nm/deg")
    
    # Calculate required ARB stiffness
    arb_stiff_front = calc.calculate_arb_stiffness(required_roll_stiff_front, roll_stiff_front)
    arb_stiff_rear = calc.calculate_arb_stiffness(required_roll_stiff_rear, roll_stiff_rear)
    
    print(f"\nRequired Front ARB Stiffness: {arb_stiff_front:.1f} Nm/deg")
    print(f"Required Rear ARB Stiffness: {arb_stiff_rear:.1f} Nm/deg")
    
    print("\n--- ARB DIAMETER CALCULATION ---")
    
    # ARB geometry from Image 3
    arb_arm_length_front = 298.5  # mm (L2)
    arb_arm_length_rear = 298.5   # mm
    half_track_front = 1122.8 / 2  # mm (half of ARB track)
    half_track_rear = 744.5 / 2    # mm
    
    # Calculate ARB diameter
    arb_dia_front, arb_wheel_rate_front = calc.calculate_arb_diameter(
        arb_stiff_front, arb_arm_length_front, half_track_front
    )
    
    arb_dia_rear, arb_wheel_rate_rear = calc.calculate_arb_diameter(
        arb_stiff_rear, arb_arm_length_rear, half_track_rear
    )
    
    print(f"Front ARB Diameter: {arb_dia_front:.2f} mm")
    print(f"Front ARB Wheel Rate: {arb_wheel_rate_front:.2f} N/mm")
    
    print(f"\nRear ARB Diameter: {arb_dia_rear:.2f} mm")
    print(f"Rear ARB Wheel Rate: {arb_wheel_rate_rear:.2f} N/mm")
    
    print("\n--- VERIFICATION ---")
    # Verify with given diameter (if known)
    # From images, we can see ARB diameter values
    # Let's verify the calculation is correct
    
    # Calculate effective roll stiffness
    total_front_roll = roll_stiff_front + arb_stiff_front
    total_rear_roll = roll_stiff_rear + arb_stiff_rear
    
    print(f"Total Front Roll Stiffness: {total_front_roll:.1f} Nm/deg")
    print(f"Total Rear Roll Stiffness: {total_rear_roll:.1f} Nm/deg")
    
    # Roll stiffness distribution
    total_roll = total_front_roll + total_rear_roll
    front_roll_dist = (total_front_roll / total_roll) * 100
    
    print(f"\nFront/Rear Roll Stiffness Distribution: {front_roll_dist:.1f}/{100-front_roll_dist:.1f}")
    
    print("="*70)


if __name__ == "__main__":
    example_calculation()