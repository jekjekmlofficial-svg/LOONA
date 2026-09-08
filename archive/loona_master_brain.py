import threading
import time
from flask import Flask, jsonify
import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write
import cv2
import os
from ultralytics import YOLO
import socket
import logging

# ==========================================
# 1. THE WI-FI SERVER THREAD
# ==========================================
app = Flask(__name__)
current_command = "STANDBY" 
camera_active = False
system_running = True

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/loona/status', methods=['GET'])
def esp32_endpoint():
    global current_command
    response = {"device": "LOONA_AI_CORE", "action": current_command, "speed": 80}
    # Nire-reset ang tao detection, pero pinapanatili ang search mode kung naghahanap pa
    if current_command not in ["STANDBY", "SEARCH_MODE"]: 
        current_command = "STANDBY"
    return jsonify(response)

def run_server():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

# ==========================================
# 2. THE VOICE THREAD (Laging Nakikinig)
# ==========================================
def run_voice():
    global current_command, camera_active, system_running
    recognizer = sr.Recognizer()
    sample_rate = 44100
    duration = 4
    temp_file = "temp_voice.wav"
    
    while system_running:
        if not camera_active:
            print("\n🎙️ Listening... (Say 'LOONA find my phone' or 'shutdown')")
        
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        write(temp_file, sample_rate, audio_data)
        
        with sr.AudioFile(temp_file) as source:
            audio = recognizer.record(source)
            
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"🗣️ Heard: {command}")
            
            if "find" in command and "phone" in command:
                current_command = "SEARCH_MODE"
                camera_active = True
                print("🤖 Action: SEARCH_MODE -> Engaging camera...")
            elif "stop" in command and camera_active:
                camera_active = False
                current_command = "STANDBY"
                print("🤖 Action: Stopping camera tracking...")
            elif "shutdown" in command:
                system_running = False
                camera_active = False
                print("🤖 Action: SHUTTING DOWN SYSTEM.")
                os._exit(0) # Pinapatay agad ang buong Python process
                
        except sr.UnknownValueError:
            pass 
        except sr.RequestError:
            pass

    if os.path.exists(temp_file):
        os.remove(temp_file)

# ==========================================
# 3. THE VISION MAIN THREAD (Naghihintay ng Utos)
# ==========================================
def run_vision():
    global current_command, camera_active, system_running
    print("Loading Neural Network...")
    model = YOLO('yolov8s.pt')
    
    while system_running:
        if camera_active:
            cap = cv2.VideoCapture(0)
            print("📷 Vision Module Online. (Say 'stop' to disable camera)")
            
            while cap.isOpened() and camera_active and system_running:
                success, frame = cap.read()
                if not success: break
                
                results = model(frame, conf=0.6)
                cv2.imshow("LOONA Vision Tracker", results[0].plot())
                
                for box in results[0].boxes:
                    if int(box.cls[0]) == 0: 
                        current_command = "PERSON_DETECTED"
                        break 
                        
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    camera_active = False
                    current_command = "STANDBY"
                    break
                    
            cap.release()
            cv2.destroyAllWindows()
        else:
            time.sleep(0.5) # Nagpapahinga habang hindi tinatawag ang camera

# ==========================================
# SYSTEM START
# ==========================================
if __name__ == '__main__':
    laptop_ip = get_ip()
    print(f"\n=======================================")
    print(f"🌐 SERVER IP FOR ESP32: http://{laptop_ip}:5000/loona/status")
    print(f"=======================================")
    
    # Ino-on ang Server sa background
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Ino-on ang Tenga sa background
    voice_thread = threading.Thread(target=run_voice)
    voice_thread.daemon = True
    voice_thread.start()
    
    # Ino-on ang Mata sa harapan
    run_vision()