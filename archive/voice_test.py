import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write
import os

# 1. Setup Recording Parameters
sample_rate = 44100  
duration = 10  # Ilang segundo makikinig ang laptop (pwede mong habaan)

print(f"🎙️ Magsalita ka na! Makikinig ako ng {duration} seconds...")
print("Try saying: 'LOONA find my phone'")

# 2. Record using sounddevice (No PyAudio needed!)
audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
sd.wait()  # Hihintayin matapos ang 4 seconds
print("✅ Tapos na makinig. Pino-process ang boses...")

# 3. Save temporarily as WAV file
temp_file = "temp_voice.wav"
write(temp_file, sample_rate, audio_data)

# 4. Pass the recorded audio to the AI
recognizer = sr.Recognizer()
with sr.AudioFile(temp_file) as source:
    audio = recognizer.record(source)

try:
    # Converting speech to text using Google's free engine
    command = recognizer.recognize_google(audio)
    
    print(f"\n🗣️ LOONA heard: {command}")
    
    # 5. Logic / Action
    if "find" in command.lower() and "phone" in command.lower():
        print("🤖 SYSTEM ACTION: Triggering Vision Module para hanapin ang phone!")
    else:
        print("🤖 SYSTEM ACTION: Narinig ko, pero walang naka-program na action diyan.")

except sr.UnknownValueError:
    print("\n❌ Hindi maintindihan ng AI ang sinabi mo. Masyadong maingay o malabo.")
except sr.RequestError as e:
    print(f"\n❌ May error sa connection: {e}")

# (Optional) Clean up the temp file so it doesn't clutter your folder
if os.path.exists(temp_file):
    os.remove(temp_file)