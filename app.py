from flask import Flask, request, Response
import openai
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, filename='calls.log', format='%(asctime)s %(message)s')

# Gesprächsverlauf
convo_history = []

@app.route("/webhook/voice", methods=["POST"])
def voice():
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Vicki">Hallo, ich bin Thinkable – die KI-Ansprechpartnerin von Thinkkraft. Wie kann ich dir helfen?</Say>
    <Gather input="speech" action="/webhook/process" method="POST" timeout="5" />
    <Say>Ich konnte dich leider nicht verstehen. Bitte versuche es noch einmal.</Say>
    <Redirect>/webhook/voice</Redirect>
</Response>"""
    return Response(twiml_response, mimetype="text/xml")


@app.route("/webhook/process", methods=["POST"])
def process():
    user_input = request.form.get("SpeechResult", "").strip()
    logging.info(f"User said: {user_input}")

    if not user_input:
        return redirect_response()

    # Wenn Termininteresse erkannt wird
    if any(keyword in user_input.lower() for keyword in ["democall", "demo-call", "demogespräch", "termin", "gründer", "founder"]):
        return Response("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Willst du, dass ich dich mit unserem Gründer Herrn Schwalbe verbinde?</Say>
    <Gather input="speech" action="/webhook/transfer" method="POST" timeout="5" />
    <Say>Okay, dann nicht. Ich bin trotzdem für dich da.</Say>
    <Redirect>/webhook/voice</Redirect>
</Response>""", mimetype="text/xml")

    # GPT-Antwort generieren
    convo_history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist Thinkable, die KI-Ansprechpartnerin von Thinkkraft. Sei hilfreich, freundlich, fachlich kompetent und unterstützend. Verweise auf das Video, wenn nötig."},
            *convo_history
        ]
    )
    ai_reply = response["choices"][0]["message"]["content"]
    convo_history.append({"role": "assistant", "content": ai_reply})

    # Antwort zurückgeben
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{ai_reply}</Say>
    <Redirect>/webhook/voice</Redirect>
</Response>"""
    return Response(twiml_response, mimetype="text/xml")


@app.route("/webhook/transfer", methods=["POST"])
def transfer():
    user_reply = request.form.get("SpeechResult", "").lower()
    logging.info(f"Transfer confirmation: {user_reply}")

    if "ja" in user_reply or "mach" in user_reply:
        twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Ich verbinde dich jetzt mit meinem Boss, Herrn Schwalbe. Einen Moment bitte.</Say>
    <Dial>+4915737737721</Dial>
</Response>"""
        return Response(twiml_response, mimetype="text/xml")
    else:
        return redirect_response()


def redirect_response():
    return Response("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Ich konnte dich nicht verstehen. Lass es uns noch einmal versuchen.</Say>
    <Redirect>/webhook/voice</Redirect>
</Response>""", mimetype="text/xml")


@app.route("/", methods=["GET"])
def home():
    return "Thinkable Voice Webhook läuft ✅"


if __name__ == "__main__":
    app.run(debug=True)
