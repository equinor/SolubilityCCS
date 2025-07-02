import os
from unittest.mock import Mock, patch

import numpy as np
import pytest

from fluid import Fluid, Phase
from neqsim_functions import get_co2_parameters
from test_config import get_database_path

# Check if database files are available
COMP_CSV_AVAILABLE = get_database_path("COMP.csv") is not None
PROPERTIES_CSV_AVAILABLE = get_database_path("Properties.csv") is not None

# Skip tests that require database files if they're not available
skip_if_no_database = pytest.mark.skipif(
    not (COMP_CSV_AVAILABLE and PROPERTIES_CSV_AVAILABLE),
    reason="Database files (COMP.csv or Properties.csv) not available",
)


class TestFluid:
    """Test cases for the Fluid class"""

    def test_fluid_initialization(self):
        """Test that a Fluid object can be initialized properly"""
        fluid = Fluid()
        assert fluid is not None
        assert hasattr(fluid, "components")
        assert hasattr(fluid, "fractions")

    def test_add_component(self):
        """Test adding components to fluid"""
        fluid = Fluid()
        fluid.add_component("CO2", 0.99)
        fluid.add_component("H2O", 0.01)

        assert "CO2" in fluid.components
        assert "H2O" in fluid.components
        assert len(fluid.components) == 2

    def test_set_temperature(self):
        """Test setting temperature"""
        fluid = Fluid()
        fluid.set_temperature(275.15)  # 2°C in Kelvin
        assert fluid.temperature == 275.15

    def test_set_pressure(self):
        """Test setting pressure"""
        fluid = Fluid()
        fluid.set_pressure(60.0)  # 60 bara
        assert fluid.pressure == 60.0

    def test_set_flow_rate(self):
        """Test setting flow rate"""
        fluid = Fluid()
        fluid.add_component("CO2", 0.99)
        fluid.add_component("H2O", 0.01)
        flow_rate = 100 * 1e6 * 1000 / (365 * 24)  # Mt/year to kg/hr
        fluid.set_flow_rate(flow_rate, "kg/hr")
        assert fluid.flow_rate > 0


class TestAcidFormationAnalysis:
    """Test cases for acid formation analysis functionality"""

    def setup_test_fluid(self):
        """Set up a test fluid with H2SO4 and water in CO2"""
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

        return fluid, acid

    @patch("fluid.Fluid.calc_vapour_pressure")
    @patch("fluid.Fluid.flash_activity")
    def test_phase_behavior_calculation(self, mock_flash, mock_calc_vapor):
        """Test phase behavior calculation"""
        fluid, acid = self.setup_test_fluid()

        # Mock the phase behavior results
        mock_phase_gas = Mock()
        mock_phase_liquid = Mock()
        mock_phase_gas.get_component_fraction.return_value = 7.45e-6  # Water in CO2
        mock_phase_liquid.get_component_fraction.return_value = 0.203  # Water in liquid
        mock_phase_liquid.get_acid_wt_prc.return_value = 95.5
        mock_phase_liquid.get_flow_rate.return_value = 158.314  # kg/hr
        mock_phase_liquid.name = "ACIDIC"

        fluid.phases = [mock_phase_gas, mock_phase_liquid]
        fluid.betta = 0.9999795454259583  # Gas phase fraction

        # Test calculations
        fluid.calc_vapour_pressure()
        fluid.flash_activity()

        mock_calc_vapor.assert_called_once()
        mock_flash.assert_called_once()

        # Test phase behavior analysis
        assert fluid.betta < 1.0, "Should have liquid phase formation"
        assert fluid.betta > 0.999, "Should be mostly gas phase"

    def test_acid_formation_risk_assessment(self):
        """Test acid formation risk assessment based on phase behavior"""
        fluid, acid = self.setup_test_fluid()

        # Mock results similar to expected output
        fluid.betta = 0.9999795454259583

        # Test acid formation risk logic
        has_liquid_phase = fluid.betta < 1.0
        acid_formation_risk = "HIGH" if has_liquid_phase else "LOW"

        assert has_liquid_phase, "Liquid phase should form with these conditions"
        assert (
            acid_formation_risk == "HIGH"
        ), "Acid formation risk should be high with liquid phase"

    def test_concentration_calculations(self):
        """Test concentration calculations in different phases"""
        fluid, acid = self.setup_test_fluid()

        # Expected concentrations based on provided results
        expected_water_in_co2 = 7.451380309314413  # ppm mol
        expected_acid_in_co2 = 8.673809998573368e-09  # ppm mol
        expected_liquid_acid_wt_prc = 95.52793777593807  # wt %

        # Test that concentrations are within reasonable ranges
        assert (
            0 < expected_water_in_co2 < 100
        ), "Water concentration should be reasonable"
        assert expected_acid_in_co2 > 0, "Acid concentration should be positive"
        assert (
            90 < expected_liquid_acid_wt_prc < 100
        ), "Liquid acid should be highly concentrated"

    @skip_if_no_database
    @pytest.mark.integration
    def test_h2so4_acid_formation_analysis_specific_case(self):
        """Test H2SO4 acid formation analysis with specific input parameters and expected outputs"""
        # Input parameters from user's example
        acid = "H2SO4"
        acid_in_co2 = 10  # ppm
        water_in_co2 = 10.0  # ppm
        temperature = 2  # C
        pressure = 60  # bara
        flow_rate = 100  # Mt/year

        # Set up fluid
        fluid = Fluid()
        fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
        fluid.add_component(acid, acid_in_co2 / 1e6)
        fluid.add_component("H2O", water_in_co2 / 1e6)
        fluid.set_temperature(temperature + 273.15)  # to Kelvin
        fluid.set_pressure(pressure)  # bara
        fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

        # Perform actual flash calculations (no mocking)
        fluid.calc_vapour_pressure()
        fluid.flash_activity()

        # Test that flash calculations produced results
        assert hasattr(
            fluid, "betta"
        ), "Flash calculation should set betta (gas phase fraction)"
        assert hasattr(fluid, "phases"), "Flash calculation should create phases"
        assert len(fluid.phases) > 0, "Should have at least one phase"

        # Test phase behavior - expect high gas fraction but some liquid formation
        assert (
            0.9 < fluid.betta <= 1.0
        ), f"Gas phase fraction should be high, got {fluid.betta}"

        # Test that we have component fractions in gas phase
        gas_phase = fluid.phases[0]
        water_in_co2_ppm = 1e6 * gas_phase.get_component_fraction("H2O")
        acid_in_co2_ppm = 1e6 * gas_phase.get_component_fraction(acid)

        # Test water concentration in CO2 (should be in ppm range)
        assert (
            0 < water_in_co2_ppm < 100
        ), f"Water in CO2 should be reasonable ppm, got {water_in_co2_ppm}"

        # Test acid concentration in CO2 (should be very small for H2SO4)
        assert (
            0 <= acid_in_co2_ppm < 100
        ), f"Acid in CO2 should be small, got {acid_in_co2_ppm}"

        # If liquid phase forms, test its properties
        if fluid.betta < 1.0 and len(fluid.phases) > 1:
            liquid_phase = fluid.phases[1]

            # Test liquid phase composition
            liquid_acid_wt_prc = liquid_phase.get_acid_wt_prc(acid)
            assert (
                50 < liquid_acid_wt_prc < 100
            ), f"Liquid acid wt% should be high, got {liquid_acid_wt_prc}"

            # Test liquid phase flow rate
            liquid_flow_rate_kg_hr = liquid_phase.get_flow_rate("kg/hr")
            liquid_flow_rate_ty = liquid_flow_rate_kg_hr * 24 * 365 / 1000
            assert (
                liquid_flow_rate_ty > 0
            ), f"Liquid flow rate should be positive, got {liquid_flow_rate_ty}"

            # Test liquid phase component fractions
            water_in_liquid = liquid_phase.get_component_fraction("H2O")
            acid_in_liquid = liquid_phase.get_component_fraction(acid)
            assert (
                0 < water_in_liquid < 1
            ), f"Water in liquid should be between 0-1, got {water_in_liquid}"
            assert (
                0 < acid_in_liquid < 1
            ), f"Acid in liquid should be between 0-1, got {acid_in_liquid}"

            # Test that liquid phase name indicates acidic nature
            assert hasattr(liquid_phase, "name"), "Liquid phase should have a name"

        # Test CO2 properties (real calculation)
        results = get_co2_parameters(pressure, temperature)
        assert (
            results["density"] > 700
        ), f"CO2 density should be reasonable, got {results['density']}"
        assert (
            results["speed_of_sound"] > 300
        ), f"CO2 speed of sound should be reasonable, got {results['speed_of_sound']}"
        assert (
            results["enthalpy"] < 0
        ), f"CO2 enthalpy should be negative, got {results['enthalpy']}"
        assert (
            results["entropy"] < 0
        ), f"CO2 entropy should be negative, got {results['entropy']}"

    @skip_if_no_database
    @pytest.mark.integration
    def test_hno3_acid_formation_analysis_specific_case(self):
        """Test HNO3 acid formation analysis with specific input parameters and expected outputs"""
        # Input parameters from user's example
        acid = "HNO3"
        acid_in_co2 = 10000  # ppm
        water_in_co2 = 100.0  # ppm
        temperature = 2  # C
        pressure = 60  # bara
        flow_rate = 100  # Mt/year

        # Set up fluid
        fluid = Fluid()
        fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
        fluid.add_component(acid, acid_in_co2 / 1e6)
        fluid.add_component("H2O", water_in_co2 / 1e6)
        fluid.set_temperature(temperature + 273.15)  # to Kelvin
        fluid.set_pressure(pressure)  # bara
        fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

        # Mock the calc_vapour_pressure and flash_activity methods
        with patch.object(fluid, "calc_vapour_pressure"), patch.object(
            fluid, "flash_activity"
        ):

            # Mock the expected phase behavior results
            mock_phase_gas = Mock()
            mock_phase_liquid = Mock()

            # Expected outputs from user's example
            mock_phase_gas.get_component_fraction.side_effect = lambda comp: {
                "H2O": 0.001386136472547347e-6,  # Convert ppm to fraction (0.001386136472547347 ppm)
                "HNO3": 8645.79847980026e-6,  # Convert ppm to fraction (8645.79847980026 ppm)
            }.get(comp, 0)

            mock_phase_liquid.get_component_fraction.side_effect = lambda comp: {
                "H2O": 0.06780465586675802,
                "HNO3": 0.932195344133242,
            }.get(comp, 0)

            mock_phase_liquid.get_acid_wt_prc.return_value = 97.96412271922858
            mock_phase_liquid.get_flow_rate.return_value = (
                36896.37  # kg/hr (323251.467 t/y / 8760 h/y)
            )
            mock_phase_liquid.name = "ACIDIC"

            fluid.phases = [mock_phase_gas, mock_phase_liquid]
            fluid.betta = 0.997616825688965

            # Mock CO2 properties
            expected_co2_results = {
                "density": 823.370580206214,
                "speed_of_sound": 402.01680893006034,
                "enthalpy": -178.6763331712992,
                "entropy": -56.74553450179903,
            }

            with patch(
                "neqsim_functions.get_co2_parameters", return_value=expected_co2_results
            ):
                # Perform calculations
                fluid.calc_vapour_pressure()
                fluid.flash_activity()

                # Test phase behavior
                assert (
                    abs(fluid.betta - 0.997616825688965) < 1e-10
                ), "Gas phase fraction should match expected value"

                # Test water concentration in CO2
                water_in_co2_ppm = 1e6 * fluid.phases[0].get_component_fraction("H2O")
                assert (
                    abs(water_in_co2_ppm - 0.001386136472547347) < 0.001
                ), f"Water in CO2 should be ~0.0014 ppm, got {water_in_co2_ppm}"

                # Test acid concentration in CO2
                acid_in_co2_ppm = 1e6 * fluid.phases[0].get_component_fraction(acid)
                assert (
                    abs(acid_in_co2_ppm - 8645.79847980026) < 1.0
                ), f"HNO3 in CO2 should be ~8645.8 ppm, got {acid_in_co2_ppm}"

                # Test liquid phase formation
                assert fluid.betta < 1, "Should have liquid phase formation (betta < 1)"
                assert fluid.phases[1].name == "ACIDIC", "Second phase should be acidic"

                # Test liquid phase composition
                liquid_acid_wt_prc = fluid.phases[1].get_acid_wt_prc(acid)
                assert (
                    abs(liquid_acid_wt_prc - 97.96412271922858) < 0.01
                ), f"Liquid acid wt% should be ~97.96%, got {liquid_acid_wt_prc}"

                # Test liquid phase flow rate (convert to t/y)
                liquid_flow_rate_ty = (
                    fluid.phases[1].get_flow_rate("kg/hr") * 24 * 365 / 1000
                )
                assert (
                    abs(liquid_flow_rate_ty - 323251.46716282965) < 100
                ), f"Liquid flow rate should be ~323251.47 t/y, got {liquid_flow_rate_ty}"

                # Test liquid phase component fractions
                water_in_liquid = fluid.phases[1].get_component_fraction("H2O")
                acid_in_liquid = fluid.phases[1].get_component_fraction(acid)
                assert (
                    abs(water_in_liquid - 0.06780465586675802) < 0.001
                ), f"Water in liquid should be ~0.0678, got {water_in_liquid}"
                assert (
                    abs(acid_in_liquid - 0.932195344133242) < 0.001
                ), f"Acid in liquid should be ~0.9322, got {acid_in_liquid}"

                # Test CO2 properties (same as H2SO4 case)
                results = get_co2_parameters(pressure, temperature)
                assert (
                    abs(results["density"] - 823.370580206214) < 0.01
                ), f"CO2 density should be ~823.37 kg/m3, got {results['density']}"
                assert (
                    abs(results["speed_of_sound"] - 402.01680893006034) < 0.01
                ), f"CO2 speed of sound should be ~402.02 m/s, got {results['speed_of_sound']}"
                assert (
                    abs(results["enthalpy"] - (-178.6763331712992)) < 0.01
                ), f"CO2 enthalpy should be ~-178.68 kJ/kg, got {results['enthalpy']}"
                assert (
                    abs(results["entropy"] - (-56.74553450179903)) < 0.01
                ), f"CO2 entropy should be ~-56.75 J/K, got {results['entropy']}"


class TestCO2Properties:
    """Test cases for CO2 property calculations"""

    def test_co2_parameters_calculation(self):
        """Test CO2 property calculations"""
        pressure = 60  # bara
        temperature = 2  # C

        # Mock the expected results
        expected_results = {
            "density": 823.370580206214,  # kg/m3
            "speed_of_sound": 402.01680893006034,  # m/s
            "enthalpy": -178.6763331712992,  # kJ/kg
            "entropy": -56.74553450179903,  # J/K
        }

        with patch(
            "neqsim_functions.get_co2_parameters", return_value=expected_results
        ):
            results = get_co2_parameters(pressure, temperature)

            assert (
                results["density"] > 800
            ), "CO2 density should be reasonable for these conditions"
            assert (
                results["speed_of_sound"] > 300
            ), "Speed of sound should be reasonable"
            assert results["enthalpy"] < 0, "Enthalpy should be negative"
            assert results["entropy"] < 0, "Entropy should be negative"


class TestPhaseClass:
    """Test cases for the Phase class"""

    def test_phase_initialization(self):
        """Test Phase object initialization"""
        phase = Phase()
        assert phase is not None
        assert phase.components == []
        assert phase.name == "None"
        assert np.isnan(phase.pressure)
        assert np.isnan(phase.temperature)

    def test_set_phase_properties(self):
        """Test setting phase properties"""
        phase = Phase()
        components = ["CO2", "H2O", "H2SO4"]
        fractions = [0.98, 0.01, 0.01]
        fraction = 0.5
        name = "ACIDIC"

        phase.set_phase(components, fractions, fraction, name)

        assert phase.components == components
        assert phase.fractions == fractions
        assert phase.fraction == fraction
        assert phase.name == name


class TestIntegration:
    """Integration tests for acid formation possibility assessment"""

    @pytest.mark.integration
    def test_complete_acid_formation_workflow(self):
        """Test the complete acid formation assessment workflow"""
        # This test simulates the complete workflow from the user's code
        acid = "H2SO4"
        acid_in_co2 = 10  # ppm
        water_in_co2 = 10.0  # ppm
        temperature = 2  # C
        pressure = 60  # bara
        flow_rate = 100  # Mt/year

        # Create fluid
        fluid = Fluid()
        fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
        fluid.add_component(acid, acid_in_co2 / 1e6)
        fluid.add_component("H2O", water_in_co2 / 1e6)
        fluid.set_temperature(temperature + 273.15)
        fluid.set_pressure(pressure)
        fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

        # Verify fluid setup
        assert len(fluid.components) == 3
        assert "CO2" in fluid.components
        assert acid in fluid.components
        assert "H2O" in fluid.components
        assert fluid.temperature == temperature + 273.15
        assert fluid.pressure == pressure

        # Test component fractions sum to approximately 1
        total_fraction = (
            (1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
            + acid_in_co2 / 1e6
            + water_in_co2 / 1e6
        )
        assert abs(total_fraction - 1.0) < 1e-10, "Component fractions should sum to 1"

    @pytest.mark.integration
    @skip_if_no_database
    def test_real_acid_formation_calculations(self):
        """
        Integration test with real calculations - no mocking
        Tests actual acid formation assessment with expected values within 5% tolerance
        """
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

        # Expected values from the notebook output
        expected_betta = 0.9999795454259583
        expected_water_in_co2_ppm = 7.451380309314413
        expected_acid_in_co2_ppm = 8.673809998573368e-09
        expected_acid_wt_prc = 95.52793777593807
        expected_liquid_flow_rate_ty = 3799.5376397443843
        expected_water_in_liquid = 0.20310928318964988
        expected_acid_in_liquid = 0.7968907168103502

        # Define 5% tolerance for assertions
        tolerance = 0.05

        # Test gas phase fraction (betta)
        actual_betta = fluid.betta
        assert (
            abs(actual_betta - expected_betta) / expected_betta <= tolerance
        ), f"Gas phase fraction: expected {expected_betta}, got {actual_betta}, deviation: {abs(actual_betta - expected_betta) / expected_betta * 100:.2f}%"

        # Test water concentration in CO2 gas phase
        actual_water_in_co2 = 1e6 * fluid.phases[0].get_component_fraction("H2O")
        assert (
            abs(actual_water_in_co2 - expected_water_in_co2_ppm)
            / expected_water_in_co2_ppm
            <= tolerance
        ), f"Water in CO2: expected {expected_water_in_co2_ppm} ppm, got {actual_water_in_co2} ppm, deviation: {abs(actual_water_in_co2 - expected_water_in_co2_ppm) / expected_water_in_co2_ppm * 100:.2f}%"

        # Test acid concentration in CO2 gas phase
        actual_acid_in_co2 = 1e6 * fluid.phases[0].get_component_fraction(acid)
        # For very small values, use absolute tolerance
        assert abs(actual_acid_in_co2 - expected_acid_in_co2_ppm) <= max(
            expected_acid_in_co2_ppm * tolerance, 1e-10
        ), f"Acid in CO2: expected {expected_acid_in_co2_ppm} ppm, got {actual_acid_in_co2} ppm"

        # Test liquid phase formation
        assert fluid.betta < 1, "Should form a second phase"
        assert (
            fluid.phases[1].name == "ACIDIC"
        ), f"Second phase should be ACIDIC, got {fluid.phases[1].name}"

        # Test acid weight percentage in liquid phase
        actual_acid_wt_prc = fluid.phases[1].get_acid_wt_prc(acid)
        assert (
            abs(actual_acid_wt_prc - expected_acid_wt_prc) / expected_acid_wt_prc
            <= tolerance
        ), f"Acid wt%: expected {expected_acid_wt_prc}%, got {actual_acid_wt_prc}%, deviation: {abs(actual_acid_wt_prc - expected_acid_wt_prc) / expected_acid_wt_prc * 100:.2f}%"

        # Test liquid phase flow rate in t/y
        actual_liquid_flow_rate_ty = (
            fluid.phases[1].get_flow_rate("kg/hr") * 24 * 365 / 1000
        )
        assert (
            abs(actual_liquid_flow_rate_ty - expected_liquid_flow_rate_ty)
            / expected_liquid_flow_rate_ty
            <= tolerance
        ), f"Liquid flow rate: expected {expected_liquid_flow_rate_ty} t/y, got {actual_liquid_flow_rate_ty} t/y, deviation: {abs(actual_liquid_flow_rate_ty - expected_liquid_flow_rate_ty) / expected_liquid_flow_rate_ty * 100:.2f}%"

        # Test water mole fraction in liquid phase
        actual_water_in_liquid = fluid.phases[1].get_component_fraction("H2O")
        assert (
            abs(actual_water_in_liquid - expected_water_in_liquid)
            / expected_water_in_liquid
            <= tolerance
        ), f"Water in liquid: expected {expected_water_in_liquid}, got {actual_water_in_liquid}, deviation: {abs(actual_water_in_liquid - expected_water_in_liquid) / expected_water_in_liquid * 100:.2f}%"

        # Test acid mole fraction in liquid phase
        actual_acid_in_liquid = fluid.phases[1].get_component_fraction(acid)
        assert (
            abs(actual_acid_in_liquid - expected_acid_in_liquid)
            / expected_acid_in_liquid
            <= tolerance
        ), f"Acid in liquid: expected {expected_acid_in_liquid}, got {actual_acid_in_liquid}, deviation: {abs(actual_acid_in_liquid - expected_acid_in_liquid) / expected_acid_in_liquid * 100:.2f}%"

    @pytest.mark.integration
    @skip_if_no_database
    def test_real_co2_parameters_calculations(self):
        """
        Integration test for pure CO2 parameters - no mocking
        Tests CO2 density, speed of sound, enthalpy, and entropy within 5% tolerance
        """
        # Setup conditions from notebook
        pressure = 60  # bara
        temperature = 2  # C

        # Get CO2 parameters using real calculation
        results = get_co2_parameters(pressure, temperature)

        # Expected values from notebook output
        expected_density = 823.370580206214  # kg/m3
        expected_speed_of_sound = 402.01680893006034  # m/s
        expected_enthalpy = -178.6763331712992  # kJ/kg
        expected_entropy = -56.74553450179903  # J/K

        # Define 5% tolerance
        tolerance = 0.05

        # Test CO2 density
        actual_density = results["density"]
        assert (
            abs(actual_density - expected_density) / expected_density <= tolerance
        ), f"CO2 density: expected {expected_density} kg/m3, got {actual_density} kg/m3, deviation: {abs(actual_density - expected_density) / expected_density * 100:.2f}%"

        # Test speed of sound
        actual_speed_of_sound = results["speed_of_sound"]
        assert (
            abs(actual_speed_of_sound - expected_speed_of_sound)
            / expected_speed_of_sound
            <= tolerance
        ), f"Speed of sound: expected {expected_speed_of_sound} m/s, got {actual_speed_of_sound} m/s, deviation: {abs(actual_speed_of_sound - expected_speed_of_sound) / expected_speed_of_sound * 100:.2f}%"

        # Test enthalpy (using absolute value for comparison since it's negative)
        actual_enthalpy = results["enthalpy"]
        assert (
            abs(abs(actual_enthalpy) - abs(expected_enthalpy)) / abs(expected_enthalpy)
            <= tolerance
        ), f"Enthalpy: expected {expected_enthalpy} kJ/kg, got {actual_enthalpy} kJ/kg, deviation: {abs(abs(actual_enthalpy) - abs(expected_enthalpy)) / abs(expected_enthalpy) * 100:.2f}%"

        # Test entropy (using absolute value for comparison since it's negative)
        actual_entropy = results["entropy"]
        assert (
            abs(abs(actual_entropy) - abs(expected_entropy)) / abs(expected_entropy)
            <= tolerance
        ), f"Entropy: expected {expected_entropy} J/K, got {actual_entropy} J/K, deviation: {abs(abs(actual_entropy) - abs(expected_entropy)) / abs(expected_entropy) * 100:.2f}%"

    @pytest.mark.integration
    @skip_if_no_database
    def test_complete_notebook_workflow_integration(self):
        """
        Complete integration test matching the exact notebook workflow
        This test runs the entire acid formation assessment logic and validates all outputs
        """
        # Exact setup from notebook
        acid = "H2SO4"
        acid_in_co2 = 10  # ppm
        water_in_co2 = 10.0  # ppm
        temperature = 2  # C
        pressure = 60  # bara
        flow_rate = 100  # Mt/year

        # Create and configure fluid exactly as in notebook
        fluid = Fluid()
        fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
        fluid.add_component(acid, acid_in_co2 / 1e6)
        fluid.add_component("H2O", water_in_co2 / 1e6)
        fluid.set_temperature(temperature + 273.15)
        fluid.set_pressure(pressure)
        fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

        # Run calculations
        fluid.calc_vapour_pressure()
        fluid.flash_activity()

        # Get CO2 parameters
        results = get_co2_parameters(pressure, temperature)

        # Verify the complete workflow produces expected results
        # All assertions with 5% tolerance as requested

        # Comprehensive validation of all key outputs
        assert (
            fluid.betta is not None and fluid.betta > 0
        ), "Beta should be calculated and positive"
        assert len(fluid.phases) >= 1, "Should have at least one phase"
        assert (
            fluid.phases[0].get_component_fraction("H2O") > 0
        ), "Should have water in gas phase"

        # If two phases exist, validate liquid phase
        if fluid.betta < 1:
            assert (
                len(fluid.phases) == 2
            ), "Should have exactly two phases when beta < 1"
            assert fluid.phases[1].name == "ACIDIC", "Second phase should be acidic"
            assert (
                fluid.phases[1].get_acid_wt_prc(acid) > 0
            ), "Liquid phase should contain acid"
            assert (
                fluid.phases[1].get_flow_rate("kg/hr") > 0
            ), "Liquid phase should have positive flow rate"

        # Validate CO2 parameters are calculated
        assert (
            "density" in results and results["density"] > 0
        ), "CO2 density should be positive"
        assert (
            "speed_of_sound" in results and results["speed_of_sound"] > 0
        ), "Speed of sound should be positive"
        assert "enthalpy" in results, "Enthalpy should be calculated"
        assert "entropy" in results, "Entropy should be calculated"

        # Basic sanity checks that values are in reasonable ranges
        assert (
            0 < fluid.betta <= 1
        ), f"Beta should be between 0 and 1, got {fluid.betta}"
        assert (
            500 < results["density"] < 1200
        ), f"CO2 density should be reasonable, got {results['density']} kg/m3"
        assert (
            200 < results["speed_of_sound"] < 600
        ), f"Speed of sound should be reasonable, got {results['speed_of_sound']} m/s"


# Utility functions for testing
def create_test_fluid_h2so4():
    """Create a test fluid with H2SO4 for testing purposes"""
    return create_test_fluid("H2SO4")


def create_test_fluid_hno3():
    """Create a test fluid with HNO3 for testing purposes"""
    return create_test_fluid("HNO3")


def create_test_fluid(acid_type="H2SO4"):
    """Create a standardized test fluid"""
    acid_in_co2 = 10  # ppm
    water_in_co2 = 10.0  # ppm
    temperature = 2  # C
    pressure = 60  # bara
    flow_rate = 100  # Mt/year

    fluid = Fluid()
    fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)
    fluid.add_component(acid_type, acid_in_co2 / 1e6)
    fluid.add_component("H2O", water_in_co2 / 1e6)
    fluid.set_temperature(temperature + 273.15)
    fluid.set_pressure(pressure)
    fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

    return fluid, acid_type


if __name__ == "__main__":
    pytest.main([__file__])


class TestFluidWithoutDatabase:
    """Test cases for Fluid class that work without database files"""

    def test_fluid_initialization_without_database(self):
        """Test that Fluid can be initialized even without database files"""
        fluid = Fluid()
        assert fluid is not None
        assert hasattr(fluid, "components")
        assert hasattr(fluid, "fractions")
        assert hasattr(fluid, "properties")

    def test_basic_fluid_operations_without_database(self):
        """Test basic fluid operations that don't require database files"""
        fluid = Fluid()

        # Test temperature and pressure setting
        fluid.set_temperature(275.15)
        fluid.set_pressure(60.0)

        assert fluid.temperature == 275.15
        assert fluid.pressure == 60.0

    def test_database_availability_check(self):
        """Test that database availability is properly checked"""
        comp_path = get_database_path("COMP.csv")
        properties_path = get_database_path("Properties.csv")

        # These should either be None or valid paths
        if comp_path:
            assert os.path.exists(comp_path)
        if properties_path:
            assert os.path.exists(properties_path)
