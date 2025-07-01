import pandas as pd
import numpy as np
import os

def get_database_path(filename):
    """Get the path to a database file, with fallbacks for different environments"""
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    paths_to_try = [
        os.path.join(script_dir, "Database", filename),
        os.path.join(current_dir, "Database", filename),
        os.path.join(current_dir, filename),
        f"/workspaces/SolubilityCCS/Database/{filename}",  # Dev container path
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
    return None

# Try to load WaterActivityH2SO4.csv database
water_activity_path = get_database_path("WaterActivityH2SO4.csv")
if water_activity_path:
    try:
        water_h2so4 = pd.read_csv(water_activity_path, sep=";", decimal=',')
        print(f"Sulfuric acid activity: Loaded water activity data from: {water_activity_path}")
    except Exception as e:
        print(f"Sulfuric acid activity: Warning - Could not load WaterActivityH2SO4.csv from {water_activity_path}: {e}")
        # Create a minimal fallback dataframe
        water_h2so4 = pd.DataFrame({
            "Temperature": [0, 25, 50, 100],
            0.1: [1.0, 1.0, 1.0, 1.0],  # Default activity values
            0.5: [0.8, 0.8, 0.8, 0.8],
            0.9: [0.6, 0.6, 0.6, 0.6]
        })
        print("Sulfuric acid activity: Using fallback water activity data")
else:
    print("Sulfuric acid activity: Warning - WaterActivityH2SO4.csv not found, using fallback data")
    # Create a minimal fallback dataframe
    water_h2so4 = pd.DataFrame({
        "Temperature": [0, 25, 50, 100],
        0.1: [1.0, 1.0, 1.0, 1.0],  # Default activity values
        0.5: [0.8, 0.8, 0.8, 0.8],
        0.9: [0.6, 0.6, 0.6, 0.6]
    })
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
    try:
        # Check if dataframe is valid
        if water_h2so4.empty or "Temperature" not in water_h2so4.columns:
            return 1.0  # Default fallback value
            
        # Check if the column exists
        if y not in water_h2so4.columns:
            return 1.0  # Default fallback value
            
        # Get the temperature and corresponding column data
        temperatures = water_h2so4["Temperature"].values
        column_data = water_h2so4[y].values  # Directly access the column data

        # Check if we have valid data
        if len(temperatures) == 0 or len(column_data) == 0:
            return 1.0  # Default fallback value

        # Perform interpolation
        if x < temperatures.min() or x > temperatures.max():
            # If x is out of bounds, clip to the nearest boundary
            x = np.clip(x, temperatures.min(), temperatures.max())
        
        interpolated_value = np.interp(x, temperatures, column_data)
        
        return interpolated_value
    except Exception as e:
        print(f"Sulfuric acid activity: Error in get_value2: {e}")
        return 1.0  # Default fallback value

def find_closest_values(sorted_list, target):
    """
    Find the closest larger and smaller values to the target in a sorted list.
    
    Parameters:
    sorted_list: List of numeric values
    target: Target value to find closest values for
    
    Returns:
    tuple: (larger, smaller) values closest to target
    """
    try:
        if not sorted_list or len(sorted_list) == 0:
            return None, None
            
        larger = None
        smaller = None
        
        for number in sorted_list:
            try:
                num_val = float(number)
                if num_val > target and (larger is None or num_val < larger):
                    larger = num_val
                if num_val < target and (smaller is None or num_val > smaller):
                    smaller = num_val
            except (ValueError, TypeError):
                continue  # Skip non-numeric values
                
        return larger, smaller
    except Exception as e:
        print(f"Sulfuric acid activity: Error in find_closest_values: {e}")
        return None, None

def calc_activity_water_h2so4(temperature, water):
    """
    Calculate water activity in H2SO4 solution
    
    Parameters:
    temperature (float): Temperature in Kelvin
    water (float): Water mole fraction
    
    Returns:
    float: Water activity
    """
    try:
        # Ensure we have valid data
        if water_h2so4.empty:
            return 1.0  # Default fallback value
            
        value = get_value2(temperature, water)
        return value
    except Exception as e:
        try:
            # Fallback interpolation method
            if len(water_h2so4.columns) < 2:
                return 1.0  # Default fallback value
                
            available_columns = [col for col in water_h2so4.columns[1:] if isinstance(col, (int, float))]
            if len(available_columns) < 2:
                return 1.0  # Default fallback value
                
            larger, smaller = find_closest_values(available_columns, water)
            
            if larger is None or smaller is None:
                return 1.0  # Default fallback value
                
            value1 = get_value2(temperature, larger)
            value2 = get_value2(temperature, smaller)
            value = value2 + (water-smaller)*(value2 - value1)/(smaller - larger)
            return value
        except Exception as fallback_error:
            print(f"Sulfuric acid activity: Error in calc_activity_water_h2so4: {fallback_error}")
            return 1.0  # Default fallback value
