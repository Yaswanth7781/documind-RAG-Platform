import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="UniGuard AI - API Gateway")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
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

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_auth(path: str, request: Request):
    return await forward_request(f"{AUTH_SERVICE_URL}/auth/{path}", request)

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
