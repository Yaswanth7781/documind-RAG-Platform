from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional
from audit_service import init_db, insert_audit_log, SessionLocal
from shared.models.audit_models import AuditLog
from shared.core.security import verify_token

app = FastAPI(title="UniGuard AI - Audit Service")

class AuditRequest(BaseModel):
    role: str
    query: str
    intent: str
    risk_level: str
    confidence_score: str
    decision: str
    needs_review: bool
    reg_no: Optional[str] = None

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
        needs_review=req.needs_review,
        reg_no=req.reg_no
    )
    return {"status": "success"}

@app.get("/audit/list", summary="List Audit Logs")
def get_audit_logs(token_payload: dict = Depends(verify_token)):
    db = SessionLocal()
    try:
        # Show ONLY high risk queries in compliance audit logs
        logs = db.query(AuditLog).filter(AuditLog.risk_level.ilike('high')).order_by(AuditLog.id.desc()).all()
        return {
            "status": "success",
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "user_role": log.user_role,
                    "reg_no": log.reg_no,
                    "query": log.query,
                    "intent": log.intent,
                    "risk_level": log.risk_level,
                    "confidence_score": log.confidence_score,
                    "decision_summary": log.decision_summary,
                    "needs_review": bool(log.needs_review)
                }
                for log in logs
            ]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "audit-service"}
