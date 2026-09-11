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