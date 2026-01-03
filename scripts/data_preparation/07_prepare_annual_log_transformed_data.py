"""
年次データに対数変換を適用するスクリプト
"""

import pandas as pd
import numpy as np
import os

print("="*60)
print("年次データの対数変換")
print("="*60)

# 1. 年次データの読み込み
print("\n年次データを読み込み中...")
data_file = 'demand_regression_data_annual.csv'
if not os.path.exists(data_file):
    print(f"エラー: {data_file} が見つかりません。")
    print("先に 06_aggregate_to_annual_data.py を実行してください。")
    exit(1)

df = pd.read_csv(data_file, encoding='utf-8-sig')
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

# GDP (trillion yen)の対数変換
mask_gdp = df['GDP (trillion yen)'].notna() & (df['GDP (trillion yen)'] > 0)
df.loc[mask_gdp, 'ln_GDP'] = np.log(df.loc[mask_gdp, 'GDP (trillion yen)'])

# Tax_rate (%)の対数変換
mask_tax = df['Tax_rate (%)'].notna() & (df['Tax_rate (%)'] > 0)
df.loc[mask_tax, 'ln_Tax_rate'] = np.log(df.loc[mask_tax, 'Tax_rate (%)'])

# P_relative（相対価格）の対数変換（存在する場合）
if 'P_relative' in df.columns:
    mask_p_rel = df['P_relative'].notna() & (df['P_relative'] > 0)
    df.loc[mask_p_rel, 'ln_P_relative'] = np.log(df.loc[mask_p_rel, 'P_relative'])
    print("相対価格の対数変換を追加しました")

print(f"対数変換完了:")
print(f"  ln_Q: {df['ln_Q'].notna().sum()}行")
print(f"  ln_P: {df['ln_P'].notna().sum()}行")
print(f"  ln_GDP: {df['ln_GDP'].notna().sum()}行")
print(f"  ln_Tax_rate: {df['ln_Tax_rate'].notna().sum()}行")
if 'ln_P_relative' in df.columns:
    print(f"  ln_P_relative: {df['ln_P_relative'].notna().sum()}行")

# 3. 処理済みデータを保存
output_dir = 'analysis'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'demand_regression_data_annual_log_transformed.csv')
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n" + "="*60)
print("処理済みデータを保存しました")
print("="*60)
print(f"出力ファイル: {output_file}")

# 4. 全変数が揃っているデータの確認
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
if len(df_complete) > 0:
    print(f"期間: {df_complete['Year'].min()} - {df_complete['Year'].max()}")

print("\n完了しました！")
print("\n次のステップ:")
print("  python analysis/01_estimate_demand_function_annual_level_model.py")

