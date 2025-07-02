#!/bin/bash

# Pre-commit setup and initial formatting script
# This script sets up pre-commit hooks and fixes initial code formatting issues

echo "Setting up pre-commit hooks..."

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

echo "Running initial code formatting..."

# Fix basic formatting issues
black .
isort .

# Fix notebook formatting
nbqa black *.ipynb || echo "Note: Some notebook formatting may have issues"
nbqa isort *.ipynb || echo "Note: Some notebook import sorting may have issues"

echo "Pre-commit setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and fix any remaining linting issues"
echo "2. Add type hints where needed"
echo "3. Fix any remaining code quality issues"
echo ""
echo "You can run 'pre-commit run --all-files' to see remaining issues."
