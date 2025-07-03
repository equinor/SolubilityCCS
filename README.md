# SolubilityCCS

A Python package for analyzing solubility and acid formation behavior in Carbon Capture and Storage (CCS) systems using advanced thermodynamic models.

## Overview

SolubilityCCS provides tools to analyze acid formation risks in CO2 transport and storage systems. The package uses the **SRK-CPA (Soave-Redlich-Kwong Cubic Plus Association)** equation of state to calculate fugacity coefficients and activity models to determine component activities in multiphase systems.

### Thermodynamic Models

- **Fugacity calculations**: SRK-CPA equation of state for prediction of component fugacities
- **Activity calculations**: Activity coefficient models for liquid phase behavior
- **Phase equilibrium**: Robust flash calculations for multiphase systems

### Supported Systems

The model currently supports the following chemical systems:

- **CO₂-water** (binary system)
- **CO₂-water-H₂SO₄** (ternary system with sulfuric acid)
- **CO₂-water-HNO₃** (ternary system with nitric acid)

> **Coming Soon**: CO₂-water-H₂SO₄-HNO₃ (quaternary system)

### Applications

- **Initial solubility estimates** for acids in CO₂ streams
- **Acid formation risk assessment** in CCS transport pipelines
- **Phase behavior analysis** under various pressure and temperature conditions
- **Liquid phase formation prediction** and composition analysis

## Installation

### Requirements

- Python 3.9 or higher
- NeqSim (Java-based thermodynamic library)
- Scientific Python stack (NumPy, SciPy, Pandas, Matplotlib)

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

### Basic Acid Formation Analysis

```python
from solubilityccs import Fluid
from solubilityccs.neqsim_functions import get_co2_parameters

# System parameters
acid = "H2SO4"  # Supported: "H2SO4", "HNO3"
acid_concentration = 10.0  # ppm
water_concentration = 10.0  # ppm
temperature = 2.0  # °C
pressure = 60.0  # bara
flow_rate = 100  # Mt/year

# Create fluid system
fluid = Fluid()
fluid.add_component("CO2", 1.0 - acid_concentration/1e6 - water_concentration/1e6)
fluid.add_component(acid, acid_concentration/1e6)
fluid.add_component("H2O", water_concentration/1e6)

# Set operating conditions
fluid.set_temperature(temperature + 273.15)  # Convert to Kelvin
fluid.set_pressure(pressure)
fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

# Perform thermodynamic calculations
fluid.calc_vapour_pressure()
fluid.flash_activity()

# Analyze results
print(f"Gas phase fraction: {fluid.betta:.4f}")
print(f"Water in CO2: {1e6 * fluid.phases[0].get_component_fraction('H2O'):.2f} ppm")
print(f"{acid} in CO2: {1e6 * fluid.phases[0].get_component_fraction(acid):.2f} ppm")

# Check for liquid phase formation (acid formation risk)
if fluid.betta < 1.0:
    print("\n⚠️  ACID FORMATION RISK DETECTED!")
    print(f"Liquid phase type: {fluid.phases[1].name}")
    print(f"Liquid acid concentration: {fluid.phases[1].get_acid_wt_prc(acid):.2f} wt%")
    print(f"Liquid phase flow rate: {fluid.phases[1].get_flow_rate('kg/hr') * 24 * 365 / 1000:.2f} t/y")
else:
    print("\n✅ Single gas phase - No acid formation risk")

# Get pure CO2 properties
co2_props = get_co2_parameters(pressure, temperature)
print(f"\nPure CO2 properties at {temperature}°C, {pressure} bara:")
print(f"Density: {co2_props['density']:.2f} kg/m³")
print(f"Speed of sound: {co2_props['speed_of_sound']:.2f} m/s")
print(f"Enthalpy: {co2_props['enthalpy']:.2f} kJ/kg")
print(f"Entropy: {co2_props['entropy']:.2f} J/K")
```

### Advanced Usage

```python
from solubilityccs import Fluid
from solubilityccs.neqsim_functions import (
    get_acid_fugacity_coeff,
    get_water_fugacity_coefficient
)

# Calculate fugacity coefficients for different acids
h2so4_fug_coeff = get_acid_fugacity_coeff("H2SO4", 60.0, 2.0)
hno3_fug_coeff = get_acid_fugacity_coeff("HNO3", 60.0, 2.0)
water_fug_coeff = get_water_fugacity_coefficient(60.0, 2.0)

print(f"H2SO4 fugacity coefficient: {h2so4_fug_coeff}")
print(f"HNO3 fugacity coefficient: {hno3_fug_coeff}")
print(f"Water fugacity coefficient: {water_fug_coeff}")
```

## Features

### Core Functionality

- **Thermodynamic property calculations** using SRK-CPA equation of state
- **Multiphase flash calculations** with activity coefficient models
- **Component fugacity and activity calculations**
- **Phase behavior analysis** for CO2-acid-water systems
- **Acid formation risk assessment** for CCS applications

### Supported Components

- **CO₂** (Carbon dioxide)
- **H₂O** (Water)
- **H₂SO₄** (Sulfuric acid)
- **HNO₃** (Nitric acid)

### Calculation Capabilities

- Vapor-liquid equilibrium calculations
- Component solubility predictions
- Liquid phase formation analysis
- Acid concentration calculations
- Pure component property estimation

### Database Integration

- Built-in component database (COMP.csv)
- Thermodynamic property database (Properties.csv)
- Water activity data for H₂SO₄ systems

## Examples

See the `examples/` directory for more comprehensive examples:

- **`basic_usage.py`**: Simple acid formation analysis
- **`example.ipynb`**: Jupyter notebook with detailed workflow
- **`acid_formation_analysis.py`**: Advanced analysis scripts

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Java Runtime Environment (for NeqSim)

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

## Testing

The package includes comprehensive tests covering:

- **Unit tests** for individual components
- **Integration tests** for complete workflows
- **Validation tests** against known data
- **Path resolution tests** for robust file handling

Run the test suite:
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test categories
pytest test_fluid.py -v
pytest test_integration_validation.py -v

# Quick tests without coverage (faster)
python run_tests.py quick
```

### Known Issue: Segmentation Fault in CI

You may occasionally see a segmentation fault (exit code 139) in CI after all tests pass successfully. This is a known issue that occurs during Python interpreter shutdown when using coverage reporting with certain C extensions (like NeqSim). The tests themselves pass correctly, and the segfault happens during cleanup.

**Workaround**: The CI workflows are configured to treat this as a success if the coverage report was generated successfully.

## API Reference

### Main Classes

- **`Fluid`**: Main class for fluid system creation and analysis
- **`Phase`**: Represents individual phases in the system
- **`AcidFormationAnalysis`**: Specialized analysis for acid formation risks

### Key Functions

- **`get_co2_parameters(pressure, temperature)`**: Calculate pure CO2 properties
- **`get_acid_fugacity_coeff(acid, pressure, temperature)`**: Calculate acid fugacity coefficients
- **`get_water_fugacity_coefficient(pressure, temperature)`**: Calculate water fugacity coefficients

## Limitations and Considerations

1. **Model applicability**: Limited to CO2-water-acid systems
2. **Pressure/temperature ranges**: Validated for CCS-relevant conditions
3. **Initial estimates**: Results should be verified with experimental data when available
4. **Mixing rules**: Binary interaction parameters are system-specific

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

**Important**: Pre-commit hooks are required for all contributions. Make sure to run `make setup-pre-commit` after cloning the repository.

## Release Process

This project uses automated releases via GitHub Actions. When you merge a pull request:

- **Patch release** (1.0.0 → 1.0.1): Default for bug fixes
- **Minor release** (1.0.0 → 1.1.0): Include "feat" or "feature" in PR title
- **Major release** (1.0.0 → 2.0.0): Include "breaking" or "major" in PR title

See [RELEASE_PROCESS.md](RELEASE_PROCESS.md) for detailed information.

## Citation

If you use SolubilityCCS in your research, please cite:

```bibtex
@software{solubilityccs,
  title = {SolubilityCCS: A Python package for analyzing solubility and acid formation in CCS systems},
  author = {SolubilityCCS Contributors},
  url = {https://github.com/your-username/SolubilityCCS},
  version = {1.0.0},
  year = {2025}
}
```

## License

See [LICENSE](LICENSE) for license information.

## Support

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](https://github.com/your-username/SolubilityCCS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/SolubilityCCS/discussions)
- **Email**: [Contact information]

---

**Note**: This package provides initial estimates for acid solubilities in CO2 streams. For critical applications, results should be validated against experimental data or more detailed models.
