"""
Acid Formation Analysis Script for CO2 Systems with Acids.

This script analyzes the acid formation potential of CO2 systems containing acids
(H2SO4 or HNO3) and water by calculating phase behavior and liquid phase
formation.
"""

from solubilityccs import Fluid
from solubilityccs.neqsim_functions import get_co2_parameters


def analyze_acid_formation_potential(
    acid="H2SO4",
    acid_in_co2=10,
    water_in_co2=10.0,
    temperature=2,
    pressure=60,
    flow_rate=100,
):
    """
    Analyze acid formation potential of CO2 system with acid and water.

    Args:
        acid (str): Type of acid - "H2SO4" or "HNO3"
        acid_in_co2 (float): Acid concentration in CO2 (ppm)
        water_in_co2 (float): Water concentration in CO2 (ppm)
        temperature (float): Temperature (°C)
        pressure (float): Pressure (bara)
        flow_rate (float): Flow rate (Mt/year)

    Returns
    -------
    dict
        Analysis results
    """
    # Create and configure fluid
    fluid = Fluid()
    fluid.add_component("CO2", 1.0 - acid_in_co2 / 1e6 - water_in_co2 / 1e6)  # mole
    fluid.add_component(acid, acid_in_co2 / 1e6)  # mole
    fluid.add_component("H2O", water_in_co2 / 1e6)  # mole
    fluid.set_temperature(temperature + 273.15)  # to Kelvin
    fluid.set_pressure(pressure)  # bara
    fluid.set_flow_rate(flow_rate * 1e6 * 1000 / (365 * 24), "kg/hr")

    # Perform calculations
    fluid.calc_vapour_pressure()
    fluid.flash_activity()

    # Collect results
    results = {
        "gas_phase_fraction": fluid.betta,
        "acid_formation_risk": "HIGH" if fluid.betta < 1 else "LOW",
        "water_in_co2_ppm": 1e6 * fluid.phases[0].get_component_fraction("H2O"),
        "acid_in_co2_ppm": 1e6 * fluid.phases[0].get_component_fraction(acid),
    }

    # If liquid phase forms
    if fluid.betta < 1:
        results.update(
            {
                "liquid_phase_name": fluid.phases[1].name,
                "liquid_acid_wt_pct": fluid.phases[1].get_acid_wt_prc(acid),
                "liquid_flow_rate_ty": fluid.phases[1].get_flow_rate("kg/hr")
                * 24
                * 365
                / 1000,
                "water_in_liquid_mol_frac": fluid.phases[1].get_component_fraction(
                    "H2O"
                ),
                "acid_in_liquid_mol_frac": fluid.phases[1].get_component_fraction(acid),
            }
        )

    # Get CO2 properties
    co2_results = get_co2_parameters(pressure, temperature)
    results.update(
        {
            "co2_density": co2_results["density"],
            "co2_speed_of_sound": co2_results["speed_of_sound"],
            "co2_enthalpy": co2_results["enthalpy"],
            "co2_entropy": co2_results["entropy"],
        }
    )

    return results


def print_analysis_results(results, acid):
    """Print formatted analysis results."""
    print(
        f"Mole fraction of gas phase to total phase "
        f"{results['gas_phase_fraction']:.16f} mol/mol"
    )
    print(f"Acid Formation Risk: {results['acid_formation_risk']}")
    print(f"Water in CO2 {results['water_in_co2_ppm']:.12f} ppm mol")
    print(f"{acid} in CO2 {results['acid_in_co2_ppm']:.12e} ppm mol")

    if "liquid_phase_name" in results:
        print(f"Second phase is {results['liquid_phase_name']}")
        print(f"Liquid phase formed {results['liquid_acid_wt_pct']:.14f} wt %")
        print(f"Liquid flow rate {results['liquid_flow_rate_ty']:.13f} t/y")
        print(
            f"Water in liquid phase "
            f"{results['water_in_liquid_mol_frac']:.17f} mol fraction"
        )
        print(
            f"{acid} in liquid phase "
            f"{results['acid_in_liquid_mol_frac']:.16f} mol fraction"
        )

    print("\nAdditional information for pure CO2 at these conditions:")
    print(f"Pure CO2 density {results['co2_density']} kg/m3")
    print(f"Pure CO2 speed of sound: {results['co2_speed_of_sound']} m/s")
    print(f"Pure CO2 enthalpy: {results['co2_enthalpy']} kJ/kg")
    print(f"Pure CO2 entropy: {results['co2_entropy']} J/K")


def main():
    """Run main analysis function."""
    # Analysis parameters
    acid = "H2SO4"  # HNO3 or H2SO4
    acid_in_co2 = 10  # ppm
    water_in_co2 = 10.0  # ppm
    temperature = 2  # C
    pressure = 60  # bara
    flow_rate = 100  # Mt/year

    try:
        # Perform analysis
        results = analyze_acid_formation_potential(
            acid=acid,
            acid_in_co2=acid_in_co2,
            water_in_co2=water_in_co2,
            temperature=temperature,
            pressure=pressure,
            flow_rate=flow_rate,
        )

        # Print results
        print_analysis_results(results, acid)

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main()
