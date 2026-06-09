from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shared.core.security import create_access_token
from shared.core.config import ADMIN_PIN

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UniGuard AI - Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    pin: str

@app.post("/auth/login", summary="Admin Login Endpoint")
def login(req: LoginRequest):
    if req.pin == ADMIN_PIN:
        token = create_access_token({"role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid admin PIN")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth-service"}
