import time
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from scripts.retrieve import retrieve

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def build_prompt(query, passages):
    parts = []
    for idx, p in enumerate(passages, start=1):
        doc_id = p.get("doc_id")
        title = p.get("title")
        source = p.get("source")
        score = p.get("score")
        text = p.get("content")
        parts.append(f"[{idx}] (doc:{doc_id}, title:{title}, source:{source}, score:{score})\n{text}\n")
    prompt = (
        "You are a helpful assistant. Answer concisely using ONLY the provided passages.\n"
        "Cite passage indices like [1], [2] if helpful. If the answer cannot be found, say you don't know.\n\n"
        f"Question: {query}\n\n"
        "Passages:\n" + "\n".join(parts) + "\nAnswer:"
    )
    return prompt

def call_gemini(prompt, max_tokens=256, temperature=0.1, model="gemini-2.0-flash"):
    llm = ChatGoogleGenerativeAI(model=model, temperature=temperature, max_output_tokens=max_tokens)
    resp = llm.invoke(prompt)
    return resp.content

def answer_query(query, top_k=5, model="gemini-2.0-flash"):
    t0 = time.time()
    passages = retrieve(query, top_k=top_k)
    prompt = build_prompt(query, passages)
    answer = call_gemini(prompt, model=model)
    latency = int((time.time() - t0) * 1000)
    return {"answer": answer, "sources": passages, "latency_ms": latency}
