import mediapipe as mp
import cv2
import numpy as np
from typing import List, Tuple, Optional

class FaceDetector:
    def __init__(self, min_detection_confidence: float = 0.5):
        """Initialize MediaPipe Face Detection with BlazeFace"""
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize the face detection model
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for short-range (2m), 1 for full-range (5m)
            min_detection_confidence=min_detection_confidence
        )
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in image and return bounding boxes
        Returns: List of (x, y, width, height) tuples
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.face_detection.process(rgb_image)
        
        faces = []
        if results.detections:
            h, w, _ = image.shape
            for detection in results.detections:
                # Extract bounding box
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                faces.append((x, y, width, height))
        
        return faces
    
    def extract_face_roi(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract face region of interest from image"""
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]




import torch
import torch.nn as nn
import torchvision.transforms as transforms
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class MobileFaceNet(nn.Module):
    """Simplified MobileFaceNet implementation"""
    def __init__(self, embedding_size=128):
        super(MobileFaceNet, self).__init__()
        # This is a simplified version - you'd load the actual pretrained model
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.classifier = nn.Linear(64, embedding_size)
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return nn.functional.normalize(x, p=2, dim=1)

class FaceRecognizer:
    def __init__(self, model_path: str = None, threshold: float = 0.6):
        """Initialize face recognition model"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.threshold = threshold
        
        # Load pretrained model (you'd load actual MobileFaceNet weights here)
        self.model = MobileFaceNet()
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        
        # Employee embeddings database
        self.employee_embeddings = {}
        self.load_employee_database()
    
    def extract_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """Extract face embedding from cropped face image"""
        # Preprocess image
        if len(face_image.shape) == 3:
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        input_tensor = self.transform(face_image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            embedding = self.model(input_tensor)
            return embedding.cpu().numpy().flatten()
    
    def add_employee(self, employee_id: str, face_image: np.ndarray):
        """Add new employee to the recognition database"""
        embedding = self.extract_embedding(face_image)
        self.employee_embeddings[employee_id] = embedding
        self.save_employee_database()
    
    def recognize_face(self, face_image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Recognize face and return employee_id and confidence score
        Returns: (employee_id, confidence) or (None, 0.0) if not recognized
        """
        if not self.employee_embeddings:
            return None, 0.0
        
        # Extract embedding for input face
        input_embedding = self.extract_embedding(face_image).reshape(1, -1)
        
        best_match = None
        best_score = 0.0
        
        # Compare with all employee embeddings
        for employee_id, stored_embedding in self.employee_embeddings.items():
            stored_embedding = stored_embedding.reshape(1, -1)
            similarity = cosine_similarity(input_embedding, stored_embedding)[0][0]
            
            if similarity > best_score:
                best_score = similarity
                best_match = employee_id
        
        # Return match if above threshold
        if best_score >= self.threshold:
            return best_match, best_score
        else:
            return None, best_score
    
    def save_employee_database(self, filepath: str = "employee_embeddings.pkl"):
        """Save employee embeddings to file"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.employee_embeddings, f)
    
    def load_employee_database(self, filepath: str = "employee_embeddings.pkl"):
        """Load employee embeddings from file"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.employee_embeddings = pickle.load(f)


from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

app = FastAPI(title="Face Recognition Microservice", version="1.0.0")

# Initialize components
face_detector = FaceDetector()
face_recognizer = FaceRecognizer()

@app.post("/detect-faces")
async def detect_faces_endpoint(file: UploadFile = File(...)):
    """Detect faces in uploaded image"""
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect faces
        faces = face_detector.detect_faces(image)
        
        return JSONResponse({
            "status": "success",
            "faces_detected": len(faces),
            "bounding_boxes": faces
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recognize-face")
async def recognize_face_endpoint(file: UploadFile = File(...)):
    """Recognize face in uploaded image"""
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect faces
        faces = face_detector.detect_faces(image)
        
        if not faces:
            return JSONResponse({
                "status": "no_face_detected",
                "employee_id": None,
                "confidence": 0.0
            })
        
        # Use the largest face (assuming it's the primary subject)
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        face_roi = face_detector.extract_face_roi(image, largest_face)
        
        # Recognize face
        employee_id, confidence = face_recognizer.recognize_face(face_roi)
        
        return JSONResponse({
            "status": "success",
            "employee_id": employee_id,
            "confidence": float(confidence),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-employee")
async def add_employee_endpoint(employee_id: str, file: UploadFile = File(...)):
    """Add new employee to recognition database"""
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect faces
        faces = face_detector.detect_faces(image)
        
        if not faces:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        # Use the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        face_roi = face_detector.extract_face_roi(image, largest_face)
        
        # Add employee
        face_recognizer.add_employee(employee_id, face_roi)
        
        return JSONResponse({
            "status": "success",
            "message": f"Employee {employee_id} added successfully"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

