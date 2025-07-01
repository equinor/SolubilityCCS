.PHONY: test test-verbose test-coverage test-unit test-integration clean install help

# Default Python command (can be overridden)
PYTHON := /usr/local/python/current/bin/python

help:
	@echo "Available commands:"
	@echo "  install       - Install all dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-verbose  - Run tests with verbose output"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-unit     - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo "  clean         - Clean up test artifacts"

install:
	$(PYTHON) -m pip install -r requirements.txt

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
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
