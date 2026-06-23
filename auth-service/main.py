import os
import hashlib
import sqlite3
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

# SQLite database setup
DB_DIR = "/app/data"
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

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth-service"}
