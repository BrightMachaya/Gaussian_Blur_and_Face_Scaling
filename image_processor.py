import numpy as np
import math


class ImageProcessor:
    @staticmethod
    def create_gaussian_kernel(kernel_size, sigma):
        """Create a Gaussian kernel manually"""
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
        center = kernel_size // 2
        
        for i in range(kernel_size):
            for j in range(kernel_size):
                x = i - center
                y = j - center
                kernel[i, j] = (1.0 / (2 * math.pi * sigma ** 2)) * \
                              math.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
        
        kernel /= kernel.sum()
        
        return kernel
    
    @staticmethod
    def apply_gaussian_blur_manual(image, kernel_size, sigma):
        """Apply Gaussian blur using manual convolution"""
        kernel = ImageProcessor.create_gaussian_kernel(kernel_size, sigma)
        height, width = image.shape[:2]
        blurred = np.zeros_like(image, dtype=np.float32)
        pad = kernel_size // 2
        padded_image = np.pad(image, ((pad, pad), (pad, pad), (0, 0)), mode='reflect')
        
        for c in range(3):
            for i in range(height):
                for j in range(width):
                    region = padded_image[i:i+kernel_size, j:j+kernel_size, c]
                    blurred[i, j, c] = np.sum(region * kernel)
        
        blurred = np.clip(blurred, 0, 255).astype(np.uint8)
        return blurred
    
    @staticmethod
    def manual_resize_bicubic(image, target_size):
        """Manual bicubic interpolation for image resizing"""
        src_h, src_w = image.shape[:2]
        dst_h, dst_w = target_size[1], target_size[0]
        resized = np.zeros((dst_h, dst_w, 3), dtype=np.uint8)
        scale_x = src_w / dst_w
        scale_y = src_h / dst_h
        
        def cubic_interpolate(p, x):
            return p[1] + 0.5 * x * (p[2] - p[0] + 
                   x * (2.0 * p[0] - 5.0 * p[1] + 4.0 * p[2] - p[3] + 
                   x * (3.0 * (p[1] - p[2]) + p[3] - p[0])))
        
        for y in range(dst_h):
            for x in range(dst_w):
                src_x = x * scale_x
                src_y = y * scale_y
                x1 = int(src_x)
                y1 = int(src_y)
                
                for c in range(3):
                    values = np.zeros((4, 4), dtype=np.float32)
                    
                    for i in range(-1, 3):
                        for j in range(-1, 3):
                            xi = max(0, min(src_w - 1, x1 + i))
                            yj = max(0, min(src_h - 1, y1 + j))
                            values[i+1, j+1] = image[yj, xi, c]
                    
                    x_interp = src_x - x1
                    arr = []
                    for i in range(4):
                        arr.append(cubic_interpolate(values[i, :], x_interp))
                    
                    y_interp = src_y - y1
                    final_value = cubic_interpolate(arr, y_interp)
                    resized[y, x, c] = np.clip(final_value, 0, 255)
        
        return resized
    
    def resize_to_exact_size(self, img, target_size):
        """Resize image to exact target size, maintaining aspect ratio with padding if needed"""
        h, w = img.shape[:2]
        target_w, target_h = target_size
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = self.manual_resize_bicubic(img, (new_w, new_h))
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        return canvas