import openai
import os
import dotenv
from twilio.rest import Client

# API key stored in environment variable
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# twilio set up
twilio_phone_number = "18444275958"

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

bank_history = []
cardholder_history = []
initial_prompt = "Bank: Hi! How can I help you today?"
text = "Cardholder: " + input(initial_prompt + "\n")

bank_history.append(initial_prompt)
cardholder_history.append(text)

conversation_history = "\n".join(bank_history + cardholder_history)

disputing = True
while disputing:

        answer = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a world-class employee at a financial bank, and your only job is to handle credit card disputes. A person will come to you with their dispute and you will ask them the right questions in the right order. You start off asking for their name, then credit card number, then credit card reason codes, then transaction date, and finally whether they have any other questions. Please be curteous and patient and concise. If you determine that the situation is fully resolved and the cardholder has no more questions, reply with 'Have a good day.' at the end of your final sentence. Return the answer that best responds to the input."}, 
                {"role": "user", "content": "Conversation History: \n" + conversation_history.replace(text, "") + "\nQuery: \n" + text}],
        )["choices"][0]["message"]['content']

        text = "Cardholder: " + input(answer + "\n")
        if text == "quit":
                disputing = False
        if answer == "Have a good day.":
                disputing = False

        bank_history.append(answer)
        cardholder_history.append(text)

        conversation_history = "\n".join(bank_history[i] + " " + cardholder_history[i] for i in range(len(bank_history)))
        print(conversation_history)



