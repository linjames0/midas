from flask import Flask
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    # Respond to incoming phone calls with a custom message
    # Start our TwiML response
    resp = VoiceResponse()

    resp.say("Hello world!")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)