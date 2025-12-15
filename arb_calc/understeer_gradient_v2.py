"""Vehicle dynamics calculator for ARB sizing and understeer budget.

Based on Skill-Lync project methodology:
- Design ARB diameters to meet target roll gradient
- Select K&C parameters to meet target understeer budget

All SI units (m, kg, N, rad) unless noted.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
import arb_calc
import json
import sys

GRAVITY = 9.81  # m/s^2


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
    
    @classmethod
    def from_dict(cls, data: dict) -> KCConstraints:
        """Create KCConstraints from dictionary."""
        return cls(
            roll_steer_front=(data.get("roll_steer_front_min", 3.0), data.get("roll_steer_front_max", 6.5)),
            roll_steer_rear=(data.get("roll_steer_rear_min", -8.0), data.get("roll_steer_rear_max", -3.0)),
            roll_camber_front=(data.get("roll_camber_front_min", 80.0), data.get("roll_camber_front_max", 90.0)),
            roll_camber_rear=(data.get("roll_camber_rear_min", 50.0), data.get("roll_camber_rear_max", 65.0)),
            lateral_force_steer_compliance_front=(data.get("lateral_force_steer_compliance_front_min", 0.008), data.get("lateral_force_steer_compliance_front_max", 0.05)),
            lateral_force_steer_compliance_rear=(data.get("lateral_force_steer_compliance_rear_min", 0.015), data.get("lateral_force_steer_compliance_rear_max", 0.04)),
            lateral_force_camber_compliance_front=(data.get("lateral_force_camber_compliance_front_min", 0.1), data.get("lateral_force_camber_compliance_front_max", 0.3)),
            lateral_force_camber_compliance_rear=(data.get("lateral_force_camber_compliance_rear_min", 0.15), data.get("lateral_force_camber_compliance_rear_max", 0.4)),
            aligning_torque_steer_compliance_front=(data.get("aligning_torque_steer_compliance_front_min", 0.2), data.get("aligning_torque_steer_compliance_front_max", 0.4)),
            aligning_torque_steer_compliance_rear=(data.get("aligning_torque_steer_compliance_rear_min", 0.06), data.get("aligning_torque_steer_compliance_rear_max", 0.1)),
        )


@dataclass
class VehicleParams:
    """Basic vehicle parameters."""
    total_mass: float  # kg
    sprung_mass: float  # kg
    wheelbase: float  # m
    front_track: float  # m
    rear_track: float  # m
    front_weight: float  # N
    rear_weight: float  # N
    total_cg_height: float  # m from ground
    sprung_cg_height: float  # m from ground
    front_rc_height: float  # m from ground
    rear_rc_height: float  # m from ground
    front_unsprung_mass: float  # kg per axle
    rear_unsprung_mass: float  # kg per axle
    
    def __post_init__(self):
        """Calculate derived parameters."""
        self.weight_front_ratio = self.front_weight / (self.front_weight + self.rear_weight)
        self.weight_rear_ratio = 1.0 - self.weight_front_ratio
    
    @classmethod
    def from_dict(cls, data: dict) -> VehicleParams:
        """Create VehicleParams from dictionary."""
        return cls(
            total_mass=data["total_mass"],
            sprung_mass=data["sprung_mass"],
            wheelbase=data["wheelbase"],
            front_track=data["front_track"],
            rear_track=data["rear_track"],
            front_weight=data["front_weight"],
            rear_weight=data["rear_weight"],
            total_cg_height=data["total_cg_height"],
            sprung_cg_height=data["sprung_cg_height"],
            front_rc_height=data["front_rc_height"],
            rear_rc_height=data["rear_rc_height"],
            front_unsprung_mass=data["front_unsprung_mass"],
            rear_unsprung_mass=data["rear_unsprung_mass"],
        )


@dataclass
class AxleParams:
    """Suspension parameters for one axle."""
    spring_rate: float  # N/m at spring
    motion_ratio: float  # wheel travel / spring travel
    track_width: float  # m
    arb_shear_modulus: float = 80e9  # Pa
    arb_young_modulus: float = 210e9  # Pa
    arb_center_length: float = 0.9  # m
    arb_arm_length: float = 0.25  # m
    arb_d_od: float = 0.020  # m
    arb_d_id: float = 0.0  # m (solid bar)
    
    # K&C Parameters
    roll_steer_gradient: float = 6.5  # %
    camber_per_roll: float = 90.0  # %
    lateral_force_steer_compliance: float = 0.0  # rad/N
    lateral_force_camber_compliance: float = 0.0  # rad/N
    aligning_torque_steer_compliance: float = 0.0  # rad/Nm
    
    @classmethod
    def from_dict(cls, data: dict) -> AxleParams:
        """Create AxleParams from dictionary."""
        return cls(
            spring_rate=data.get("spring_rate", 30000),  # Default, will be overridden if ride_frequency provided
            motion_ratio=data["motion_ratio"],
            track_width=data["track_width"],
            arb_shear_modulus=data.get("arb_shear_modulus", 80e9),
            arb_young_modulus=data.get("arb_young_modulus", 210e9),
            arb_center_length=data.get("arb_center_length", 0.9),
            arb_arm_length=data.get("arb_arm_length", 0.25),
            arb_d_od=data.get("arb_d_od", 0.020),
            arb_d_id=data.get("arb_d_id", 0.0),
        )


@dataclass
class TireParams:
    """Tire characteristics for one axle."""
    cornering_stiffness: float  # N/rad
    camber_stiffness: float  # N/rad
    vertical_stiffness: float  # N/m
    pneumatic_trail: float = 0.015  # m
    
    @classmethod
    def from_dict(cls, data: dict) -> TireParams:
        """Create TireParams from dictionary."""
        return cls(
            cornering_stiffness=data["cornering_stiffness"],
            camber_stiffness=data["camber_stiffness"],
            vertical_stiffness=data["vertical_stiffness"],
            pneumatic_trail=data.get("pneumatic_trail", 0.015),
        )


@dataclass
class RollGradientTarget:
    """Roll gradient design targets."""
    target_deg_per_g_min: float = 3.5
    target_deg_per_g_max: float = 3.8
    front_aux_percent_max: float = 60.0
    rear_aux_percent_max: float = 25.0
    
    @classmethod
    def from_dict(cls, data: dict) -> RollGradientTarget:
        """Create RollGradientTarget from dictionary."""
        return cls(
            target_deg_per_g_min=data.get("target_deg_per_g_min", 3.5),
            target_deg_per_g_max=data.get("target_deg_per_g_max", 3.8),
            front_aux_percent_max=data.get("front_aux_percent_max", 60.0),
            rear_aux_percent_max=data.get("rear_aux_percent_max", 25.0),
        )


@dataclass
class UndersteerBudget:
    """Understeer gradient components."""
    roll_steer: float = 0.0
    roll_camber: float = 0.0
    lateral_force_compliance_steer: float = 0.0
    lateral_force_compliance_camber: float = 0.0
    aligning_torque_compliance_steer: float = 0.0
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
        self.torque_arm_height = self._calculate_torque_arm()
    
    def _calculate_torque_arm(self) -> float:
        """Torque arm for roll moment."""
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
        self, axle: AxleParams, arb_tip_rate: float
    ) -> dict[str, float]:
        """Calculate roll stiffness breakdown for one axle."""
        k_spring_wheel = axle.spring_rate * axle.motion_ratio ** 2
        k_arb_wheel = arb_tip_rate * axle.motion_ratio ** 2
        
        k_phi_spring = arb_calc.roll_stiffness_from_wheel_rate(
            k_spring_wheel, axle.track_width
        )
        k_phi_arb = arb_calc.roll_stiffness_from_wheel_rate(
            k_arb_wheel, axle.track_width
        )
        
        return {
            "spring_wheel_rate": k_spring_wheel,
            "arb_wheel_rate": k_arb_wheel,
            "spring_roll_stiffness": k_phi_spring,
            "arb_roll_stiffness": k_phi_arb,
            "total_roll_stiffness": k_phi_spring + k_phi_arb,
            "arb_tip_rate": arb_tip_rate,
            "aux_percent": (k_phi_arb / (k_phi_spring + k_phi_arb)) * 100,
        }
    
    def calculate_roll_gradient(self, total_roll_stiffness: float) -> float:
        """Roll gradient in deg/g."""
        return arb_calc.roll_gradient_deg_per_g(
            total_roll_stiffness=total_roll_stiffness,
            sprung_mass=self.vehicle.sprung_mass,
            torque_arm_height=self.torque_arm_height,
        )
    
    def optimize_arb_diameters(self) -> dict:
        """Iteratively size ARB diameters to meet roll gradient target."""
        front_d_min, front_d_max = 0.010, 0.040
        rear_d_min, rear_d_max = 0.008, 0.025
        
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
                front_d_max = front_d_mid
            else:
                front_d_min = front_d_mid
        
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
                rear_d_max = rear_d_mid
            else:
                rear_d_min = rear_d_mid
        
        # Final calculation
        self.front.arb_d_od = (front_d_min + front_d_max) / 2.0
        self.rear.arb_d_od = (rear_d_min + rear_d_max) / 2.0
        
        front_tip = self.calculate_arb_tip_rate(self.front)
        rear_tip = self.calculate_arb_tip_rate(self.rear)
        
        front_data = self.calculate_axle_roll_stiffness(self.front, front_tip)
        rear_data = self.calculate_axle_roll_stiffness(self.rear, rear_tip)
        
        total_k_phi = front_data["total_roll_stiffness"] + rear_data["total_roll_stiffness"]
        current_rg = self.calculate_roll_gradient(total_k_phi)
        
        return {
            "front": front_data,
            "rear": rear_data,
            "total_roll_stiffness": total_k_phi,
            "roll_gradient_deg_per_g": current_rg,
            "meets_target": (
                self.target.target_deg_per_g_min <= current_rg <= 
                self.target.target_deg_per_g_max
            ),
        }
    
    def optimize_kc_parameters(self, kc_constraints: KCConstraints) -> dict:
        """Select K&C parameters to maximize understeer."""
        self.front.roll_steer_gradient = kc_constraints.roll_steer_front[1]
        self.rear.roll_steer_gradient = kc_constraints.roll_steer_rear[0]
        
        self.front.camber_per_roll = kc_constraints.roll_camber_front[1]
        self.rear.camber_per_roll = kc_constraints.roll_camber_rear[0]
        
        # Convert deg/kN to rad/N: (deg/1000N) * (π/180 rad/deg) = (deg * π/180) / 1000 rad/N
        self.front.lateral_force_steer_compliance = kc_constraints.lateral_force_steer_compliance_front[1] * math.pi/180 / 1000
        self.rear.lateral_force_steer_compliance = kc_constraints.lateral_force_steer_compliance_rear[0] * math.pi/180 / 1000
        
        self.front.lateral_force_camber_compliance = kc_constraints.lateral_force_camber_compliance_front[1] * math.pi/180 / 1000
        self.rear.lateral_force_camber_compliance = kc_constraints.lateral_force_camber_compliance_rear[0] * math.pi/180 / 1000
        
        # Convert deg/100Nm to rad/Nm: (deg/100Nm) * (π/180 rad/deg) = (deg * π/180) / 100 rad/Nm
        self.front.aligning_torque_steer_compliance = kc_constraints.aligning_torque_steer_compliance_front[1] * math.pi/180 / 100
        self.rear.aligning_torque_steer_compliance = kc_constraints.aligning_torque_steer_compliance_rear[0] * math.pi/180 / 100
    
    def calculate_understeer_budget(
        self, roll_gradient_deg_per_g: float, lateral_accel_g: float = 1.0
    ) -> UndersteerBudget:
        """Calculate all understeer gradient components."""
        budget = UndersteerBudget()
        roll_grad_rad = math.radians(roll_gradient_deg_per_g)
        
        F_yf = self.vehicle.front_weight * lateral_accel_g
        F_yr = self.vehicle.rear_weight * lateral_accel_g
        
        # Roll steer
        epsilon_f = math.radians(self.front.roll_steer_gradient / 100.0)
        epsilon_r = math.radians(self.rear.roll_steer_gradient / 100.0)
        budget.roll_steer = math.degrees((epsilon_f - epsilon_r) * roll_grad_rad)
        
        # Roll camber
        gamma_f_per_roll = math.radians(self.front.camber_per_roll / 100.0)
        gamma_r_per_roll = math.radians(self.rear.camber_per_roll / 100.0)
        
        camber_gain_f = gamma_f_per_roll * roll_grad_rad * (
            self.tire_front.camber_stiffness / self.tire_front.cornering_stiffness
        )
        camber_gain_r = gamma_r_per_roll * roll_grad_rad * (
            self.tire_rear.camber_stiffness / self.tire_rear.cornering_stiffness
        )
        budget.roll_camber = math.degrees(camber_gain_f - camber_gain_r)
        
        # Lateral force compliance steer
        lfcs = (self.front.lateral_force_steer_compliance * F_yf - 
                self.rear.lateral_force_steer_compliance * F_yr)
        budget.lateral_force_compliance_steer = math.degrees(lfcs)
        
        # Lateral force compliance camber
        lfcc_f = (self.front.lateral_force_camber_compliance * F_yf * 
                 self.tire_front.camber_stiffness / self.tire_front.cornering_stiffness)
        lfcc_r = (self.rear.lateral_force_camber_compliance * F_yr * 
                 self.tire_rear.camber_stiffness / self.tire_rear.cornering_stiffness)
        budget.lateral_force_compliance_camber = math.degrees(lfcc_f - lfcc_r)
        
        # Aligning torque compliance steer
        AT_f = self.tire_front.pneumatic_trail * self.vehicle.front_weight * lateral_accel_g
        AT_r = self.tire_rear.pneumatic_trail * self.vehicle.rear_weight * lateral_accel_g
        atcs = (self.front.aligning_torque_steer_compliance * AT_f - 
                self.rear.aligning_torque_steer_compliance * AT_r)
        budget.aligning_torque_compliance_steer = math.degrees(atcs)
        
        # Weight distribution
        wd = (self.vehicle.front_weight / self.tire_front.cornering_stiffness - 
              self.vehicle.rear_weight / self.tire_rear.cornering_stiffness)
        budget.weight_distribution = math.degrees(wd)
        
        # Aligning torque steer
        at_steer = ((AT_f + AT_r) / 
                   (self.vehicle.wheelbase * 
                    (self.tire_front.cornering_stiffness + self.tire_rear.cornering_stiffness)))
        budget.aligning_torque_steer = math.degrees(at_steer)
        
        return budget
    
    def generate_report(self, results: dict, understeer: UndersteerBudget) -> str:
        """Generate comprehensive design report."""
        report = []
        report.append("=" * 100)
        report.append("VEHICLE DYNAMICS DESIGN REPORT - ARB Sizing & Understeer Budget")
        report.append("=" * 100)
        
        report.append("\n1. VEHICLE PARAMETERS")
        report.append(f"   Total mass: {self.vehicle.total_mass:.0f} kg")
        report.append(f"   Sprung mass: {self.vehicle.sprung_mass:.0f} kg")
        report.append(f"   Weight distribution: {self.vehicle.weight_front_ratio*100:.1f}% F / {self.vehicle.weight_rear_ratio*100:.1f}% R")
        report.append(f"   Torque arm height: {self.torque_arm_height:.3f} m")
        
        report.append("\n2. ROLL GRADIENT DESIGN")
        report.append(f"   Target range: {self.target.target_deg_per_g_min:.2f} - {self.target.target_deg_per_g_max:.2f} deg/g")
        report.append(f"   Achieved: {results['roll_gradient_deg_per_g']:.3f} deg/g")
        deviation = abs(results['roll_gradient_deg_per_g'] - 3.8) / 3.8 * 100
        report.append(f"   Deviation: {deviation:.1f}% (target within 5%)")
        report.append(f"   Status: {'✓' if results['meets_target'] else '✗'}")
        
        front = results["front"]
        report.append("\n3. FRONT AXLE")
        report.append(f"   ARB diameter: {self.front.arb_d_od*1000:.2f} mm")
        report.append(f"   ARB tip rate: {front['arb_tip_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {front['spring_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {front['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   Primary roll stiffness: {front['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary roll stiffness: {front['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {front['aux_percent']:.2f}% (max {self.target.front_aux_percent_max}%)")
        
        rear = results["rear"]
        report.append("\n4. REAR AXLE")
        report.append(f"   ARB diameter: {self.rear.arb_d_od*1000:.2f} mm")
        report.append(f"   ARB tip rate: {rear['arb_tip_rate']:,.0f} N/m")
        report.append(f"   Spring wheel rate: {rear['spring_wheel_rate']:,.0f} N/m")
        report.append(f"   ARB wheel rate: {rear['arb_wheel_rate']:,.0f} N/m")
        report.append(f"   Primary roll stiffness: {rear['spring_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary roll stiffness: {rear['arb_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Auxiliary %: {rear['aux_percent']:.2f}% (max {self.target.rear_aux_percent_max}%)")
        
        report.append(f"\n5. TOTAL ROLL STIFFNESS: {results['total_roll_stiffness']:,.0f} Nm/rad")
        report.append(f"   Front contribution: {front['total_roll_stiffness']:,.0f} Nm/rad ({front['total_roll_stiffness']/results['total_roll_stiffness']*100:.1f}%)")
        report.append(f"   Rear contribution: {rear['total_roll_stiffness']:,.0f} Nm/rad ({rear['total_roll_stiffness']/results['total_roll_stiffness']*100:.1f}%)")
        
        report.append("\n6. UNDERSTEER BUDGET (deg/g at 1.0g lateral acceleration)")
        report.append(f"   Roll steer:                      {understeer.roll_steer:+.3f}")
        report.append(f"   Roll camber:                     {understeer.roll_camber:+.3f}")
        report.append(f"   Lateral force compliance steer:  {understeer.lateral_force_compliance_steer:+.3f}")
        report.append(f"   Lateral force compliance camber: {understeer.lateral_force_compliance_camber:+.3f}")
        report.append(f"   Aligning torque compliance:      {understeer.aligning_torque_compliance_steer:+.3f}")
        report.append(f"   Weight distribution:             {understeer.weight_distribution:+.3f}")
        report.append(f"   Aligning torque steer:           {understeer.aligning_torque_steer:+.3f}")
        report.append(f"   " + "-" * 50)
        report.append(f"   TOTAL UNDERSTEER GRADIENT:       {understeer.total():+.3f} deg/g")
        
        report.append("\n" + "=" * 100)
        return "\n".join(report)
    
    def generate_constraint_table(self) -> str:
        """Generate detailed K&C constraints and selected values table."""
        table = []
        table.append("\n" + "=" * 130)
        table.append("K&C PARAMETER CONSTRAINTS AND SELECTED VALUES")
        table.append("=" * 130)
        
        # Get current roll stiffness data to show aux percentages
        front_tip = self.calculate_arb_tip_rate(self.front)
        rear_tip = self.calculate_arb_tip_rate(self.rear)
        front_data = self.calculate_axle_roll_stiffness(self.front, front_tip)
        rear_data = self.calculate_axle_roll_stiffness(self.rear, rear_tip)
        
        constraints_data = [
            ("Auxiliary roll stiffness front (%)", 25, 60, front_data["aux_percent"]),
            ("Auxiliary roll stiffness rear (%)", 0, 20, rear_data["aux_percent"]),
            ("Roll steer front (%)", 3.0, 6.5, self.front.roll_steer_gradient),
            ("Roll steer rear (%)", -8.0, -3.0, self.rear.roll_steer_gradient),
            ("Roll camber front (%)", 80.0, 90.0, self.front.camber_per_roll),
            ("Roll camber rear (%)", 50.0, 65.0, self.rear.camber_per_roll),
            ("Lateral force compliance steer front (deg/kN)", 0.008, 0.05, self.front.lateral_force_steer_compliance * 180/math.pi * 1000),
            ("Lateral force compliance steer rear (deg/kN)", 0.015, 0.04, self.rear.lateral_force_steer_compliance * 180/math.pi * 1000),
            ("Lateral force compliance camber front (deg/kN)", 0.1, 0.3, self.front.lateral_force_camber_compliance * 180/math.pi * 1000),
            ("Lateral force compliance camber rear (deg/kN)", 0.15, 0.4, self.rear.lateral_force_camber_compliance * 180/math.pi * 1000),
            ("Aligning torque compliance steer front (deg/100Nm)", 0.2, 0.4, self.front.aligning_torque_steer_compliance * 180/math.pi * 100),
            ("Aligning torque compliance steer rear (deg/100Nm)", 0.06, 0.1, self.rear.aligning_torque_steer_compliance * 180/math.pi * 100),
        ]
        
        table.append(f"\n{'Parameter':<55} {'Minimum':<15} {'Maximum':<15} {'Selected':<15} {'Status':<10}")
        table.append("-" * 130)
        
        for param_name, min_val, max_val, selected_val in constraints_data:
            in_range = min_val <= selected_val <= max_val
            status = "✓" if in_range else "✗"
            
            table.append(f"{param_name:<55} {min_val:<15.3f} {max_val:<15.3f} {selected_val:<15.3f} {status:<10}")
        
        table.append("-" * 130)
        table.append("=" * 130)
        
        return "\n".join(table)


if __name__ == "__main__":
    # Load from JSON file (default or command line argument)
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input_template.json"
    
    try:
        with open(input_file, "r") as f:
            config = json.load(f)
        print(f"Loaded configuration from: {input_file}\n")
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        print(f"Usage: python understeer_gradient_v2.py [input_file.json]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        sys.exit(1)
    
    # Create objects from loaded data
    vehicle = VehicleParams.from_dict(config["vehicle"])
    front_axle = AxleParams.from_dict(config["front_axle"])
    rear_axle = AxleParams.from_dict(config["rear_axle"])
    
    # Calculate spring rates from ride frequency if provided
    # Formula: f = (1/2π) * √(k_wheel/m_corner)
    # Therefore: k_spring = (2π*f)² * m_corner / MR²
    if "ride_frequency" in config["front_axle"]:
        f_front = config["front_axle"]["ride_frequency"]  # Hz
        m_corner_front = vehicle.sprung_mass * vehicle.weight_front_ratio / 2  # kg per corner
        k_spring_front = (2 * math.pi * f_front) ** 2 * m_corner_front / (front_axle.motion_ratio ** 2)
        front_axle.spring_rate = k_spring_front
        print(f"Front spring rate calculated from ride frequency {f_front:.2f} Hz: {k_spring_front:,.0f} N/m")
    
    if "ride_frequency" in config["rear_axle"]:
        f_rear = config["rear_axle"]["ride_frequency"]  # Hz
        m_corner_rear = vehicle.sprung_mass * vehicle.weight_rear_ratio / 2  # kg per corner
        k_spring_rear = (2 * math.pi * f_rear) ** 2 * m_corner_rear / (rear_axle.motion_ratio ** 2)
        rear_axle.spring_rate = k_spring_rear
        print(f"Rear spring rate calculated from ride frequency {f_rear:.2f} Hz: {k_spring_rear:,.0f} N/m\n")
    tire_front = TireParams.from_dict(config["tire_front"])
    tire_rear = TireParams.from_dict(config["tire_rear"])
    target = RollGradientTarget.from_dict(config["roll_gradient_target"])
    
    calc = VehicleDynamicsCalculator(
        vehicle=vehicle,
        front=front_axle,
        rear=rear_axle,
        tire_front=tire_front,
        tire_rear=tire_rear,
        target=target,
    )
    
    print("Optimizing ARB diameters to meet roll gradient target (3.5-3.8 deg/g)...")
    results = calc.optimize_arb_diameters()
    
    print("Optimizing K&C parameters to maximize understeer...")
    kc_constraints = KCConstraints.from_dict(config["kc_constraints"])
    calc.optimize_kc_parameters(kc_constraints)
    
    # Calculate final understeer budget
    understeer = calc.calculate_understeer_budget(results["roll_gradient_deg_per_g"])
    
    print(calc.generate_report(results, understeer))
    print(calc.generate_constraint_table())
