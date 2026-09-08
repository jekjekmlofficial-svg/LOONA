# L.O.O.N.A. Core AI & Rover Vision System 🤖🚗

A fully offline, multi-threaded Artificial Intelligence system designed for real-time conversational interaction and spatial awareness. Built for local hardware deployment (RTX 4060, 16GB RAM) with upcoming integration for hardware rover tracking.

## 🛠️ The Tech Stack (The Holy Trinity + Voice)

L.O.O.N.A. operates on four independent threads running simultaneously:

### 1. Vision (Mata) 👀
*   **Model:** YOLOv8 Nano (`yolov8n.pt`)
*   **Function:** Real-time object detection and spatial awareness.
*   **Optimization:** Throttled to **1 FPS** (Inference only, gradients disabled) to heavily reduce RAM/VRAM consumption while maintaining functional tracking data.
*   **Next Phase:** Map X/Y bounding box coordinates to Serial/UART signals for rover motor control (Person Follower mode).

### 2. Hearing (Tainga) 🎤
*   **Model:** Faster-Whisper (`base.en`) + Silero VAD (Voice Activity Detection).
*   **Function:** Offline Speech-to-Text.
*   **Optimization:** Configured for sub-second snappy reaction. VAD threshold locked at **0.8 seconds** to instantly process user commands upon silence.

### 3. Brain (Utak) 🧠
*   **Model:** Llama 3 (via Ollama local server, model: `loona-brain`).
*   **Function:** Natural language processing, contextual memory, and personality handling.
*   **Optimization:** Maintained in VRAM (`keep_alive: -1`) to eliminate cold-start delays. System prompt engineered for concise, expressive, and non-robotic responses.

### 4. Voice (Bibig) 👄
*   **Model:** Kokoro-82M ONNX (`af_bella` voice profile).
*   **Function:** Expressive, high-fidelity Text-to-Speech.
*   **Optimization:** Running at 1.2x speed with a 0.4-second silence padding algorithm to prevent audio clipping. Achieves Jarvis/Copilot-level conversational prosody completely offline.

---

## 📂 Repository Structure

```text
LOONA/
├── brain/
│   ├── loona_trinity.py       # MAIN SCRIPT: Multi-threaded AI core
│   ├── yolov8n.pt             # YOLO Vision weights
│   └── archive/               # Old benchmark & test scripts
├── firmware/                  # (Upcoming) C++ code for Arduino/ESP32 Rover
├── hardware/                  # (Upcoming) Schematics and PCB layouts
├── kokoro-v0_19.onnx          # Kokoro TTS Engine (Model)
├── voices.bin                 # Kokoro Expressive Voice Packs
└── README.md                  # Project documentation