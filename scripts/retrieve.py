import os, json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
import db.connection as db
import logging

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_embedding_gemini(text: str):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector = embeddings.embed_query(text)
    return vector

def retrieve(query: str, top_k: int = 5):
    supabase = db.init_db()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents",
    )
    docs = vector_store.similarity_search(query, k=top_k)
    return list(map(lambda doc: doc.page_content, docs))