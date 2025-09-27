from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel
from rag_chain import answer_question

app = FastAPI(title="Minimal RAG API", version="0.1.0")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    """
    Simple RAG endpoint:
    - Input: question
    - Output: answer + citations
    """
    result = answer_question(req.question)
    return AskResponse(answer=result["answer"], sources=result["sources"])
