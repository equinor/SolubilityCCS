#!/usr/bin/env python3
"""Integration validation tests for acid formation assessment calculations.

This test file contains pytest-compatible tests that validate the integration
of acid formation assessment calculations with real data and expected results.
"""

from solubilityccs import Fluid
from solubilityccs.neqsim_functions import get_co2_parameters


class TestIntegrationValidation:
    """Test class for integration validation of acid formation assessment."""

    def test_h2so4_acid_formation_validation(self):
        """Test H2SO4 acid formation calculations against expected notebook results."""
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
            "liquid_flow_rate_ty": (
                fluid.phases[1].get_flow_rate("kg/hr") * 24 * 365 / 1000
            ),
            "water_in_liquid": fluid.phases[1].get_component_fraction("H2O"),
            "acid_in_liquid": fluid.phases[1].get_component_fraction(acid),
        }

        # Test phase behavior with 5% tolerance
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

        # Test liquid phase component fractions
        deviation = (
            abs(actual_values["water_in_liquid"] - expected_values["water_in_liquid"])
            / expected_values["water_in_liquid"]
            * 100
        )
        assert (
            deviation <= tolerance
        ), f"Water in liquid deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

        deviation = (
            abs(actual_values["acid_in_liquid"] - expected_values["acid_in_liquid"])
            / expected_values["acid_in_liquid"]
            * 100
        )
        assert (
            deviation <= tolerance
        ), f"Acid in liquid deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

    def test_co2_parameters_validation(self):
        """Test CO2 parameter calculations against expected results."""
        temperature = 2  # C
        pressure = 60  # bara

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

        # Test enthalpy (using absolute values due to negative values)
        deviation = (
            abs(abs(results["enthalpy"]) - abs(expected_co2["enthalpy"]))
            / abs(expected_co2["enthalpy"])
            * 100
        )
        assert (
            deviation <= tolerance
        ), f"CO2 enthalpy deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

        # Test entropy (using absolute values due to negative values)
        deviation = (
            abs(abs(results["entropy"]) - abs(expected_co2["entropy"]))
            / abs(expected_co2["entropy"])
            * 100
        )
        assert (
            deviation <= tolerance
        ), f"CO2 entropy deviation {deviation:.4f}% exceeds {tolerance}% tolerance"

    def test_integration_workflow_validation(self):
        """Test the complete integration workflow without mocking."""
        # This test ensures that all components work together
        acid = "H2SO4"
        acid_in_co2 = 10  # ppm
        water_in_co2 = 10.0  # ppm
        temperature = 2  # C
        pressure = 60  # bara
        flow_rate = 100  # Mt/year

        # Test that we can create a fluid and perform all calculations
        fluid = Fluid()
        assert fluid is not None, "Fluid object should be created"

        fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
        fluid.add_component(acid, acid_in_co2 / 1e6)
        fluid.add_component("H2O", water_in_co2 / 1e6)

        # Set conditions
        fluid.set_temperature(temperature + 273.15)
        fluid.set_pressure(pressure)
        fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

        # Perform calculations
        fluid.calc_vapour_pressure()
        fluid.flash_activity()

        # Test that we get reasonable results
        assert hasattr(fluid, "betta"), "Fluid should have betta attribute"
        assert 0 <= fluid.betta <= 1, "Betta should be between 0 and 1"
        assert len(fluid.phases) >= 2, "Fluid should have at least 2 phases"

        # Test CO2 parameters
        co2_results = get_co2_parameters(pressure, temperature)
        assert "density" in co2_results, "CO2 results should include density"
        assert (
            "speed_of_sound" in co2_results
        ), "CO2 results should include speed of sound"
        assert "enthalpy" in co2_results, "CO2 results should include enthalpy"
        assert "entropy" in co2_results, "CO2 results should include entropy"

        # Test that density is reasonable for CO2 at these conditions
        assert co2_results["density"] > 0, "CO2 density should be positive"
        assert (
            co2_results["speed_of_sound"] > 0
        ), "CO2 speed of sound should be positive"
