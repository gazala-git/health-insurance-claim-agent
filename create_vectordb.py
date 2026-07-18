from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import (
    EMBEDDING_MODEL,
    HANDBOOK_PATH,
    VECTOR_DB_PATH,
)

handbook_folder = Path(HANDBOOK_PATH)

documents = []

for file in handbook_folder.glob("*.md"):

    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    documents.append(
        Document(
            page_content=text,
            metadata={"source": file.name}
        )
    )

print(f"Loaded {len(documents)} handbook files.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks.")

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=VECTOR_DB_PATH
)

print("Vector database created successfully!")