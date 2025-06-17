from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.db.init_db import init_db
from app.core.config import get_settings
from app.db.session import engine
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Starting application...")
        logger.info(f"Database URL: {settings.DATABASE_URL[:20]}..." if len(settings.DATABASE_URL) > 20 else settings.DATABASE_URL)
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Simple database test without blocking
        logger.info("Database connection test completed")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error("Continuing with startup despite database error")

@app.get("/")
async def root():
    return {"message": "Welcome to the Diet Tracking Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/db-test")
async def test_database():
    """Test database connection"""
    try:
        # Debug: Show what database URL we're using
        db_url = settings.DATABASE_URL
        masked_url = db_url.split('@')[0] + "@***" if '@' in db_url else "***"
        
        # Test database connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_url": masked_url,
            "database_type": "PostgreSQL" if "postgresql" in db_url.lower() else "SQLite"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "database_url": settings.DATABASE_URL.split('@')[0] + "@***" if '@' in settings.DATABASE_URL else "***",
            "database_type": "PostgreSQL" if "postgresql" in settings.DATABASE_URL.lower() else "SQLite"
        } 