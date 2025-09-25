"""
ingest_and_embed.py

Pipeline unificado para:
1. Ingestar documentos (PDF, DOCX, CSV, JSON, Markdown, TXT)
2. Hacer chunking configurable
3. Generar embeddings usando Gemini (LangChain)
4. Subirlos en batch a Supabase (pgvector)

Requisitos:
- .env con SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GOOGLE_API_KEY
- Tabla 'documents' en Supabase con columna 'embedding' (pgvector)
"""

import os
import uuid
from datetime import datetime
from getpass import getpass

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, CSVLoader, TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import db.connection as db
from supabase import Client
from langchain_community.document_loaders import JSONLoader

# -----------------------------
# Utilidades
# -----------------------------
def json_to_text(obj):
    """Convert any JSON-like structure (dict/list/scalars) into readable text."""
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            parts.append(f"{k}: {json_to_text(v)}")
        return "\n".join(parts)
    if isinstance(obj, list):
        return "\n".join([json_to_text(item) for item in obj])
    return str(obj)

# -----------------------------
# Config y entorno
# -----------------------------
load_dotenv()

RAW_DIR = os.getenv("RAW_DIR", "data/raw")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE_CHARS", 1200))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP_CHARS", 200))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# -----------------------------
# Inicializar Supabase
# -----------------------------
supabase: Client = db.init_db()

# -----------------------------
# Inicializar embeddings Gemini (LangChain)
# -----------------------------
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# -----------------------------
# Carga de documentos según extensión
# -----------------------------
def load_file(file_path: str):
    ext = file_path.lower()
    try:
        if ext.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif ext.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        elif ext.endswith(".csv"):
            loader = CSVLoader(file_path, encoding="utf-8")
        elif ext.endswith(".jsonl"):
            # JSON Lines: cada línea es un objeto JSON independiente
            loader = JSONLoader(file_path, jq_schema=".", text_content=False, json_lines=True)
        elif ext.endswith(".json"):
            # JSON genérico: cargamos el objeto completo (dict o list) sin asumir esquema
            loader = JSONLoader(file_path, jq_schema=".", text_content=False)
        elif ext.endswith(".md"):
            # Usamos TextLoader para Markdown para evitar dependencia extra de 'unstructured'
            loader = TextLoader(file_path, encoding="utf-8")
        elif ext.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            print(f"[SKIP] Formato no soportado: {file_path}")
            return []
        docs = loader.load()
        # Si es JSON/JSONL, convertimos dict/list a texto legible de forma genérica
        if ext.endswith(".json") or ext.endswith(".jsonl"):
            for d in docs:
                if not isinstance(d.page_content, str):
                    d.page_content = json_to_text(d.page_content).strip()
        # Asegurar que page_content sea string para el splitter
        for d in docs:
            if not isinstance(d.page_content, str):
                try:
                    d.page_content = str(d.page_content)
                except Exception:
                    d.page_content = ""
        return docs
    except Exception as e:
        print(f"[ERROR] Cargando {file_path}: {e}")
        return []

# -----------------------------
# Chunking de documentos
# -----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

def process_documents(raw_dir=RAW_DIR):
    all_docs = []
    for root, _, files in os.walk(raw_dir):
        for file in files:
            file_path = os.path.join(root, file)
            docs = load_file(file_path)
            if not docs:
                continue
            for doc in docs:
                # metadata base
                doc.metadata["doc_id"] = str(uuid.uuid4())
                doc.metadata["title"] = os.path.splitext(file)[0]
                doc.metadata["source"] = "user"
                doc.metadata["created_at"] = datetime.utcnow().isoformat()
            # chunking
            chunks = text_splitter.split_documents(docs)
            all_docs.extend(chunks)
            print(f"[INFO] {file_path}: {len(chunks)} chunks")
    return all_docs

# -----------------------------
# Subida a Supabase
# -----------------------------
def upsert_documents(docs):
    total = len(docs)
    for i in range(0, total, BATCH_SIZE):
        batch = docs[i:i+BATCH_SIZE]
        texts = [d.page_content for d in batch]
        # generar embeddings
        try:
            embs = embeddings.embed_documents(texts)
        except Exception as e:
            print(f"[ERROR] Generando embeddings batch {i//BATCH_SIZE + 1}: {e}")
            raise
        # construir rows
        rows = []
        for doc, emb in zip(batch, embs):
            # UUIDv5 estable por chunk basado en contenido y título
            content_for_id = f"{doc.metadata.get('title', '')}-{doc.page_content}"
            stable_uuid = uuid.uuid5(uuid.NAMESPACE_URL, content_for_id)
            row = {
                "doc_id": str(stable_uuid),
                "title": doc.metadata.get("title", ""),
                "content": doc.page_content,
                "embedding": emb,
                "source": doc.metadata.get("source", ""),
                "date": doc.metadata.get("created_at")
            }
            rows.append(row)
        # bulk upsert
        res = supabase.table("documents").upsert(rows, on_conflict="doc_id").execute()
        # SDK v2 devuelve objeto pydantic con .data y .error, no status_code
        if getattr(res, "error", None):
            raise RuntimeError(f"Error en Supabase: {res.error}")
        print(f"[INFO] Upserted batch {i//BATCH_SIZE + 1} ({len(batch)} docs) - inserted: {len(res.data) if getattr(res, 'data', None) else 'unknown'}")

# -----------------------------
# Pipeline principal
# -----------------------------
if __name__ == "__main__":
    print("[INFO] Cargando y procesando documentos...")
    docs = process_documents()
    print(f"[INFO] Total chunks generados: {len(docs)}")
    if docs:
        upsert_documents(docs)
        print("[INFO] Proceso completado: documentos subidos a Supabase.")
    else:
        print("[INFO] No se generaron documentos para subir.")