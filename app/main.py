from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhook import router as webhook_router
from app.db.init_db import init_db
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Diet Tracking Chatbot",
    description="A WhatsApp/SMS chatbot for diet tracking and nutrition analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Diet Tracking Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 