import sys

import pandas as pd


def main():
    """Read and process Excel file data."""
    try:
        print("Reading Excel file...")
        df = pd.read_excel("Database/solubilityExperimentalData.xlsx")
        print(f"Successfully read Excel file with shape: {df.shape}")

        # The first row contains the actual headers, so let's use it
        # Skip the first row as it contains headers
        df_data = df.iloc[1:].copy()

        # Set proper column names based on first row
        column_names = [
            "N",
            "Pressure",
            "Temperature",
            "H2O_ppm",
            "H2SO4_ppm",
            "HNO3_ppm",
            "betta",
            "Liq_H2O",
            "Liq_H2SO4",
            "Liq_HNO3",
            "Gas_H2O",
            "Gas_H2SO4",
            "Gas_HNO3",
            "Comment",
        ]
        df_data.columns = column_names

        print("\nProper column names:")
        for i, col in enumerate(df_data.columns):
            print(f"{i+1}: {col}")

        print("\nFirst 5 data rows:")
        print(df_data.head().to_string())

        print("\nData types after cleaning:")
        print(df_data.dtypes)

        # Check for numeric columns
        numeric_cols = [
            "N",
            "Pressure",
            "Temperature",
            "H2O_ppm",
            "H2SO4_ppm",
            "HNO3_ppm",
            "Liq_H2O",
            "Liq_H2SO4",
            "Liq_HNO3",
            "Gas_H2O",
            "Gas_H2SO4",
            "Gas_HNO3",
        ]

        for col in numeric_cols:
            if col in df_data.columns:
                df_data[col] = pd.to_numeric(df_data[col], errors="coerce")

        print("\nConverted numeric data:")
        print(df_data[numeric_cols].head())

        # Check non-null values
        print("\nNon-null counts:")
        print(df_data.count())

        return df_data

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
