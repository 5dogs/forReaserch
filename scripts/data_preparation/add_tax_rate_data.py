import pandas as pd
import numpy as np

print("税率データを追加します...\n")

# 1. 既存のdemand_regression_data_raw.csvを読み込む
target_file = 'demand_regression_data_raw.csv'
df_main = pd.read_csv(target_file)
df_main['Year'] = df_main['Year'].astype(str)

print(f"既存データ: {len(df_main)}行")
print(f"既存データの期間: {df_main['Year'].min()} - {df_main['Year'].max()}")

# 2. 税率データを読み込む
tax_file = r"data/-2025ガソリン関連税四半期ごと/gasoline_tax_quarterly.csv"
print(f"\n{tax_file} を読み込み中...")

df_tax = pd.read_csv(tax_file, encoding='utf-8')

# Year_Quarter列からYearQuarter形式に変換（例: 2007-Q1 → 2007Q1）
df_tax['YearQuarter'] = df_tax['Year_Quarter'].str.replace('-', '')

# 実効従量税率_円Lを使用（消費税込みの実効税率）
df_tax_quarterly = df_tax[['YearQuarter', '実効従量税率_円L']].copy()
df_tax_quarterly.columns = ['YearQuarter', 'Effective_tax_rate_yen_per_liter']

print(f"税率データ: {len(df_tax_quarterly)}行")
print(f"税率データの期間: {df_tax_quarterly['YearQuarter'].min()} - {df_tax_quarterly['YearQuarter'].max()}")
print(f"税率データのYearQuarterサンプル: {df_tax_quarterly['YearQuarter'].head(10).tolist()}")

# 3. 1950年から1989年までの行を追加（まだ存在しない場合）
existing_years = set(df_main['Year'].unique())
needed_years = []
for year in range(1950, 1990):
    for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
        year_quarter = f"{year}{quarter}"
        if year_quarter not in existing_years:
            needed_years.append(year_quarter)

if needed_years:
    print(f"\n1950-1989年の欠けている行を追加: {len(needed_years)}行")
    new_rows = pd.DataFrame({
        'Year': needed_years,
        'Q (liters)': np.nan,
        'P (yen/liter)': np.nan,
        'Tax_rate (%)': np.nan,
        'GDP (trillion yen)': np.nan
    })
    df_main = pd.concat([new_rows, df_main], ignore_index=True)
    df_main = df_main.sort_values('Year').reset_index(drop=True)
    print(f"追加後の総行数: {len(df_main)}")

# 4. メインデータフレームにYearQuarter列を追加
df_main['YearQuarter'] = df_main['Year']
print(f"\nメインデータのYearQuarterサンプル: {df_main['YearQuarter'].head(10).tolist()}")

# YearQuarterの形式を統一
df_tax_quarterly['YearQuarter'] = df_tax_quarterly['YearQuarter'].astype(str).str.replace('.0', '')

print(f"\nデータをマージ中...")

# 税率データをマージ
df_main = df_main.merge(df_tax_quarterly[['YearQuarter', 'Effective_tax_rate_yen_per_liter']], 
                        on='YearQuarter', how='left')

# 5. 税率を%に変換（価格に対する%として）
# 価格がある期間：Tax_rate (%) = (実効従量税率_円L / 価格) * 100
# 価格がない期間：空欄のまま
df_main['Tax_rate (%)'] = np.nan
mask = df_main['Effective_tax_rate_yen_per_liter'].notna() & df_main['P (yen/liter)'].notna()
df_main.loc[mask, 'Tax_rate (%)'] = (df_main.loc[mask, 'Effective_tax_rate_yen_per_liter'] / 
                                      df_main.loc[mask, 'P (yen/liter)'] * 100).round(2)

# 既存のTax_rate (%)がある場合は上書きしない（既存データを優先）
existing_tax_mask = df_main['Tax_rate (%)'].notna() & (df_main['Tax_rate (%)'] != '')
# 既存のTax_rate (%)が数値でない場合は上書き
existing_tax_mask = existing_tax_mask & pd.to_numeric(df_main['Tax_rate (%)'], errors='coerce').notna()

# 既存のTax_rate (%)がない場合のみ、計算した値を設定
update_mask = mask & ~existing_tax_mask
df_main.loc[update_mask, 'Tax_rate (%)'] = (df_main.loc[update_mask, 'Effective_tax_rate_yen_per_liter'] / 
                                             df_main.loc[update_mask, 'P (yen/liter)'] * 100).round(2)

# 不要な列を削除
df_main = df_main.drop(columns=['Effective_tax_rate_yen_per_liter', 'YearQuarter'], errors='ignore')

# 6. 保存
df_main.to_csv(target_file, index=False, encoding='utf-8-sig')
print(f"\n{target_file} を更新しました")
print(f"最終データ行数: {len(df_main)}")

# 統計情報
print(f"\n=== 統計情報 ===")
print(f"データ期間: {df_main['Year'].min()} - {df_main['Year'].max()}")
print(f"\n各データの欠損状況:")
print(f"  Q (liters): {df_main['Q (liters)'].notna().sum()} / {len(df_main)}")
print(f"  P (yen/liter): {df_main['P (yen/liter)'].notna().sum()} / {len(df_main)}")
print(f"  Tax_rate (%): {df_main['Tax_rate (%)'].notna().sum()} / {len(df_main)}")
print(f"  GDP (trillion yen): {df_main['GDP (trillion yen)'].notna().sum()} / {len(df_main)}")

# 価格がある期間の税率計算状況
price_tax_mask = df_main['P (yen/liter)'].notna() & df_main['Tax_rate (%)'].notna()
print(f"\n価格データがある期間で税率が計算された行数: {price_tax_mask.sum()}")

# データサンプルを表示
print(f"\n最初の20行:")
print(df_main.head(20).to_string())

print(f"\n1950-1990年のサンプル（10行）:")
print(df_main[df_main['Year'].str.startswith(('1950', '1960', '1970', '1980', '1990'))].head(10).to_string())

print("\n完了しました！")

