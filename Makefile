.PHONY: help setup install test lint smoke up down seed

# Default target
help:
	@echo ""
	@echo "Sentinel MAS — available commands"
	@echo ""
	@echo "  make setup     First-time setup (symlinks playbook → .claude/commands)"
	@echo "  make install   Install all service dependencies"
	@echo "  make up        Start local development stack"
	@echo "  make down      Stop local development stack"
	@echo "  make seed      Seed local database with sample data"
	@echo "  make test      Run all tests"
	@echo "  make lint      Run linters for all services"
	@echo "  make smoke     Run smoke tests (set BASE_URL for non-local)"
	@echo ""

setup:
	@bash setup.sh

install:
	cd services/api && pip install -r requirements.txt
	cd services/central && pip install -r requirements.txt
	cd services/ui && npm install

up:
	docker compose up

down:
	docker compose down

seed:
	cd services/api && python scripts/seed.py

test:
	cd services/api && pytest
	cd services/central && pytest
	cd services/ui && npm test -- --watchAll=false

lint:
	cd services/api && ruff check . && mypy .
	cd services/central && ruff check . && mypy .
	cd services/ui && npm run lint

smoke:
	@BASE_URL=$${BASE_URL:-http://localhost:8000} && \
	echo "Running smoke tests against $$BASE_URL" && \
	curl -sf $$BASE_URL/health | grep -q "ok" && echo "  health: ok" && \
	curl -sf $$BASE_URL/api/agents | grep -q "agents" && echo "  agents: ok" && \
	echo "Smoke tests passed."
