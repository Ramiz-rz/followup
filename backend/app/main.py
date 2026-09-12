import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database import init_db
from app.routes import projects, analyze, commitments, waiting
from app.services.ai_analyzer import is_ai_configured

app = FastAPI(title="FollowUp API", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "analysis_mode": "ai" if is_ai_configured() else "local",
    }


app.include_router(projects.router)
app.include_router(analyze.router)
app.include_router(commitments.router)
app.include_router(waiting.router)
