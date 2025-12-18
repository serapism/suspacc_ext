# Suspension & ARB Design Calculator

## Overview

The **Suspension & ARB Design Calculator** is a specialized engineering tool designed for vehicle dynamics analysis. It assists engineers in calculating ride frequencies, roll stiffness requirements, and detailed Anti-Roll Bar (ARB) design parameters using both geometric and strain energy methods.

Built with Python and Tkinter, it features a tabbed Graphical User Interface (GUI) that streamlines the workflow from initial vehicle mass inputs to final component sizing.

## Features

### 1. Ride Frequency Analysis
Calculates the required spring stiffness to achieve target ride frequencies.
*   **Inputs:** Front/Rear axle weights, unsprung masses, tire stiffness, motion ratios, and parametric stiffness.
*   **Outputs:** Spring rates, wheel rates, ride rates, and wheel hop frequencies.
*   **Visuals:** Real-time weight distribution calculation.

### 2. Roll Stiffness Calculation
Determines the required roll stiffness distribution based on a 14-step vehicle dynamics methodology.
*   **Inputs:** Vehicle geometry (CG height, roll centers, track widths), wheel rates, and target roll gradients.
*   **Outputs:** Roll moment calculation, tire roll stiffness contribution, spring contribution, and the resulting required ARB stiffness for front and rear.

### 3. ARB Design (Geometric)
Sizes the Anti-Roll Bar based on the requirements calculated in the Roll Stiffness tab.
*   **Inputs:** Bush stiffness, clamp spans, eye spans, and lever ratios.
*   **Outputs:** Required bar stiffness, bush lever ratios, and combined eye stiffness.

### 4. ARB Energy Method
An advanced calculator that uses the **Strain Energy Method** to determine the exact stiffness of an ARB.
*   **Methodology:** Accounts for bending and torsional energy in the straight section, bends, and arms.
*   **Inputs:** Detailed geometry (eyeball span, shoulder span, arm length, bend radius), material properties (Young's Modulus, Shear Modulus), and cross-section details (solid or hollow).
*   **Outputs:** Precise spring rate (N/mm), bar mass, moments of inertia, and a detailed breakdown of strain energy per section.

## Getting Started

### Prerequisites
*   **Python 3.x**
*   **Tkinter** (Standard Python GUI library, usually included with Python installations)

### Installation
No specific installation is required. Ensure the source files are in a directory and run the main script.

### Usage
Run the main application file:

```bash
python src_py/roll_stiff_new_arb_dia.py
```

*(Note: Adjust the path according to your specific file structure if necessary)*

## Workflow

The application is designed to be used sequentially, though tabs function independently:

1.  **Ride Frequency:** Establish baseline spring rates.
2.  **Roll Stiffness:** Use the calculated spring rates to determine how much additional roll stiffness is needed from ARBs.
3.  **ARB Design:** Size the ARB system (bars + bushings) to meet the roll stiffness targets.
4.  **ARB Energy Method:** Verify the specific bar geometry to ensure it delivers the calculated stiffness.

## Version Information

*   **Version:** 1.0.0
*   **Release Date:** December 2024
*   **Created by:** Nirmal
*   **Organization:** CEER