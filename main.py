from fastapi import FastAPI
from pydantic import BaseModel
from redactor import redact_text
from langchain_community.llms import Ollama

app = FastAPI(title="Privacy-Preserving LLM Pipeline")

llm = Ollama(base_url="http://localhost:11434", model="llama3")

# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class RedactRequest(BaseModel):
    text: str


class ChatRequest(BaseModel):
    text: str
    prompt: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/redact")
def redact(request: RedactRequest):
    """
    Accept raw text and return a copy with all PII redacted.
    """
    redacted = redact_text(request.text)
    return {"redacted_text": redacted}


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Redact PII from the provided text first, then send the redacted text
    together with the user's prompt to the local Ollama LLM.
    """
    redacted = redact_text(request.text)
    full_prompt = f"{request.prompt}\n\nContext:\n{redacted}"
    response = llm.invoke(full_prompt)
    return {
        "redacted_text": redacted,
        "response": response,
    }
