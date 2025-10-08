from fastapi import FastAPI, Request
import requests, os, json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

load_dotenv()
app = FastAPI()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- LangChain setup ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
prompt = PromptTemplate.from_template(
    "You are a helpful WhatsApp AI assistant. Use conversation history to respond naturally.\n\n{chat_history}\nUser: {input}\nAI:"
)
chain = ConversationChain(llm=llm, memory=memory, prompt=prompt)

@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    return "Verification failed"

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        sender = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

        # --- LangChain handles the message ---
        reply = chain.run(message).strip()

        # --- Send reply back via WhatsApp Cloud API ---
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": sender,
            "text": {"body": reply}
        }
        requests.post(url, json=payload, headers=headers)

    except Exception as e:
        print("Error:", e)
    return "ok"
