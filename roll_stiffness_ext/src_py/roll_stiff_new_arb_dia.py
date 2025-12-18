import tkinter as tk
from tkinter import ttk, messagebox
import math


class SuspensionCalculator:
    """
    Suspension & ARB Design Calculator
    Based on vehicle dynamics principles
    """
    
    def __init__(self):
        self.g = 9.81  # gravitational acceleration (m/s^2)
        
    def calculate_spring_stiffness(self, sprung_mass, target_ride_frequency, motion_ratio):
        """Calculate required spring stiffness"""
        omega = 2 * math.pi * target_ride_frequency
        spring_stiffness_N_m = (omega**2 * sprung_mass) / (motion_ratio**2)
        spring_stiffness_N_mm = spring_stiffness_N_m / 1000
        return spring_stiffness_N_mm
    
    def calculate_wheel_rate(self, spring_stiffness, motion_ratio):
        """Calculate wheel rate from spring stiffness"""
        wheel_rate = spring_stiffness * (motion_ratio**2)
        return wheel_rate
    
    def calculate_ride_rate(self, wheel_rate, tire_stiffness):
        """Calculate ride rate"""
        if tire_stiffness <= 0:
            return wheel_rate
        ride_rate = 1 / (1/wheel_rate + 1/tire_stiffness)
        return ride_rate
    
    def calculate_spring_rate_from_frequency(self, wheel_rate, tire_stiffness):
        """Calculate spring rate from wheel rate"""
        ride_rate = self.calculate_ride_rate(wheel_rate, tire_stiffness)
        return ride_rate
    
    def calculate_roll_stiffness(self, spring_rate, track_width, motion_ratio):
        """Calculate roll stiffness from spring rate"""
        track_m = track_width / 1000
        roll_stiffness_Nm_rad = 2 * spring_rate * 1000 * (motion_ratio**2) * ((track_m/2)**2)
        roll_stiffness_Nm_deg = roll_stiffness_Nm_rad * (math.pi / 180)
        return roll_stiffness_Nm_deg
    
    def calculate_wheel_hop_frequency(self, wheel_rate, tire_stiffness, unsprung_mass):
        """
        Calculate wheel hop frequency
        
        Wheel hop is the resonance of unsprung mass on the tire stiffness.
        The effective stiffness is the series combination of wheel rate and tire stiffness.
        
        Formula: f = (1/2π) * sqrt(K_eff / m_unsprung)
        where K_eff = (K_wheel * K_tire) / (K_wheel + K_tire)
        """
        if tire_stiffness <= 0 or unsprung_mass <= 0:
            return 0
        
        # Calculate effective stiffness (series combination)
        # This is the ride rate at the wheel
        k_eff = (wheel_rate * tire_stiffness) / (wheel_rate + tire_stiffness)
        
        # Convert to N/m
        k_eff_N_m = k_eff * 1000
        
        # Calculate natural frequency
        omega = math.sqrt(k_eff_N_m / unsprung_mass)
        frequency = omega / (2 * math.pi)
        
        return frequency
    
    def calculate_required_roll_stiffness(self, vehicle_sprung_mass, cg_height, wheelbase, 
                                         front_roll_center, rear_roll_center, roll_gradient):
        """Calculate required total roll stiffness"""
        # This is a simplified calculation
        cg_height_m = cg_height / 1000
        wheelbase_m = wheelbase / 1000
        
        # Roll moment arm (simplified)
        roll_arm = cg_height_m - (front_roll_center + rear_roll_center) / 2000
        
        # Required roll stiffness based on target roll gradient
        # K_roll = (m * g * h) / roll_gradient
        required_roll_stiffness = (vehicle_sprung_mass * self.g * roll_arm) / (roll_gradient * math.pi / 180)
        
        return required_roll_stiffness
    
    def calculate_arb_diameter(self, required_arb_stiffness_Nm_deg, arm_length, half_track, 
                              arb_material_G=80000):
        """Calculate ARB diameter"""
        arm_length_m = arm_length / 1000
        half_track_m = half_track / 1000
        
        required_arb_stiffness_Nm_rad = required_arb_stiffness_Nm_deg * (180 / math.pi)
        
        # ARB formula: d^4 = (K_roll * 32 * L * track^2) / (G * arm_length^2 * 2)
        d_4 = (required_arb_stiffness_Nm_rad * 32 * half_track_m * (2*half_track_m)**2) / \
              (arb_material_G * 1e6 * (arm_length_m**2) * 2)
        
        arb_diameter_m = d_4 ** 0.25
        arb_diameter_mm = arb_diameter_m * 1000
        
        # Calculate ARB vertical stiffness rate at wheel
        arb_stiffness_N_m = (arb_material_G * 1e6 * math.pi * (arb_diameter_m**4)) / \
                            (32 * half_track_m) * ((arm_length_m / half_track_m)**2)
        arb_stiffness_N_mm = arb_stiffness_N_m / 1000
        
        # ARB roll stiffness
        track_m = 2 * half_track_m
        arb_roll_stiffness_Nm_rad = 2 * arb_stiffness_N_m * ((track_m/2)**2)
        arb_roll_stiffness_Nm_deg = arb_roll_stiffness_Nm_rad * (math.pi / 180)
        
        return arb_diameter_mm, arb_stiffness_N_mm, arb_roll_stiffness_Nm_deg


class SuspensionCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SUSPENSION & ARB DESIGN CALCULATOR")
        self.root.geometry("1400x900")
        
        self.calculator = SuspensionCalculator()
        
        # Initialize ARB roll stiffness values (from Roll Stiffness tab)
        self.arb_roll_stiffness_fr_required = 0.0
        self.arb_roll_stiffness_rr_required = 0.0
        
        # Create main container
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create header with mode buttons
        self.create_header(main_frame)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create tabs
        self.create_ride_frequency_tab()
        self.create_roll_stiffness_tab()
        self.create_arb_design_tab()
        self.create_7dof_tab()
        self.create_damping_curves_tab()
        self.create_other_loading_tab()
        
        # Initialize variables
        self.initialize_default_values()
        
    def create_header(self, parent):
        """Create header with CEER logo and version information"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # CEER Logo
        logo_frame = ttk.Frame(header_frame, relief=tk.RIDGE, borderwidth=2, width=100, height=40)
        logo_frame.grid(row=0, column=0, padx=5, rowspan=2)
        logo_frame.grid_propagate(False)
        logo_label = tk.Label(logo_frame, text="CEER", font=('Arial', 16, 'bold'), 
                             foreground='#003366', bg='white')
        logo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Mode buttons
        ttk.Button(header_frame, text="DESIGN", width=15).grid(row=0, column=1, padx=5)
        ttk.Button(header_frame, text="BENCHMARK", width=15).grid(row=0, column=2, padx=5)
        
        # Version and creator information (right side)
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=3, padx=20, sticky=tk.E, rowspan=2)
        
        ttk.Label(info_frame, text="Created by: Nirmal", 
                 font=('Arial', 9, 'italic'), foreground='#555555').pack(anchor=tk.E)
        ttk.Label(info_frame, text="Version: 1.0.0", 
                 font=('Arial', 9), foreground='#555555').pack(anchor=tk.E)
        ttk.Label(info_frame, text="Release Date: December 2024", 
                 font=('Arial', 9), foreground='#555555').pack(anchor=tk.E)
        
        # Configure column weight to push info to the right
        header_frame.columnconfigure(3, weight=1)
        
    def create_ride_frequency_tab(self):
        """Create Ride Frequency tab - Redesigned for simplicity and beauty"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="RIDE FREQUENCY")
        
        # Configure grid weights for responsive layout
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)
        
        # ============ TOP SECTION: INPUTS ============
        input_container = ttk.Frame(tab, padding="15")
        input_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Left Column: Vehicle & Mass Inputs
        left_inputs = ttk.Frame(input_container)
        left_inputs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=10)
        
        # Vehicle Masses Section
        mass_frame = ttk.LabelFrame(left_inputs, text="VEHICLE MASSES", padding="15")
        mass_frame.pack(fill=tk.BOTH, pady=(0, 10))
        
        # Front Axle Weight
        row_f = ttk.Frame(mass_frame)
        row_f.pack(fill=tk.X, pady=5)
        ttk.Label(row_f, text="Front Axle Weight (LH+RH):", width=25, font=('Arial', 9)).pack(side=tk.LEFT)
        self.front_axle_weight = ttk.Entry(row_f, width=12, font=('Arial', 10))
        self.front_axle_weight.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_f, text="kg", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Rear Axle Weight
        row_r = ttk.Frame(mass_frame)
        row_r.pack(fill=tk.X, pady=5)
        ttk.Label(row_r, text="Rear Axle Weight (LH+RH):", width=25, font=('Arial', 9)).pack(side=tk.LEFT)
        self.rear_axle_weight = ttk.Entry(row_r, width=12, font=('Arial', 10))
        self.rear_axle_weight.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_r, text="kg", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(mass_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Unsprung Mass Front
        row_uf = ttk.Frame(mass_frame)
        row_uf.pack(fill=tk.X, pady=5)
        ttk.Label(row_uf, text="Unsprung Mass Front (One Side):", width=25, font=('Arial', 9)).pack(side=tk.LEFT)
        self.unsprung_mass_front = ttk.Entry(row_uf, width=12, font=('Arial', 10))
        self.unsprung_mass_front.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_uf, text="kg", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Unsprung Mass Rear
        row_ur = ttk.Frame(mass_frame)
        row_ur.pack(fill=tk.X, pady=5)
        ttk.Label(row_ur, text="Unsprung Mass Rear (One Side):", width=25, font=('Arial', 9)).pack(side=tk.LEFT)
        self.unsprung_mass_rear = ttk.Entry(row_ur, width=12, font=('Arial', 10))
        self.unsprung_mass_rear.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_ur, text="kg", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Tire Stiffness Section
        tire_frame = ttk.LabelFrame(left_inputs, text="TIRE STIFFNESS", padding="15")
        tire_frame.pack(fill=tk.BOTH, pady=(0, 10))
        
        row_tire = ttk.Frame(tire_frame)
        row_tire.pack(fill=tk.X, pady=5)
        ttk.Label(row_tire, text="Tire Stiffness:", width=20, font=('Arial', 9)).pack(side=tk.LEFT)
        self.tire_stiffness = ttk.Entry(row_tire, width=12, font=('Arial', 10))
        self.tire_stiffness.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_tire, text="N/mm", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Middle Column: Suspension Inputs
        middle_inputs = ttk.Frame(input_container)
        middle_inputs.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=10)
        
        # Suspension Inputs Section
        susp_frame = ttk.LabelFrame(middle_inputs, text="SUSPENSION INPUTS", padding="15")
        susp_frame.pack(fill=tk.BOTH, pady=(0, 10))
        
        # Motion Ratio Front
        row_mrf = ttk.Frame(susp_frame)
        row_mrf.pack(fill=tk.X, pady=5)
        ttk.Label(row_mrf, text="Motion Ratio (Front):", width=20, font=('Arial', 9)).pack(side=tk.LEFT)
        self.motion_ratio_front = ttk.Entry(row_mrf, width=12, font=('Arial', 10))
        self.motion_ratio_front.pack(side=tk.LEFT, padx=5)
        
        # Motion Ratio Rear
        row_mrr = ttk.Frame(susp_frame)
        row_mrr.pack(fill=tk.X, pady=5)
        ttk.Label(row_mrr, text="Motion Ratio (Rear):", width=20, font=('Arial', 9)).pack(side=tk.LEFT)
        self.motion_ratio_rear = ttk.Entry(row_mrr, width=12, font=('Arial', 10))
        self.motion_ratio_rear.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(susp_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Parametric Stiffness
        row_param = ttk.Frame(susp_frame)
        row_param.pack(fill=tk.X, pady=5)
        ttk.Label(row_param, text="Parametric Stiffness:", width=20, font=('Arial', 9)).pack(side=tk.LEFT)
        self.parametric_stiffness = ttk.Entry(row_param, width=12, font=('Arial', 10))
        self.parametric_stiffness.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_param, text="N/mm", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Right Column: Target Frequencies
        right_inputs = ttk.Frame(input_container)
        right_inputs.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N), padx=10)
        
        # Target Frequencies Section
        target_frame = ttk.LabelFrame(right_inputs, text="TARGET RIDE FREQUENCY", padding="15")
        target_frame.pack(fill=tk.BOTH, pady=(0, 10))
        
        # Target Frequency Front
        row_tff = ttk.Frame(target_frame)
        row_tff.pack(fill=tk.X, pady=5)
        ttk.Label(row_tff, text="Ride Frequency (Front):", width=22, font=('Arial', 9)).pack(side=tk.LEFT)
        self.target_freq_front = ttk.Entry(row_tff, width=12, font=('Arial', 10))
        self.target_freq_front.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_tff, text="Hz", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Target Frequency Rear
        row_tfr = ttk.Frame(target_frame)
        row_tfr.pack(fill=tk.X, pady=5)
        ttk.Label(row_tfr, text="Ride Frequency (Rear):", width=22, font=('Arial', 9)).pack(side=tk.LEFT)
        self.target_freq_rear = ttk.Entry(row_tfr, width=12, font=('Arial', 10))
        self.target_freq_rear.pack(side=tk.LEFT, padx=5)
        ttk.Label(row_tfr, text="Hz", font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Calculate Button
        calc_btn_frame = ttk.Frame(right_inputs)
        calc_btn_frame.pack(fill=tk.X, pady=15)
        ttk.Button(calc_btn_frame, text="⚙ CALCULATE OUTPUTS", 
                  command=self.calculate_ride_frequency,
                  width=25).pack()
        
        # ============ MIDDLE SECTION: WEIGHT DISTRIBUTION ============
        weight_dist_frame = ttk.LabelFrame(tab, text="WEIGHT DISTRIBUTION", padding="10")
        weight_dist_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20, pady=10)
        
        dist_container = ttk.Frame(weight_dist_frame)
        dist_container.pack(expand=True)
        
        # Front Weight %
        fw_frame = ttk.Frame(dist_container)
        fw_frame.pack(side=tk.LEFT, padx=30)
        ttk.Label(fw_frame, text="Front Weight:", font=('Arial', 10, 'bold')).pack()
        self.fw_display = tk.Label(fw_frame, text="0.0 %", font=('Arial', 14, 'bold'), 
                                   fg='#0066cc', bg='#e6f2ff', relief=tk.SUNKEN, 
                                   width=10, padx=10, pady=5)
        self.fw_display.pack(pady=5)
        
        # Rear Weight %
        rw_frame = ttk.Frame(dist_container)
        rw_frame.pack(side=tk.LEFT, padx=30)
        ttk.Label(rw_frame, text="Rear Weight:", font=('Arial', 10, 'bold')).pack()
        self.rw_display = tk.Label(rw_frame, text="0.0 %", font=('Arial', 14, 'bold'), 
                                   fg='#cc6600', bg='#fff2e6', relief=tk.SUNKEN,
                                   width=10, padx=10, pady=5)
        self.rw_display.pack(pady=5)
        
        # ============ BOTTOM SECTION: RESULTS TABLE ============
        results_frame = ttk.LabelFrame(tab, text="CALCULATION RESULTS", padding="15")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20, pady=10)
        
        # Create styled table
        style = ttk.Style()
        style.configure('Results.Treeview', rowheight=30, font=('Arial', 9))
        style.configure('Results.Treeview.Heading', font=('Arial', 10, 'bold'))
        
        # Results Table
        columns = ('Parameter', 'Front', 'Rear', 'Unit')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', 
                                        height=6, style='Results.Treeview')
        
        # Define headings
        self.results_tree.heading('Parameter', text='PARAMETER')
        self.results_tree.heading('Front', text='FRONT')
        self.results_tree.heading('Rear', text='REAR')
        self.results_tree.heading('Unit', text='UNIT')
        
        # Define column widths
        self.results_tree.column('Parameter', width=250, anchor=tk.W)
        self.results_tree.column('Front', width=150, anchor=tk.CENTER)
        self.results_tree.column('Rear', width=150, anchor=tk.CENTER)
        self.results_tree.column('Unit', width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert empty rows
        self.results_tree.insert('', tk.END, values=('Spring Rate', '-', '-', 'N/mm'), tags=('spring',))
        self.results_tree.insert('', tk.END, values=('Wheel Rate (from Spring)', '-', '-', 'N/mm'), tags=('wheel',))
        self.results_tree.insert('', tk.END, values=('Total Wheel Rate (Spring+Parametric)', '-', '-', 'N/mm'), tags=('total',))
        self.results_tree.insert('', tk.END, values=('Ride Rate', '-', '-', 'N/mm'), tags=('ride',))
        self.results_tree.insert('', tk.END, values=('Wheel Hop Frequency', '-', '-', 'Hz'), tags=('hop',))
        
        # Configure row colors
        self.results_tree.tag_configure('spring', background='#cce6ff')
        self.results_tree.tag_configure('wheel', background='#e6f2ff')
        self.results_tree.tag_configure('total', background='#cce6ff')
        self.results_tree.tag_configure('ride', background='#e6f2ff')
        self.results_tree.tag_configure('hop', background='#cce6ff')
        
    def create_roll_stiffness_tab(self):
        """Create Roll Stiffness tab based on 14-Step Methodology"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ROLL STIFFNESS")
        
        # Main layout
        left_frame = ttk.Frame(tab)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        right_frame = ttk.Frame(tab)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configure weights
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        
        # ===== LEFT SIDE =====
        
        # INPUTS SECTION
        inputs_frame = ttk.LabelFrame(left_frame, text="INPUT PARAMETERS", padding="10")
        inputs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vehicle Geometry
        ttk.Label(inputs_frame, text="VEHICLE GEOMETRY", font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0,5))
        
        ttk.Label(inputs_frame, text="CG Height").grid(row=1, column=0, sticky=tk.W)
        self.roll_cg_height = ttk.Entry(inputs_frame, width=10)
        self.roll_cg_height.grid(row=1, column=1, padx=5)
        ttk.Label(inputs_frame, text="mm").grid(row=1, column=2)
        
        ttk.Label(inputs_frame, text="Roll Center Height (Front)").grid(row=2, column=0, sticky=tk.W)
        self.front_roll_center = ttk.Entry(inputs_frame, width=10)
        self.front_roll_center.grid(row=2, column=1, padx=5)
        ttk.Label(inputs_frame, text="mm").grid(row=2, column=2)
        
        ttk.Label(inputs_frame, text="Roll Center Height (Rear)").grid(row=3, column=0, sticky=tk.W)
        self.rear_roll_center = ttk.Entry(inputs_frame, width=10)
        self.rear_roll_center.grid(row=3, column=1, padx=5)
        ttk.Label(inputs_frame, text="mm").grid(row=3, column=2)
        
        ttk.Label(inputs_frame, text="Track Width (Front)").grid(row=4, column=0, sticky=tk.W)
        self.roll_front_track = ttk.Entry(inputs_frame, width=10)
        self.roll_front_track.grid(row=4, column=1, padx=5)
        ttk.Label(inputs_frame, text="mm").grid(row=4, column=2)
        
        ttk.Label(inputs_frame, text="Track Width (Rear)").grid(row=5, column=0, sticky=tk.W)
        self.roll_rear_track = ttk.Entry(inputs_frame, width=10)
        self.roll_rear_track.grid(row=5, column=1, padx=5)
        ttk.Label(inputs_frame, text="mm").grid(row=5, column=2)
        
        # Spring & Bushing
        ttk.Label(inputs_frame, text="SPRING & BUSHING", font=('Arial', 9, 'bold')).grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(10,5))
        
        ttk.Label(inputs_frame, text="Wheel Rate (Front)").grid(row=7, column=0, sticky=tk.W)
        self.roll_wheel_rate_front = ttk.Entry(inputs_frame, width=10)
        self.roll_wheel_rate_front.grid(row=7, column=1, padx=5)
        ttk.Label(inputs_frame, text="N/mm").grid(row=7, column=2)
        
        ttk.Label(inputs_frame, text="Wheel Rate (Rear)").grid(row=8, column=0, sticky=tk.W)
        self.roll_wheel_rate_rear = ttk.Entry(inputs_frame, width=10)
        self.roll_wheel_rate_rear.grid(row=8, column=1, padx=5)
        ttk.Label(inputs_frame, text="N/mm").grid(row=8, column=2)
        
        # Targets
        ttk.Label(inputs_frame, text="TARGETS", font=('Arial', 9, 'bold')).grid(row=9, column=0, columnspan=3, sticky=tk.W, pady=(10,5))
        
        ttk.Label(inputs_frame, text="Target Roll Angle @ 0.5G").grid(row=10, column=0, sticky=tk.W)
        self.roll_target_angle = ttk.Entry(inputs_frame, width=10)
        self.roll_target_angle.grid(row=10, column=1, padx=5)
        ttk.Label(inputs_frame, text="deg").grid(row=10, column=2)
        
        ttk.Label(inputs_frame, text="Target Front Distribution").grid(row=11, column=0, sticky=tk.W)
        self.roll_target_dist = ttk.Entry(inputs_frame, width=10)
        self.roll_target_dist.grid(row=11, column=1, padx=5)
        ttk.Label(inputs_frame, text="%").grid(row=11, column=2)
        
        # Calculate Button
        ttk.Button(left_frame, text="CALCULATE ROLL STIFFNESS", 
                  command=self.calculate_roll_stiffness, width=30).pack(pady=20)
        
        # ===== RIGHT SIDE =====
        
        # RESULTS SECTION
        results_frame = ttk.LabelFrame(right_frame, text="CALCULATION RESULTS", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Step 3-5: Roll Geometry
        geom_frame = ttk.LabelFrame(results_frame, text="ROLL GEOMETRY", padding="5")
        geom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(geom_frame, text="Eff. Roll Center Height:").grid(row=0, column=0, sticky=tk.W)
        self.out_rc_height = ttk.Label(geom_frame, text="-", font=('Arial', 9, 'bold'))
        self.out_rc_height.grid(row=0, column=1, padx=5)
        ttk.Label(geom_frame, text="mm").grid(row=0, column=2)
        
        ttk.Label(geom_frame, text="Roll Moment Arm:").grid(row=1, column=0, sticky=tk.W)
        self.out_roll_arm = ttk.Label(geom_frame, text="-", font=('Arial', 9, 'bold'))
        self.out_roll_arm.grid(row=1, column=1, padx=5)
        ttk.Label(geom_frame, text="mm").grid(row=1, column=2)
        
        ttk.Label(geom_frame, text="Roll Moment @ 0.5G:").grid(row=2, column=0, sticky=tk.W)
        self.out_roll_moment = ttk.Label(geom_frame, text="-", font=('Arial', 9, 'bold'))
        self.out_roll_moment.grid(row=2, column=1, padx=5)
        ttk.Label(geom_frame, text="Nm").grid(row=2, column=2)
        
        # Step 6: Tire Roll Stiffness
        tire_frame = ttk.LabelFrame(results_frame, text="TIRE ROLL STIFFNESS", padding="5")
        tire_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(tire_frame, text="Front:").grid(row=0, column=0, sticky=tk.W)
        self.out_tire_roll_fr = ttk.Label(tire_frame, text="-", foreground='blue')
        self.out_tire_roll_fr.grid(row=0, column=1, padx=5)
        ttk.Label(tire_frame, text="Nm/deg").grid(row=0, column=2)
        
        ttk.Label(tire_frame, text="Rear:").grid(row=1, column=0, sticky=tk.W)
        self.out_tire_roll_rr = ttk.Label(tire_frame, text="-", foreground='blue')
        self.out_tire_roll_rr.grid(row=1, column=1, padx=5)
        ttk.Label(tire_frame, text="Nm/deg").grid(row=1, column=2)
        
        # Step 7-8: Spring Contribution
        spring_frame = ttk.LabelFrame(results_frame, text="SPRING CONTRIBUTION", padding="5")
        spring_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(spring_frame, text="Wheel Rate FR:").grid(row=0, column=0, sticky=tk.W)
        self.out_wh_rate_fr = ttk.Label(spring_frame, text="-")
        self.out_wh_rate_fr.grid(row=0, column=1, padx=5)
        ttk.Label(spring_frame, text="N/mm").grid(row=0, column=2)
        
        ttk.Label(spring_frame, text="Wheel Rate RR:").grid(row=1, column=0, sticky=tk.W)
        self.out_wh_rate_rr = ttk.Label(spring_frame, text="-")
        self.out_wh_rate_rr.grid(row=1, column=1, padx=5)
        ttk.Label(spring_frame, text="N/mm").grid(row=1, column=2)
        
        ttk.Label(spring_frame, text="Roll Stiffness FR:").grid(row=2, column=0, sticky=tk.W)
        self.out_spring_roll_fr = ttk.Label(spring_frame, text="-", foreground='green')
        self.out_spring_roll_fr.grid(row=2, column=1, padx=5)
        ttk.Label(spring_frame, text="Nm/deg").grid(row=2, column=2)
        
        ttk.Label(spring_frame, text="Roll Stiffness RR:").grid(row=3, column=0, sticky=tk.W)
        self.out_spring_roll_rr = ttk.Label(spring_frame, text="-", foreground='green')
        self.out_spring_roll_rr.grid(row=3, column=1, padx=5)
        ttk.Label(spring_frame, text="Nm/deg").grid(row=3, column=2)
        
        # Step 9-11: Requirements
        req_frame = ttk.LabelFrame(results_frame, text="REQUIREMENTS", padding="5")
        req_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(req_frame, text="Total Req. Roll Stiffness:").grid(row=0, column=0, sticky=tk.W)
        self.out_total_req = ttk.Label(req_frame, text="-", font=('Arial', 9, 'bold'))
        self.out_total_req.grid(row=0, column=1, padx=5)
        ttk.Label(req_frame, text="Nm/deg").grid(row=0, column=2)
        
        ttk.Label(req_frame, text="Susp. Req. (Total):").grid(row=1, column=0, sticky=tk.W)
        self.out_susp_req_total = ttk.Label(req_frame, text="-")
        self.out_susp_req_total.grid(row=1, column=1, padx=5)
        ttk.Label(req_frame, text="Nm/deg").grid(row=1, column=2)
        
        ttk.Label(req_frame, text="Susp. Req. FR:").grid(row=2, column=0, sticky=tk.W)
        self.out_susp_req_fr = ttk.Label(req_frame, text="-")
        self.out_susp_req_fr.grid(row=2, column=1, padx=5)
        ttk.Label(req_frame, text="Nm/deg").grid(row=2, column=2)
        
        ttk.Label(req_frame, text="Susp. Req. RR:").grid(row=3, column=0, sticky=tk.W)
        self.out_susp_req_rr = ttk.Label(req_frame, text="-")
        self.out_susp_req_rr.grid(row=3, column=1, padx=5)
        ttk.Label(req_frame, text="Nm/deg").grid(row=3, column=2)
        
        # ARB Requirements
        arb_frame = ttk.LabelFrame(results_frame, text="ARB REQUIREMENTS", padding="5")
        arb_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(arb_frame, text="ARB Roll Stiffness FR:").grid(row=0, column=0, sticky=tk.W)
        self.out_arb_req_fr = ttk.Label(arb_frame, text="-", font=('Arial', 10, 'bold'), foreground='red')
        self.out_arb_req_fr.grid(row=0, column=1, padx=5)
        ttk.Label(arb_frame, text="Nm/deg").grid(row=0, column=2)
        
        ttk.Label(arb_frame, text="ARB Roll Stiffness RR:").grid(row=1, column=0, sticky=tk.W)
        self.out_arb_req_rr = ttk.Label(arb_frame, text="-", font=('Arial', 10, 'bold'), foreground='red')
        self.out_arb_req_rr.grid(row=1, column=1, padx=5)
        ttk.Label(arb_frame, text="Nm/deg").grid(row=1, column=2)
        
    def create_arb_design_tab(self):
        """Create simplified ARB Design tab - uses inputs from previous tabs"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ARB DESIGN")
        
        # Main container
        main_container = ttk.Frame(tab)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Info section
        info_frame = ttk.LabelFrame(main_container, text="INFO - Data from Previous Tabs", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(info_frame, text="• ARB Roll Stiffness Required: From Roll Stiffness Tab", 
                 foreground='blue').grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text="• Track Width: From Roll Stiffness Tab", 
                 foreground='blue').grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # ARB Inputs Frame
        inputs_frame = ttk.LabelFrame(main_container, text="ARB DESIGN INPUTS", padding="10")
        inputs_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Left side - Front inputs
        left_inputs = ttk.Frame(inputs_frame)
        left_inputs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=20)
        
        ttk.Label(left_inputs, text="FRONT ARB", font=('Arial', 10, 'bold'), 
                 foreground='darkblue').grid(row=0, column=0, columnspan=3, pady=(0,10))
        
        ttk.Label(left_inputs, text="Bush Stiffness").grid(row=1, column=0, sticky=tk.W)
        self.arb_bush_stiffness_front = ttk.Entry(left_inputs, width=12)
        self.arb_bush_stiffness_front.grid(row=1, column=1, padx=5)
        ttk.Label(left_inputs, text="N/mm").grid(row=1, column=2)
        
        ttk.Label(left_inputs, text="Clamp Span").grid(row=2, column=0, sticky=tk.W)
        self.arb_clamp_span_front = ttk.Entry(left_inputs, width=12)
        self.arb_clamp_span_front.grid(row=2, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=2, column=2)
        
        ttk.Label(left_inputs, text="Eye Span").grid(row=3, column=0, sticky=tk.W)
        self.arb_eye_span_front = ttk.Entry(left_inputs, width=12)
        self.arb_eye_span_front.grid(row=3, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=3, column=2)
        
        ttk.Label(left_inputs, text="Lever Ratio (σ)").grid(row=4, column=0, sticky=tk.W)
        self.arb_lever_ratio_front = ttk.Entry(left_inputs, width=12)
        self.arb_lever_ratio_front.grid(row=4, column=1, padx=5)
        ttk.Label(left_inputs, text="-").grid(row=4, column=2)
        
        ttk.Button(left_inputs, text="Calculate Front ARB", 
                  command=lambda: self.calculate_arb_outputs('front'),
                  width=20).grid(row=5, column=0, columnspan=3, pady=10)
        
        # Right side - Rear inputs
        right_inputs = ttk.Frame(inputs_frame)
        right_inputs.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=20)
        
        ttk.Label(right_inputs, text="REAR ARB", font=('Arial', 10, 'bold'), 
                 foreground='darkgreen').grid(row=0, column=0, columnspan=3, pady=(0,10))
        
        ttk.Label(right_inputs, text="Bush Stiffness").grid(row=1, column=0, sticky=tk.W)
        self.arb_bush_stiffness_rear = ttk.Entry(right_inputs, width=12)
        self.arb_bush_stiffness_rear.grid(row=1, column=1, padx=5)
        ttk.Label(right_inputs, text="N/mm").grid(row=1, column=2)
        
        ttk.Label(right_inputs, text="Clamp Span").grid(row=2, column=0, sticky=tk.W)
        self.arb_clamp_span_rear = ttk.Entry(right_inputs, width=12)
        self.arb_clamp_span_rear.grid(row=2, column=1, padx=5)
        ttk.Label(right_inputs, text="mm").grid(row=2, column=2)
        
        ttk.Label(right_inputs, text="Eye Span").grid(row=3, column=0, sticky=tk.W)
        self.arb_eye_span_rear = ttk.Entry(right_inputs, width=12)
        self.arb_eye_span_rear.grid(row=3, column=1, padx=5)
        ttk.Label(right_inputs, text="mm").grid(row=3, column=2)
        
        ttk.Label(right_inputs, text="Lever Ratio (σ)").grid(row=4, column=0, sticky=tk.W)
        self.arb_lever_ratio_rear = ttk.Entry(right_inputs, width=12)
        self.arb_lever_ratio_rear.grid(row=4, column=1, padx=5)
        ttk.Label(right_inputs, text="-").grid(row=4, column=2)
        
        ttk.Button(right_inputs, text="Calculate Rear ARB", 
                  command=lambda: self.calculate_arb_outputs('rear'),
                  width=20).grid(row=5, column=0, columnspan=3, pady=10)
        
        # ARB Outputs Frame
        outputs_frame = ttk.LabelFrame(main_container, text="ARB CALCULATION RESULTS", padding="10")
        outputs_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Front outputs
        front_out_frame = ttk.Frame(outputs_frame, relief=tk.GROOVE, borderwidth=2)
        front_out_frame.grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N))
        
        ttk.Label(front_out_frame, text="FRONT ARB RESULTS", font=('Arial', 9, 'bold'),
                 background='lightblue').grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(front_out_frame, text="ARB Wheel Rate Required", background='lightyellow').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.arb_wheel_rate_required_front = ttk.Entry(front_out_frame, width=12, state='readonly')
        self.arb_wheel_rate_required_front.grid(row=1, column=1, padx=5)
        ttk.Label(front_out_frame, text="N/mm").grid(row=1, column=2)
        
        ttk.Label(front_out_frame, text="Bush Lever Ratio", background='lightyellow').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.bush_lever_ratio_front_display = ttk.Entry(front_out_frame, width=12, state='readonly')
        self.bush_lever_ratio_front_display.grid(row=2, column=1, padx=5)
        ttk.Label(front_out_frame, text="-").grid(row=2, column=2)
        
        ttk.Label(front_out_frame, text="Bush Stiffness at Eye", background='lightyellow').grid(row=3, column=0, sticky=tk.W, padx=5)
        self.bush_stiffness_eye_front_display = ttk.Entry(front_out_frame, width=12, state='readonly')
        self.bush_stiffness_eye_front_display.grid(row=3, column=1, padx=5)
        ttk.Label(front_out_frame, text="N/mm").grid(row=3, column=2)
        
        ttk.Label(front_out_frame, text="ARB Bar Stiffness", background='lightgreen', 
                 font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, padx=5)
        self.arb_bar_stiffness_front_display = ttk.Entry(front_out_frame, width=12, state='readonly')
        self.arb_bar_stiffness_front_display.grid(row=4, column=1, padx=5)
        ttk.Label(front_out_frame, text="N/mm").grid(row=4, column=2)
        
        ttk.Label(front_out_frame, text="Combined Eye Stiffness", background='lightgreen',
                 font=('Arial', 9, 'bold')).grid(row=5, column=0, sticky=tk.W, padx=5)
        self.combined_eye_stiffness_front_display = ttk.Entry(front_out_frame, width=12, state='readonly')
        self.combined_eye_stiffness_front_display.grid(row=5, column=1, padx=5)
        ttk.Label(front_out_frame, text="N/mm").grid(row=5, column=2)
        
        # Rear outputs
        rear_out_frame = ttk.Frame(outputs_frame, relief=tk.GROOVE, borderwidth=2)
        rear_out_frame.grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N))
        
        ttk.Label(rear_out_frame, text="REAR ARB RESULTS", font=('Arial', 9, 'bold'),
                 background='lightblue').grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(rear_out_frame, text="ARB Wheel Rate Required", background='lightyellow').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.arb_wheel_rate_required_rear = ttk.Entry(rear_out_frame, width=12, state='readonly')
        self.arb_wheel_rate_required_rear.grid(row=1, column=1, padx=5)
        ttk.Label(rear_out_frame, text="N/mm").grid(row=1, column=2)
        
        ttk.Label(rear_out_frame, text="Bush Lever Ratio", background='lightyellow').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.bush_lever_ratio_rear_display = ttk.Entry(rear_out_frame, width=12, state='readonly')
        self.bush_lever_ratio_rear_display.grid(row=2, column=1, padx=5)
        ttk.Label(rear_out_frame, text="-").grid(row=2, column=2)
        
        ttk.Label(rear_out_frame, text="Bush Stiffness at Eye", background='lightyellow').grid(row=3, column=0, sticky=tk.W, padx=5)
        self.bush_stiffness_eye_rear_display = ttk.Entry(rear_out_frame, width=12, state='readonly')
        self.bush_stiffness_eye_rear_display.grid(row=3, column=1, padx=5)
        ttk.Label(rear_out_frame, text="N/mm").grid(row=3, column=2)
        
        ttk.Label(rear_out_frame, text="ARB Bar Stiffness", background='lightgreen',
                 font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, padx=5)
        self.arb_bar_stiffness_rear_display = ttk.Entry(rear_out_frame, width=12, state='readonly')
        self.arb_bar_stiffness_rear_display.grid(row=4, column=1, padx=5)
        ttk.Label(rear_out_frame, text="N/mm").grid(row=4, column=2)
        
        ttk.Label(rear_out_frame, text="Combined Eye Stiffness", background='lightgreen',
                 font=('Arial', 9, 'bold')).grid(row=5, column=0, sticky=tk.W, padx=5)
        self.combined_eye_stiffness_rear_display = ttk.Entry(rear_out_frame, width=12, state='readonly')
        self.combined_eye_stiffness_rear_display.grid(row=5, column=1, padx=5)
        ttk.Label(rear_out_frame, text="N/mm").grid(row=5, column=2)
        
    def create_7dof_tab(self):
        """Create 7 DOF tab placeholder"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="7 DOF")
        
        label = ttk.Label(tab, text="7 DOF Analysis\n(To be implemented)", 
                         font=('Arial', 16), justify=tk.CENTER)
        label.pack(expand=True)
        
    def create_damping_curves_tab(self):
        """Create Damping Curves tab placeholder"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="DAMPING CURVES")
        
        label = ttk.Label(tab, text="Damping Curves Analysis\n(To be implemented)", 
                         font=('Arial', 16), justify=tk.CENTER)
        label.pack(expand=True)
        
    def create_other_loading_tab(self):
        """Create Other Loading Conditions tab placeholder"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="OTHER LOADING CONDITIONS")
        
        label = ttk.Label(tab, text="Other Loading Conditions\n(To be implemented)", 
                         font=('Arial', 16), justify=tk.CENTER)
        label.pack(expand=True)
        
    def initialize_default_values(self):
        """Initialize with default values from the images"""
        # Ride Frequency Tab - Vehicle inputs
        self.front_axle_weight.insert(0, "1037.5")  # ~50% of 2075
        self.rear_axle_weight.insert(0, "1037.5")   # ~50% of 2075
        self.unsprung_mass_front.insert(0, "123.2")
        self.unsprung_mass_rear.insert(0, "107.2")
        
        # Tire stiffness (single value)
        self.tire_stiffness.insert(0, "246.8")
        
        # Motion ratios
        self.motion_ratio_front.insert(0, "1.665")
        self.motion_ratio_rear.insert(0, "1.498")
        
        # Parametric stiffness
        self.parametric_stiffness.insert(0, "10")
        
        # Target frequencies
        self.target_freq_front.insert(0, "1.21")
        self.target_freq_rear.insert(0, "1.29")
        
        # Roll stiffness tab
        self.roll_cg_height.insert(0, "692.9")
        self.roll_front_track.insert(0, "1630")
        self.roll_rear_track.insert(0, "1630")
        self.front_roll_center.insert(0, "68")
        self.rear_roll_center.insert(0, "138")
        self.roll_wheel_rate_front.insert(0, "0.0")
        self.roll_wheel_rate_rear.insert(0, "0.0")
        self.roll_target_angle.insert(0, "2.2")
        self.roll_target_dist.insert(0, "60")
        
        # ARB Design tab - bush and geometry inputs (example values - user should adjust)
        self.arb_bush_stiffness_front.insert(0, "500")  # N/mm
        self.arb_bush_stiffness_rear.insert(0, "450")   # N/mm
        self.arb_clamp_span_front.insert(0, "100")      # mm
        self.arb_clamp_span_rear.insert(0, "100")       # mm
        self.arb_eye_span_front.insert(0, "80")         # mm
        self.arb_eye_span_rear.insert(0, "80")          # mm
        self.arb_lever_ratio_front.insert(0, "1.5")     # dimensionless
        self.arb_lever_ratio_rear.insert(0, "1.5")      # dimensionless
        
    def calculate_ride_frequency(self):
        """Calculate ride frequency outputs with new simplified inputs"""
        try:
            # Get inputs
            front_axle = float(self.front_axle_weight.get())  # Total front axle (LH+RH)
            rear_axle = float(self.rear_axle_weight.get())    # Total rear axle (LH+RH)
            total_mass = front_axle + rear_axle
            
            unsprung_f = float(self.unsprung_mass_front.get())  # One side
            unsprung_r = float(self.unsprung_mass_rear.get())   # One side
            
            tire_stiff = float(self.tire_stiffness.get())
            parametric_stiff = float(self.parametric_stiffness.get())
            
            mr_front = float(self.motion_ratio_front.get())
            mr_rear = float(self.motion_ratio_rear.get())
            
            target_f = float(self.target_freq_front.get())
            target_r = float(self.target_freq_rear.get())
            
            # Calculate sprung masses (per side)
            # Front/Rear axle weight is LH+RH, so divide by 2 for one side
            # Then subtract unsprung mass (which is already one side)
            sprung_mass_f = (front_axle / 2) - unsprung_f
            sprung_mass_r = (rear_axle / 2) - unsprung_r
            
            # Calculate weight distribution
            front_weight_ratio = front_axle / total_mass
            rear_weight_ratio = rear_axle / total_mass
            
            # Update weight distribution display with beautiful formatting
            self.fw_display.config(text=f"{front_weight_ratio*100:.1f} %")
            self.rw_display.config(text=f"{rear_weight_ratio*100:.1f} %")
            
            # First, calculate the required wheel rate from target frequency
            # This is the total wheel rate needed at the wheel (spring + parametric)
            # Formula: omega = 2*pi*f, K_wheel = m * omega^2
            omega_f = 2 * math.pi * target_f
            omega_r = 2 * math.pi * target_r
            
            required_wheel_rate_f = (sprung_mass_f * omega_f**2) / 1000  # N/mm
            required_wheel_rate_r = (sprung_mass_r * omega_r**2) / 1000  # N/mm
            
            # PARAMETRIC STIFFNESS CONCEPT:
            # Parametric stiffness represents additional stiffness at the wheel
            # (e.g., from bushings, links, etc.) that acts in parallel with the spring
            # Total Wheel Rate = (Spring Rate × MR²) + Parametric Stiffness
            # 
            # Therefore, to achieve the target wheel rate:
            # Spring Rate = (Required Wheel Rate - Parametric Stiffness) / MR²
            #
            # Increasing parametric stiffness REDUCES required spring stiffness
            # to maintain the same ride frequency
            
            spring_stiff_f = (required_wheel_rate_f - parametric_stiff) / (mr_front**2)
            spring_stiff_r = (required_wheel_rate_r - parametric_stiff) / (mr_rear**2)
            
            # Verify: Calculate wheel rate components
            wheel_rate_from_spring_f = spring_stiff_f * (mr_front**2)
            wheel_rate_from_spring_r = spring_stiff_r * (mr_rear**2)
            
            # Total wheel rate (spring contribution + parametric)
            wheel_rate_f_with_param = wheel_rate_from_spring_f + parametric_stiff
            wheel_rate_r_with_param = wheel_rate_from_spring_r + parametric_stiff
            
            # Calculate ride rates (including tire stiffness)
            ride_rate_f = self.calculator.calculate_ride_rate(wheel_rate_f_with_param, tire_stiff)
            ride_rate_r = self.calculator.calculate_ride_rate(wheel_rate_r_with_param, tire_stiff)
            
            # Calculate wheel hop frequencies
            # Wheel hop uses the ride rate (wheel+tire in series) and unsprung mass
            # Formula: f = (1/2π) * sqrt(k/m) where k is in N/m and m is in kg
            wheel_hop_f = self.calculator.calculate_wheel_hop_frequency(wheel_rate_f_with_param, tire_stiff, unsprung_f)
            wheel_hop_r = self.calculator.calculate_wheel_hop_frequency(wheel_rate_r_with_param, tire_stiff, unsprung_r)
            
            # Update results table with proper formatting
            items = self.results_tree.get_children()
            
            self.results_tree.item(items[0], values=('Spring Rate', f'{spring_stiff_f:.2f}', f'{spring_stiff_r:.2f}', 'N/mm'))
            self.results_tree.item(items[1], values=('Wheel Rate (from Spring)', f'{wheel_rate_from_spring_f:.2f}', f'{wheel_rate_from_spring_r:.2f}', 'N/mm'))
            self.results_tree.item(items[2], values=('Total Wheel Rate (Spring+Parametric)', f'{wheel_rate_f_with_param:.2f}', f'{wheel_rate_r_with_param:.2f}', 'N/mm'))
            self.results_tree.item(items[3], values=('Ride Rate', f'{ride_rate_f:.2f}', f'{ride_rate_r:.2f}', 'N/mm'))
            self.results_tree.item(items[4], values=('Wheel Hop Frequency', f'{wheel_hop_f:.2f}', f'{wheel_hop_r:.2f}', 'Hz'))
            
            # Update roll stiffness tab values
            self.roll_wheel_rate_front.delete(0, tk.END)
            self.roll_wheel_rate_front.insert(0, f"{wheel_rate_f_with_param:.2f}")
            
            self.roll_wheel_rate_rear.delete(0, tk.END)
            self.roll_wheel_rate_rear.insert(0, f"{wheel_rate_r_with_param:.2f}")
            
            self.roll_sprung_mass.delete(0, tk.END)
            self.roll_sprung_mass.insert(0, f"{sprung_mass_f*2 + sprung_mass_r*2:.1f}")
            
            # Store total mass for roll calculations
            self.total_vehicle_mass = total_mass
            
            messagebox.showinfo("✓ Success", 
                              f"Ride frequency calculations completed successfully!\n\n"
                              f"Front Sprung Mass (per side): {sprung_mass_f:.1f} kg\n"
                              f"Rear Sprung Mass (per side): {sprung_mass_r:.1f} kg\n"
                              f"Total Sprung Mass: {sprung_mass_f*2 + sprung_mass_r*2:.1f} kg\n\n"
                              f"Parametric Stiffness Effect:\n"
                              f"- Parametric: {parametric_stiff:.1f} N/mm\n"
                              f"- Required Spring Rate Front: {spring_stiff_f:.2f} N/mm\n"
                              f"- Required Spring Rate Rear: {spring_stiff_r:.2f} N/mm")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numbers in all fields.\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")
    
    def calculate_roll_stiffness(self):
        """Calculate roll stiffness requirements based on 14-Step Methodology"""
        try:
            # === INPUTS ===
            # Vehicle
            axle_fr = float(self.front_axle_weight.get())
            axle_rr = float(self.rear_axle_weight.get())
            unsprung_fr = float(self.unsprung_mass_front.get())
            unsprung_rr = float(self.unsprung_mass_rear.get())
            
            cg_height = float(self.roll_cg_height.get())
            rc_fr = float(self.front_roll_center.get())
            rc_rr = float(self.rear_roll_center.get())
            track_fr = float(self.roll_front_track.get())
            track_rr = float(self.roll_rear_track.get())
            
            # Spring & Bush
            wh_rate_fr = float(self.roll_wheel_rate_front.get())
            wh_rate_rr = float(self.roll_wheel_rate_rear.get())
            
            # Tire
            tire_stiff = float(self.tire_stiffness.get()) # Using single value for now
            
            # Targets
            target_angle = float(self.roll_target_angle.get())
            target_dist = float(self.roll_target_dist.get())
            
            # === CALCULATIONS ===
            
            # STEP 1: Sprung Mass
            sprung_fr = axle_fr - 2 * unsprung_fr
            sprung_rr = axle_rr - 2 * unsprung_rr
            sprung_total = sprung_fr + sprung_rr
            
            # STEP 3: Roll Center Height (Mass Weighted)
            rc_height = (sprung_rr / sprung_total) * (rc_rr - rc_fr) + rc_fr
            
            # STEP 4: Roll Moment Arm
            roll_arm = cg_height - rc_height
            
            # STEP 5: Roll Moment @ 0.5G
            roll_moment = sprung_total * 0.5 * 9.81 * roll_arm / 1000
            
            # STEP 6: Tire Roll Stiffness
            deg_to_rad = math.pi / 180
            tire_roll_fr = 0.5 * tire_stiff * (track_fr**2) / 1000 * deg_to_rad
            tire_roll_rr = 0.5 * tire_stiff * (track_rr**2) / 1000 * deg_to_rad
            tire_roll_total = tire_roll_fr + tire_roll_rr
            
            # STEP 7: Spring Wheel Rate (Series with Insulator + Parallel Bush)
            
            # STEP 8: Spring Roll Stiffness
            spring_roll_fr = 0.5 * wh_rate_fr * (track_fr**2) / 1000 * deg_to_rad
            spring_roll_rr = 0.5 * wh_rate_rr * (track_rr**2) / 1000 * deg_to_rad
            spring_roll_total = spring_roll_fr + spring_roll_rr
            
            # STEP 9: Required Total Roll Stiffness
            req_total_roll = roll_moment / target_angle
            
            # STEP 10: Required Suspension Roll Stiffness (Tire Series Effect)
            if tire_roll_total > req_total_roll:
                req_susp_total = req_total_roll * tire_roll_total / (tire_roll_total - req_total_roll)
            else:
                req_susp_total = req_total_roll * 2 # Impossible target
                messagebox.showwarning("Warning", "Tire stiffness too low to achieve target roll angle!")
            
            req_susp_fr = req_susp_total * (target_dist / 100)
            req_susp_rr = req_susp_total * (1 - target_dist / 100)
            
            # STEP 11: Required ARB Roll Stiffness
            req_arb_fr = max(0, req_susp_fr - spring_roll_fr)
            req_arb_rr = max(0, req_susp_rr - spring_roll_rr)
            
            # Store values for ARB Design tab
            self.arb_roll_stiffness_fr_required = req_arb_fr
            self.arb_roll_stiffness_rr_required = req_arb_rr
            
            # === UPDATE OUTPUTS ===
            self.out_rc_height.config(text=f"{rc_height:.1f}")
            self.out_roll_arm.config(text=f"{roll_arm:.1f}")
            self.out_roll_moment.config(text=f"{roll_moment:.1f}")
            
            self.out_tire_roll_fr.config(text=f"{tire_roll_fr:.1f}")
            self.out_tire_roll_rr.config(text=f"{tire_roll_rr:.1f}")
            
            self.out_wh_rate_fr.config(text=f"{wh_rate_fr:.2f}")
            self.out_wh_rate_rr.config(text=f"{wh_rate_rr:.2f}")
            self.out_spring_roll_fr.config(text=f"{spring_roll_fr:.1f}")
            self.out_spring_roll_rr.config(text=f"{spring_roll_rr:.1f}")
            
            self.out_total_req.config(text=f"{req_total_roll:.1f}")
            self.out_susp_req_total.config(text=f"{req_susp_total:.1f}")
            self.out_susp_req_fr.config(text=f"{req_susp_fr:.1f}")
            self.out_susp_req_rr.config(text=f"{req_susp_rr:.1f}")
            
            self.out_arb_req_fr.config(text=f"{req_arb_fr:.1f}")
            self.out_arb_req_rr.config(text=f"{req_arb_rr:.1f}")
            
            # Update ARB Design Tab Input
            self.req_arb_roll_stiffness.delete(0, tk.END)
            self.req_arb_roll_stiffness.insert(0, f"{req_arb_fr + req_arb_rr:.1f}")
            
            messagebox.showinfo("Success", "Roll stiffness calculations completed!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numbers in all fields.\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")
    
    def calculate_arb_design(self, position):
        """Calculate ARB stiffness distribution"""
        try:
            required_total = float(self.req_arb_roll_stiffness.get())
            front_percent = float(self.front_stiffness_percent.get())
            
            if position == 'front':
                arb_stiff_f = required_total * (front_percent / 100)
                arb_stiff_r = required_total * ((100 - front_percent) / 100)
                
                self.front_arb_stiffness_display.delete(0, tk.END)
                self.front_arb_stiffness_display.insert(0, f"{arb_stiff_f:.1f}")
                
                self.rear_arb_stiffness_display.delete(0, tk.END)
                self.rear_arb_stiffness_display.insert(0, f"{arb_stiff_r:.1f}")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numbers.\n{str(e)}")
    
    def calculate_arb_outputs(self, position):
        """
        Calculate ARB wheel rate and bar stiffness based on Chapter 12 methodology
        Following Step 12.3a through 12.3e
        """
        try:
            # Constants
            deg_to_rad = math.radians(1)  # π/180
            
            if position == 'front':
                # Get required ARB roll stiffness from Roll Stiffness tab
                arb_roll_stiffness_required = self.arb_roll_stiffness_fr_required
                
                # Get inputs
                tread = float(self.roll_front_track.get())  # Track width from Roll Stiffness tab
                bush_stiffness = float(self.arb_bush_stiffness_front.get())
                clamp_span = float(self.arb_clamp_span_front.get())
                eye_span = float(self.arb_eye_span_front.get())
                lever_ratio = float(self.arb_lever_ratio_front.get())
                
                # Step 12.3a: Required ARB wheel rate (from roll stiffness)
                arb_wh_required = (arb_roll_stiffness_required * 2 * 1000) / (tread**2 * deg_to_rad)
                
                # Step 12.3b: Bush lever ratio
                bush_lever_ratio = clamp_span / eye_span
                
                # Step 12.3c: Bush stiffness at eye point
                bush_stiffness_at_eye = bush_stiffness * bush_lever_ratio**2
                
                # Step 12.3e: Required bar stiffness (solving series equation)
                # K_bar = (K_bush_eye × K_wh_required) / (2 × (σ² × K_bush_eye - K_wh_required))
                denom = 2 * (lever_ratio**2 * bush_stiffness_at_eye - arb_wh_required)
                
                if denom > 0 and arb_wh_required > 0:
                    arb_bar_stiffness = (bush_stiffness_at_eye * arb_wh_required) / denom
                    warning_msg = ""
                elif arb_wh_required > 0:
                    # Bush too soft - bar alone cannot achieve target
                    arb_bar_stiffness = arb_wh_required / lever_ratio**2  # Approximation
                    warning_msg = "WARNING: FR bush stiffness insufficient for target"
                else:
                    arb_bar_stiffness = 0
                    warning_msg = "WARNING: No ARB required for front"
                
                # Step 12.3d: Combined eye stiffness (for verification)
                if arb_bar_stiffness > 0:
                    combined_eye_stiffness = 1 / (1/(2*arb_bar_stiffness) + 1/bush_stiffness_at_eye)
                else:
                    combined_eye_stiffness = 0
                
                # Update outputs
                self._update_entry(self.arb_wheel_rate_required_front, f"{arb_wh_required:.2f}")
                self._update_entry(self.bush_lever_ratio_front_display, f"{bush_lever_ratio:.3f}")
                self._update_entry(self.bush_stiffness_eye_front_display, f"{bush_stiffness_at_eye:.2f}")
                self._update_entry(self.arb_bar_stiffness_front_display, f"{arb_bar_stiffness:.2f}")
                self._update_entry(self.combined_eye_stiffness_front_display, f"{combined_eye_stiffness:.2f}")
                
                if warning_msg:
                    messagebox.showwarning("Warning", warning_msg)
                else:
                    messagebox.showinfo("Success", "Front ARB calculations completed!")
                
            else:  # rear
                # Get required ARB roll stiffness from Roll Stiffness tab
                arb_roll_stiffness_required = self.arb_roll_stiffness_rr_required
                
                # Get inputs
                tread = float(self.roll_rear_track.get())  # Track width from Roll Stiffness tab
                bush_stiffness = float(self.arb_bush_stiffness_rear.get())
                clamp_span = float(self.arb_clamp_span_rear.get())
                eye_span = float(self.arb_eye_span_rear.get())
                lever_ratio = float(self.arb_lever_ratio_rear.get())
                
                # Step 12.3a: Required ARB wheel rate (from roll stiffness)
                arb_wh_required = (arb_roll_stiffness_required * 2 * 1000) / (tread**2 * deg_to_rad)
                
                # Step 12.3b: Bush lever ratio
                bush_lever_ratio = clamp_span / eye_span
                
                # Step 12.3c: Bush stiffness at eye point
                bush_stiffness_at_eye = bush_stiffness * bush_lever_ratio**2
                
                # Step 12.3e: Required bar stiffness (solving series equation)
                denom = 2 * (lever_ratio**2 * bush_stiffness_at_eye - arb_wh_required)
                
                if denom > 0 and arb_wh_required > 0:
                    arb_bar_stiffness = (bush_stiffness_at_eye * arb_wh_required) / denom
                    warning_msg = ""
                elif arb_wh_required > 0:
                    # Bush too soft - bar alone cannot achieve target
                    arb_bar_stiffness = arb_wh_required / lever_ratio**2  # Approximation
                    warning_msg = "WARNING: RR bush stiffness insufficient for target"
                else:
                    arb_bar_stiffness = 0
                    warning_msg = "WARNING: No ARB required for rear"
                
                # Step 12.3d: Combined eye stiffness (for verification)
                if arb_bar_stiffness > 0:
                    combined_eye_stiffness = 1 / (1/(2*arb_bar_stiffness) + 1/bush_stiffness_at_eye)
                else:
                    combined_eye_stiffness = 0
                
                # Update outputs
                self._update_entry(self.arb_wheel_rate_required_rear, f"{arb_wh_required:.2f}")
                self._update_entry(self.bush_lever_ratio_rear_display, f"{bush_lever_ratio:.3f}")
                self._update_entry(self.bush_stiffness_eye_rear_display, f"{bush_stiffness_at_eye:.2f}")
                self._update_entry(self.arb_bar_stiffness_rear_display, f"{arb_bar_stiffness:.2f}")
                self._update_entry(self.combined_eye_stiffness_rear_display, f"{combined_eye_stiffness:.2f}")
                
                if warning_msg:
                    messagebox.showwarning("Warning", warning_msg)
                else:
                    messagebox.showinfo("Success", "Rear ARB calculations completed!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numbers.\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")
    
    def _update_entry(self, entry_widget, value):
        """Helper function to update readonly entry widgets"""
        entry_widget.config(state='normal')
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, value)
        entry_widget.config(state='readonly')


def main():
    root = tk.Tk()
    app = SuspensionCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()