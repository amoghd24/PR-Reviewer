# MCP Enterprise PR Reviewer - Development Makefile

.PHONY: help install dev-install test lint format clean run-servers run-host setup-env

# Default target
help:
	@echo "MCP Enterprise PR Reviewer - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup-env          Create virtual environment and install dependencies"
	@echo "  install            Install production dependencies"
	@echo "  dev-install        Install development dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  test               Run all tests"
	@echo "  lint               Run linting checks"
	@echo "  format             Format code with black and isort"
	@echo "  clean              Clean up temporary files"
	@echo ""
	@echo "Runtime Commands:"
	@echo "  run-servers        Start all MCP servers"
	@echo "  run-host           Start the MCP host (FastAPI)"
	@echo ""
	@echo "Configuration Commands:"
	@echo "  register-github    Complete GitHub OAuth flow"
	@echo "  register-slack     Complete Slack OAuth flow"

# Environment setup
setup-env:
	python -m venv pr-reviewer-env
	@echo "Virtual environment created. Activate with:"
	@echo "source pr-reviewer-env/bin/activate  # On Unix"
	@echo "pr-reviewer-env\\Scripts\\activate     # On Windows"

# Installation
install:
	pip install -r requirements.txt

dev-install: install
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

# Code quality
lint:
	black --check .
	isort --check-only .
	mypy .
	
format:
	black .
	isort .

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

# Runtime commands (to be implemented as servers are built)
run-servers:
	@echo "Starting MCP servers..."
	@echo "This will start all individual MCP servers"
	# Implementation will be added as servers are built

run-host:
	@echo "Starting MCP Host (FastAPI)..."
	@echo "This will start the main orchestration server"
	# Implementation will be added when host is built

# OAuth registration commands (to be implemented)
register-github:
	@echo "Starting GitHub OAuth registration..."
	# Implementation will be added in security phase

register-slack:
	@echo "Starting Slack OAuth registration..."
	# Implementation will be added in security phase

