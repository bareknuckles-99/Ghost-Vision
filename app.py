import cv2
import base64
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from main import GhostVision # Importing the main engine lessgooo!

app = Flask(__name__)
CORS(app) # Allows React app to talk to this server
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

#initiate 
system = GhostVision()

def broadcast_video():
    """Continuously grabs frames from the engine and sends them to the web."""
    system.start_detection_thread() # first def in class GhostVision in main engine file
    
    while True:
        if system.frame is not None:
            # 1. Encoding the frame as a JPEG
            small_frame = cv2.resize(system.frame, (640, 480)) # Shrink resolution
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50] # 50% compression
            _, buffer = cv2.imencode('.jpg', small_frame, encode_param)
            
            # 2. Converting to Base64 string
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            # 3. Emits/broadcasting to all connected web clients
            socketio.emit('video_frame', {'image': jpg_as_text})
            socketio.emit('threat_status', {
                'level': system.threat_level,
                'color': system.alert_color
            })
        
        socketio.sleep(0.04) # Roughly 25 Frames Per Second

@socketio.on('connect')
def handle_connect():
    print("Dashboard Connected!")
    # Start the video broadcast when someone opens the website
    socketio.start_background_task(broadcast_video)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)