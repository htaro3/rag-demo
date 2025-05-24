# config.py
import os
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# --- .envの読み込み ---
load_dotenv()

# --- Google Gemini APIキー設定 ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Chroma DB 設定 ---
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/chroma_db')
COLLECTION_NAME = "rag_docs"

client = chromadb.PersistentClient(
    path=DB_PATH,
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(COLLECTION_NAME)
