from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/webhook/voice", methods=["POST"])
def voice_webhook():
    vr = VoiceResponse()
    vr.say("Hallo, hier ist Thinkable – ich bin online und hoere dich.", language="de-DE", voice="Polly.Vicki")
    return Response(str(vr), mimetype="application/xml")

# Render sucht standardmäßig nach 'app'
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
