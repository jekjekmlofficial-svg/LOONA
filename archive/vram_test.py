import cv2
import time
import threading
import requests
from ultralytics import YOLO

# 1 I-load ang YOLOv8 sa iisang process lang (Tipid sa Ram)
print("Loading.....")
model = YOLO("../yolov8n.pt")

def llm_stress_test():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "loona-brain", # Dito natin ginamit ang in-optimize mong model!
        "propmt": "Write a very detailed 5-paragraph essay about the history of microprocessors.",
        "stream": False,
        "keep_alive": 1
    }

    time.sleep(3) # Warm-up delay sa camera

    while True:
        print("\n[AI] NAG--IISIP ajg LLAMA 3... (Bantayan ang RAM % at FPS!)")
        start_time =  time.time()
        try:
            requests.post(url, json=payload)
            print(f"[AI] TAPOS NA SUMAGOT! (Took {time.time() - start_time:.2f}s)\n")
        except:
            pass
        time.sleep(5)


# 2 Simulan ang AI request sa background thread
threading.Thread(target=llm_stress_test, daemon=True).start()

# 3 Vision Loop (Main Thread)

cap = cv2.VideoCapture(0)
print("Starting Camera Loop...")

while cap.isOpened():
    start_time = time.time()
    ret, frame = cap.read()
    if not ret: break

    # YOLO Inferene
    Results = model(frame, verbose=False)

    # Calculate FPS
    fps = 1.0 / (time.time() - start_time)

    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("LOONA Vision Test (Optimized)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()