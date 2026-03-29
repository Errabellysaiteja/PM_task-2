# E-Commerce Support Resolution Agent

An autonomous, multi-agent Retrieval-Augmented Generation (RAG) system designed to resolve e-commerce customer support tickets. Built with CrewAI, LangChain, ChromaDB, and Google Gemini, this system grounds all responses strictly in company policy, enforces citations, and prevents LLM hallucinations.

## Architecture Highlights
* **Multi-Agent Orchestration:** Utilizes CrewAI to divide tasks among specialized agents (Triage, Retrieval, Writing, Compliance).
* **RAG Pipeline:** Local ChromaDB vector store powered by HuggingFace `all-MiniLM-L6-v2` embeddings.
* **Zero-Hallucination Controls:** Strict Pydantic JSON schemas, temperature=0 LLM calls, and a dedicated Compliance Agent to audit citations.

## Prerequisites
* Python 3.10+
* A Google Gemini API Key

## Workflow

[ Inputs ]
   ├── Free-form Ticket Text
   └── Structured Order Context (JSON)
        ↓
[ CrewAI Orchestration Engine (Powered by Gemini 2.5 Flash) ]
   │
   ├── 1. Triage Agent
   │      ↳ Classifies issue, checks for missing data, drafts clarifying questions.
   │
   ├── 2. Policy Retriever Agent
   │      ↳ Queries the Vector Database using the custom Policy Search Tool.
   │      │
   │      ├── [ RAG Database ]
   │      │    ↳ Raw Documents → Text Splitter → HuggingFace Embeddings → ChromaDB
   │      │
   │      ↳ Extracts exact text chunks and appends source document metadata.
   │
   ├── 3. Resolution Writer Agent
   │      ↳ Drafts the customer-facing response using ONLY retrieved evidence.
   │
   └── 4. Compliance & Safety Agent
          ↳ Audits the draft. Blocks unsupported claims and ensures citations are present.
        ↓
[ Output ]
   └── Structured JSON Resolution (Decision, Rationale, Citations, Customer Draft)

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ecommerce-resolution-agent
   ```
2. **Setup Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
3. **Configure Environment Variables:**
```bash
Create a .env file in the root directory and add your API key:
GEMINI_API_KEY=your_gemini_api_key_here
```
How to Run
Step 1: Build the Knowledge Base
Ingests the policy documents and builds the Chroma vector database. Run this once, or whenever policies are updated.
```bash
python src/rag_pipeline.py
```
Step 2: Run a Single Ticket Test
Executes the CrewAI system on a hardcoded sample ticket and outputs the structured JSON resolution.
```bash
python src/main.py
```
Step 3: Run the Evaluation Suite
Runs the system against a suite of 20 test cases (Standard, Exceptions, Conflicts, Not-in-Policy) and saves the output to evaluation_results.json.
```bash
python src/evaluate.py
```

Project Structure
data/policies/: Raw text files containing the e-commerce policies.

src/rag_pipeline.py: Document ingestion, chunking, and ChromaDB setup.

src/agents.py: Defines the Triage, Retriever, Writer, and Compliance agents.

src/tasks.py: Defines Pydantic data contracts and agent instructions.

src/main.py: Crew initialization and custom CrewAI BaseTool integration.

src/evaluate.py: Batch processing script for the 20-ticket test set.


