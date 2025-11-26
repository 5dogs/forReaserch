"""
需要関数の推定スクリプト（年次データ・レベルモデル版）
ln(Q) = C + α×ln(GDP) + β×ln(P_relative) + γ×ln(Tax_rate) + δ1×D2008 + δ2×D2020 + ε

先行研究に合わせて年次データでレベルモデルを推定します。
実質GDP、相対価格、ダミー変数を使用します。
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import os
import json

# 出力ディレクトリ
output_dir = 'analysis/results'
os.makedirs(output_dir, exist_ok=True)

print("="*60)
print("需要関数の推定（年次データ・レベルモデル）")
print("="*60)
print("\n【年次データ・レベルモデルとは】")
print("レベルモデル: ln(Q) = C + α×ln(GDP) + β×ln(P_relative) + γ×ln(Tax_rate) + δ1×D2008 + δ2×D2020 + ε")
print("- 変数の水準（レベル）をそのまま使用")
print("- 年次データを使用（季節変動を除去）")
print("- 実質GDP、相対価格を使用（先行研究と同じ）")
print("- ダミー変数で重要なイベントを捕捉")
print("\n【先行研究との比較】")
print("先行研究: ln(Q)＝C＋α＊ln(GDP)＋β＊ln(P)＋γ＊D94 → R²=95%程度")
print("現在の方法: 年次データ + 実質GDP + 相対価格 + ダミー変数")

# 1. 対数変換済み年次データの読み込み
print("\n" + "="*60)
print("データの読み込み")
print("="*60)
data_file = 'analysis/demand_regression_data_annual_log_transformed.csv'
if not os.path.exists(data_file):
    print("エラー: 対数変換済み年次データが見つかりません。")
    print("先に 07_prepare_annual_log_transformed_data.py を実行してください。")
    exit(1)

df = pd.read_csv(data_file, encoding='utf-8-sig')
df['Year'] = df['Year'].astype(str)

print(f"データ期間: {df['Year'].min()} - {df['Year'].max()}")
print(f"総行数: {len(df)}")

# 2. 相対価格の対数変換（まだ計算されていない場合）
if 'P_relative' in df.columns and 'ln_P_relative' not in df.columns:
    df['ln_P_relative'] = np.log(df['P_relative'])
    print("相対価格の対数変換を計算しました")

# 3. 全変数が揃っているデータのみを抽出（相対価格を使用）
use_relative_price = 'P_relative' in df.columns and df['P_relative'].notna().any()

if use_relative_price:
    print("\n相対価格を使用します（先行研究の方法）")
    price_col = 'P_relative'
    ln_price_col = 'ln_P_relative'
else:
    print("\n名目価格を使用します（相対価格データがありません）")
    price_col = 'P (yen/liter)'
    ln_price_col = 'ln_P'

# ダミー変数の確認
dummy_vars = []
if 'D2008' in df.columns:
    dummy_vars.append('D2008')
if 'D2020' in df.columns:
    dummy_vars.append('D2020')
if 'D2009' in df.columns:
    dummy_vars.append('D2009')

print(f"使用するダミー変数: {dummy_vars}")

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
print(f"期間: {df_complete['Year'].min()} - {df_complete['Year'].max()}")

if len(df_complete) < 10:
    print("警告: 分析可能なデータが少なすぎます（最低10行必要）")
    exit(1)

# 4. レベルモデルでの回帰分析
print("\n" + "="*60)
print("回帰分析（年次データ・レベルモデル）")
print("="*60)
if use_relative_price:
    print("推定式: ln(Q) = C + α×ln(GDP) + β×ln(P_relative) + γ×ln(Tax_rate) + δ1×D2008 + δ2×D2020 + ε")
    X = df_complete[['ln_GDP', 'ln_P_relative', 'ln_Tax_rate'] + dummy_vars].copy()
    X.columns = ['ln_GDP', 'ln_P', 'ln_Tax_rate'] + dummy_vars  # 統一のため
else:
    print("推定式: ln(Q) = C + α×ln(GDP) + β×ln(P) + γ×ln(Tax_rate) + δ1×D2008 + δ2×D2020 + ε")
    X = df_complete[['ln_GDP', 'ln_P', 'ln_Tax_rate'] + dummy_vars].copy()

y = df_complete['ln_Q'].copy()

# 欠損値を除外
valid_mask = X.notna().all(axis=1) & y.notna()
X = X[valid_mask]
y = y[valid_mask]

print(f"回帰分析に使用するデータ: {len(X)}行")

if len(X) < 10:
    print("警告: 回帰分析に使用できるデータが少なすぎます")
    exit(1)

# 定数項を追加
X = sm.add_constant(X)
X.columns = ['const', 'ln_GDP', 'ln_P', 'ln_Tax_rate'] + dummy_vars

# OLS回帰分析の実行
model = sm.OLS(y, X).fit()

# 結果の表示
print("\n" + "="*60)
print("回帰分析結果")
print("="*60)
print(model.summary())

# 係数の抽出
alpha = model.params['ln_GDP']      # 所得弾力性
beta = model.params['ln_P']         # 価格弾力性
gamma = model.params['ln_Tax_rate'] # 税率弾力性
const = model.params['const']       # 定数項

# ダミー変数の係数
dummy_coeffs = {}
for dummy in dummy_vars:
    dummy_coeffs[dummy] = model.params[dummy]

# P値の抽出
pvalues = model.pvalues

# 結果の保存
print("\n" + "="*60)
print("推定された係数")
print("="*60)
print(f"所得弾力性 (α): {alpha:.4f}")
print(f"  → GDPが1%増加すると、ガソリン消費量は{alpha:.4f}%変化")

print(f"\n価格弾力性 (β): {beta:.4f}")
print(f"  → 価格が1%上昇すると、ガソリン消費量は{beta:.4f}%変化")

print(f"\n税率弾力性 (γ): {gamma:.4f}")
print(f"  → 税率が1%上昇すると、ガソリン消費量は{gamma:.4f}%変化")

print(f"\n定数項 (C): {const:.4f}")

for dummy, coeff in dummy_coeffs.items():
    print(f"\n{dummy}の係数: {coeff:.4f}")
    print(f"  → {dummy}が1の時、ガソリン消費量は{coeff:.4f}変化")

# 統計的有意性
print("\n" + "="*60)
print("統計的有意性")
print("="*60)
print(f"R-squared: {model.rsquared:.4f} ({model.rsquared*100:.1f}%)")
print(f"Adjusted R-squared: {model.rsquared_adj:.4f} ({model.rsquared_adj*100:.1f}%)")
print(f"F統計量: {model.fvalue:.4f}")
print(f"F統計量のP値: {model.f_pvalue:.6f} {'***' if model.f_pvalue < 0.001 else '**' if model.f_pvalue < 0.01 else '*' if model.f_pvalue < 0.05 else '(非有意)'}")

print(f"\n各係数の有意性:")
print(f"  所得弾力性 (α): P値 = {pvalues['ln_GDP']:.6f} {'***' if pvalues['ln_GDP'] < 0.001 else '**' if pvalues['ln_GDP'] < 0.01 else '*' if pvalues['ln_GDP'] < 0.05 else '(非有意)'}")
print(f"  価格弾力性 (β): P値 = {pvalues['ln_P']:.6f} {'***' if pvalues['ln_P'] < 0.001 else '**' if pvalues['ln_P'] < 0.01 else '*' if pvalues['ln_P'] < 0.05 else '(非有意)'}")
print(f"  税率弾力性 (γ): P値 = {pvalues['ln_Tax_rate']:.6f} {'***' if pvalues['ln_Tax_rate'] < 0.001 else '**' if pvalues['ln_Tax_rate'] < 0.01 else '*' if pvalues['ln_Tax_rate'] < 0.05 else '(非有意)'}")
for dummy in dummy_vars:
    print(f"  {dummy}: P値 = {pvalues[dummy]:.6f} {'***' if pvalues[dummy] < 0.001 else '**' if pvalues[dummy] < 0.01 else '*' if pvalues[dummy] < 0.05 else '(非有意)'}")
print("  (***: p<0.001, **: p<0.01, *: p<0.05)")

# 結果をCSVに保存
results_df = pd.DataFrame({
    'Variable': ['α (所得弾力性)', 'β (価格弾力性)', 'γ (税率弾力性)', 'C (定数項)'] + [f'{d}の係数' for d in dummy_vars],
    'Coefficient': [alpha, beta, gamma, const] + [dummy_coeffs[d] for d in dummy_vars],
    'P_value': [pvalues['ln_GDP'], pvalues['ln_P'], pvalues['ln_Tax_rate'], pvalues['const']] + [pvalues[d] for d in dummy_vars],
    'Interpretation': [
        f'GDPが1%増加→消費量{alpha:.4f}%変化',
        f'価格が1%上昇→消費量{beta:.4f}%変化',
        f'税率が1%上昇→消費量{gamma:.4f}%変化',
        '定数項',
    ] + [f'{d}が1の時、消費量{dummy_coeffs[d]:.4f}変化' for d in dummy_vars]
})

results_df.to_csv(
    os.path.join(output_dir, '01_demand_function_coefficients_annual_level_model.csv'),
    index=False,
    encoding='utf-8-sig'
)

# 分析データを保存
df_analysis = df_complete[['Year', 'Q (liters)', 'P (yen/liter)', 'Tax_rate (%)', 'GDP (trillion yen)', 
                           'CPI', 'P_relative', 'ln_Q', 'ln_P', 'ln_P_relative', 'ln_GDP', 'ln_Tax_rate'] + dummy_vars].copy()
df_analysis.to_csv(
    os.path.join(output_dir, '01_analysis_data_annual_level_model.csv'),
    index=False,
    encoding='utf-8-sig'
)

# JSON形式でも保存
results_json = {
    'alpha': float(alpha),
    'beta': float(beta),
    'gamma': float(gamma),
    'const': float(const),
    'rsquared': float(model.rsquared),
    'rsquared_adj': float(model.rsquared_adj),
    'f_pvalue': float(model.f_pvalue),
    'model_type': 'annual_level_model',
    'dummy_variables': {d: float(dummy_coeffs[d]) for d in dummy_vars},
    'dummy_pvalues': {d: float(pvalues[d]) for d in dummy_vars}
}

with open(os.path.join(output_dir, '01_coefficients_annual_level_model.json'), 'w', encoding='utf-8') as f:
    json.dump(results_json, f, indent=2, ensure_ascii=False)

print("\n" + "="*60)
print("結果を保存しました")
print("="*60)
print(f"分析データ: {os.path.join(output_dir, '01_analysis_data_annual_level_model.csv')}")
print(f"係数結果: {os.path.join(output_dir, '01_demand_function_coefficients_annual_level_model.csv')}")
print(f"係数（JSON）: {os.path.join(output_dir, '01_coefficients_annual_level_model.json')}")

print("\n完了しました！")

