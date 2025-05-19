# VideoProcessing

## Requirements

- Python 3.8+
- OpenAI API key

## Installation

1. Clone the repository
```bash git clone <repository-url>```

2. Create a virtual environment and activate it
```bash python3 -m venv venv source venv/bin/activate```

3. Install dependencies
```bash pip install -r requirements.txt```

4. Configure your environment variables
   Copy the example environment file and update it with the requirement values:
   ```bash cp .env.example .env```

## Running the application
```bash uvicorn main:app --reload```

## For Local Testing
Start Redis Container in a different terminal ```docker run -p 6379:6379 redis```
Start Celery task Queue in a different terminal ```celery -A app.core.worker.celery worker --loglevel=info```


The application will start at `http://127.0.0.1:8000`

- API documentation: `http://localhost:8001/docs`
- Health check: `http://localhost:8000/api/health/check`
- Ping endpoint: `http://localhost:8001/api/ping`

## Project Structure

- `app/`: Main application package
  - `api/`: API endpoints
  - `agent/`: Agent implementations
  - `core/`: Core application components
  - `utils/`: Utility functions

## Troubleshooting