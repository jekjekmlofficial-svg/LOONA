import cv2, time, threading, requests, queue, warnings, json, os, gc
import sounddevice as sd
import numpy as np
import torch
torch.set_grad_enabled(False)
from kokoro_onnx import Kokoro
from silero_vad import load_silero_vad
from faster_whisper import WhisperModel
from ultralytics import YOLO

warnings.filterwarnings("ignore")

# ==========================================
# QUEUES (Mga Tulay ng Data)
# ==========================================
dialogue_queue = queue.Queue()
tts_queue = queue.Queue() 

# Global variable para sa paningin
current_vision_objects = "wala"

print("Loading The Holy Trinity (YOLO, Whisper, Llama 3)...")
yolo_model = YOLO("yolov8n.pt") 
# 🔴 FIX 1: Tumaas ang talino ng Tainga (base.en) para hindi hallucinated ang words
whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
vad_model = load_silero_vad()

# ==========================================
# ANG BIBIG NI L.O.O.N.A. (Kokoro-82M Expressive TTS)
# ==========================================
def tts_thread():
    model_path = r"C:\Users\Crisanto\LOONA\kokoro-v0_19.onnx"
    voices_path = r"C:\Users\Crisanto\LOONA\voices.bin"
    
    try:
        kokoro = Kokoro(model_path, voices_path)
        print("[BIBIG] 👄 Kokoro Expressive Voice Engine is READY!")
    except Exception as e:
        print(f"[BIBIG] ❌ Failed to load Kokoro: {e}")
        return

    while True:
        text_chunk = tts_queue.get()
        if not text_chunk or text_chunk.strip() == "":
            continue
            
        try:
            samples, sample_rate = kokoro.create(
                text_chunk, 
                voice="af_bella", 
                speed=1.2, 
                lang="en-us"
            )
            
            # 🔴 FIX 1: Silence Padding (Dudugtungan ng 0.4 seconds na katahimikan sa dulo)
            silence = np.zeros(int(sample_rate * 0.4), dtype=np.float32)
            padded_samples = np.concatenate((samples, silence))
            
            # I-play ang padded audio
            sd.play(padded_samples, samplerate=sample_rate, blocking=True)
            
            # 🔴 FIX 2: RAM Leak Prevention (Piliting burahin ang audio data sa RAM)
            del samples, silence, padded_samples
            gc.collect() 
            
        except Exception as e:
            print(f"\n[BIBIG] ❌ Error sa Kokoro Generation: {e}")

# ==========================================
# ANG UTAK NI L.O.O.N.A.
# ==========================================
# 🔴 FIX 2: Sassy Prompt, no name-dropping!
conversation_history = [
    {"role": "system", "content": "You are L.O.O.N.A., a sassy, witty, and highly intelligent companion. You are talking directly to your creator, a 20-year-old Computer Engineering student. STRICT RULES: 1. NEVER say 'As an AI' or 'As a robot'. 2. DO NOT use his name in every sentence. It is annoying. Rarely use his name. 3. Stop commenting on his prompts. Just answer directly and conversationally like a real human. 4. Keep responses extremely short (1-2 sentences). Do not use emojis."}
]
MAX_HISTORY = 21

def llm_thread():
    global current_vision_objects
    url = "http://localhost:11434/api/chat" 
    OLLAMA_MODEL = "loona-brain" # Siguraduhing ito ang totoong pangalan ng model mo

    with requests.Session() as session:
        while True:
            user_text = dialogue_queue.get() 
            
            print(f"\n[UTAK] 🧠 Iniisip ang sagot sa: '{user_text}'")
            print(f"[UTAK] 👁️ (Current vision injected: I see {current_vision_objects})")
            
            # Ang malinis na text lang ang ise-save natin sa permanent history
            conversation_history.append({"role": "user", "content": user_text})
            
            if len(conversation_history) > MAX_HISTORY:
                conversation_history[:] = [conversation_history[0]] + conversation_history[-(MAX_HISTORY-1):]
            
            # Gagawa tayo ng temporary copy ng history para sa payload (Patagong ipapasa ang Mata)
            payload_messages = list(conversation_history)
            payload_messages[-1]["content"] = f"{user_text} [System Note: Hidden visual context for you, I am currently seeing: {current_vision_objects}]"
            
            # 🔴 FIX 3: keep_alive = -1 para walang reload delay
            payload = {
                "model": OLLAMA_MODEL, 
                "messages": payload_messages, 
                "stream": True, 
                "keep_alive": -1 
            }
            
            try:
                ai_response = ""
                
                with session.post(url, json=payload, stream=True) as response:
                    print("[UTAK] 🗣️ L.O.O.N.A.: ", end="", flush=True)
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            word = chunk.get("message", {}).get("content", "")
                            ai_response += word
                            print(word, end="", flush=True)
                    print("\n")
                
                # 🔴 FIX 3: Ipapasa ang BUONG sagot ng isahan para walang bitin/gaps
                if ai_response.strip():
                    tts_queue.put(ai_response.strip())
                
                conversation_history.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                print(f"\n[UTAK] ❌ Error sa pag-iisip: {e}")

# ==========================================
# ANG TAINGA NI L.O.O.N.A.
# ==========================================
def whisper_thread():
    SAMPLE_RATE, CHUNK_SIZE = 16000, 512
    audio_buffer, is_listening, silence_counter = [], False, 0
    print("🎤 [TAINGA] Naka-abang sa boses mo...")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
        while True:
            chunk, _ = stream.read(CHUNK_SIZE)
            audio_data = chunk.flatten()
            tensor_data = torch.from_numpy(audio_data)
            speech_prob = vad_model(tensor_data, SAMPLE_RATE).item()

            if speech_prob > 0.5:
                if not is_listening:
                    print("\n[VAD] 🟢 Nakikinig...")
                    is_listening = True
                audio_buffer.extend(audio_data.tolist())
                silence_counter = 0
            elif is_listening:
                audio_buffer.extend(audio_data.tolist())
                silence_counter += (CHUNK_SIZE / SAMPLE_RATE)
                buffer_duration = len(audio_buffer) / SAMPLE_RATE

                # 🔴 FIX 4: Mabilisang 0.8 seconds response time!
                if silence_counter > 0.8 or buffer_duration > 15.0:
                    np_audio = np.array(audio_buffer, dtype=np.float32)
                    segments, _ = whisper_model.transcribe(np_audio, beam_size=1)
                    text = "".join(segment.text for segment in segments).strip()

                    if text:
                        print(f"[TAINGA] Narinig ko: {text}")
                        dialogue_queue.put(text) 
                    else:
                        print("[TAINGA] Walang malinaw na narinig.")

                    audio_buffer.clear()
                    is_listening, silence_counter = False, 0

# ==========================================
# MULTITHREADING SETUP & MATA
# ==========================================
threading.Thread(target=llm_thread, daemon=True).start()
threading.Thread(target=whisper_thread, daemon=True).start()
threading.Thread(target=tts_thread, daemon=True).start() 

cap = cv2.VideoCapture(0)
print("👀 [MATA] Camera is live! (Running at optimized 1 FPS para iwas RAM leak)")

# 🔴 SETUP TIMER PARA KAY YOLO
last_yolo_time = 0 

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    current_time = time.time()
    
    # 🔴 FIX 2: 1 litrato kada segundo lang ang iisipin ng AI!
    if current_time - last_yolo_time >= 1.0:
        # Dito lang tatakbo si YOLO
        results = yolo_model(frame, verbose=False)
        
        detected_set = set()
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            class_name = yolo_model.names[class_id]
            detected_set.add(class_name)
            
        if detected_set:
            current_vision_objects = ", ".join(detected_set)
        else:
            current_vision_objects = "wala"
            
        # I-reset ang timer pagkatapos mag-isip
        last_yolo_time = current_time 

    # Ang pag-display ng camera ay mananatiling mabilis at smooth
    cv2.putText(frame, f"Vision: {current_vision_objects}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("LOONA - Mata, Utak, Tainga, at Bibig", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()