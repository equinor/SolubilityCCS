# Contributing to SolubilityCCS

Thank you for your interest in contributing to SolubilityCCS! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setting Up Your Development Environment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SolubilityCCS
   ```

2. **Install dependencies:**
   ```bash
   make install-dev
   ```

   Or manually:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```

3. **Set up pre-commit hooks:**
   ```bash
   make setup-pre-commit
   ```

   Or manually:
   ```bash
   pre-commit install
   ```

## Code Quality Standards

This project uses several tools to maintain code quality:

### Pre-commit Hooks

Pre-commit hooks are **required** and will run automatically before each commit. They include:

- **Code formatting** with `black` and `isort`
- **Linting** with `flake8`
- **Type checking** with `mypy`
- **Security scanning** with `bandit`
- **Documentation style** with `pydocstyle`
- **General code quality checks**

### Manual Code Quality Checks

You can run these tools manually:

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run security checks
make security-check

# Run all pre-commit hooks on all files
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration
```

### Writing Tests

- Write tests for all new functionality
- Maintain high test coverage (aim for >90%)
- Use descriptive test names and docstrings
- Use the `@skip_if_no_database` decorator for tests requiring database files
- Mark integration tests with `@pytest.mark.integration`

## Code Style Guidelines

### Python Code Style

- **Line length**: 88 characters (enforced by `black`)
- **Import organization**: Use `isort` with the `black` profile
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use NumPy-style docstrings for public functions and classes

### Jupyter Notebooks

- Clean notebook output before committing
- Use descriptive cell comments
- Keep notebooks focused on specific analyses or demonstrations

## Commit Guidelines

### Commit Message Format

Use clear, descriptive commit messages:

```
type(scope): brief description

Longer explanation if needed

- List any breaking changes
- Reference issues: Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pre-commit Requirements

**All commits must pass pre-commit hooks.** If pre-commit hooks fail:

1. Fix the issues highlighted by the tools
2. Stage the fixed files: `git add .`
3. Commit again: `git commit -m "your message"`

To skip pre-commit hooks (not recommended):
```bash
git commit -m "your message" --no-verify
```

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Ensure code quality:**
   ```bash
   # Run all quality checks
   pre-commit run --all-files
   make test-coverage
   ```

4. **Create a pull request:**
   - Use a descriptive title
   - Include a detailed description of changes
   - Reference any related issues
   - Ensure all CI checks pass

## Project Structure

```
SolubilityCCS/
├── fluid.py                      # Main fluid modeling classes
├── neqsim_functions.py          # NeqSim integration functions
├── acid_formation_analysis.py   # Acid formation analysis scripts
├── sulfuric_acid_activity.py    # Acid activity calculations
├── test_*.py                    # Test files
├── *.ipynb                      # Jupyter notebooks
├── Database/                    # Data files
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── .pre-commit-config.yaml      # Pre-commit configuration
├── pyproject.toml              # Tool configurations
├── Makefile                    # Build and development commands
└── README.md                   # Project documentation
```

## Getting Help

- Check existing issues and documentation
- Create an issue for bugs or feature requests
- Use clear, descriptive titles and provide context

## Code of Conduct

- Be respectful and constructive
- Focus on the code and technical aspects
- Help maintain a welcoming environment for all contributors

Thank you for contributing to SolubilityCCS!
