from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import logging
from api_models import (
    RecognizeFaceResponse, 
    RegisterEmployeeResponse,
    ListEmployeesResponse,
    DeleteEmployeeResponse,
    MarkAttendanceResponse
)
from face_detection import FaceDetector
from face_pose import ImprovedFacePoseDetector
from face_recognition import RealFaceRecognizer
from collections import defaultdict
from datetime import datetime

app = FastAPI(title="Face Recognition API", version="1.0.0")

# Allow all CORS for testing - restrict in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
face_detector = FaceDetector()
face_pose_detector = ImprovedFacePoseDetector()
face_recognizer = RealFaceRecognizer()

from fastapi import Request
import time

@app.post("/recognize-face/", response_model=RecognizeFaceResponse)
async def recognize_face(
    # request: Request,
    image: UploadFile = File(...),
    frame_id: str = Form(None)
):
    start_time = time.time()
    try:
        image_bytes = await image.read()
        npimg = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        faces = face_detector.detect_faces(frame)
        if not faces:
            return RecognizeFaceResponse(
                employee_id=None, employee_name=None, confidence=0.0, success=False, error="No face detected"
            )
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        face_roi = face_detector.extract_face_roi(frame, largest_face)
        employee_id, employee_name, confidence = face_recognizer.recognize_face(face_roi)
        elapsed = time.time() - start_time
        return RecognizeFaceResponse(
            employee_id=employee_id,
            employee_name=employee_name,
            confidence=confidence if employee_id else 0.0,
            success=bool(employee_id),
            error=None if employee_id else "Face not recognized",
            frame_id=frame_id,
            latency_ms=int(elapsed * 1000)
        )
    except Exception as e:
        logging.exception("Error in /recognize-face")
        return RecognizeFaceResponse(
            employee_id=None, employee_name=None, confidence=0.0, success=False, error=str(e)
        )

@app.post("/register-employee/", response_model=RegisterEmployeeResponse)
async def register_employee(
    employee_id: str = Form(...),
    employee_name: str = Form(...),
    images: list[UploadFile] = File(...)
):
    """Register a new employee with multiple face images."""
    try:
        face_images = []
        for img_file in images:
            image_bytes = await img_file.read()
            npimg = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            faces = face_detector.detect_faces(frame)
            if faces:
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                face_roi = face_detector.extract_face_roi(frame, largest_face)
                face_images.append(face_roi)
        if not face_images:
            return RegisterEmployeeResponse(success=False, message=None, error="No faces detected in uploaded images")
        registered = face_recognizer.add_employee(employee_id, employee_name, face_images)
        if registered:
            return RegisterEmployeeResponse(success=True, message="Employee registered", error=None)
        else:
            return RegisterEmployeeResponse(success=False, message=None, error="Registration failed")
    except Exception as e:
        logging.exception("Error in /register-employee")
        return RegisterEmployeeResponse(success=False, message=None, error=str(e))

@app.get("/list-employees/", response_model=ListEmployeesResponse)
async def list_employees():
    """List all registered employees."""
    try:
        employees_dict = face_recognizer.list_employees()
        employees = []
        for emp_id, info in employees_dict.items():
            employees.append({
                "employee_id": emp_id,
                "name": info["name"],
                "registered_date": info["registered_date"],
                "num_samples": info["num_samples"],
                "model": info["model"]
            })
        return ListEmployeesResponse(employees=employees)
    except Exception as e:
        logging.exception("Error in /list-employees")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-employee/{employee_id}", response_model=DeleteEmployeeResponse)
async def delete_employee(employee_id: str):
    """Delete employee by ID."""
    try:
        result = face_recognizer.remove_employee(employee_id)
        if result:
            return DeleteEmployeeResponse(success=True, message="Employee deleted", error=None)
        else:
            return DeleteEmployeeResponse(success=False, message=None, error="Employee not found")
    except Exception as e:
        logging.exception("Error in /delete-employee")
        return DeleteEmployeeResponse(success=False, message=None, error=str(e))

@app.post("/mark-attendance/", response_model=MarkAttendanceResponse)
async def mark_attendance(image: UploadFile = File(...)):
    """Recognize face and mark attendance."""
    try:
        image_bytes = await image.read()
        npimg = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        faces = face_detector.detect_faces(frame)
        if not faces:
            return MarkAttendanceResponse(success=False, employee_id=None, employee_name=None, timestamp=None)
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        face_roi = face_detector.extract_face_roi(frame, largest_face)
        employee_id, employee_name, confidence = face_recognizer.recognize_face(face_roi)
        if employee_id:
            face_recognizer.db.record_attendance(employee_id, employee_name)
            from datetime import datetime
            return MarkAttendanceResponse(
                success=True, employee_id=employee_id, employee_name=employee_name,
                timestamp=datetime.now().isoformat()
            )
        else:
            return MarkAttendanceResponse(success=False, employee_id=None, employee_name=None, timestamp=None)
    except Exception as e:
        logging.exception("Error in /mark-attendance")
        return MarkAttendanceResponse(success=False, employee_id=None, employee_name=None, timestamp=None)



from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import json

from face_detection import FaceDetector
from face_recognition import RealFaceRecognizer

# app = FastAPI()

# # Initialize your detection/recognition classes
# face_detector = FaceDetector()
# face_recognizer = RealFaceRecognizer()

# @app.websocket("/ws/recognize/")
# async def websocket_recognize(websocket: WebSocket):
#     await websocket.accept()
#     print("Client connected to /ws/recognize")

#     try:
#         while True:
#             # Receive bytes (assume client sends binary JPEG frame)
#             data = await websocket.receive_bytes()

#             # Convert to OpenCV image
#             npimg = np.frombuffer(data, np.uint8)
#             frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#             # Detect faces
#             faces = face_detector.detect_faces(frame)
#             if not faces:
#                 response = {
#                     "success": False,
#                     "error": "No face detected"
#                 }
#                 await websocket.send_text(json.dumps(response))
#                 continue

#             largest_face = max(faces, key=lambda x: x[2]*x[3])
#             face_roi = face_detector.extract_face_roi(frame, largest_face)

#             # Recognize face
#             employee_id, employee_name, confidence = face_recognizer.recognize_face(face_roi)
#             if employee_id:
#                 response = {
#                     "success": True,
#                     "employee_id": employee_id,
#                     "employee_name": employee_name,
#                     "confidence": float(confidence)
#                 }
#             else:
#                 response = {
#                     "success": False,
#                     "employee_id": None,
#                     "employee_name": None,
#                     "confidence": float(confidence),
#                     "error": "Unknown face"
#                 }
#             await websocket.send_text(json.dumps(response))
#     except WebSocketDisconnect:
#         print("Client disconnected from /ws/recognize")
#     except Exception as e:
#         print(f"Error in websocket: {e}")
#         await websocket.send_text(json.dumps({"success": False, "error": str(e)}))
#         await websocket.close()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import json

from face_detection import FaceDetector
from face_recognition import RealFaceRecognizer

# app = FastAPI()

# face_detector = FaceDetector()
# face_recognizer = RealFaceRecognizer()

@app.websocket("/ws/recognize/")
async def websocket_recognize(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            npimg = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

            faces = face_detector.detect_faces(frame)
            faces_response = []

            for bbox in faces:
                x, y, w, h = bbox
                face_roi = face_detector.extract_face_roi(frame, bbox)
                employee_id, employee_name, confidence = face_recognizer.recognize_face(face_roi)
                faces_response.append({
                    "bbox": {"x": x, "y": y, "w": w, "h": h},
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "confidence": float(confidence)
                })

            response = {
                "num_faces": len(faces_response),
                "faces": faces_response,
                "success": len(faces_response) > 0,
                "error": None if len(faces_response) > 0 else "No faces detected"
            }
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({"success": False, "error": str(e)}))
        await websocket.close()





# Keeps track of recently marked attendances for this WebSocket session
# (You may want a more robust solution for multi-user/global session)
recent_attendance = defaultdict(lambda: 0)
ATTENDANCE_COOLDOWN = 300  # seconds between markings for same employee

@app.websocket("/ws/attendance/")
async def websocket_attendance(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            npimg = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

            faces = face_detector.detect_faces(frame)
            faces_response = []
            now = datetime.now().timestamp()

            for bbox in faces:
                x, y, w, h = bbox
                face_roi = face_detector.extract_face_roi(frame, bbox)
                employee_id, employee_name, confidence = face_recognizer.recognize_face(face_roi)
                attendance_marked = False
                timestamp = None

                if employee_id:
                    # Check if we should mark attendance (e.g., not marked recently)
                    last_mark = recent_attendance[employee_id]
                    if now - last_mark > ATTENDANCE_COOLDOWN:
                        face_recognizer.db.record_attendance(employee_id, employee_name)
                        attendance_marked = True
                        timestamp = datetime.now().isoformat()
                        recent_attendance[employee_id] = now

                faces_response.append({
                    "bbox": {"x": x, "y": y, "w": w, "h": h},
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "confidence": float(confidence),
                    "attendance_marked": attendance_marked,
                    "timestamp": timestamp
                })

            response = {
                "num_faces": len(faces_response),
                "faces": faces_response,
                "success": len(faces_response) > 0,
                "error": None if len(faces_response) > 0 else "No faces detected"
            }
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        print("Client disconnected from /ws/attendance")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"success": False, "error": str(e)}))
        await websocket.close()
