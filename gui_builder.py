from tkinter import Toplevel, Frame, Label, Button, Scale, HORIZONTAL
from PIL import Image, ImageTk
import cv2


class GUIBuilder:
    def __init__(self, app):
        self.app = app
    
    def create_main_window(self, main_window):
        """Create the main GUI window with perfect alignment using grid"""
        main_window.title("Gaussian Blur and Face Scaling")
        main_window.geometry("1400x900")
        
        # Configure grid weights for main window
        main_window.grid_rowconfigure(0, weight=0)  # Title
        main_window.grid_rowconfigure(1, weight=1)  # Images (expands)
        main_window.grid_rowconfigure(2, weight=0)  # Spacer
        main_window.grid_rowconfigure(3, weight=0)  # Controls (fixed)
        main_window.grid_rowconfigure(4, weight=1)  # Bottom spacer (expands)
        main_window.grid_columnconfigure(0, weight=1)
        
        # ============================================
        # TITLE (Row 0)
        # ============================================
        title_label = Label(main_window, text="Gaussian Blur and Face Scaling", 
                        font=("Arial", 22, "bold"))
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="n")
        
        # ============================================
        # IMAGE ROW (Row 1)
        # ============================================
        # Create a frame specifically for the three images
        image_row_frame = Frame(main_window)
        image_row_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 0))
        
        # Configure image row frame grid (1 row, 3 columns)
        image_row_frame.grid_rowconfigure(0, weight=1)
        image_row_frame.grid_columnconfigure(0, weight=1, uniform="image_col")
        image_row_frame.grid_columnconfigure(1, weight=1, uniform="image_col")
        image_row_frame.grid_columnconfigure(2, weight=1, uniform="image_col")
        
        # Create image columns
        self.create_image_columns(image_row_frame)
        
        # ============================================
        # SPACER (Row 2) - To lower the adjuster bar
        # ============================================
        spacer_frame = Frame(main_window, height=40)  # Increased spacer to lower adjuster
        spacer_frame.grid(row=2, column=0, sticky="ew")
        spacer_frame.grid_propagate(False)  # Keep fixed height
        
        # ============================================
        # CONTROL SECTION (Row 3) - Only adjuster remains
        # ============================================
        control_section = Frame(main_window)
        control_section.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Create a container for centering the controls
        control_container = Frame(control_section)
        control_container.pack(expand=True)  # Center horizontally
        
        # Control title
        control_title = Label(control_container, text="Gaussian Blur Control", 
                            font=("Arial", 14, "bold"))
        control_title.pack(pady=(0, 10))
        
        # Current blur info
        current_stage = self.app.blur_stages[self.app.current_blur_stage]
        self.app.blur_info_label = Label(control_container,
                                        text=f"{current_stage['name']} | Kernel: {current_stage['kernel']}x{current_stage['kernel']} | Sigma: {current_stage['sigma']}",
                                        font=("Arial", 11, "bold"),
                                        fg=current_stage['color'])
        self.app.blur_info_label.pack(pady=(0, 15))
        
        # Slider frame
        slider_frame = Frame(control_container)
        slider_frame.pack(pady=5)
        
        # Min label
        min_label = Label(slider_frame, text="Light", font=("Arial", 9, "bold"))
        min_label.pack(side="left", padx=5)
        
        # Slider
        self.app.slider = Scale(slider_frame, from_=0, to=100, orient=HORIZONTAL,
                            length=350, showvalue=False,
                            command=self.app.update_blur_from_slider,
                            sliderlength=20, troughcolor="#e0e0e0")
        self.app.slider.set(current_stage["slider_value"])
        self.app.slider.pack(side="left", padx=15)
        
        # Max label
        max_label = Label(slider_frame, text="Heavy", font=("Arial", 9, "bold"))
        max_label.pack(side="left", padx=5)
        
        # Stage indicators (dots only, no descriptions)
        indicator_frame = Frame(control_container)
        indicator_frame.pack(pady=10)
        
        self.app.stage_dots = []
        self.app.stage_names = []
        
        for i, stage in enumerate(self.app.blur_stages):
            indicator_item = Frame(indicator_frame)
            indicator_item.pack(side="left", padx=40)
            
            # Dot indicator
            dot_color = stage['color'] if i == self.app.current_blur_stage else "#cccccc"
            dot = Label(indicator_item, text="●", font=("Arial", 20), fg=dot_color)
            dot.pack()
            
            # Stage name (small label under dot)
            name_color = "black" if i == self.app.current_blur_stage else "#666666"
            stage_name = Label(indicator_item, text=stage['name'], 
                            font=("Arial", 9, "bold"), fg=name_color)
            stage_name.pack()
            
            self.app.stage_dots.append(dot)
            self.app.stage_names.append(stage_name)
        
        # ============================================
        # BOTTOM SPACER (Row 4) - Takes up remaining space
        # ============================================
        bottom_spacer = Frame(main_window)
        bottom_spacer.grid(row=4, column=0, sticky="nsew")
        
        # Start the main loop
        main_window.mainloop()
    
    def create_image_columns(self, image_row_frame):
        """Create the three image columns"""
        # ===== COLUMN 0: ORIGINAL IMAGE =====
        col0 = Frame(image_row_frame, bd=1, relief="solid", padx=5, pady=5)
        col0.grid(row=0, column=0, sticky="nsew", padx=5)
        
        # Original title
        original_title = Label(col0, text="Original Image", 
                            font=("Arial", 14, "bold"))
        original_title.grid(row=0, column=0, pady=(0, 5), sticky="n")
        
        # Original image display
        original_rgb = cv2.cvtColor(self.app.original_image, cv2.COLOR_BGR2RGB)
        original_resized = self.app.resize_to_exact_size(original_rgb, self.app.image_display_size)
        original_pil = Image.fromarray(original_resized)
        self.app.original_photo = ImageTk.PhotoImage(image=original_pil)
        
        self.app.original_label = Label(col0, image=self.app.original_photo, 
                                    relief="solid", bd=2)
        self.app.original_label.grid(row=1, column=0, pady=(0, 5), sticky="n")
        
        # Original info
        original_info = Label(col0, 
                            text=f"Original Size: {self.app.original_image.shape[1]}x{self.app.original_image.shape[0]}",
                            font=("Arial", 9))
        original_info.grid(row=2, column=0, sticky="n")
        
        # Configure column 0
        col0.grid_rowconfigure(1, weight=1)
        col0.grid_columnconfigure(0, weight=1)
        
        # ===== COLUMN 1: BLURRED IMAGE =====
        col1 = Frame(image_row_frame, bd=1, relief="solid", padx=5, pady=5)
        col1.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Blurred title
        blurred_title = Label(col1, text="Blurred Image Output", 
                            font=("Arial", 14, "bold"))
        blurred_title.grid(row=0, column=0, pady=(0, 5), sticky="n")
        
        # Blurred image display
        blurred_rgb = cv2.cvtColor(self.app.blurred_image, cv2.COLOR_BGR2RGB)
        blurred_resized = self.app.resize_to_exact_size(blurred_rgb, self.app.image_display_size)
        blurred_pil = Image.fromarray(blurred_resized)
        self.app.blurred_photo = ImageTk.PhotoImage(image=blurred_pil)
        
        self.app.blurred_label = Label(col1, image=self.app.blurred_photo, 
                                    relief="solid", bd=2)
        self.app.blurred_label.grid(row=1, column=0, pady=(0, 5), sticky="n")
        
        # Configure column 1
        col1.grid_rowconfigure(1, weight=1)
        col1.grid_columnconfigure(0, weight=1)
        
        # ===== COLUMN 2: RESIZED FACE =====
        col2 = Frame(image_row_frame, bd=1, relief="solid", padx=5, pady=5)
        col2.grid(row=0, column=2, sticky="nsew", padx=5)
        
        # Face title
        face_title = Label(col2, text="Resized Face Output", 
                        font=("Arial", 14, "bold"))
        face_title.grid(row=0, column=0, pady=(0, 5), sticky="n")
        
        # Face image display
        face_rgb = cv2.cvtColor(self.app.resized_face_image, cv2.COLOR_BGR2RGB)
        face_pil = Image.fromarray(face_rgb)
        self.app.face_photo = ImageTk.PhotoImage(image=face_pil)
        
        self.app.face_label = Label(col2, image=self.app.face_photo, 
                                relief="solid", bd=2)
        self.app.face_label.grid(row=1, column=0, pady=(0, 5), sticky="n")
        
        # Face size info
        size_label = Label(col2, 
                        text=f"Size: {self.app.face_display_size[0]}x{self.app.face_display_size[1]} pixels",
                        font=("Arial", 10))
        size_label.grid(row=2, column=0, pady=5, sticky="n")
        
        # Face navigation (only if multiple faces)
        if len(self.app.extracted_faces) > 1:
            # Face counter label
            self.app.face_nav_label = Label(col2, 
                                        text=f"Face {self.app.current_face_index + 1} of {len(self.app.extracted_faces)}",
                                        font=("Arial", 10, "bold"), fg="blue")
            self.app.face_nav_label.grid(row=3, column=0, pady=(5, 2), sticky="n")
            
            # Navigation buttons frame - positioned to avoid overlap
            nav_frame = Frame(col2)
            nav_frame.grid(row=4, column=0, pady=(0, 5), sticky="n")
            
            # Small blue arrow buttons
            prev_btn = Button(nav_frame, text="◀", 
                            command=lambda: self.app.navigate_faces("prev"),
                            font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                            width=3, height=1, relief="flat", bd=1)
            prev_btn.pack(side="left", padx=2)
            
            next_btn = Button(nav_frame, text="▶", 
                            command=lambda: self.app.navigate_faces("next"),
                            font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                            width=3, height=1, relief="flat", bd=1)
            next_btn.pack(side="left", padx=2)
            
            # Configure column 2 with extra row for navigation
            col2.grid_rowconfigure(1, weight=1)
            col2.grid_rowconfigure(4, weight=0)
        else:
            # Configure column 2 without navigation
            col2.grid_rowconfigure(1, weight=1)
        
        col2.grid_columnconfigure(0, weight=1)