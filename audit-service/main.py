from fastapi import FastAPI
from pydantic import BaseModel
from audit_service import init_db, insert_audit_log

app = FastAPI(title="UniGuard AI - Audit Service")

class AuditRequest(BaseModel):
    role: str
    query: str
    intent: str
    risk_level: str
    confidence_score: str
    decision: str
    needs_review: bool

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/audit", summary="Create Audit Log")
def create_audit(req: AuditRequest):
    insert_audit_log(
        role=req.role,
        query=req.query,
        intent=req.intent,
        risk_level=req.risk_level,
        confidence_score=req.confidence_score,
        decision=req.decision,
        needs_review=req.needs_review
    )
    return {"status": "success"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "audit-service"}
