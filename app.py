import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI

# Make the src/ directory importable when running:
# python app.py
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from api.routes import router as api_router


load_dotenv()

app = FastAPI(
    title="SupplyGuard AI",
    description="AI-powered Supply Chain Disruption Response Assistant",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/")
def home():
    return {
        "application": "SupplyGuard AI",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
    )