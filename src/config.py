import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = "llama-3.3-70b-versatile"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

VECTOR_DB_PATH = "data/vectordb"

HANDBOOK_PATH = "data/handbooks"