# UniGuard AI Microservices Architecture

This directory contains the modernized microservices architecture for the UniGuard AI platform.

## Architecture

The monolithic backend has been decoupled into the following independent services:

- **api-gateway (Port 8000)**: Serves as the single entry point. Proxies frontend requests to the underlying services based on route prefixes (`/auth/*`, `/documents/*`, `/ai/*`).
- **auth-service (Port 8001)**: Validates Admin PINs and handles JWT generation.
- **document-service (Port 8002)**: Ingests enterprise PDFs, extracts text, chunks it, and uploads the embeddings to Pinecone (or local ChromaDB).
- **chat-service (Port 8003)**: Executes the 5-Agent Pipeline to process queries, retrieve context, analyze compliance risk, and generate summaries.
- **audit-service (Port 8004)**: Manages SQLite database and records the conversational audit logs async.

## Running the Architecture

The easiest way to start all microservices is using Docker Compose.

```bash
# From the UniGuard-AI-Microservices directory:
docker-compose up --build
```

### Environment Variables

Your API keys (Groq, Pinecone, AWS) are securely stored in the `.env` file at the root of the `UniGuard-AI-Microservices` folder. Docker Compose automatically injects them into the respective containers.

### Local Python Execution (Without Docker)

If you prefer to run them manually:
1. Create a python virtual environment and install requirements for each service.
2. Ensure you add `UniGuard-AI-Microservices` to your `PYTHONPATH` so the `shared` module can be resolved.
3. Start each service on its designated port.
```bash
$env:PYTHONPATH="C:\path\to\UniGuard-AI-Microservices"
uvicorn api-gateway.main:app --port 8000
uvicorn auth-service.main:app --port 8001
uvicorn document-service.main:app --port 8002
uvicorn chat-service.main:app --port 8003
uvicorn audit-service.main:app --port 8004
```
