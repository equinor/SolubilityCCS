from neqsim import jneqsim

# Import path utilities for robust file path handling
from .path_utils import get_database_path

# Set up database with relative path and error handling
try:
    comp_database_path = get_database_path("COMP.csv")
    jneqsim.util.database.NeqSimDataBase.replaceTable("COMP", comp_database_path)
except FileNotFoundError as e:
    raise RuntimeError(
        f"Failed to initialize COMP database in neqsim_functions: {str(e)}"
    ) from e


def get_component_list(fluid):
    """Get components from a neqsim fluid object.

    Parameters
    ----------
    fluid : neqsim fluid object
        A neqsim fluid object

    Returns
    -------
    list
        List of component names in the fluid
    """
    number_of_components = fluid.getNumberOfComponents()
    components_list = []
    for i in range(number_of_components):
        component = fluid.getComponent(i)
        name = component.getName()
        components_list.append(name)
    return components_list


def get_gas_fug_coef(fluid1):
    fug = []
    components_list = get_component_list(fluid1)
    for component in components_list:
        fug.append(fluid1.getPhase(0).getComponent(component).getFugacityCoefficient())
    return fug


def get_fugacity(fluid1):
    fugacity = []
    components_list = get_component_list(fluid1)
    i = -1
    for component in components_list:
        i += 1
        fugacity.append(
            get_gas_fug_coef(fluid1)[i]
            * fluid1.getPressure("bara")
            * fluid1.getPhase(0).getComponent(component).getx()
        )
    return fugacity


def get_acid_fugacity_coeff(acid, pressure, temperature):
    # CPA model
    fluid1 = jneqsim.thermo.system.SystemSrkCPAstatoil(298.15, 1.01325)
    fluid1.setTemperature(temperature, "C")
    fluid1.setPressure(pressure, "bara")
    fluid1.addComponent(acid, 1.0)
    fluid1.addComponent("water", 0.1)
    fluid1.addComponent("CO2", 1.0)
    fluid1.setMixingRule(9)
    fluid1.setMultiPhaseCheck(True)

    components_list = get_component_list(fluid1)
    test_ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid1)
    test_ops.TPflash()

    if acid == "HNO3":
        value = 0.37  # HNO3
    else:
        value = 0.08 - 0.27315 * ((temperature + 273.15) / 273.15 - 1.0)

    (fluid1.getPhases()[0]).getMixingRule().setBinaryInteractionParameter(
        components_list.index(acid), components_list.index("CO2"), value
    )

    (fluid1.getPhases()[1]).getMixingRule().setBinaryInteractionParameter(
        components_list.index(acid), components_list.index("CO2"), value
    )

    test_ops.TPflash()

    return get_gas_fug_coef(fluid1)


def get_water_fugacity_coefficient(pressure, temperature):
    temperature = temperature + 273.15
    # CPA model
    fluid1 = jneqsim.thermo.system.SystemSrkCPAstatoil(298.15, 1.01325)
    fluid1.setTemperature(temperature, "K")
    fluid1.setPressure(pressure, "bara")
    fluid1.addComponent("CO2", 110.0)
    fluid1.addComponent("water", 100.0)
    fluid1.setMixingRule(9)
    fluid1.setMultiPhaseCheck(True)

    components_list = get_component_list(fluid1)
    test_ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid1)
    test_ops.TPflash()

    value = -0.28985
    valueT = -0.273

    val = value + valueT * (temperature / 273.15 - 1.0)

    (fluid1.getPhases()[0]).getMixingRule().setBinaryInteractionParameter(
        components_list.index("water"), components_list.index("CO2"), val
    )

    test_ops.TPflash()

    return get_gas_fug_coef(fluid1)


def get_co2_parameters(pressure, temperature):
    temperature = temperature + 273.15
    # CPA model
    fluid1 = jneqsim.thermo.system.SystemSrkCPAstatoil(298.15, 1.01325)
    fluid1.setTemperature(temperature, "K")
    fluid1.setPressure(pressure, "bara")
    fluid1.addComponent("CO2", 1.0)
    fluid1.setMixingRule(9)
    fluid1.setMultiPhaseCheck(True)

    test_ops = jneqsim.thermodynamicoperations.ThermodynamicOperations(fluid1)
    test_ops.TPflash()

    fluid1.initPhysicalProperties()

    results = {
        "density": fluid1.getDensity("kg/m3"),
        "speed_of_sound": fluid1.getSoundSpeed("m/s"),
        "enthalpy": fluid1.getEnthalpy("kJ/kg"),
        "entropy": fluid1.getEntropy("J/K"),
    }

    return results
