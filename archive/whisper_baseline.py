import time
from faster_whisper import WhisperModel

print("\nLoading Faster-Whisper (tiny.en) via int8...")
start_time = time.time()

# I-load ang model sa CUDA gamit ang pinakamagaang compute type
model = WhisperModel("tiny.en", device="cuda", compute_type="int8")

print(f"✅ Loaded in {time.time() - start_time:.2f} seconds!")
print("Silipin ang Task Manager. Magkano ang itinaas ng RAM %?")

# Standby lang ng 2 minuto para ma-monitor mo ang memory steady state
time.sleep(120)