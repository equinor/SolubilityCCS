from neqsim import jNeqSim
jNeqSim.util.database.NeqSimDataBase.replaceTable('COMP', "/workspaces/SolubilityCCS/Database/COMP.csv") ##

def get_component_list(fluid):
    """
    This function takes a fluid neqsim object as input and returns a list of components in the fluid.

    Args:
    - fluid: a neqsim fluid object

    Returns:
    - components_list: a list of names of components in the fluid
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
        fugacity.append(get_gas_fug_coef(fluid1)[i]*fluid1.getPressure("bara")*fluid1.getPhase(0).getComponent(component).getx())
    return fugacity

def get_acid_fugacity_coeff(acid, pressure, temperature):    

    fluid1 = jNeqSim.thermo.system.SystemSrkCPAstatoil(298.15, 1.01325) ## CPA model
    fluid1.setTemperature(temperature, 'C')
    fluid1.setPressure(pressure, 'bara')
    fluid1.addComponent(acid, 1.0)
    fluid1.addComponent('water', 0.1)
    fluid1.addComponent('CO2', 1.0)
    fluid1.setMixingRule(9)
    fluid1.setMultiPhaseCheck(True)

    components_list = get_component_list(fluid1)
    test_ops = jNeqSim.thermodynamicOperations.ThermodynamicOperations(fluid1)
    test_ops.TPflash()

    if acid=="HNO3":    
        value = 0.37 #HNO3
    else:
        value = 0.08 - 0.27315*((temperature + 273.15)/273.15 - 1.0)

    (fluid1.getPhases()[0]).getMixingRule().setBinaryInteractionParameter(
                components_list.index(acid), components_list.index("CO2"), value)

    (fluid1.getPhases()[1]).getMixingRule().setBinaryInteractionParameter(
                components_list.index(acid), components_list.index("CO2"), value)

    test_ops.TPflash()

    return (get_gas_fug_coef(fluid1))

def get_water_fugacity_coefficient(pressure, temperature):

    temperature = temperature + 273.15
    fluid1 = jNeqSim.thermo.system.SystemSrkCPAstatoil(298.15, 1.01325) ## CPA model
    fluid1.setTemperature(temperature, 'K')
    fluid1.setPressure(pressure, 'bara')
    fluid1.addComponent('CO2', 110.0)
    fluid1.addComponent('water', 100.0)
    fluid1.setMixingRule(9)
    fluid1.setMultiPhaseCheck(True)

    components_list = get_component_list(fluid1)
    test_ops = jNeqSim.thermodynamicOperations.ThermodynamicOperations(fluid1)
    test_ops.TPflash()

    value = -0.28985
    valueT = -0.273

    val = value + valueT*(temperature/273.15 - 1.0)

    (fluid1.getPhases()[0]).getMixingRule().setBinaryInteractionParameter(
                components_list.index("water"), components_list.index("CO2"), val)


    test_ops.TPflash()

    return (get_gas_fug_coef(fluid1))
