import cv2
from mtcnn import MTCNN


class FaceDetector:
    def __init__(self):
        self.detector = MTCNN()
    
    def detect_faces(self, image, app):
        """Detect faces in the image"""
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            app.faces = self.detector.detect_faces(rgb_image)
            
            if len(app.faces) == 0:
                return False
            
            print(f"Detected {len(app.faces)} face(s)")
            return True
        except Exception as e:
            print(f"Face detection error: {e}")
            return False
    
    def extract_all_faces(self, image, faces):
        """Extract all faces from the image and store them in temporary storage"""
        extracted_faces = []
        
        for i, face in enumerate(faces):
            x, y, w, h = face['box']
            
            padding = int(min(w, h) * 0.2)
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            face_image = image[y:y+h, x:x+w].copy()
            
            extracted_faces.append({
                'image': face_image,
                'box': (x, y, w, h),
                'confidence': face['confidence'],
                'index': i
            })
        
        return extracted_faces