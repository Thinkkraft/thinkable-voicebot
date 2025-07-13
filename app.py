from flask import Flask, request, send_from_directory, make_response
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Konfiguriere deine ElevenLabs-Daten
ELEVENLABS_API_KEY = "sk_d719e2c9e7ff203762c7b229bf6d16e7215b99dc82147c2c"
VOICE_ID = "Juhf0FPNgWSQ31o2ocR5"

# Stelle sicher, dass der static-Ordner existiert
os.makedirs("static", exist_ok=True)

def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.8
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        filename = f"response_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        filepath = os.path.join("static", filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filename
    else:
        print("Fehler bei ElevenLabs:", response.text)
        return None

@app.route("/webhook/voice", methods=["POST"])
def voice_webhook():
    # Text den Thinkable sagen soll
    text = "Hallo Boss, wie geht es Ihnen heute? Was kann ich für Sie tun?"
    
    filename = text_to_speech(text)

    if filename:
        audio_url = f"https://{request.host}/static/{filename}"
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
</Response>"""
        response = make_response(twiml)
        response.headers["Content-Type"] = "text/xml"
        return response
    else:
        return "<Response><Say>Es gab einen Fehler beim Erzeugen der Antwort.</Say></Response>", 500

# Route zum Testen (optional)
@app.route("/")
def home():
    return "Thinkable VoiceBot läuft!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
