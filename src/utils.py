from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import (
    GROQ_API_KEY,
    MODEL_NAME,
    EMBEDDING_MODEL,
    VECTOR_DB_PATH,
)

# ----------------------------------
# LLM
# ----------------------------------
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