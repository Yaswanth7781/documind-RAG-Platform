import os
import hashlib
import sqlite3
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shared.core.security import create_access_token
from shared.core.config import ADMIN_PIN

app = FastAPI(title="UniGuard AI - API Gateway")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite database setup for Auth
DB_DIR = os.getenv("DB_DIR", "./data" if not os.path.exists("/app/data") and os.name == "nt" else "/app/data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            reg_no TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

class SignupRequest(BaseModel):
    reg_no: str
    password: str
    role: str # Student, Faculty, Admin
    admin_pin: str = None

class LoginRequest(BaseModel):
    reg_no: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@app.post("/auth/signup", summary="User Signup Endpoint")
def signup(req: SignupRequest):
    role_norm = req.role.strip()
    if role_norm not in ["Student", "Faculty", "Admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be Student, Faculty, or Admin.")
        
    if role_norm == "Admin":
        if req.admin_pin != ADMIN_PIN:
            raise HTTPException(status_code=403, detail="Invalid admin security PIN")
            
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT reg_no FROM users WHERE reg_no = ?", (req.reg_no,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User with this Registration Number already exists.")
            
        pwd_hash = hash_password(req.password)
        # Store role matching role_norm
        cursor.execute("INSERT INTO users (reg_no, password_hash, role) VALUES (?, ?, ?)",
                       (req.reg_no, pwd_hash, role_norm))
        conn.commit()
        return {"status": "success", "message": "User registered successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/auth/login", summary="User Login Endpoint")
def login(req: LoginRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash, role FROM users WHERE reg_no = ?", (req.reg_no,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid Registration Number or Password")
            
        pwd_hash, role = row
        if hash_password(req.password) != pwd_hash:
            raise HTTPException(status_code=401, detail="Invalid Registration Number or Password")
            
        # Map 'Admin' to 'admin' for token checking compatibility
        token_role = "admin" if role == "Admin" else role.lower()
        token = create_access_token({"sub": req.reg_no, "role": token_role, "display_role": role})
        return {
            "access_token": token, 
            "token_type": "bearer", 
            "role": role, 
            "reg_no": req.reg_no
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://document-service:8002")
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://chat-service:8003")
AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://audit-service:8004")

async def forward_request(url: str, request: Request) -> Response:
    client = httpx.AsyncClient(timeout=120.0)
    body = await request.body()
    headers = dict(request.headers)
    # Remove host header to avoid conflicts
    if "host" in headers:
        del headers["host"]
        
    response = await client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=body,
        params=request.query_params
    )
    
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@app.api_route("/documents/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_documents(path: str, request: Request):
    return await forward_request(f"{DOCUMENT_SERVICE_URL}/documents/{path}", request)

@app.api_route("/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_chat(path: str, request: Request):
    return await forward_request(f"{CHAT_SERVICE_URL}/ai/{path}", request)

@app.api_route("/audit/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_audit(path: str, request: Request):
    return await forward_request(f"{AUDIT_SERVICE_URL}/audit/{path}", request)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api-gateway"}

