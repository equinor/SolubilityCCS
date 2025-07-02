#!/usr/bin/env python3
"""
Example usage of the solubilityCCS package.

This script demonstrates how to use the package for basic CCS solubility analysis.
"""


def main():
    """Run a simple example of the SolubilityCCS package."""
    try:
        from solubilityccs import Fluid

        print("SolubilityCCS Example")
        print("=" * 50)

        # Create a fluid system
        fluid = Fluid()

        # Add components (example for CO2 with trace acids)
        fluid.add_component("CO2", 0.999)
        fluid.add_component("H2SO4", 10e-6)  # 10 ppm
        fluid.add_component("H2O", 10e-6)  # 10 ppm

        print(f"Components added: {fluid.components}")
        print(f"Fractions: {fluid.fractions}")

        # Set conditions (example for deep saline aquifer)
        fluid.set_temperature(275.15)  # 2°C
        fluid.set_pressure(60.0)  # 60 bara

        print(f"Temperature: {fluid.temperature} K")
        print(f"Pressure: {fluid.pressure} bar")

        # Perform calculations
        fluid.calc_vapour_pressure()
        fluid.flash_activity()

        # Display results
        print("\nResults:")
        print(f"Gas phase fraction (beta): {fluid.betta:.6f}")
        print(f"Number of phases: {len(fluid.phases)}")

        # Phase information
        for i, phase in enumerate(fluid.phases):
            if phase.fraction > 1e-10:  # Only show phases with significant fraction
                print(f"\nPhase {i} ({phase.name}):")
                print(f"  Fraction: {phase.fraction:.6f}")
                print(f"  Components: {phase.components}")
                print(f"  Component fractions: {[f'{x:.6f}' for x in phase.fractions]}")

        print("\nExample completed successfully!")

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure the package is properly installed.")
    except Exception as e:
        print(f"Error during execution: {e}")


if __name__ == "__main__":
    main()
