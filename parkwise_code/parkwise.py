import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, time
import csv
from matplotlib.patches import Rectangle
import numpy as np

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login - Smart Parking System")
        self.root.geometry("500x400")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)
        
        # Custom colors
        self.bg_color = "#2c3e50"
        self.primary_color = "#3498db"
        self.secondary_color = "#2980b9"
        self.accent_color = "#e74c3c"
        self.text_color = "#ecf0f1"
        
        # Main frame
        login_frame = tk.Frame(root, bg=self.bg_color, padx=30, pady=30)
        login_frame.pack(fill="both", expand=True)
        
        # App title
        title_label = tk.Label(
            login_frame, 
            text="SMART PARKING SYSTEM", 
            font=("Helvetica", 24, "bold"), 
            fg=self.primary_color, 
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # Admin login label
        login_label = tk.Label(
            login_frame, 
            text="ADMIN LOGIN", 
            font=("Helvetica", 18), 
            fg=self.text_color, 
            bg=self.bg_color
        )
        login_label.pack(pady=(0, 30))
        
        # Username frame
        username_frame = tk.Frame(login_frame, bg=self.bg_color)
        username_frame.pack(fill="x", pady=10)
        
        tk.Label(
            username_frame, 
            text="Username:", 
            font=("Helvetica", 14), 
            fg=self.text_color, 
            bg=self.bg_color
        ).pack(side="left", padx=10)
        
        self.username_entry = tk.Entry(
            username_frame, 
            font=("Helvetica", 14), 
            bg="#34495e", 
            fg=self.text_color, 
            insertbackground="white",
            relief="flat",
            width=20
        )
        self.username_entry.pack(side="right", expand=True, fill="x", padx=10)
        
        # Password frame
        password_frame = tk.Frame(login_frame, bg=self.bg_color)
        password_frame.pack(fill="x", pady=10)
        
        tk.Label(
            password_frame, 
            text="Password:", 
            font=("Helvetica", 14), 
            fg=self.text_color, 
            bg=self.bg_color
        ).pack(side="left", padx=10)
        
        self.password_entry = tk.Entry(
            password_frame, 
            font=("Helvetica", 14), 
            show="*", 
            bg="#34495e", 
            fg=self.text_color,
            insertbackground="white",
            relief="flat",
            width=20
        )
        self.password_entry.pack(side="right", expand=True, fill="x", padx=10)
        
        # Login button
        login_btn = tk.Button(
            login_frame, 
            text="LOGIN", 
            command=self.authenticate,
            bg=self.primary_color, 
            fg="white", 
            font=("Helvetica", 14, "bold"),
            activebackground=self.secondary_color,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            width=15
        )
        login_btn.pack(pady=30)
        
        # Hover effects
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg=self.secondary_color))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg=self.primary_color))
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username == "admin" and password == "admin123":
            self.root.destroy()
            # Start the main application
            root = tk.Tk()
            app = ParkingAdminSystem(root)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class ParkingAdminSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel - Smart Parking System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f2f5")
        
        # Database connection
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="parking_system"
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {err}")
            self.root.destroy()
            return
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background="#f0f2f5")
        self.style.configure('TLabel', background="#f0f2f5", font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), foreground="#2c3e50")
        
        # Color scheme
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.danger_color = "#e74c3c"
        self.warning_color = "#f39c12"
        self.dark_color = "#2c3e50"
        self.light_color = "#ecf0f1"
        
        # Create main containers
        self.header_frame = ttk.Frame(root, style='TFrame')
        self.sidebar_frame = ttk.Frame(root, width=200, style='TFrame')
        self.content_frame = ttk.Frame(root, style='TFrame')
        
        # Layout
        self.header_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)
        self.content_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        # Header
        ttk.Label(self.header_frame, text="Smart Parking System - Admin Panel", style='Title.TLabel').pack(side="left")
        ttk.Label(self.header_frame, text=f"Logged in as Admin | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                 style='Header.TLabel').pack(side="right")
        
        # Sidebar buttons
        self.create_sidebar_buttons()
        
        # Default view
        self.show_dashboard()
    
    def create_sidebar_buttons(self):
        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🚗 Parked Vehicles", self.show_parked_vehicles),
            ("🅿 Slot Availability", self.show_slot_availability),
            ("📈 Analytics", self.show_analytics),
            ("⚙ Manual Control", self.show_manual_control),
            ("🔍 Search", self.show_search),
            ("📤 Export Data", self.export_data),
            ("🔄 Refresh", self.refresh_data),
            ("🚪 Logout", self.logout)
        ]
        
        for text, command in buttons:
            btn = tk.Button(self.sidebar_frame, text=text, command=command, 
                           bg=self.primary_color, fg="white", font=('Helvetica', 11),
                           bd=0, padx=10, pady=10, width=15, anchor="w")
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.dark_color))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.primary_color))
    
    def logout(self):
        if messagebox.askokcancel("Logout", "Are you sure you want to logout?"):
            self.db.close()
            self.root.destroy()
            # Restart login window
            root = tk.Tk()
            app = LoginWindow(root)
            root.mainloop()
    
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content_frame()
        
        # Dashboard title
        ttk.Label(self.content_frame, text="Dashboard Overview", style='Header.TLabel').pack(pady=10)
        
        # Create dashboard metrics frame
        metrics_frame = ttk.Frame(self.content_frame)
        metrics_frame.pack(fill="x", pady=10)
        
        # Get metrics data
        total_parked = self.get_total_parked_vehicles()
        total_exited = self.get_total_exited_vehicles()
        slots_available = self.get_available_slots()
        today_income = self.get_today_income()
        
        # Create metric cards
        self.create_metric_card(metrics_frame, "🚗 Parked Vehicles", total_parked, self.primary_color, 0)
        self.create_metric_card(metrics_frame, "🚪 Exited Vehicles", total_exited, self.secondary_color, 1)
        self.create_metric_card(metrics_frame, "🅿 Available Slots", slots_available, self.warning_color, 2)
        self.create_metric_card(metrics_frame, "💰 Today's Income", f"₹{today_income}", "#9b59b6", 3)
        
        # Parking slot visualization
        ttk.Label(self.content_frame, text="Parking Slot Visualization", style='Header.TLabel').pack(pady=(20, 5))
        
        # Create a scrollable canvas for the slot visualization
        canvas_container = ttk.Frame(self.content_frame)
        canvas_container.pack(fill="both", expand=True)
        
        # Add scrollbars
        canvas = tk.Canvas(canvas_container, bg='white')
        scroll_y = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scroll_x = ttk.Scrollbar(canvas_container, orient="horizontal", command=canvas.xview)
        
        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Layout scrollbars and canvas
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create frame inside canvas for the visualization
        viz_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=viz_frame, anchor="nw")
        
        try:
            # Get slot data
            self.cursor.execute("SELECT zone, slot, status FROM parking_slots ORDER BY zone, CAST(SUBSTRING(slot, 2) AS UNSIGNED)")
            slot_data = self.cursor.fetchall()
            
            if not slot_data:
                raise ValueError("No slot data found in database")
                
            # Create visualization with larger figure size
            fig, ax = plt.subplots(figsize=(18, 25))
            plt.subplots_adjust(left=0.2, right=0.95, top=0.95, bottom=0.05)
            
            # Define sections and their properties - all in 10x10 format
            sections = {
                'A': {'y_offset': 0, 'label': 'Section A (2-wheelers)', 'color': '#3498db', 
                    'rows': 10, 'slots_per_row': 10, 'slot_width': 1.0, 'row_height': 1.0},
                'B': {'y_offset': 12, 'label': 'Section B (2-wheelers)', 'color': '#2980b9', 
                    'rows': 10, 'slots_per_row': 10, 'slot_width': 1.0, 'row_height': 1.0},
                'C': {'y_offset': 24, 'label': 'Section C (2-wheelers)', 'color': '#2ecc71', 
                    'rows': 10, 'slots_per_row': 10, 'slot_width': 1.0, 'row_height': 1.0},
                'D': {'y_offset': 36, 'label': 'Section D (4-wheelers)', 'color': '#e67e22', 
                    'rows': 10, 'slots_per_row': 10, 'slot_width': 1.0, 'row_height': 1.0},
                'E': {'y_offset': 48, 'label': 'Section E (4-wheelers)', 'color': '#9b59b6', 
                    'rows': 10, 'slots_per_row': 10, 'slot_width': 1.0, 'row_height': 1.0}
            }
            
            # Draw section labels and background
            for section, params in sections.items():
                # Section background
                ax.add_patch(Rectangle(
                    (-2, params['y_offset'] - 1), 
                    params['slots_per_row'] * params['slot_width'] + 2, 
                    params['rows'] * params['row_height'] + 1,
                    facecolor=params['color'], alpha=0.1, edgecolor='none'
                ))
                
                # Section label
                ax.text(-1.5, params['y_offset'] + (params['rows'] * params['row_height'])/2 - 0.5, 
                    params['label'], ha='left', va='center', fontsize=12, weight='bold')
            
            # Draw all slots in a consistent 10x10 grid
            for zone, slot, status in slot_data:
                if zone in sections:
                    params = sections[zone]
                    slot_num = int(slot[1:])  # Get the number part (11 from A11)
                    row = (slot_num - 1) // params['slots_per_row']  # Calculate row (0-9)
                    col = (slot_num - 1) % params['slots_per_row']   # Position in row (0-9)
                    
                    x = col * params['slot_width']
                    y = params['y_offset'] + row * params['row_height']
                    
                    # Set color based on status
                    color = '#e74c3c' if status == 'occupied' else '#2ecc71'
                    
                    # Draw the slot rectangle (slightly smaller than cell size)
                    rect = Rectangle(
                        (x, y), params['slot_width']*0.9, params['row_height']*0.8,
                        facecolor=color, edgecolor='black', alpha=0.7, lw=0.5
                    )
                    ax.add_patch(rect)
                    
                    # Add slot number label (only show for first column and every 5th slot)
                    if col == 0 or (col+1) % 5 == 0:
                        ax.text(x + (params['slot_width']*0.9)/2, y + (params['row_height']*0.8)/2, 
                            slot, ha='center', va='center', fontsize=8, color='white')
            
            # Set axis limits and remove ticks
            max_x = max([params['slots_per_row'] * params['slot_width'] for params in sections.values()])
            max_y = max([params['y_offset'] + params['rows'] * params['row_height'] for params in sections.values()])
            
            ax.set_xlim(-2, max_x + 1)
            ax.set_ylim(-1, max_y + 1)
            ax.axis('off')
            ax.set_title('Parking Slot Status (Red = Occupied, Green = Available)', fontsize=14, pad=20)
            
            # Add legend
            occupied_patch = Rectangle((0, 0), 1, 1, fc='#e74c3c')
            available_patch = Rectangle((0, 0), 1, 1, fc='#2ecc71')
            ax.legend([occupied_patch, available_patch], ['Occupied', 'Available'], 
                    loc='upper right', bbox_to_anchor=(1, 1))
            
            # Embed in Tkinter
            canvas_fig = FigureCanvasTkAgg(fig, master=viz_frame)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            error_label = ttk.Label(viz_frame, text=f"Error loading parking slots: {str(e)}", foreground="red")
            error_label.pack()
            print(f"Error in parking slot visualization: {e}")
    
    def create_metric_card(self, parent, title, value, color, column):
        card = tk.Frame(parent, bg=color, bd=0, highlightthickness=0, relief="ridge")
        card.grid(row=0, column=column, padx=5, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        tk.Label(card, text=title, bg=color, fg="white", font=('Helvetica', 12, 'bold')).pack(pady=(10, 0))
        tk.Label(card, text=value, bg=color, fg="white", font=('Helvetica', 24, 'bold')).pack(pady=(5, 10))
        
        # Hover effects
        card.bind("<Enter>", lambda e, c=card: c.config(highlightbackground="black", highlightthickness=1))
        card.bind("<Leave>", lambda e, c=card: c.config(highlightthickness=0))
    
    def get_total_parked_vehicles(self):
        self.cursor.execute("SELECT COUNT(*) FROM parking_users WHERE status='occupied'")
        return self.cursor.fetchone()[0]
    
    def get_total_exited_vehicles(self):
        self.cursor.execute("SELECT COUNT(*) FROM parking_users WHERE status='free' AND exit_time IS NOT NULL")
        return self.cursor.fetchone()[0]
    
    def get_available_slots(self):
        self.cursor.execute("SELECT COUNT(*) FROM parking_slots WHERE status='free'")
        available = self.cursor.fetchone()[0]
        return f"{available}/500"
    
    def get_today_income(self):
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT SUM(total_charge) FROM parking_users WHERE DATE(exit_time)=%s AND paid='yes'", (today,))
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def load_recent_activity(self):
        self.recent_table.delete(*self.recent_table.get_children())
        self.cursor.execute("""
            SELECT user_id, name, vehicle_no, vehicle_type, entry_time, slot_allocated, paid 
            FROM parking_users 
            WHERE status='occupied' 
            ORDER BY entry_time DESC 
            LIMIT 10
        """)
        
        for row in self.cursor.fetchall():
            self.recent_table.insert("", "end", values=row)
    
    def show_parked_vehicles(self):
        self.clear_content_frame()
        
        # Title and filter frame
        ttk.Label(self.content_frame, text="Currently Parked Vehicles", style='Header.TLabel').pack(pady=10)
        
        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.pack(fill="x", pady=5)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side="left", padx=5)
        
        self.filter_var = tk.StringVar()
        filter_options = ["All", "2-wheeler", "4-wheeler"]
        filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=filter_options, state="readonly")
        filter_dropdown.pack(side="left", padx=5)
        filter_dropdown.set("All")
        filter_dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_parked_vehicles())
        
        # Treeview for parked vehicles
        columns = ("User ID", "Name", "Vehicle No", "Vehicle Type", "Entry Time", "Slot", "Preferred Exit", "Paid Status")
        self.parked_table = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.parked_table.heading(col, text=col)
            self.parked_table.column(col, width=120, anchor="center")
        
        self.parked_table.pack(fill="both", expand=True)
        
        # Control buttons frame
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill="x", pady=10)
        
        # Force exit button
        exit_btn = tk.Button(button_frame, text="Force Exit Selected Vehicle", command=self.force_exit_vehicle,
                        bg=self.danger_color, fg="white", font=('Helvetica', 11))
        exit_btn.pack(side="left", padx=5)
        
        # Mark as paid button
        paid_btn = tk.Button(button_frame, text="Mark as Paid", command=self.mark_as_paid,
                        bg=self.secondary_color, fg="white", font=('Helvetica', 11))
        paid_btn.pack(side="left", padx=5)
        
        # Load data
        self.load_parked_vehicles()

    def load_parked_vehicles(self):
        # Clear existing data
        for item in self.parked_table.get_children():
            self.parked_table.delete(item)
        
        # Get filter value and map to database value
        filter_value = self.filter_var.get()
        # Map display values to database values
        vehicle_type_map = {
            "All": "All",  # Keep "All" as is
            "2-wheeler": "two_wheeler",  # Map to database value
            "4-wheeler": "four_wheeler"  # Map to database value
        }
        
        # Construct query based on filter
        if filter_value == "All":
            query = """
                SELECT user_id, name, vehicle_no, vehicle_type, entry_time, slot_allocated, 
                    preferred_exit_time, paid 
                FROM parking_users 
                WHERE status='occupied'
                ORDER BY entry_time DESC
            """
            self.cursor.execute(query)
        else:
            # Use mapped database value
            db_vehicle_type = vehicle_type_map[filter_value]
            query = """
                SELECT user_id, name, vehicle_no, vehicle_type, entry_time, slot_allocated, 
                    preferred_exit_time, paid 
                FROM parking_users 
                WHERE status='occupied' AND vehicle_type=%s
                ORDER BY entry_time DESC
            """
            self.cursor.execute(query, (db_vehicle_type,))
        
        # Display data in table
        results = self.cursor.fetchall()
        
        # Map database values back to display values for showing in the table
        display_vehicle_type_map = {
            "two_wheeler": "2-wheeler",
            "four_wheeler": "4-wheeler"
        }
        
        for record in results:
            # Convert vehicle_type from database value to display value
            record_list = list(record)
            record_list[3] = display_vehicle_type_map.get(record[3], record[3])
            self.parked_table.insert("", "end", values=record_list)

    def force_exit_vehicle(self):
        selected_item = self.parked_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a vehicle to force exit")
            return
        
        item_data = self.parked_table.item(selected_item[0])['values']
        user_id = item_data[0]
        slot = item_data[5]
        
        # Calculate charge (simplified - you might want to implement proper calculation)
        entry_time = item_data[4]
        exit_time = datetime.now()
        hours_parked = (exit_time - entry_time).total_seconds() / 3600
        charge = round(hours_parked * 20, 2)  # ₹20 per hour
        
        # Update database
        try:
            # Update parking_users table
            self.cursor.execute("""
                UPDATE parking_users 
                SET exit_time=%s, total_charge=%s, status='free' 
                WHERE user_id=%s
            """, (exit_time, charge, user_id))
            
            # Update parking_slots table
            self.cursor.execute("""
                UPDATE parking_slots 
                SET status='free' 
                WHERE slot=%s
            """, (slot,))
            
            self.db.commit()
            
            messagebox.showinfo("Success", f"Vehicle {user_id} has been exited. Charge: ₹{charge}")
            self.load_parked_vehicles()
            self.refresh_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating database: {err}")
            self.db.rollback()
    
    def mark_as_paid(self):
        selected_item = self.parked_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a vehicle to mark as paid")
            return
        
        item_data = self.parked_table.item(selected_item[0])['values']
        user_id = item_data[0]
        
        # Update database
        self.cursor.execute("""
            UPDATE parking_users 
            SET paid='yes' 
            WHERE user_id=%s
        """, (user_id,))
        self.db.commit()
        
        messagebox.showinfo("Success", f"Payment status updated for vehicle {user_id}")
        self.load_parked_vehicles()

    def show_slot_availability(self):
        self.clear_content_frame()
        
        ttk.Label(self.content_frame, text="Parking Slot Availability", style='Header.TLabel').pack(pady=10)
        
        # Create a canvas for the slot visualization
        canvas_frame = ttk.Frame(self.content_frame)
        canvas_frame.pack(fill="both", expand=True)
        
        # Get slot data
        self.cursor.execute("""
            SELECT vehicle_type, COUNT(*) 
            FROM parking_users 
            WHERE status='occupied' 
            GROUP BY vehicle_type
        """)
        parked_counts = dict(self.cursor.fetchall())
        
        # Data for visualization
        labels = ['two_wheeler', 'four_wheeler']
        parked = [parked_counts.get(label, 0) for label in labels]
        available = [200 - parked[0], 300 - parked[1]]  # 200 slots for 2-wheelers, 300 for 4-wheelers
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot with adjusted spacing
        x = range(len(labels))
        width = 0.6  # Increased width from 0.35 to 0.6
        
        p1 = ax.bar(x, available, width, label='Available', color='lightgreen')
        p2 = ax.bar(x, parked, width, bottom=available, label='Occupied', color='lightblue')
        
        # Add data labels on bars
        for i, v in enumerate(available):
            ax.text(i, v/2, str(v), ha='center', va='center')
        
        for i, v in enumerate(parked):
            ax.text(i, available[i] + v/2, str(v), ha='center', va='center')
        
        # Display labels
        display_labels = ['2-wheeler', '4-wheeler']
        
        ax.set_ylabel('Number of Slots')
        ax.set_title('Current Slot Availability by Vehicle Type')
        ax.set_xticks(x)
        ax.set_xticklabels(display_labels)
        ax.legend()
        
        # Make bars closer together
        plt.tight_layout()
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add detailed table
        ttk.Label(self.content_frame, text="Detailed Slot Status", style='Header.TLabel').pack(pady=10)
        
        detail_frame = ttk.Frame(self.content_frame)
        detail_frame.pack(fill="x", pady=5)
        
        for i, label in enumerate(display_labels):
            ttk.Label(detail_frame, text=f"{label}: {available[i]} available, {parked[i]} occupied",
                    font=('Helvetica', 11)).grid(row=0, column=i, padx=20)
   
    def show_analytics(self):
        self.clear_content_frame()
        
        ttk.Label(self.content_frame, text="Parking Analytics", style='Header.TLabel').pack(pady=10)
        
        # Create notebook for multiple analytics tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill="both", expand=True)
        
        # Tab 1: Daily Vehicle Count
        daily_frame = ttk.Frame(notebook)
        notebook.add(daily_frame, text="Daily Vehicle Count")
        
        # Get daily data for last 7 days
        self.cursor.execute("""
            SELECT DATE(entry_time) as day, COUNT(*) as count 
            FROM parking_users 
            WHERE entry_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) 
            GROUP BY day 
            ORDER BY day
        """)
        daily_data = self.cursor.fetchall()
        
        days = [str(row[0]) for row in daily_data]
        counts = [row[1] for row in daily_data]
        
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(days, counts, marker='o', color=self.primary_color)
        ax1.set_title("Vehicles Parked Per Day (Last 7 Days)")
        ax1.set_ylabel("Number of Vehicles")
        ax1.grid(True)
        
        canvas1 = FigureCanvasTkAgg(fig1, master=daily_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)
        
        # Tab 2: Peak Hours
        peak_frame = ttk.Frame(notebook)
        notebook.add(peak_frame, text="Peak Hours")
        
        self.cursor.execute("""
            SELECT HOUR(entry_time) as hour, COUNT(*) as count 
            FROM parking_users 
            GROUP BY hour 
            ORDER BY hour
        """)
        peak_data = self.cursor.fetchall()
        
        hours = [f"{row[0]}:00" for row in peak_data]
        hour_counts = [row[1] for row in peak_data]
        
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.bar(hours, hour_counts, color=self.primary_color)
        ax2.set_title("Parking Usage by Hour of Day")
        ax2.set_ylabel("Number of Vehicles")
        ax2.grid(True)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=peak_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)
        
        # Tab 3: Income Analysis
        income_frame = ttk.Frame(notebook)
        notebook.add(income_frame, text="Income Analysis")
        
        self.cursor.execute("""
            SELECT DATE(exit_time) as day, SUM(total_charge) as income 
            FROM parking_users 
            WHERE exit_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND status='free' AND paid='yes'
            GROUP BY day 
            ORDER BY day
        """)
        income_data = self.cursor.fetchall()
        
        income_days = [str(row[0]) for row in income_data]
        income_amounts = [row[1] if row[1] else 0 for row in income_data]
        
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        ax3.bar(income_days, income_amounts, color=self.secondary_color)
        ax3.set_title("Daily Income (Last 7 Days)")
        ax3.set_ylabel("Amount (₹)")
        ax3.grid(True)
        
        canvas3 = FigureCanvasTkAgg(fig3, master=income_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True)
    
    def show_manual_control(self):
        self.clear_content_frame()
        
        ttk.Label(self.content_frame, text="Manual Slot Control", style='Header.TLabel').pack(pady=10)
        
        # Control frame
        control_frame = ttk.Frame(self.content_frame)
        control_frame.pack(fill="x", pady=10)
        
        ttk.Label(control_frame, text="Slot Number:").grid(row=0, column=0, padx=5, sticky="e")
        self.slot_entry = ttk.Entry(control_frame, width=15)
        self.slot_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(control_frame, text="Action:").grid(row=1, column=0, padx=5, sticky="e")
        self.action_var = tk.StringVar(value="free")
        ttk.Radiobutton(control_frame, text="Free Slot", variable=self.action_var, value="free").grid(row=1, column=1, padx=5, sticky="w")
        ttk.Radiobutton(control_frame, text="Block Slot", variable=self.action_var, value="block").grid(row=1, column=2, padx=5, sticky="w")
        
        action_btn = tk.Button(control_frame, text="Execute Action", command=self.execute_slot_action,
                             bg=self.primary_color, fg="white", font=('Helvetica', 11))
        action_btn.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Status frame
        status_frame = ttk.Frame(self.content_frame)
        status_frame.pack(fill="both", expand=True)
        
        ttk.Label(status_frame, text="Current Slot Status", style='Header.TLabel').pack(pady=10)
        
        columns = ("Slot", "Zone", "Status", "Vehicle No", "User ID", "Entry Time", "Paid Status")
        self.slot_table = ttk.Treeview(status_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.slot_table.heading(col, text=col)
            self.slot_table.column(col, width=100, anchor="center")
        
        self.slot_table.pack(fill="both", expand=True)
        
        # Load slot data
        self.load_slot_status()
    
    def load_slot_status(self):
        self.slot_table.delete(*self.slot_table.get_children())
        
        # Get all slots with their status
        self.cursor.execute("""
            SELECT s.slot, s.zone, s.status, u.vehicle_no, u.user_id, u.entry_time, u.paid 
            FROM parking_slots s
            LEFT JOIN parking_users u ON s.slot = u.slot_allocated AND u.status='occupied'
            ORDER BY s.zone, s.slot
        """)
        
        for row in self.cursor.fetchall():
            formatted_row = list(row)
            # Format datetime objects if needed
            for i, val in enumerate(formatted_row):
                if isinstance(val, datetime):
                    formatted_row[i] = val.strftime('%Y-%m-%d %H:%M')
                elif val is None:
                    formatted_row[i] = "N/A"
            self.slot_table.insert("", "end", values=formatted_row)
    
    def execute_slot_action(self):
        slot = self.slot_entry.get().strip()
        action = self.action_var.get()
        
        if not slot:
            messagebox.showwarning("Warning", "Please enter a slot number")
            return
        
        if action == "free":
            # Check if slot is occupied
            self.cursor.execute("SELECT user_id FROM parking_users WHERE slot_allocated=%s AND status='occupied'", (slot,))
            result = self.cursor.fetchone()
            
            if result:
                user_id = result[0]
                # Calculate charge (simplified)
                self.cursor.execute("SELECT entry_time FROM parking_users WHERE user_id=%s", (user_id,))
                entry_time = self.cursor.fetchone()[0]
                exit_time = datetime.now()
                hours_parked = (exit_time - entry_time).total_seconds() / 3600
                charge = round(hours_parked * 20, 2)
                
                # Update database
                try:
                    # Update parking_users table
                    self.cursor.execute("""
                        UPDATE parking_users 
                        SET exit_time=%s, total_charge=%s, status='free' 
                        WHERE user_id=%s
                    """, (exit_time, charge, user_id))
                    
                    # Update parking_slots table
                    self.cursor.execute("""
                        UPDATE parking_slots 
                        SET status='free' 
                        WHERE slot=%s
                    """, (slot,))
                    
                    self.db.commit()
                    
                    messagebox.showinfo("Success", f"Slot {slot} freed. User {user_id} charged ₹{charge}")
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error updating database: {err}")
                    self.db.rollback()
            else:
                messagebox.showinfo("Info", f"Slot {slot} is already free")
        
        elif action == "block":
            # Check if slot is occupied
            self.cursor.execute("SELECT user_id FROM parking_users WHERE slot_allocated=%s AND status='occupied'", (slot,))
            result = self.cursor.fetchone()
            
            if result:
                messagebox.showwarning("Warning", f"Slot {slot} is currently occupied. Free it first.")
            else:
                # Update parking_slots table to mark as occupied (blocked)
                try:
                    self.cursor.execute("""
                        UPDATE parking_slots 
                        SET status='occupied' 
                        WHERE slot=%s
                    """, (slot,))
                    self.db.commit()
                    messagebox.showinfo("Success", f"Slot {slot} has been blocked")
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error updating database: {err}")
                    self.db.rollback()
        
        self.load_slot_status()
        self.refresh_data()
    
    def show_search(self):
        self.clear_content_frame()
        
        ttk.Label(self.content_frame, text="Search Parking Records", style='Header.TLabel').pack(pady=10)
        
        # Search frame
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(fill="x", pady=10)
        
        ttk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=5)
        
        self.search_by_var = tk.StringVar(value="vehicle_no")
        search_options = [("Vehicle Number", "vehicle_no"), 
                         ("User ID", "user_id"), 
                         ("Slot Number", "slot_allocated")]
        
        for i, (text, value) in enumerate(search_options):
            ttk.Radiobutton(search_frame, text=text, variable=self.search_by_var, value=value).grid(row=0, column=i+1, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        
        search_btn = tk.Button(search_frame, text="Search", command=self.perform_search,
                             bg=self.primary_color, fg="white", font=('Helvetica', 11))
        search_btn.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")
        
        # Results frame
        results_frame = ttk.Frame(self.content_frame)
        results_frame.pack(fill="both", expand=True)
        
        columns = ("User ID", "Name", "Vehicle No", "Type", "Entry Time", "Exit Time", "Slot", "Status", "Charge", "Paid")
        self.search_table = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.search_table.heading(col, text=col)
            self.search_table.column(col, width=100, anchor="center")
        
        self.search_table.pack(fill="both", expand=True)

    def perform_search(self):
        search_by = self.search_by_var.get()
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
        
        self.search_table.delete(*self.search_table.get_children())
        
        query = f"""
            SELECT user_id, name, vehicle_no, vehicle_type, entry_time, exit_time, 
                   slot_allocated, status, total_charge, paid 
            FROM parking_users 
            WHERE {search_by} LIKE %s 
            ORDER BY entry_time DESC
        """
        
        self.cursor.execute(query, (f"%{search_term}%",))
        
        for row in self.cursor.fetchall():
            formatted_row = list(row)
            # Format datetime objects if needed
            for i, val in enumerate(formatted_row):
                if isinstance(val, datetime):
                    formatted_row[i] = val.strftime('%Y-%m-%d %H:%M')
                elif val is None:
                    formatted_row[i] = "N/A"
            self.search_table.insert("", "end", values=formatted_row)
    
    def export_data(self):
        # Ask for date range
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Data")
        export_window.geometry("400x300")
        
        ttk.Label(export_window, text="Export Parking Data", style='Header.TLabel').pack(pady=10)
        
        ttk.Label(export_window, text="From Date (YYYY-MM-DD):").pack(pady=5)
        from_entry = ttk.Entry(export_window)
        from_entry.pack(pady=5)
        
        ttk.Label(export_window, text="To Date (YYYY-MM-DD):").pack(pady=5)
        to_entry = ttk.Entry(export_window)
        to_entry.pack(pady=5)
        
        ttk.Label(export_window, text="File Format:").pack(pady=5)
        format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(export_window, text="CSV", variable=format_var, value="csv").pack()
        
        def execute_export():
            from_date = from_entry.get().strip()
            to_date = to_entry.get().strip()
            file_format = format_var.get()
            
            if not from_date or not to_date:
                messagebox.showwarning("Warning", "Please enter both date ranges")
                return
            
            try:
                # Validate dates
                datetime.strptime(from_date, '%Y-%m-%d')
                datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            # Get data
            self.cursor.execute("""
                SELECT user_id, name, vehicle_no, vehicle_type, entry_time, exit_time, 
                       slot_allocated, status, total_charge, paid 
                FROM parking_users 
                WHERE DATE(entry_time) BETWEEN %s AND %s 
                ORDER BY entry_time
            """, (from_date, to_date))
            
            data = self.cursor.fetchall()
            
            if not data:
                messagebox.showinfo("Info", "No data found for the selected date range")
                return
            
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=f".{file_format}",
                filetypes=[("CSV Files", "*.csv")],
                title="Save Export File"
            )
            
            if not file_path:
                return  # User canceled
            
            # Write to file
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow([
                    "User ID", "Name", "Vehicle Number", "Vehicle Type", 
                    "Entry Time", "Exit Time", "Slot", "Status", "Total Charge", "Paid Status"
                ])
                # Write data
                for row in data:
                    writer.writerow(row)
            
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
            export_window.destroy()
        
        export_btn = tk.Button(export_window, text="Export", command=execute_export,
                              bg=self.secondary_color, fg="white", font=('Helvetica', 11))
        export_btn.pack(pady=20)
    
    def refresh_data(self):
        current_tab = self.get_current_tab()
        if current_tab == "dashboard":
            self.show_dashboard()
        elif current_tab == "parked":
            self.show_parked_vehicles()
        elif current_tab == "slots":
            self.show_slot_availability()
        elif current_tab == "analytics":
            self.show_analytics()
        elif current_tab == "manual":
            self.show_manual_control()
        elif current_tab == "search":
            self.perform_search()
    
    def get_current_tab(self):
        # This is a simplified way to track the current view
        # In a more complex app, you might want to implement proper tab tracking
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Notebook):
                return "analytics"
            elif hasattr(self, 'recent_table') and child == self.recent_table:
                return "dashboard"
            elif hasattr(self, 'parked_table') and child == self.parked_table:
                return "parked"
            elif hasattr(self, 'slot_table') and child == self.slot_table:
                return "manual"
            elif hasattr(self, 'search_table') and child == self.search_table:
                return "search"
        
        # Check for slot availability view (has matplotlib canvas)
        for child in self.content_frame.winfo_children():
            if isinstance(child, FigureCanvasTkAgg):
                return "slots"
        
        return "dashboard"
    
    def exit_system(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the admin panel?"):
            self.db.close()
            self.root.destroy()

if __name__ == "__main__":
    # Start with login window
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()