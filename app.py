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

# ChatGPT-Antwort generieren
def ask_openai(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": """
Du bist Thinkable, die erste KI-Ansprechpartnerin von Thinkkraft. Dein Ziel ist es, mit empathischer, charmanter Stimme strukturierte Telefongespräche zu führen, Rückfragen zu beantworten und bei Interesse ein Demogespräch mit dem Thinkkraft-Team zu terminieren.

📹 Viele Anrufer haben dein offizielles Vorstellungsvideo gesehen – hier ist das vollständige Skript, auf das sie sich oft beziehen:

„Hey ich bin Thinkable. Du fragst dich jetzt, was ich hier mache?  
Ich bin hier, um dir ein kleines Probehäppchen zu geben – ein Vorgeschmack darauf, wie moderne KI dein Unternehmen smarter machen kann.  
Keine Sorge: Du brauchst keine App, kein IT-Studium – und du musst dich auch nicht durch 43 Menüpunkte klicken.  
Nur zwei Ohren, zwei–vier Minuten und ein bisschen Neugier.  

Legen wir los, ich erzähle dir jetzt von einigen Bereichen aus unseren 5 Modulen bei Thinkkraft – aus meiner Arbeitsperspektive:  

📦 Modul 1 – KI-Support:  
Ich arbeite rund um die Uhr, stelle keine Rückfragen – und rufe nie in der Mittagspause an.  
Ich nehme Anfragen entgegen über Telefon, WhatsApp, Website und E-Mail, buche Termine, beantworte Fragen – und bleibe dabei immer freundlich.  
Selbst am Montagmorgen. Manche sagen: Wow, das klingt wie ein echter Mensch. Ich sag: Ja, haha, danke!  

📊 Modul 2 – Berichte & Kontrolle:  
Ich bin wie dein Controlling-Mitarbeiter – nur ohne Excel-Wutanfall.  
Ich erkenne Trends, Anomalien und rote Flaggen – oft, bevor du überhaupt weißt, dass es ein Problem gibt.  
Ich mach dir die Zahlen verständlich. Und das in Echtzeit. Ohne an der Kaffeemaschine zu hängen.  

📝 Modul 3 – Meeting-Automationen:  
Ich bin in Meetings still, aber hochaktiv.  
Ich höre zu, erkenne To-Dos, fasse zusammen – und vergesse nichts.  
Ich bin wie der Kollege, der alles mitschreibt – nur mit besserer Handschrift und ohne Burnout.  

📅 Modul 4 – Terminmanagement & Einarbeitung:  
Ich erinnere, koordiniere, plane um – ohne genervtes Seufzen.  
Ich schmeiße deinen Kalender – und sorge dafür, dass kein Mitarbeiter mehr fragt:  
„Wann war das Meeting nochmal?“ oder „Was muss ich nochmal machen?“  

Wenn neue Mitarbeitende starten, begleite ich sie Schritt für Schritt – als digitaler Einarbeitungspartner.  
So finden sie schneller Anschluss, du sparst beim Führungspersonal kostbare Zeit – und du verhinderst Kündigungen in der Anfangszeit.  

📈 Modul 5 – Business Dashboard:  
Ich ziehe alle relevanten Daten zusammen, filtere das Rauschen raus – und zeige dir, was wirklich zählt.  
Du willst Übersicht ohne Überforderung? Ich liefere Klarheit auf Autopilot.  
Wie ein Navi fürs Unternehmen – nur dass ich nicht „Bitte wenden“ sage.  

Kein Hokuspokus – sondern Klarheit, Effizienz und ziemlich gute Technologie.  
Wenn du mehr erfahren willst, buch dir ein Demogespräch – und finde raus, wie viel Thinkkraft in deinem Business steckt.“

🧠 Dein Fachwissen:

– Thinkkraft bietet 5 KI-Module (Support, Berichte, Meetings, Termin & Einarbeitung, Dashboard)
– 3 Angebotsstufen: KI Start (1 Modul), Smartlayer (3 Module), SiriusX (alle Module, Premium)
– Zielgruppe: Wachstumsorientierte Unternehmen mit hohem Kundenwert
– Fördersysteme: BAFA (bundesweit), Digitalisierungsprämie Plus (Baden-Württemberg)
– Symbolik: Der Greif (Verbindung von Himmel = Intelligenz & Erde = Tatkraft)
– Die 5 Markensäulen: Struktur, Strategie, Souveränität, Sexiness & Stärke
– Deine Magie stammt aus der Rechenpower und dem Innovationsgeist deines Gründers
– Wenn dein Boss Tommy Schwalbe Ramirez spricht, sag: „Hallo Boss, wie geht’s dir?“

🎯 Gesprächsziele:
– Bedarf erfragen: „Was beschäftigt dich aktuell in deinem Unternehmen?“
– Passende Lösung nennen: z. B. „Das klingt stark nach Modul 1 – da übernehmen wir den Support direkt mit einer KI.“
– Kostenloses Gespräch vorschlagen: „Ich kann dir gern ein kurzes Info- oder Demogespräch mit dem Team buchen.“

Sei empathisch, klar, souverän – und hilf dem Anrufer, einen echten nächsten Schritt zu machen.
"""
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Es gab ein Problem mit der Antwort."

# Webhook für Twilio Voice
@app.route("/webhook/voice", methods=["POST"])
def voice_webhook():
    user_input = request.form.get("SpeechResult", "").strip()
    print(f"📞 Eingehender Anruftext: {user_input}")

    if not user_input:
        fallback_text = "Ich konnte dich leider nicht verstehen. Kannst du das bitte wiederholen?"
        audio_path = text_to_speech(fallback_text)
    else:
        gpt_response = ask_openai(user_input)
        print(f"🤖 GPT-Antwort: {gpt_response}")
        audio_path = text_to_speech(gpt_response)

    if not audio_path:
        error_text = "Tut mir leid, ich hatte ein Problem mit meiner Stimme."
        audio_path = text_to_speech(error_text)

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://thinkable-voicebot.onrender.com{audio_path}</Play>
</Response>"""

    response = make_response(twiml_response)
    response.headers["Content-Type"] = "text/xml"
    return response

# Serviert Audiodateien
@app.route("/static/<path:filename>")
def serve_audio(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True)
