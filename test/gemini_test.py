import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the API with the key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# model = genai.GenerativeModel("models/gemini-1.5-flash")
model = genai.GenerativeModel("models/text-embedding-004")
chat = model.start_chat(history=[])
response = chat.send_message("こんにちは！今日は何の日？")
print(response.text)