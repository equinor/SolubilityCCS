# Testing Documentation for SolubilityCCS

## Overview

This document describes the testing strategy and setup for the SolubilityCCS project, which analyzes acid formation potential in CO2 systems containing acids (H2SO4 or HNO3) and water.

## Test Structure

### Test Files
- `test_fluid.py` - Main test file containing all test cases
- `pytest.ini` - Pytest configuration
- `requirements.txt` - Testing dependencies

### Test Categories

#### 1. Unit Tests
- **TestFluid**: Tests for the Fluid class functionality
  - Initialization
  - Component addition
  - Temperature/pressure setting
  - Flow rate configuration

- **TestPhaseClass**: Tests for the Phase class
  - Phase initialization
  - Property setting

#### 2. Integration Tests
- **TestAcidFormationAnalysis**: Tests for acid formation analysis workflow
  - Phase behavior calculations
  - Acid formation risk assessment
  - Concentration calculations

- **TestCO2Properties**: Tests for CO2 property calculations
  - Density, speed of sound, enthalpy, entropy

- **TestIntegration**: Complete workflow tests
  - End-to-end acid formation analysis

## Running Tests

### Command Line Options

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html --cov-report=term-missing

# Run only unit tests
python -m pytest -m "not integration"

# Run only integration tests
python -m pytest -m integration

# Run quick tests
python -m pytest -v --tb=short
```

### Using Make

```bash
# Install dependencies
make install

# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage
make test-coverage

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Clean up test artifacts
make clean
```

### Using the Test Runner Script

```bash
# Run full test suite with coverage
python run_tests.py

# Run quick tests without coverage
python run_tests.py quick
```

### Using VS Code Tasks

Access through Command Palette (`Ctrl+Shift+P`) → "Tasks: Run Task":
- Run All Tests
- Run Tests with Coverage
- Run Quick Tests
- Run Acid Formation Analysis

## Test Configuration

### pytest.ini Configuration
- Test discovery patterns
- Coverage settings (70% minimum)
- Warning filters
- Test markers for categorization

### Coverage Settings
- HTML reports generated in `htmlcov/` directory
- Terminal coverage summary
- Minimum coverage threshold: 70%

## Expected Test Results

The test suite validates the expected behavior from the analysis script:

```
Mole fraction of gas phase to total phase 0.9999795454259583 mol/mol
water in CO2 7.451380309314413 ppm mol
H2SO4 in CO2 8.673809998573368e-09 ppm mol
Second phase is ACIDIC
Liquid phase formed 95.52793777593807 wt %
Liquid phase formed 3799.5376397443843 t/y
Water in liquid phase 0.20310928318964988 mol fraction
H2SO4 in liquid phase 0.7968907168103502 mol fraction
Pure CO2 density 823.370580206214 kg/m3
Pure CO2 speed of sound: 402.01680893006034 m/s
Pure CO2 enthalpy: -178.6763331712992 kJ/kg
Pure CO2 entropy: -56.74553450179903 J/K
```

## Continuous Integration

### GitHub Actions
- Automated testing on push/pull request
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Coverage reporting via Codecov

## Test Data and Mocking

The tests use mocking to simulate the NeqSim thermodynamic calculations since they may require specific Java dependencies or databases that might not be available in all test environments.

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
2. **NeqSim Issues**: Tests use mocking to avoid Java/NeqSim dependency issues
3. **Coverage Issues**: Adjust coverage threshold in `pytest.ini` if needed

### Debug Mode
Add `-s` flag to pytest to see print statements:
```bash
python -m pytest -s -v
```

## Adding New Tests

1. Add test methods to appropriate test classes in `test_fluid.py`
2. Use descriptive test names starting with `test_`
3. Add appropriate markers (`@pytest.mark.integration`, etc.)
4. Mock external dependencies when needed
5. Follow the AAA pattern (Arrange, Act, Assert)

## Test Maintenance

- Review and update tests when functionality changes
- Maintain high test coverage (>70%)
- Keep test data and expected results updated
- Regularly review and clean up test artifacts
