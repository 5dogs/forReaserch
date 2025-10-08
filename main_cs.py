import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# ----------------------------------------
# Step 1. データの読み込みと前処理
# ----------------------------------------
df = pd.read_csv("sample_demand_regression_data.csv")  # ← ファイル名を適宜変更
df = df.rename(columns={
    "Q (millions)": "Q",
    "GDP (trillion yen)": "GDP",
    "P (thousand yen)": "P"
})

# 対数変換
df["ln_Q"] = np.log(df["Q"])
df["ln_GDP"] = np.log(df["GDP"])
df["ln_P"] = np.log(df["P"])

# 対数差分（次のCSV用）
df["Δln(Q)"] = df["ln_Q"].diff()
df["Δln(GDP)"] = df["ln_GDP"].diff()
df["Δln(P)"] = df["ln_P"].diff()

# 差分データを別ファイルに保存
df_diff = df[["Year", "Δln(Q)", "Δln(GDP)", "Δln(P)"]].dropna()
df_diff.to_csv("diff_output.csv", index=False)

# ----------------------------------------
# Step 2. 回帰分析（需要関数の推定）
# ln(Q) = a + b * ln(GDP) + c * ln(P)
# ----------------------------------------
X = df[["ln_GDP", "ln_P"]]
X = sm.add_constant(X)
y = df["ln_Q"]

model = sm.OLS(y, X).fit()
print("\n--- 回帰結果 ---")
print(model.summary())

# ----------------------------------------
# Step 3. 推定された需要関数に基づく余剰の計算
# 消費者余剰（CS） = ∫0^Q P(Q') dQ' - P×Q
# → 近似: CS ≈ (ε / (1 + ε)) × P × Q  （ε = 価格弾力性）
# ----------------------------------------
b_price = model.params["ln_P"]
epsilon = b_price  # ln(P)の係数は弾力性に等しい

df["CS"] = (epsilon / (1 + epsilon)) * df["P"] * df["Q"]

# CSグラフの表示
plt.figure(figsize=(10, 5))
plt.plot(df["Year"], df["CS"], marker='o')
plt.title("推定された消費者余剰（CS）の推移")
plt.xlabel("Year")
plt.ylabel("CS（千円×百万個）")
plt.grid(True)
plt.tight_layout()
plt.show()
