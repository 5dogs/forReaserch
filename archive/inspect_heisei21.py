import pandas as pd

df = pd.read_csv(r"data/-2024ガソリン販売量/統合.csv", header=None, encoding="utf-8")

for idx in range(90, 110):
    row = df.iloc[idx]
    values = [str(v) for v in row.tolist() if pd.notna(v)]
    print(idx, values[:8])

