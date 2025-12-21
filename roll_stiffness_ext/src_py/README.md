# Suspension & ARB Design Calculator

## Overview

The **Suspension & ARB Design Calculator** is a comprehensive Python-based GUI application designed for vehicle dynamics engineering. It facilitates the calculation of ride frequencies, roll stiffness requirements, and detailed Anti-Roll Bar (ARB) design parameters using both simplified geometric models and advanced strain energy methods.

## Features

### 1. Ride Frequency Analysis
*   **Mass Management:** Input front/rear axle weights and unsprung masses to calculate sprung mass and weight distribution.
*   **Frequency Targets:** Calculate required spring rates based on target ride frequencies (Hz).
*   **Stiffness Calculations:** Computes wheel rates, ride rates, and wheel hop frequencies.
*   **Parametric Stiffness:** Accounts for auxiliary stiffness (bushings, links) acting in parallel with springs.

### 2. Roll Stiffness Calculation
*   **14-Step Methodology:** Implements a structured approach to roll dynamics.
*   **Geometry:** Calculates effective roll center heights and roll moment arms based on CG and suspension geometry.
*   **Requirements:** Determines total required roll stiffness to meet target roll gradients (deg/g).
*   **Distribution:** Calculates the split between tire stiffness, spring stiffness, and the remaining requirement for ARBs.

### 3. ARB Design (Simplified)
*   **Targeting:** Uses outputs from the Roll Stiffness tab to size ARBs.
*   **Linkage Effects:** Accounts for bush stiffness, clamp spans, eye spans, and motion ratios.
*   **Outputs:** Calculates required bar stiffness and combined eye stiffness.

### 4. ARB Energy Method (Advanced)
*   **Strain Energy Calculation:** Uses energy methods to calculate the exact stiffness of complex ARB shapes.
*   **Detailed Geometry:** Inputs for eyeball span, shoulder span, arm length, bend radii, and number of bends.
*   **Material Properties:** Supports custom Young's Modulus (E), Shear Modulus (G), and hollow vs. solid bars.
*   **Analysis:** Provides a breakdown of energy stored in bending vs. torsion for different sections of the bar.

### 5. Data Management
*   **Configuration System:** Save, load, update, and delete design configurations (JSON-based).
*   **Excel Export:** Export detailed reports of all tabs to `.xlsx` format for documentation.

## Prerequisites

*   **Python 3.x**
*   **tkinter** (Included with standard Python installations)

### Optional Dependencies
For the "Export to Excel" functionality, the following packages are required:

```bash
pip install pandas openpyxl
```

## Usage

Run the main application script:

```bash
python roll_stiff_new_arb_dia.py
```

### Workflow
1.  **Ride Frequency Tab:** Establish baseline vehicle masses and spring rates.
2.  **Roll Stiffness Tab:** Define vehicle geometry (CG, Roll Centers) and roll targets to determine how much roll stiffness the ARBs need to provide.
3.  **ARB Design Tab:** Define the linkage geometry (lever ratios, bush stiffness) to find the required bar stiffness.
4.  **ARB Energy Method Tab:** Use the "Auto-Fill" feature to import targets, then refine the physical bar geometry (bends, diameter) to match the required stiffness.

## File Structure

*   `roll_stiff_new_arb_dia.py`: Main application containing the GUI and all calculation logic.
*   `saved_configs.json`: (Created at runtime) Stores user-saved design configurations.

## Version Information

*   **Version:** 1.0.0
*   **Release Date:** December 2024
*   **Created By:** Nirmal (CEER)

## Future Implementations

*   7 DOF Analysis
*   Damping Curves
*   Other Loading Conditions