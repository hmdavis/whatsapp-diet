# WhatsApp Diet Tracker

A FastAPI-based WhatsApp/SMS chatbot for diet tracking and nutrition analysis using OpenAI and Twilio.

## Features

- WhatsApp/SMS integration via Twilio
- AI-powered food analysis using OpenAI
- Diet tracking and logging
- RESTful API endpoints
- PostgreSQL database support

## Local Development

### Prerequisites

- Python 3.11+
- SQLite (for local development)
- OpenAI API key
- Twilio account (for WhatsApp/SMS)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd whatsapp-diet
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
DATABASE_URL=sqlite:///./diet_tracker.db
DEBUG=True
```

5. Initialize database:
```bash
python -m app.db.init_db
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Development Workflow

For development, you can:

1. **View API Documentation**: Visit `http://localhost:8000/docs` for interactive Swagger UI
2. **Test Database**: Use `GET /db-test` endpoint to verify database connectivity
3. **Test Webhook**: Use tools like ngrok to expose localhost for Twilio webhook testing
4. **Monitor Logs**: The application uses structured logging for debugging

```bash
# Test the webhook locally with ngrok
ngrok http 8000

# Update your Twilio webhook URL to:
# https://your-ngrok-url.ngrok.io/api/v1/webhook/message
```

## Railway Deployment

### Prerequisites

- Railway account
- GitHub repository with your code
- OpenAI API key
- Twilio account

### Deployment Steps

1. **Connect to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"

2. **Configure Environment Variables:**
   In Railway dashboard, add these environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   DEBUG=False
   ```

3. **Add PostgreSQL Database:**
   - In your Railway project, click "New" → "Database" → "PostgreSQL"
   - Railway will automatically set the `DATABASE_URL` environment variable

4. **Deploy:**
   - Railway will automatically detect your FastAPI app
   - It will use the `railway.json` configuration
   - Your app will be deployed and get a public URL

5. **Update Twilio Webhook:**
   - Go to your Twilio console
   - Update your webhook URL to: `https://your-railway-app.railway.app/api/v1/webhook`

### Database Migration

After deployment, your database tables will be automatically created on startup. If you need to run Alembic migrations:

```bash
# Connect to Railway shell
railway shell

# Run migrations
alembic upgrade head
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /db-test` - Database connection test
- `POST /api/v1/webhook/message` - Twilio webhook endpoint for WhatsApp/SMS
- `GET /api/v1/food-logs/{user_id}` - Get user's food logs
- `POST /api/v1/food-logs/{user_id}` - Create food log entries

## Architecture

### Design Principles

The codebase follows these key principles for maintainability:

1. **Separation of Concerns**: Each layer has a single responsibility
   - API layer handles HTTP requests/responses
   - Service layer contains business logic
   - Repository layer manages data access
   - Models define data structure

2. **Dependency Injection**: Services are injected rather than created directly
   - Improves testability and flexibility
   - Managed through `app/core/dependencies.py`

3. **Repository Pattern**: Centralized data access logic
   - Abstracts database operations
   - Makes testing easier with mockable interfaces

4. **Service-Oriented Architecture**: Business logic separated into focused services
   - `MessageClassificationService`: Determines if message is question vs food entry
   - `NutritionCalculationService`: Handles all nutrition math and progress tracking
   - `ResponseFormattingService`: Formats user-facing messages
   - `OpenAIService`: Manages AI interactions
   - `FoodLogService`: Coordinates food logging workflow

5. **Error Handling**: Custom exceptions for different error types
   - Domain-specific exceptions in `app/exceptions/`
   - Consistent error responses across the API

### Key Components

- **Schemas**: Pydantic models for request/response validation and serialization
- **Repositories**: Data access abstraction with common CRUD operations
- **Services**: Business logic encapsulation with clear interfaces
- **Dependencies**: FastAPI dependency injection for clean service instantiation

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI analysis | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | Yes |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `DEBUG` | Debug mode (True/False) | No |

## Project Structure

```
app/
├── api/                          # API layer
│   ├── v1/                       # API version 1
│   │   ├── webhook.py           # WhatsApp/SMS webhook handler
│   │   └── food_logs.py         # Food log REST endpoints
│   └── __init__.py              # API router setup
├── core/                        # Core configuration
│   ├── config.py                # Application settings
│   └── dependencies.py          # Dependency injection setup
├── db/                          # Database layer
│   ├── base.py                  # SQLAlchemy base
│   ├── init_db.py               # Database initialization
│   └── session.py               # Database session management
├── exceptions/                  # Custom exceptions
│   ├── base.py                  # Base exception classes
│   ├── food.py                  # Food-related exceptions
│   ├── user.py                  # User-related exceptions
│   └── external.py              # External service exceptions
├── models/                      # SQLAlchemy models
│   ├── food_log.py              # Food log database model
│   └── user.py                  # User database model
├── repositories/                # Data access layer
│   ├── base.py                  # Base repository pattern
│   ├── user_repository.py       # User data operations
│   └── food_log_repository.py   # Food log data operations
├── schemas/                     # Pydantic schemas
│   ├── webhook.py               # Webhook request/response schemas
│   ├── food_log.py              # Food log schemas
│   ├── user.py                  # User schemas
│   └── nutrition.py             # Nutrition data schemas
├── services/                    # Business logic layer
│   ├── food_log_service.py      # Food logging business logic
│   ├── openai_service.py        # OpenAI integration
│   ├── message_classification_service.py  # Message type classification
│   ├── nutrition_calculation_service.py   # Nutrition calculations
│   └── response_formatting_service.py     # Response formatting
└── main.py                      # FastAPI application entry point
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   - Ensure `DATABASE_URL` is properly set
   - Check if PostgreSQL is running (in production)

2. **Twilio Webhook Issues:**
   - Verify webhook URL is accessible
   - Check Twilio credentials

3. **OpenAI API Errors:**
   - Verify API key is valid
   - Check API usage limits

### Railway Specific

- Use Railway logs to debug deployment issues
- Check environment variables in Railway dashboard
- Ensure all dependencies are in `requirements.txt`

## License

MIT License 