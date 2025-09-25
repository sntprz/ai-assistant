import os
import json
import uuid
from datetime import datetime

import pandas as pd
from PyPDF2 import PdfReader
import docx
from markdown import markdown
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"
OUTPUT_DIR = "data/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Funciones de extracción de texto ---
def extract_text_pdf(file_path):
    text = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text).strip()

def extract_text_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()]).strip()

def extract_text_csv(file_path):
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    rows = []
    for _, row in df.iterrows():
        rows.append(" | ".join([f"{col}: {val}" for col, val in row.items()]))
    return "\n".join(rows).strip()

import json

def extract_text_json(file_path):
    def json_to_text(obj):
        
        if isinstance(obj, dict):
            # Concatenar cada clave y su valor
            parts = []
            for k, v in obj.items():
                parts.append(f"{k}: {json_to_text(v)}")
            return "\n".join(parts)
        elif isinstance(obj, list):
            # Convertir cada elemento de la lista
            return "\n".join([json_to_text(item) for item in obj])
        else:
            # Valores simples (str, int, float, bool, None)
            return str(obj)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = json_to_text(data)
    return text.strip()

def extract_text_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html = markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n").strip()

# --- Función para generar metadatos ---
def generate_metadata(file_name):
    return {
        "doc_id": str(uuid.uuid4()),
        "title": os.path.splitext(os.path.basename(file_name))[0],
        "date": datetime.now().isoformat(),
        "source": "user"
    }

# --- Función principal de ingestión ---
def ingest():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"corpus_{timestamp}.jsonl")

    corpus = []
    for root, _, files in os.walk(RAW_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            ext = file.lower()
            try:
                if ext.endswith(".pdf"):
                    text = extract_text_pdf(file_path)
                elif ext.endswith(".docx"):
                    text = extract_text_docx(file_path)
                elif ext.endswith(".csv"):
                    text = extract_text_csv(file_path)
                elif ext.endswith(".json"):
                    text = extract_text_json(file_path)
                elif ext.endswith(".md"):
                    text = extract_text_md(file_path)
                else:
                    print(f"Skipping unsupported file: {file_path}")
                    continue

                if not text:
                    print(f"No text extracted from {file_path}, skipping.")
                    continue

                metadata = generate_metadata(file)
                metadata["content"] = text
                corpus.append(metadata)
                print(f"Processed: {file_path}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    # Guardar todo en JSONL
    with open(output_file, "w", encoding="utf-8") as out_f:
        for doc in corpus:
            out_f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Ingestion complete. Output saved to {output_file}")

if __name__ == "__main__":
    ingest()
