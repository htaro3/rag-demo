import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the API with the key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash")
chat = model.start_chat(history=[])
response = chat.send_message("こんにちは！AIの自己紹介をして")
print(response.text)