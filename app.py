from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Play, Gather, Dial
import os
import openai
import requests

app = Flask(__name__, static_folder="static")

# === Konfiguration ===
openai.api_key = "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"
elevenlabs_api_key = "sk_d719e2c9e7ff203762c7b229bf6d16e7215b99dc82147c2c"
voice_id = "Juhf0FPNgWSQ31o2ocR5"
forward_number = "+4915737737721"

# === Begrüßung abspielen ===
@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()
    response.play(url="https://thinkable-voicebot.onrender.com/static/greeting.mp3")
    gather = Gather(input='speech', timeout=5, speechTimeout='auto', action='/gather')
    gather.say("Was kann ich für dich tun?")
    response.append(gather)
    return str(response)

# === Nutzerantwort empfangen und KI-Antwort erzeugen ===
@app.route("/gather", methods=['POST'])
def gather():
    speech_input = request.form.get('SpeechResult', '')
    print("User sagte:", speech_input)

    if any(word in speech_input.lower() for word in ["termin", "demo", "mit jemandem sprechen", "call", "anruf", "telefonat"]):
        response = VoiceResponse()
        response.say("Ich verbinde dich jetzt weiter.")
        response.dial(forward_number)
        return str(response)

    # OpenAI GPT-4 Prompt
    system_prompt = """
    Du bist Thinkable, der freundliche KI-Assistent von Thinkkraft. Du kennst die Module des Angebots (Support-KI, Berichte, Terminentlastung, Dashboard usw.) 
    und den Erklärtext aus dem Video. Du beantwortest freundlich, souverän und klar alle Fragen zu Thinkkraft und gibst gerne Überblick oder Hilfe.
    Wenn jemand Interesse an einem Termin zeigt, leite weiter.
    """

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": speech_input}
        ]
    )
    ai_response = completion.choices[0].message.content

    # ElevenLabs Text-to-Speech
    audio_url = generate_tts(ai_response)

    response = VoiceResponse()
    response.play(audio_url)
    return str(response)

# === TTS Funktion (ElevenLabs API) ===
def generate_tts(text):
    tts_url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }
    response = requests.post(tts_url, json=payload, headers=headers)
    audio_path = "response.mp3"
    with open(audio_path, "wb") as f:
        f.write(response.content)
    return request.url_root + "static/response.mp3"

# === MP3-Dateien aus /static ausliefern ===
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# === Server starten (lokal) ===
if __name__ == "__main__":
    app.run(debug=True)
