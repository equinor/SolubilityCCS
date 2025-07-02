# SolubilityCCS

A Python package for analyzing solubility and acid formation behavior in Carbon Capture and Storage (CCS) systems.

## Installation

### From PyPI (Recommended)

```bash
pip install solubilityCCS
```

### From Source

```bash
git clone <repository-url>
cd SolubilityCCS
pip install -e .
```

## Quick Start

```python
from solubilityCCS import Fluid

# Create a fluid system
fluid = Fluid()
fluid.add_component("CO2", 0.999)
fluid.add_component("H2SO4", 10e-6)  # 10 ppm
fluid.add_component("H2O", 10e-6)    # 10 ppm

# Set conditions
fluid.set_temperature(275.15)  # 2°C
fluid.set_pressure(60.0)       # 60 bara

# Perform calculations
fluid.calc_vapour_pressure()
fluid.flash_activity()

# Analyze results
print(f"Gas phase fraction: {fluid.betta}")
print(f"Number of phases: {len(fluid.phases)}")
```

## Features

- Fluid property calculations for CO2-acid-water systems
- Phase behavior analysis using NeqSim
- Acid formation risk assessment
- Support for various acids (H2SO4, HNO3, etc.)
- Comprehensive testing suite

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SolubilityCCS
   ```

2. **Install dependencies:**
   ```bash
   make install-dev
   ```

3. **Set up pre-commit hooks (REQUIRED):**
   ```bash
   make setup-pre-commit
   ```

4. **Run tests:**
   ```bash
   make test
   ```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. **All commits must pass pre-commit checks.**

Pre-commit hooks include:
- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)
- Documentation style (pydocstyle)
- General code quality checks

To run pre-commit manually:
```bash
pre-commit run --all-files
```

### Development Commands

```bash
# Install dependencies
make install-dev

# Set up pre-commit hooks
make setup-pre-commit

# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run security checks
make security-check

# Run tests
make test
make test-coverage
make test-unit
make test-integration

# Clean up artifacts
make clean
```

## Usage

### Basic Example

```python
from fluid import Fluid

# Create a fluid with CO2, acid, and water
fluid = Fluid()
fluid.add_component("CO2", 0.999)
fluid.add_component("H2SO4", 10e-6)  # 10 ppm
fluid.add_component("H2O", 10e-6)    # 10 ppm

# Set conditions
fluid.set_temperature(275.15)  # 2°C
fluid.set_pressure(60.0)       # 60 bara

# Perform calculations
fluid.calc_vapour_pressure()
fluid.flash_activity()

# Analyze results
print(f"Gas phase fraction: {fluid.betta}")
print(f"Number of phases: {len(fluid.phases)}")
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

**Important**: Pre-commit hooks are required for all contributions. Make sure to run `make setup-pre-commit` after cloning the repository.

## License

See [LICENSE](LICENSE) for license information.
