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
- `POST /api/v1/webhook` - Twilio webhook endpoint
- `GET /api/v1/food-logs` - Get food logs
- `POST /api/v1/food-logs` - Create food log

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
├── api/
│   ├── endpoints/
│   │   └── food_logs.py
│   └── webhook.py
├── core/
│   └── config.py
├── db/
│   ├── base.py
│   ├── init_db.py
│   └── session.py
├── models/
│   ├── food_log.py
│   └── user.py
├── services/
│   ├── food_log_service.py
│   └── openai_service.py
└── main.py
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