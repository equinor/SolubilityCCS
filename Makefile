.PHONY: test test-verbose test-coverage test-unit test-integration clean install install-dev setup-pre-commit format lint type-check security-check help

# Default Python command - try venv first, fallback to system python
PYTHON := $(shell if [ -f ./venv/bin/python ]; then echo ./venv/bin/python; elif [ -f ./venv/Scripts/python.exe ]; then echo ./venv/Scripts/python.exe; else echo python; fi)

help:
	@echo "Available commands:"
	@echo "  install          - Install production dependencies"
	@echo "  install-dev      - Install development dependencies"
	@echo "  setup-pre-commit - Set up pre-commit hooks"
	@echo "  format           - Format code with black and isort"
	@echo "  lint             - Run linting with flake8"
	@echo "  type-check       - Run type checking with mypy"
	@echo "  security-check   - Run security checks with bandit"
	@echo "  test             - Run all tests"
	@echo "  test-verbose     - Run tests with verbose output"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-unit        - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo "  clean            - Clean up test artifacts"

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

setup-pre-commit:
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "Pre-commit hooks installed successfully!"
	@echo "Run 'pre-commit run --all-files' to check all files"

format:
	black .
	isort .
	nbqa black *.ipynb
	nbqa isort *.ipynb

lint:
	flake8 .
	nbqa flake8 *.ipynb

type-check:
	mypy .

security-check:
	bandit -r . -f json -o bandit-report.json || bandit -r .

test:
	$(PYTHON) -m pytest

test-verbose:
	$(PYTHON) -m pytest -v

test-coverage:
	$(PYTHON) -m pytest --cov=. --cov-report=html --cov-report=term-missing

test-unit:
	$(PYTHON) -m pytest -m "not integration"

test-integration:
	$(PYTHON) -m pytest -m integration

clean:
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf .mypy_cache/
	rm -rf bandit-report.json
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
