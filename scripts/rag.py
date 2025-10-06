import time
import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from scripts.retrieve import retrieve
import langchain

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)
langchain.debug = True

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def build_prompt(query, passages):
    parts = []
    for idx, content in enumerate(passages, start=1):
        parts.append(f"[{idx}] \n{content}\n")
    prompt = (
        "You are a helpful assistant. Answer concisely using ONLY the provided passages.\n"
        "Cite passage indices like [1], [2] if helpful.\n\n"
        f"Question: {query}\n\n"
        "Passages:\n" + "\n".join(parts) + "\nAnswer:"
    )
    return prompt

def call_gemini(prompt, temperature=0.1, model="gemini-2.5-flash"):
    llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
    resp = llm.invoke(prompt)
    logger.debug(resp.content)
    return resp.content

def answer_query(query, top_k=5, model="gemini-2.5-flash"):
    t0 = time.time()
    passages = retrieve(query, top_k=top_k)
    prompt = build_prompt(query, passages)
    answer = call_gemini(prompt, model=model)
    logger.debug(answer)
    latency = int((time.time() - t0) * 1000)
    return {"answer": answer, "sources": passages, "latency_ms": latency}
