import cv2
import numpy as np
import math
from tkinter import Tk, messagebox, Toplevel
from PIL import Image, ImageTk

from face_detector import FaceDetector
from image_processor import ImageProcessor
from gui_builder import GUIBuilder


class FaceBlurAndScaleApp:
    def __init__(self):
        self.root = Tk()
        self.root.withdraw()  # Hide main window
        
        # Initialize components
        self.face_detector = FaceDetector()
        self.image_processor = ImageProcessor()
        self.gui_builder = GUIBuilder(self)
        
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
        from tkinter import filedialog
        
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
        return self.face_detector.detect_faces(self.original_image, self)
    
    def extract_all_faces(self):
        """Extract all faces from the image and store them in temporary storage"""
        self.extracted_faces = self.face_detector.extract_all_faces(self.original_image, self.faces)
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
    
    def create_gaussian_kernel(self, kernel_size, sigma):
        """Create a Gaussian kernel manually"""
        return self.image_processor.create_gaussian_kernel(kernel_size, sigma)
    
    def apply_gaussian_blur_manual(self, image, kernel_size, sigma):
        """Apply Gaussian blur using manual convolution"""
        return self.image_processor.apply_gaussian_blur_manual(image, kernel_size, sigma)
    
    def manual_resize_bicubic(self, image, target_size):
        """Manual bicubic interpolation for image resizing"""
        return self.image_processor.manual_resize_bicubic(image, target_size)
    
    def resize_face_to_display(self):
        """Resize face image to fit display frame using manual bicubic interpolation"""
        if self.face_image is None:
            return
        
        target_width, target_height = self.face_display_size
        self.resized_face_image = self.manual_resize_bicubic(
            self.face_image, 
            (target_width, target_height)
        )
        
        print(f"Face resized to: {target_width}x{target_height} pixels")
    
    def apply_gaussian_blur(self, image, kernel_size, sigma):
        """Apply Gaussian blur using manual implementation"""
        blurred = self.apply_gaussian_blur_manual(image, kernel_size, sigma)
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
        return self.image_processor.resize_to_exact_size(img, target_size)
    
    def save_images(self):
        """Save all three output images"""
        from tkinter import filedialog
        
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
        self.gui_builder.create_main_window(self.main_window)
    
    def save_current_face(self):
        """Save the currently displayed face image"""
        from tkinter import filedialog
        
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