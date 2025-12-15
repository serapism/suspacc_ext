"""Vehicle dynamics calculator for ARB sizing and understeer budget.

Based on Skill-Lync project methodology:
- Design ARB diameters to meet target roll gradient
- Select K&C parameters to meet target understeer budget

All SI units (m, kg, N, rad) unless noted.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional
import arb_calc
import csv
from io import StringIO

GRAVITY = 9.81  # m/s^2


@dataclass
class VehicleParams:
    """Basic vehicle parameters."""
    total_mass: float  # kg
    sprung_mass: float  # kg
    wheelbase: float  # m
    front_track: float  # m
    rear_track: float  # m
    
    # Weight distribution
    front_weight: float  # N
    rear_weight: float  # N
    
    # CG heights
    total_cg_height: float  # m from ground
    sprung_cg_height: float  # m from ground
    
    # Roll centers
    front_rc_height: float  # m from ground
    rear_rc_height: float  # m from ground
    
    # Unsprung masses
    front_unsprung_mass: float  # kg per axle
    rear_unsprung_mass: float  # kg per axle
    
    def __post_init__(self):
        """Calculate derived parameters."""
        self.weight_front_ratio = self.front_weight / (self.front_weight + self.rear_weight)
        self.weight_rear_ratio = 1.0 - self.weight_front_ratio


@dataclass
class AxleParams:
    """Suspension parameters for one axle."""
    spring_rate: float  # N/m at spring
    motion_ratio: float  # wheel travel / spring travel
    track_width: float  # m
    
    # ARB geometry (steel properties default)
    arb_shear_modulus: float = 80e9  # Pa
    arb_young_modulus: float = 210e9  # Pa
    arb_center_length: float = 0.9  # m
    arb_arm_length: float = 0.25  # m
    arb_d_od: float = 0.020  # m (initial guess)
    arb_d_id: float = 0.0  # m (solid bar)
    
    # K&C parameters for understeer budget
    roll_steer_gradient: float = 0.0  # deg steer / deg roll
    camber_per_roll: float = 0.0  # deg camber / deg roll
    
    # Compliance parameters (per force or moment)
    lateral_force_steer_compliance: float = 0.0  # rad / N lateral
    lateral_force_camber_compliance: float = 0.0  # rad / N lateral
    aligning_torque_steer_compliance: float = 0.0  # rad / Nm
    
    def wheel_rate_spring(self) -> float:
        """Spring wheel rate."""
        return self.spring_rate * self.motion_ratio ** 2
    
    def roll_stiffness_spring(self) -> float:
        """Primary roll stiffness from springs (Nm/rad)."""
        k_w = self.wheel_rate_spring()
        return k_w * self.track_width ** 2 / 2.0


@dataclass
class TireParams:
    """Tire characteristics for one axle."""
    cornering_stiffness: float  # N/rad (per axle, both tires)
    camber_stiffness: float  # N/rad camber (per axle)
    vertical_stiffness: float  # N/m (per tire)
    pneumatic_trail: float = 0.015  # m (typical)
    
    def aligning_moment_per_g(self, weight: float) -> float:
        """Aligning torque at 1g lateral (Nm)."""
        # Simplified: AT ≈ pneumatic_trail × lateral_force
        return self.pneumatic_trail * weight


@dataclass
class KCConstraints:
    """K&C parameter constraint ranges."""
    roll_steer_front: tuple = (3.0, 6.5)  # %
    roll_steer_rear: tuple = (-8.0, -3.0)
    roll_camber_front: tuple = (80.0, 90.0)  # %
    roll_camber_rear: tuple = (50.0, 65.0)
    lateral_force_steer_compliance_front: tuple = (0.008, 0.05)  # deg/kN
    lateral_force_steer_compliance_rear: tuple = (0.015, 0.04)
    lateral_force_camber_compliance_front: tuple = (0.1, 0.3)  # deg/kN
    lateral_force_camber_compliance_rear: tuple = (0.15, 0.4)
    aligning_torque_steer_compliance_front: tuple = (0.2, 0.4)  # deg/100Nm
    aligning_torque_steer_compliance_rear: tuple = (0.06, 0.1)
    """Roll gradient design targets (Skill-Lync constraints)."""
    target_deg_per_g_min: float = 3.5
    target_deg_per_g_max: float = 3.8
    front_aux_percent_max: float = 60.0  # % of axle roll stiffness
    rear_aux_percent_max: float = 25.0
    target_understeer: str = "Maximum possible"  # Design goal


@dataclass
class UndersteerBudget:
    """Understeer gradient components (all in deg/g)."""
    # Kinematic contributions
    roll_steer: float = 0.0
    roll_camber: float = 0.0
    
    # Compliance contributions
    lateral_force_compliance_steer: float = 0.0
    lateral_force_compliance_camber: float = 0.0
    aligning_torque_compliance_steer: float = 0.0
    
    # Fundamental (geometry + tire)
    weight_distribution: float = 0.0
    aligning_torque_steer: float = 0.0
    
    def total(self) -> float:
        """Total understeer gradient."""
        return (self.roll_steer + self.roll_camber + 
                self.lateral_force_compliance_steer + 
                self.lateral_force_compliance_camber +
                self.aligning_torque_compliance_steer +
                self.weight_distribution + self.aligning_torque_steer)


class VehicleDynamicsCalculator:
    """Main calculator for ARB sizing and understeer budget."""
    
    def __init__(
        self,
        vehicle: VehicleParams,
        front: AxleParams,
        rear: AxleParams,
        tire_front: TireParams,
        tire_rear: TireParams,
        target: RollGradientTarget,
    ):
        self.vehicle = vehicle
        self.front = front
        self.rear = rear
        self.tire_front = tire_front
        self.tire_rear = tire_rear
        self.target = target
        
        # Calculated properties
        self.torque_arm_height = self._calculate_torque_arm()
        self.front_arb_tip_rate = 0.0
        self.rear_arb_tip_rate = 0.0
        
    def _calculate_torque_arm(self) -> float:
        """Torque arm for roll moment (Skill-Lync method)."""
        # h_arm = h_s - Z_rcf - (a_s/L)*(Z_rcr - Z_rcf)
        a_s = self.vehicle.weight_front_ratio * self.vehicle.wheelbase
        h_arm = (self.vehicle.sprung_cg_height - 
                self.vehicle.front_rc_height - 
                (a_s / self.vehicle.wheelbase) * 
                (self.vehicle.rear_rc_height - self.vehicle.front_rc_height))
        return h_arm
    
    def calculate_arb_tip_rate(self, axle: AxleParams) -> float:
        """Calculate ARB tip rate from geometry."""
        return arb_calc.arb_tip_rate(
            shear_modulus=axle.arb_shear_modulus,
            young_modulus=axle.arb_young_modulus,
            d_od=axle.arb_d_od,
            center_length=axle.arb_center_length,
            arm_length=axle.arb_arm_length,
            d_id=axle.arb_d_id,
        )
    
    def calculate_axle_roll_stiffness(
        self, 
        axle: AxleParams, 
        arb_tip_rate: float
    ) -> dict[str, float]:
        """Calculate roll stiffness breakdown for one axle."""
        k_spring_wheel = axle.wheel_rate_spring()
        k_arb_wheel = arb_tip_rate * axle.motion_ratio ** 2
        
        k_phi_spring = arb_calc.roll_stiffness_from_wheel_rate(
            k_spring_wheel, axle.track_width
        )
        k_phi_arb = arb_calc.roll_stiffness_from_wheel_rate(
            k_arb_wheel, axle.track_width
        )
        
        # Tire roll stiffness (vertical stiffness effect)
        # Simplified: not included in wheel-center calc per Skill-Lync
        
        return {
            "spring_wheel_rate": k_spring_wheel,
            "arb_wheel_rate": k_arb_wheel,
            "spring_roll_stiffness": k_phi_spring,
            "arb_roll_stiffness": k_phi_arb,
            "total_roll_stiffness": k_phi_spring + k_phi_arb,
            "arb_tip_rate": arb_tip_rate,
        optimize_arb_diameters(self) -> dict:
        """Iteratively size ARB diameters to meet roll gradient target."""
        # Bisection search for front and rear ARB diameters
        front_d_min, front_d_max = 0.010, 0.040  # m (10-40 mm)
        rear_d_min, rear_d_max = 0.008, 0.025    # m (8-25 mm)
        
        tolerance = 0.001  # deg/g
        max_iterations = 50
        
        # Optimize front diameter
        for _ in range(max_iterations):
            front_d_mid = (front_d_min + front_d_max) / 2.0
            self.front.arb_d_od = front_d_mid
            
            front_tip = self.calculate_arb_tip_rate(self.front)
            rear_tip = self.calculate_arb_tip_rate(self.rear)
            
            front_data = self.calculate_axle_roll_stiffness(self.front, front_tip)
            rear_data = self.calculate_axle_roll_stiffness(self.rear, rear_tip)
            
            total_k_phi = front_data["total_roll_stiffness"] + rear_data["total_roll_stiffness"]
            current_rg = self.calculate_roll_gradient(total_k_phi)
            
            if current_rg < self.target.target_deg_per_g_min:
                front_d_max = front_d_mid  # Too soft, increase diameter
            else:
                front_d_min = front_d_mid  # Stiff enough
        
        # Optimize rear diameter
        self.front.arb_d_od = (front_d_min + front_d_max) / 2.0
        
        for _ in range(max_iterations):
            rear_d_mid = (rear_d_min + rear_d_max) / 2.0
            self.rear.arb_d_od = rear_d_mid
            
            front_tip = self.calculate_arb_tip_rate(self.front)
            rear_tip = self.calculate_arb_tip_rate(self.rear)
            
            front_data = self.calculate_axle_roll_stiffness(self.front, front_tip)
            rear_data = self.calculate_axle_roll_stiffness(self.rear, rear_tip)
            
            total_k_phi = front_data["total_roll_stiffness"] + rear_data["total_roll_stiffness"]
            current_rg = self.calculate_roll_gradient(total_k_phi)
            
            if current_rg < self.target.target_deg_per_g_min:
                rear_d_max = rear_d_mid  # Too soft
            else:
                rear_d_min = rear_d_mid  # Stiff enough
        
        # Final calculation
        self.front.arb_d_od = (front_d_min + front_d_max) / 2.0
        self.rear.arb_d_od = (rear_d_min + rear_d_max) / 2.0
        
        self.front_arb_tip_rate = self.calculate_arb_tip_rate(self.front)
        self.rear_arb_tip_rate = self.calculate_arb_tip_rate(self.rear)
        
        front_data = self.calculate_axle_roll_stiffness(self.front, self.front_arb_tip_rate)
        rear_data = self.calculate_axle_roll_stiffness(self.rear, self.rear_arb_tip_rate)
        
        total_k_phi = front_data["total_roll_stiffness"] + rear_data["total_roll_stiffness"]
        current_rg = self.calculate_roll_gradient(total_k_phi)
        
        return {
            "front": front_data,
            "rear": rear_data,
            "total_roll_stiffness": total_k_phi,
            "roll_gradient_deg_per_g": current_rg,
            "torque_arm_height": self.torque_arm_height,
            "meets_target": (
                self.target.target_deg_per_g_min <= current_rg <= 
                self.target.target_deg_per_g_max
            ),
            "front_aux_in_range": front_data["aux_percent"] <= self.target.front_aux_percent_max,
            "rear_aux_in_range": rear_data["aux_percent"] <= self.target.rear_aux_percent_max,
        }
    
    def optimize_kc_parameters(self, kc_constraints: KCConstraints) -> dict:
        """Select K&C parameters to maximize understeer (minimize negative understeer)."""
        # Use maximum values from ranges to maximize understeer
        self.front.roll_steer_gradient = kc_constraints.roll_steer_front[1]  # max
        self.rear.roll_steer_gradient = kc_constraints.roll_steer_rear[0]  # min (most negative)
        
        self.front.camber_per_roll = kc_constraints.roll_camber_front[1]  # max
        self.rear.camber_per_roll = kc_constraints.roll_camber_rear[0]  # min
        
        # Compliance: use max for understeer-promoting effects
        self.front.lateral_force_steer_compliance = kc_constraints.lateral_force_steer_compliance_front[1] / 1000
        self.rear.lateral_force_steer_compliance = kc_constraints.lateral_force_steer_compliance_rear[0] / 1000
        
        self.front.lateral_force_camber_compliance = kc_constraints.lateral_force_camber_compliance_front[1] / 1000
        self.rear.lateral_force_camber_compliance = kc_constraints.lateral_force_camber_compliance_rear[0] / 1000
        
        self.front.aligning_torque_steer_compliance = kc_constraints.aligning_torque_steer_compliance_front[1] / 100 * math.pi/180 / 1000
        self.rear.aligning_torque_steer_compliance = kc_constraints.aligning_torque_steer_compliance_rear[0] / 100 * math.pi/180 / 1000
        
        return {
            "roll_steer_front": self.front.roll_steer_gradient,
            "roll_steer_rear": self.rear.roll_steer_gradient,
            "roll_camber_front": self.front.camber_per_roll,
            "roll_camber_rear": self.rear.camber_per_roll
            "front": front_data,
            "rear": rear_data,
            "total_roll_stiffness": total_k_phi,
            "roll_gradient_deg_per_g": current_rg,
            "torque_arm_height": self.torque_arm_height,
            "meets_target": (
                self.target.target_deg_per_g_min <= current_rg <= 
                self.target.target_deg_per_g_max
            ),
            "front_aux_in_range": front_data["aux_percent"] <= self.target.front_aux_percent_max,
            "rear_aux_in_range": rear_data["aux_percent"] <= self.target.rear_aux_percent_max,
        }
    
    def calculate_understeer_budget(
        self, 
        roll_gradient_deg_per_g: float,
        lateral_accel_g: float = 1.0
    ) -> UndersteerBudget:
        """Calculate all understeer gradient components (Skill-Lync formulas)."""
        budget = UndersteerBudget()
        report.append(f"   Total mass: {self.vehicle.total_mass:.0f} kg")
        report.append(f"   Sprung mass: {self.vehicle.sprung_mass:.0f} kg")
        report.append(f"   Wheelbase: {self.vehicle.wheelbase:.3f} m")
        report.append(f"   Weight dist: {self.vehicle.weight_front_ratio*100:.1f}% F / "
                     f"{self.vehicle.weight_rear_ratio*100:.1f}% R")
        report.append(f"   Torque arm height: {self.torque_arm_height:.3f} m")
        
        # Roll gradient results
        report.append("\n2. ROLL GRADIENT DESIGN")
        report.append(f"   Target range: {self.target.target_deg_per_g_min:.2f} - {self.target.target_deg_per_g_max:.2f} deg/g")
        report.append(f"   Achieved: {results['roll_gradient_deg_per_g']:.2f} deg/g")
        deviation = abs(results['roll_gradient_deg_per_g'] - self.target.target_deg_per_g_max) / self.target.target_deg_per_g_max * 100
        report.append(f"   Deviation: {deviation:.1f}%")
        report.append(f"   Meets target: {'✓' if results['meets_target'] else '✗'}")
        
        # Front axle
        front = results["front"]
        report.append("\n3. FRONT AXLE")
        report.append(f"   ARB diameter: {self.front.arb_d_od*1000:.2f} mm (solid)")
        report.append(f"   ARB tip rate: {front['arb_tip_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {front['spring_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {front['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   Primary roll stiffness: {front['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary roll stiffness: {front['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {front['aux_percent']:.1f}% (max {self.target.front_aux_percent_max}%)")
        report.append(f"   In range: {'✓' if results['front_aux_in_range'] else '✗'}")
        
        # Rear axle
        rear = results["rear"]
        report.append("\n4. REAR AXLE")
        report.append(f"   ARB diameter: {self.rear.arb_d_od*1000:.2f} mm (solid)")
        report.append(f"   ARB tip rate: {rear['arb_tip_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {rear['spring_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {rear['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   Primary roll stiffness: {rear['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary roll stiffness: {rear['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {rear['aux_percent']:.1f}% (max {self.target.rear_aux_percent_max}%)")
        report.append(f"   In range: {'✓' if results['rear_aux_in_range'] else '✗'}")
        
        # Total roll stiffness
        report.append(f"\n5. TOTAL ROLL STIFFNESS: {results['total_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Front contribution: {front['total_roll_stiffness']:,.0f} Nm/rad "
                     f"({front['total_roll_stiffness']/results['total_roll_stiffness']*100:.1f}%)")
        report.append(f"   Rear contribution: {rear['total_roll_stiffness']:,.0f} Nm/rad "
                     f"({rear['total_roll_stiffness']/results['total_roll_stiffness']*100:.1f}%)")
        
        # Understeer budget
        report.append("\n6. UNDERSTEER BUDGET (deg/g)")
        report.append(f"   Roll steer:                      {understeer.roll_steer:+.3f}")
        report.append(f"   Roll camber:                     {understeer.roll_camber:+.3f}")
        report.append(f"   Lateral force compliance steer:  {understeer.lateral_force_compliance_steer:+.3f}")
        report.append(f"   Lateral force compliance camber: {understeer.lateral_force_compliance_camber:+.3f}")
        report.append(f"   Aligning torque compliance steer:{understeer.aligning_torque_compliance_steer:+.3f}")
        report.append(f"   Weight distribution:             {understeer.weight_distribution:+.3f}")
        report.append(f"   Aligning torque steer:           {understeer.aligning_torque_steer:+.3f}")
        report.append(f"   " + "-" * 50)
        report.append(f"   TOTAL UNDERSTEER GRADIENT:       {understeer.total():+.3f} deg/g")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def generate_constraint_table(self) -> str:
        """Generate table showing how design meets K&C constraints."""
        table = []
        table.append("\n" + "=" * 100)
        table.append("K&C PARAMETER CONSTRAINTS AND FINAL VALUES")
        table.append("=" * 100)
        
        constraints_data = [
            ("Auxiliary roll stiffness front (%)", 25, 60, 60, self.front.arb_roll_stiffness, None),
            ("Auxiliary roll stiffness rear (%)", 0, 20, 20, self.rear.arb_roll_stiffness, None),
            ("Roll steer front (%)", 3, 6.5, self.front.roll_steer_gradient, None, "%"),
            ("Roll steer rear (%)", -8, -3, self.rear.roll_steer_gradient, None, "%"),
            ("Roll camber front (%)", 80, 90, self.front.camber_per_roll, None, "%"),
            ("Roll camber rear (%)", 50, 65, self.rear.camber_per_roll, None, "%"),
            ("Lateral force compliance steer front (deg/kN)", 0.008, 0.05, self.front.lateral_force_steer_compliance * 1000, None, "deg/kN"),
            ("Lateral force compliance steer rear (deg/kN)", 0.015, 0.04, self.rear.lateral_force_steer_compliance * 1000, None, "deg/kN"),
            ("Lateral force compliance camber front (deg/kN)", 0.1, 0.3, self.front.lateral_force_camber_compliance * 1000, None, "deg/kN"),
            ("Lateral force compliance camber rear (deg/kN)", 0.15, 0.4, self.rear.lateral_force_camber_compliance * 1000, None, "deg/kN"),
            ("Aligning torque compliance steer front (deg/100Nm)", 0.2, 0.4, self.front.aligning_torque_steer_compliance / (math.pi/180 * 1000) * 100, None, "deg/100Nm"),
            ("Aligning torque compliance steer rear (deg/100Nm)", 0.06, 0.1, self.rear.aligning_torque_steer_compliance / (math.pi/180 * 1000) * 100, None, "deg/100Nm"),
        ]
        
        table.append(f"{'Parameter':<45} {'Minimum':<12} {'Maximum':<12} {'Selected':<12} {'Status':<8}")
        table.append("-" * 100)
        
        for param_name, min_val, max_val, final_val, calc_val, unit in constraints_data:
            if calc_val is not None:
                display_val = calc_val
            else:
                display_val = final_val
            
            in_range = min_val <= display_val <= max_val
            status = "✓" if in_range else "✗"
            
            table.append(f"{param_name:<45} {min_val:<12.3f} {max_val:<12.3f} {display_val:<12.3f} {status:<8}")
        
        table.append("=" * 100)
        return "\n".join(tableve design report."""
        results = self.size_arb_diameters()
        understeer = self.calculate_understeer_budget(results["roll_gradient_deg_per_g"])
        
        report = []
        report.append("=" * 70)
        report.append("VEHICLE DYNAMICS DESIGN REPORT")
        report.append("ARB Sizing & Understeer Budget")
        report.append("=" * 70)
        
        # Vehicle summary
        report.append("\n1. VEHICLE PARAMETERS")
        report.append(f"   Total mass: {self.vehicle.total_mass:.0f} kg")
        report.append(f"   Sprung mass: {self.vehicle.sprung_mass:.0f} kg")
        report.append(f"   Wheelbase: {self.vehicle.wheelbase:.3f} m")
        report.append(f"   Weight dist: {self.vehicle.weight_front_ratio*100:.1f}% F / "
                     f"{self.vehicle.weight_rear_ratio*100:.1f}% R")
        report.append(f"   Torque arm height: {self.torque_arm_height:.3f} m")
        
        # Roll gradient results
        report.append("\n2. ROLL GRADIENT DESIGN")
        report.append(f"   Target range: {self.target.target_deg_per_g_min:.2f} - {self.target.target_deg_per_g_max:.2f} deg/g")
        report.append(f"   Achieved: {results['roll_gradient_deg_per_g']:.2f} deg/g")
        report.append(f"   Meets target: {'✓' if results['meets_target'] else '✗'}")
        
        # Front axle
        front = results["front"]
        report.append("\n3. FRONT AXLE")
        report.append(f"   ARB diameter: {self.front.arb_d_od*1000:.1f} mm (solid)")
        report.append(f"   ARB tip rate: {front['arb_tip_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {front['spring_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {front['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   Primary roll stiffness: {front['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary roll stiffness: {front['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {front['aux_percent']:.1f}% "
                     f"(max {self.target.front_aux_percent_max}%)")
        report.append(f"   In range: {'✓' if results['front_aux_in_range'] else '✗'}")
        
        # Rear axle
        rear = results["rear"]
        report.append("\n4. REAR AXLE")
        report.append(f"   ARB diameter: {self.rear.arb_d_od*1000:.1f} mm (solid)")
        report.append(f"   ARB tip rate: {rear['arb_tip_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {rear['spring_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {rear['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   Primary roll stiffness: {rear['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary roll stiffness: {rear['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {rear['aux_percent']:.1f}% "
                     f"(max {self.target.rear_aux_percent_max}%)")
        report.append(f"   In range: {'✓' if results['rear_aux_in_range'] else '✗'}")
        
        # Total roll stiffness
        report.append(f"\n5. TOTAL ROLL STIFFNESS: {results['total_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Front contribution: {front['total_roll_stiffness']:,.0f} Nm/rad "
                     f"({front['total_roll_stiffness']/results['total_roll_stiffness']*100:.1f}%)")
        report.append(f"   Rear contribution: {rear['total_roll_stiffness']:,.0f} Nm/rad "
                     f"({rear['total_roll_stiffness']/results['total_roll_stiffness']*100:.1f}%)")
        
        # Understeer budget
        report.append("\n6. UNDERSTEER BUDGET (deg/g)")
        report.append(f"   Roll steer:                      {understeer.roll_steer:+.3f}")
        report.append(f"   Roll camber:                     {understeer.roll_camber:+.3f}")
        report.append(f"   Lateral force compliance steer:  {understeer.lateral_force_compliance_steer:+.3f}")
        report.append(f"   Lateral force compliance camber: {understeer.lateral_force_compliance_camber:+.3f}")
        report.append(f"   Aligning torque compliance steer:{understeer.aligning_torque_compliance_steer:+.3f}")
        report.append(f"   Weight distribution:             {understeer.weight_distribution:+.3f}")
        report.append(f"   Aligning torque steer:           {understeer.aligning_torque_steer:+.3f}")
        report.append(f"   " + "-" * 50)
        report.append(f"   TOTAL UNDERSTEER GRADIENT:       {understeer.total():+.3f} deg/g")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example: Passenger car design case
    
    vehicle = VehicleParams(
        total_mass=1450,
        sprung_mass=1300,
        wheelbase=2.65,
        front_track=1.55,
        rear_track=1.53,
        front_weight=7850,  # N (55% front)
        rear_weight=6400,   # N (45% rear)
        total_cg_height=0.52,
        sprung_cg_height=0.55,
        front_rc_height=0.05,
        rear_rc_height=0.08,
        front_unsprung_mass=70,
        rear_unsprung_mass=80,
    )
    
    front_axle = AxleParams(
        spring_rate=35000,
        motion_ratio=0.95,
        track_width=1.55,
        arb_d_od=0.0228,  # 22.8 mm - tune this to meet roll gradient
        arb_center_length=0.9,
        arb_arm_length=0.25,
        # K&C Parameters per Skill-Lync constraints
        roll_steer_gradient=6.5,  # % = 6.5 deg steer per 100 deg roll → 0.065 deg/deg
        camber_per_roll=90.0,  # % = 90 deg camber per 100 deg roll → 0.90 deg/deg
        lateral_force_steer_compliance=0.05 / 1000,  # 0.05 deg/kN → rad/N
        lateral_force_camber_compliance=0.3 / 1000,  # 0.3 deg/kN → rad/N
        aligning_torque_steer_compliance=0.4 / 100 * math.pi/180 / 1000,  # 0.4 deg/100Nm → rad/Nm
    )
    
    rear_axle = AxleParams(
        spring_rate=30000,
        motion_ratio=0.90,
        track_width=1.53,
        arb_d_od=0.0135,  # 13.5 mm - tune this to meet roll gradient
        arb_center_length=0.9,
        arb_arm_length=0.22,
        # K&C Parameters per Skill-Lync constraints (using mid-range values)
        roll_steer_gradient=-6.0,  # % = -6 deg steer per 100 deg roll (range -4 to -8)
        camber_per_roll=65.0,  # % = 65 deg camber per 100 deg roll (range 50-80)
        lateral_force_steer_compliance=0.012 / 1000,  # 0.012 deg/kN (range 0.008-0.015)
        lateral_force_camber_compliance=0.25 / 1000,  # 0.25 deg/kN (range 0.15-0.4)
        aligning_torque_steer_compliance=0.08 / 100 * math.pi/180 / 1000,  # 0.08 deg/100Nm (range 0.06-0.1)
    )
    
    tire_front = TireParams(
        cornering_stiffness=80000,  # N/rad (both tires)
        camber_stiffness=8000,
        vertical_stiffness=200000,
        pneumatic_trail=0.015,
    )
    
    tire_rear = TireParams(
        cornering_stiffness=85000,
        camber_stiffness=8500,
        vertical_stiffness=210000,
        pneumatic_trail=0.014,
    )
    
    target = RollGradientTarget(
        target_deg_per_g_min=3.5,
        target_deg_per_g_max=3.8,
        front_aux_percent_max=60,
        rear_aux_percent_max=25,
    )
    
    calc = VehicleDynamicsCalculator(
        vehicle=vehicle,
        front=front_axle,
        rear=rear_axle,
        tire_front=tire_front,
        tire_rear=tire_rear,
        target=target,
    )
    
    # Optimize ARB diameters to meet roll gradient target
    print("Optimizing ARB diameters to meet roll gradient target...")
    results = calc.optimize_arb_diameters()
    
    # Optimize K&C parameters
    kc_constraints = KCConstraints()
    kc_selected = calc.optimize_kc_parameters(kc_constraints)
    
    print(calc.generate_report())
    print(calc.generate_constraint_table())