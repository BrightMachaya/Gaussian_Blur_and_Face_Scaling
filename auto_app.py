import cv2
import numpy as np
from tkinter import Tk, filedialog, messagebox, Toplevel, Button, Label, Frame, Scale, HORIZONTAL
from PIL import Image, ImageTk
from mtcnn import MTCNN

class FaceBlurAndScaleApp:
    def __init__(self):
        self.root = Tk()
        self.root.withdraw()  # Hide main window
        
        # Initialize face detector
        self.detector = MTCNN()
        
        # Image variables
        self.original_image = None
        self.blurred_image = None
        self.face_image = None
        self.resized_face_image = None
        self.faces = []
        self.extracted_faces = []
        self.current_face_index = 0
        
        # Blur settings - 3 stages
        self.blur_stages = [
            {"name": "Light Blur", "kernel": 25, "sigma": 10, "color": "#4CAF50", "slider_value": 0},
            {"name": "Medium Blur", "kernel": 55, "sigma": 25, "color": "#FF9800", "slider_value": 50},
            {"name": "Heavy Blur", "kernel": 101, "sigma": 50, "color": "#F44336", "slider_value": 100}
        ]
        self.current_blur_stage = 1
        
        # Image display settings
        self.image_display_size = (400, 400)
        self.face_display_size = (400, 400)
        
        # Load image
        self.load_image()
        
        # Create GUI
        self.create_gui()
        
    def load_image(self):
        """Load image from file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select an Image with Face",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        
        if not file_path:
            messagebox.showerror("Error", "No image selected!")
            self.root.quit()
            return
        
        self.original_image = cv2.imread(file_path)
        if self.original_image is None:
            messagebox.showerror("Error", "Could not load image!")
            self.root.quit()
            return
        
        self.detect_faces()
        
        if self.faces:
            self.extract_all_faces()
            self.extract_face()
            self.resize_face_to_display()
        else:
            messagebox.showinfo("No Face", "No faces detected in the image!")
            self.root.quit()
            return
        
        self.apply_blur()
    
    def detect_faces(self):
        """Detect faces in the image"""
        try:
            rgb_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.faces = self.detector.detect_faces(rgb_image)
            
            if len(self.faces) == 0:
                return False
            
            print(f"Detected {len(self.faces)} face(s)")
            return True
        except Exception as e:
            print(f"Face detection error: {e}")
            return False
    
    def extract_all_faces(self):
        """Extract all faces from the image and store them in temporary storage"""
        self.extracted_faces = []
        
        for i, face in enumerate(self.faces):
            x, y, w, h = face['box']
            
            padding = int(min(w, h) * 0.2)
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(self.original_image.shape[1] - x, w + 2 * padding)
            h = min(self.original_image.shape[0] - y, h + 2 * padding)
            
            face_image = self.original_image[y:y+h, x:x+w].copy()
            
            self.extracted_faces.append({
                'image': face_image,
                'box': (x, y, w, h),
                'confidence': face['confidence'],
                'index': i
            })
        
        print(f"Extracted {len(self.extracted_faces)} face(s) to temporary storage")
    
    def extract_face(self):
        """Extract the current face from stored faces"""
        if not self.extracted_faces:
            return
        
        current_face_data = self.extracted_faces[self.current_face_index]
        self.face_image = current_face_data['image'].copy()
        
        print(f"Displaying face {self.current_face_index + 1}/{len(self.extracted_faces)}")
    
    def navigate_faces(self, direction):
        """Navigate between extracted faces"""
        if len(self.extracted_faces) <= 1:
            return
        
        if direction == "next":
            self.current_face_index = (self.current_face_index + 1) % len(self.extracted_faces)
        elif direction == "prev":
            self.current_face_index = (self.current_face_index - 1) % len(self.extracted_faces)
        
        self.extract_face()
        self.resize_face_to_display()
        self.update_display()
        self.update_face_navigation_info()
    
    def update_face_navigation_info(self):
        """Update face navigation information in the GUI"""
        if hasattr(self, 'face_nav_label'):
            if len(self.extracted_faces) > 1:
                self.face_nav_label.config(
                    text=f"Face {self.current_face_index + 1} of {len(self.extracted_faces)}",
                    fg="blue"
                )
    
    def resize_face_to_display(self):
        """Resize face image to fit display frame using built-in bicubic interpolation"""
        if self.face_image is None:
            return
        
        target_width, target_height = self.face_display_size
        # Using cv2.resize with bicubic interpolation
        self.resized_face_image = cv2.resize(
            self.face_image, 
            (target_width, target_height), 
            interpolation=cv2.INTER_CUBIC
        )
        
        print(f"Face resized to: {target_width}x{target_height} pixels")
    
    def apply_gaussian_blur(self, image, kernel_size, sigma):
        """Apply Gaussian blur using built-in cv2.GaussianBlur"""
        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Use cv2.GaussianBlur built-in function
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
        return blurred
    
    def apply_blur(self):
        """Apply blur to the original image based on current stage"""
        if self.original_image is None:
            return
        
        stage = self.blur_stages[self.current_blur_stage]
        print(f"Applying {stage['name']}: Kernel={stage['kernel']}, Sigma={stage['sigma']}")
        
        self.blurred_image = self.apply_gaussian_blur(
            self.original_image.copy(), 
            stage['kernel'], 
            stage['sigma']
        )
    
    def update_blur_from_slider(self, value):
        """Update blur based on slider value (3 distinct stages)"""
        slider_val = int(float(value))
        
        if slider_val <= 25:
            new_stage = 0
            self.slider.set(0)
        elif slider_val <= 75:
            new_stage = 1
            self.slider.set(50)
        else:
            new_stage = 2
            self.slider.set(100)
        
        if new_stage != self.current_blur_stage:
            self.current_blur_stage = new_stage
            self.apply_blur()
            self.update_display()
            self.update_blur_info()
            self.update_stage_indicators()
    
    def update_display(self):
        """Update all three output frames"""
        if self.original_image is not None:
            original_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            original_resized = self.resize_to_exact_size(original_rgb, self.image_display_size)
            original_pil = Image.fromarray(original_resized)
            self.original_photo = ImageTk.PhotoImage(image=original_pil)
            self.original_label.config(image=self.original_photo)
        
        if self.blurred_image is not None:
            blurred_rgb = cv2.cvtColor(self.blurred_image, cv2.COLOR_BGR2RGB)
            blurred_resized = self.resize_to_exact_size(blurred_rgb, self.image_display_size)
            blurred_pil = Image.fromarray(blurred_resized)
            self.blurred_photo = ImageTk.PhotoImage(image=blurred_pil)
            self.blurred_label.config(image=self.blurred_photo)
        
        if self.resized_face_image is not None:
            face_rgb = cv2.cvtColor(self.resized_face_image, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            self.face_photo = ImageTk.PhotoImage(image=face_pil)
            self.face_label.config(image=self.face_photo)
    
    def update_blur_info(self):
        """Update blur information display"""
        stage = self.blur_stages[self.current_blur_stage]
        self.blur_info_label.config(
            text=f"{stage['name']} | Kernel: {stage['kernel']}x{stage['kernel']} | Sigma: {stage['sigma']}",
            fg=stage['color']
        )
    
    def update_stage_indicators(self):
        """Update stage indicator colors"""
        for i, stage in enumerate(self.blur_stages):
            dot_color = stage['color'] if i == self.current_blur_stage else "#cccccc"
            self.stage_dots[i].config(fg=dot_color)
            stage_name_color = "black" if i == self.current_blur_stage else "#666666"
            self.stage_names[i].config(fg=stage_name_color)
    
    def resize_to_exact_size(self, img, target_size):
        """Resize image to exact target size, maintaining aspect ratio with padding if needed"""
        h, w = img.shape[:2]
        target_w, target_h = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize using cv2.resize with bicubic interpolation
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # Create canvas and place resized image in center
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    
    def save_images(self):
        """Save all three output images"""
        if self.blurred_image is None or self.resized_face_image is None:
            messagebox.showerror("Error", "No images to save!")
            return
        
        original_path = filedialog.asksaveasfilename(
            title="Save Original Image",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
        )
        
        if original_path:
            cv2.imwrite(original_path, self.original_image)
            print(f"Original image saved to: {original_path}")
        
        blur_path = filedialog.asksaveasfilename(
            title="Save Blurred Image",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
        )
        
        if blur_path:
            cv2.imwrite(blur_path, self.blurred_image)
            print(f"Blurred image saved to: {blur_path}")
        
        face_path = filedialog.asksaveasfilename(
            title="Save Resized Face Image",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
        )
        
        if face_path:
            cv2.imwrite(face_path, self.resized_face_image)
            print(f"Face image saved to: {face_path}")
        
        if original_path or blur_path or face_path:
            messagebox.showinfo("Success", "Images saved successfully!")
    

    
    def create_gui(self):
        """Create the main GUI window with perfect alignment using grid"""
        self.main_window = Toplevel(self.root)
        self.main_window.title("Gaussian Blur and Face Scaling")
        self.main_window.geometry("1400x900")
        
        # Configure grid weights for main window
        self.main_window.grid_rowconfigure(0, weight=0)  # Title
        self.main_window.grid_rowconfigure(1, weight=1)  # Images (expands)
        self.main_window.grid_rowconfigure(2, weight=0)  # Spacer
        self.main_window.grid_rowconfigure(3, weight=0)  # Controls (fixed)
        self.main_window.grid_rowconfigure(4, weight=1)  # Bottom spacer (expands)
        self.main_window.grid_columnconfigure(0, weight=1)
        
        # ============================================
        # TITLE (Row 0)
        # ============================================
        title_label = Label(self.main_window, text="Gaussian Blur and Face Scaling", 
                        font=("Arial", 22, "bold"))
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="n")
        
        # ============================================
        # IMAGE ROW (Row 1)
        # ============================================
        # Create a frame specifically for the three images
        image_row_frame = Frame(self.main_window)
        image_row_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 0))
        
        # Configure image row frame grid (1 row, 3 columns)
        image_row_frame.grid_rowconfigure(0, weight=1)
        image_row_frame.grid_columnconfigure(0, weight=1, uniform="image_col")
        image_row_frame.grid_columnconfigure(1, weight=1, uniform="image_col")
        image_row_frame.grid_columnconfigure(2, weight=1, uniform="image_col")
        
        # ===== COLUMN 0: ORIGINAL IMAGE =====
        col0 = Frame(image_row_frame, bd=1, relief="solid", padx=5, pady=5)
        col0.grid(row=0, column=0, sticky="nsew", padx=5)
        
        # Original title
        original_title = Label(col0, text="Original Image", 
                            font=("Arial", 14, "bold"))
        original_title.grid(row=0, column=0, pady=(0, 5), sticky="n")
        
        # Original image display
        original_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        original_resized = self.resize_to_exact_size(original_rgb, self.image_display_size)
        original_pil = Image.fromarray(original_resized)
        self.original_photo = ImageTk.PhotoImage(image=original_pil)
        
        self.original_label = Label(col0, image=self.original_photo, 
                                relief="solid", bd=2)
        self.original_label.grid(row=1, column=0, pady=(0, 5), sticky="n")
        
        # Original info
        original_info = Label(col0, 
                            text=f"Original Size: {self.original_image.shape[1]}x{self.original_image.shape[0]}",
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
        blurred_rgb = cv2.cvtColor(self.blurred_image, cv2.COLOR_BGR2RGB)
        blurred_resized = self.resize_to_exact_size(blurred_rgb, self.image_display_size)
        blurred_pil = Image.fromarray(blurred_resized)
        self.blurred_photo = ImageTk.PhotoImage(image=blurred_pil)
        
        self.blurred_label = Label(col1, image=self.blurred_photo, 
                                relief="solid", bd=2)
        self.blurred_label.grid(row=1, column=0, pady=(0, 5), sticky="n")
        
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
        face_rgb = cv2.cvtColor(self.resized_face_image, cv2.COLOR_BGR2RGB)
        face_pil = Image.fromarray(face_rgb)
        self.face_photo = ImageTk.PhotoImage(image=face_pil)
        
        self.face_label = Label(col2, image=self.face_photo, 
                            relief="solid", bd=2)
        self.face_label.grid(row=1, column=0, pady=(0, 5), sticky="n")
        
        # Face size info
        size_label = Label(col2, 
                        text=f"Size: {self.face_display_size[0]}x{self.face_display_size[1]} pixels",
                        font=("Arial", 10))
        size_label.grid(row=2, column=0, pady=5, sticky="n")
        
        # Face navigation (only if multiple faces)
        if len(self.extracted_faces) > 1:
            # Face counter label
            self.face_nav_label = Label(col2, 
                                    text=f"Face {self.current_face_index + 1} of {len(self.extracted_faces)}",
                                    font=("Arial", 10, "bold"), fg="blue")
            self.face_nav_label.grid(row=3, column=0, pady=(5, 2), sticky="n")
            
            # Navigation buttons frame - positioned to avoid overlap
            nav_frame = Frame(col2)
            nav_frame.grid(row=4, column=0, pady=(0, 5), sticky="n")
            
            # Small blue arrow buttons
            prev_btn = Button(nav_frame, text="◀", 
                            command=lambda: self.navigate_faces("prev"),
                            font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                            width=3, height=1, relief="flat", bd=1)
            prev_btn.pack(side="left", padx=2)
            
            next_btn = Button(nav_frame, text="▶", 
                            command=lambda: self.navigate_faces("next"),
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
        
        # ============================================
        # SPACER (Row 2) - To lower the adjuster bar
        # ============================================
        spacer_frame = Frame(self.main_window, height=40)  # Increased spacer to lower adjuster
        spacer_frame.grid(row=2, column=0, sticky="ew")
        spacer_frame.grid_propagate(False)  # Keep fixed height
        
        # ============================================
        # CONTROL SECTION (Row 3) - Only adjuster remains
        # ============================================
        control_section = Frame(self.main_window)
        control_section.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Create a container for centering the controls
        control_container = Frame(control_section)
        control_container.pack(expand=True)  # Center horizontally
        
        # Control title
        control_title = Label(control_container, text="Gaussian Blur Control", 
                            font=("Arial", 14, "bold"))
        control_title.pack(pady=(0, 10))
        
        # Current blur info
        current_stage = self.blur_stages[self.current_blur_stage]
        self.blur_info_label = Label(control_container,
                                    text=f"{current_stage['name']} | Kernel: {current_stage['kernel']}x{current_stage['kernel']} | Sigma: {current_stage['sigma']}",
                                    font=("Arial", 11, "bold"),
                                    fg=current_stage['color'])
        self.blur_info_label.pack(pady=(0, 15))
        
        # Slider frame
        slider_frame = Frame(control_container)
        slider_frame.pack(pady=5)
        
        # Min label
        min_label = Label(slider_frame, text="Light", font=("Arial", 9, "bold"))
        min_label.pack(side="left", padx=5)
        
        # Slider
        self.slider = Scale(slider_frame, from_=0, to=100, orient=HORIZONTAL,
                        length=350, showvalue=False,
                        command=self.update_blur_from_slider,
                        sliderlength=20, troughcolor="#e0e0e0")
        self.slider.set(current_stage["slider_value"])
        self.slider.pack(side="left", padx=15)
        
        # Max label
        max_label = Label(slider_frame, text="Heavy", font=("Arial", 9, "bold"))
        max_label.pack(side="left", padx=5)
        
        # Stage indicators (dots only, no descriptions)
        indicator_frame = Frame(control_container)
        indicator_frame.pack(pady=10)
        
        self.stage_dots = []
        
        for i, stage in enumerate(self.blur_stages):
            indicator_item = Frame(indicator_frame)
            indicator_item.pack(side="left", padx=40)
            
            # Dot indicator
            dot_color = stage['color'] if i == self.current_blur_stage else "#cccccc"
            dot = Label(indicator_item, text="●", font=("Arial", 20), fg=dot_color)
            dot.pack()
            
            # Stage name (small label under dot)
            name_color = "black" if i == self.current_blur_stage else "#666666"
            stage_name = Label(indicator_item, text=stage['name'], 
                            font=("Arial", 9, "bold"), fg=name_color)
            stage_name.pack()
            
            self.stage_dots.append(dot)
        
        # ============================================
        # BOTTOM SPACER (Row 4) - Takes up remaining space
        # ============================================
        bottom_spacer = Frame(self.main_window)
        bottom_spacer.grid(row=4, column=0, sticky="nsew")
        
        # Start the main loop
        self.main_window.mainloop()
    
    def save_current_face(self):
        """Save the currently displayed face image"""
        if self.resized_face_image is None:
            messagebox.showerror("Error", "No face image to save!")
            return
        
        face_path = filedialog.asksaveasfilename(
            title=f"Save Face {self.current_face_index + 1}",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
        )
        
        if face_path:
            cv2.imwrite(face_path, self.resized_face_image)
            print(f"Face {self.current_face_index + 1} saved to: {face_path}")
            messagebox.showinfo("Success", f"Face {self.current_face_index + 1} saved successfully!")
    
    def reload_image(self):
        """Reload with a new image"""
        self.main_window.destroy()
        self.__init__()

# Run the application
if __name__ == "__main__":
    print("Starting Gaussian Blur and Face Scaling Application")
    print("Feature: All faces extracted with small arrow navigation buttons")
    print("All output frames are perfectly aligned horizontally")
    app = FaceBlurAndScaleApp()