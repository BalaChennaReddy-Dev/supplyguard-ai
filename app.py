import os
from dotenv import load_dotenv

from fastapi import FastAPI

load_dotenv()

app = FastAPI(
    title="SupplyGuard AI",
    description="AI-powered Supply Chain Disruption Response Assistant",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "application": "SupplyGuard AI",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
    }