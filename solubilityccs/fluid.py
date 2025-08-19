import atexit
import math
import warnings
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from neqsim import jneqsim
from scipy.optimize import bisect

from .neqsim_functions import get_acid_fugacity_coeff, get_water_fugacity_coefficient
from .path_utils import get_database_path
from .sulfuric_acid_activity import calc_activity_water_h2so4

# Suppress runtime warnings
warnings.filterwarnings("ignore")

# Global variable to track database initialization
_database_initialized = False


def _cleanup_jpype():
    """Clean up JPype resources to prevent segmentation faults."""
    try:
        import jpype

        if jpype.isJVMStarted():
            jpype.shutdownJVM()
    except (ImportError, Exception):
        # If JPype is not available or shutdown fails, just continue
        pass


# Register cleanup function to run at exit
atexit.register(_cleanup_jpype)


def _initialize_database():
    """Initialize the neqsim database if not already done."""
    global _database_initialized
    if not _database_initialized:
        try:
            comp_database_path = get_database_path("COMP.csv")
            jneqsim.util.database.NeqSimDataBase.replaceTable(
                "COMP", comp_database_path
            )
            _database_initialized = True
        except FileNotFoundError as e:
            raise RuntimeError(f"Failed to initialize COMP database: {str(e)}") from e


class Phase:
    def __init__(self):
        self.components = []
        self.pressure = np.nan
        self.temperature = np.nan
        self.database = np.nan
        self.reading_properties: Dict[str, List[float]] = {}
        self.flow_rate = 1e-10
        self.fractions = []
        self.fraction = np.nan
        self.name = "None"

    def phase_to_fluid(self):

        fluid = Fluid()
        for component, fraction in zip(self.components, self.fractions):
            fluid.add_component(component, fraction)
        fluid.set_temperature(self.temperature)
        fluid.set_pressure(self.pressure)
        fluid.set_flow_rate(self.get_flow_rate("kg/hr"), "kg/hr")

        return fluid

    def set_phase(self, components, fractions, fraction, name):
        self.components = components
        self.fractions = fractions
        self.fraction = fraction
        self.name = name

    def set_database(self, database):
        self.database = database

    def set_properties(self, reading_properties):
        self.reading_properties = reading_properties

    def set_pressure(self, pressure):
        self.pressure = pressure

    def set_temperature(self, temperature):
        self.temperature = temperature

    def get_phase_fraction(self):
        return self.fraction

    def get_fractions(self):
        return self.fractions

    def get_component_fractions(self):
        return dict(zip(self.components, self.fractions))

    def set_phase_flow_rate(self, total_flow_rate):
        self.flow_rate = total_flow_rate * self.fraction

    def get_molar_mass(self):
        self.MW = 0
        for i, component in enumerate(self.components):
            self.MW += self.reading_properties["M"][i] * self.fractions[i] / 1000
        return self.MW

    def get_fraction_component(self, component):
        for i, componenti in enumerate(self.components):

            if component == componenti:
                return self.fractions[i]
        return 0

    def get_flow_rate(self, unit):
        if unit == "mole/hr":
            return self.flow_rate
        elif unit == "kg/hr":
            return self.flow_rate * self.get_molar_mass()
        else:
            raise ValueError("No UNIT FOUND for Flow Rate")

    def get_component_flow_rate(self, component, unit):
        index = self.components.index(component)
        if unit == "mole/hr":
            return self.flow_rate * self.fractions[index]
        elif unit == "kg/hr":
            return (
                self.get_component_flow_rate(component, "mole/hr")
                * self.reading_properties["M"][index]
                / 1000
            )
        else:
            raise ValueError("No UNIT FOUND for Flow Rate")

    def get_component_fraction(self, component):
        index = self.components.index(component)
        return self.fractions[index]

    def get_phase_flow_rate(self, unit):
        flow_rate = 0
        for component in self.components:
            flow_rate = flow_rate + self.get_component_flow_rate(component, "kg/hr")
        return flow_rate

    def get_acid_wt_prc(self, name):
        acid = self.get_component_flow_rate(name, "kg/hr")
        phase_rate = self.get_phase_flow_rate("kg/hr")
        return 100 * acid / phase_rate

    def normalize(self):
        faktor = 1 / sum(self.fractions)
        for i in range(len(self.fractions)):
            self.fractions[i] = self.fractions[i] * faktor

    def set_name(self):
        if self.get_component_fraction("H2O") > 0.999:
            self.name = "AQUEOUS"
        else:
            self.name = "ACIDIC"

    def set_component_fraction(self, component, fraction):
        """Set the fraction of a specific component in the phase."""
        if component in self.components:
            index = self.components.index(component)
            self.fractions[index] = fraction
        else:
            raise ValueError(f"Component {component} not found in phase.")


class Fluid:

    def __init__(self):
        # Initialize database when Fluid instance is created
        _initialize_database()

        self.phases = []
        self.components = []
        self.fractions = []
        self.molecular_weight: List[float] = []
        self.critical_temperature: List[float] = []
        self.critical_pressure: List[float] = []
        self.accentric_factor: List[float] = []
        self.volume_correction: List[float] = []
        self.reduced_temperature = []
        self.reduced_pressure = []
        self.K_values = []
        self.m: List[float] = []
        self.flow_rate = 1
        self.use_volume_correction = False
        self.AntoineParameterA: List[float] = []
        self.AntoineParameterB: List[float] = []
        self.AntoineParameterC: List[float] = []
        self.AntoineParameterUnit: List[str] = []
        self.ActivityK1: List[float] = []
        self.ActivityK2: List[float] = []
        self.ActivityK3: List[float] = []

        self.tol = 1e-10

        self.betta = np.nan
        self.m = []
        self.alpha = []
        self.a = []
        self.b = []
        self.A = []
        self.B = []

        self.gas_phase = Phase()
        self.liquid_phase = Phase()

        self.phases.append(self.gas_phase)
        self.phases.append(self.liquid_phase)

        self.reading_properties = {
            "M": self.molecular_weight,
            "Tc": self.critical_temperature,
            "Pc": self.critical_pressure,
            "w": self.accentric_factor,
            "s": self.volume_correction,
            "A": self.AntoineParameterA,
            "B": self.AntoineParameterB,
            "C": self.AntoineParameterC,
            "UnitAnt": self.AntoineParameterUnit,
            "ActivityK1": self.ActivityK1,
            "ActivityK2": self.ActivityK2,
            "ActivityK3": self.ActivityK3,
        }
        for i in range(len(self.phases)):
            self.get_phase(i).set_properties(self.reading_properties)

        self.temperature = 273.15
        self.pressure = 1.01325

        self.factor_up = 1.1
        self.factor_down = 0.9

        # Load properties database with relative path and error handling
        try:
            properties_path = get_database_path("Properties.csv")
            self.properties = pd.read_csv(
                properties_path, sep=";", index_col="Component"
            )
        except FileNotFoundError as e:
            raise RuntimeError(f"Failed to load Properties database: {str(e)}") from e

    def set_temperature(self, temperature):
        self.temperature = temperature
        for i in range(len(self.phases)):
            self.get_phase(i).set_temperature(temperature)

    def set_pressure(self, pressure):
        self.pressure = pressure
        for i in range(len(self.phases)):
            self.get_phase(i).set_pressure(pressure)

    def get_molar_mass(self):
        self.MW = 0
        for i, component in enumerate(self.components):
            self.MW += self.reading_properties["M"][i] * self.fractions[i] / 1000
        return self.MW

    def set_flow_rate(self, flow_rate, unit):
        self.normalize()
        if unit == "mole/hr":
            self.flow_rate = flow_rate
        elif unit == "kg/hr":
            self.flow_rate = flow_rate / self.get_molar_mass()
        else:
            self.flow_rate = np.nan
            raise ValueError("No UNIT FOUND for Flow Rate")

    def get_flow_rate(self, unit):
        if unit == "mole/hr":
            return self.flow_rate
        elif unit == "kg/hr":
            return self.flow_rate * self.get_molar_mass()
        else:
            raise ValueError("No UNIT FOUND for Flow Rate")

    def read_property(self, component):
        for column_name, prop_list in self.reading_properties.items():
            if component in self.properties.index:
                try:
                    value = self.properties.loc[component, column_name]
                    # Handle both string and numeric values
                    if isinstance(value, str):
                        prop_list.append(float(value.replace(",", ".")))
                    else:
                        prop_list.append(float(value))
                except (KeyError, IndexError, ValueError, TypeError):
                    prop_list.append(self.properties.loc[component, column_name])
            else:
                raise ValueError(
                    f"Properties for component {component} not found in the database."
                )

    def add_component(self, component, fraction):
        self.components.append(component)
        self.fractions.append(fraction)
        self.read_property(component)

    def calc_Rachford_Rice(self, betta):
        f = 0
        for k in range(len(self.K_values)):
            if self.K_values[k] > 1e50:
                self.K_values[k] = 1e50
            elif self.K_values[k] < 1e-50:
                self.K_values[k] = 1e-50

        for i, component in enumerate(self.components):
            f += (
                self.fractions[i]
                * (self.K_values[i] - 1)
                / (1 - betta + betta * self.K_values[i])
            )
        return f

    def solve_Rachford_Rice(self):
        val_0 = self.calc_Rachford_Rice(0)
        val_1 = self.calc_Rachford_Rice(1)
        if val_0 * val_1 > 0:
            if abs(val_0) < abs(val_1):
                self.betta = 0
            else:
                self.betta = 1
        else:
            self.betta = bisect(self.calc_Rachford_Rice, 0, 1)
            self.calc_Rachford_Rice(self.betta)
            if self.betta > 1:
                self.betta = 1.0
            if self.betta < 0:
                self.betta = 0.0
        return self.betta

    def plot_Rachford_Rice(self):
        # Define a range of beta values
        betta_values = np.linspace(0, 1, 50)

        # Calculate corresponding values of the Rachford-Rice function
        f_values = [self.calc_Rachford_Rice(b) for b in betta_values]
        print(f_values)

        # Plot the Rachford-Rice function
        plt.plot(betta_values, f_values)
        plt.xlabel("Beta")
        plt.ylabel("Rachford-Rice function")
        plt.title("Rachford-Rice function vs. Beta")
        plt.grid(True)
        plt.show()

    def calc_phases(self):
        yi = []
        xi = []
        for i, component in enumerate(self.components):
            yi.append(
                self.K_values[i]
                * self.fractions[i]
                / (1 - self.betta + self.betta * self.K_values[i])
            )
            xi.append(
                self.fractions[i] / (1 - self.betta + self.betta * self.K_values[i])
            )
        self.get_phase(0).set_phase(self.components, yi, self.betta, "gas")
        self.get_phase(1).set_phase(self.components, xi, 1 - self.betta, "liquid")

    def normalize(self):
        faktor = 1 / sum(self.fractions)
        for i in range(len(self.fractions)):
            self.fractions[i] = self.fractions[i] * faktor

    def update_k_values_activity(self):

        for i, component in enumerate(self.components):
            faktor = self.activity[i] / self.fugacity[i]
            faktor = max(min(faktor, self.factor_up), self.factor_down)
            self.K_values[i] = self.K_values[i] * faktor
            # Check if the value is infinite and set it to 1e50 if true
            if math.isinf(self.K_values[i]):
                self.K_values[i] = 1e50

    def calc_vapour_pressure(self):
        self.vapour_pressure = []
        for i in range(len(self.fractions)):
            vapour_pressure = 10 ** (
                self.AntoineParameterA[i]
                - self.AntoineParameterB[i]
                / (self.AntoineParameterC[i] + self.temperature - 273.15)
            )
            if self.AntoineParameterUnit[i] == "mmhg":
                vapour_pressure = vapour_pressure * 0.00133322
            self.vapour_pressure.append(vapour_pressure)

    def calc_activity(self):
        self.activity = []
        self.activity_coefficient = []

        if len(self.components) == 1:
            activity = self.get_phase(1).fractions[0] * self.vapour_pressure[0]
            self.activity_coefficient.append(1)
            self.activity.append(activity)
            return

        if "H2O" not in self.components or (
            ("HNO3" not in self.components) and ("H2SO4" not in self.components)
        ):
            for i, component in enumerate(self.components):
                activity = self.get_phase(1).fractions[i] * self.vapour_pressure[i]
                if component == "CO2":
                    activity = 1e50
                self.activity_coefficient.append(1)
                self.activity.append(activity)
            return
        for i, component in enumerate(self.components):
            if component == "H2O":
                activity = 0
                if "HNO3" in self.components:
                    activity += np.exp(
                        (0.06 * (self.temperature - 273.15) - 13.3637)
                        * (self.get_phase(1).get_fraction_component("HNO3")) ** 2
                    )
                if "H2SO4" in self.components:
                    activity += calc_activity_water_h2so4(
                        self.temperature,
                        self.get_phase(1).get_fraction_component("H2O"),
                    )
            elif component == "HNO3":
                activity = np.exp(
                    (
                        self.ActivityK1[i] * (self.temperature - 273.15)
                        - self.ActivityK2[i]
                    )
                    * (self.get_phase(1).get_fraction_component("H2O")) ** 2
                )
            elif component == "H2SO4":
                activity = np.exp(
                    (
                        self.ActivityK1[i] * ((self.temperature - 273.15) ** 2)
                        + self.ActivityK2[i] * (self.temperature - 273.15)
                        + self.ActivityK3[i]
                    )
                    * (self.get_phase(1).get_fraction_component("H2O")) ** 2
                )
            else:
                activity = 1e50
            self.activity.append(activity)

        for i, component in enumerate(self.components):
            self.activity_coefficient.append(self.activity[i])
            self.activity[i] = (
                self.activity[i]
                * self.get_phase(1).fractions[i]
                * self.vapour_pressure[i]
            )

    def calc_fugacicy_coefficient_neqsim_CPA(self):
        self.fug_coeff = []
        for i, component in enumerate(self.components):
            if component == "H2O":
                fug_c = get_water_fugacity_coefficient(
                    self.pressure, self.temperature - 273.15
                )[1]
            elif component == "HNO3" or component == "H2SO4":
                fug_c = get_acid_fugacity_coeff(
                    component, self.pressure, self.temperature - 273.15
                )[0]
            elif component == "CO2":
                fug_c = 1.0
            self.fug_coeff.append(fug_c)

    def calc_fugacity_neqsim_CPA(self, fractions):
        self.fugacity = []
        for i, component in enumerate(self.components):
            self.fugacity.append(self.fug_coeff[i] * self.pressure * fractions[i])

    def get_component_fraction(self, component):
        """Get the fraction of a specific component in the fluid."""
        if component in self.components:
            index = self.components.index(component)
            return self.fractions[index]
        else:
            raise ValueError(f"Component {component} not found in fluid.")

    def set_component_fraction(self, component, fraction):
        """Set the fraction of a specific component in the fluid."""
        if component in self.components:
            index = self.components.index(component)
            self.fractions[index] = fraction
        else:
            raise ValueError(f"Component {component} not found in fluid.")

    def validate_composition(self):
        if "H2O" not in self.components:
            self.add_component("H2O", 1e-30)

        if self.get_component_fraction("H2O") < 1e-30:
            self.set_component_fraction("H2O", 1e-30)

        if "H2SO4" not in self.components and "HNO3" not in self.components:
            self.add_component("HNO3", 1e-30)

        if "H2SO4" in self.components and self.get_component_fraction("H2SO4") < 1e-30:
            self.set_component_fraction("H2SO4", 1e-30)

        if "HNO3" in self.components and self.get_component_fraction("HNO3") < 1e-30:
            self.set_component_fraction("HNO3", 1e-30)

    def flash_activity(self):
        self.validate_composition()
        self.calc_vapour_pressure()
        self.normalize()
        self.K_values = [1e50, 0.005, 0.005]
        self.calc_fugacicy_coefficient_neqsim_CPA()
        self.iteration = 0
        while 1:
            K_old = self.K_values.copy()
            bettaOld = self.betta
            self.solve_Rachford_Rice()
            bettaNew = self.betta
            abs(bettaOld - bettaNew)  # Check convergence
            self.calc_phases()
            for i in range(len(self.phases)):
                self.phases[i].set_phase_flow_rate(self.flow_rate)
            self.get_phase(1).set_component_fraction("CO2", 1e-50)
            self.get_phase(1).normalize()
            self.calc_fugacity_neqsim_CPA(self.phases[0].fractions)
            self.calc_activity()
            self.update_k_values_activity()
            K_new = self.K_values.copy()
            self.iteration += 1
            self.error = 0

            for i, component in enumerate(self.components):
                self.error += abs(K_new[i] - K_old[i])

            if self.iteration > 30000:
                self.factor_up = 1.0001
                self.factor_down = 0.999

            if self.iteration > 40000:
                self.K_values[:] = [
                    (k_old + k_new) / 2 for k_old, k_new in zip(K_old, K_new)
                ]
                self.solve_Rachford_Rice()
                self.calc_phases()
                self.get_phase(1).set_component_fraction("CO2", 1e-50)
                self.get_phase(1).normalize()
                self.calc_fugacity_neqsim_CPA(self.phases[0].fractions)
                self.calc_activity()
                self.phases[1].set_phase_flow_rate(self.flow_rate)

                break

            if self.error < self.tol:
                break

        self.phases[1].set_name()

    def get_phase(self, i):
        return self.phases[i]

    def init(self):
        # self.validate_composition()
        self.calc_vapour_pressure()
        # self.normalize()
        self.K_values = [1e50, 0.005, 0.005]
        self.calc_fugacicy_coefficient_neqsim_CPA()
        self.calc_activity()

    def get_component_activity(self, component):
        if component in self.components:
            index = self.components.index(component)
            return self.activity[index]
        else:
            raise ValueError(f"Component {component} not found in fluid.")

    def get_acid_solubility(self, acid, concentration):

        self.add_component("CO2", 1)
        self.add_component("H2O", 1)
        self.add_component(acid, 1)

        components = ["CO2", "H2O", acid]
        yi = [1, 300 * 1e-6, 10 * 1e-6]
        xi = [0, 1 - concentration, concentration]
        self.components = components
        self.get_phase(0).set_phase(components, yi, 0.5, "gas")
        self.get_phase(1).set_phase(components, xi, 0.5, "liquid")
        self.calc_vapour_pressure()
        self.calc_fugacicy_coefficient_neqsim_CPA()
        self.init()
        solubility_ppm = (
            1e6
            * self.get_component_activity(acid)
            / (self.fug_coeff[self.components.index(acid)] * self.pressure)
        )

        return solubility_ppm


class ModelResults:
    """Class to format and display modeling results as a clean table string."""

    def __init__(self, fluid, co2_properties=None):
        """Initialize with fluid object and optional CO2 properties.

        Parameters
        ----------
        fluid : Fluid
            The fluid object after flash calculations
        co2_properties : dict, optional
            Dictionary with CO2 properties from get_co2_parameters
        """
        self.fluid = fluid
        self.co2_properties = co2_properties or {}

    def generate_table(self, include_co2_props=True, include_liquid_details=True):
        """Generate a beautifully formatted table string with results.

        Parameters
        ----------
        include_co2_props : bool, default True
            Include pure CO2 properties in the table
        include_liquid_details : bool, default True
            Include detailed liquid phase information if present

        Returns
        -------
        str
            Formatted table string
        """
        lines = []

        # Header with decorative border
        lines.append("═" * 65)
        lines.append("                 SOLUBILITY CCS ANALYSIS RESULTS")
        lines.append("═" * 65)

        # Get acid component name
        acid_components = [
            comp
            for comp in ["H2SO4", "HNO3"]
            if any(comp in str(c) for c in self.fluid.components)
        ]
        acid = acid_components[0] if acid_components else "Unknown"

        # System Overview Section
        lines.append("")
        lines.append("📋 SYSTEM OVERVIEW")
        lines.append("─" * 35)
        lines.append(f"Temperature:          {self.fluid.temperature - 273.15:.2f} °C")
        lines.append(f"Pressure:             {self.fluid.pressure:.2f} bara")

        # Phase Behavior Assessment
        lines.append("")
        lines.append("⚗️  PHASE BEHAVIOR ASSESSMENT")
        lines.append("─" * 35)

        if self.fluid.betta < 1.0:
            lines.append("🚨 STATUS: ACID FORMATION RISK DETECTED!")
            lines.append("⚠️  RISK LEVEL: Two-phase system present")
        else:
            lines.append("✅ STATUS: Single gas phase - No acid formation risk")
            lines.append("🟢 RISK LEVEL: Safe operation")

        # Gas Phase Composition (or Liquid CO2 if high density)
        lines.append("")

        # Check CO2 density to determine if it's liquid CO2
        co2_density = (
            self.co2_properties.get("density", 0) if self.co2_properties else 0
        )
        if isinstance(co2_density, (int, float)) and co2_density > 300:
            lines.append("LIQUID CO2 PHASE COMPOSITION")
        else:
            lines.append("GAS PHASE COMPOSITION")
        lines.append("─" * 35)

        if len(self.fluid.phases) > 0:
            h2o_ppm = 1e6 * self.fluid.phases[0].get_component_fraction("H2O")
            acid_ppm = 1e6 * self.fluid.phases[0].get_component_fraction(acid)

            lines.append(f"Water in CO₂:         {h2o_ppm:.2f} ppm (mol)")
            lines.append(f"{acid} in CO₂:        {acid_ppm:.2f} ppm (mol)")

        # Liquid Phase Details (if present)
        if (
            self.fluid.betta < 1.0
            and len(self.fluid.phases) > 1
            and include_liquid_details
        ):
            lines.append("")
            lines.append("LIQUID PHASE DETAILS")
            lines.append("─" * 35)

            liquid_phase = self.fluid.phases[1]
            lines.append(f"Phase Type:           {liquid_phase.name}")
            lines.append(
                f"Acid Concentration:   {liquid_phase.get_acid_wt_prc(acid):.2f} wt%"
            )

            # Flow rate calculations (if available)
            try:
                flow_rate_ty = liquid_phase.get_flow_rate("kg/hr") * 24 * 365 / 1000
                lines.append(f"Liquid Flow Rate:     {flow_rate_ty:.2f} t/year")
            except (ValueError, AttributeError):
                lines.append("Liquid Flow Rate:     Not available")

            h2o_mol_frac = liquid_phase.get_component_fraction("H2O")
            acid_mol_frac = liquid_phase.get_component_fraction(acid)

            lines.append(f"Water Mol Fraction: {h2o_mol_frac:.2f}")
            lines.append(f"{acid} Mol Fraction: {acid_mol_frac:.2f}")

        # Pure CO2 Properties
        if include_co2_props and self.co2_properties:
            lines.append("")
            lines.append("PURE CO₂ PROPERTIES")
            lines.append("─" * 35)

            density = self.co2_properties.get("density", "N/A")
            speed_of_sound = self.co2_properties.get("speed_of_sound", "N/A")
            enthalpy = self.co2_properties.get("enthalpy", "N/A")
            entropy = self.co2_properties.get("entropy", "N/A")

            # Format density
            if isinstance(density, (int, float)):
                lines.append(f"Density:              {density:.2f} kg/m³")
            else:
                lines.append(f"Density:              {density} kg/m³")

            # Format speed of sound
            if isinstance(speed_of_sound, (int, float)):
                lines.append(f"Speed of Sound:       {speed_of_sound:.2f} m/s")
            else:
                lines.append(f"Speed of Sound:       {speed_of_sound} m/s")

            # Format enthalpy
            if isinstance(enthalpy, (int, float)):
                lines.append(f"Enthalpy:             {enthalpy:.2f} kJ/kg")
            else:
                lines.append(f"Enthalpy:             {enthalpy} kJ/kg")

            # Format entropy
            if isinstance(entropy, (int, float)):
                lines.append(f"Entropy:              {entropy:.2f} J/K")
            else:
                lines.append(f"Entropy:              {entropy} J/K")

        # Footer
        lines.append("")
        lines.append("═" * 65)
        lines.append("              📊 Analysis Complete | SolubilityCCS")
        lines.append("═" * 65)

        return "\n".join(lines)

    def to_dict(self):
        """Return results as a dictionary for programmatic access.

        Returns
        -------
        dict
            Dictionary containing all modeling results
        """
        # Get acid component name
        acid_components = [
            comp
            for comp in ["H2SO4", "HNO3"]
            if any(comp in str(c) for c in self.fluid.components)
        ]
        acid = acid_components[0] if acid_components else "Unknown"

        results = {
            "system": {
                "acid_type": acid,
                "temperature_C": self.fluid.temperature - 273.15,
                "pressure_bara": self.fluid.pressure,
                "number_of_phases": len(self.fluid.phases),
                "gas_phase_fraction": self.fluid.betta,
                "acid_formation_risk": self.fluid.betta < 1.0,
            }
        }

        # Gas phase composition
        if len(self.fluid.phases) > 0:
            results["gas_phase"] = {
                "water_ppm_mol": 1e6
                * self.fluid.phases[0].get_component_fraction("H2O"),
                "acid_ppm_mol": 1e6 * self.fluid.phases[0].get_component_fraction(acid),
            }

        # Liquid phase (if present)
        if self.fluid.betta < 1.0 and len(self.fluid.phases) > 1:
            liquid_phase = self.fluid.phases[1]
            results["liquid_phase"] = {
                "phase_type": liquid_phase.name,
                "acid_concentration_wt_pct": liquid_phase.get_acid_wt_prc(acid),
                "water_mol_fraction": liquid_phase.get_component_fraction("H2O"),
                "acid_mol_fraction": liquid_phase.get_component_fraction(acid),
            }

            try:
                results["liquid_phase"]["flow_rate_t_per_year"] = (
                    liquid_phase.get_flow_rate("kg/hr") * 24 * 365 / 1000
                )
            except (ValueError, AttributeError):
                results["liquid_phase"]["flow_rate_t_per_year"] = None

        # CO2 properties
        if self.co2_properties:
            results["co2_properties"] = self.co2_properties.copy()

        return results

    def __str__(self):
        """Return the formatted table string."""
        return self.generate_table()

    def __repr__(self):
        """Return a representation of the ModelResults object."""
        return (
            f"ModelResults(phases={len(self.fluid.phases)}, "
            f"betta={self.fluid.betta:.4f})"
        )
