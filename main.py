# main.py
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI, Form, Response
from twilio.rest import Client
from chatbot import get_gemini_response

# Initialize FastAPI app
app = FastAPI()

# Initialize Twilio client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
from_whatsapp_number = os.getenv("FROM_WHATSAPP_NUMBER")


@app.get("/")
def read_root():
    return {"Status": "WhatsApp bot is running!"}


@app.post("/webhook")
def webhook(Body: str = Form(), From: str = Form()):
    """
    This is the webhook endpoint that receives incoming messages from Twilio.
    - Body: The text of the incoming message.
    - From: The user's WhatsApp number (e.g., whatsapp:+919876543210)
    """
    print(f"Received message: '{Body}' from {From}")

    # 1. Get the intelligent response from our chatbot logic
    bot_response = get_gemini_response(Body)
    print(f"Generated response: '{bot_response}'")

    # 2. Send the response back to the user via Twilio
    try:
        client.messages.create(
            from_=from_whatsapp_number,
            body=bot_response,
            to=From
        )
    except Exception as e:
        print(f"Error sending message: {e}")

    # Return an empty response to Twilio to acknowledge receipt
    return Response(status_code=204)