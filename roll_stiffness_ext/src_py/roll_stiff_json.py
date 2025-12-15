"""
Roll Stiffness Calculator - JSON Input Version
Integrates with the understeer_gradient calculator JSON format
"""

import json
import sys
import math


class RollStiffnessCalculator:
    """Calculate roll stiffness, spring rates, and ARB parameters from JSON input"""
    
    def __init__(self):
        self.g = 9.81  # m/s^2
    
    def calculate_spring_rate_from_ride_frequency(self, ride_frequency, corner_mass, motion_ratio):
        """
        Calculate spring rate from ride frequency
        Formula: f = (1/2π) * √(k_wheel/m_corner)
        Therefore: k_spring = (2π*f)² * m_corner / MR²
        
        Args:
            ride_frequency: Hz
            corner_mass: kg per corner
            motion_ratio: dimensionless
        
        Returns:
            Spring rate in N/m
        """
        omega = 2 * math.pi * ride_frequency
        k_spring = (omega ** 2) * corner_mass / (motion_ratio ** 2)
        return k_spring
    
    def calculate_wheel_rate(self, spring_rate, motion_ratio):
        """Calculate wheel rate from spring rate"""
        return spring_rate * (motion_ratio ** 2)
    
    def calculate_roll_stiffness_from_spring(self, spring_rate, motion_ratio, track_width):
        """
        Calculate roll stiffness contribution from springs
        Formula: k_φ = 2 * k_wheel * (t/2)²
        
        Args:
            spring_rate: N/m at spring
            motion_ratio: dimensionless
            track_width: m
        
        Returns:
            Roll stiffness in Nm/rad
        """
        k_wheel = self.calculate_wheel_rate(spring_rate, motion_ratio)
        k_roll = k_wheel * (track_width ** 2) / 2
        return k_roll
    
    def calculate_arb_stiffness(self, arb_params):
        """
        Calculate ARB stiffness from geometry and material properties
        Uses torsion bar and cantilever beam formulas
        
        Returns:
            Dictionary with arb_tip_rate (N/m), arb_wheel_rate (N/m), arb_roll_stiffness (Nm/rad)
        """
        # Extract parameters
        G = arb_params['arb_shear_modulus']  # Pa
        E = arb_params['arb_young_modulus']  # Pa
        d_od = arb_params['arb_d_od']  # m
        d_id = arb_params.get('arb_d_id', 0.0)  # m
        L_center = arb_params['arb_center_length']  # m
        L_arm = arb_params['arb_arm_length']  # m
        MR = arb_params['motion_ratio']
        track = arb_params['track_width']  # m
        
        # Polar second moment (torsion)
        J = math.pi / 32 * (d_od**4 - d_id**4)
        
        # Area moment (bending)
        I = math.pi / 64 * (d_od**4 - d_id**4)
        
        # Torsion stiffness (center section)
        k_torsion = G * J / L_center
        
        # Cantilever stiffness (arms) - both arms
        k_cantilever = 3 * E * I / (L_arm ** 3)
        
        # Series combination: 1/k_total = 1/k_cantilever_left + 1/k_torsion + 1/k_cantilever_right
        # Since both arms are identical: 1/k_total = 2/k_cantilever + 1/k_torsion
        k_arb_tip = 1 / (2/k_cantilever + 1/k_torsion)
        
        # Convert to wheel rate
        k_arb_wheel = k_arb_tip * (MR ** 2)
        
        # Roll stiffness
        k_arb_roll = k_arb_wheel * (track ** 2) / 2
        
        return {
            'arb_tip_rate': k_arb_tip,
            'arb_wheel_rate': k_arb_wheel,
            'arb_roll_stiffness': k_arb_roll
        }
    
    def calculate_torque_arm(self, vehicle):
        """Calculate roll moment arm height"""
        weight_front = vehicle['front_weight']
        weight_rear = vehicle['rear_weight']
        weight_front_ratio = weight_front / (weight_front + weight_rear)
        
        a_s = weight_front_ratio * vehicle['wheelbase']
        h_arm = (vehicle['sprung_cg_height'] - 
                vehicle['front_rc_height'] - 
                (a_s / vehicle['wheelbase']) * 
                (vehicle['rear_rc_height'] - vehicle['front_rc_height']))
        return h_arm
    
    def calculate_roll_gradient(self, total_roll_stiffness, sprung_mass, torque_arm_height):
        """
        Calculate roll gradient
        Formula: φ/Ay = (m*g*h_arm) / k_φ (rad/g)
        
        Returns:
            Roll gradient in deg/g
        """
        roll_grad_rad_per_g = (sprung_mass * self.g * torque_arm_height) / total_roll_stiffness
        roll_grad_deg_per_g = math.degrees(roll_grad_rad_per_g)
        return roll_grad_deg_per_g
    
    def process_config(self, config):
        """Process complete JSON configuration and return results"""
        vehicle = config['vehicle']
        front_axle = config['front_axle']
        rear_axle = config['rear_axle']
        
        # Calculate weight ratios
        weight_total = vehicle['front_weight'] + vehicle['rear_weight']
        weight_front_ratio = vehicle['front_weight'] / weight_total
        weight_rear_ratio = vehicle['rear_weight'] / weight_total
        
        # Calculate spring rates from ride frequency
        m_corner_front = vehicle['sprung_mass'] * weight_front_ratio / 2
        m_corner_rear = vehicle['sprung_mass'] * weight_rear_ratio / 2
        
        k_spring_front = self.calculate_spring_rate_from_ride_frequency(
            front_axle['ride_frequency'], m_corner_front, front_axle['motion_ratio']
        )
        k_spring_rear = self.calculate_spring_rate_from_ride_frequency(
            rear_axle['ride_frequency'], m_corner_rear, rear_axle['motion_ratio']
        )
        
        # Calculate wheel rates
        k_wheel_front = self.calculate_wheel_rate(k_spring_front, front_axle['motion_ratio'])
        k_wheel_rear = self.calculate_wheel_rate(k_spring_rear, rear_axle['motion_ratio'])
        
        # Calculate spring roll stiffness
        k_roll_spring_front = self.calculate_roll_stiffness_from_spring(
            k_spring_front, front_axle['motion_ratio'], front_axle['track_width']
        )
        k_roll_spring_rear = self.calculate_roll_stiffness_from_spring(
            k_spring_rear, rear_axle['motion_ratio'], rear_axle['track_width']
        )
        
        # Calculate ARB contributions
        front_arb_data = self.calculate_arb_stiffness(front_axle)
        rear_arb_data = self.calculate_arb_stiffness(rear_axle)
        
        # Total roll stiffness
        k_roll_front_total = k_roll_spring_front + front_arb_data['arb_roll_stiffness']
        k_roll_rear_total = k_roll_spring_rear + rear_arb_data['arb_roll_stiffness']
        k_roll_total = k_roll_front_total + k_roll_rear_total
        
        # Auxiliary percentages
        aux_percent_front = (front_arb_data['arb_roll_stiffness'] / k_roll_front_total) * 100
        aux_percent_rear = (rear_arb_data['arb_roll_stiffness'] / k_roll_rear_total) * 100
        
        # Calculate roll gradient
        torque_arm = self.calculate_torque_arm(vehicle)
        roll_gradient = self.calculate_roll_gradient(k_roll_total, vehicle['sprung_mass'], torque_arm)
        
        return {
            'vehicle': {
                'sprung_mass': vehicle['sprung_mass'],
                'weight_front_ratio': weight_front_ratio,
                'weight_rear_ratio': weight_rear_ratio,
                'torque_arm_height': torque_arm
            },
            'front': {
                'ride_frequency': front_axle['ride_frequency'],
                'spring_rate': k_spring_front,
                'wheel_rate': k_wheel_front,
                'spring_roll_stiffness': k_roll_spring_front,
                'arb_diameter_mm': front_axle['arb_d_od'] * 1000,
                'arb_tip_rate': front_arb_data['arb_tip_rate'],
                'arb_wheel_rate': front_arb_data['arb_wheel_rate'],
                'arb_roll_stiffness': front_arb_data['arb_roll_stiffness'],
                'total_roll_stiffness': k_roll_front_total,
                'aux_percent': aux_percent_front
            },
            'rear': {
                'ride_frequency': rear_axle['ride_frequency'],
                'spring_rate': k_spring_rear,
                'wheel_rate': k_wheel_rear,
                'spring_roll_stiffness': k_roll_spring_rear,
                'arb_diameter_mm': rear_axle['arb_d_od'] * 1000,
                'arb_tip_rate': rear_arb_data['arb_tip_rate'],
                'arb_wheel_rate': rear_arb_data['arb_wheel_rate'],
                'arb_roll_stiffness': rear_arb_data['arb_roll_stiffness'],
                'total_roll_stiffness': k_roll_rear_total,
                'aux_percent': aux_percent_rear
            },
            'total': {
                'roll_stiffness': k_roll_total,
                'roll_gradient_deg_per_g': roll_gradient
            }
        }
    
    def generate_report(self, results):
        """Generate formatted text report"""
        report = []
        report.append("=" * 100)
        report.append("ROLL STIFFNESS DESIGN REPORT")
        report.append("=" * 100)
        
        v = results['vehicle']
        report.append("\n1. VEHICLE PARAMETERS")
        report.append(f"   Sprung mass: {v['sprung_mass']:.0f} kg")
        report.append(f"   Weight distribution: {v['weight_front_ratio']*100:.1f}% F / {v['weight_rear_ratio']*100:.1f}% R")
        report.append(f"   Roll torque arm height: {v['torque_arm_height']:.3f} m")
        
        f = results['front']
        report.append("\n2. FRONT AXLE")
        report.append(f"   Target ride frequency: {f['ride_frequency']:.2f} Hz")
        report.append(f"   Spring rate: {f['spring_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {f['wheel_rate']:,.0f} N/m")
        report.append(f"   Spring roll stiffness: {f['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   ARB diameter: {f['arb_diameter_mm']:.2f} mm")
        report.append(f"   ARB tip rate: {f['arb_tip_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {f['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB roll stiffness: {f['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Total roll stiffness: {f['total_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {f['aux_percent']:.2f}%")
        
        r = results['rear']
        report.append("\n3. REAR AXLE")
        report.append(f"   Target ride frequency: {r['ride_frequency']:.2f} Hz")
        report.append(f"   Spring rate: {r['spring_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {r['wheel_rate']:,.0f} N/m")
        report.append(f"   Spring roll stiffness: {r['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   ARB diameter: {r['arb_diameter_mm']:.2f} mm")
        report.append(f"   ARB tip rate: {r['arb_tip_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {r['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB roll stiffness: {r['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Total roll stiffness: {r['total_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {r['aux_percent']:.2f}%")
        
        t = results['total']
        report.append("\n4. TOTAL VEHICLE")
        report.append(f"   Total roll stiffness: {t['roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Roll gradient: {t['roll_gradient_deg_per_g']:.3f} deg/g")
        report.append(f"   Front contribution: {f['total_roll_stiffness']:,.0f} Nm/rad ({f['total_roll_stiffness']/t['roll_stiffness']*100:.1f}%)")
        report.append(f"   Rear contribution: {r['total_roll_stiffness']:,.0f} Nm/rad ({r['total_roll_stiffness']/t['roll_stiffness']*100:.1f}%)")
        
        report.append("\n" + "=" * 100)
        return "\n".join(report)


def main():
    # Load from JSON file (default or command line argument)
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input_template.json"
    
    try:
        with open(input_file, "r") as f:
            config = json.load(f)
        print(f"Loaded configuration from: {input_file}\n")
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        print(f"Usage: python roll_stiff_json.py [input_file.json]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        sys.exit(1)
    
    # Calculate roll stiffness
    calculator = RollStiffnessCalculator()
    results = calculator.process_config(config)
    
    # Print report
    print(calculator.generate_report(results))


if __name__ == "__main__":
    main()
