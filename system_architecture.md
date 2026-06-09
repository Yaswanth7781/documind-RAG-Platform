# UniGuard AI - System Architecture & API Documentation

This document provides a comprehensive overview of the UniGuard AI platform's microservice architecture, multi-agent data flows, and REST API endpoints.

## 1. High-Level Architecture

The system is built on a containerized **Microservices Architecture**. The frontend strictly communicates with a unified API Gateway, which intelligently proxies requests to specialized backend services.

```mermaid
flowchart TB
    %% Styling
    classDef client fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff,rx:8px
    classDef gateway fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff,rx:8px
    classDef service fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff,rx:8px
    classDef database fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff,rx:8px
    classDef external fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff,rx:8px

    User([👤 User / Admin]):::client -->|React + Vite| Frontend[🖥️ Frontend Client]:::client
    Frontend -->|HTTP Requests| APIGateway{🚦 API Gateway\nPort 8000}:::gateway
    
    APIGateway -->|/auth| Auth[🔐 Auth Service\nPort 8001]:::service
    APIGateway -->|/documents| Doc[📄 Document Service\nPort 8002]:::service
    APIGateway -->|/ai| Chat[🤖 Chat Service\nPort 8003]:::service
    
    %% Document Service Flow
    Doc -->|1. Extract & Chunk| PyMuPDF(PyMuPDF + Langchain)
    Doc -->|2. Generate Embeddings & Upsert| Pinecone[(🌲 Pinecone Serverless\nVector Store)]:::database
    
    %% Chat Service Flow
    Chat -->|RAG Context Retrieval| Pinecone
    Chat -->|LLM Inference| Groq[🧠 Groq Cloud API\nLlama 3 8B]:::external
    Chat -->|Store Interaction Log| Audit[📋 Audit Service\nPort 8004]:::service
    
    %% Audit Service Flow
    Audit -->|Write log| SQLite[(🗄️ SQLite Database)]:::database
```

---

## 2. Multi-Agent RAG Pipeline (Chat Flow)

When a user submits a query, the **Chat Service** orchestrates a sequence of 5 specialized AI agents to prevent hallucinations and strictly enforce university policy.

```mermaid
sequenceDiagram
    participant U as User
    participant C as Chat Service
    participant G as Groq LLM
    participant P as Pinecone DB
    participant A as Audit Service

    U->>C: "What happens if I fight in hostel?"
    
    Note over C,G: Agent 0: Linguistics Normalizer
    C->>G: Translate to English & Add Synonyms
    G-->>C: "hostel fight (physical altercation, violence)"
    
    Note over C,G: Agent 1: Intent Classifier
    C->>G: Classify Intent (JSON)
    G-->>C: { category: "Discipline", priority: "High" }
    
    Note over C,P: Agent 2: RAG Retriever
    C->>P: Fetch top 3 vectors (Cosine Similarity)
    P-->>C: [Relevant Policy Chunks]
    
    Note over C,G: Agent 3: Compliance & Risk Analyst
    C->>G: Assess risk based on policy chunks (JSON)
    G-->>C: { risk_level: "High", needs_review: true }
    
    Note over C,G: Agent 4: Persona Generator
    C->>G: Summarize policy as Admin/Student/Faculty
    G-->>C: "According to the handbook, strict disciplinary action..."
    
    C->>A: Save Audit Log (Risk, Query, Response)
    C-->>U: Final AI Response
```

---

## 3. API Endpoints

All external requests from the frontend are routed through the **API Gateway (`http://localhost:8000`)**.

### 🔐 Auth Service (`/auth`)
| Endpoint | Method | Security | Description |
|----------|--------|----------|-------------|
| `/auth/login` | `POST` | Public | Authenticates an Admin using a secure PIN. Returns a JWT Bearer token. |

### 📄 Document Service (`/documents`)
| Endpoint | Method | Security | Description |
|----------|--------|----------|-------------|
| `/documents/upload` | `POST` | Admin JWT | Accepts a `.pdf` file. Extracts text, splits it into 1000-character chunks, generates embeddings, and saves them to Pinecone. |
| `/documents/list` | `GET` | Public | Queries Pinecone for unique document sources and returns a list of active policy files. |
| `/documents/{filename}` | `DELETE`| Admin JWT | Erases all vectors matching the specific document filename from the Pinecone index. |

### 🤖 Chat Service (`/ai`)
| Endpoint | Method | Security | Description |
|----------|--------|----------|-------------|
| `/ai/chat` | `POST` | Public | Triggers the Multi-Agent LLM pipeline. Accepts a JSON payload containing the user's `prompt`, `role` (Student/Faculty/Admin), and `history`. |

### 📋 Audit Service (`/audit` - Internal)
*Note: This service is typically only accessed internally by the Chat Service.*
| Endpoint | Method | Security | Description |
|----------|--------|----------|-------------|
| `/audit` | `POST` | Internal | Stores a completed chat interaction into the local SQLite database. |
| `/audit/logs` | `GET` | Admin JWT | Retrieves all stored system logs for administrative review. |
| `/audit/export`| `GET` | Admin JWT | Exports the entire database as a CSV for reporting. |
