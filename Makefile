.PHONY: help install install-dev run test lint format clean docker-build docker-run migrate create-migration

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development dependencies"
	@echo "  run          - Run the development server"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean cache files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  migrate      - Run database migrations"
	@echo "  create-migration - Create new migration"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app/
	mypy app/
	bandit -r app/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -delete

docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

create-migration:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

setup-dev:
	pip install -r requirements-dev.txt
	pre-commit install
	cp .env.example .env
	@echo "Development environment setup complete!"
	@echo "Don't forget to update .env with your database credentials"
