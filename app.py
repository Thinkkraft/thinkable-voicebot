from flask import Flask, request, send_from_directory, make_response
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ElevenLabs-Konfiguration
ELEVENLABS_API_KEY = "sk_d719e2c9e7ff203762c7b229bf6d16e7215b99dc82147c2c"
VOICE_ID = "Juhf0FPNgWSQ31o2ocR5"

# OpenAI-Konfiguration
OPENAI_API_KEY = "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"

# Stelle sicher, dass der static-Ordner existiert
os.makedirs("static", exist_ok=True)

# Sprachsynthese mit ElevenLabs
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
        return f"/static/{filename}"
    else:
        return None

# Frage an ChatGPT senden
def ask_openai(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = []

    # Boss-Erkennung
    if "tommy" in prompt.lower() or "boss" in prompt.lower():
        messages.append({
            "role": "system",
            "content": "Begrüße Tommy als 'Hallo Boss, was kann ich für Sie tun?'"
        })
    else:
        messages.append({
            "role": "system",
            "content": "Du bist Thinkable, ein freundlicher KI-Assistent für Telefonate. Antworte kurz, hilfreich und mit positiver Ausstrahlung."
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Es gab ein Problem mit der Antwort."

# Webhook-Endpunkt für Twilio
@app.route("/webhook/voice", methods=["POST"])
def voice_webhook():
    user_input = request.form.get("SpeechResult", "Hallo")
    print(f"User said: {user_input}")

    gpt_response = ask_openai(user_input)
    audio_path = text_to_speech(gpt_response)

    if not audio_path:
        gpt_response = "Tut mir leid, ich konnte gerade nicht antworten."
        audio_path = text_to_speech(gpt_response)

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://thinkable-voicebot.onrender.com{audio_path}</Play>
</Response>"""

    response = make_response(twiml_response)
    response.headers["Content-Type"] = "text/xml"
    return response

# Dient dazu, Audiodateien aus /static zu liefern
@app.route("/static/<path:filename>")
def serve_audio(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True)
