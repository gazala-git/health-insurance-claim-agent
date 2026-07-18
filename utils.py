import os

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import (
    GROQ_API_KEY,
    MODEL_NAME,
    EMBEDDING_MODEL,
    VECTOR_DB_PATH,
)

# ----------------------------------
# LLM Selection
# ----------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

if LLM_PROVIDER == "gemini":
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
    )
else:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=MODEL_NAME,
        temperature=0,
    )

# ----------------------------------
# Embedding Model
# ----------------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

# ----------------------------------
# Vector Database
# ----------------------------------
vector_db = Chroma(
    persist_directory=VECTOR_DB_PATH,
    embedding_function=embedding_model,
)