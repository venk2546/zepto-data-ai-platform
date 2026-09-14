# SupportAI Helpdesk Agent

## Overview

SupportAI is a Retrieval-Augmented Generation (RAG) based customer support assistant.

The system uses a collection of customer support documents as its knowledge base. When a customer asks a question, the system searches the knowledge base for relevant information and provides the retrieved context to a Large Language Model (LLM).

The goal is to provide accurate, document-grounded customer support responses while reducing the chance of unsupported or invented answers.

---

## Project Structure

```text
support_assistant/
│
├── docs/
│   ├── customer_support_hours.txt
│   ├── damaged_missing_items.txt
│   ├── delivery_policy.txt
│   ├── gift_cards.txt
│   ├── membership_tiers.txt
│   ├── order_cancellation.txt
│   ├── order_tracking.txt
│   └── returns_refunds.txt
│
├── chroma_db/
│
├── ingest.py
├── retriever.py
├── llm.py
├── rag.py
└── README.md

Knowledge Base

The docs/ directory contains 8 customer support documents:

Delivery Policy
Returns & Refunds
Membership Tiers
Order Tracking
Order Cancellation
Damaged/Missing Items
Gift Cards
Customer Support Hours

These documents form the knowledge base used by the SupportAI system.

RAG Architecture

The system follows this pipeline:

Customer Question
       ↓
Query Embedding
       ↓
ChromaDB Semantic Search
       ↓
Relevant Document Chunks
       ↓
Confidence Check
       ↓
Conversation Context
       ↓
LLM
       ↓
Grounded Support Answer
       ↓
Sources

If the retrieved information has low confidence, the system does not generate an unsupported answer and instead escalates the question to human support.

Components
1. ingest.py

Responsible for preparing the knowledge base.

Main operations:

Load support documents
Split documents into chunks
Generate embeddings
Store embeddings in ChromaDB

Embedding model:

all-MiniLM-L6-v2

The current knowledge base contains:

8 documents
27 chunks
384-dimensional embeddings
2. retriever.py

Responsible for semantic search.

The retriever:

Receives the customer's question.
Converts the question into an embedding.
Searches ChromaDB.
Retrieves the most relevant document chunks.
Returns the document text, source, and confidence score.
3. llm.py

Responsible for connecting the application to the Large Language Model through OpenRouter.

The API key is stored outside the source code using an environment variable.

The API key should never be committed to GitHub.

4. rag.py

This is the main SupportAI application.

It combines:

Document retrieval
ChromaDB
Confidence checking
Conversation history
Follow-up question handling
LLM generation
Source display
Human-support escalation
Confidence Threshold

The application currently uses:

CONFIDENCE_THRESHOLD = 0.15

The strongest retrieved result is checked against this threshold.

High-confidence question

If:

confidence >= 0.15

the retrieved information is passed to the LLM.

Low-confidence question

If:

confidence < 0.15

the system avoids generating an unsupported response and displays a human-support escalation message.

Conversation History

The application maintains conversation history so that follow-up questions can use previous context.

For example:

Customer:
How can I track my order?

SupportAI:
You can track your order...

Customer:
What if I have a problem with it?

The system uses the previous customer question to create a contextual search query so that "it" can be understood as referring to the order.

Example
Customer Question
How can I track my order?
Retrieved Information
Source: order_tracking.txt
SupportAI
You can track your order using the order tracking feature...
Unknown Question Example

If a customer asks:

What is the capital of France?

the question is outside the support knowledge base.

The system detects the low confidence score and responds with a fallback message instead of generating an unsupported support answer.

I don't have enough information in the support documents
to answer your question.

This question will be escalated to human support.
Technologies Used
Python
Pandas
Sentence Transformers
all-MiniLM-L6-v2
ChromaDB
OpenRouter API
Large Language Model (LLM)
Retrieval-Augmented Generation (RAG)
Environment Variables
.env
Git / GitHub
How to Run
Step 1 — Activate the virtual environment

From the project root:

.\.venv\Scripts\Activate.ps1

You should see:

(.venv) PS D:\Masai\zepto-data-ai-platform>
Step 2 — Install dependencies

If dependencies are not already installed:

pip install pandas chromadb sentence-transformers python-dotenv requests
Step 3 — Ingest the documents

Run:

python support_assistant\ingest.py

Expected result:

Data successfully stored in ChromaDB.
Total records in ChromaDB: 27
Step 4 — Run the SupportAI application
python support_assistant\rag.py

Then enter a customer question:

Customer: How can I track my order?

The application retrieves relevant information and generates a response using the LLM.

Security

The OpenRouter API key is stored in `.env`

The `.env` file must not be uploaded to GitHub.

The project .gitignore should contain:

```text
.env
support_assistant/chroma_db/
__pycache__/
*.pyc
```


## Development Status

Module 3 implementation and functional testing completed successfully.

The system has been tested with:

- Relevant customer support questions
- Follow-up questions
- Unknown questions
- Low-confidence human escalation
- ChromaDB retrieval
- LLM response generation


## Future Improvements

Possible future improvements include:

- Better retrieval ranking
- More advanced conversation context handling
- Additional support documents
- Improved confidence scoring
- Human support integration
- Logging and monitoring

## Docker

The SupportAI Helpdesk Agent can also be run inside a Docker container.

The Docker setup uses Python 3.12 and installs the project dependencies from the root `requirements.txt`.

When the container starts, it first runs `ingest.py` to create the ChromaDB knowledge base and then starts the RAG application using `rag.py`.

### Build the Docker Image

From the project root directory:

```bash
docker build -t zepto-support-ai .
```

This creates a Docker image named:

```text
zepto-support-ai:latest
```

### Run the Docker Container

The OpenRouter API key is stored in the `.env` file and is passed to the container at runtime.

Run:

```bash
docker run -it --env-file .env zepto-support-ai
```

The container performs the following pipeline:

```text
Support documents
        ↓
ingest.py
        ↓
SentenceTransformer embeddings
        ↓
ChromaDB
        ↓
rag.py
        ↓
SupportAI Helpdesk Agent
```

After startup, the terminal displays:

```text
===================================
       SupportAI Helpdesk Agent
===================================
Type 'exit' to stop the assistant.

Customer:
```

### Example Docker Test

Example in-scope query:

```text
Customer: How can I track my order?

Best confidence: 0.4126

SupportAI:
You can track your order using the order tracking feature.

Sources:
- order_tracking.txt
- delivery_policy.txt
```

Example out-of-scope query:

```text
Customer: What is the capital of France?

Best confidence: 0.0

SupportAI:
I don't have enough information in the support documents to answer your question.

This question will be escalated to human support.
```

Type `exit` to stop the SupportAI application and exit the container.

### Docker Files

The project uses:

- `Dockerfile` — defines the Docker image and application startup process.
- `.dockerignore` — prevents unnecessary or sensitive files such as `.env`, `.venv`, `.git`, and local ChromaDB data from being copied into the image.
- `requirements.txt` — contains the Python dependencies installed inside the Docker image.

The `.env` file is not included in the Docker image. It is supplied securely at runtime using `--env-file .env`.

---

## LangGraph Workflow

The SupportAI assistant uses LangGraph to control the flow of customer questions.

The graph is implemented in:

```text
support_assistant/graph.py
```

The graph contains three main nodes:

1. `classify_intent`
2. `retrieve_and_answer`
3. `direct_answer`

The workflow is:

```text
Customer Question
        ↓
classify_intent
        ↓
   Intent Classification
      /          \
policy_question   general_question
      ↓                 ↓
retrieve_and_answer   direct_answer
      ↓                 ↓
ChromaDB Retrieval    Direct Response
      ↓                 ↓
Top 3 Chunks            ↓
      ↓                 ↓
Generate Answer         ↓
      \                 /
          Final Response
```

### Mock LLM Mode

The project uses deterministic mock mode as the default execution mode.

If `MOCK_LLM` is not set, it defaults to mock mode.

```text
MOCK_LLM=1
```

In mock mode, no external LLM API is required.

Policy questions are identified using keywords such as:

```text
delivery
return
refund
membership
tracking
cancel
gift card
support hours
```

Policy questions are routed to ChromaDB retrieval.

General questions are routed directly to a fixed response:

```text
I can only answer questions about Zepto policies right now.
```

The optional real LLM path can be enabled with:

```text
MOCK_LLM=0
```

The real LLM path uses the configured OpenRouter API key.

---

## Structured Prompt

The optional real-LLM path uses a structured prompt containing:

- Role
- Context
- Task
- Format
- Length
- Negative constraint
- Few-shot example

The assistant is explicitly instructed not to answer using information that is not present in the supplied Zepto policy context.

---

## FastAPI Service

The SupportAI service exposes a FastAPI endpoint:

```text
POST /ask
```

The API implementation is located in:

```text
support_assistant/api.py
```

### Request Format

```json
{
  "query": "How does order tracking work?"
}
```

### Response Format

```json
{
  "answer": "string",
  "sources": [],
  "confidence": 1.0
}
```

The response is validated using a Pydantic response model containing:

- `answer`
- `sources`
- `confidence`

---

## Running FastAPI Locally

From the project root:

```powershell
uvicorn support_assistant.api:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

The API can then be tested using the `POST /ask` endpoint.

---

## Example API Call 1 — Policy Question

Request:

```json
{
  "query": "How does order tracking work?"
}
```

Response:

```json
{
  "answer": "Based on the retrieved context: Order Tracking\n\nCustomers can track an active order using the order tracking feature.\n\nAfter an order is successfully placed, the customer can view the current order status.\n\nOrder statuses may change",
  "sources": [
    "order_tracking.txt",
    "delivery_policy.txt",
    "order_tracking.txt"
  ],
  "confidence": 0.6212
}
```

This request is classified as a `policy_question`.

The query is embedded using `all-MiniLM-L6-v2`, and the top three relevant chunks are retrieved from the `zepto_support` ChromaDB collection.

---

## Example API Call 2 — General Question

Request:

```json
{
  "query": "What is the capital of France?"
}
```

Response:

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

This request is classified as a `general_question`.

It is routed to the `direct_answer` node, so ChromaDB retrieval is not required.

---

## Docker

The complete SupportAI service can run inside Docker.

### Build the Docker Image

From the project root:

```powershell
docker build --load -t zepto-support-ai .
```

### Run the Docker Container

```powershell
docker run -p 8000:8000 zepto-support-ai
```

The container performs the following startup sequence:

```text
Docker Container
       ↓
ingest.py
       ↓
Load 8 Policy Documents
       ↓
Chunk Documents
       ↓
all-MiniLM-L6-v2 Embeddings
       ↓
ChromaDB
       ↓
27 Stored Records
       ↓
FastAPI / Uvicorn
       ↓
POST /ask
```

After the container starts, open:

```text
http://127.0.0.1:8000/docs
```

The Dockerized `POST /ask` endpoint can then be tested through Swagger.

---

## Final SupportAI Architecture

```text
8 Zepto Policy Documents
          ↓
       ingest.py
          ↓
     Text Chunking
          ↓
all-MiniLM-L6-v2
          ↓
       ChromaDB
   zepto_support
          ↓
        27 chunks
          ↓
      FastAPI /ask
          ↓
       LangGraph
          ↓
   classify_intent
      /       \
 policy       general
    ↓            ↓
retrieve_and_   direct_
answer          answer
    ↓            ↓
ChromaDB       Fixed Mock
Top-3 Search   Response
    ↓            ↓
Mock / Real LLM Generation
          ↓
    Pydantic Response
          ↓
answer + sources + confidence
```

### Component Responsibilities

- `ingest.py` — loads documents, chunks text, creates embeddings, and stores them in ChromaDB.
- `retriever.py` — embeds customer queries and retrieves the top matching policy chunks.
- `graph.py` — implements the LangGraph StateGraph, intent classification, routing, retrieval, and answer generation.
- `api.py` — exposes the LangGraph workflow through the FastAPI `POST /ask` endpoint.
- `docs/` — contains the eight Zepto policy documents.
- `chroma_db/` — local persistent vector database generated during ingestion.
- `Dockerfile` — packages and serves the SupportAI FastAPI application.

The default graded path uses deterministic `MOCK_LLM` behavior. External LLM access is optional and does not affect the default offline workflow.