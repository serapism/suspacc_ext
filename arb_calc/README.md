# Anti-Roll Bar Calculator (arb_calc.py)

Helpers to size and evaluate anti-roll bars using formulas from Suspension Secrets and Skill-Lync. All lengths are meters and rates N/m unless noted.

## Core relationships
- Polar second moment (round bar): $J = \tfrac{\pi}{32}(d_{od}^4 - d_{id}^4)$
- Area moment (round): $I = \tfrac{\pi}{64}(d_{od}^4 - d_{id}^4)$
- Bar torsion to vertical tip rate (one arm): $k_{torsion} = \dfrac{GJ}{L\,r^2}$
- Cantilever arm rate: $k_{arm} = \dfrac{3EI}{L^3}$
- ARB tip rate (one side loaded): springs in series of left arm, torsion segment, right arm
- Wheel vertical rate from tip: $k_w = k_{tip}\,MR^2$
- Axle roll stiffness: $k_{\phi} = k_w\,t^2/2$
- Roll gradient: $\dfrac{\phi}{A_y} = \dfrac{m\,g\,h_{arm}}{k_{\phi,total}}$ (rad/g, convert to deg/g)

## Key functions (arb_calc.py)
- `arb_tip_rate(...)`: geometry and material -> arm-tip vertical rate via series model.
- `axle_roll_stiffness(...)`: spring and ARB tip rates -> wheel rates and axle roll stiffness.
- `arb_axle_summary(...)`: one-call wrapper that goes geometry -> tip rate -> roll stiffness breakdown.
- `roll_gradient_deg_per_g(...)`: total roll stiffness + torque arm -> roll gradient (deg/g).

## Quick start
Run the built-in example:

```
python arb_calc.py
```

Sample parameters in `__main__`:
- Steel bar (E=210e9 Pa, G=80e9 Pa)
- Front: 22 mm OD, 0.9 m center length, 0.25 m arm, MR 0.95, track 1.55 m, spring 35 kN/m
- Rear: 14 mm OD, 0.9 m center length, 0.22 m arm, MR 0.90, track 1.53 m, spring 30 kN/m
- Torque arm (CG height minus roll-center effects): 0.45 m, sprung mass 1300 kg

Outputs include per-axle spring/ARB wheel rates, roll stiffness, total $k_{\phi}$, and roll gradient (deg/g).

## Adapting
- Change `d_od`, `center_length`, `arm_length`, and `d_id` to match bar geometry.
- Adjust `motion_ratio` to your linkage; it scales both spring and ARB effects at the wheel.
- Use your track widths per axle; roll stiffness scales with $t^2$.
- Update `torque_arm_height` and `sprung_mass` to reflect your vehicle for roll gradient.

## Source notes
- Suspension Secrets: provides torsion + cantilever model and series combination for ARB stiffness.
- Skill-Lync ARB project: uses wheel-center roll stiffness $k_{\phi} = k_w t^2/2$ and roll-gradient sizing against targets (deg/g).