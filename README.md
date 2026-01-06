# Gaussian Blur and Face Scaling Application

A desktop application that applies Gaussian blur to images and extracts/resizes faces with advanced interpolation techniques.

## Features

- **Multi-Face Detection**: Automatically detects and extracts multiple faces from images
- **Three-Stage Gaussian Blur**: Adjustable blur intensity with visual feedback
- **High-Quality Face Resizing**: Manual bicubic interpolation for superior image quality
- **Face Navigation**: Browse through multiple detected faces with arrow controls
- **Save Capabilities**: Export original, blurred, and resized face images separately
- **Perfect Alignment**: Clean, responsive GUI with perfectly aligned image displays

## Algorithms Used

### 1. **MTCNN Face Detection**
- **What it does**: Detects human faces with bounding boxes and confidence scores
- **Advantages**: 
  - High accuracy even with challenging lighting/angles
  - Returns facial landmarks (eyes, nose, mouth) for precise extraction
  - Handles multiple faces in a single image

### 2. **Manual Gaussian Blur**
- **What it does**: Applies blur by convolving image with Gaussian kernel
- **Implementation**: Manual convolution without OpenCV's built-in functions
- **Advantages**:
  - **Educational value**: Shows how Gaussian blur actually works mathematically
  - **Custom control**: Precise control over kernel size and sigma values
  - **Three preset stages**: Light, Medium, Heavy blur for different privacy levels

### 3. **Manual Bicubic Interpolation**
- **What it does**: Resizes images using cubic polynomial interpolation
- **Implementation**: Custom algorithm without PIL/OpenCV resize functions
- **Advantages**:
  - **Superior quality**: Smoother results than bilinear/nearest-neighbor methods
  - **Reduced artifacts**: Minimizes jagged edges and blurring in resized images
  - **Mathematical transparency**: Demonstrates interpolation fundamentals

### 4. **Face Extraction with Padding**
- **What it does**: Extracts faces with 20% padding around detected boxes
- **Advantages**:
  - **Better framing**: Includes hair and chin area, not just facial features
  - **Consistent output**: Uniform padding regardless of face size/orientation
  - **Natural appearance**: More aesthetically pleasing than tight cropping

## Why These Algorithms?

### Educational Perspective
The manual implementations (Gaussian blur and bicubic interpolation) serve as excellent learning tools. Unlike using library functions as "black boxes," these implementations:
- Demonstrate the underlying mathematics
- Show computational complexity trade-offs
- Provide insight into image processing fundamentals

### Practical Advantages
- **Privacy Protection**: Gaussian blur allows adjustable anonymization
- **Quality Preservation**: Bicubic interpolation maintains face clarity during resizing
- **Flexibility**: Three distinct blur levels suit different privacy needs

## Installation

### Requirements
- python 3 or higher
- MTCNN 
- Numpy

1. Clone the repository:
```bash
git clone https://github.com/BrightMachaya/Gaussian_Blur_and_Face_Scaling.git
cd Gaussian_Blur_and_Face_Scaling
python ./app.py

```


* If you find this project useful, please give it a star ⭐ *
