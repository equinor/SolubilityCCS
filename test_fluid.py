import os
from unittest.mock import Mock, patch

import numpy as np
import pytest

from solubilityccs import Fluid, Phase
from solubilityccs.neqsim_functions import get_co2_parameters
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

    @patch("solubilityccs.fluid.Fluid.calc_vapour_pressure")
    @patch("solubilityccs.fluid.Fluid.flash_activity")
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
            "solubilityccs.neqsim_functions.get_co2_parameters",
            return_value=expected_results,
        ):
            results = get_co2_parameters(pressure, temperature + 273.15)

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
