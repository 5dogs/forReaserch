import pandas as pd
import re

CSV_PATH = r"data/-2024ガソリン販売量/統合.csv"
TARGET_YEAR_HEISEI = "21年"  # Heisei 21 -> 2009
ERA_NAME = "平成"


def clean_number(value):
    if pd.isna(value):
        return None
    s = (
        str(value)
        .replace('"', "")
        .replace(",", "")
        .replace("r", "")
        .strip()
    )
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main():
    df = pd.read_csv(CSV_PATH, header=None, encoding="utf-8")

    monthly_gasoline = {}
    current_era = None
    current_year_str = None

    for _, row in df.iterrows():
        era = row[2] if pd.notna(row[2]) else current_era
        year_str = row[3] if pd.notna(row[3]) else current_year_str
        month_str = row[4]

        if era is not None:
            current_era = era
        if year_str is not None:
            current_year_str = year_str

        if str(era).strip() == ERA_NAME and isinstance(year_str, str) and TARGET_YEAR_HEISEI in year_str:
            if isinstance(month_str, str) and "月" in month_str and "～" not in month_str:
                match = re.search(r"(\d+)", month_str)
                if match:
                    month = int(match.group(1))
                    gas_kl = clean_number(row[7])
                    if gas_kl is not None:
                        monthly_gasoline[month] = gas_kl

    if len(monthly_gasoline) != 12:
        print("Warning: monthly data not complete:", sorted(monthly_gasoline.keys()))

    # Fallback: quarter summaries found in the \"販売部門\" section
    quarter_fallback = {}
    fallback_year = None
    for _, row in df.iterrows():
        row_values = [str(v) for v in row if pd.notna(v)]
        if not row_values:
            continue

        digits = re.findall(r"\d+", row_values[0])
        if len(digits) >= 3:
            year_num = int(digits[0])
            if year_num != 21:
                fallback_year = None
                continue
            fallback_year = year_num
            start_month = int(digits[1])
        elif len(digits) >= 1 and fallback_year == 21:
            start_month = int(digits[0])
        else:
            continue

        quarter = (start_month - 1) // 3 + 1

        value_cell = next(
            (
                cell
                for cell in row_values[1:]
                if re.fullmatch(r"[0-9,]+", cell)
            ),
            None,
        )
        if value_cell:
            quarter_fallback[quarter] = float(value_cell.replace(",", ""))

    quarter_months = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
    quarter_totals = {}
    for q, months in quarter_months.items():
        total = sum(monthly_gasoline.get(m, 0) for m in months)
        if total == 0 and q in quarter_fallback:
            total = quarter_fallback[q]
        quarter_totals[q] = total
        print(f"2009 Q{q} gasoline (kl): {total:,.0f}")

    # Update demand_regression_data_raw.csv
    df_main = pd.read_csv("demand_regression_data_raw.csv")
    df_main = df_main.set_index("Year")

    for q in [2, 3, 4]:
        liters = int(round(quarter_totals[q] * 1000))
        key = f"2009Q{q}"
        if key in df_main.index:
            old_val = df_main.at[key, "Q (liters)"]
            df_main.at[key, "Q (liters)"] = liters
            print(f"Updated {key}: {old_val} -> {liters}")
        else:
            print(f"Key {key} not found in demand_regression_data_raw.csv")

    df_main = df_main.reset_index()
    df_main.to_csv("demand_regression_data_raw.csv", index=False, encoding="utf-8-sig")
    print("Saved demand_regression_data_raw.csv")


if __name__ == "__main__":
    main()

