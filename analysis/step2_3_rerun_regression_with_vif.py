"""
Step 2 & 3: 2025年を除外して回帰分析を再実行し、VIFを計算して多重共線性を診断
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import os
import json

print("="*60)
print("Step 2 & 3: 回帰分析の再実行と多重共線性の診断")
print("="*60)

# 出力ディレクトリ
output_dir = 'analysis/results'
os.makedirs(output_dir, exist_ok=True)

# 1. データの読み込み
print("\n【1. データの読み込み】")
data_file = 'analysis/demand_regression_data_annual_log_transformed.csv'
df = pd.read_csv(data_file, encoding='utf-8-sig')
df['Year'] = df['Year'].astype(str)

print(f"データ期間: {df['Year'].min()} - {df['Year'].max()}")
print(f"総行数: {len(df)}")

# 2. 相対価格を使用
use_relative_price = 'P_relative' in df.columns and df['P_relative'].notna().any()
if use_relative_price:
    price_col = 'P_relative'
    ln_price_col = 'ln_P_relative'
    print("相対価格を使用します")
else:
    price_col = 'P (yen/liter)'
    ln_price_col = 'ln_P'
    print("名目価格を使用します")

# 3. ダミー変数の確認
dummy_vars = []
if 'D2008' in df.columns:
    dummy_vars.append('D2008')
if 'D2020' in df.columns:
    dummy_vars.append('D2020')
if 'D2009' in df.columns:
    dummy_vars.append('D2009')
print(f"使用するダミー変数: {dummy_vars}")

# 4. 全変数が揃っているデータを抽出
df_complete = df[
    df['Q (liters)'].notna() & 
    df[price_col].notna() & 
    df['Tax_rate (%)'].notna() & 
    df['GDP (trillion yen)'].notna() &
    df['ln_Q'].notna() &
    df[ln_price_col].notna() &
    df['ln_GDP'].notna() &
    df['ln_Tax_rate'].notna()
].copy()

print(f"\n全変数が揃っているデータ: {len(df_complete)}行")

# 5. 2025年を除外（異常値のため）
print(f"\n【2. 2025年の異常値を除外】")
if '2025' in df_complete['Year'].values:
    print(f"2025年のデータを除外します（GDPが異常に小さいため）")
    print(f"2025年のGDP: {df_complete[df_complete['Year'] == '2025']['GDP (trillion yen)'].iloc[0]:.2f} 兆円")
    df_complete = df_complete[df_complete['Year'] != '2025'].copy()
    print(f"除外後のデータ: {len(df_complete)}行")
    print(f"期間: {df_complete['Year'].min()} - {df_complete['Year'].max()}")

# 6. 回帰分析の準備
print(f"\n【3. 回帰分析の実行（2025年除外）】")
if use_relative_price:
    print("推定式: ln(Q) = C + α×ln(GDP) + β×ln(P_relative) + γ×ln(Tax_rate) + δ1×D2008 + δ2×D2020 + δ3×D2009 + ε")
    X = df_complete[['ln_GDP', 'ln_P_relative', 'ln_Tax_rate'] + dummy_vars].copy()
    X.columns = ['ln_GDP', 'ln_P', 'ln_Tax_rate'] + dummy_vars
else:
    print("推定式: ln(Q) = C + α×ln(GDP) + β×ln(P) + γ×ln(Tax_rate) + δ1×D2008 + δ2×D2020 + δ3×D2009 + ε")
    X = df_complete[['ln_GDP', 'ln_P', 'ln_Tax_rate'] + dummy_vars].copy()

y = df_complete['ln_Q'].copy()

# 欠損値を除外
valid_mask = X.notna().all(axis=1) & y.notna()
X = X[valid_mask]
y = y[valid_mask]

print(f"回帰分析に使用するデータ: {len(X)}行")

# 定数項を追加
X_with_const = sm.add_constant(X)
X_with_const.columns = ['const', 'ln_GDP', 'ln_P', 'ln_Tax_rate'] + dummy_vars

# 7. OLS回帰分析の実行
print(f"\n【4. 回帰分析結果】")
model = sm.OLS(y, X_with_const).fit()
print(model.summary())

# 係数の抽出
alpha = model.params['ln_GDP']
beta = model.params['ln_P']
gamma = model.params['ln_Tax_rate']
const = model.params['const']

dummy_coeffs = {}
for dummy in dummy_vars:
    dummy_coeffs[dummy] = model.params[dummy]

pvalues = model.pvalues

print(f"\n【5. 係数の比較】")
print("="*60)
print(f"所得弾力性 (α): {alpha:.4f} (P値: {pvalues['ln_GDP']:.6f})")
print(f"価格弾力性 (β): {beta:.4f} (P値: {pvalues['ln_P']:.6f})")
print(f"税率弾力性 (γ): {gamma:.4f} (P値: {pvalues['ln_Tax_rate']:.6f})")
print(f"R-squared: {model.rsquared:.4f}")

if beta > 0:
    print(f"\n[警告] βが正の値（{beta:.4f}）となっています。")
    print("   これは理論と矛盾しています（価格上昇→需要増加）。")
    print("   多重共線性の可能性が高いです。")

# 8. VIF（分散拡大係数）の計算
print(f"\n【6. VIF（分散拡大係数）の計算】")
print("="*60)
print("VIF > 10 の場合、多重共線性が問題となります。")

# 説明変数だけ（定数項を除く）
X_for_vif = X_with_const.iloc[:, 1:]  # 定数項を除外

vif_data = pd.DataFrame()
vif_data["Variable"] = X_for_vif.columns
vif_data["VIF"] = [variance_inflation_factor(X_for_vif.values, i) 
                   for i in range(len(X_for_vif.columns))]

print("\nVIF値:")
print(vif_data.to_string(index=False))

# 多重共線性の警告
high_vif = vif_data[vif_data['VIF'] > 10]
if len(high_vif) > 0:
    print(f"\n[警告] 以下の変数で多重共線性が検出されました（VIF > 10）:")
    print(high_vif.to_string(index=False))
    print("\nこれらの変数をモデルから除外するか、主成分分析などを検討してください。")

# 9. 変数間の相関マトリックス（詳細）
print(f"\n【7. 変数間の相関マトリックス（詳細）】")
print("="*60)
corr_vars = ['ln_Q', 'ln_GDP', 'ln_P_relative', 'ln_Tax_rate']
corr_matrix = df_complete[corr_vars].corr()
print(corr_matrix.round(4))

# 特に問題となる相関を確認
print(f"\n重要な相関:")
corr_p_tax = df_complete['ln_P_relative'].corr(df_complete['ln_Tax_rate'])
print(f"  ln_P_relative と ln_Tax_rate: {corr_p_tax:.4f}")
if abs(corr_p_tax) > 0.9:
    print("    [警告] 極めて強い相関（多重共線性の原因）")

# 10. 結果を保存
print(f"\n【8. 結果の保存】")
results_json = {
    'alpha': float(alpha),
    'beta': float(beta),
    'gamma': float(gamma),
    'const': float(const),
    'rsquared': float(model.rsquared),
    'rsquared_adj': float(model.rsquared_adj),
    'f_pvalue': float(model.f_pvalue),
    'model_type': 'annual_level_model_excl_2025',
    'excluded_year': '2025',
    'dummy_variables': {d: float(dummy_coeffs[d]) for d in dummy_vars},
    'dummy_pvalues': {d: float(pvalues[d]) for d in dummy_vars},
    'vif': {row['Variable']: float(row['VIF']) for _, row in vif_data.iterrows()}
}

output_file = os.path.join(output_dir, '01_coefficients_annual_level_model_excl_2025.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results_json, f, indent=2, ensure_ascii=False)

print(f"結果を保存しました: {output_file}")

print("\n" + "="*60)
print("Step 2 & 3完了")
print("="*60)

