"""Anti-roll bar and roll-stiffness helpers.

Sources:
- Suspension Secrets: torsion + cantilever stiffness and springs-in-series ARB model.
- Skill-Lync ARB project: wheel-center roll stiffness k_phi = k_wheel * t^2 / 2 and roll-gradient sizing.

All lengths in meters and rates in N/m unless otherwise stated.
"""

from __future__ import annotations

import math

GRAVITY = 9.81  # m/s^2


def polar_second_moment(d_od: float, d_id: float = 0.0) -> float:
    """Polar second moment J for a round (solid or tubular) section, m^4."""
    if d_od <= 0:
        raise ValueError("Outer diameter must be positive")
    if d_id < 0 or d_id >= d_od:
        raise ValueError("Inner diameter must be >= 0 and < outer diameter")
    return math.pi / 32.0 * (d_od ** 4 - d_id ** 4)


def area_moment_round(d_od: float, d_id: float = 0.0) -> float:
    """Area moment of inertia I for a round section, m^4."""
    if d_od <= 0:
        raise ValueError("Outer diameter must be positive")
    if d_id < 0 or d_id >= d_od:
        raise ValueError("Inner diameter must be >= 0 and < outer diameter")
    return math.pi / 64.0 * (d_od ** 4 - d_id ** 4)


def torsion_stiffness(
    shear_modulus: float,
    d_od: float,
    center_length: float,
    arm_length: float,
    d_id: float = 0.0,
) -> float:
    """Vertical stiffness at one arm tip from bar torsion only (Suspension Secrets).

    k = G*J / (L * r^2)
    """
    if center_length <= 0 or arm_length <= 0:
        raise ValueError("Center length and arm length must be positive")
    J = polar_second_moment(d_od, d_id)
    return shear_modulus * J / (center_length * arm_length ** 2)


def cantilever_stiffness(
    young_modulus: float,
    d_od: float,
    arm_length: float,
    d_id: float = 0.0,
) -> float:
    """Vertical stiffness of a round-section cantilever arm (Suspension Secrets).

    k = 3*E*I / L^3
    """
    if arm_length <= 0:
        raise ValueError("Arm length must be positive")
    I = area_moment_round(d_od, d_id)
    return 3.0 * young_modulus * I / (arm_length ** 3)


def series_rate(*rates: float) -> float:
    """Combine stiffnesses in series: 1/k = sum(1/k_i)."""
    finite = [r for r in rates if r > 0]
    if not finite:
        raise ValueError("At least one positive stiffness is required")
    return 1.0 / sum(1.0 / r for r in finite)


def arb_tip_rate(
    shear_modulus: float,
    young_modulus: float,
    d_od: float,
    center_length: float,
    arm_length: float,
    d_id: float = 0.0,
    arm_rate_left: float | None = None,
    arm_rate_right: float | None = None,
) -> float:
    """Total vertical stiffness at the ARB arm tip (one side loaded).

    Springs-in-series model per Suspension Secrets: left arm + bar torsion + right arm.
    If arm_rate_* not provided, both arms use the cantilever stiffness from geometry.
    """
    k_arm_default = cantilever_stiffness(young_modulus, d_od, arm_length, d_id)
    k_left = arm_rate_left if arm_rate_left is not None else k_arm_default
    k_right = arm_rate_right if arm_rate_right is not None else k_arm_default
    k_torsion = torsion_stiffness(shear_modulus, d_od, center_length, arm_length, d_id)
    return series_rate(k_left, k_torsion, k_right)


def wheel_rate_from_tip(tip_rate: float, motion_ratio: float) -> float:
    """Convert bar tip rate to wheel vertical rate using MR (wheel / bar-tip)."""
    if motion_ratio <= 0:
        raise ValueError("Motion ratio must be positive")
    return tip_rate * motion_ratio ** 2


def roll_stiffness_from_wheel_rate(wheel_rate: float, track_width: float) -> float:
    """Roll stiffness contribution of one axle: k_phi = k_wheel * t^2 / 2 (Skill-Lync)."""
    if track_width <= 0:
        raise ValueError("Track width must be positive")
    return wheel_rate * (track_width ** 2) / 2.0


def axle_roll_stiffness(
    spring_rate: float,
    arb_tip_vertical_rate: float,
    motion_ratio: float,
    track_width: float,
) -> dict[str, float]:
    """Return spring/ARB wheel rates and roll stiffness for one axle (Skill-Lync layout)."""
    k_s_wheel = spring_rate * motion_ratio ** 2
    k_arb_wheel = arb_tip_vertical_rate * motion_ratio ** 2
    k_phi_s = roll_stiffness_from_wheel_rate(k_s_wheel, track_width)
    k_phi_arb = roll_stiffness_from_wheel_rate(k_arb_wheel, track_width)
    return {
        "spring_wheel_rate": k_s_wheel,
        "arb_wheel_rate": k_arb_wheel,
        "spring_roll_stiffness": k_phi_s,
        "arb_roll_stiffness": k_phi_arb,
        "total_roll_stiffness": k_phi_s + k_phi_arb,
    }


def roll_gradient_deg_per_g(
    total_roll_stiffness: float,
    sprung_mass: float,
    torque_arm_height: float,
) -> float:
    """Compute roll gradient (deg/g): phi/Ay = (m*g*h_arm)/k_phi (Skill-Lync)."""
    if total_roll_stiffness <= 0:
        raise ValueError("Total roll stiffness must be positive")
    phi_rad_per_g = sprung_mass * GRAVITY * torque_arm_height / total_roll_stiffness
    return math.degrees(phi_rad_per_g)


def arb_axle_summary(
    shear_modulus: float,
    young_modulus: float,
    d_od: float,
    center_length: float,
    arm_length: float,
    spring_rate: float,
    motion_ratio: float,
    track_width: float,
    d_id: float = 0.0,
) -> dict[str, float]:
    """One-call helper: geometry -> tip rate -> wheel rates -> roll stiffness."""

    tip_rate = arb_tip_rate(
        shear_modulus=shear_modulus,
        young_modulus=young_modulus,
        d_od=d_od,
        center_length=center_length,
        arm_length=arm_length,
        d_id=d_id,
    )
    axle = axle_roll_stiffness(
        spring_rate=spring_rate,
        arb_tip_vertical_rate=tip_rate,
        motion_ratio=motion_ratio,
        track_width=track_width,
    )
    axle["arb_tip_rate"] = tip_rate
    return axle


if __name__ == "__main__":
    # Simple usage example with steel bar and passenger-car dimensions (SI units).
    steel_E = 210e9  # Pa
    steel_G = 80e9  # Pa

    front = arb_axle_summary(
        shear_modulus=steel_G,
        young_modulus=steel_E,
        d_od=0.022,          # 22 mm bar
        center_length=0.9,   # 900 mm between bends
        arm_length=0.25,     # 250 mm lever
        spring_rate=35000.0, # N/m at the spring
        motion_ratio=0.95,
        track_width=1.55,
    )

    rear = arb_axle_summary(
        shear_modulus=steel_G,
        young_modulus=steel_E,
        d_od=0.014,          # 14 mm bar
        center_length=0.9,
        arm_length=0.22,
        spring_rate=30000.0,
        motion_ratio=0.90,
        track_width=1.53,
    )

    total_kphi = front["total_roll_stiffness"] + rear["total_roll_stiffness"]
    # Example torque arm (sprung CG height minus roll center effects).
    torque_arm = 0.45  # m
    sprung_mass = 1300.0  # kg
    rg = roll_gradient_deg_per_g(total_roll_stiffness=total_kphi, sprung_mass=sprung_mass, torque_arm_height=torque_arm)

    print("Front axle:", front)
    print("Rear axle:", rear)
    print("Total roll stiffness (Nm/rad):", total_kphi)
    print("Roll gradient (deg/g):", rg)