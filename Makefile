.PHONY: help setup install dev prod test clean lint format

help:
	@echo "Available commands:"
	@echo "  make setup      - Initial project setup"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development environment"
	@echo "  make prod       - Start production environment"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean up containers and volumes"

setup:
	@echo "Setting up project..."
	cp -n .env.example .env.production || true
	mkdir -p storage/generated/frontend
	mkdir -p storage/generated/backend
	mkdir -p storage/temp
	mkdir -p storage/cache
	mkdir -p storage/logs
	mkdir -p app
	@echo "Setup complete!"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	docker-compose -f docker-compose.yml up --build

prod:
	docker-compose -f docker-compose.yml up -d --build

test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app tests
	mypy app
	pylint app

format:
	black app tests
	isort app tests

clean:
	docker-compose down -v
	rm -rf storage/temp/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

