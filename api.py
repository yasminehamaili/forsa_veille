"""API FastAPI : le chatbot du front (Figma -> React) appelle /chat."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import ask
from ingest import run as run_ingest

app = FastAPI(title="Forsa TIC - Chatbot expert")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatIn(BaseModel):
    message: str
    departement: str | None = None


@app.post("/chat")
def chat(body: ChatIn):
    return ask(body.message, body.departement)


@app.post("/ingest")
def ingest():
    return run_ingest()


@app.get("/health")
def health():
    return {"status": "ok"}
