import mediapipe as mp
import cv2
import numpy as np
import logging

logger = logging.getLogger("face_detection")

class FaceDetector:
    """Detect faces using MediaPipe Face Detection."""

    def __init__(self, min_detection_confidence=0.5):
        try:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=min_detection_confidence
            )
            logger.info("FaceDetector initialized.")
        except Exception as e:
            logger.error(f"FaceDetector init error: {e}")
            raise

    def detect_faces(self, image: np.ndarray):
        """Detect faces and return bounding boxes."""
        try:
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
                    faces.append((x, y, width, height))
            return faces
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []

    def extract_face_roi(self, image: np.ndarray, bbox):
        """Extract face region from bounding box."""
        try:
            x, y, w, h = bbox
            return image[y:y+h, x:x+w]
        except Exception as e:
            logger.error(f"Extract face ROI error: {e}")
            return None
