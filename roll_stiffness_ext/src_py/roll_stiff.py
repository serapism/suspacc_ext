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
        """Create header with DESIGN and BENCHMARK buttons"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Logo placeholder
        logo_frame = ttk.Frame(header_frame, relief=tk.RIDGE, borderwidth=2, width=80, height=30)
        logo_frame.grid(row=0, column=0, padx=5)
        logo_label = ttk.Label(logo_frame, text="HONDA", foreground="red")
        logo_label.pack()
        
        # Mode buttons
        ttk.Button(header_frame, text="DESIGN", width=15).grid(row=0, column=1, padx=5)
        ttk.Button(header_frame, text="BENCHMARK", width=15).grid(row=0, column=2, padx=5)
        
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
        """Create Roll Stiffness tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ROLL STIFFNESS")
        
        # Main layout
        left_frame = ttk.Frame(tab)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        right_frame = ttk.Frame(tab)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # ===== LEFT SIDE =====
        
        # Output from Ride Frequency Tab
        freq_output_frame = ttk.LabelFrame(left_frame, text="OUTPUT FROM RIDE FREQUENCY TAB", padding="10")
        freq_output_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Ride Rates
        ttk.Label(freq_output_frame, text="RIDE RATES", font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=2)
        
        ttk.Label(freq_output_frame, text="Ride Rate (Front)").grid(row=1, column=0, sticky=tk.W)
        self.roll_ride_rate_front = ttk.Entry(freq_output_frame, width=12)
        self.roll_ride_rate_front.grid(row=1, column=1, padx=5)
        ttk.Label(freq_output_frame, text="N/mm").grid(row=1, column=2)
        
        ttk.Label(freq_output_frame, text="Ride Rate (Rear)").grid(row=2, column=0, sticky=tk.W)
        self.roll_ride_rate_rear = ttk.Entry(freq_output_frame, width=12)
        self.roll_ride_rate_rear.grid(row=2, column=1, padx=5)
        ttk.Label(freq_output_frame, text="N/mm").grid(row=2, column=2)
        
        # Wheel Rates
        ttk.Label(freq_output_frame, text="WHEEL RATES", font=('Arial', 9, 'bold')).grid(row=3, column=0, columnspan=2, pady=(10,0))
        
        ttk.Label(freq_output_frame, text="Wheel Rate (Front)").grid(row=4, column=0, sticky=tk.W)
        self.roll_wheel_rate_front = ttk.Entry(freq_output_frame, width=12)
        self.roll_wheel_rate_front.grid(row=4, column=1, padx=5)
        ttk.Label(freq_output_frame, text="N/mm").grid(row=4, column=2)
        
        ttk.Label(freq_output_frame, text="Wheel Rate (Rear)").grid(row=5, column=0, sticky=tk.W)
        self.roll_wheel_rate_rear = ttk.Entry(freq_output_frame, width=12)
        self.roll_wheel_rate_rear.grid(row=5, column=1, padx=5)
        ttk.Label(freq_output_frame, text="N/mm").grid(row=5, column=2)
        
        # Spring Rates
        ttk.Label(freq_output_frame, text="SPRING RATES", font=('Arial', 9, 'bold')).grid(row=6, column=0, columnspan=2, pady=(10,0))
        
        ttk.Label(freq_output_frame, text="Spring Rate (Front)").grid(row=7, column=0, sticky=tk.W)
        self.roll_spring_rate_front = ttk.Entry(freq_output_frame, width=12)
        self.roll_spring_rate_front.grid(row=7, column=1, padx=5)
        ttk.Label(freq_output_frame, text="N/mm").grid(row=7, column=2)
        
        ttk.Label(freq_output_frame, text="Spring Rate (Rear)").grid(row=8, column=0, sticky=tk.W)
        self.roll_spring_rate_rear = ttk.Entry(freq_output_frame, width=12)
        self.roll_spring_rate_rear.grid(row=8, column=1, padx=5)
        ttk.Label(freq_output_frame, text="N/mm").grid(row=8, column=2)
        
        # Vehicle Inputs
        vehicle_inputs_frame = ttk.LabelFrame(left_frame, text="VEHICLE INPUTS", padding="10")
        vehicle_inputs_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(vehicle_inputs_frame, text="Vehicle Sprung Mass (D+1)").grid(row=0, column=0, sticky=tk.W)
        self.roll_sprung_mass = ttk.Entry(vehicle_inputs_frame, width=12)
        self.roll_sprung_mass.grid(row=0, column=1, padx=5)
        ttk.Label(vehicle_inputs_frame, text="kg").grid(row=0, column=2)
        
        ttk.Label(vehicle_inputs_frame, text="CG Longitudinal Distance from Front Axle").grid(row=1, column=0, sticky=tk.W)
        self.roll_cg_long = ttk.Entry(vehicle_inputs_frame, width=12)
        self.roll_cg_long.grid(row=1, column=1, padx=5)
        ttk.Label(vehicle_inputs_frame, text="mm").grid(row=1, column=2)
        
        ttk.Label(vehicle_inputs_frame, text="CG Height from ground").grid(row=2, column=0, sticky=tk.W)
        self.roll_cg_height = ttk.Entry(vehicle_inputs_frame, width=12)
        self.roll_cg_height.grid(row=2, column=1, padx=5)
        ttk.Label(vehicle_inputs_frame, text="mm").grid(row=2, column=2)
        
        ttk.Label(vehicle_inputs_frame, text="Wheelbase").grid(row=3, column=0, sticky=tk.W)
        self.roll_wheelbase = ttk.Entry(vehicle_inputs_frame, width=12)
        self.roll_wheelbase.grid(row=3, column=1, padx=5)
        ttk.Label(vehicle_inputs_frame, text="mm").grid(row=3, column=2)
        
        ttk.Label(vehicle_inputs_frame, text="Front Track Width").grid(row=4, column=0, sticky=tk.W)
        self.roll_front_track = ttk.Entry(vehicle_inputs_frame, width=12)
        self.roll_front_track.grid(row=4, column=1, padx=5)
        ttk.Label(vehicle_inputs_frame, text="mm").grid(row=4, column=2)
        
        ttk.Label(vehicle_inputs_frame, text="Rear Track Width").grid(row=5, column=0, sticky=tk.W)
        self.roll_rear_track = ttk.Entry(vehicle_inputs_frame, width=12)
        self.roll_rear_track.grid(row=5, column=1, padx=5)
        ttk.Label(vehicle_inputs_frame, text="mm").grid(row=5, column=2)
        
        # Suspension Inputs
        susp_inputs_frame = ttk.LabelFrame(left_frame, text="SUSPENSION INPUTS", padding="10")
        susp_inputs_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(susp_inputs_frame, text="Front Roll Center Height").grid(row=0, column=0, sticky=tk.W)
        self.front_roll_center = ttk.Entry(susp_inputs_frame, width=12)
        self.front_roll_center.grid(row=0, column=1, padx=5)
        ttk.Label(susp_inputs_frame, text="mm").grid(row=0, column=2)
        
        ttk.Label(susp_inputs_frame, text="Rear Roll Center Height").grid(row=1, column=0, sticky=tk.W)
        self.rear_roll_center = ttk.Entry(susp_inputs_frame, width=12)
        self.rear_roll_center.grid(row=1, column=1, padx=5)
        ttk.Label(susp_inputs_frame, text="mm").grid(row=1, column=2)
        
        ttk.Label(susp_inputs_frame, text="Spring Track (Front)").grid(row=2, column=0, sticky=tk.W)
        self.spring_track_front = ttk.Entry(susp_inputs_frame, width=12)
        self.spring_track_front.grid(row=2, column=1, padx=5)
        ttk.Label(susp_inputs_frame, text="mm").grid(row=2, column=2)
        
        ttk.Label(susp_inputs_frame, text="Spring Track (Rear)").grid(row=3, column=0, sticky=tk.W)
        self.spring_track_rear = ttk.Entry(susp_inputs_frame, width=12)
        self.spring_track_rear.grid(row=3, column=1, padx=5)
        ttk.Label(susp_inputs_frame, text="mm").grid(row=3, column=2)
        
        # Rear Twist Beam checkbox
        self.rear_twist_beam = tk.BooleanVar()
        ttk.Checkbutton(susp_inputs_frame, text="Rear Twist Beam Suspension?", 
                       variable=self.rear_twist_beam).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(susp_inputs_frame, text="Twist Beam Stiffness").grid(row=5, column=0, sticky=tk.W)
        self.twist_beam_stiffness = ttk.Entry(susp_inputs_frame, width=12)
        self.twist_beam_stiffness.grid(row=5, column=1, padx=5)
        ttk.Label(susp_inputs_frame, text="Nm/deg").grid(row=5, column=2)
        
        ttk.Button(left_frame, text="Calculate Required Roll Stiffness", 
                  command=self.calculate_roll_stiffness, width=30).grid(row=3, column=0, pady=10)
        
        # ===== RIGHT SIDE =====
        
        # Target Roll Gradient
        target_roll_frame = ttk.LabelFrame(right_frame, text="TARGET ROLL GRADIENT", padding="10")
        target_roll_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(target_roll_frame, text="Roll Gradient").grid(row=0, column=0, sticky=tk.W)
        self.target_roll_gradient = ttk.Entry(target_roll_frame, width=12)
        self.target_roll_gradient.grid(row=0, column=1, padx=5)
        ttk.Label(target_roll_frame, text="deg/g").grid(row=0, column=2)
        
        # Intermediate Outputs
        intermediate_frame = ttk.LabelFrame(right_frame, text="INTERMEDIATE OUTPUTS", 
                                          padding="10", relief=tk.GROOVE)
        intermediate_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Configure background color
        intermediate_frame.configure()
        
        ttk.Label(intermediate_frame, text="Roll Center Height at CG", 
                 background='lightgreen').grid(row=0, column=0, sticky=tk.W)
        self.roll_center_at_cg = ttk.Entry(intermediate_frame, width=12)
        self.roll_center_at_cg.grid(row=0, column=1, padx=5)
        ttk.Label(intermediate_frame, text="mm", background='lightgreen').grid(row=0, column=2)
        
        ttk.Label(intermediate_frame, text="Roll Moment", 
                 background='lightgreen').grid(row=1, column=0, sticky=tk.W)
        self.roll_moment = ttk.Entry(intermediate_frame, width=12)
        self.roll_moment.grid(row=1, column=1, padx=5)
        ttk.Label(intermediate_frame, text="Nm", background='lightgreen').grid(row=1, column=2)
        
        # Springs Output
        springs_frame = ttk.LabelFrame(right_frame, text="SPRINGS", padding="10", relief=tk.GROOVE)
        springs_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(springs_frame, text="Front Roll Stiffness", background='cyan').grid(row=0, column=0, sticky=tk.W)
        self.front_roll_stiffness_springs = ttk.Entry(springs_frame, width=12)
        self.front_roll_stiffness_springs.grid(row=0, column=1, padx=5)
        ttk.Label(springs_frame, text="Nm/deg", background='cyan').grid(row=0, column=2)
        
        ttk.Label(springs_frame, text="Total Roll Stiffness", background='cyan').grid(row=1, column=0, sticky=tk.W)
        self.total_roll_stiffness_springs = ttk.Entry(springs_frame, width=12)
        self.total_roll_stiffness_springs.grid(row=1, column=1, padx=5)
        ttk.Label(springs_frame, text="Nm/deg", background='cyan').grid(row=1, column=2)
        
        ttk.Label(springs_frame, text="Required Suspension Roll Stiffness", 
                 background='cyan').grid(row=2, column=0, sticky=tk.W)
        self.required_susp_roll_stiffness = ttk.Entry(springs_frame, width=12)
        self.required_susp_roll_stiffness.grid(row=2, column=1, padx=5)
        ttk.Label(springs_frame, text="Nm/deg", background='cyan').grid(row=2, column=2)
        
        ttk.Label(springs_frame, text="Rear Roll Stiffness", background='cyan').grid(row=3, column=0, sticky=tk.W)
        self.rear_roll_stiffness_springs = ttk.Entry(springs_frame, width=12)
        self.rear_roll_stiffness_springs.grid(row=3, column=1, padx=5)
        ttk.Label(springs_frame, text="Nm/deg", background='cyan').grid(row=3, column=2)
        
        ttk.Label(springs_frame, text="Front/Rear Roll Stiffness Distribution", 
                 background='cyan').grid(row=4, column=0, sticky=tk.W)
        self.fr_roll_stiffness_dist = ttk.Entry(springs_frame, width=12)
        self.fr_roll_stiffness_dist.grid(row=4, column=1, padx=5)
        ttk.Label(springs_frame, text="", background='cyan').grid(row=4, column=2)
        
        ttk.Label(springs_frame, text="Additional Roll Stiffness Required", 
                 font=('Arial', 9, 'bold'), background='yellow').grid(row=5, column=0, sticky=tk.W)
        self.additional_roll_stiffness = ttk.Entry(springs_frame, width=12)
        self.additional_roll_stiffness.grid(row=5, column=1, padx=5)
        ttk.Label(springs_frame, text="Nm/deg", background='yellow').grid(row=5, column=2)
        
        ttk.Label(springs_frame, text="Anti Roll Bar is required", 
                 font=('Arial', 10, 'bold'), foreground='red').grid(row=6, column=0, 
                                                                     columnspan=3, pady=5)
        
        # Suspension Roll Stiffness
        susp_roll_frame = ttk.LabelFrame(right_frame, text="SUSPENSION ROLL STIFFNESS", 
                                        padding="10", relief=tk.GROOVE)
        susp_roll_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(susp_roll_frame, text="Total Roll Stiffness", background='cyan').grid(row=0, column=0, sticky=tk.W)
        self.total_susp_roll_stiffness = ttk.Entry(susp_roll_frame, width=12)
        self.total_susp_roll_stiffness.grid(row=0, column=1, padx=5)
        ttk.Label(susp_roll_frame, text="Nm/deg", background='cyan').grid(row=0, column=2)
        
        ttk.Label(susp_roll_frame, text="Total Front Roll stiffness(incl/arb)", 
                 background='cyan').grid(row=1, column=0, sticky=tk.W)
        self.total_front_roll_with_arb = ttk.Entry(susp_roll_frame, width=12)
        self.total_front_roll_with_arb.grid(row=1, column=1, padx=5)
        ttk.Label(susp_roll_frame, text="Nm/deg", background='cyan').grid(row=1, column=2)
        
        ttk.Label(susp_roll_frame, text="Total Rear Roll stiffness(incl/arb)", 
                 background='cyan').grid(row=2, column=0, sticky=tk.W)
        self.total_rear_roll_with_arb = ttk.Entry(susp_roll_frame, width=12)
        self.total_rear_roll_with_arb.grid(row=2, column=1, padx=5)
        ttk.Label(susp_roll_frame, text="Nm/deg", background='cyan').grid(row=2, column=2)
        
        ttk.Label(susp_roll_frame, text="F/R Roll Stiffness Distribution", 
                 background='cyan').grid(row=3, column=0, sticky=tk.W)
        self.fr_susp_roll_dist = ttk.Entry(susp_roll_frame, width=12)
        self.fr_susp_roll_dist.grid(row=3, column=1, padx=5)
        ttk.Label(susp_roll_frame, text="", background='cyan').grid(row=3, column=2)
        
    def create_arb_design_tab(self):
        """Create ARB Design tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ARB DESIGN")
        
        # Main container
        main_container = ttk.Frame(tab)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Top section
        top_frame = ttk.Frame(main_container)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(top_frame, text="Required Effective ARB Roll Stiffness", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.req_arb_roll_stiffness = ttk.Entry(top_frame, width=12)
        self.req_arb_roll_stiffness.grid(row=0, column=1, padx=5)
        ttk.Label(top_frame, text="Nm/deg").grid(row=0, column=2)
        
        # ARB Track
        ttk.Label(top_frame, text="ARB Track (Front)").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.arb_track_front = ttk.Entry(top_frame, width=12)
        self.arb_track_front.grid(row=1, column=1, padx=5)
        ttk.Label(top_frame, text="mm").grid(row=1, column=2)
        
        ttk.Label(top_frame, text="Front Track Width").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.arb_front_track_width = ttk.Entry(top_frame, width=12)
        self.arb_front_track_width.grid(row=2, column=1, padx=5)
        ttk.Label(top_frame, text="mm").grid(row=2, column=2)
        
        ttk.Label(top_frame, text="ARB Track (Rear)").grid(row=1, column=3, sticky=tk.W, padx=5)
        self.arb_track_rear = ttk.Entry(top_frame, width=12)
        self.arb_track_rear.grid(row=1, column=4, padx=5)
        ttk.Label(top_frame, text="mm").grid(row=1, column=5)
        
        ttk.Label(top_frame, text="Rear Track Width").grid(row=2, column=3, sticky=tk.W, padx=5)
        self.arb_rear_track_width = ttk.Entry(top_frame, width=12)
        self.arb_rear_track_width.grid(row=2, column=4, padx=5)
        ttk.Label(top_frame, text="mm").grid(row=2, column=5)
        
        # ARB checkboxes
        checkbox_frame = ttk.Frame(top_frame)
        checkbox_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.front_arb_enabled = tk.BooleanVar(value=True)
        self.rear_arb_enabled = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(checkbox_frame, text="Front ARB", 
                       variable=self.front_arb_enabled).grid(row=0, column=0, padx=20)
        ttk.Checkbutton(checkbox_frame, text="Rear ARB", 
                       variable=self.rear_arb_enabled).grid(row=0, column=1, padx=20)
        
        ttk.Label(top_frame, text="Front stiffness n%").grid(row=4, column=0, sticky=tk.W, padx=5)
        self.front_stiffness_percent = ttk.Entry(top_frame, width=12)
        self.front_stiffness_percent.grid(row=4, column=1, padx=5)
        
        # Intermediate Outputs
        intermediate_frame = ttk.LabelFrame(main_container, text="INTERMEDIATE OUTPUTS", 
                                          padding="10", relief=tk.GROOVE)
        intermediate_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Front ARB section
        front_arb_frame = ttk.Frame(intermediate_frame)
        front_arb_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        
        ttk.Label(front_arb_frame, text="Front ARB Stiffness (Nm/deg)", 
                 background='lightgreen').grid(row=0, column=0, sticky=tk.W)
        self.front_arb_stiffness_display = ttk.Entry(front_arb_frame, width=12)
        self.front_arb_stiffness_display.grid(row=0, column=1, padx=5)
        ttk.Button(front_arb_frame, text="Calculate Stiffness", 
                  command=lambda: self.calculate_arb_design('front')).grid(row=0, column=2, padx=5)
        
        ttk.Label(front_arb_frame, text="Rear ARB Stiffness (Nm/deg)", 
                 background='lightgreen').grid(row=1, column=0, sticky=tk.W)
        self.rear_arb_stiffness_display = ttk.Entry(front_arb_frame, width=12)
        self.rear_arb_stiffness_display.grid(row=1, column=1, padx=5)
        
        # ARB Inputs and Outputs - Front
        arb_front_io_frame = ttk.LabelFrame(main_container, text="ARB INPUTS (FRONT)", padding="10")
        arb_front_io_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Left side - inputs
        left_inputs = ttk.Frame(arb_front_io_frame)
        left_inputs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=10)
        
        ttk.Label(left_inputs, text="Half ARB Track (L)").grid(row=0, column=0, sticky=tk.W)
        self.half_arb_track_front = ttk.Entry(left_inputs, width=12)
        self.half_arb_track_front.grid(row=0, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=0, column=2)
        
        ttk.Label(left_inputs, text="ARB Arm Length (L2)").grid(row=1, column=0, sticky=tk.W)
        self.arb_arm_length_front = ttk.Entry(left_inputs, width=12)
        self.arb_arm_length_front.grid(row=1, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=1, column=2)
        
        ttk.Label(left_inputs, text="a").grid(row=2, column=0, sticky=tk.W)
        self.arb_a_front = ttk.Entry(left_inputs, width=12)
        self.arb_a_front.grid(row=2, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=2, column=2)
        
        ttk.Label(left_inputs, text="b").grid(row=3, column=0, sticky=tk.W)
        self.arb_b_front = ttk.Entry(left_inputs, width=12)
        self.arb_b_front.grid(row=3, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=3, column=2)
        
        ttk.Label(left_inputs, text="c").grid(row=4, column=0, sticky=tk.W)
        self.arb_c_front = ttk.Entry(left_inputs, width=12)
        self.arb_c_front.grid(row=4, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=4, column=2)
        
        ttk.Label(left_inputs, text="L1").grid(row=5, column=0, sticky=tk.W)
        self.arb_l1_front = ttk.Entry(left_inputs, width=12)
        self.arb_l1_front.grid(row=5, column=1, padx=5)
        ttk.Label(left_inputs, text="mm").grid(row=5, column=2)
        
        # Middle - diagram placeholder
        diagram_frame = ttk.Frame(arb_front_io_frame, relief=tk.RIDGE, borderwidth=2, width=250, height=200)
        diagram_frame.grid(row=0, column=1, padx=20, pady=10)
        diagram_frame.grid_propagate(False)
        
        canvas = tk.Canvas(diagram_frame, width=240, height=190, bg='white')
        canvas.pack()
        
        # Draw simple ARB diagram
        # Horizontal bar
        canvas.create_line(20, 100, 220, 100, width=3)
        # Vertical arms
        canvas.create_line(60, 100, 60, 150, width=2)
        canvas.create_line(180, 100, 180, 150, width=2)
        # Labels
        canvas.create_text(120, 85, text="L (Half ARB Track)")
        canvas.create_text(60, 165, text="L2")
        canvas.create_text(30, 50, text="Anti-roll bar geometry used in SAE Spring Design Manual", 
                          font=('Arial', 7))
        
        # Right side - outputs
        right_outputs = ttk.Frame(arb_front_io_frame)
        right_outputs.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N), padx=10)
        
        ttk.Label(right_outputs, text="ARB INPUTS (REAR)", font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=3)
        
        ttk.Label(right_outputs, text="Half ARB Track (L)").grid(row=1, column=0, sticky=tk.W)
        self.half_arb_track_rear = ttk.Entry(right_outputs, width=12)
        self.half_arb_track_rear.grid(row=1, column=1, padx=5)
        ttk.Label(right_outputs, text="mm").grid(row=1, column=2)
        
        ttk.Label(right_outputs, text="ARB Arm Length (L2)").grid(row=2, column=0, sticky=tk.W)
        self.arb_arm_length_rear = ttk.Entry(right_outputs, width=12)
        self.arb_arm_length_rear.grid(row=2, column=1, padx=5)
        ttk.Label(right_outputs, text="mm").grid(row=2, column=2)
        
        ttk.Label(right_outputs, text="a").grid(row=3, column=0, sticky=tk.W)
        self.arb_a_rear = ttk.Entry(right_outputs, width=12)
        self.arb_a_rear.grid(row=3, column=1, padx=5)
        ttk.Label(right_outputs, text="mm").grid(row=3, column=2)
        
        ttk.Label(right_outputs, text="b").grid(row=4, column=0, sticky=tk.W)
        self.arb_b_rear = ttk.Entry(right_outputs, width=12)
        self.arb_b_rear.grid(row=4, column=1, padx=5)
        ttk.Label(right_outputs, text="mm").grid(row=4, column=2)
        
        ttk.Label(right_outputs, text="c").grid(row=5, column=0, sticky=tk.W)
        self.arb_c_rear = ttk.Entry(right_outputs, width=12)
        self.arb_c_rear.grid(row=5, column=1, padx=5)
        ttk.Label(right_outputs, text="mm").grid(row=5, column=2)
        
        # Bottom outputs section
        bottom_outputs = ttk.Frame(arb_front_io_frame)
        bottom_outputs.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Front outputs
        front_out_frame = ttk.Frame(bottom_outputs, relief=tk.GROOVE, borderwidth=2)
        front_out_frame.grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(front_out_frame, text="ARB Diameter Front (mm)", background='cyan').grid(row=0, column=0, sticky=tk.W, padx=5)
        self.arb_diameter_front_display = ttk.Entry(front_out_frame, width=12)
        self.arb_diameter_front_display.grid(row=0, column=1, padx=5)
        
        ttk.Label(front_out_frame, text="ARB Stiffness Front (Nm/deg)", background='cyan').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.arb_stiffness_front_final = ttk.Entry(front_out_frame, width=12)
        self.arb_stiffness_front_final.grid(row=1, column=1, padx=5)
        
        ttk.Label(front_out_frame, text="ARB Weight Front (kg)", background='cyan').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.arb_weight_front = ttk.Entry(front_out_frame, width=12)
        self.arb_weight_front.grid(row=2, column=1, padx=5)
        
        ttk.Button(front_out_frame, text="Calculate Outputs", 
                  command=lambda: self.calculate_arb_outputs('front')).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Rear outputs
        rear_out_frame = ttk.Frame(bottom_outputs, relief=tk.GROOVE, borderwidth=2)
        rear_out_frame.grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(rear_out_frame, text="ARB Diameter Rear (mm)", background='cyan').grid(row=0, column=0, sticky=tk.W, padx=5)
        self.arb_diameter_rear_display = ttk.Entry(rear_out_frame, width=12)
        self.arb_diameter_rear_display.grid(row=0, column=1, padx=5)
        
        ttk.Label(rear_out_frame, text="ARB Stiffness Rear (Nm/deg)", background='cyan').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.arb_stiffness_rear_final = ttk.Entry(rear_out_frame, width=12)
        self.arb_stiffness_rear_final.grid(row=1, column=1, padx=5)
        
        ttk.Label(rear_out_frame, text="ARB Weight Rear (kg)", background='cyan').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.arb_weight_rear = ttk.Entry(rear_out_frame, width=12)
        self.arb_weight_rear.grid(row=2, column=1, padx=5)
        
        # Total ARB weight
        total_frame = ttk.Frame(bottom_outputs)
        total_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(total_frame, text="Total ARB", font=('Arial', 10, 'bold'), background='cyan').grid(row=0, column=0)
        self.total_arb_weight = ttk.Entry(total_frame, width=12)
        self.total_arb_weight.grid(row=0, column=1, padx=5)
        ttk.Label(total_frame, text="kg", background='cyan').grid(row=0, column=2)
        
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
        self.roll_wheelbase.insert(0, "2750")
        self.roll_front_track.insert(0, "1630")
        self.roll_rear_track.insert(0, "1630")
        self.front_roll_center.insert(0, "68")
        self.rear_roll_center.insert(0, "138")
        self.spring_track_front.insert(0, "1268")
        self.spring_track_rear.insert(0, "1240")
        self.target_roll_gradient.insert(0, "4.5")
        
        # ARB Design tab
        self.arb_track_front.insert(0, "1122.8")
        self.arb_track_rear.insert(0, "744.5")
        self.arb_front_track_width.insert(0, "1630")
        self.arb_rear_track_width.insert(0, "1630")
        self.front_stiffness_percent.insert(0, "60")
        
        # ARB geometry
        self.arb_arm_length_front.insert(0, "298.5")
        self.arb_arm_length_rear.insert(0, "298.5")
        self.half_arb_track_front.insert(0, "561.4")
        self.half_arb_track_rear.insert(0, "372.3")
        
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
            self.roll_ride_rate_front.delete(0, tk.END)
            self.roll_ride_rate_front.insert(0, f"{ride_rate_f:.2f}")
            
            self.roll_ride_rate_rear.delete(0, tk.END)
            self.roll_ride_rate_rear.insert(0, f"{ride_rate_r:.2f}")
            
            self.roll_wheel_rate_front.delete(0, tk.END)
            self.roll_wheel_rate_front.insert(0, f"{wheel_rate_f_with_param:.2f}")
            
            self.roll_wheel_rate_rear.delete(0, tk.END)
            self.roll_wheel_rate_rear.insert(0, f"{wheel_rate_r_with_param:.2f}")
            
            self.roll_spring_rate_front.delete(0, tk.END)
            self.roll_spring_rate_front.insert(0, f"{spring_stiff_f:.2f}")
            
            self.roll_spring_rate_rear.delete(0, tk.END)
            self.roll_spring_rate_rear.insert(0, f"{spring_stiff_r:.2f}")
            
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
        """Calculate roll stiffness requirements"""
        try:
            # Get spring rates
            spring_rate_f = float(self.roll_spring_rate_front.get())
            spring_rate_r = float(self.roll_spring_rate_rear.get())
            
            # Get motion ratios from ride frequency tab
            mr_front = float(self.motion_ratio_front.get())
            mr_rear = float(self.motion_ratio_rear.get())
            
            # Get track widths
            track_f = float(self.spring_track_front.get())
            track_r = float(self.spring_track_rear.get())
            
            # Calculate roll stiffness from springs
            roll_stiff_f = self.calculator.calculate_roll_stiffness(spring_rate_f, track_f, mr_front)
            roll_stiff_r = self.calculator.calculate_roll_stiffness(spring_rate_r, track_r, mr_rear)
            
            total_spring_roll = roll_stiff_f + roll_stiff_r
            
            # Get vehicle parameters
            sprung_mass = float(self.roll_sprung_mass.get())
            cg_height = float(self.roll_cg_height.get())
            wb = float(self.roll_wheelbase.get())
            front_rc = float(self.front_roll_center.get())
            rear_rc = float(self.rear_roll_center.get())
            cg_long = float(self.roll_cg_long.get())
            roll_gradient = float(self.target_roll_gradient.get())
            
            # Calculate roll center at CG
            rear_weight_ratio = cg_long / wb
            front_weight_ratio = 1 - rear_weight_ratio
            rc_at_cg = front_rc * front_weight_ratio + rear_rc * rear_weight_ratio
            
            # Calculate roll moment arm
            roll_arm = cg_height - rc_at_cg
            
            # Calculate required total roll stiffness
            # Using simplified formula: K_roll_total = (M * g * h_roll) / (roll_gradient * pi/180)
            required_total = (sprung_mass * 9.81 * roll_arm / 1000) / (roll_gradient * math.pi / 180)
            
            # Calculate additional roll stiffness needed
            additional_needed = max(0, required_total - total_spring_roll)
            
            # Calculate front/rear distribution
            front_roll_dist = (roll_stiff_f / total_spring_roll * 100) if total_spring_roll > 0 else 50
            
            # Update displays
            self.front_roll_stiffness_springs.delete(0, tk.END)
            self.front_roll_stiffness_springs.insert(0, f"{roll_stiff_f:.1f}")
            
            self.rear_roll_stiffness_springs.delete(0, tk.END)
            self.rear_roll_stiffness_springs.insert(0, f"{roll_stiff_r:.1f}")
            
            self.total_roll_stiffness_springs.delete(0, tk.END)
            self.total_roll_stiffness_springs.insert(0, f"{total_spring_roll:.1f}")
            
            self.required_susp_roll_stiffness.delete(0, tk.END)
            self.required_susp_roll_stiffness.insert(0, f"{required_total:.1f}")
            
            self.additional_roll_stiffness.delete(0, tk.END)
            self.additional_roll_stiffness.insert(0, f"{additional_needed:.1f}")
            
            self.fr_roll_stiffness_dist.delete(0, tk.END)
            self.fr_roll_stiffness_dist.insert(0, f"{front_roll_dist:.1f}/{100-front_roll_dist:.1f}")
            
            self.roll_center_at_cg.delete(0, tk.END)
            self.roll_center_at_cg.insert(0, f"{rc_at_cg:.1f}")
            
            self.roll_moment.delete(0, tk.END)
            roll_moment = sprung_mass * 9.81 * roll_arm / 1000
            self.roll_moment.insert(0, f"{roll_moment:.0f}")
            
            # Update ARB design tab with required ARB stiffness
            self.req_arb_roll_stiffness.delete(0, tk.END)
            self.req_arb_roll_stiffness.insert(0, f"{additional_needed:.1f}")
            
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
        """Calculate ARB diameter and outputs"""
        try:
            if position == 'front':
                arb_stiffness = float(self.front_arb_stiffness_display.get())
                arm_length = float(self.arb_arm_length_front.get())
                half_track = float(self.half_arb_track_front.get())
                
                # Calculate diameter
                diameter, wheel_rate, roll_stiff = self.calculator.calculate_arb_diameter(
                    arb_stiffness, arm_length, half_track
                )
                
                self.arb_diameter_front_display.delete(0, tk.END)
                self.arb_diameter_front_display.insert(0, f"{diameter:.2f}")
                
                self.arb_stiffness_front_final.delete(0, tk.END)
                self.arb_stiffness_front_final.insert(0, f"{roll_stiff:.1f}")
                
                # Estimate weight (simplified)
                weight = 0.05 * diameter  # Rough estimate
                self.arb_weight_front.delete(0, tk.END)
                self.arb_weight_front.insert(0, f"{weight:.2f}")
                
            else:  # rear
                arb_stiffness = float(self.rear_arb_stiffness_display.get())
                arm_length = float(self.arb_arm_length_rear.get())
                half_track = float(self.half_arb_track_rear.get())
                
                diameter, wheel_rate, roll_stiff = self.calculator.calculate_arb_diameter(
                    arb_stiffness, arm_length, half_track
                )
                
                self.arb_diameter_rear_display.delete(0, tk.END)
                self.arb_diameter_rear_display.insert(0, f"{diameter:.2f}")
                
                self.arb_stiffness_rear_final.delete(0, tk.END)
                self.arb_stiffness_rear_final.insert(0, f"{roll_stiff:.1f}")
                
                weight = 0.05 * diameter
                self.arb_weight_rear.delete(0, tk.END)
                self.arb_weight_rear.insert(0, f"{weight:.2f}")
            
            messagebox.showinfo("Success", f"{position.title()} ARB calculations completed!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numbers.\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")


def main():
    root = tk.Tk()
    app = SuspensionCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()