# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- **Run server**: `uvicorn app.main:app --reload`
- **Initialize database**: `python -m app.db.init_db`
- **Database migrations**: `alembic upgrade head`
- **Environment setup**: Create `.env` file with required variables (see README.md)

### Testing & Deployment
- **Railway deployment**: Uses `hypercorn app.main:app --bind "::"` (configured in railway.json)
- **Database test endpoint**: `GET /db-test` for connection verification

## Architecture

### Core Components
- **FastAPI application** (`app/main.py`): Main entry point with CORS middleware and startup database initialization
- **Twilio webhook handler** (`app/api/webhook.py`): Processes WhatsApp/SMS messages, distinguishes between questions and food entries
- **Database models**: SQLAlchemy async models for User and FoodLog with nutritional tracking
- **Services layer**: Separated OpenAI integration and food logging business logic

### Message Processing Flow
1. Webhook receives Twilio message → extracts phone number and message body
2. User lookup/creation in database
3. Message classification: question vs food entry using keyword detection
4. **Food entries**: OpenAI analysis → multiple FoodLog records → nutritional summary response
5. **Questions**: Context-aware response using recent food history and user profile

### Database Schema
- **Users**: Basic profile with nutritional targets (calories, protein, carbs, fats)
- **FoodLogs**: Detailed nutritional breakdown per food item with AI confidence scores and normalized titles
- Supports both SQLite (development) and PostgreSQL (production via DATABASE_URL)

### Key Services
- **FoodLogService**: Handles food entry creation with AI analysis, retrieves user history and daily summaries
- **OpenAIService**: Food analysis and diet question answering with user context
- Async database operations throughout

### Configuration
- Environment-based settings via Pydantic Settings
- Automatic database URL detection (SQLite/PostgreSQL)
- Railway deployment configuration with Nixpacks builder