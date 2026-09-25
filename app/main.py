"""
FastAPI app exposing the RAG + agent pipeline as a single /ask endpoint.
Same pattern as the churn-prediction API: one focused route, pydantic
request/response models, health check for deployment platforms like Render.
"""

from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agent import answer_question

app = FastAPI(title="ERP RAG Agent", version="0.1.0")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    route: str
    sources: list[dict]


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    result = answer_question(request.question)
    return result
