from fastapi import FastAPI, HTTPException
from shared.models.request_models import ChatRequest
from shared.models.response_models import ChatResponse, ChatCitation
from workflow_service import execute_policy_workflow

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UniGuard AI - Chat Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    "/ai/chat",
    response_model=ChatResponse,
    summary="Multi-Agent Policy Chat"
)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = execute_policy_workflow(
            prompt=request.prompt, 
            user_role=request.role,
            history=request.history,
            reg_no=request.reg_no
        )
        
        citations = []
        for meta in result.get("metadatas", []):
            if meta and "source" in meta:
                citations.append(ChatCitation(
                    source=meta["source"], 
                    chunk=int(meta.get("chunk", 0)),
                    page=int(meta.get("page", 0)),
                    similarity=float(meta.get("similarity_score", 0.0))
                ))

        return ChatResponse(
            response=result["response"], 
            citations=citations,
            workflow_steps=result["workflow_steps"],
            confidence_score=result["confidence_score"],
            needs_review=result["needs_review"],
            intent_category=result.get("intent_category", "General"),
            intent_priority=result.get("intent_priority", "Low")
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred in workflow: {exc}",
        )

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "chat-service"}
