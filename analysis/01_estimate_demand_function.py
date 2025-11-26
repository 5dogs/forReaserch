"""
需要関数の推定スクリプト
⊿lnQ = α×⊿lnGDP + β×⊿lnP + γ×⊿lnTax_rate + ε

四半期データに対応した需要関数の推定を行います。
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import os

# 出力ディレクトリ
output_dir = 'analysis/results'
os.makedirs(output_dir, exist_ok=True)

print("="*60)
print("需要関数の推定")
print("="*60)

# 1. 対数変換済みデータの読み込み
print("\n対数変換済みデータを読み込み中...")
# analysisフォルダ内のファイルを探す
data_file = os.path.join(os.path.dirname(__file__), 'demand_regression_data_log_transformed.csv')
if not os.path.exists(data_file):
    # ルートディレクトリから実行された場合
    data_file = 'analysis/demand_regression_data_log_transformed.csv'
if not os.path.exists(data_file):
    print("エラー: 対数変換済みデータが見つかりません。")
    print("先に 00_prepare_log_transformed_data.py を実行してください。")
    exit(1)

df = pd.read_csv(data_file)
df['Year'] = df['Year'].astype(str)

print(f"データ期間: {df['Year'].min()} - {df['Year'].max()}")
print(f"総行数: {len(df)}")

# 2. 全変数が揃っているデータのみを抽出（対数変換済み列も確認）
df_complete = df[
    df['Q (liters)'].notna() & 
    df['P (yen/liter)'].notna() & 
    df['Tax_rate (%)'].notna() & 
    df['GDP (trillion yen)'].notna() &
    df['ln_Q'].notna() &
    df['ln_P'].notna() &
    df['ln_GDP'].notna() &
    df['ln_Tax_rate'].notna()
].copy()

print(f"\n全変数が揃っているデータ: {len(df_complete)}行")
print(f"期間: {df_complete['Year'].min()} - {df_complete['Year'].max()}")

if len(df_complete) < 10:
    print("警告: 分析可能なデータが少なすぎます（最低10行必要）")
    exit(1)

# 3. 対数差分が計算されているか確認（なければ計算）
if 'Δln_Q' not in df_complete.columns or df_complete['Δln_Q'].isna().all():
    print("\n対数差分を計算中...")
    df_complete['Δln_Q'] = df_complete['ln_Q'].diff()
    df_complete['Δln_P'] = df_complete['ln_P'].diff()
    df_complete['Δln_GDP'] = df_complete['ln_GDP'].diff()
    df_complete['Δln_Tax_rate'] = df_complete['ln_Tax_rate'].diff()
else:
    print("\n対数差分は既に計算済みです")

# 最初の行はNaNになるので除外
df_analysis = df_complete[df_complete['Δln_Q'].notna()].copy()

print(f"分析対象データ: {len(df_analysis)}行（最初の行を除外）")

# 5. 回帰分析の準備
print("\n回帰分析を実行中...")
X = df_analysis[['Δln_GDP', 'Δln_P', 'Δln_Tax_rate']].copy()
y = df_analysis['Δln_Q'].copy()

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
X.columns = ['const', 'Δln_GDP', 'Δln_P', 'Δln_Tax_rate']

# 6. OLS回帰分析の実行
model = sm.OLS(y, X).fit()

# 7. 結果の表示
print("\n" + "="*60)
print("回帰分析結果")
print("="*60)
print(model.summary())

# 8. 係数の取得と解釈
alpha = model.params['Δln_GDP']      # 所得弾力性
beta = model.params['Δln_P']         # 価格弾力性
gamma = model.params['Δln_Tax_rate'] # 税率弾力性
const = model.params['const']        # 定数項

print("\n" + "="*60)
print("推定された係数")
print("="*60)
print(f"所得弾力性 (α): {alpha:.6f}")
print(f"  → GDPが1%増加すると、ガソリン消費量は{alpha:.4f}%変化")
print(f"\n価格弾力性 (β): {beta:.6f}")
print(f"  → 価格が1%上昇すると、ガソリン消費量は{beta:.4f}%変化")
print(f"\n税率弾力性 (γ): {gamma:.6f}")
print(f"  → 税率が1%上昇すると、ガソリン消費量は{gamma:.4f}%変化")
print(f"\n定数項: {const:.6f}")

# 9. 統計的有意性の確認
print("\n" + "="*60)
print("統計的有意性")
print("="*60)
print(f"R-squared: {model.rsquared:.4f} ({model.rsquared*100:.1f}%)")
print(f"Adjusted R-squared: {model.rsquared_adj:.4f} ({model.rsquared_adj*100:.1f}%)")
print(f"F統計量: {model.fvalue:.4f}")
print(f"F統計量のP値: {model.f_pvalue:.6f} {'***' if model.f_pvalue < 0.001 else '**' if model.f_pvalue < 0.01 else '*' if model.f_pvalue < 0.05 else '(非有意)'}")

pvalues = model.pvalues
print(f"\n各係数の有意性:")
print(f"  所得弾力性 (α): P値 = {pvalues['Δln_GDP']:.6f} {'***' if pvalues['Δln_GDP'] < 0.001 else '**' if pvalues['Δln_GDP'] < 0.01 else '*' if pvalues['Δln_GDP'] < 0.05 else '(非有意)'}")
print(f"  価格弾力性 (β): P値 = {pvalues['Δln_P']:.6f} {'***' if pvalues['Δln_P'] < 0.001 else '**' if pvalues['Δln_P'] < 0.01 else '*' if pvalues['Δln_P'] < 0.05 else '(非有意)'}")
print(f"  税率弾力性 (γ): P値 = {pvalues['Δln_Tax_rate']:.6f} {'***' if pvalues['Δln_Tax_rate'] < 0.001 else '**' if pvalues['Δln_Tax_rate'] < 0.01 else '*' if pvalues['Δln_Tax_rate'] < 0.05 else '(非有意)'}")
print(f"  (***: p<0.001, **: p<0.01, *: p<0.05)")

# 10. 結果をDataFrameに保存
results_df = pd.DataFrame({
    'Coefficient': ['α (所得弾力性)', 'β (価格弾力性)', 'γ (税率弾力性)', '定数項'],
    'Value': [alpha, beta, gamma, const],
    'P_value': [pvalues['Δln_GDP'], pvalues['Δln_P'], pvalues['Δln_Tax_rate'], pvalues['const']],
    'Interpretation': [
        f'GDPが1%増加→消費量{alpha:.4f}%変化',
        f'価格が1%上昇→消費量{beta:.4f}%変化',
        f'税率が1%上昇→消費量{gamma:.4f}%変化',
        '基礎的な需要変化率'
    ]
})

# 11. 分析データと結果を保存
df_analysis.to_csv(f'{output_dir}/01_analysis_data.csv', index=False, encoding='utf-8-sig')
results_df.to_csv(f'{output_dir}/01_demand_function_coefficients.csv', index=False, encoding='utf-8-sig')

print(f"\n" + "="*60)
print("結果を保存しました")
print("="*60)
print(f"分析データ: {output_dir}/01_analysis_data.csv")
print(f"係数結果: {output_dir}/01_demand_function_coefficients.csv")

# 12. 係数を辞書として返す（次のスクリプトで使用）
coefficients = {
    'alpha': alpha,
    'beta': beta,
    'gamma': gamma,
    'const': const,
    'model': model,
    'rsquared': model.rsquared,
    'rsquared_adj': model.rsquared_adj,
    'f_pvalue': model.f_pvalue
}

# 係数をJSON形式で保存
import json
with open(f'{output_dir}/01_coefficients.json', 'w', encoding='utf-8') as f:
    json.dump({k: float(v) if isinstance(v, (np.integer, np.floating)) else str(v) 
               for k, v in coefficients.items() if k != 'model'}, 
              f, indent=2, ensure_ascii=False)

print(f"係数（JSON）: {output_dir}/01_coefficients.json")
print("\n完了しました！")

