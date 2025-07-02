#!/usr/bin/env python3
"""Validation script for acid formation assessment calculations.

This demonstrates that our integration tests are working with real calculations.
Can be run as a script or as pytest tests.
"""

import pytest

from solubilityccs import Fluid
from solubilityccs.neqsim_functions import get_co2_parameters


def validate_acid_formation_calculations():
    """Core validation logic that can be used by both script and pytest."""
    # Setup exactly as in the notebook
    acid = "H2SO4"
    acid_in_co2 = 10  # ppm
    water_in_co2 = 10.0  # ppm
    temperature = 2  # C
    pressure = 60  # bara
    flow_rate = 100  # Mt/year

    fluid = Fluid()
    fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
    fluid.add_component(acid, acid_in_co2 / 1e6)
    fluid.add_component("H2O", water_in_co2 / 1e6)
    fluid.set_temperature(temperature + 273.15)
    fluid.set_pressure(pressure)
    fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

    # Perform the actual calculations
    fluid.calc_vapour_pressure()
    fluid.flash_activity()

    # Expected values from notebook output
    expected_values = {
        "betta": 0.9999795454259583,
        "water_in_co2_ppm": 7.451380309314413,
        "acid_in_co2_ppm": 8.673809998573368e-09,
        "acid_wt_prc": 95.52793777593807,
        "liquid_flow_rate_ty": 3799.5376397443843,
        "water_in_liquid": 0.20310928318964988,
        "acid_in_liquid": 0.7968907168103502,
    }

    # Calculate actual values
    actual_values = {
        "betta": fluid.betta,
        "water_in_co2_ppm": 1e6 * fluid.phases[0].get_component_fraction("H2O"),
        "acid_in_co2_ppm": 1e6 * fluid.phases[0].get_component_fraction(acid),
        "acid_wt_prc": fluid.phases[1].get_acid_wt_prc(acid),
        "liquid_flow_rate_ty": fluid.phases[1].get_flow_rate("kg/hr") * 24 * 365 / 1000,
        "water_in_liquid": fluid.phases[1].get_component_fraction("H2O"),
        "acid_in_liquid": fluid.phases[1].get_component_fraction(acid),
    }

    return expected_values, actual_values, pressure, temperature


def test_phase_behavior_validation():
    """Test phase behavior calculations with pytest assertions."""
    expected_values, actual_values, _, _ = validate_acid_formation_calculations()
    tolerance = 5.0  # percent

    # Test gas phase fraction (betta)
    deviation = (
        abs(actual_values["betta"] - expected_values["betta"])
        / expected_values["betta"]
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"Gas phase fraction deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

    # Test water in CO2
    deviation = (
        abs(actual_values["water_in_co2_ppm"] - expected_values["water_in_co2_ppm"])
        / expected_values["water_in_co2_ppm"]
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"Water in CO2 deviation {deviation:.4f}% exceeds {tolerance}% tolerance"


def test_acid_formation_validation():
    """Test acid formation calculations with pytest assertions."""
    expected_values, actual_values, _, _ = validate_acid_formation_calculations()
    tolerance = 5.0  # percent

    # Test acid weight percentage in liquid phase
    deviation = (
        abs(actual_values["acid_wt_prc"] - expected_values["acid_wt_prc"])
        / expected_values["acid_wt_prc"]
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"Acid wt% deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

    # Test liquid flow rate
    deviation = (
        abs(
            actual_values["liquid_flow_rate_ty"]
            - expected_values["liquid_flow_rate_ty"]
        )
        / expected_values["liquid_flow_rate_ty"]
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"Liquid flow rate deviation {deviation:.4f}% exceeds {tolerance}% tolerance"


def test_co2_parameters_validation():
    """Test CO2 parameter calculations with pytest assertions."""
    _, _, pressure, temperature = validate_acid_formation_calculations()

    results = get_co2_parameters(pressure, temperature)
    expected_co2 = {
        "density": 823.370580206214,
        "speed_of_sound": 402.01680893006034,
        "enthalpy": -178.6763331712992,
        "entropy": -56.74553450179903,
    }

    tolerance = 5.0  # percent

    # Test density
    deviation = (
        abs(results["density"] - expected_co2["density"])
        / expected_co2["density"]
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"CO2 density deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

    # Test speed of sound
    deviation = (
        abs(results["speed_of_sound"] - expected_co2["speed_of_sound"])
        / expected_co2["speed_of_sound"]
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"CO2 speed of sound deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

    # Test enthalpy
    deviation = (
        abs(abs(results["enthalpy"]) - abs(expected_co2["enthalpy"]))
        / abs(expected_co2["enthalpy"])
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"CO2 enthalpy deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

    # Test entropy
    deviation = (
        abs(abs(results["entropy"]) - abs(expected_co2["entropy"]))
        / abs(expected_co2["entropy"])
        * 100
    )
    assert (
        deviation <= tolerance
    ), f"CO2 entropy deviation {deviation:.4f}% exceeds {tolerance}% tolerance"


class TestIntegrationValidation:
    """Test class for integration validation to ensure pytest discovery."""

    def test_integration_acid_formation_phase_behavior(self):
        """Test phase behavior calculations with pytest assertions."""
        test_phase_behavior_validation()

    def test_integration_acid_formation_validation(self):
        """Test acid formation calculations with pytest assertions."""
        test_acid_formation_validation()

    def test_integration_co2_parameters_validation(self):
        """Test CO2 parameter calculations with pytest assertions."""
        test_co2_parameters_validation()


if __name__ == "__main__":
    # Run the tests when executed as a script
    pytest.main([__file__, "-v"])
