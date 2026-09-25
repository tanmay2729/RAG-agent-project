# ERP RAG Agent

A small RAG + agent demo for business documents (invoices, purchase orders)
with a routing layer that decides between structured inventory lookups and
unstructured document retrieval - modeled on the kind of ERP-integrated AI
agent described in the Shree Radha Studio AI Engineer posting.

Everything in this stack is free: sentence-transformers and Chroma run
locally with no API cost, and Groq's free tier covers the LLM calls.

## Architecture

```
Question -> agent.py (router)
              |-- inventory keyword match --> inventory.py (mock DB lookup)
              |-- otherwise --> retrieval.py (Chroma search) --> llm.py (Groq)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add your free GROQ_API_KEY from console.groq.com

python data/generate_data.py   # generate synthetic documents
python -m app.ingest            # embed + store them in Chroma

.env is loaded automatically by the app.
uvicorn app.main:app --reload   # run locally at http://localhost:8000
```

## Usage

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many units of Zari Thread are in stock?"}'

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which invoices are overdue?"}'
```

## Tests

```bash
pytest
```

## Deploy (free)

- **Render free web service**: connect the repo, use the Dockerfile as the
  build method, set `GROQ_API_KEY` as an environment variable. Same pattern
  as the churn-prediction API deployment.
- Chroma persists to a local folder (`app/chroma_db/`), which is fine for a
  demo on a single free instance; for a real multi-instance deployment
  you'd point it at a hosted Chroma server or another vector DB instead.

## Design choices

- **Embeddings:** `sentence-transformers` (MiniLM) - free, runs on CPU,
  no API dependency for this step.
- **Vector store:** Chroma - free, open-source, persists locally with a
  simple API (`add` / `query`), less boilerplate than a raw FAISS index.
- **LLM:** Groq - fast inference, generous free tier, OpenAI-style API.
- **Agent:** a simple keyword router rather than a framework, so the
  decision logic is fully visible and explainable in an interview.
