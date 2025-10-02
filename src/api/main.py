# src/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from scripts.rag import answer_query

app = FastAPI()

class QueryIn(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=50)

@app.post("/query")
def query_endpoint(payload: QueryIn):
    try:
        res = answer_query(
            payload.query,
            top_k=payload.top_k,
        )
        return {"answer": res["answer"], "sources": res["sources"], "latency_ms": res["latency_ms"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
