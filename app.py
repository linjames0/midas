from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
import dotenv

# API key stored in environment variable
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# initialize context variables
bank_history = []
cardholder_history = []
conversation_history = ""
greeting = "Hello, I'm here to assist with credit card disputes. How can I help you today?"

bank_history.append("Bank: " + greeting)

# start of flask app
app = Flask(__name__)

# welcome menu
@app.route("/voice", methods=['GET', 'POST'])
def voice():
    global bank_history
    global cardholder_history
    global conversation_history

    # initialize Twilio response
    resp = VoiceResponse()

    # get user speech
    with resp.gather(input='speech', action='/handle-record', timeout=4) as gather:
            gather.say(greeting)

    return str(resp)

# main menu
@app.route("/handle-record", methods=['GET', 'POST'])
def handle_record():
    global bank_history
    global cardholder_history
    global conversation_history

    # initialize Twilio response
    resp = VoiceResponse()

    # get user speech
    if 'SpeechResult' in request.values:
        user_speech = request.values.get("SpeechResult")
    elif 'Digits' in request.values:
        user_speech = request.values.get("Digits")

    # add user speech to history
    cardholder_history.append("Cardholder: " + user_speech)
    conversation_history = "\n".join(bank_history[i] + " " + cardholder_history[i] for i in range(len(bank_history)))
    print(conversation_history)

    # take in the user input and return the AI answer
    answer = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "You are a world-class employee at a financial bank, and your only job is to handle credit card disputes. A person will come to you with their dispute and you will ask them the right questions in the right order. You start off asking for their name, then credit card number, then credit card reason codes, then transaction date, and finally whether they have any other questions. Please be curteous and patient and concise. If you determine that the situation is fully resolved and the cardholder has no more questions, reply with 'Have a good day.' at the end of your final sentence. Return the answer that best responds to the input."}, 
            {"role": "user", "content": "Conversation History: \n" + conversation_history.replace(user_speech, "") + "\nQuery: \n" + "Cardholder: " + user_speech}],
    )["choices"][0]["message"]['content']

    # add bank answer to history
    bank_history.append(answer)
    print(answer)

    # if it makes sense for the call to end, end it
    if user_speech.lower() == "quit" or "have a good day" in answer.lower():
        resp.say(answer[6:])
        return str(resp)
    
    # ask for the credit card number
    elif "credit card number" in answer.lower() and "credit card number" not in conversation_history.lower():
        with resp.gather(input="dtmf", action="/handle-record", num_digits=17) as gather:
            gather.say("Please enter your credit card number, followed by the pound key.")
    
    # continue with the conversation
    else:
        with resp.gather(input="speech", action="/handle-record", timeout=4) as gather:
            gather.say(answer[6:])

    return str(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))