import time
import threading
import requests
import gc
import psutil
import os
import numpy as np
from faster_whisper import WhisperModel

print("Loading Whisper...")
whisper_model = WhisperModel("tiny.en", device="cuda", compute_type="int8")

def get_ram():
    return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

def llm_thread():
    url = "http://localhost:11434/api/generate"
    payload = {"model": "loona-brain", "prompt": "Hello", "stream": False, "keep_alive": 0}
    # Gumamit ng Session para walang orphaned sockets
    with requests.Session() as session:
        while True:
            try:
                with session.post(url, json=payload) as response:
                    pass # Explicitly closed via context manager
            except:
                pass

def whisper_thread():
    dummy = np.zeros(16000, dtype=np.float32)
    while True:
        try:
            segments, _ = whisper_model.transcribe(dummy, beam_size=1)
            for _ in segments: pass # Iterate without building a giant list in memory
        except:
            pass

threading.Thread(target=llm_thread, daemon=True).start()
threading.Thread(target=whisper_thread, daemon=True).start()

print("\nRunning Max Stress (Checking for Leaks)...")
time.sleep(120) # Hayaang mag-ipon ang objects ng 2 minuto

print(f"RAM Before GC: {get_ram():.1f} MB")
gc.collect()
print(f"RAM After GC: {get_ram():.1f} MB")