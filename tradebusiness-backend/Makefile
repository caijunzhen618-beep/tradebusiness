.PHONY: help dev test lint format clean db-reset db-seed production-check

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev:  ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests
	pytest tests/ -v

production-check:  ## Run production preflight checks
	pytest tests/ -q
	black --check app/ scripts/ tests/
	isort --check-only app/ scripts/ tests/
	powershell -NoProfile -File ../scripts/verify_nginx_template.ps1
	python -c "import yaml; yaml.safe_load(open('docker-compose.prod.yml', encoding='utf-8')); print('production compose ok')"

test-coverage:  ## Run tests with coverage
	pytest tests/ --cov=app --cov-report=html --cov-report=term

lint:  ## Run linters
	black --check app/ tests/
	isort --check-only app/ tests/
	flake8 app/ tests/
	mypy app/

format:  ## Format code
	black app/ tests/
	isort app/ tests/

db-reset:  ## Reset database (WARNING: deletes all data)
	python scripts/init_db.py reset

db-seed:  ## Seed initial data
	python scripts/init_db.py

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov logs/*.log

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install black isort flake8 mypy pylint pytest pytest-cov pytest-asyncio

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## View Docker logs
	docker-compose logs -f backend

migrate:  ## Run database migrations
	alembic upgrade head

migration:  ## Create a new migration (use NAME=name)
	@if [ -z "$(NAME)" ]; then echo "Usage: make migration NAME=migration_name"; exit 1; fi
	alembic revision --autogenerate -m "$(NAME)"
