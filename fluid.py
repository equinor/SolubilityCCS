import math
import warnings
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from neqsim import jNeqSim
from scipy.optimize import bisect

from neqsim_functions import get_acid_fugacity_coeff, get_water_fugacity_coefficient
from path_utils import get_database_path
from sulfuric_acid_activity import calc_activity_water_h2so4

# Suppress runtime warnings
warnings.filterwarnings("ignore")

# Set up database with relative path and error handling
try:
    comp_database_path = get_database_path("COMP.csv")
    jNeqSim.util.database.NeqSimDataBase.replaceTable("COMP", comp_database_path)
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


class Fluid:

    def __init__(self):
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

    def flash_activity(self):
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

            self.get_phase(1).fractions[0] = 1e-50
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
                self.get_phase(1).fractions[0] = 1e-50
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
