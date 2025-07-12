import cv2
import asyncio
import websockets
import json

async def stream_camera():
    uri = "ws://localhost:8000/ws/recognize/"
    uri = "ws://localhost:8000/ws/attendance/"
    
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            # Send binary image
            await websocket.send(buffer.tobytes())

            # Receive result
            result = await websocket.recv()
            data = json.loads(result)
            print(data)

            if cv2.waitKey(1) == 27:  # ESC to exit
                break
        cap.release()

asyncio.run(stream_camera())
