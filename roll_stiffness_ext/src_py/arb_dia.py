"""
ARB (Anti-Roll Bar) Stiffness Calculator
Based on spring model energy method with full intermediate outputs (C3-C76)
"""

import math
from typing import Dict, Optional


class ARBCalculator:
    """
    Calculate ARB stiffness using energy method.
    Outputs all intermediate calculations from C3 to C76.
    """
    
    # Default material properties
    DEFAULT_E = 210000  # Young's modulus, MPa (steel)
    DEFAULT_G = 80000   # Shear modulus, MPa (steel)
    
    def __init__(self):
        self.results: Dict[str, float] = {}
    
    def calculate(self,
                  k_supplier: float = 40.0,          # N/mm - supplier spring rate
                  eyeball_span: float = 1130.2,      # mm - total span between eyeball mounts
                  shoulder_span: float = 601.0,      # mm - span at shoulder/bend
                  clamp_span: float = 505.0,         # mm - clamp mounting span
                  arm_length: float = 201.5,         # mm - lever arm length
                  shoulder_R: float = 55.0,          # mm - shoulder bend radius
                  stroke: float = 25.0,              # mm - vertical stroke/displacement
                  material_diameter: float = 26.0,   # mm - outer diameter
                  wall_thickness: Optional[float] = None,  # mm - wall thickness (None = solid)
                  E: Optional[float] = None,         # MPa - Young's modulus
                  G: Optional[float] = None          # MPa - Shear modulus
                  ) -> Dict[str, float]:
        """
        Calculate ARB stiffness and all intermediate values.
        
        Parameters:
        -----------
        k_supplier : Supplier-specified spring rate (N/mm)
        eyeball_span : Total span between eyeball mounts (mm)
        shoulder_span : Span at shoulder/bend (mm)
        clamp_span : Clamp mounting span (mm)
        arm_length : Lever arm length (mm)
        shoulder_R : Shoulder bend radius (mm)
        stroke : Vertical stroke/displacement (mm)
        material_diameter : Outer diameter of bar (mm)
        wall_thickness : Wall thickness if hollow (mm), None for solid
        E : Young's modulus (MPa)
        G : Shear modulus (MPa)
        
        Returns:
        --------
        Dictionary with all calculated values C3-C76
        """
        
        # Apply defaults
        if E is None:
            E = self.DEFAULT_E
        if G is None:
            G = self.DEFAULT_G
        
        # Handle solid vs hollow bar
        if wall_thickness is None or wall_thickness <= 0 or wall_thickness >= material_diameter / 2:
            wall_thickness = material_diameter / 2  # Solid bar
        
        # Store inputs
        C7 = k_supplier
        C14 = eyeball_span
        C15 = shoulder_span
        C16 = clamp_span
        C17 = arm_length
        C18 = shoulder_R
        C19 = stroke
        C20 = material_diameter
        C21 = wall_thickness
        C37 = E
        C38 = G
        
        # Initialize results dictionary
        r: Dict[str, float] = {}
        
        # Store primary inputs (C7, C14-C21)
        r['C7'] = C7
        r['C14'] = C14
        r['C15'] = C15
        r['C16'] = C16
        r['C17'] = C17
        r['C18'] = C18
        r['C19'] = C19
        r['C20'] = C20
        r['C21'] = C21
        
        # ========== Linear mass (C22) ==========
        # Mass = π(D_outer²/4 - D_inner²/4) × length × density / 1e6
        # Density of steel ≈ 7.81 g/cm³ = 7810 kg/m³
        C22 = ((C20 / 2) ** 2 * math.pi - ((C20 - C21) / 2) ** 2 * math.pi) * C14 * 7.81 / 1_000_000
        r['C22'] = C22
        
        # ========== Material properties (C37-C38) ==========
        r['C37'] = C37  # E - Young's modulus
        r['C38'] = C38  # G - Shear modulus
        
        # ========== Section geometry (C39-C43) ==========
        C39 = max(0, C20 - 2 * C21)  # Inner diameter
        r['C39'] = C39
        
        # Second moment of area (bending)
        C40 = math.pi * (C20 ** 4 - C39 ** 4) / 64
        r['C40'] = C40
        
        # Section modulus (bending)
        C41 = math.pi * (C20 ** 4 - C39 ** 4) / (32 * C20)
        r['C41'] = C41
        
        # Polar moment of area (torsion)
        C42 = math.pi * (C20 ** 4 - C39 ** 4) / 32
        r['C42'] = C42
        
        # Polar section modulus (torsion)
        C43 = math.pi * (C20 ** 4 - C39 ** 4) / (16 * C20)
        r['C43'] = C43
        
        # ========== Kinematics helpers (C44-C56) ==========
        C45 = C14 / 2  # Half eyeball span
        r['C45'] = C45
        
        C48 = C17  # Arm length
        r['C48'] = C48
        
        C49 = (C14 - C15) / 2  # Half difference between eyeball and shoulder
        r['C49'] = C49
        
        C51 = math.atan(C48 / C49)  # Bend angle
        r['C51'] = C51
        
        C55 = C51 / 2  # Half bend angle
        r['C55'] = C55
        
        C50 = C18 * math.tan(C51 / 2)  # Tangent offset
        r['C50'] = C50
        
        C44 = math.sqrt(C48 ** 2 + C49 ** 2) - C50  # Effective straight length
        r['C44'] = C44
        
        C46 = C15 / 2 - C50  # Adjusted shoulder position
        r['C46'] = C46
        
        C47 = C16 / 2  # Half clamp span
        r['C47'] = C47
        
        C52 = math.atan(C18 / C44)
        r['C52'] = C52
        
        C53 = math.atan(C44 / C18)
        r['C53'] = C53
        
        C54 = math.atan(-C44 / C18)
        r['C54'] = C54
        
        C56 = C51 - C55
        r['C56'] = C56
        
        # ========== Energy method - Section A (C57-C59) ==========
        # Bending energy in straight section
        C57 = C44 ** 3 / (3 * C37 * C40)  # A1
        r['C57'] = C57
        
        # Torsional energy
        C58 = C48 ** 2 * C46 / (C38 * C42)  # A2
        r['C58'] = C58
        
        C59 = C57 + C58  # A total
        r['C59'] = C59
        
        # ========== Energy method - Section B (C60-C64) ==========
        C60 = C18 / (C37 * C40)  # B1 - bending factor
        r['C60'] = C60
        
        C61 = (C44 ** 2 / 2) * (C51 + math.sin(2 * C51) / 2)  # B2
        r['C61'] = C61
        
        C62 = C44 * C18 * math.sin(C51) ** 2  # B3
        r['C62'] = C62
        
        C63 = (C18 ** 2 / 2) * (C51 - math.sin(2 * C51) / 2)  # B4
        r['C63'] = C63
        
        C64 = (C61 + C62 + C63) * C60  # B total
        r['C64'] = C64
        
        # ========== Energy method - Section C (C65-C69) ==========
        C65 = C18 / (C38 * C42)  # C1 - torsion factor
        r['C65'] = C65
        
        C66 = (C51 - math.sin(2 * C51) / 2) * C44 ** 2 / 2  # C2
        r['C66'] = C66
        
        C67 = (math.cos(C51) - 1) ** 2 * C44 * C18  # C3
        r['C67'] = C67
        
        C68 = C18 ** 2 * ((3 * C51 / 2) - 2 * math.sin(C51) + 0.25 * math.sin(2 * C51))  # C4
        r['C68'] = C68
        
        C69 = C65 * (C66 + C67 + C68)  # C total
        r['C69'] = C69
        
        # ========== Energy method - Section D (C70-C74) ==========
        C70 = (C46 - C47) / (C37 * C40)  # D1
        r['C70'] = C70
        
        C71 = (C49 + C18 * math.tan(C51 / 2)) ** 2  # D2
        r['C71'] = C71
        
        C72 = (C46 - C47) * (C49 + C18 * math.tan(C51 / 2))  # D3
        r['C72'] = C72
        
        C73 = (C46 - C47) ** 2 / 3  # D4
        r['C73'] = C73
        
        C74 = C70 * (C71 + C72 + C73)  # D total
        r['C74'] = C74
        
        # ========== Energy method - Section E (C75) ==========
        C75 = (C45 - C47) ** 2 * C47 / (3 * C37 * C40)  # E
        r['C75'] = C75
        
        # ========== Total energy and spring rates (C76, C28, C8-C10) ==========
        C76 = C59 + C64 + C69 + C74 + C75  # Total energy sum Σ(A…E)
        r['C76'] = C76
        
        # Spring rate calculations
        C28 = 1 / (2 * C76)  # Calculated spring rate (N/mm)
        r['C28'] = C28
        
        C9 = C28 * 9.80665  # Calculated rate in N/mm
        r['C9'] = C9
        
        C10 = C7 / C9  # Ratio: supplier rate / calculated rate
        r['C10'] = C10
        
        C8 = C9 * C10  # Adjusted spring rate
        r['C8'] = C8
        
        # Store results for later access
        self.results = r
        
        return r
    
    def get_summary(self) -> Dict[str, float]:
        """
        Get key output parameters.
        
        Returns:
        --------
        Dictionary with main results
        """
        if not self.results:
            raise ValueError("No calculation results available. Run calculate() first.")
        
        return {
            'k_calculated_N_per_mm': self.results['C28'],
            'k_with_gravity_N_per_mm': self.results['C9'],
            'supplier_to_calc_ratio': self.results['C10'],
            'k_adjusted_N_per_mm': self.results['C8'],
            'linear_mass_kg': self.results['C22'],
            'total_energy_sum': self.results['C76'],
            'energy_section_A': self.results['C59'],
            'energy_section_B': self.results['C64'],
            'energy_section_C': self.results['C69'],
            'energy_section_D': self.results['C74'],
            'energy_section_E': self.results['C75'],
        }
    
    def print_results(self, show_all: bool = False):
        """
        Print calculation results in a readable format.
        
        Parameters:
        -----------
        show_all : If True, print all C3-C76 values. If False, print summary only.
        """
        if not self.results:
            print("No calculation results available. Run calculate() first.")
            return
        
        print("\n" + "="*70)
        print("ARB STIFFNESS CALCULATION RESULTS")
        print("="*70)
        
        print("\n--- KEY OUTPUTS ---")
        summary = self.get_summary()
        print(f"Calculated spring rate (C28):     {summary['k_calculated_N_per_mm']:.4f} N/mm")
        print(f"With gravity factor (C9):         {summary['k_with_gravity_N_per_mm']:.4f} N/mm")
        print(f"Supplier/Calc ratio (C10):        {summary['supplier_to_calc_ratio']:.4f}")
        print(f"Adjusted spring rate (C8):        {summary['k_adjusted_N_per_mm']:.4f} N/mm")
        print(f"Linear mass (C22):                {summary['linear_mass_kg']:.6f} kg")
        
        print("\n--- ENERGY COMPONENTS ---")
        print(f"Section A (straight bending):     {summary['energy_section_A']:.6e}")
        print(f"Section B (bend bending):         {summary['energy_section_B']:.6e}")
        print(f"Section C (bend torsion):         {summary['energy_section_C']:.6e}")
        print(f"Section D (middle section):       {summary['energy_section_D']:.6e}")
        print(f"Section E (outer section):        {summary['energy_section_E']:.6e}")
        print(f"Total energy sum (C76):           {summary['total_energy_sum']:.6e}")
        
        if show_all:
            print("\n--- ALL CALCULATED VALUES (C3-C76) ---")
            for i in range(3, 77):
                key = f'C{i}'
                if key in self.results:
                    print(f"{key:6s} = {self.results[key]:15.6e}")
        
        print("="*70 + "\n")


# ========== Example usage ==========
if __name__ == "__main__":
    # Create calculator instance
    calc = ARBCalculator()
    
    # Example 1: Default values (matching VB defaults)
    print("Example 1: Default configuration")
    results = calc.calculate()
    calc.print_results(show_all=False)
    
    # Example 2: Custom hollow bar
    print("\n\nExample 2: Custom hollow bar (32mm OD, 3mm wall)")
    results = calc.calculate(
        k_supplier=50.0,
        material_diameter=32.0,
        wall_thickness=3.0,
        eyeball_span=1200.0,
        shoulder_span=650.0,
        clamp_span=520.0,
        arm_length=220.0
    )
    calc.print_results(show_all=False)
    
    # Example 3: Access specific values
    print("\n\nExample 3: Accessing specific calculated values")
    print(f"Bend angle (C51): {results['C51']:.4f} radians = {math.degrees(results['C51']):.2f} degrees")
    print(f"Polar moment (C42): {results['C42']:.2f} mm⁴")
    print(f"Spring rate: {results['C28']:.4f} N/mm")