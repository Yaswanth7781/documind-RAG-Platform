# UniGuard AI Microservices Architecture

This directory contains the modernized microservices architecture for the UniGuard AI platform.

## Architecture

The monolithic backend has been decoupled into the following independent services:

- **api-gateway (Port 8000)**: Serves as the single entry point. Handles user authentication (`/auth/*`) natively, and proxies request routes (`/documents/*`, `/ai/*`, `/audit/*`) to specialized backend services.
- **document-service (Port 8002)**: Ingests enterprise PDFs, extracts text, chunks it, and uploads dense embeddings to Pinecone serverless vector store.
- **chat-service (Port 8003)**: Executes the 5-Agent Pipeline powered by Groq Llama 3 and **BM25 + Dense Semantic Hybrid Search (Reciprocal Rank Fusion)** to retrieve compliance context, analyze risk, and generate persona responses.
- **audit-service (Port 8004)**: Manages SQLite database and records conversational audit logs async.

## Key Features & Research Paper

- **Hybrid RAG Retrieval Engine**: Combines Sparse Lexical BM25 ranking with Dense `multilingual-e5-large` vector embeddings using Reciprocal Rank Fusion (RRF).
- **Publication & Documentation**: The comprehensive IEEE research paper detailing system performance, benchmarks, and multi-agent pipeline is available in [`IEEE_Conference_Paper_UniGuard_AI.md`](file:///c:/Users/user/Desktop/agenticaipro/UniGuard-AI-Multi-Agent-RAG-Based-University-Compliance-Intelligence-Platform/UniGuard-AI-Microservices/IEEE_Conference_Paper_UniGuard_AI.md).

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
uvicorn document-service.main:app --port 8002
uvicorn chat-service.main:app --port 8003
uvicorn audit-service.main:app --port 8004
```
