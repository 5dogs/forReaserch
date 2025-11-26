"""
消費者物価指数（CPI）データの処理スクリプト
月次データを四半期データに変換し、相対価格を計算する
"""

import pandas as pd
import numpy as np
import os

print("="*60)
print("消費者物価指数（CPI）データの処理")
print("="*60)

# 1. CPIデータの読み込み
cpi_file = 'data/-2025消費者物価指数/自由帳 - zmi2020s.csv'
if not os.path.exists(cpi_file):
    print(f"エラー: {cpi_file} が見つかりません。")
    exit(1)

print(f"\nCPIデータを読み込み中: {cpi_file}")
df_cpi = pd.read_csv(cpi_file, encoding='utf-8-sig')

# 2. データ行の抽出（年月形式: YYYYMM）
print("\nデータ行を抽出中...")
df_cpi_data = df_cpi[df_cpi['類・品目'].astype(str).str.match(r'^\d{6}$', na=False)].copy()

if len(df_cpi_data) == 0:
    print("エラー: データ行が見つかりません。")
    exit(1)

print(f"データ行数: {len(df_cpi_data)}")

# 3. 年月列の処理
df_cpi_data['年月'] = df_cpi_data['類・品目'].astype(str)
df_cpi_data['Year'] = df_cpi_data['年月'].str[:4].astype(int)
df_cpi_data['Month'] = df_cpi_data['年月'].str[4:6].astype(int)

# 4. 四半期の計算
def get_quarter(month):
    if month in [1, 2, 3]:
        return 1
    elif month in [4, 5, 6]:
        return 2
    elif month in [7, 8, 9]:
        return 3
    else:
        return 4

df_cpi_data['Quarter'] = df_cpi_data['Month'].apply(get_quarter)
df_cpi_data['YearQuarter'] = df_cpi_data['Year'].astype(str) + 'Q' + df_cpi_data['Quarter'].astype(str)

# 5. 消費者物価指数（総合）の抽出と数値変換
print("\n消費者物価指数（総合）を抽出中...")
df_cpi_data['CPI'] = pd.to_numeric(df_cpi_data['総合'], errors='coerce')

# 6. 四半期平均の計算
print("\n四半期平均を計算中...")
df_cpi_quarterly = df_cpi_data.groupby(['Year', 'Quarter']).agg({
    'CPI': 'mean',
    'YearQuarter': 'first'
}).reset_index()

df_cpi_quarterly = df_cpi_quarterly.sort_values(['Year', 'Quarter'])

print(f"四半期データ数: {len(df_cpi_quarterly)}")
print(f"期間: {df_cpi_quarterly['YearQuarter'].min()} - {df_cpi_quarterly['YearQuarter'].max()}")

# 7. データの保存
output_file = 'data/-2025消費者物価指数/CPI_quarterly.csv'
os.makedirs(os.path.dirname(output_file), exist_ok=True)

df_cpi_quarterly[['Year', 'Quarter', 'YearQuarter', 'CPI']].to_csv(
    output_file, index=False, encoding='utf-8-sig'
)

print(f"\n四半期データを保存しました: {output_file}")

# 8. データの確認
print("\n" + "="*60)
print("四半期データの確認")
print("="*60)
print(df_cpi_quarterly[['Year', 'Quarter', 'YearQuarter', 'CPI']].head(10).to_string())
print("\n...")
print(df_cpi_quarterly[['Year', 'Quarter', 'YearQuarter', 'CPI']].tail(10).to_string())

# 9. 統計情報
print("\n" + "="*60)
print("統計情報")
print("="*60)
print(f"CPIの平均: {df_cpi_quarterly['CPI'].mean():.2f}")
print(f"CPIの最小値: {df_cpi_quarterly['CPI'].min():.2f}")
print(f"CPIの最大値: {df_cpi_quarterly['CPI'].max():.2f}")
print(f"CPIの標準偏差: {df_cpi_quarterly['CPI'].std():.2f}")

print("\n完了しました！")
print(f"\n次のステップ:")
print("1. このCPIデータをメインデータにマージ")
print("2. 相対価格 = ガソリン価格 / CPI を計算")
print("3. レベルモデルで再推定")

