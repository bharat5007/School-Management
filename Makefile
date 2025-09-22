.PHONY: help venv install install-dev run test lint format clean docker-build docker-run migrate create-migration setup-dev

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Default target
help:
	@echo "Available targets:"
	@echo "  venv         - Create virtual environment"
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
	@echo "  setup-dev    - Complete development setup"

venv:
	python3 -m venv $(VENV)
	@echo "Virtual environment created. Activate with: source $(VENV)/bin/activate"

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Production dependencies installed in virtual environment"

install-dev: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@echo "Development dependencies installed in virtual environment"

run:
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(VENV)/bin/pytest

test-cov:
	$(VENV)/bin/pytest --cov=app --cov-report=html --cov-report=term

lint:
	$(VENV)/bin/flake8 app/
	$(VENV)/bin/mypy app/
	$(VENV)/bin/bandit -r app/

format:
	$(VENV)/bin/black app/ tests/
	$(VENV)/bin/isort app/ tests/

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf $(VENV)
	@echo "Cleaned up cache files and virtual environment"

docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-down:
	docker-compose down

migrate:
	$(VENV)/bin/alembic upgrade head

create-migration:
	@read -p "Enter migration message: " message; \
	$(VENV)/bin/alembic revision --autogenerate -m "$$message"

setup-dev: install-dev
	$(VENV)/bin/pre-commit install
	cp .env.example .env
	@echo ""
	@echo "Development environment setup complete!"
	@echo "Virtual environment created at: $(VENV)"
	@echo "Activate with: source $(VENV)/bin/activate"
	@echo "Don't forget to update .env with your database credentials"
