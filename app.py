import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "frontend",
    "dist",
)

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

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000)
