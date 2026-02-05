import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from skimage import io, measure, filters, morphology, segmentation
from skimage.color import rgb2gray
from skimage.feature import graycomatrix, graycoprops
from scipy.stats import skew, kurtosis
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import hashlib
from PIL import Image, ImageTk
from fpdf import FPDF
import tempfile
import datetime
import shutil
from tkinter.scrolledtext import ScrolledText
import json
import sys
import traceback
import numpy as np
from image_processing import ImageProcessor
from feature_extraction import FeatureExtractor
from ml_models import ModelTrainer, ModelEvaluator
from visualization import Visualizer
from report_generator import ReportGenerator
from utils import create_tooltip

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lung Analysis Suite - Login")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 500
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')
        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_frame = tk.Frame(self.root, bg="#1a237e")
        self.main_frame.pack(fill="both", expand=True)

        left_panel = tk.Frame(self.main_frame, bg="#283593", width=300)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        tk.Label(left_panel,
                 text="Welcome to\nLung Analysis\nSuite",
                 font=('Helvetica', 24, 'bold'),
                 bg="#283593",
                 fg="white",
                 justify="center").pack(pady=(100, 0))

        tk.Label(left_panel,
                 text="Advanced Medical Imaging Analysis",
                 font=('Helvetica', 12),
                 bg="#283593",
                 fg="#e8eaf6",
                 wraplength=250).pack(pady=(20, 0))

        right_panel = tk.Frame(self.main_frame, bg="white")
        right_panel.pack(side="right", fill="both", expand=True)

        login_container = tk.Frame(right_panel, bg="white", padx=50, pady=30)
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_container,
                 text="Login",
                 font=('Helvetica', 28, 'bold'),
                 bg="white",
                 fg="#1a237e").pack(pady=(0, 30))

        username_frame = tk.Frame(login_container, bg="white")
        username_frame.pack(fill="x", pady=10)

        tk.Label(username_frame,
                 text="Username",
                 font=('Helvetica', 12),
                 bg="white",
                 fg="#1a237e").pack(anchor="w")

        self.username = ttk.Entry(username_frame,
                                  font=('Helvetica', 12),
                                  width=35)
        self.username.pack(fill="x", pady=(5, 0))

        password_frame = tk.Frame(login_container, bg="white")
        password_frame.pack(fill="x", pady=10)

        tk.Label(password_frame,
                 text="Password",
                 font=('Helvetica', 12),
                 bg="white",
                 fg="#1a237e").pack(anchor="w")

        self.password = ttk.Entry(password_frame,
                                  font=('Helvetica', 12),
                                  width=35,
                                  show="•")
        self.password.pack(fill="x", pady=(5, 0))

        button_frame = tk.Frame(login_container, bg="white")
        button_frame.pack(pady=30)

        self.login_btn = tk.Button(button_frame,
                                   text="Login",
                                   command=self.login,
                                   font=('Helvetica', 12, 'bold'),
                                   bg="#4caf50",
                                   fg="white",
                                   width=15,
                                   height=2,
                                   cursor="hand2",
                                   relief="flat")
        self.login_btn.pack(side=tk.LEFT, padx=10)

        self.signup_btn = tk.Button(button_frame,
                                    text="Sign Up",
                                    command=self.show_signup,
                                    font=('Helvetica', 12),
                                    bg="#2196f3",
                                    fg="white",
                                    width=15,
                                    height=2,
                                    cursor="hand2",
                                    relief="flat")
        self.signup_btn.pack(side=tk.LEFT, padx=10)

        self.login_btn.bind("<Enter>", lambda e: e.widget.config(bg="#66bb6a"))
        self.login_btn.bind("<Leave>", lambda e: e.widget.config(bg="#4caf50"))
        self.signup_btn.bind("<Enter>", lambda e: e.widget.config(bg="#42a5f5"))
        self.signup_btn.bind("<Leave>", lambda e: e.widget.config(bg="#2196f3"))

        self.users_file = "users.json"
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.quit()
            self.root.destroy()

    def login(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        with open(self.users_file, 'r') as f:
            users = json.load(f)

        if username in users and users[username]["password"] == hashlib.sha256(password.encode()).hexdigest():
            self.root.quit()
            self.root.destroy()
            app = LungAnalysisSuite(username)
            app.root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_signup(self):
        self.root.withdraw()
        SignupWindow(self)

    def run(self):
        self.root.mainloop()


class SignupWindow:
    def __init__(self, login_window):
        self.login_window = login_window
        self.root = tk.Toplevel()
        self.root.title("Sign Up - Lung Analysis Suite")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 500
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')
        self.root.resizable(False, False)

        self.main_frame = tk.Frame(self.root, bg="#1a237e")
        self.main_frame.pack(fill="both", expand=True)

        left_panel = tk.Frame(self.main_frame, bg="#283593", width=300)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        tk.Label(left_panel,
                 text="Join Our\nMedical Imaging\nCommunity",
                 font=('Helvetica', 28, 'bold'),
                 bg="#283593",
                 fg="#FFFFFF",
                 justify="center").pack(pady=(80, 0))

        tk.Label(left_panel,
                 text="Advanced Lung Analysis Platform\nfor Medical Professionals",
                 font=('Helvetica', 12),
                 bg="#283593",
                 fg="#e8eaf6",
                 justify="center").pack(pady=(20, 0))

        right_panel = tk.Frame(self.main_frame, bg="white")
        right_panel.pack(side="right", fill="both", expand=True)

        signup_container = tk.Frame(right_panel, bg="white", padx=50, pady=30)
        signup_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(signup_container,
                 text="Create Account",
                 font=('Helvetica', 28, 'bold'),
                 bg="white",
                 fg="#1a237e").pack(pady=(0, 30))

        username_frame = tk.Frame(signup_container, bg="white")
        username_frame.pack(fill="x", pady=10)

        tk.Label(username_frame,
                 text="Username",
                 font=('Helvetica', 12),
                 bg="white",
                 fg="#1a237e").pack(anchor="w")

        self.username = ttk.Entry(username_frame,
                                  font=('Helvetica', 12),
                                  width=35)
        self.username.pack(fill="x", pady=(5, 0))

        password_frame = tk.Frame(signup_container, bg="white")
        password_frame.pack(fill="x", pady=10)

        tk.Label(password_frame,
                 text="Password",
                 font=('Helvetica', 12),
                 bg="white",
                 fg="#1a237e").pack(anchor="w")

        self.password = ttk.Entry(password_frame,
                                  font=('Helvetica', 12),
                                  width=35,
                                  show="•")
        self.password.pack(fill="x", pady=(5, 0))

        confirm_frame = tk.Frame(signup_container, bg="white")
        confirm_frame.pack(fill="x", pady=10)

        tk.Label(confirm_frame,
                 text="Confirm Password",
                 font=('Helvetica', 12),
                 bg="white",
                 fg="#1a237e").pack(anchor="w")

        self.confirm_password = ttk.Entry(confirm_frame,
                                          font=('Helvetica', 12),
                                          width=35,
                                          show="•")
        self.confirm_password.pack(fill="x", pady=(5, 0))

        button_frame = tk.Frame(signup_container, bg="white")
        button_frame.pack(pady=30)

        self.signup_btn = tk.Button(button_frame,
                                    text="Create Account",
                                    command=self.signup,
                                    font=('Helvetica', 12, 'bold'),
                                    bg="#4CAF50",
                                    fg="white",
                                    width=15,
                                    height=2,
                                    cursor="hand2",
                                    relief="flat")
        self.signup_btn.pack(side=tk.LEFT, padx=10)

        self.back_btn = tk.Button(button_frame,
                                  text="Back to Login",
                                  command=self.back_to_login,
                                  font=('Helvetica', 12),
                                  bg="#2196F3",
                                  fg="white",
                                  width=15,
                                  height=2,
                                  cursor="hand2",
                                  relief="flat")
        self.back_btn.pack(side=tk.LEFT, padx=10)

        self.signup_btn.bind("<Enter>", lambda e: e.widget.config(bg="#388E3C"))
        self.signup_btn.bind("<Leave>", lambda e: e.widget.config(bg="#4CAF50"))
        self.back_btn.bind("<Enter>", lambda e: e.widget.config(bg="#1976D2"))
        self.back_btn.bind("<Leave>", lambda e: e.widget.config(bg="#2196F3"))

        self.root.protocol("WM_DELETE_WINDOW", self.back_to_login)

    def signup(self):
        username = self.username.get()
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        with open(self.login_window.users_file, 'r') as f:
            users = json.load(f)

        if username in users:
            messagebox.showerror("Error", "Username already exists")
            return

        # Hash the password for security
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Add the new user
        users[username] = {
            "password": hashed_password,
            "created_at": str(datetime.datetime.now())
        }
        
        with open(self.login_window.users_file, 'w') as f:
            json.dump(users, f, indent=4)
            
        messagebox.showinfo("Success", "Account created successfully! You can now log in.")
        self.back_to_login()

    def back_to_login(self):
        self.root.destroy()
        self.login_window.root.deiconify()


class LungAnalysisSuite:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"Lung Analysis Suite - Welcome {username}")
        
        # Set window size and position
        self.root.state('zoomed')  # Maximize window
        
        # Initialize data structures
        self.current_image = None
        self.current_image_path = None
        self.processed_image = None
        self.segmented_image = None
        self.feature_data = None
        self.classification_results = None
        self.session_history = []
        
        # Create the main GUI
        self.create_gui()
        
        # Initialize modules
        self.image_processor = ImageProcessor()
        self.feature_extractor = FeatureExtractor()
        self.model_trainer = ModelTrainer()
        self.model_evaluator = ModelEvaluator()
        self.visualizer = Visualizer()
        self.report_generator = ReportGenerator(username)
        
        # Load pretrained models if available
        self.load_models()
        
    def create_gui(self):
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create top menubar
        self.create_menubar()
        
        # Create left panel for navigation
        self.create_left_panel()
        
        # Create right panel for content
        self.create_right_panel()
        
        # Start with home view
        self.show_home_view()
        
    def create_menubar(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Save Processed Image", command=self.save_processed_image)
        file_menu.add_separator()
        file_menu.add_command(label="Log Out", command=self.logout)
        file_menu.add_command(label="Exit", command=self.exit_application)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Process Image", command=self.process_current_image)
        analysis_menu.add_command(label="Extract Features", command=self.extract_features)
        analysis_menu.add_command(label="Classify", command=self.classify_image)
        analysis_menu.add_command(label="Generate Report", command=self.generate_report)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def create_left_panel(self):
        self.left_panel = tk.Frame(self.main_frame, width=200, bg="#e8eaf6", padx=10, pady=10)
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)
        
        # App title
        tk.Label(self.left_panel, 
                 text="Lung Analysis Suite", 
                 font=("Helvetica", 14, "bold"),
                 bg="#e8eaf6", 
                 fg="#283593").pack(pady=(0, 20))
        
        # Navigation buttons
        nav_buttons = [
            ("Home", self.show_home_view, "View the dashboard"),
            ("Image Processing", self.show_processing_view, "Process and segment images"),
            ("Feature Extraction", self.show_feature_view, "Extract features from images"),
            ("Classification", self.show_classification_view, "Classify using ML models"),
            ("Results", self.show_results_view, "View analysis results"),
            ("Reports", self.show_reports_view, "Generate and view reports")
        ]
        
        for text, command, tooltip in nav_buttons:
            btn = tk.Button(self.left_panel, 
                           text=text, 
                           command=command,
                           width=18, 
                           bg="#c5cae9", 
                           fg="#1a237e",
                           relief="flat",
                           pady=5)
            btn.pack(pady=5, fill="x")
            create_tooltip(btn, tooltip)
            
            # Hover effects
            btn.bind("<Enter>", lambda e: e.widget.config(bg="#9fa8da"))
            btn.bind("<Leave>", lambda e: e.widget.config(bg="#c5cae9"))
            
        # User info at bottom
        user_frame = tk.Frame(self.left_panel, bg="#e8eaf6")
        user_frame.pack(side="bottom", fill="x", pady=10)
        
        tk.Label(user_frame, 
                 text=f"Logged in as:", 
                 font=("Helvetica", 9),
                 bg="#e8eaf6").pack(anchor="w")
        
        tk.Label(user_frame, 
                 text=self.username, 
                 font=("Helvetica", 10, "bold"),
                 bg="#e8eaf6", 
                 fg="#283593").pack(anchor="w")
        
    def create_right_panel(self):
        self.right_panel = tk.Frame(self.main_frame, bg="white")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # This will hold different views
        self.content_frame = tk.Frame(self.right_panel, bg="white")
        self.content_frame.pack(fill="both", expand=True)
        
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_home_view(self):
        self.clear_content_frame()
        
        # Welcome header
        header_frame = tk.Frame(self.content_frame, bg="white", pady=20)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, 
                 text="Welcome to Lung Analysis Suite", 
                 font=("Helvetica", 22, "bold"),
                 bg="white", 
                 fg="#1a237e").pack()
        
        tk.Label(header_frame, 
                 text="Advanced Medical Imaging Analysis Platform", 
                 font=("Helvetica", 14),
                 bg="white", 
                 fg="#5c6bc0").pack(pady=5)
        
        # Main content
        content = tk.Frame(self.content_frame, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Quick actions
        actions_frame = tk.Frame(content, bg="white")
        actions_frame.pack(fill="x", pady=20)
        
        tk.Label(actions_frame, 
                 text="Quick Actions", 
                 font=("Helvetica", 16, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w")
        
        button_frame = tk.Frame(actions_frame, bg="white")
        button_frame.pack(fill="x", pady=10)
        
        quick_buttons = [
            ("Open Image", self.open_image, "#4caf50"),
            ("Process Image", self.process_current_image, "#2196f3"),
            ("Generate Report", self.generate_report, "#ff9800")
        ]
        
        for text, command, color in quick_buttons:
            btn = tk.Button(button_frame, 
                           text=text, 
                           command=command,
                           bg=color, 
                           fg="white",
                           font=("Helvetica", 12),
                           width=15,
                           height=2,
                           relief="flat")
            btn.pack(side="left", padx=10)
            
        # Recent activity
        recent_frame = tk.Frame(content, bg="white", pady=10)
        recent_frame.pack(fill="both", expand=True)
        
        tk.Label(recent_frame, 
                 text="Recent Activity", 
                 font=("Helvetica", 16, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w", pady=(0, 10))
        
        # Table headers
        headers_frame = tk.Frame(recent_frame, bg="#e8eaf6")
        headers_frame.pack(fill="x")
        
        headers = ["Timestamp", "Activity", "Image Name", "Result"]
        widths = [150, 200, 250, 200]
        
        for i, header in enumerate(headers):
            tk.Label(headers_frame, 
                    text=header, 
                    font=("Helvetica", 11, "bold"),
                    width=widths[i]//10,
                    bg="#e8eaf6", 
                    fg="#1a237e").pack(side="left", padx=2, pady=5)
            
        # Activity entries (most recent 5)
        activity_container = tk.Frame(recent_frame, bg="white")
        activity_container.pack(fill="both", expand=True)
        
        if self.session_history:
            # Show only the most recent 5 entries
            for i, activity in enumerate(self.session_history[-5:]):
                entry_frame = tk.Frame(activity_container, bg="white" if i % 2 == 0 else "#f5f5f5")
                entry_frame.pack(fill="x")
                
                tk.Label(entry_frame, 
                        text=activity.get("timestamp", ""), 
                        width=widths[0]//10,
                        anchor="w",
                        bg=entry_frame["bg"]).pack(side="left", padx=2, pady=5)
                
                tk.Label(entry_frame, 
                        text=activity.get("activity", ""), 
                        width=widths[1]//10,
                        anchor="w",
                        bg=entry_frame["bg"]).pack(side="left", padx=2, pady=5)
                
                tk.Label(entry_frame, 
                        text=activity.get("image_name", ""), 
                        width=widths[2]//10,
                        anchor="w",
                        bg=entry_frame["bg"]).pack(side="left", padx=2, pady=5)
                
                tk.Label(entry_frame, 
                        text=activity.get("result", ""), 
                        width=widths[3]//10,
                        anchor="w",
                        bg=entry_frame["bg"]).pack(side="left", padx=2, pady=5)
        else:
            # No activity yet
            tk.Label(activity_container, 
                    text="No recent activity", 
                    font=("Helvetica", 11),
                    bg="white",
                    fg="gray").pack(pady=20)
            
    def show_processing_view(self):
        self.clear_content_frame()
        
        # Header
        header_frame = tk.Frame(self.content_frame, bg="white", pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, 
                 text="Image Processing", 
                 font=("Helvetica", 18, "bold"),
                 bg="white", 
                 fg="#1a237e").pack()
        
        # Main content - split into two panels
        content = tk.Frame(self.content_frame, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Image display
        image_panel = tk.Frame(content, bg="white", width=500, height=500)
        image_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        image_panel.pack_propagate(False)
        
        image_header = tk.Frame(image_panel, bg="white")
        image_header.pack(fill="x")
        
        tk.Label(image_header, 
                 text="Original Image", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(side="left")
        
        open_btn = tk.Button(image_header, 
                            text="Open Image", 
                            command=self.open_image,
                            bg="#2196f3", 
                            fg="white",
                            relief="flat",
                            padx=10)
        open_btn.pack(side="right")
        
        # Canvas for the image
        self.image_canvas_frame = tk.Frame(image_panel, bg="#f5f5f5", bd=1, relief="solid")
        self.image_canvas_frame.pack(fill="both", expand=True, pady=10)
        
        # Display loaded image if any
        if self.current_image is not None:
            self.display_image(self.image_canvas_frame, self.current_image)
        else:
            placeholder = tk.Label(self.image_canvas_frame, 
                                  text="No image loaded. Use 'Open Image' button.",
                                  bg="#f5f5f5", 
                                  fg="gray")
            placeholder.pack(fill="both", expand=True)
        
        # Right side - Processing controls and preview
        processing_panel = tk.Frame(content, bg="white", width=500, height=500)
        processing_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        processing_panel.pack_propagate(False)
        
        processing_header = tk.Frame(processing_panel, bg="white")
        processing_header.pack(fill="x")
        
        tk.Label(processing_header, 
                 text="Processed Image", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(side="left")
        
        # Canvas for the processed image
        self.processed_canvas_frame = tk.Frame(processing_panel, bg="#f5f5f5", bd=1, relief="solid")
        self.processed_canvas_frame.pack(fill="both", expand=True, pady=10)
        
        # Display processed image if any
        if self.processed_image is not None:
            self.display_image(self.processed_canvas_frame, self.processed_image)
        else:
            placeholder = tk.Label(self.processed_canvas_frame, 
                                  text="No processed image. Use controls below.",
                                  bg="#f5f5f5", 
                                  fg="gray")
            placeholder.pack(fill="both", expand=True)
        
        # Processing controls
        controls_frame = tk.Frame(processing_panel, bg="white", pady=10)
        controls_frame.pack(fill="x")
        
        tk.Label(controls_frame, 
                 text="Processing Options:", 
                 font=("Helvetica", 12, "bold"),
                 bg="white").pack(anchor="w")
        
        options_frame = tk.Frame(controls_frame, bg="white", pady=5)
        options_frame.pack(fill="x")
        
        # Processing method selection
        methods_frame = tk.Frame(options_frame, bg="white")
        methods_frame.pack(side="left", fill="both", expand=True)
        
        self.processing_method = tk.StringVar()
        self.processing_method.set("standard")  # Default processing method
        
        methods = [
            ("Standard Segmentation", "standard"),
            ("Watershed Segmentation", "watershed"),
            ("Active Contour", "active_contour")
        ]
        
        for text, value in methods:
            tk.Radiobutton(methods_frame, 
                          text=text, 
                          variable=self.processing_method, 
                          value=value,
                          bg="white").pack(anchor="w")
        
        # Process button
        process_btn = tk.Button(controls_frame, 
                               text="Process Image", 
                               command=self.process_current_image,
                               bg="#4caf50", 
                               fg="white",
                               font=("Helvetica", 12),
                               width=15,
                               relief="flat")
        process_btn.pack(pady=10)
        
        # Action buttons frame
        action_buttons = tk.Frame(processing_panel, bg="white")
        action_buttons.pack(fill="x", pady=5)
        
        tk.Button(action_buttons, 
                 text="Save Processed Image", 
                 command=self.save_processed_image,
                 bg="#ff9800", 
                 fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        tk.Button(action_buttons, 
                 text="Continue to Feature Extraction", 
                 command=self.extract_and_show_features,
                 bg="#2196f3", 
                 fg="white",
                 relief="flat").pack(side="right", padx=5)
        
    def show_feature_view(self):
        self.clear_content_frame()
        
        # Header
        header_frame = tk.Frame(self.content_frame, bg="white", pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, 
                 text="Feature Extraction", 
                 font=("Helvetica", 18, "bold"),
                 bg="white", 
                 fg="#1a237e").pack()
        
        # Main content - split into two panels
        content = tk.Frame(self.content_frame, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Segmented image and controls
        image_panel = tk.Frame(content, bg="white", width=400)
        image_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        image_header = tk.Frame(image_panel, bg="white")
        image_header.pack(fill="x")
        
        tk.Label(image_header, 
                 text="Segmented Image", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(side="left")
        
        # Canvas for the segmented image
        self.segmented_canvas_frame = tk.Frame(image_panel, bg="#f5f5f5", bd=1, relief="solid", height=300)
        self.segmented_canvas_frame.pack(fill="both", expand=True, pady=10)
        
        # Display segmented image if any
        if self.segmented_image is not None:
            self.display_image(self.segmented_canvas_frame, self.segmented_image)
        else:
            placeholder = tk.Label(self.segmented_canvas_frame, 
                                  text="No segmented image. Process an image first.",
                                  bg="#f5f5f5", 
                                  fg="gray")
            placeholder.pack(fill="both", expand=True)
        
        # Controls for feature extraction
        controls_frame = tk.Frame(image_panel, bg="white", pady=10)
        controls_frame.pack(fill="x")
        
        tk.Label(controls_frame, 
                 text="Feature Types:", 
                 font=("Helvetica", 12, "bold"),
                 bg="white").pack(anchor="w")
        
        # Checkboxes for features
        features_frame = tk.Frame(controls_frame, bg="white", pady=5)
        features_frame.pack(fill="x")
        
        self.use_shape_features = tk.BooleanVar(value=True)
        self.use_texture_features = tk.BooleanVar(value=True)
        self.use_intensity_features = tk.BooleanVar(value=True)
        
        tk.Checkbutton(features_frame, 
                      text="Shape Features", 
                      variable=self.use_shape_features,
                      bg="white").pack(anchor="w")
        
        tk.Checkbutton(features_frame, 
                      text="Texture Features", 
                      variable=self.use_texture_features,
                      bg="white").pack(anchor="w")
        
        tk.Checkbutton(features_frame, 
                      text="Intensity Features", 
                      variable=self.use_intensity_features,
                      bg="white").pack(anchor="w")
        
        # Extract button
        extract_btn = tk.Button(controls_frame, 
                               text="Extract Features", 
                               command=self.extract_features,
                               bg="#4caf50", 
                               fg="white",
                               font=("Helvetica", 12),
                               width=15,
                               relief="flat")
        extract_btn.pack(pady=10)
        
        # Right side - Feature data display
        features_panel = tk.Frame(content, bg="white", width=500)
        features_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        features_header = tk.Frame(features_panel, bg="white")
        features_header.pack(fill="x")
        
        tk.Label(features_header, 
                 text="Extracted Features", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(side="left")
        
        # Feature table
        self.features_table_frame = tk.Frame(features_panel, bg="#f5f5f5", bd=1, relief="solid")
        self.features_table_frame.pack(fill="both", expand=True, pady=10)
        
        # Show features if available
        if self.feature_data is not None:
            self.display_features_table()
        else:
            placeholder = tk.Label(self.features_table_frame, 
                                  text="No features extracted. Use the 'Extract Features' button.",
                                  bg="#f5f5f5", 
                                  fg="gray")
            placeholder.pack(fill="both", expand=True)
        
        # Action buttons
        action_buttons = tk.Frame(features_panel, bg="white")
        action_buttons.pack(fill="x", pady=5)
        
        tk.Button(action_buttons, 
                 text="Visualize Features", 
                 command=self.visualize_features,
                 bg="#ff9800", 
                 fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        tk.Button(action_buttons, 
                 text="Continue to Classification", 
                 command=self.show_classification_view,
                 bg="#2196f3", 
                 fg="white",
                 relief="flat").pack(side="right", padx=5)
        
    def show_classification_view(self):
        self.clear_content_frame()
        
        # Header
        header_frame = tk.Frame(self.content_frame, bg="white", pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, 
                 text="Image Classification", 
                 font=("Helvetica", 18, "bold"),
                 bg="white", 
                 fg="#1a237e").pack()
        
        # Check if features are extracted
        if self.feature_data is None:
            # Show message to extract features first
            message_frame = tk.Frame(self.content_frame, bg="white", pady=50)
            message_frame.pack(fill="both", expand=True)
            
            tk.Label(message_frame, 
                    text="No features extracted yet!", 
                    font=("Helvetica", 14, "bold"),
                    bg="white", 
                    fg="#f44336").pack()
            
            tk.Label(message_frame, 
                    text="Please process an image and extract features before classification.", 
                    font=("Helvetica", 12),
                    bg="white").pack(pady=10)
            
            tk.Button(message_frame, 
                     text="Go to Feature Extraction", 
                     command=self.show_feature_view,
                     bg="#2196f3", 
                     fg="white",
                     font=("Helvetica", 12),
                     relief="flat").pack(pady=20)
            
            return
        
        # Main content
        content = tk.Frame(self.content_frame, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Model selection
        model_panel = tk.Frame(content, bg="white", width=400)
        model_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        model_header = tk.Frame(model_panel, bg="white")
        model_header.pack(fill="x")
        
        tk.Label(model_header, 
                 text="Classification Model", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w")
        
        # Model selection
        model_frame = tk.Frame(model_panel, bg="white", pady=20)
        model_frame.pack(fill="x")
        
        tk.Label(model_frame, 
                 text="Select Model:", 
                 font=("Helvetica", 12, "bold"),
                 bg="white").pack(anchor="w")
        
        self.classification_model = tk.StringVar()
        self.classification_model.set("svm")  # Default model
        
        models = [
            ("Support Vector Machine", "svm"),
            ("Random Forest", "random_forest"),
            ("Logistic Regression", "logistic_regression"),
            ("Neural Network", "neural_network")
        ]
        
        for text, value in models:
            tk.Radiobutton(model_frame, 
                          text=text, 
                          variable=self.classification_model, 
                          value=value,
                          bg="white").pack(anchor="w", pady=2)
        
        # Advanced parameters
        params_frame = tk.Frame(model_panel, bg="white", pady=10)
        params_frame.pack(fill="x")
        
        tk.Label(params_frame, 
                 text="Advanced Parameters:", 
                 font=("Helvetica", 12, "bold"),
                 bg="white").pack(anchor="w")
        
        # Classification button
        classify_btn = tk.Button(model_panel, 
                                text="Classify Image", 
                                command=self.classify_image,
                                bg="#4caf50", 
                                fg="white",
                                font=("Helvetica", 12),
                                width=15,
                                relief="flat")
        classify_btn.pack(pady=20)
        
        # Right side - Classification results
        results_panel = tk.Frame(content, bg="white", width=500)
        results_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        results_header = tk.Frame(results_panel, bg="white")
        results_header.pack(fill="x")
        
        tk.Label(results_header, 
                 text="Classification Results", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w")
        
        # Results container
        self.classification_results_frame = tk.Frame(results_panel, bg="#f5f5f5", bd=1, relief="solid")
        self.classification_results_frame.pack(fill="both", expand=True, pady=10)
        
        # Show results if available
        if self.classification_results is not None:
            self.display_classification_results()
        else:
            placeholder = tk.Label(self.classification_results_frame, 
                                  text="No classification results. Use the 'Classify Image' button.",
                                  bg="#f5f5f5", 
                                  fg="gray")
            placeholder.pack(fill="both", expand=True)
        
        # Action buttons
        action_buttons = tk.Frame(results_panel, bg="white")
        action_buttons.pack(fill="x", pady=5)
        
        tk.Button(action_buttons, 
                 text="Visualize Results", 
                 command=self.visualize_classification_results,
                 bg="#ff9800", 
                 fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        tk.Button(action_buttons, 
                 text="Generate Report", 
                 command=self.generate_report,
                 bg="#2196f3", 
                 fg="white",
                 relief="flat").pack(side="right", padx=5)
        
    def show_results_view(self):
        self.clear_content_frame()
        
        # Header
        header_frame = tk.Frame(self.content_frame, bg="white", pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, 
                 text="Analysis Results", 
                 font=("Helvetica", 18, "bold"),
                 bg="white", 
                 fg="#1a237e").pack()
        
        # Check if classification has been done
        if self.classification_results is None:
            # Show message to classify first
            message_frame = tk.Frame(self.content_frame, bg="white", pady=50)
            message_frame.pack(fill="both", expand=True)
            
            tk.Label(message_frame, 
                    text="No classification results yet!", 
                    font=("Helvetica", 14, "bold"),
                    bg="white", 
                    fg="#f44336").pack()
            
            tk.Label(message_frame, 
                    text="Please classify an image before viewing results.", 
                    font=("Helvetica", 12),
                    bg="white").pack(pady=10)
            
            tk.Button(message_frame, 
                     text="Go to Classification", 
                     command=self.show_classification_view,
                     bg="#2196f3", 
                     fg="white",
                     font=("Helvetica", 12),
                     relief="flat").pack(pady=20)
            
            return
        
        # Main content - tabs for different visualizations
        self.results_notebook = ttk.Notebook(self.content_frame)
        self.results_notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Summary tab
        summary_frame = tk.Frame(self.results_notebook, bg="white")
        self.results_notebook.add(summary_frame, text="Summary")
        
        # Create summary content
        self.create_summary_tab(summary_frame)
        
        # Visualization tab
        viz_frame = tk.Frame(self.results_notebook, bg="white")
        self.results_notebook.add(viz_frame, text="Visualizations")
        
        # Create visualization content
        self.create_visualization_tab(viz_frame)
        
        # Metrics tab
        metrics_frame = tk.Frame(self.results_notebook, bg="white")
        self.results_notebook.add(metrics_frame, text="Metrics")
        
        # Create metrics content
        self.create_metrics_tab(metrics_frame)
        
        # Bottom buttons
        buttons_frame = tk.Frame(self.content_frame, bg="white", pady=10)
        buttons_frame.pack(fill="x")
        
        tk.Button(buttons_frame, 
                 text="Generate Report", 
                 command=self.generate_report,
                 bg="#4caf50", 
                 fg="white",
                 font=("Helvetica", 12),
                 width=15,
                 relief="flat").pack(side="right", padx=10)
        
    def create_summary_tab(self, parent_frame):
        # Image and classification summary
        
        # Image info
        image_frame = tk.Frame(parent_frame, bg="white", pady=10)
        image_frame.pack(fill="x")
        
        tk.Label(image_frame, 
                 text="Image Information", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w")
        
        # Image details
        details_frame = tk.Frame(image_frame, bg="white", padx=20, pady=10)
        details_frame.pack(fill="x")
        
        # If image is loaded
        if self.current_image_path:
            image_name = os.path.basename(self.current_image_path)
            image_size = f"{self.current_image.width}x{self.current_image.height}"
            
            # Create two columns
            left_col = tk.Frame(details_frame, bg="white")
            left_col.pack(side="left", fill="both", expand=True)
            
            right_col = tk.Frame(details_frame, bg="white")
            right_col.pack(side="right", fill="both", expand=True)
            
            # Left column details
            tk.Label(left_col, 
                    text="Filename:", 
                    font=("Helvetica", 11, "bold"),
                    bg="white").pack(anchor="w", pady=2)
            
            tk.Label(left_col, 
                    text=image_name, 
                    bg="white").pack(anchor="w", padx=20, pady=2)
            
            tk.Label(left_col, 
                    text="Dimensions:", 
                    font=("Helvetica", 11, "bold"),
                    bg="white").pack(anchor="w", pady=2)
            
            tk.Label(left_col, 
                    text=image_size, 
                    bg="white").pack(anchor="w", padx=20, pady=2)
            
            # Right column with thumbnail
            if self.current_image:
                # Create a small thumbnail
                thumb = self.current_image.copy()
                thumb.thumbnail((100, 100))
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(thumb)
                
                # Keep a reference to avoid garbage collection
                self.thumb_image = photo
                
                # Display thumbnail
                tk.Label(right_col, 
                        image=photo, 
                        bg="white").pack(side="right", padx=10)
        
        # Classification results
        results_frame = tk.Frame(parent_frame, bg="white", pady=20)
        results_frame.pack(fill="x")
        
        tk.Label(results_frame, 
                 text="Classification Results", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w")
        
        # Results details
        results_details = tk.Frame(results_frame, bg="white", padx=20, pady=10)
        results_details.pack(fill="x")
        
        # Create two columns
        left_col = tk.Frame(results_details, bg="white")
        left_col.pack(side="left", fill="both", expand=True)
        
        right_col = tk.Frame(results_details, bg="white")
        right_col.pack(side="right", fill="both", expand=True)
        
        # Display classification results
        if self.classification_results:
            # Main classification
            tk.Label(left_col, 
                    text="Diagnosis:", 
                    font=("Helvetica", 11, "bold"),
                    bg="white").pack(anchor="w", pady=2)
            
            diagnosis = self.classification_results.get("diagnosis", "Unknown")
            tk.Label(left_col, 
                    text=diagnosis, 
                    font=("Helvetica", 13),
                    fg="#1a237e" if diagnosis == "Normal" else "#d32f2f",
                    bg="white").pack(anchor="w", padx=20, pady=2)
            
            # Confidence
            tk.Label(left_col, 
                    text="Confidence:", 
                    font=("Helvetica", 11, "bold"),
                    bg="white").pack(anchor="w", pady=2)
            
            confidence = self.classification_results.get("confidence", 0)
            tk.Label(left_col, 
                    text=f"{confidence:.1f}%", 
                    bg="white").pack(anchor="w", padx=20, pady=2)
            
            # Model used
            tk.Label(right_col, 
                    text="Model Used:", 
                    font=("Helvetica", 11, "bold"),
                    bg="white").pack(anchor="w", pady=2)
            
            model = self.classification_results.get("model", "Unknown")
            tk.Label(right_col, 
                    text=model, 
                    bg="white").pack(anchor="w", padx=20, pady=2)
            
            # Date of analysis
            tk.Label(right_col, 
                    text="Analysis Date:", 
                    font=("Helvetica", 11, "bold"),
                    bg="white").pack(anchor="w", pady=2)
            
            date = self.classification_results.get("date", "Unknown")
            tk.Label(right_col, 
                    text=date, 
                    bg="white").pack(anchor="w", padx=20, pady=2)
            
        # Features summary
        features_frame = tk.Frame(parent_frame, bg="white", pady=20)
        features_frame.pack(fill="x")
        
        tk.Label(features_frame, 
                 text="Key Features", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w")
        
        # Key features list
        if self.feature_data:
            features_list = tk.Frame(features_frame, bg="white", padx=20, pady=10)
            features_list.pack(fill="x")
            
            # Show most important features
            important_features = [
                ("Area", self.feature_data.get("area", "N/A")),
                ("Perimeter", self.feature_data.get("perimeter", "N/A")),
                ("Circularity", self.feature_data.get("circularity", "N/A")),
                ("Mean Intensity", self.feature_data.get("mean_intensity", "N/A")),
                ("Contrast", self.feature_data.get("contrast", "N/A"))
            ]
            
            for name, value in important_features:
                feature_entry = tk.Frame(features_list, bg="white", pady=2)
                feature_entry.pack(fill="x")
                
                tk.Label(feature_entry, 
                        text=f"{name}:", 
                        width=15,
                        anchor="w",
                        font=("Helvetica", 11, "bold"),
                        bg="white").pack(side="left")
                
                # Format the value to 4 decimal places if it's a float
                if isinstance(value, float):
                    formatted_value = f"{value:.4f}"
                else:
                    formatted_value = str(value)
                
                tk.Label(feature_entry, 
                        text=formatted_value, 
                        anchor="w",
                        bg="white").pack(side="left", padx=10)
        
    def create_visualization_tab(self, parent_frame):
        # Create a frame for the matplotlib figure
        plot_frame = tk.Frame(parent_frame, bg="white")
        plot_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs for different visualizations
        viz_notebook = ttk.Notebook(plot_frame)
        viz_notebook.pack(fill="both", expand=True)
        
        # Tab for original vs processed images
        images_frame = tk.Frame(viz_notebook, bg="white")
        viz_notebook.add(images_frame, text="Images")
        
        # Tab for feature distributions
        features_frame = tk.Frame(viz_notebook, bg="white")
        viz_notebook.add(features_frame, text="Features")
        
        # Tab for classification results
        class_frame = tk.Frame(viz_notebook, bg="white")
        viz_notebook.add(class_frame, text="Classification")
        
        # Create visualizations if we have data
        if self.current_image and self.processed_image:
            self.create_image_comparison(images_frame)
        
        if self.feature_data:
            self.create_feature_visualization(features_frame)
        
        if self.classification_results:
            self.create_classification_visualization(class_frame)
        
    def create_image_comparison(self, parent_frame):
        # Create figure with original and processed images side by side
        fig = plt.Figure(figsize=(10, 5), dpi=100)
        fig.subplots_adjust(wspace=0.3)
        
        # Original image
        ax1 = fig.add_subplot(121)
        ax1.set_title("Original Image")
        
        # Convert PIL image to array for matplotlib
        if self.current_image:
            img_array = np.array(self.current_image)
            ax1.imshow(img_array)
            ax1.axis('off')
        
        # Processed image
        ax2 = fig.add_subplot(122)
        ax2.set_title("Processed Image")
        
        if self.processed_image:
            proc_array = np.array(self.processed_image)
            ax2.imshow(proc_array)
            ax2.axis('off')
        
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar_frame = tk.Frame(parent_frame)
        toolbar_frame.pack(fill="x")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        
    def create_feature_visualization(self, parent_frame):
        if not self.feature_data:
            return
            
        # Create figure with feature visualizations
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        fig.subplots_adjust(hspace=0.4)
        
        # Prepare data for visualization
        # For this example, let's show some key features as a bar chart
        feature_names = ["Area", "Perimeter", "Eccentricity", "Circularity", "Mean Intensity"]
        feature_values = [
            self.feature_data.get("area", 0),
            self.feature_data.get("perimeter", 0),
            self.feature_data.get("eccentricity", 0),
            self.feature_data.get("circularity", 0),
            self.feature_data.get("mean_intensity", 0)
        ]
        
        # Normalize values for better visualization
        if max(feature_values) > 0:
            feature_values = [v / max(feature_values) for v in feature_values]
        
        # Bar chart of normalized features
        ax1 = fig.add_subplot(211)
        ax1.set_title("Key Feature Values (Normalized)")
        bars = ax1.bar(feature_names, feature_values, color="#3f51b5")
        ax1.set_ylim(0, 1.1)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # Texture features as a heatmap (if available)
        if "texture_matrix" in self.feature_data:
            ax2 = fig.add_subplot(212)
            ax2.set_title("Texture Features (GLCM)")
            
            # Get the texture matrix or create a sample one
            texture_matrix = self.feature_data["texture_matrix"]
            im = ax2.imshow(texture_matrix, cmap='viridis')
            fig.colorbar(im, ax=ax2)
            
            # Add labels
            ax2.set_xlabel("Pixel Value j")
            ax2.set_ylabel("Pixel Value i")
        else:
            # If no texture matrix, create a pie chart of feature types
            ax2 = fig.add_subplot(212)
            ax2.set_title("Feature Distribution by Type")
            
            # Count features by type
            shape_count = sum(1 for k in self.feature_data if k.startswith("shape_"))
            texture_count = sum(1 for k in self.feature_data if k.startswith("texture_"))
            intensity_count = sum(1 for k in self.feature_data if k.startswith("intensity_"))
            
            if shape_count + texture_count + intensity_count > 0:
                labels = ['Shape', 'Texture', 'Intensity']
                sizes = [shape_count, texture_count, intensity_count]
                colors = ['#3f51b5', '#4caf50', '#ff9800']
                
                ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                       shadow=True, startangle=90)
                ax2.axis('equal')
            
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar_frame = tk.Frame(parent_frame)
        toolbar_frame.pack(fill="x")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        
    def create_classification_visualization(self, parent_frame):
        if not self.classification_results:
            return
            
        # Create figure with classification visualizations
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        fig.subplots_adjust(hspace=0.4)
        
        # Probability distribution
        ax1 = fig.add_subplot(211)
        ax1.set_title("Classification Probability Distribution")
        
        # Get class probabilities or use default values
        class_names = self.classification_results.get("class_names", ["Normal", "Abnormal"])
        probs = self.classification_results.get("probabilities", [0.5, 0.5])
        
        bars = ax1.bar(class_names, probs, color=["#4caf50", "#f44336"])
        ax1.set_ylim(0, 1.1)
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{height:.1%}', ha='center', va='bottom')
        
        # ROC curve if available, otherwise confusion matrix
        if "roc_curve" in self.classification_results:
            ax2 = fig.add_subplot(212)
            ax2.set_title("ROC Curve")
            
            fpr = self.classification_results["roc_curve"]["fpr"]
            tpr = self.classification_results["roc_curve"]["tpr"]
            auc = self.classification_results["roc_curve"]["auc"]
            
            ax2.plot(fpr, tpr, color='#3f51b5', lw=2, 
                    label=f'ROC curve (AUC = {auc:.2f})')
            ax2.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')
            ax2.set_xlim([0.0, 1.0])
            ax2.set_ylim([0.0, 1.05])
            ax2.set_xlabel('False Positive Rate')
            ax2.set_ylabel('True Positive Rate')
            ax2.legend(loc="lower right")
            ax2.grid(True, linestyle='--', alpha=0.7)
        else:
            # Create a confusion matrix visualization
            ax2 = fig.add_subplot(212)
            ax2.set_title("Prediction Confidence")
            
            # Simple confidence gauge
            confidence = self.classification_results.get("confidence", 75) / 100
            
            # Create a custom gauge
            theta = np.linspace(0, 180, 100) * np.pi / 180
            r = 1
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Draw the gauge background
            ax2.plot(x, y, 'gray', alpha=0.3, linewidth=20)
            
            # Draw the gauge value
            value_theta = np.linspace(0, 180 * confidence, 100) * np.pi / 180
            value_x = r * np.cos(value_theta)
            value_y = r * np.sin(value_theta)
            
            # Color based on confidence
            if confidence < 0.4:
                color = '#f44336'  # Red for low confidence
            elif confidence < 0.7:
                color = '#ff9800'  # Orange for medium confidence
            else:
                color = '#4caf50'  # Green for high confidence
                
            ax2.plot(value_x, value_y, color, linewidth=20)
            
            # Add the confidence percentage text
            ax2.text(0, 0, f"{confidence*100:.1f}%", 
                    fontsize=24, ha='center', va='center')
            
            ax2.set_xlim([-1.2, 1.2])
            ax2.set_ylim([-0.2, 1.2])
            ax2.axis('off')
        
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar_frame = tk.Frame(parent_frame)
        toolbar_frame.pack(fill="x")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        
    def create_metrics_tab(self, parent_frame):
        # Metrics summary table
        metrics_frame = tk.Frame(parent_frame, bg="white", padx=20, pady=20)
        metrics_frame.pack(fill="both", expand=True)
        
        tk.Label(metrics_frame, 
                 text="Classification Metrics", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w", pady=(0, 20))
        
        # Create table header
        header_frame = tk.Frame(metrics_frame, bg="#e8eaf6")
        header_frame.pack(fill="x")
        
        headers = ["Metric", "Value", "Description"]
        widths = [150, 100, 500]
        
        for i, header in enumerate(headers):
            tk.Label(header_frame, 
                    text=header, 
                    font=("Helvetica", 11, "bold"),
                    width=widths[i]//10,
                    bg="#e8eaf6", 
                    fg="#1a237e").pack(side="left", padx=2, pady=5)
        
        # Metrics data
        metrics_container = tk.Frame(metrics_frame, bg="white")
        metrics_container.pack(fill="both", expand=True)
        
        if self.classification_results:
            metrics = [
                ("Accuracy", 
                 f"{self.classification_results.get('accuracy', 0):.2f}", 
                 "The proportion of correct predictions among the total number of cases"),
                
                ("Precision", 
                 f"{self.classification_results.get('precision', 0):.2f}", 
                 "The proportion of true positive predictions among all positive predictions"),
                
                ("Recall", 
                 f"{self.classification_results.get('recall', 0):.2f}", 
                 "The proportion of true positive predictions among all actual positives"),
                
                ("F1 Score", 
                 f"{self.classification_results.get('f1_score', 0):.2f}", 
                 "The harmonic mean of precision and recall"),
                
                ("AUC", 
                 f"{self.classification_results.get('auc', 0):.2f}", 
                 "Area Under the ROC Curve, measuring the ability to discriminate between classes")
            ]
            
            for i, (metric, value, desc) in enumerate(metrics):
                entry_frame = tk.Frame(metrics_container, bg="white" if i % 2 == 0 else "#f5f5f5")
                entry_frame.pack(fill="x")
                
                tk.Label(entry_frame, 
                        text=metric, 
                        width=widths[0]//10,
                        anchor="w",
                        font=("Helvetica", 11),
                        bg=entry_frame["bg"]).pack(side="left", padx=2, pady=8)
                
                tk.Label(entry_frame, 
                        text=value, 
                        width=widths[1]//10,
                        anchor="center",
                        font=("Helvetica", 11, "bold"),
                        fg="#283593",
                        bg=entry_frame["bg"]).pack(side="left", padx=2, pady=8)
                
                tk.Label(entry_frame, 
                        text=desc, 
                        width=widths[2]//10,
                        anchor="w",
                        wraplength=widths[2] - 20,
                        bg=entry_frame["bg"]).pack(side="left", padx=2, pady=8)
        else:
            # No metrics available
            tk.Label(metrics_container, 
                    text="No classification metrics available", 
                    font=("Helvetica", 11),
                    bg="white",
                    fg="gray").pack(pady=20)
            
    def show_reports_view(self):
        self.clear_content_frame()
        
        # Header
        header_frame = tk.Frame(self.content_frame, bg="white", pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, 
                 text="Report Generation", 
                 font=("Helvetica", 18, "bold"),
                 bg="white", 
                 fg="#1a237e").pack()
        
        # Main content
        content = tk.Frame(self.content_frame, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Report options
        options_panel = tk.Frame(content, bg="white", width=400)
        options_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(options_panel, 
                 text="Report Options", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w", pady=(0, 10))
        
        # Option checkboxes
        options_frame = tk.Frame(options_panel, bg="white", padx=20, pady=10)
        options_frame.pack(fill="x")
        
        self.include_images = tk.BooleanVar(value=True)
        self.include_features = tk.BooleanVar(value=True)
        self.include_classification = tk.BooleanVar(value=True)
        self.include_metrics = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, 
                      text="Include Original and Processed Images", 
                      variable=self.include_images,
                      bg="white").pack(anchor="w", pady=5)
        
        tk.Checkbutton(options_frame, 
                      text="Include Feature Analysis", 
                      variable=self.include_features,
                      bg="white").pack(anchor="w", pady=5)
        
        tk.Checkbutton(options_frame, 
                      text="Include Classification Results", 
                      variable=self.include_classification,
                      bg="white").pack(anchor="w", pady=5)
        
        tk.Checkbutton(options_frame, 
                      text="Include Performance Metrics", 
                      variable=self.include_metrics,
                      bg="white").pack(anchor="w", pady=5)
        
        # Report filename
        filename_frame = tk.Frame(options_panel, bg="white", padx=20, pady=20)
        filename_frame.pack(fill="x")
        
        tk.Label(filename_frame, 
                 text="Report Filename:", 
                 font=("Helvetica", 12),
                 bg="white").pack(anchor="w")
        
        self.report_filename = ttk.Entry(filename_frame, width=30)
        self.report_filename.pack(fill="x", pady=5)
        self.report_filename.insert(0, f"lung_analysis_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Generate button
        generate_btn = tk.Button(options_panel, 
                                text="Generate Report", 
                                command=self.generate_report,
                                bg="#4caf50", 
                                fg="white",
                                font=("Helvetica", 12, "bold"),
                                width=15,
                                height=2,
                                relief="flat")
        generate_btn.pack(pady=20)
        
        # Right side - Report preview
        preview_panel = tk.Frame(content, bg="white", width=500)
        preview_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(preview_panel, 
                 text="Report Preview", 
                 font=("Helvetica", 14, "bold"),
                 bg="white", 
                 fg="#283593").pack(anchor="w", pady=(0, 10))
        
        # Preview container
        preview_container = tk.Frame(preview_panel, bg="#f5f5f5", bd=1, relief="solid")
        preview_container.pack(fill="both", expand=True)
        
        # Check if we have data for a report
        if not self.current_image_path or not self.classification_results:
            # Not enough data for a preview
            tk.Label(preview_container, 
                    text="Please process and classify an image before generating a report",
                    font=("Helvetica", 11),
                    bg="#f5f5f5",
                    fg="gray").pack(fill="both", expand=True)
        else:
            # Create a scrollable text area with preview
            preview_text = ScrolledText(preview_container, width=50, height=25)
            preview_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Add preview content
            preview_text.insert(tk.END, "LUNG ANALYSIS REPORT\n", "title")
            preview_text.insert(tk.END, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            preview_text.insert(tk.END, f"User: {self.username}\n\n")
            
            preview_text.insert(tk.END, "IMAGE INFORMATION\n", "header")
            preview_text.insert(tk.END, f"Filename: {os.path.basename(self.current_image_path)}\n")
            preview_text.insert(tk.END, f"Dimensions: {self.current_image.width}x{self.current_image.height}\n\n")
            
            preview_text.insert(tk.END, "CLASSIFICATION RESULTS\n", "header")
            preview_text.insert(tk.END, f"Diagnosis: {self.classification_results.get('diagnosis', 'Unknown')}\n")
            preview_text.insert(tk.END, f"Confidence: {self.classification_results.get('confidence', 0):.1f}%\n")
            preview_text.insert(tk.END, f"Model: {self.classification_results.get('model', 'Unknown')}\n\n")
            
            if self.feature_data:
                preview_text.insert(tk.END, "KEY FEATURES\n", "header")
                preview_text.insert(tk.END, f"Area: {self.feature_data.get('area', 'N/A')}\n")
                preview_text.insert(tk.END, f"Perimeter: {self.feature_data.get('perimeter', 'N/A')}\n")
                preview_text.insert(tk.END, f"Circularity: {self.feature_data.get('circularity', 'N/A'):.4f}\n")
                preview_text.insert(tk.END, f"Mean Intensity: {self.feature_data.get('mean_intensity', 'N/A'):.4f}\n\n")
            
            preview_text.insert(tk.END, "PERFORMANCE METRICS\n", "header")
            preview_text.insert(tk.END, f"Accuracy: {self.classification_results.get('accuracy', 0):.2f}\n")
            preview_text.insert(tk.END, f"Precision: {self.classification_results.get('precision', 0):.2f}\n")
            preview_text.insert(tk.END, f"Recall: {self.classification_results.get('recall', 0):.2f}\n")
            preview_text.insert(tk.END, f"F1 Score: {self.classification_results.get('f1_score', 0):.2f}\n")
            preview_text.insert(tk.END, f"AUC: {self.classification_results.get('auc', 0):.2f}\n\n")
            
            preview_text.insert(tk.END, "NOTES\n", "header")
            preview_text.insert(tk.END, "This is a sample preview of the report. The actual PDF report will include visualizations and more detailed information.\n")
            
            # Configure tags for styling
            preview_text.tag_configure("title", font=("Helvetica", 14, "bold"))
            preview_text.tag_configure("header", font=("Helvetica", 12, "bold"))
            
            # Make text read-only
            preview_text.config(state=tk.DISABLED)
            
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Lung Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp")]
        )
        
        if not file_path:
            return
            
        try:
            # Open the image
            image = Image.open(file_path)
            
            # Save image info
            self.current_image = image
            self.current_image_path = file_path
            
            # Reset related data
            self.processed_image = None
            self.segmented_image = None
            self.feature_data = None
            self.classification_results = None
            
            # Add to session history
            self.add_to_history("Image Loaded", os.path.basename(file_path), "Success")
            
            # If we're in the processing view, update the image display
            if hasattr(self, 'image_canvas_frame'):
                for widget in self.image_canvas_frame.winfo_children():
                    widget.destroy()
                    
                self.display_image(self.image_canvas_frame, image)
                
                # Clear the processed image area
                for widget in self.processed_canvas_frame.winfo_children():
                    widget.destroy()
                
                placeholder = tk.Label(self.processed_canvas_frame, 
                                      text="No processed image. Use controls below.",
                                      bg="#f5f5f5", 
                                      fg="gray")
                placeholder.pack(fill="both", expand=True)
            
            messagebox.showinfo("Success", f"Image loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
            traceback.print_exc()
        
    def display_image(self, frame, image):
        """Display an image in the given frame with proper scaling"""
        for widget in frame.winfo_children():
            widget.destroy()
            
        # Get frame dimensions
        frame.update()
        frame_width = frame.winfo_width()
        frame_height = frame.winfo_height()
        
        # Create a copy to avoid modifying the original
        img_copy = image.copy()
        
        # Calculate scaling to fit in the frame
        img_width, img_height = img_copy.size
        
        # Calculate scaling factor
        width_ratio = frame_width / img_width
        height_ratio = frame_height / img_height
        
        # Use the smaller ratio to ensure the image fits completely
        scale_factor = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(img_width * scale_factor * 0.9)  # 90% of the available space
        new_height = int(img_height * scale_factor * 0.9)
        
        # Resize the image
        img_resized = img_copy.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        img_tk = ImageTk.PhotoImage(img_resized)
        
        # Store a reference to avoid garbage collection
        frame.image = img_tk
        
        # Create and place the label
        img_label = tk.Label(frame, image=img_tk, bg="#f5f5f5")
        img_label.pack(expand=True)
        
    def process_current_image(self):
        """Process the currently loaded image"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
            
        try:
            # Get the processing method
            method = getattr(self, 'processing_method', tk.StringVar(value="standard")).get()
            
            # Process the image
            # In a real app, this would call the actual image processor
            self.processed_image, self.segmented_image = self.image_processor.process_image(
                self.current_image, method=method)
            
            # Add to session history
            self.add_to_history("Image Processing", os.path.basename(self.current_image_path), "Success")
            
            # If we're in the processing view, update the display
            if hasattr(self, 'processed_canvas_frame'):
                self.display_image(self.processed_canvas_frame, self.processed_image)
                
            messagebox.showinfo("Success", "Image processed successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            traceback.print_exc()
        
    def extract_and_show_features(self):
        """Extract features and switch to feature view"""
        self.extract_features()
        if self.feature_data:
            self.show_feature_view()
        
    def extract_features(self):
        """Extract features from the processed image"""
        if self.segmented_image is None:
            messagebox.showwarning("Warning", "Please process an image first")
            return
        
        try:
            # Get feature extraction options
            use_shape = getattr(self, 'use_shape_features', tk.BooleanVar(value=True)).get()
            use_texture = getattr(self, 'use_texture_features', tk.BooleanVar(value=True)).get()
            use_intensity = getattr(self, 'use_intensity_features', tk.BooleanVar(value=True)).get()
            
            # Extract features
            self.feature_data = self.feature_extractor.extract_features(
                self.current_image, 
                self.segmented_image,
                extract_shape=use_shape,
                extract_texture=use_texture,
                extract_intensity=use_intensity
            )
            
            # Add to session history
            self.add_to_history("Feature Extraction", os.path.basename(self.current_image_path), 
                               f"{len(self.feature_data)} features")
            
            # Update display if in feature view
            if hasattr(self, 'features_table_frame'):
                self.display_features_table()
                
            messagebox.showinfo("Success", "Features extracted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract features: {str(e)}")
            traceback.print_exc()
        
    def display_features_table(self):
        """Display the extracted features in a table"""
        if not self.feature_data:
            return
            
        # Clear previous content
        for widget in self.features_table_frame.winfo_children():
            widget.destroy()
            
        # Create a scrollable frame
        canvas = tk.Canvas(self.features_table_frame, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(self.features_table_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Table headers
        headers_frame = tk.Frame(scrollable_frame, bg="#e8eaf6")
        headers_frame.pack(fill="x")
        
        tk.Label(headers_frame, 
                text="Feature", 
                font=("Helvetica", 11, "bold"),
                width=20,
                anchor="w",
                bg="#e8eaf6", 
                fg="#1a237e").pack(side="left", padx=2, pady=5)
        
        tk.Label(headers_frame, 
                text="Value", 
                font=("Helvetica", 11, "bold"),
                width=15,
                bg="#e8eaf6", 
                fg="#1a237e").pack(side="left", padx=2, pady=5)
        
        tk.Label(headers_frame, 
                text="Description", 
                font=("Helvetica", 11, "bold"),
                width=40,
                anchor="w",
                bg="#e8eaf6", 
                fg="#1a237e").pack(side="left", padx=2, pady=5)
        
        # Feature descriptions - would be more comprehensive in a real application
        descriptions = {
            "area": "Total area of the segmented region",
            "perimeter": "Length of the boundary of the segmented region",
            "circularity": "Measure of how close the segmented region is to a circle",
            "eccentricity": "Measure of elongation of the segmented region",
            "mean_intensity": "Average pixel intensity in the segmented region",
            "std_intensity": "Standard deviation of pixel intensity",
            "contrast": "Measure of local intensity variation",
            "energy": "Sum of squared elements in the GLCM",
            "homogeneity": "Measure of closeness of distribution of GLCM elements",
            "correlation": "Measure of correlation between pixel pairs"
        }
        
        # Add rows for each feature
        row_index = 0
        for feature, value in self.feature_data.items():
            # Skip complex features like matrices
            if isinstance(value, (np.ndarray, list)) and len(value) > 10:
                continue
                
            # Create row with alternating background
            bg_color = "#f5f5f5" if row_index % 2 == 0 else "white"
            row_frame = tk.Frame(scrollable_frame, bg=bg_color)
            row_frame.pack(fill="x")
            
            # Feature name - make it more readable
            display_name = feature.replace("_", " ").title()
            
            tk.Label(row_frame, 
                    text=display_name, 
                    width=20,
                    anchor="w",
                    bg=bg_color).pack(side="left", padx=2, pady=5)
            
            # Format the value based on type
            if isinstance(value, float):
                formatted_value = f"{value:.4f}"
            else:
                formatted_value = str(value)
                
            tk.Label(row_frame, 
                    text=formatted_value, 
                    width=15,
                    anchor="center",
                    bg=bg_color).pack(side="left", padx=2, pady=5)
            
            # Description if available
            description = descriptions.get(feature, "")
            
            tk.Label(row_frame, 
                    text=description, 
                    width=40,
                    anchor="w",
                    wraplength=300,
                    bg=bg_color).pack(side="left", padx=2, pady=5)
            
            row_index += 1
        
    def visualize_features(self):
        """Visualize the extracted features"""
        if not self.feature_data:
            messagebox.showwarning("Warning", "Please extract features first")
            return
            
        try:
            # Create a new window for visualization
            viz_window = tk.Toplevel(self.root)
            viz_window.title("Feature Visualization")
            viz_window.geometry("800x600")
            
            # Create visualization using our visualizer
            self.visualizer.visualize_features(self.feature_data, viz_window)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize features: {str(e)}")
            traceback.print_exc()
        
    def classify_image(self):
        """Classify the image using the selected model"""
        if not self.feature_data:
            messagebox.showwarning("Warning", "Please extract features first")
            return
            
        try:
            # Get the selected model
            model_type = getattr(self, 'classification_model', tk.StringVar(value="svm")).get()
            
            # Classify using the model evaluator
            self.classification_results = self.model_evaluator.classify(
                self.feature_data, model_type)
            
            # Add timestamp to results
            self.classification_results["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add to session history
            self.add_to_history("Classification", os.path.basename(self.current_image_path), 
                               self.classification_results.get("diagnosis", "Unknown"))
            
            # Update display if in classification view
            if hasattr(self, 'classification_results_frame'):
                self.display_classification_results()
                
            messagebox.showinfo("Success", "Image classified successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to classify image: {str(e)}")
            traceback.print_exc()
        
    def display_classification_results(self):
        """Display the classification results"""
        if not self.classification_results:
            return
            
        # Clear previous content
        for widget in self.classification_results_frame.winfo_children():
            widget.destroy()
            
        # Create results container
        results_container = tk.Frame(self.classification_results_frame, bg="#f5f5f5", padx=20, pady=20)
        results_container.pack(fill="both", expand=True)
        
        # Main diagnosis section
        diagnosis_frame = tk.Frame(results_container, bg="#f5f5f5", pady=10)
        diagnosis_frame.pack(fill="x")
        
        diagnosis = self.classification_results.get("diagnosis", "Unknown")
        diagnosis_color = "#4caf50" if diagnosis == "Normal" else "#f44336"
        
        tk.Label(diagnosis_frame, 
                text="Diagnosis:", 
                font=("Helvetica", 14, "bold"),
                bg="#f5f5f5").pack(side="left", padx=10)
        
        tk.Label(diagnosis_frame, 
                text=diagnosis, 
                font=("Helvetica", 18, "bold"),
                fg=diagnosis_color,
                bg="#f5f5f5").pack(side="left", padx=10)
        
        # Confidence section
        confidence_frame = tk.Frame(results_container, bg="#f5f5f5", pady=10)
        confidence_frame.pack(fill="x")
        
        confidence = self.classification_results.get("confidence", 0)
        
        tk.Label(confidence_frame, 
                text="Confidence:", 
                font=("Helvetica", 12, "bold"),
                bg="#f5f5f5").pack(side="left", padx=10)
        
        # Progress bar for confidence
        confidence_bar = ttk.Progressbar(confidence_frame, 
                                         length=300, 
                                         mode='determinate',
                                         value=confidence)
        confidence_bar.pack(side="left", padx=10)
        
        tk.Label(confidence_frame, 
                text=f"{confidence:.1f}%", 
                font=("Helvetica", 12),
                bg="#f5f5f5").pack(side="left", padx=10)
        
        # Divider
        ttk.Separator(results_container, orient="horizontal").pack(fill="x", pady=20)
        
        # Class probabilities section
        probabilities_frame = tk.Frame(results_container, bg="#f5f5f5", pady=10)
        probabilities_frame.pack(fill="x")
        
        tk.Label(probabilities_frame, 
                text="Class Probabilities:", 
                font=("Helvetica", 12, "bold"),
                bg="#f5f5f5").pack(anchor="w", padx=10)
        
        # Get class probabilities
        class_names = self.classification_results.get("class_names", ["Normal", "Abnormal"])
        probs = self.classification_results.get("probabilities", [0.5, 0.5])
        
        # Create bars for each class
        for i, (cls, prob) in enumerate(zip(class_names, probs)):
            class_frame = tk.Frame(results_container, bg="#f5f5f5", pady=5)
            class_frame.pack(fill="x")
            
            tk.Label(class_frame, 
                    text=f"{cls}:", 
                    font=("Helvetica", 11),
                    width=10,
                    bg="#f5f5f5").pack(side="left", padx=10)
            
            # Bar color based on class
            style_name = f"class{i}.Horizontal.TProgressbar"
            bar_color = "#4caf50" if i == 0 else "#f44336"
            
            if not hasattr(self, f'style_{i}_created'):
                style = ttk.Style()
                style.configure(style_name, background=bar_color)
                setattr(self, f'style_{i}_created', True)
            
            # Progress bar
            class_bar = ttk.Progressbar(class_frame, 
                                       length=300, 
                                       mode='determinate',
                                       style=style_name,
                                       value=prob * 100)
            class_bar.pack(side="left", padx=10)
            
            tk.Label(class_frame, 
                    text=f"{prob*100:.1f}%", 
                    font=("Helvetica", 11),
                    bg="#f5f5f5").pack(side="left", padx=10)
        
        # Divider
        ttk.Separator(results_container, orient="horizontal").pack(fill="x", pady=20)
        
        # Model and timestamp info
        info_frame = tk.Frame(results_container, bg="#f5f5f5", pady=10)
        info_frame.pack(fill="x")
        
        model = self.classification_results.get("model", "Unknown")
        model_display = {
            "svm": "Support Vector Machine",
            "random_forest": "Random Forest",
            "logistic_regression": "Logistic Regression",
            "neural_network": "Neural Network"
        }.get(model, model)
        
        tk.Label(info_frame, 
                text=f"Model: {model_display}", 
                font=("Helvetica", 11),
                bg="#f5f5f5").pack(anchor="w", padx=10, pady=2)
        
        tk.Label(info_frame, 
                text=f"Analysis Date: {self.classification_results.get('date', 'Unknown')}", 
                font=("Helvetica", 11),
                bg="#f5f5f5").pack(anchor="w", padx=10, pady=2)
        
    def visualize_classification_results(self):
        """Visualize the classification results"""
        if not self.classification_results:
            messagebox.showwarning("Warning", "Please classify the image first")
            return
            
        try:
            # Create a new window for visualization
            viz_window = tk.Toplevel(self.root)
            viz_window.title("Classification Results Visualization")
            viz_window.geometry("800x600")
            
            # Create visualization using our visualizer
            self.visualizer.visualize_classification(self.classification_results, viz_window)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize classification results: {str(e)}")
            traceback.print_exc()
        
    def save_processed_image(self):
        """Save the processed image to a file"""
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.processed_image.save(file_path)
            messagebox.showinfo("Success", f"Image saved to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            traceback.print_exc()
        
    def generate_report(self):
        """Generate a PDF report of the analysis results"""
        if not self.current_image_path or not self.classification_results:
            messagebox.showwarning("Warning", "Please process and classify an image first")
            return
            
        # Get report filename
        if hasattr(self, 'report_filename'):
            filename = self.report_filename.get()
        else:
            filename = f"lung_analysis_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        # Get report options
        include_images = getattr(self, 'include_images', tk.BooleanVar(value=True)).get()
        include_features = getattr(self, 'include_features', tk.BooleanVar(value=True)).get()
        include_classification = getattr(self, 'include_classification', tk.BooleanVar(value=True)).get()
        include_metrics = getattr(self, 'include_metrics', tk.BooleanVar(value=True)).get()
        
        # Choose save location
        file_path = filedialog.asksaveasfilename(
            title="Save Report PDF",
            initialfile=filename,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Generate the report
            self.report_generator.generate_report(
                file_path,
                self.current_image,
                self.processed_image,
                self.feature_data,
                self.classification_results,
                include_images=include_images,
                include_features=include_features,
                include_classification=include_classification,
                include_metrics=include_metrics
            )
            
            # Add to session history
            self.add_to_history("Report Generation", os.path.basename(file_path), "Success")
            
            messagebox.showinfo("Success", f"Report saved to {file_path}")
            
            # Ask if user wants to open the report
            if messagebox.askyesno("Open Report", "Would you like to open the report now?"):
                self.open_report(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            traceback.print_exc()
        
    def open_report(self, file_path):
        """Open the generated PDF report"""
        try:
            import platform
            import subprocess
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # Linux and other Unix-like
                subprocess.run(['xdg-open', file_path])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open report: {str(e)}")
        
    def show_documentation(self):
        """Show application documentation"""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Lung Analysis Suite Documentation")
        doc_window.geometry("800x600")
        
        main_frame = tk.Frame(doc_window, bg="white")
        main_frame.pack(fill="both", expand=True)
        
        # Add documentation content
        text_widget = ScrolledText(main_frame, wrap=tk.WORD, font=("Helvetica", 12))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add documentation text
        doc_text = """
# Lung Analysis Suite Documentation

## Overview
The Lung Analysis Suite is an advanced medical imaging analysis application designed for processing and analyzing lung medical images. It offers image segmentation, feature extraction, and classification using machine learning algorithms to assist with lung pathology diagnosis.

## Getting Started
1. Load an image using the "Open Image" button or File > Open Image menu
2. Process the image using the available methods
3. Extract features from the processed image
4. Classify the image using the selected machine learning model
5. Generate a detailed report of the analysis

## Image Processing
The application offers multiple methods for processing and segmenting lung images:
- Standard Segmentation: Basic thresholding and morphological operations
- Watershed Segmentation: Advanced segmentation for complex boundaries
- Active Contour: Contour-based segmentation for detailed boundaries

## Feature Extraction
The following types of features can be extracted:
- Shape Features: Area, perimeter, circularity, eccentricity, etc.
- Texture Features: GLCM-based features like contrast, homogeneity, energy
- Intensity Features: Mean, standard deviation, skewness, kurtosis of pixel intensities

## Classification
Available classification models:
- Support Vector Machine (SVM): Effective for high-dimensional spaces
- Random Forest: Ensemble method using multiple decision trees
- Logistic Regression: Simple and interpretable baseline model
- Neural Network: Multi-layer perceptron for complex patterns

## Reports
Generate comprehensive PDF reports including:
- Original and processed images
- Feature analysis with visualizations
- Classification results with confidence measures
- Performance metrics

## Tips for Best Results
- Use high-quality medical images in common formats (DICOM, JPEG, PNG)
- Ensure images are properly oriented and cropped
- For best classification results, use the Random Forest or SVM models
- Include all sections in the report for comprehensive documentation
"""
        
        text_widget.insert(tk.END, doc_text)
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
    def show_about(self):
        """Show application about dialog"""
        messagebox.showinfo(
            "About Lung Analysis Suite",
            "Lung Analysis Suite v1.0\n\n"
            "An advanced medical imaging application for lung analysis\n\n"
            "Features:\n"
            "- Image processing and segmentation\n"
            "- Feature extraction\n"
            "- Machine learning classification\n"
            "- Comprehensive reporting\n\n"
            "© 2023 Medical Imaging Solutions"
        )
        
    def add_to_history(self, activity, image_name, result):
        """Add an entry to the session history"""
        self.session_history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "activity": activity,
            "image_name": image_name,
            "result": result
        })
        
    def load_models(self):
        """Load pretrained models if available"""
        try:
            # This would load saved models in a real implementation
            # For this example, we'll use newly created models in the classify method
            pass
        except Exception as e:
            print(f"Warning: Could not load pretrained models: {str(e)}")
        
    def logout(self):
        """Log out and return to the login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.root.destroy()
            login_window = LoginWindow()
            login_window.run()
        
    def exit_application(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()
            self.root.destroy()


if __name__ == "__main__":
    try:
        login = LoginWindow()
        login.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()