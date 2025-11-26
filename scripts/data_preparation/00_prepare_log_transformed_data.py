"""
対数変換済みデータの準備スクリプト
demand_regression_data_raw.csvに対数変換列を追加して保存

処理内容:
1. rawデータを読み込む
2. 対数変換: ln_Q, ln_P, ln_GDP, ln_Tax_rate
3. 対数差分: Δln_Q, Δln_P, Δln_GDP, Δln_Tax_rate
4. 処理済みデータを保存
"""

import pandas as pd
import numpy as np
import os

print("="*60)
print("対数変換済みデータの準備")
print("="*60)

# 1. rawデータの読み込み
print("\nrawデータを読み込み中...")
# ルートディレクトリのrawデータを読み込む
data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'demand_regression_data_raw.csv')
if not os.path.exists(data_file):
    data_file = 'demand_regression_data_raw.csv'
if not os.path.exists(data_file):
    print(f"エラー: {data_file} が見つかりません。")
    exit(1)

df = pd.read_csv(data_file)
df['Year'] = df['Year'].astype(str)

print(f"データ期間: {df['Year'].min()} - {df['Year'].max()}")
print(f"総行数: {len(df)}")

# 2. 対数変換（正の値のみ）
print("\n対数変換を実行中...")

# Q (liters)の対数変換
mask_q = df['Q (liters)'].notna() & (df['Q (liters)'] > 0)
df.loc[mask_q, 'ln_Q'] = np.log(df.loc[mask_q, 'Q (liters)'])

# P (yen/liter)の対数変換
mask_p = df['P (yen/liter)'].notna() & (df['P (yen/liter)'] > 0)
df.loc[mask_p, 'ln_P'] = np.log(df.loc[mask_p, 'P (yen/liter)'])

# P_relative（相対価格）の対数変換（存在する場合）
if 'P_relative' in df.columns:
    mask_p_rel = df['P_relative'].notna() & (df['P_relative'] > 0)
    df.loc[mask_p_rel, 'ln_P_relative'] = np.log(df.loc[mask_p_rel, 'P_relative'])
    print("相対価格の対数変換を追加しました")

# GDP (trillion yen)の対数変換
mask_gdp = df['GDP (trillion yen)'].notna() & (df['GDP (trillion yen)'] > 0)
df.loc[mask_gdp, 'ln_GDP'] = np.log(df.loc[mask_gdp, 'GDP (trillion yen)'])

# Tax_rate (%)の対数変換
mask_tax = df['Tax_rate (%)'].notna() & (df['Tax_rate (%)'] > 0)
df.loc[mask_tax, 'ln_Tax_rate'] = np.log(df.loc[mask_tax, 'Tax_rate (%)'])

print(f"対数変換完了:")
print(f"  ln_Q: {df['ln_Q'].notna().sum()}行")
print(f"  ln_P: {df['ln_P'].notna().sum()}行")
print(f"  ln_GDP: {df['ln_GDP'].notna().sum()}行")
print(f"  ln_Tax_rate: {df['ln_Tax_rate'].notna().sum()}行")

# 3. 対数差分の計算（前四半期比変化率）
print("\n対数差分を計算中...")

# 年四半期でソート（念のため）
df = df.sort_values('Year').reset_index(drop=True)

# 対数差分を計算
df['Δln_Q'] = df['ln_Q'].diff()
df['Δln_P'] = df['ln_P'].diff()
df['Δln_GDP'] = df['ln_GDP'].diff()
df['Δln_Tax_rate'] = df['ln_Tax_rate'].diff()

print(f"対数差分計算完了:")
print(f"  Δln_Q: {df['Δln_Q'].notna().sum()}行")
print(f"  Δln_P: {df['Δln_P'].notna().sum()}行")
print(f"  Δln_GDP: {df['Δln_GDP'].notna().sum()}行")
print(f"  Δln_Tax_rate: {df['Δln_Tax_rate'].notna().sum()}行")

# 4. 処理済みデータを保存（analysisフォルダ内）
# ルートディレクトリのanalysisフォルダに保存
output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'analysis')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'demand_regression_data_log_transformed.csv')
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n" + "="*60)
print("処理済みデータを保存しました")
print("="*60)
print(f"出力ファイル: {output_file}")
print(f"追加された列:")
print(f"  - ln_Q, ln_P, ln_GDP, ln_Tax_rate (対数変換)")
print(f"  - Δln_Q, Δln_P, Δln_GDP, Δln_Tax_rate (対数差分)")

# 5. 全変数が揃っているデータの確認
df_complete = df[
    df['Q (liters)'].notna() & 
    df['P (yen/liter)'].notna() & 
    df['Tax_rate (%)'].notna() & 
    df['GDP (trillion yen)'].notna()
].copy()

print(f"\n全変数が揃っているデータ: {len(df_complete)}行")
if len(df_complete) > 0:
    print(f"期間: {df_complete['Year'].min()} - {df_complete['Year'].max()}")
    print(f"対数差分が計算可能なデータ: {df_complete['Δln_Q'].notna().sum()}行")

print("\n完了しました！")
print("\n次のステップ:")
print("  python analysis/01_estimate_demand_function.py")
print("  (このスクリプトは対数変換済みデータを使用します)")
print(f"\n出力ファイル: {output_file}")

