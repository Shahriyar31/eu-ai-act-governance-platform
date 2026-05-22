from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.ai.rag_engine import answer_compliance_question

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

class ComplianceQuestion(BaseModel):
    question: str

class ComplianceAnswer(BaseModel):
    question: str
    answer: str
    sources: list[dict]

@router.post("/ask", response_model=ComplianceAnswer)
def ask_compliance_question(request: ComplianceQuestion):
    try:
        result = answer_compliance_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))