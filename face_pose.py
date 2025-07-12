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