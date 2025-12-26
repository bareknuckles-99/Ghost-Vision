import cv2
import threading
import time
import os
from ultralytics import YOLO
from deepface import DeepFace
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class GhostVision:
    def __init__(self):
        # Loading YOLOv8 for fast person detection
        self.model = YOLO('yolov8n.pt') 
        
        # Identify the demo master face - that is the jpgs of the person to be recognized.
        self.master_img_path = "known_faces/master.jpg" # Make sure this exists!
        
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        
        # Security State
        self.threat_level = "INITIALIZING..."
        self.alert_color = (255, 255, 255)
        self.threat_counter = 0

        # Twilio Config
        self.client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
        self.last_alert_time = 0 
        self.alert_cooldown = 60

    def send_sms_alert(self, message):
        current_time = time.time()
        if current_time - self.last_alert_time > self.alert_cooldown:
            try:
                self.client.messages.create(
                    body=f"GHOST-VISION ALERT: {message}",
                    from_=os.getenv("TWILIO_PHONE"),
                    to=os.getenv("MY_PHONE")
                )
                self.last_alert_time = current_time
                print("SMS Sent!")
            except Exception as e:
                print(f"SMS Error: {e}")

    def detect_logic(self):
        # Warmup: Don't process for the first 5 seconds
        warmup_end = time.time() + 5
        print("System Warming Up... please wait.")
        
        while self.running:
            success, img = self.cap.read()
            if not success: continue

            # Skip processing if we are still in warmup
            if time.time() < warmup_end:
                self.threat_level = "SYSTEM WARMING UP..."
                self.alert_color = (255, 255, 0) # Yellow
                self.frame = img # Just show raw feed
                continue

            # Step 1: YOLO Person Detection
            results = self.model(img, verbose=False, conf=0.5)[0] 
            person_detected = any(self.model.names[int(box.cls[0])] == 'person' for box in results.boxes)
            
            new_status = "CLEAR"
            new_color = (255, 255, 255)

            if person_detected:
                try:
                    # Step 2: DeepFace Verify
                    # Use 'enforce_detection=False' to handle movement/blur
                    result = DeepFace.verify(img1_path=img, 
                                            img2_path=self.master_img_path, 
                                            model_name='VGG-Face', 
                                            enforce_detection=False,
                                            detector_backend='opencv')
                    
                    if result['verified']:
                        new_status = "AUTHORIZED: MASTER DETECTED"
                        new_color = (0, 255, 0)
                        self.threat_counter = 0 # Reset threat
                    else:
                        # Only increment threat if we ARE NOT the master
                        new_status = "THREAT: UNKNOWN SUBJECT"
                        new_color = (0, 0, 255)
                        self.threat_counter += 1
                except Exception as e:
                    # If DeepFace can't find a face at all but YOLO sees a person
                    new_status = "THREAT: IDENTITY CONCEALED"
                    new_color = (0, 0, 255)
                    self.threat_counter += 1

            # Step 3: SMS Logic (Only if threat is consistent)
            if self.threat_counter > 60: #threshold from 10/15 to 60. At ~20 FPS, this gives the system a 3-second 'thinking' window
                threading.Thread(target=self.send_sms_alert, args=("Intruder detected!",), daemon=True).start()
                # Reset counter slightly so we don't spam 100 texts a minute cuz Twilio ain't free after the trial lol
                self.threat_counter = 40

            with self.lock:
                self.threat_level = new_status
                self.alert_color = new_color
                # Important: Use results.plot() to see the YOLO boxes
                self.frame = results.plot()

    def start_detection_thread(self):
        t = threading.Thread(target=self.detect_logic, daemon=True)
        t.start()

    def run(self):
        self.start_detection_thread()
        while self.running:
            with self.lock:
                if self.frame is not None:
                    cv2.imshow("Ghost-Vision Pro", self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    system = GhostVision()
    system.run()