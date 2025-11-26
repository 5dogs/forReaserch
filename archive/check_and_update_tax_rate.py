import pandas as pd
import re

print("税率データの確認と更新を行います...\n")

# 1. demand_regression_data_raw.csvを読み込む
df_main = pd.read_csv('demand_regression_data_raw.csv')
print(f"メインデータ: {len(df_main)}行")

# 2. ガソリン関連税データを読み込む
tax_file = r"data/-2025ガソリン関連税四半期ごと/gasoline_tax_quarterly.csv"
df_tax = pd.read_csv(tax_file, encoding='utf-8')

# Year_Quarter列からYearQuarter形式に変換
df_tax['YearQuarter'] = df_tax['Year_Quarter'].str.replace('-', '')
df_tax = df_tax[['YearQuarter', '実効従量税率_円L']].copy()
df_tax.columns = ['YearQuarter', 'Tax_rate_yen_per_liter']

print(f"税データ: {len(df_tax)}行")

# 3. メインデータにYearQuarter列を追加
df_main['YearQuarter'] = df_main['Year']

# 4. 価格データを確認（既にマージされているはず）
print(f"\n価格データの確認:")
print(f"  P (yen/liter)が空: {df_main['P (yen/liter)'].isna().sum()}行")
print(f"  P (yen/liter)が \"-\": {(df_main['P (yen/liter)'] == '-').sum()}行")

# 5. 税率データを再計算
# 実効従量税率を価格で割って%にする
df_main = df_main.merge(df_tax[['YearQuarter', 'Tax_rate_yen_per_liter']], 
                        on='YearQuarter', how='left')

# 価格と税率の両方が存在する場合のみ計算
mask = df_main['Tax_rate_yen_per_liter'].notna() & df_main['P (yen/liter)'].notna()
# 価格が数値でない場合（"-"など）を除外
price_numeric = pd.to_numeric(df_main['P (yen/liter)'], errors='coerce')
mask = mask & price_numeric.notna()

# 税率を再計算
df_main.loc[mask, 'Tax_rate (%)'] = (
    df_main.loc[mask, 'Tax_rate_yen_per_liter'] / 
    price_numeric[mask] * 100
).round(2)

# 6. 結果を確認
print(f"\n税率データの更新結果:")
print(f"  Tax_rate (%)が更新された行: {mask.sum()}行")
print(f"  Tax_rate (%)が空の行: {df_main['Tax_rate (%)'].isna().sum()}行")

# 7. 更新されたデータを保存
df_output = pd.DataFrame()
df_output['Year'] = df_main['Year']
df_output['Q (liters)'] = df_main['Q (liters)']
df_output['P (yen/liter)'] = df_main['P (yen/liter)']
df_output['Tax_rate (%)'] = df_main['Tax_rate (%)']
df_output['GDP (trillion yen)'] = df_main['GDP (trillion yen)']

df_output.to_csv('demand_regression_data_raw.csv', index=False, encoding='utf-8-sig')
print(f"\ndemand_regression_data_raw.csv を更新しました")

# 8. サンプル表示
print(f"\n最初の10行:")
print(df_output.head(10).to_string())

print(f"\n最後の10行:")
print(df_output.tail(10).to_string())

print("\n完了しました！")

