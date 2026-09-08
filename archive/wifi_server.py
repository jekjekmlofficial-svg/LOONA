from flask import Flask, jsonify
import socket
import logging

app = Flask(__name__)

# Default na utos
current_command = "STANDBY"

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
    # Ito ang eksaktong JSON format na hihigupin ng ESP32
    response = {
        "device": "LOONA_AI_CORE",
        "action": current_command,
        "speed": 80
    }
    
    # Reset sa STANDBY pagkatapos ipadala
    if current_command != "STANDBY":
        print(f"📡 Naipadala ang signal sa ESP32: {current_command}")
        current_command = "STANDBY"
        
    return jsonify(response)

# Temporary manual trigger para sa testing
@app.route('/test/trigger', methods=['GET'])
def test_trigger():
    global current_command
    current_command = "MOVE_FORWARD"
    return "✅ Success! Ang command ay naging MOVE_FORWARD. I-refresh ang /loona/status para makita ang pagbabago."

if __name__ == '__main__':
    # Pampatahimik ng default logs ng Flask
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    laptop_ip = get_ip()
    print("=========================================")
    print("🌐 LOONA Wi-Fi Server Online!")
    print(f"👉 ESP32 Connection Link: http://{laptop_ip}:5000/loona/status")
    print("=========================================")
    
    app.run(host='0.0.0.0', port=5000)