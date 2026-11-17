
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.jobs import router as jobs_router

app = FastAPI(
    title="LaunchPad AI",
    description="AI-powered fresher job aggregator for India",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"]
)

app.include_router(
    jobs_router,
    prefix="/api/jobs",
    tags=["Jobs"]
)


@app.get("/")
def home():
    return {
        "message": "Welcome to LaunchPad AI",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
