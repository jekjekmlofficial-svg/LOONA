import sounddevice as sd
import numpy as np
import torch
from silero_vad import load_silero_vad
from faster_whisper import WhisperModel
import warnings

# Itago ang mga FP16 warning ng Whisper para malinis ang terminal
warnings.filterwarnings("ignore")

print("Loading AI Models (Whisper & Silero VAD)...")
whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
vad_model = load_silero_vad()

SAMPLE_RATE = 16000
CHUNK_SIZE = 512 # 32ms audio chunks - perfect size para sa Silero

audio_buffer = []
is_listening = False
silence_counter = 0

SILENCE_LIMIT = 1.5      # Ilang segundong tahimik bago i-process ang narinig
MAX_RECORD_TIME = 15.0   # HARD CAP: I-cut ang recording pag umabot ng 15s para iwas RAM leak

print("\n🎤 Ready! [IDLE STATE] Nakikinig na sa paligid...")

# Gamitin ang sounddevice para kumuha ng live audio mula sa mic
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
    while True:
        chunk, _ = stream.read(CHUNK_SIZE)
        audio_data = chunk.flatten()
        
        # Convert raw audio to tensor para sa VAD
        tensor_data = torch.from_numpy(audio_data)
        speech_prob = vad_model(tensor_data, SAMPLE_RATE).item()
        
        # STATE 1 & 2: LISTENING (Kung lumampas sa 50% chance na tao ang nagsasalita)
        if speech_prob > 0.5:
            if not is_listening:
                print("\n[VAD] 🟢 Boses detected! (Buffering...)")
                is_listening = True
            audio_buffer.extend(audio_data.tolist())
            silence_counter = 0  # I-reset ang tahimik counter dahil may nagsalita
            
        # Kung nag-buffering na pero biglang tumahimik
        elif is_listening:
            audio_buffer.extend(audio_data.tolist())
            silence_counter += (CHUNK_SIZE / SAMPLE_RATE)
            buffer_duration = len(audio_buffer) / SAMPLE_RATE
            
            # STATE 3: PROCESSING (Kung matagal nang tahimik O umabot na sa 15s Hard Cap)
            if silence_counter > SILENCE_LIMIT or buffer_duration > MAX_RECORD_TIME:
                print(f"[VAD] 🔴 Processing {buffer_duration:.1f}s of audio...")
                
                # I-convert pabalik sa format na naiintindihan ng Whisper
                np_audio = np.array(audio_buffer, dtype=np.float32)
                
                # I-transcribe minsan lang (One-shot call)
                segments, _ = whisper_model.transcribe(np_audio, beam_size=1)
                text = "".join(segment.text for segment in segments).strip()
                
                if text:
                    print(f"[TAINGA] Narinig ko: {text}")
                else:
                    print("[TAINGA] Walang malinaw na narinig.")
                
                # Clear buffer and reset (Balik sa IDLE)
                audio_buffer.clear()
                is_listening = False
                silence_counter = 0
                print("\n🎤 [IDLE STATE] Waiting for voice...")