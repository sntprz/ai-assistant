import os, json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
import db.connection as db

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
    docs_with_scores = vector_store.similarity_search_with_relevance_scores(query, k=top_k)
    results = []
    for doc, score in docs_with_scores:
        md = doc.metadata or {}
        results.append({
            "doc_id": md.get("doc_id"),
            "title": md.get("title"),
            "source": md.get("source"),
            "date": md.get("created_at") or md.get("date"),
            "content": doc.page_content,
            "score": score,
        })
    return results
