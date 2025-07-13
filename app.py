from flask import Flask, request, redirect
from twilio.twiml.voice_response import VoiceResponse, Gather
import logging

app = Flask(__name__)

# Logging aktivieren (für Debugging)
logging.basicConfig(level=logging.INFO)

@app.route("/voice", methods=["GET", "POST"])
def voice():
    response = VoiceResponse()

    # Spracheingabe vom User holen
    speech_result = request.values.get('SpeechResult', '').lower()
    logging.info(f"Nutzer sagte: {speech_result}")

    # Wenn bereits etwas gesagt wurde
    if speech_result:
        if any(kw in speech_result for kw in ["termin", "demo", "gründer", "founder", "meeting"]):
            gather = Gather(input='speech', action='/confirm', timeout=3)
            gather.say("Möchtest du mit meinem Boss Herrn Schwalbe verbunden werden?")
            response.append(gather)
            response.redirect('/voice')  # Wenn keine Antwort kommt
        else:
            response.say("Okay, danke für dein Interesse. Wenn du mehr erfahren willst, schreib uns gerne eine Nachricht oder buche dir einen Termin.")
            response.hangup()
    else:
        # Erste Begrüßung
        gather = Gather(input='speech', action='/voice', timeout=3)
        gather.say("Hey! Ich bin Thinkable von Thinkkraft. Wie kann ich dir helfen?")
        response.append(gather)
        response.redirect('/voice')

    return str(response)

@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    response = VoiceResponse()
    speech_result = request.values.get('SpeechResult', '').lower()
    logging.info(f"Bestätigung erkannt: {speech_result}")

    if any(kw in speech_result for kw in ["ja", "klar", "bitte", "mach das", "unbedingt"]):
        response.say("Ich verbinde dich jetzt mit meinem Boss Herrn Schwalbe. Einen Moment bitte.")
        response.dial("+4915737737721")
    else:
        response.say("Alles klar. Dann wünsche ich dir noch einen erfolgreichen Tag!")
        response.hangup()

    return str(response)

@app.route("/", methods=["GET"])
def home():
    return "Thinkable Voicebot läuft 🦾", 200
