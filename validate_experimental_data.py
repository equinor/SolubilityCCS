#!/usr/bin/env python3
"""
Validation script for experimental data from solubilityExperimentalData.xlsx.

Reads composition data and validates simulation results against experimental data.
"""

import logging
import os

import pandas as pd

from solubilityccs import Fluid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_experimental_data():
    """Read the experimental data from Excel file."""
    file_path = "Database/solubilityExperimentalData.xlsx"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    # Read all sheets to understand the structure
    excel_file = pd.ExcelFile(file_path)
    logger.info("Available sheets: %s", excel_file.sheet_names)

    # Read the first sheet (assuming it contains the main data)
    df = pd.read_excel(file_path, sheet_name=0)

    logger.info("DataFrame shape: %s", df.shape)
    logger.info("Column names: %s", df.columns.tolist())

    logger.debug("First few rows: %s", df.head())

    logger.debug("DataFrame info:")
    df.info(buf=None)  # Log DataFrame info directly

    return df


def validate_composition(row):
    """
    Create a fluid with the composition from the row and run flash simulation.

    Validate results against experimental data.
    """
    try:
        # Extract composition data (adjust column names based on actual Excel structure)
        # This is a template - we'll adjust based on the actual columns

        # Create fluid
        fluid = Fluid()

        # Add components based on the Excel data structure
        # We'll implement this after seeing the actual column structure

        # Set conditions
        temperature = row.get("Temperature", 25)  # Default temperature
        pressure = row.get("Pressure", 1)  # Default pressure

        if pd.notna(temperature) and pd.notna(pressure):
            fluid.set_temperature(temperature + 273.15)  # Convert to Kelvin
            fluid.set_pressure(pressure)

            # Run flash calculations
            fluid.calc_vapour_pressure()
            fluid.flash_activity()

            # Validate results
            results = {}
            results["betta"] = fluid.betta
            results["phases"] = len(fluid.phases)

            # Compare with experimental data
            experimental_betta = row.get("betta", None)
            if pd.notna(experimental_betta):
                if experimental_betta < 1:
                    results["betta_validation"] = fluid.betta < 1
                else:
                    results["betta_validation"] = (
                        abs(fluid.betta - experimental_betta) / experimental_betta
                        <= 0.05
                    )

            return results

    except Exception as e:
        print(f"Error processing row: {e}")
        return None


if __name__ == "__main__":
    # Read experimental data
    df = read_experimental_data()
