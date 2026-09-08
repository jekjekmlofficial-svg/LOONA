import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write
import cv2
import os
from ultralytics import YOLO

# 1. Initialize the YOLO Vision Model
print("Loading Neural Network...")
model = YOLO('yolov8s.pt')
recognizer = sr.Recognizer()

sample_rate = 44100
duration = 4
temp_file = "temp_voice.wav"

def activate_vision():
    cap = cv2.VideoCapture(0)
    print("📷 Vision Module Online. Press 'q' on the camera window to stop tracking.")
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # Process frame with 60% confidence filter
        results = model(frame, conf=0.6)
        cv2.imshow("LOONA Vision Tracker", results[0].plot())
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    print("📷 Vision Module Offline. Returning to Voice Standby.")

# 2. Main AI Loop
while True:
    print(f"\n🎙️ Listening for {duration} seconds... (Say 'LOONA find my phone' or 'shutdown')")
    
    # Record Audio
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    write(temp_file, sample_rate, audio_data)
    
    # Process Audio
    with sr.AudioFile(temp_file) as source:
        audio = recognizer.record(source)
        
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"🗣️ Command Received: {command}")
        
        # Trigger Logic
        if "find" in command and "phone" in command:
            print("🤖 SYSTEM ACTION: Target locked. Engaging camera...")
            activate_vision()
        elif "shutdown" in command:
            print("🤖 SYSTEM ACTION: Shutting down core processes.")
            break
            
    except sr.UnknownValueError:
        # Fails silently if it just hears background noise, looping back to listen again
        pass 
    except sr.RequestError as e:
        print(f"Network error: {e}")

if os.path.exists(temp_file):
    os.remove(temp_file)