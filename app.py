import cv2
import numpy as np
from face_detection import FaceDetector
from face_recognition import RealFaceRecognizer
from registeration import MultiPoseRegistrationApp

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