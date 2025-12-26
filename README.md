GHOST-VISION v1.0 AI-Powered Facial Recognition and Intruder Alert System

GHOST-VISION is a security dashboard that combines real-time object detection (YOLOv8) with facial recognition (DeepFace) to identify authorized masters versus unknown intruders. If a threat is detected, the system sends an SMS alert via Twilio.

HARDWARE WARNING This project uses heavy AI models including TensorFlow and YOLOv8. It is not intended for low-spec laptops or servers. Running this on weak hardware will cause significant lag and low frame rates.

TECH STACK

Frontend: React.js and Socket.IO

Backend: Python with Flask

AI: YOLOv8 and DeepFace

Alerts: Twilio API


PREREQUISITES

Python 3.9 or higher

Node.js 16 or higher

A Twilio account and phone number

A clear photo of yourself saved as: known_faces/master.jpg


INSTALLATION

STEP 1: BACKEND SETUP CODE: python -m venv venv CODE: venv\Scripts\activate CODE: pip install flask flask-socketio flask-cors ultralytics deepface tf-keras tensorflow twilio python-dotenv

STEP 2: FRONTEND SETUP CODE: cd ghost-vision-ui CODE: npm install

ENVIRONMENT SETUP Create a file named .env in the root folder and add the following: TWILIO_SID=your_sid_here TWILIO_TOKEN=your_token_here TWILIO_PHONE=your_twilio_number MY_PHONE=your_personal_number

HOW TO RUN THE SYSTEM Follow these steps in this specific order:

INITIALIZE AI MODELS Run this first to download the large AI data files. CODE: python main.py

START BACKEND LOGIC CODE: python app.py

START USER INTERFACE In a new terminal: CODE: cd ghost-vision-ui CODE: npm start

SECURITY FEATURES

Double-Verification: Uses YOLO to find a person and DeepFace to confirm who they are.

Threat Threshold: A counter system prevents false alarms from quick glitches.

Cloud Alerts: Instant SMS notification sent to your phone upon confirmed intrusion.