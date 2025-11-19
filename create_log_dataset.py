import numpy as np
import pandas as pd
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parent / "sample_demand_regression_data.csv"
OUTPUT_FILE = Path(__file__).resolve().parent / "sample_demand_regression_data2.csv"


def create_log_difference_dataset(
    input_path: Path = INPUT_FILE, output_path: Path = OUTPUT_FILE
) -> pd.DataFrame:
    """
    Create a dataset of log differences (Δln) from the base demand dataset.

    Parameters
    ----------
    input_path : Path
        CSV file containing the base level data (Q, P, Tax_rate, GDP).
    output_path : Path
        Destination CSV file for the log-difference dataset.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing Year and the log differences for each variable.
    """
    df = pd.read_csv(input_path)

    required_columns = [
        "Q (liters)",
        "P (yen/liter)",
        "Tax_rate (%)",
        "GDP (trillion yen)",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    if (df[required_columns] <= 0).any().any():
        raise ValueError("All values must be positive to compute logarithms.")

    df_log = pd.DataFrame(
        {
            "Year": df["Year"],
            "Δln(Q)": np.log(df["Q (liters)"]).diff(),
            "Δln(GDP)": np.log(df["GDP (trillion yen)"]).diff(),
            "Δln(P)": np.log(df["P (yen/liter)"]).diff(),
            "Δln(Tax_rate)": np.log(df["Tax_rate (%)"]).diff(),
        }
    )

    df_log = df_log.iloc[1:].reset_index(drop=True)
    df_log.to_csv(output_path, index=False)

    return df_log


if __name__ == "__main__":
    created_df = create_log_difference_dataset()
    print(f"Created {len(created_df)} rows in '{OUTPUT_FILE.name}'.")

