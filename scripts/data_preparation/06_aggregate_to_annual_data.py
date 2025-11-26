"""
四半期データを年次データに集約するスクリプト
先行研究と同じ年次データで分析するため
"""

import pandas as pd
import numpy as np
import os

print("="*60)
print("四半期データを年次データに集約")
print("="*60)

# 1. 四半期データの読み込み
print("\n四半期データを読み込み中...")
data_file = 'demand_regression_data_raw.csv'
if not os.path.exists(data_file):
    print(f"エラー: {data_file} が見つかりません。")
    exit(1)

df_quarterly = pd.read_csv(data_file, encoding='utf-8-sig')
df_quarterly['Year'] = df_quarterly['Year'].astype(str)

# Year列から年を抽出（例: "2007Q1" -> 2007）
df_quarterly['Year_num'] = df_quarterly['Year'].str[:4].astype(int)

print(f"四半期データ期間: {df_quarterly['Year'].min()} - {df_quarterly['Year'].max()}")
print(f"四半期データ数: {len(df_quarterly)}")

# 2. 年次データへの集約
print("\n年次データに集約中...")

# 集約方法の定義
aggregation_dict = {
    'Q (liters)': 'sum',  # 年間合計
    'P (yen/liter)': 'mean',  # 年間平均価格
    'Tax_rate (%)': 'mean',  # 年間平均税率
    'GDP (trillion yen)': 'sum',  # 年間合計（実質GDP）
    'CPI': 'mean',  # 年間平均CPI
    'P_relative': 'mean'  # 年間平均相対価格
}

# 年次データに集約
df_annual = df_quarterly.groupby('Year_num').agg(aggregation_dict).reset_index()
df_annual.rename(columns={'Year_num': 'Year'}, inplace=True)
df_annual['Year'] = df_annual['Year'].astype(str)

print(f"年次データ期間: {df_annual['Year'].min()} - {df_annual['Year'].max()}")
print(f"年次データ数: {len(df_annual)}")

# 3. ダミー変数の追加
print("\nダミー変数を追加中...")

# D2008: 2008年の暫定税率失効・復活（2008Q2-Q4の影響を年次で捉える）
df_annual['D2008'] = (df_annual['Year'] == '2008').astype(int)

# D2020: 2020年のCOVID-19パンデミック（特にQ2の影響が大きい）
df_annual['D2020'] = (df_annual['Year'] == '2020').astype(int)

# D2009: 2009年のリーマンショック影響
df_annual['D2009'] = (df_annual['Year'] == '2009').astype(int)

print(f"D2008=1の年: {df_annual[df_annual['D2008']==1]['Year'].tolist()}")
print(f"D2020=1の年: {df_annual[df_annual['D2020']==1]['Year'].tolist()}")
print(f"D2009=1の年: {df_annual[df_annual['D2009']==1]['Year'].tolist()}")

# 4. データの保存
output_file = 'demand_regression_data_annual.csv'
df_annual.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n年次データを保存しました: {output_file}")

# 5. データの確認
print("\n" + "="*60)
print("年次データの確認")
print("="*60)
print(f"全変数が揃っているデータ: {df_annual[df_annual['Q (liters)'].notna() & df_annual['P (yen/liter)'].notna() & df_annual['GDP (trillion yen)'].notna()].shape[0]}行")

# 統計情報
print("\n統計情報:")
print(f"Q (liters)の平均: {df_annual['Q (liters)'].mean():.2f} 10億リットル")
print(f"P (yen/liter)の平均: {df_annual['P (yen/liter)'].mean():.2f} 円/L")
print(f"GDP (trillion yen)の平均: {df_annual['GDP (trillion yen)'].mean():.2f} 兆円")

# サンプル表示
print("\n最初の5行:")
print(df_annual.head().to_string())
print("\n最後の5行:")
print(df_annual.tail().to_string())

print("\n完了しました！")
print(f"\n次のステップ:")
print("1. 年次データに対数変換を適用")
print("2. 年次データでレベルモデルを推定（ダミー変数含む）")

