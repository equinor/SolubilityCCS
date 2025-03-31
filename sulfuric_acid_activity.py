import pandas as pd
import numpy as np

water_h2so4 = pd.read_csv("/workspaces/SolubilityCCS/Database/WaterActivityH2SO4.csv", sep = ";", decimal=',')
water_h2so4.columns = [float(col) if i != 0 else col for i, col in enumerate(water_h2so4.columns)]

def get_value2(x, y):
    """
    Retrieve the interpolated value from the DataFrame based on the specified temperature (x) 
    and column (y). If the temperature is out of bounds, it uses interpolation.
    
    Parameters:
    x (float): The temperature value to search for.
    y (float): The column name to retrieve the value from.
    
    Returns:
    float: The interpolated value from the DataFrame.
    """
    # Get the temperature and corresponding column data
    temperatures = water_h2so4["Temperature"].values
    column_data = water_h2so4[y].values  # Directly access the column data

    # Perform interpolation
    if x < temperatures.min() or x > temperatures.max():
        # If x is out of bounds, clip to the nearest boundary
        x = np.clip(x, temperatures.min(), temperatures.max())
    
    interpolated_value = np.interp(x, temperatures, column_data)
    
    return interpolated_value

def find_closest_values(sorted_list, target):
    larger = None
    smaller = None
    
    for number in sorted_list:
        if number > target and (larger is None or number < larger):
            larger = number
        if number < target and (smaller is None or number > smaller):
            smaller = number
            
    return larger, smaller

def calc_activity_water_h2so4(temperature, water):
    try:
        value  = get_value2(temperature, water)
        return value
    except:
        larger, smaller = find_closest_values(water_h2so4.columns[1:].astype(float), water)
        value1  = get_value2(temperature, larger)
        value2  = get_value2(temperature, smaller)
        value = value2 + (water-smaller)*(value2 - value1)/(smaller - larger)
        return value
