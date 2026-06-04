# vectorstore.py
import os
from langchain_postgres import PGVector
from .config import embed_llm
from dotenv import load_dotenv
load_dotenv()
vectorstore = PGVector(
    embeddings=embed_llm,
    collection_name="medical_knowledge",
    connection=os.environ["DATABASE_URL"],   # must be postgresql+psycopg://...
    use_jsonb=True,
)