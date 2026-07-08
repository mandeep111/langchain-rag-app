# LangChain RAG App

A FastAPI-based Retrieval-Augmented Generation (RAG) service for uploading documents, processing them asynchronously, embedding their contents, storing chunks in a vector database, and answering questions using retrieved context.

The project is intentionally generic. It can be adapted to knowledge bases made from manuals, policies, internal documents, product guides, support articles, or any other document collection where users need grounded answers from uploaded files.

## What The Project Aims To Do

- Accept document uploads through an API.
- Store source files durably on local disk through a storage adapter.
- Track documents and ingestion jobs in PostgreSQL.
- Process ingestion asynchronously through Redis and RQ.
- Extract text from supported files.
- Split extracted text into retrievable chunks.
- Generate embeddings for each chunk.
- Store chunks and metadata in Chroma.
- Retrieve relevant chunks for a user question.
- Use an LLM to generate an answer grounded in retrieved context.
- Return the answer with source document references.

## Current Capabilities

- FastAPI API with async upload, document status, ingestion job status, and query endpoints.
- PostgreSQL metadata model for documents and ingestion jobs.
- Redis-backed RQ worker for background ingestion.
- Local file storage under configurable `DOCUMENT_STORAGE_PATH`.
- Supports `.txt`, `.pdf`, and `.docx` ingestion.
- Uses LangChain text splitting and RetrievalQA.
- Uses Chroma as a local persistent vector store.
- Uses Hugging Face embeddings through `langchain_huggingface`.
- Uses OpenAI Chat Completions for answer generation.
- Includes Alembic migrations, Docker Compose for the full app stack, and pytest coverage for the new ingestion foundation.

## Tech Stack

- **API framework:** FastAPI
- **ASGI server:** Uvicorn
- **Database:** PostgreSQL
- **ORM and migrations:** SQLAlchemy 2.x and Alembic
- **Queue and worker:** Redis and RQ
- **RAG orchestration:** LangChain
- **Vector database:** ChromaDB
- **Embeddings:** Hugging Face sentence-transformer model, default `all-MiniLM-L6-v2`
- **LLM:** OpenAI chat model, currently `gpt-3.5-turbo` in code
- **Document parsing:** `pdfplumber` for PDF, `python-docx` for DOCX, native Python file reading for TXT
- **Configuration:** Environment variables loaded with `python-dotenv`
- **Validation:** Pydantic schemas
- **Testing:** pytest

## Project Structure

```text
app/
  api/
    ingest.py            # Upload and document status endpoints
    ingestion_jobs.py    # Ingestion job status endpoint
    query.py             # Question-answering endpoint
  core/
    config.py            # Environment-backed settings
    embedding.py         # Embedding model factory
    queue.py             # Redis/RQ queue setup
  db/
    models.py            # SQLAlchemy document and job models
    session.py           # Database engine/session dependency
  models/
    schemas.py           # API request and response schemas
  services/
    document.py          # Text extraction and chunking
    ingestion.py         # Worker ingestion workflow
    storage.py           # Local document storage adapter
    rag_chain.py         # RetrievalQA chain setup
    vector_store.py      # Chroma access and persistence
  main.py                # FastAPI app entrypoint
  worker.py              # RQ worker entrypoint
migrations/              # Alembic migrations
tests/                   # pytest suite
docker-compose.yml       # API, worker, PostgreSQL, and Redis
Dockerfile               # App image used by API and worker
requirements.txt         # Python dependencies
```

## How To Start

### 1. Configure environment variables

Copy `.env.example` to `.env` and set your OpenAI key:

```bash
cp .env.example .env
```

Key settings:

```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql+psycopg://rag:rag@localhost:5432/rag_app
REDIS_URL=redis://localhost:6379/0
DOCUMENT_STORAGE_PATH=./storage/documents
MAX_UPLOAD_SIZE_BYTES=26214400
```

The `.env` file is the source for OpenAI and app-level settings. Docker Compose also reads `.env`, then overrides only Docker-internal service URLs such as `DATABASE_URL`, `REDIS_URL`, and `DOCUMENT_STORAGE_PATH` inside the `api` and `worker` containers.

### 2. Start the full stack

```bash
docker compose up --build
```

This starts:

- FastAPI API on `http://127.0.0.1:8000`
- RQ ingestion worker
- PostgreSQL
- Redis

The API container runs `alembic upgrade head` on startup.

The service should be available at:

- API root: `http://127.0.0.1:8000/`
- Interactive docs: `http://127.0.0.1:8000/docs`

Verify Docker received the key without printing it:

```bash
docker compose exec api sh -lc 'python -c "import os,hashlib; k=os.getenv(\"OPENAI_API_KEY\", \"\"); print(bool(k), len(k), hashlib.sha256(k.encode()).hexdigest()[:12])"'
docker compose exec worker sh -lc 'python -c "import os,hashlib; k=os.getenv(\"OPENAI_API_KEY\", \"\"); print(bool(k), len(k), hashlib.sha256(k.encode()).hexdigest()[:12])"'
```

Compare that hash with the host `.env` value:

```bash
python3 -c 'from pathlib import Path; import hashlib; v=[line.split("=",1)[1].strip() for line in Path(".env").read_text().splitlines() if line.startswith("OPENAI_API_KEY=")][0]; print(len(v), hashlib.sha256(v.encode()).hexdigest()[:12])'
```

### 3. Stop the stack

```bash
docker compose down
```

Use this to remove persisted local volumes too:

```bash
docker compose down -v
```

## Local Development Without Docker

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start only Postgres and Redis:

```bash
docker compose up -d postgres redis
```

For local non-container execution, keep `.env` using localhost service URLs:

```env
DATABASE_URL=postgresql+psycopg://rag:rag@localhost:5432/rag_app
REDIS_URL=redis://localhost:6379/0
DOCUMENT_STORAGE_PATH=./storage/documents
```

Run migrations:

```bash
alembic upgrade head
```

Run the API:

```bash
uvicorn app.main:app --reload
```

In a second terminal:

```bash
source .venv/bin/activate
python -m app.worker
```

## API Usage

### Upload a document

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload" \
  -F "file=@/path/to/document.pdf"
```

Example response:

```json
{
  "document_id": "0dd9486b-b036-419a-85ef-11372dce7895",
  "job_id": "74ae4ed8-bb41-4d34-a40b-b7a9d99f9855",
  "status": "queued",
  "status_url": "http://127.0.0.1:8000/ingestion-jobs/74ae4ed8-bb41-4d34-a40b-b7a9d99f9855"
}
```

### Check ingestion job status

```bash
curl "http://127.0.0.1:8000/ingestion-jobs/{job_id}"
```

### Check document status

```bash
curl "http://127.0.0.1:8000/documents/{document_id}"
```

### Ask a question

```bash
curl -X POST "http://127.0.0.1:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the documentation say about scheduled maintenance?"}'
```

Example response:

```json
{
  "question": "What does the documentation say about scheduled maintenance?",
  "answer": "The answer generated from retrieved document context.",
  "source_documents": ["manual.pdf"]
}
```

## Development Checks

Run the test suite:

```bash
pytest tests
```

Run migrations against the configured database:

```bash
alembic upgrade head
```

## Remaining Production Work

This milestone adds the asynchronous ingestion foundation. The next production upgrades should focus on:

- Page-aware parsing with OCR and table handling.
- Token-aware and structure-aware chunking.
- Stronger RAG prompting with citations and abstention behavior.
- Authentication, authorization, rate limiting, and upload scanning.
- Retrieval quality evaluation, golden datasets, and answer faithfulness tests.
- Deployment health checks, structured logs, metrics, backups, and restore testing.
