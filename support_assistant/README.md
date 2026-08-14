# Module 3 — Zepto Support Assistant

## 1. Project Overview

This module implements a small customer-support assistant for Zepto using a Retrieval-Augmented Generation (RAG) workflow.

The assistant uses Zepto policy documents as its knowledge base and retrieves relevant policy information before answering policy-related questions.

The application uses:

- Sentence Transformers
- `all-MiniLM-L6-v2`
- ChromaDB
- LangGraph
- FastAPI
- Pydantic
- A keyless `MOCK_LLM` path

The default application does not require an external LLM API key.

---

## 2. Architecture

The application follows this flow:

User Query
    ↓
FastAPI `/ask`
    ↓
LangGraph
    ↓
classify_intent
    ↓
 ┌───────────────────────┐
 │                       │
 ↓                       ↓
policy_question      general_question
 │                       │
 ↓                       ↓
retrieve_and_answer   direct_answer
 │
 ↓
ChromaDB
 │
 ↓
Top-3 relevant chunks
 │
 ↓
MOCK_LLM
 │
 ↓
Pydantic Response
 │
 ↓
JSON Response

---

## 3. Project Structure

```text
support_assistant/
│
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
│
├── chroma_db/
│
├── rag.py
├── prompts.py
├── main.py
├── Dockerfile
├── requirements.txt
└── README.md

