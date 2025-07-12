import logging
import cv2
import numpy as np
from deepface import DeepFace
from datetime import datetime
from database import PgVectorDB
from typing import List, Optional, Tuple, Dict

logger = logging.getLogger("face_recognition")

class RealFaceRecognizer:
    def __init__(self, model_name="Facenet", threshold=0.7):
        self.model_name = "Facenet" if model_name.lower().startswith("facenet") else "VGG-Face"
        self.threshold = threshold
        try:
            self.model = DeepFace.build_model(self.model_name)
            logger.info(f"DeepFace model {self.model_name} loaded.")
        except Exception as e:
            logger.error(f"Error loading DeepFace model: {e}")
            raise
        try:
            self.db = PgVectorDB()
        except Exception as e:
            logger.error(f"DB error in FaceRecognizer: {e}")
            raise


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
