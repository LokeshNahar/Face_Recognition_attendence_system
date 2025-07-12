import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector

class PgVectorDB:
    def __init__(self, conn_str):
        self.conn = psycopg2.connect(conn_str)
        register_vector(self.conn)
        self.ensure_tables()
    
    def ensure_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;
                CREATE TABLE IF NOT EXISTS employees (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    embedding vector(128), -- or vector(2622)
                    registered_date TIMESTAMP,
                    num_samples INTEGER,
                    model VARCHAR,
                    image BYTEA
                );
                CREATE TABLE IF NOT EXISTS employee_faces (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR REFERENCES employees(id),
                    pose VARCHAR,
                    embedding vector(128),
                    image BYTEA,
                    captured_at TIMESTAMP
                );
            """)
            self.conn.commit()

    def upsert_employee(self, employee_id, name, embedding, registered_date, num_samples, model, image_bytes):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employees (id, name, embedding, registered_date, num_samples, model, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    embedding = EXCLUDED.embedding,
                    registered_date = EXCLUDED.registered_date,
                    num_samples = EXCLUDED.num_samples,
                    model = EXCLUDED.model,
                    image = EXCLUDED.image
            """, (employee_id, name, embedding.tolist(), registered_date, num_samples, model, image_bytes))
            self.conn.commit()

    def insert_employee_face(self, employee_id, pose, embedding, image_bytes, captured_at):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employee_faces (employee_id, pose, embedding, image, captured_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (employee_id, pose, embedding.tolist(), image_bytes, captured_at))
            self.conn.commit()

    def fetch_all_employees(self):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM employees")
            return cur.fetchall()
    
    def fetch_employee_by_id(self, employee_id):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM employees WHERE id=%s", (employee_id,))
            return cur.fetchone()
    
    def fetch_faces_by_employee(self, employee_id):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM employee_faces WHERE employee_id=%s", (employee_id,))
            return cur.fetchall()

    def delete_employee(self, employee_id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM employee_faces WHERE employee_id=%s", (employee_id,))
            cur.execute("DELETE FROM employees WHERE id=%s", (employee_id,))
            self.conn.commit()

    def pgvector_search(self, embedding, top_k=1):
        # Ensure embedding is np.float32 or np.float64
        embedding = np.asarray(embedding, dtype=np.float32)
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT id, name, embedding, 1 - (embedding <=> %s) as similarity
                FROM employees
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (embedding, embedding, top_k))
            return cur.fetchall()
        
        
    def record_attendance(self, employee_id, name):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO attendance (employee_id, name, timestamp) VALUES (%s, %s, %s)",
                (employee_id, name, datetime.now())
            )
            self.conn.commit()


import cv2
import numpy as np
import os
import mediapipe as mp
from typing import List, Tuple, Optional, Dict
import json
from datetime import datetime



class FaceDetector:
    def __init__(self, min_detection_confidence: float = 0.5):
        """Initialize MediaPipe Face Detection with BlazeFace"""
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=min_detection_confidence
        )
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces and return bounding boxes"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        faces = []
        if results.detections:
            h, w, _ = image.shape
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Ensure bounding box is within image bounds
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)
                
                faces.append((x, y, width, height))
        
        return faces
    
    def extract_face_roi(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract face region of interest"""
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]


import cv2
import numpy as np
import mediapipe as mp
import math
from typing import Tuple, Optional

import cv2
import numpy as np
import mediapipe as mp
import math
from typing import Tuple, Optional, List
from collections import deque

class ImprovedFacePoseDetector:
    def __init__(self):
        """Initialize enhanced MediaPipe Face Mesh for robust pose detection"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,  # Increased for better stability
            min_tracking_confidence=0.7
        )
        
        # Enhanced landmark indices for better pose estimation
        self.nose_tip = 1
        self.nose_bridge = 168
        self.chin = 18
        self.left_eye_corner = 33
        self.right_eye_corner = 263
        self.left_eye_center = 468
        self.right_eye_center = 473
        self.left_mouth_corner = 61
        self.right_mouth_corner = 291
        self.forehead_center = 9
        
        # 3D model points for solvePnP (in mm)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),        # Nose tip
            (0.0, -330.0, -65.0),   # Chin
            (-225.0, 170.0, -135.0), # Left eye corner
            (225.0, 170.0, -135.0),  # Right eye corner
            (-150.0, -150.0, -125.0), # Left mouth corner
            (150.0, -150.0, -125.0)   # Right mouth corner
        ], dtype=np.float64)
        
        # Camera parameters (approximate values - should be calibrated for production)
        self.camera_matrix = None
        self.dist_coeffs = np.zeros((4, 1))
        
        # Pose history for smoothing
        self.pose_history = deque(maxlen=5)
        self.confidence_history = deque(maxlen=5)
        
    def _initialize_camera_matrix(self, img_width: int, img_height: int):
        """Initialize camera matrix with image dimensions"""
        focal_length = img_width
        center = (img_width / 2, img_height / 2)
        self.camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
    
    def detect_face_pose(self, image: np.ndarray) -> Tuple[str, float, bool]:
        """
        Enhanced face pose detection with multiple methods
        Returns: (pose_direction, confidence, face_detected)
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return "no_face", 0.0, False
        
        face_landmarks = results.multi_face_landmarks[0]
        h, w, _ = image.shape
        
        # Initialize camera matrix if not done
        if self.camera_matrix is None:
            self._initialize_camera_matrix(w, h)
        
        # Method 1: Enhanced 2D landmark analysis
        pose_2d, confidence_2d = self._analyze_2d_landmarks(face_landmarks, w, h)
        
        # Method 2: 3D pose estimation using solvePnP
        pose_3d, confidence_3d = self._estimate_3d_pose(face_landmarks, w, h)
        
        # Method 3: Geometric ratios analysis
        pose_geo, confidence_geo = self._analyze_geometric_ratios(face_landmarks, w, h)
        
        # Combine results with weighted voting
        final_pose, final_confidence = self._combine_pose_estimates(
            [(pose_2d, confidence_2d), (pose_3d, confidence_3d), (pose_geo, confidence_geo)]
        )
        
        # Apply temporal smoothing
        smoothed_pose, smoothed_confidence = self._apply_temporal_smoothing(
            final_pose, final_confidence
        )
        
        return smoothed_pose, smoothed_confidence, True
    
    def _analyze_2d_landmarks(self, face_landmarks, w: int, h: int) -> Tuple[str, float]:
        """Enhanced 2D landmark analysis with multiple reference points"""
        # Get key landmark coordinates
        nose_tip = face_landmarks.landmark[self.nose_tip]
        nose_bridge = face_landmarks.landmark[self.nose_bridge]
        left_eye = face_landmarks.landmark[self.left_eye_corner]
        right_eye = face_landmarks.landmark[self.right_eye_corner]
        chin = face_landmarks.landmark[self.chin]
        
        # Convert to pixel coordinates
        nose_tip_x = int(nose_tip.x * w)
        nose_bridge_x = int(nose_bridge.x * w)
        left_eye_x = int(left_eye.x * w)
        right_eye_x = int(right_eye.x * w)
        chin_x = int(chin.x * w)
        
        # Calculate face center using multiple reference points
        face_center_x = (left_eye_x + right_eye_x) // 2
        face_width = abs(right_eye_x - left_eye_x)
        
        if face_width == 0:
            return "front", 0.0
        
        # Multiple deviation calculations
        nose_deviation = nose_tip_x - face_center_x
        bridge_deviation = nose_bridge_x - face_center_x
        chin_deviation = chin_x - face_center_x
        
        # Weighted average of deviations
        weighted_deviation = (nose_deviation * 0.5 + bridge_deviation * 0.3 + chin_deviation * 0.2)
        deviation_ratio = weighted_deviation / face_width
        
        # Improved thresholds based on research
        if deviation_ratio < -0.12:  # More lenient threshold
            pose = "left"
            confidence = min(abs(deviation_ratio) * 3, 1.0)
        elif deviation_ratio > 0.12:
            pose = "right"
            confidence = min(abs(deviation_ratio) * 3, 1.0)
        else:
            pose = "front"
            # Higher confidence for front pose when deviation is small
            confidence = max(0.7, 1.0 - abs(deviation_ratio) * 5)
        
        return pose, confidence
    
    def _estimate_3d_pose(self, face_landmarks, w: int, h: int) -> Tuple[str, float]:
        """3D pose estimation using solvePnP for more accurate results"""
        try:
            # Extract 2D image points
            image_points = np.array([
                (face_landmarks.landmark[self.nose_tip].x * w, 
                 face_landmarks.landmark[self.nose_tip].y * h),
                (face_landmarks.landmark[self.chin].x * w, 
                 face_landmarks.landmark[self.chin].y * h),
                (face_landmarks.landmark[self.left_eye_corner].x * w, 
                 face_landmarks.landmark[self.left_eye_corner].y * h),
                (face_landmarks.landmark[self.right_eye_corner].x * w, 
                 face_landmarks.landmark[self.right_eye_corner].y * h),
                (face_landmarks.landmark[self.left_mouth_corner].x * w, 
                 face_landmarks.landmark[self.left_mouth_corner].y * h),
                (face_landmarks.landmark[self.right_mouth_corner].x * w, 
                 face_landmarks.landmark[self.right_mouth_corner].y * h)
            ], dtype=np.float64)
            
            # Solve PnP
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points, image_points, self.camera_matrix, self.dist_coeffs
            )
            
            if not success:
                return "front", 0.5
            
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # Extract Euler angles
            yaw = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
            yaw_degrees = math.degrees(yaw)
            
            # Determine pose based on yaw angle
            if yaw_degrees < -15:
                pose = "left"
                confidence = min(abs(yaw_degrees) / 45, 1.0)
            elif yaw_degrees > 15:
                pose = "right"
                confidence = min(abs(yaw_degrees) / 45, 1.0)
            else:
                pose = "front"
                confidence = max(0.8, 1.0 - abs(yaw_degrees) / 30)
            
            return pose, confidence
            
        except Exception as e:
            return "front", 0.5
    
    def _analyze_geometric_ratios(self, face_landmarks, w: int, h: int) -> Tuple[str, float]:
        """Analyze geometric ratios for pose detection"""
        # Get landmark coordinates
        left_eye = face_landmarks.landmark[self.left_eye_corner]
        right_eye = face_landmarks.landmark[self.right_eye_corner]
        nose_tip = face_landmarks.landmark[self.nose_tip]
        left_mouth = face_landmarks.landmark[self.left_mouth_corner]
        right_mouth = face_landmarks.landmark[self.right_mouth_corner]
        
        # Calculate distances
        left_eye_nose = math.sqrt((left_eye.x - nose_tip.x)**2 + (left_eye.y - nose_tip.y)**2)
        right_eye_nose = math.sqrt((right_eye.x - nose_tip.x)**2 + (right_eye.y - nose_tip.y)**2)
        left_mouth_nose = math.sqrt((left_mouth.x - nose_tip.x)**2 + (left_mouth.y - nose_tip.y)**2)
        right_mouth_nose = math.sqrt((right_mouth.x - nose_tip.x)**2 + (right_mouth.y - nose_tip.y)**2)
        
        # Calculate asymmetry ratios
        eye_ratio = left_eye_nose / (right_eye_nose + 1e-6)
        mouth_ratio = left_mouth_nose / (right_mouth_nose + 1e-6)
        
        # Combined ratio
        combined_ratio = (eye_ratio + mouth_ratio) / 2
        
        # Determine pose
        if combined_ratio < 0.85:
            pose = "right"
            confidence = min((1 - combined_ratio) * 2, 1.0)
        elif combined_ratio > 1.15:
            pose = "left"
            confidence = min((combined_ratio - 1) * 2, 1.0)
        else:
            pose = "front"
            confidence = max(0.75, 1.0 - abs(combined_ratio - 1) * 3)
        
        return pose, confidence
    
    def _combine_pose_estimates(self, estimates: List[Tuple[str, float]]) -> Tuple[str, float]:
        """Combine multiple pose estimates using weighted voting"""
        pose_votes = {"front": 0, "left": 0, "right": 0}
        total_confidence = 0
        
        for pose, confidence in estimates:
            pose_votes[pose] += confidence
            total_confidence += confidence
        
        # Find the pose with highest weighted vote
        best_pose = max(pose_votes, key=pose_votes.get)
        best_confidence = pose_votes[best_pose] / (total_confidence + 1e-6)
        
        return best_pose, min(best_confidence, 1.0)
    
    def _apply_temporal_smoothing(self, pose: str, confidence: float) -> Tuple[str, float]:
        """Apply temporal smoothing to reduce jittering"""
        self.pose_history.append(pose)
        self.confidence_history.append(confidence)
        
        if len(self.pose_history) < 3:
            return pose, confidence
        
        # Count pose occurrences in recent history
        pose_counts = {"front": 0, "left": 0, "right": 0}
        for p in self.pose_history:
            pose_counts[p] += 1
        
        # Use majority vote with confidence weighting
        avg_confidence = sum(self.confidence_history) / len(self.confidence_history)
        most_common_pose = max(pose_counts, key=pose_counts.get)
        
        # Only change pose if there's strong evidence
        if pose_counts[most_common_pose] >= len(self.pose_history) * 0.6:
            return most_common_pose, avg_confidence
        else:
            return pose, confidence
    
    def draw_pose_indicators(self, image: np.ndarray, pose: str, confidence: float) -> np.ndarray:
        """Enhanced pose indicators with confidence visualization"""
        # Draw pose text with confidence
        pose_text = f"Pose: {pose.upper()} ({confidence:.3f})"
        cv2.putText(image, pose_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw confidence bar
        bar_width = int(200 * confidence)
        cv2.rectangle(image, (10, 50), (10 + bar_width, 70), (0, 255, 0), -1)
        cv2.rectangle(image, (10, 50), (210, 70), (255, 255, 255), 2)
        
        # Draw pose-specific indicators
        h, w = image.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        if pose == "left":
            cv2.arrowedLine(image, (center_x, center_y), 
                           (center_x - 60, center_y), (0, 255, 0), 4)
        elif pose == "right":
            cv2.arrowedLine(image, (center_x, center_y), 
                           (center_x + 60, center_y), (0, 255, 0), 4)
        elif pose == "front":
            cv2.circle(image, (center_x, center_y), 40, (0, 255, 0), 4)
            cv2.putText(image, "FRONT", (center_x - 30, center_y + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return image


from deepface import DeepFace
import numpy as np
import cv2
import os
import json
from datetime import datetime
from typing import List, Optional, Tuple, Dict

class RealFaceRecognizer:
    def __init__(self, model_name: str = "Facenet", threshold: float = 0.7, db_conn_str="postgresql://loki:lokii@localhost/attendance_db"):
        """
        Initialize real face recognition using DeepFace model (Facenet or VGG-Face).
        model_name: "Facenet" or "VGG-Face" (case-insensitive).
        """
        # Validate model_name
        valid_models = ["Facenet", "VGG-Face"]
        model_name = model_name.strip().lower()
        self.model_name = (
            "Facenet" if model_name in ["facenet", "facenet512"] else "VGG-Face"
        )
        self.threshold = threshold
        # Load DeepFace model
        print(f"Loading DeepFace model: {self.model_name} ...")
        self.model = DeepFace.build_model(self.model_name)
        # Employee database
        self.employee_embeddings = {}
        self.employee_metadata = {}
        self.db = PgVectorDB(db_conn_str)
        self.model_name = "Facenet" if model_name.lower().startswith("facenet") else "VGG-Face"
        self.threshold = threshold

    def add_employee(self, employee_id: str, employee_name: str, face_images: List[np.ndarray]):
        embeddings = []
        for face_image in face_images:
            embedding = self.extract_embedding(face_image)
            if np.count_nonzero(embedding) > 0:
                embeddings.append(embedding)
        if embeddings:
            avg_embedding = np.mean(embeddings, axis=0)
            # Save representative image as first
            _, buffer = cv2.imencode('.jpg', face_images[0])
            image_bytes = buffer.tobytes()
            registered_date = datetime.now()
            self.db.upsert_employee(employee_id, employee_name, avg_embedding, registered_date, len(embeddings), self.model_name, image_bytes)
            for pose, img in zip(['front']*len(embeddings), face_images):  # TODO: Use actual pose if you have it
                emb = self.extract_embedding(img)
                _, buf = cv2.imencode('.jpg', img)
                self.db.insert_employee_face(employee_id, pose, emb, buf.tobytes(), registered_date)
            print(f"Added employee {employee_name} (ID: {employee_id}) with {len(embeddings)} face samples")
            return True
        return False

    def recognize_face(self, face_image: np.ndarray) -> Tuple[Optional[str], Optional[str], float]:
        input_embedding = self.extract_embedding(face_image)
        results = self.db.pgvector_search(input_embedding, top_k=1)
        if results and results[0]['similarity'] >= self.threshold:
            r = results[0]
            return r['id'], r['name'], float(r['similarity'])
        return None, None, 0.0

    def remove_employee(self, employee_id: str) -> bool:
        self.db.delete_employee(employee_id)
        return True

    def list_employees(self) -> Dict:
        rows = self.db.fetch_all_employees()
        return {
            row['id']: {
                "name": row['name'],
                "registered_date": str(row['registered_date']),
                "num_samples": row['num_samples'],
                "model": row['model']
            } for row in rows
        }
                
    def extract_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract face embedding using DeepFace and the selected model.
        """
        try:
            # Pass numpy array as img_path
            embedding_objs = DeepFace.represent(
                img_path=face_image,   # <-- THIS IS THE FIX
                model_name=self.model_name,
                # model=self.model,
                enforce_detection=False,
                detector_backend="skip"
            )
            # DeepFace.represent returns a list of dicts; get the first embedding
            embedding = embedding_objs[0]["embedding"]
            return np.array(embedding)
        except Exception as e:
            print(f"DeepFace embedding extraction failed: {e}")
            return np.zeros((2622 if self.model_name == "VGG-Face" else 128,), dtype=np.float32)

import time
from datetime import datetime
import os
import json
import pickle


class MultiPoseRegistrationApp:
    def __init__(self):
        self.face_detector = FaceDetector()
        self.face_recognizer = RealFaceRecognizer()
        self.pose_detector = ImprovedFacePoseDetector()

        os.makedirs("employee_photos", exist_ok=True)
        os.makedirs("temp_captures", exist_ok=True)

        # Now we need a dict for multiple images per pose
        self.required_poses = {'front': 20, 'left': 3, 'right': 3}
        self.min_confidence = 0.6
        self.capture_delay = 0.1  # Faster for more images

    def guided_pose_capture(self, employee_id: str, employee_name: str) -> bool:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return False

        captured_poses = {pose: [] for pose in self.required_poses}
        pose_names = list(self.required_poses.keys())
        pose_index = 0
        photo_counts = {pose: 0 for pose in self.required_poses}
        pose_start_time = None
        countdown_active = False

        print(f"\n=== Multi-Pose Registration for {employee_name} ===")
        print("Hold steady when prompted. Multiple images will be taken automatically.")

        while pose_index < len(pose_names):
            ret, frame = cap.read()
            if not ret:
                break

            current_pose, confidence, face_detected = self.pose_detector.detect_face_pose(frame)
            target_pose = pose_names[pose_index]
            target_count = self.required_poses[target_pose]
            taken_count = photo_counts[target_pose]

            display_frame = frame.copy()
            faces = self.face_detector.detect_faces(frame)
            for bbox in faces:
                x, y, w, h = bbox
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            display_frame = self.pose_detector.draw_pose_indicators(display_frame, current_pose, confidence)
            self._draw_registration_instructions(display_frame, target_pose, taken_count, target_count, captured_poses)

            # Logic for capturing images
            if (face_detected and current_pose == target_pose and confidence >= self.min_confidence and len(faces) > 0):
                if not countdown_active:
                    pose_start_time = time.time()
                    countdown_active = True

                elapsed_time = time.time() - pose_start_time
                remaining_time = self.capture_delay - elapsed_time

                if remaining_time > 0:
                    countdown_text = f"Hold pose: {remaining_time:.1f}s"
                    cv2.putText(display_frame, countdown_text, (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    progress = elapsed_time / self.capture_delay
                    self._draw_progress_circle(display_frame, progress)
                else:
                    largest_face = max(faces, key=lambda x: x[2] * x[3])
                    face_roi = self.face_detector.extract_face_roi(frame, largest_face)
                    # Save each face for averaging
                    captured_poses[target_pose].append(face_roi)
                    photo_counts[target_pose] += 1
                    print(f"✓ Captured {target_pose} photo {photo_counts[target_pose]}/{target_count}")

                    # Save to disk (optional)
                    pose_filename = f"employee_photos/{employee_id}_{target_pose}_{photo_counts[target_pose]}.jpg"
                    cv2.imwrite(pose_filename, face_roi)

                    countdown_active = False

                    if photo_counts[target_pose] >= target_count:
                        pose_index += 1
                        time.sleep(0.2)
            else:
                countdown_active = False
                pose_start_time = None

            cv2.imshow('Multi-Pose Face Registration', display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("Registration cancelled")
                cap.release()
                cv2.destroyAllWindows()
                return False

        cap.release()
        cv2.destroyAllWindows()

        # Flatten all poses into a single list of face images
        face_images = []
        for pose, images in captured_poses.items():
            face_images.extend(images)
        if len(face_images) >= 10:  # Ensure enough photos
            success = self.face_recognizer.add_employee(employee_id, employee_name, face_images)
            if success:
                print(f"\n✓ Registered {employee_name} with {len(face_images)} poses!")
                self._save_registration_metadata(employee_id, employee_name, captured_poses)
                return True
        print("Registration failed - insufficient poses captured")
        return False

    def _draw_registration_instructions(self, frame, target_pose, taken_count, target_count, captured_poses):
        h, w = frame.shape[:2]
        instruction_text = f"Show {target_pose.upper()} - Captured {taken_count}/{target_count}"
        cv2.putText(frame, instruction_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        y_offset = 80
        for i, pose in enumerate(self.required_poses):
            status = f"{len(captured_poses[pose])}/{self.required_poses[pose]}"
            color = (0, 255, 0) if len(captured_poses[pose]) == self.required_poses[pose] else (0, 255, 255)
            pose_text = f"{pose.upper()}: {status}"
            cv2.putText(frame, pose_text, (w - 180, 60 + y_offset + i * 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Pose-specific instructions
        if target_pose == "left":
            cv2.putText(frame, "Turn your head LEFT", (10, h - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif target_pose == "right":
            cv2.putText(frame, "Turn your head RIGHT", (10, h - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif target_pose == "front":
            cv2.putText(frame, "Look straight at the camera", (10, h - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    def _draw_progress_circle(self, frame, progress):
        """Draw circular progress indicator"""
        h, w = frame.shape[:2]
        center = (w - 80, 120)
        radius = 30
        
        # Background circle
        cv2.circle(frame, center, radius, (64, 64, 64), 2)
        
        # Progress arc
        if progress > 0:
            angle = int(360 * progress)
            cv2.ellipse(frame, center, (radius, radius), -90, 0, angle, (0, 255, 0), 3)
    
    def _save_registration_metadata(self, employee_id: str, employee_name: str, poses):
        """Save additional metadata about registration"""
        metadata = {
            'employee_id': employee_id,
            'employee_name': employee_name,
            'registration_date': datetime.now().isoformat(),
            'poses_captured': list(poses),
            'registration_method': 'multi_pose_webcam'
        }
        
        metadata_file = f"employee_photos/{employee_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def register_from_photos(self, employee_id: str, employee_name: str, photo_paths: list) -> bool:
        """Register employee from existing photos (keeping original functionality)"""
        face_images = []
        
        for photo_path in photo_paths:
            if not os.path.exists(photo_path):
                print(f"Photo not found: {photo_path}")
                continue
            
            image = cv2.imread(photo_path)
            if image is None:
                print(f"Could not load image: {photo_path}")
                continue
            
            faces = self.face_detector.detect_faces(image)
            if faces:
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                face_roi = self.face_detector.extract_face_roi(image, largest_face)
                face_images.append(face_roi)
                print(f"Extracted face from {photo_path}")
            else:
                print(f"No face detected in {photo_path}")
        
        if face_images:
            success = self.face_recognizer.add_employee(employee_id, employee_name, face_images)
            if success:
                self._save_registration_metadata(employee_id, employee_name, ['photo_based'])
            return success
        
        print("No valid face images found")
        return False

class UltimateRegistrationApp:
    def __init__(self):
        self.face_detector = FaceDetector()
        self.face_recognizer = RealFaceRecognizer()
        self.multi_pose_app = MultiPoseRegistrationApp()
        
        # Colors for different elements
        self.bbox_color = (0, 255, 0)
        self.recognized_color = (0, 255, 0)
        self.unknown_color = (0, 0, 255)
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with enhanced recognition display"""
        faces = self.face_detector.detect_faces(frame)
        
        for i, bbox in enumerate(faces):
            x, y, w, h = bbox
            
            if w > 0 and h > 0:
                face_roi = self.face_detector.extract_face_roi(frame, bbox)
                
                # Recognize face
                employee_id, employee_name, confidence = self.face_recognizer.recognize_face(face_roi)
                
                # Determine colors and labels
                if employee_id:
                    label = f"{employee_name} ({confidence:.3f})"
                    bbox_color = self.recognized_color
                    text_color = self.recognized_color
                else:
                    label = f"Unknown ({confidence:.3f})"
                    bbox_color = self.unknown_color
                    text_color = self.unknown_color
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), bbox_color, 2)
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x, y - 25), (x + label_size[0], y), text_color, -1)
                
                # Draw label text
                cv2.putText(frame, label, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Draw employee ID if recognized
                if employee_id:
                    cv2.putText(frame, f"ID: {employee_id}", (x, y + h + 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, bbox_color, 1)
        
        # Draw status information
        num_employees = len(self.face_recognizer.list_employees())
        status_text = f"Faces: {len(faces)} | Employees: {num_employees}"
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw instructions
        instructions = [
            "Press 'r' to register (multi-pose webcam)",
            "Press 'p' to register from photos",
            "Press 'l' to list employees",
            "Press 'd' to delete employee",
            "Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, frame.shape[0] - 100 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        return frame
    
    def run_webcam(self):
        """Run enhanced webcam with multi-pose registration"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Ultimate Face Recognition System Started")
        print("Controls:")
        print("- 'r': Register new employee (multi-pose webcam)")
        print("- 'p': Register from photo paths")
        print("- 'l': List all employees")
        print("- 'd': Delete employee")
        print("- 'q': Quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame = self.process_frame(frame)
            cv2.imshow('Ultimate Face Recognition', processed_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.register_multi_pose_webcam()
            elif key == ord('p'):
                self.register_from_photos()
            elif key == ord('l'):
                self.list_all_employees()
            elif key == ord('d'):
                self.delete_employee()
        
        cap.release()
        cv2.destroyAllWindows()
    
    def register_multi_pose_webcam(self):
        """Register employee using multi-pose webcam capture"""
        print("\n=== Multi-Pose Webcam Registration ===")
        employee_id = input("Enter Employee ID: ").strip()
        employee_name = input("Enter Employee Name: ").strip()
        
        if not employee_id or not employee_name:
            print("Invalid input. Registration cancelled.")
            return
        
        # Check if employee already exists
        if employee_id in self.face_recognizer.employee_embeddings:
            print(f"Employee {employee_id} already exists!")
            return
        
        print("\nStarting multi-pose capture...")
        print("You will be guided to capture your face from 3 different angles:")
        print("1. Front view (looking straight)")
        print("2. Left view (turn head left)")
        print("3. Right view (turn head right)")
        input("Press Enter to continue...")
        
        success = self.multi_pose_app.guided_pose_capture(employee_id, employee_name)
        
        if success:
            print(f"\n✓ Employee {employee_name} registered successfully with multi-pose capture!")
        else:
            print("\n✗ Registration failed!")
    
    def register_from_photos(self):
        """Register employee from photo paths (original functionality)"""
        print("\n=== Photo Path Registration ===")
        employee_id = input("Enter Employee ID: ").strip()
        employee_name = input("Enter Employee Name: ").strip()
        photo_paths = input("Enter photo paths (comma-separated): ").strip().split(',')
        photo_paths = [path.strip() for path in photo_paths]
        
        if not employee_id or not employee_name or not photo_paths:
            print("Invalid input. Registration cancelled.")
            return
        
        success = self.multi_pose_app.register_from_photos(employee_id, employee_name, photo_paths)
        
        if success:
            print(f"✓ Employee {employee_name} registered successfully from photos!")
        else:
            print("✗ Registration failed!")
    
    def list_all_employees(self):
        """List all registered employees"""
        employees = self.face_recognizer.list_employees()
        print("\n=== Registered Employees ===")
        if employees:
            for emp_id, metadata in employees.items():
                print(f"ID: {emp_id} | Name: {metadata['name']} | "
                      f"Samples: {metadata['num_samples']} | "
                      f"Registered: {metadata['registered_date'][:10]}")
        else:
            print("No employees registered yet.")
        print("=" * 50)
    
    def delete_employee(self):
        """Delete an employee from the database"""
        employees = self.face_recognizer.list_employees()
        if not employees:
            print("No employees to delete.")
            return
        
        print("\n=== Delete Employee ===")
        self.list_all_employees()
        employee_id = input("Enter Employee ID to delete: ").strip()
        
        if employee_id in employees:
            confirm = input(f"Delete {employees[employee_id]['name']}? (y/N): ").strip().lower()
            if confirm == 'y':
                success = self.face_recognizer.remove_employee(employee_id)
                if success:
                    print("✓ Employee deleted successfully!")
                else:
                    print("✗ Failed to delete employee.")
            else:
                print("Deletion cancelled.")
        else:
            print("Employee not found.")

    def mark_attendance(self):
        print("\n=== Attendance Marking ===")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return

        attendance_marked = False
        recognized_id = None
        recognized_name = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            faces = self.face_detector.detect_faces(frame)
            display_frame = frame.copy()
            for bbox in faces:
                x, y, w, h = bbox
                if w > 0 and h > 0:
                    face_roi = self.face_detector.extract_face_roi(frame, bbox)
                    employee_id, employee_name, confidence = self.face_recognizer.recognize_face(face_roi)
                    if employee_id:
                        label = f"{employee_name} ({confidence:.2f})"
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(display_frame, label, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                        recognized_id = employee_id
                        recognized_name = employee_name
                        attendance_marked = True
                        break
                    else:
                        label = "Unknown"
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(display_frame, label, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            cv2.imshow('Mark Attendance', display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC to cancel
                break
            if attendance_marked:
                break

        cap.release()
        cv2.destroyAllWindows()
        if attendance_marked and recognized_id:
            print(f"\nRecognized: {recognized_name} (ID: {recognized_id})")
            confirm = input("Confirm attendance? (y/n): ").strip().lower()
            if confirm == "y":
                self.face_recognizer.db.record_attendance(recognized_id, recognized_name)
                print("✓ Attendance marked successfully!")
            else:
                print("✗ Attendance not marked.")
        elif not attendance_marked:
            print("✗ No recognized face for attendance.")




def main():
    """Main function with enhanced menu system"""
    app = UltimateRegistrationApp()

    while True:
        print("\n" + "=" * 30)
        print("Ultimate Face Recognition System")
        print("1. Start live recognition with registration")
        print("2. Register employee (multi-pose webcam)")
        print("3. Register employee from photos")
        print("4. List employees")
        print("5. Mark attendance")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            app.run_webcam()
        elif choice == '2':
            app.register_multi_pose_webcam()
        elif choice == '3':
            app.register_from_photos()
        elif choice == '4':
            app.list_all_employees()
        elif choice == '5':
            app.mark_attendance()
        else:
            print("Invalid choice")
            break


if __name__ == "__main__":
    main()
