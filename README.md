# FastAPI Production Project

A production-ready FastAPI application with PostgreSQL database integration.

## Features

- 🚀 FastAPI with async/await support
- 🐘 PostgreSQL database with SQLAlchemy ORM
- 🔄 Database migrations with Alembic
- 🔐 JWT authentication and authorization
- 📊 Request/Response validation with Pydantic
- 🐳 Docker and Docker Compose support
- 🧪 Comprehensive testing with pytest
- 📝 API documentation with Swagger/OpenAPI
- 🔍 Code quality tools (Black, Flake8, isort, MyPy)
- 📦 Redis for caching and background tasks
- 🔧 Environment-based configuration

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config/                 # Configuration management
│   ├── constants/              # Application constants
│   ├── database/               # Database configuration
│   ├── middleware/             # Custom middleware
│   ├── models/                 # SQLAlchemy models
│   ├── routes/                 # API routes
│   ├── schemas/                # Pydantic schemas
│   ├── service_managers/       # Business logic
│   └── utils/                  # Utility functions
├── tests/                      # Test files
├── alembic/                    # Database migrations
├── docker-compose.yml          # Docker compose configuration
├── Dockerfile                  # Docker image configuration
├── requirements.txt            # Python dependencies
└── README.md
```

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Start the application:
   ```bash
   docker-compose up --build
   ```

4. Access the API:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Local Development

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app
```

## Code Quality

Format code:
```bash
black app/
isort app/
```

Lint code:
```bash
flake8 app/
mypy app/
```

## Contributing

1. Install pre-commit hooks:
   ```bash
   pre-commit install
