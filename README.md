# Privacy-Preserving Enterprise LLM Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Presidio](https://img.shields.io/badge/Microsoft_Presidio-PII_Redaction-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Llama_3-black?style=for-the-badge&logo=ollama&logoColor=white)

---

## Overview

Enterprise adoption of large language models introduces a critical compliance risk: sensitive personally identifiable information (PII) — names, contact details, government identifiers — can be inadvertently forwarded to external inference endpoints, violating the **India Digital Personal Data Protection (DPDP) Act, 2023** and **GDPR Article 5(1)(c)** data minimisation principles.

This pipeline enforces a **privacy-first, edge-redaction architecture**. All PII is detected and scrubbed _before_ any text reaches the LLM. Inference is handled entirely by a locally hosted **Ollama / Llama 3** instance, ensuring that sensitive data never transits a network boundary. The result is an auditable, air-gapped document analysis system suitable for legal, HR, and financial enterprise workflows.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit Frontend                           │
│          (app.py — side-by-side audit UI, st.chat_message)          │
└───────────────────────┬──────────────────────────┬──────────────────┘
                        │ POST /redact              │ POST /chat
                        ▼                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend  (main.py)                   │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Presidio Redaction Layer  (redactor.py)           │
│                                                                     │
│   ┌──────────────────┐    ┌───────────────────────────────────┐     │
│   │  NLP Recognisers │    │  Custom Regex Recognisers         │     │
│   │  · PERSON        │    │  · AADHAR_NUMBER                  │     │
│   │  · EMAIL_ADDRESS │    │    pattern: \b\d{4}-\d{4}-\d{4}\b │     │
│   │  · PHONE_NUMBER  │    └───────────────────────────────────┘     │
│   └──────────────────┘                                              │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │  Redacted text only
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Local LLM Inference  (Ollama — llama3)                 │
│                     http://localhost:11434                          │
│                  *** air-gapped / no egress ***                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages

- **Data Ingestion** — `.txt` documents uploaded via the Streamlit UI; raw text extracted in-browser and forwarded to the FastAPI service layer.
- **Regex / NLP Redaction** — Microsoft Presidio runs a dual-pass analysis: (1) spaCy `en_core_web_lg` NER for contextual entity detection; (2) deterministic regex patterns for structured identifiers (Aadhar, email, phone). Detected spans are replaced with `<ENTITY_TYPE>` tokens.
- **LLM Inference** — Only the redacted, PII-free text is passed to the LangChain `Ollama` wrapper, which routes to the locally running Llama 3 model. Zero network egress.
- **UI Rendering** — Streamlit presents a real-time, side-by-side audit view: raw document vs. redacted document, plus a stateful chat interface backed by `st.session_state` for full turn history.

---

## Key Features

### 🔐 Zero-Trust PII Architecture
Redaction is enforced at the **service layer**, not the client — making it impossible for consuming applications to bypass the scrubbing step. The `/chat` endpoint redacts unconditionally before invoking the LLM, regardless of the caller.

### 🆔 Structured Identifier Recognition (Aadhar / Indian PII)
A custom `PatternRecognizer` extends Presidio's default recogniser registry with a high-confidence (`score=0.9`) regex for India's **12-digit Aadhar UID** format (`XXXX-XXXX-XXXX`). This complements spaCy's probabilistic NER with deterministic pattern coverage for government-issued identifiers not present in standard training corpora.

### 🤖 Air-Gapped Local Inference
The LangChain `Ollama` integration points exclusively to `http://localhost:11434`. No API keys, no cloud endpoints, no data retention by third parties. The model (`llama3`) runs fully on-premise, satisfying strict data residency requirements.

### 🖥️ Side-by-Side Streamlit Audit UI
The Streamlit frontend renders the **original** and **redacted** document side-by-side in read-only text areas, giving compliance teams a clear visual diff of what PII was removed. The integrated chat panel allows domain-specific Q&A over the redacted context, with full session-scoped conversation history.

### ⚡ FastAPI + Pydantic Validation
The REST layer uses Pydantic request models for strict input validation. Both `/redact` and `/chat` return structured JSON responses, making the backend trivially integrable with downstream enterprise systems (RPA, audit logging, SIEM platforms).

---

## Project Structure

```
.
├── main.py              # FastAPI application — /redact and /chat endpoints
├── redactor.py          # Presidio analyzer + anonymizer + custom Aadhar recogniser
├── app.py               # Streamlit frontend — two-column audit UI
├── generate_data.py     # Faker-based synthetic Indian employment contract generator
├── sample_contract.txt  # Generated sample document (produced by generate_data.py)
└── requirements.txt     # Python dependencies
```

---

## Local Setup

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or higher |
| Ollama | Latest — [ollama.com/download](https://ollama.com/download) |
| Ollama model | `llama3` |

---

### 1 — Clone the repository

```bash
git clone https://github.com/your-org/privacy-preserving-llm-pipeline.git
cd privacy-preserving-llm-pipeline
```

---

### 2 — Create and activate a virtual environment

```bash
# Create
python -m venv .venv

# Activate — macOS / Linux
source .venv/bin/activate

# Activate — Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

---

### 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 4 — Download the spaCy language model

Presidio requires a spaCy NER model. The large model provides the highest accuracy for PII detection:

```bash
python -m spacy download en_core_web_lg
```

> For resource-constrained environments, `en_core_web_sm` may be substituted, with reduced entity recall.

---

### 5 — Pull the Llama 3 model via Ollama

Ensure the Ollama daemon is running, then pull the model:

```bash
# Start the Ollama service (if not already running as a system daemon)
ollama serve

# In a separate terminal — pull Llama 3
ollama pull llama3
```

---

### 6 — Generate a sample contract (optional)

```bash
python generate_data.py
```

This writes a synthetic Indian employment contract with realistic PII to `sample_contract.txt`.

---

### 7 — Start the FastAPI backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API documentation is auto-generated and available at:
- **Swagger UI** → [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** → [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 8 — Start the Streamlit frontend

```bash
streamlit run app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## API Reference

### `POST /redact`

Accepts raw text and returns the PII-scrubbed version.

```json
// Request
{ "text": "Rohan Mehta's Aadhar is 3456-7890-1234, email: rohan@example.com" }

// Response
{ "redacted_text": "<PERSON>'s Aadhar is <AADHAR_NUMBER>, email: <EMAIL_ADDRESS>" }
```

### `POST /chat`

Redacts the input text, then queries the local LLM with the supplied prompt.

```json
// Request
{ "text": "...<raw document>...", "prompt": "Summarise the key obligations of the employee." }

// Response
{
  "redacted_text": "...<scrubbed document>...",
  "response": "...<LLM answer over redacted context>..."
}
```

---

## Compliance Notes

| Regulation | Mechanism |
|---|---|
| **DPDP Act, 2023 (India)** | Aadhar UIDs, names, and contact details are redacted prior to any processing by automated systems |
| **GDPR Article 5(1)(c)** — Data Minimisation | Only the minimum necessary (redacted) text is forwarded to the inference layer |
| **GDPR Article 25** — Privacy by Design | Redaction is architecturally enforced at the service boundary, not optionally applied at the client |
| **Data Residency** | All inference runs on a local Ollama instance; no data leaves the host machine |

---

## License

This project is licensed under the **MIT License**. See `LICENSE` for details.
