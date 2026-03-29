# E-Commerce Support Resolution Agent

An autonomous, multi-agent Retrieval-Augmented Generation (RAG) system designed to resolve e-commerce customer support tickets. Built with CrewAI, LangChain, ChromaDB, and Google Gemini, this system grounds all responses strictly in company policy, enforces citations, and prevents LLM hallucinations.

## Architecture Highlights
* **Multi-Agent Orchestration:** Utilizes CrewAI to divide tasks among specialized agents (Triage, Retrieval, Writing, Compliance).
* **RAG Pipeline:** Local ChromaDB vector store powered by HuggingFace `all-MiniLM-L6-v2` embeddings.
* **Zero-Hallucination Controls:** Strict Pydantic JSON schemas, temperature=0 LLM calls, and a dedicated Compliance Agent to audit citations.

## Prerequisites
* Python 3.10+
* A Google Gemini API Key

## Project Structure

ecommerce-resolution-agent/
├── .github/
│   └── workflows/
│       └── ci.yml             
├── data/
│   └── policies/              # Raw e-commerce policy text files
├── src/
│   ├── __init__.py
│   ├── agents.py              # CrewAI agent definitions & backstories
│   ├── evaluate.py            # 20-ticket batch testing script
│   ├── main.py                # Entry point & tool integration
│   ├── rag_pipeline.py        # Document ingestion & ChromaDB setup
│   └── tasks.py               # Pydantic JSON schemas & task instructions
├── .gitignore                 # Keeps API keys and DBs out of version control
├── evaluation_results.json    # The output metrics from the 20 test cases
├── README.md                  # You are here
└── requirements.txt           # Python dependencies
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


