from flask import Flask, request, send_file
from twilio.twiml.voice_response import VoiceResponse, Play, Gather, Dial
import openai
import requests
import os

app = Flask(__name__)

# === Konfiguration ===
openai.api_key = "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"
elevenlabs_api_key = "sk_d719e2c9e7ff203762c7b229bf6d16e7215b99dc82147c2c"
voice_id = "Juhf0FPNgWSQ31o2ocR5"
forward_number = "+4915737737721"

# === Start: Begrüßung direkt per ElevenLabs-Sprache ===
@app.route("/voice", methods=["POST"])
def voice():
    greeting_text = "Hey Boss, willkommen zurück bei Thinkkraft. Was kann ich heute für dich tun?"

    audio_url = generate_tts_and_serve(greeting_text)

    response = VoiceResponse()
    response.play(audio_url)

    gather = Gather(input='speech', timeout=5, speechTimeout='auto', action='/gather')
    gather.say("Ich höre zu.")
    response.append(gather)

    return str(response)

# === Nutzerantwort empfangen und KI-Antwort erzeugen ===
@app.route("/gather", methods=["POST"])
def gather():
    speech_input = request.form.get("SpeechResult", "")
    print("User sagte:", speech_input)

    if any(word in speech_input.lower() for word in ["termin", "demo", "call", "anruf", "telefonat", "mit jemandem sprechen"]):
        response = VoiceResponse()
        response.say("Ich verbinde dich jetzt weiter.")
        response.dial(forward_number)
        return str(response)

    # Systemprompt mit Wissen über Thinkable
    system_prompt = """
    Du bist Thinkable, die freundliche KI-Assistentin von Thinkkraft. 
    Du kennst die fünf Module von Thinkkraft (Support-KI, Berichte, Terminentlastung, Einarbeitung, Dashboard) 
    und den Inhalt aus dem Begrüßungsvideo. 
    Du sprichst souverän, smart, locker und respektvoll mit dem Anrufer, nennst ihn bei Bedarf „Boss“. 
    Wenn jemand Interesse zeigt, einen Termin zu machen, leite ihn weiter.
    """

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": speech_input}
        ]
    )

    ai_response = completion.choices[0].message.content
    audio_url = generate_tts_and_serve(ai_response)

    response = VoiceResponse()
    response.play(audio_url)
    return str(response)

# === ElevenLabs Text-to-Speech Funktion ===
def generate_tts_and_serve(text):
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "accept": "audio/mpeg",
            "xi-api-key": elevenlabs_api_key,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
    )

    audio_path = "response.mp3"
    with open(audio_path, "wb") as f:
        f.write(response.content)

    return request.url_root + "response.mp3"

# === Audio-Datei ausliefern (für Twilio) ===
@app.route("/response.mp3")
def serve_response():
    return send_file("response.mp3", mimetype="audio/mpeg")

# === Server starten ===
if __name__ == "__main__":
    app.run(debug=True)
