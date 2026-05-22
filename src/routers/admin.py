from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.database.connection import get_db
from src.database.models import ClassificationRule
from src.routers.auth import verify_token
from src.database.models import User


router = APIRouter(prefix="/admin", tags=["Admin"])

class RuleCreateRequest(BaseModel):
    sector: Optional[str] = None
    keyword: Optional[str] = None
    automated_decision: Optional[bool] = None
    processes_personal_data: Optional[bool] = None
    interacts_with_humans: Optional[bool] = None
    risk_tier: str
    justification_template: str
    priority: int = 10

class RuleUpdateRequest(BaseModel):
    sector: Optional[str] = None
    keyword: Optional[str] = None
    automated_decision: Optional[bool] = None
    processes_personal_data: Optional[bool] = None
    interacts_with_humans: Optional[bool] = None
    risk_tier: Optional[str] = None
    justification_template: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class RuleResponse(BaseModel):
    id: int
    sector: Optional[str]
    keyword: Optional[str]
    automated_decision: Optional[bool]
    processes_personal_data: Optional[bool]
    interacts_with_humans: Optional[bool]
    risk_tier: str
    justification_template: str
    priority: int
    is_active: bool

    class Config:
        from_attributes = True
      
      
@router.get("/rules", response_model=list[RuleResponse])
def list_rules(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    query = db.query(ClassificationRule)
    if not include_inactive:
        query = query.filter(ClassificationRule.is_active == True)
    rules = query.order_by(ClassificationRule.priority.asc()).all()
    return rules


@router.post("/rules", response_model=RuleResponse)
def create_rule(request: RuleCreateRequest, db: Session = Depends(get_db)):
    if not request.sector and not request.keyword and not request.interacts_with_humans:
        raise HTTPException(
            status_code=400,
            detail="Rule must have at least one condition: sector, keyword, or interacts_with_humans"
        )

    rule = ClassificationRule(
        sector=request.sector,
        keyword=request.keyword,
        automated_decision=request.automated_decision,
        processes_personal_data=request.processes_personal_data,
        interacts_with_humans=request.interacts_with_humans,
        risk_tier=request.risk_tier,
        justification_template=request.justification_template,
        priority=request.priority
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/rules/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, request: RuleUpdateRequest, db: Session = Depends(get_db)):
    rule = db.query(ClassificationRule).filter(ClassificationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    updates = request.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}", response_model=RuleResponse)
def deactivate_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(ClassificationRule).filter(ClassificationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    rule.is_active = False
    db.commit()
    db.refresh(rule)
    return rule