import time
from datetime import datetime
import os
import json
import pickle
import cv2
from face_detection import FaceDetector
from face_recognition import RealFaceRecognizer
from face_pose import ImprovedFacePoseDetector  # Assuming this is your custom pose detector

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
