import pandas as pd
import numpy as np

print("1990年からの価格データを追加します...\n")

# 1. 既存のdemand_regression_data_raw.csvを読み込む
target_file = 'demand_regression_data_raw.csv'
df_main = pd.read_csv(target_file)
df_main['Year'] = df_main['Year'].astype(str)

print(f"既存データ: {len(df_main)}行")
print(f"既存データの期間: {df_main['Year'].min()} - {df_main['Year'].max()}")

# 2. 価格データを読み込む
price_file = r"data/1990-2025_ガソリン小売価格四半期ごと/1990-2025レギュラー現金価格.csv"
print(f"\n{price_file} を読み込み中...")

# 価格データは週次なので、四半期ごとに平均を取る必要がある
df_price_raw = pd.read_csv(price_file, encoding='utf-8', skiprows=2)

# 調査日列（列1、インデックス1）と全国平均価格列（列2、インデックス2）を取得
df_price = pd.DataFrame()
df_price['調査日'] = df_price_raw.iloc[:, 1]  # 調査日（列1）
df_price['全国平均'] = pd.to_numeric(df_price_raw.iloc[:, 2], errors='coerce')  # 全国平均価格（列2）

# 調査日から年と四半期を抽出
def extract_year_quarter(date_str):
    """日付文字列から年と四半期を抽出"""
    if pd.isna(date_str):
        return None, None
    
    try:
        # 日付をパース
        date = pd.to_datetime(date_str, format='%Y/%m/%d', errors='coerce')
        if pd.isna(date):
            return None, None
        
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        return year, f"Q{quarter}"
    except:
        return None, None

df_price['Year'], df_price['Quarter'] = zip(*df_price['調査日'].apply(extract_year_quarter))
df_price = df_price.dropna(subset=['Year', 'Quarter', '全国平均'])

# 四半期ごとに平均価格を計算
df_price_quarterly = df_price.groupby(['Year', 'Quarter'])['全国平均'].mean().reset_index()
# Yearを整数型に変換してから文字列に
df_price_quarterly['Year'] = df_price_quarterly['Year'].astype(int)
df_price_quarterly['YearQuarter'] = df_price_quarterly['Year'].astype(str) + df_price_quarterly['Quarter']
df_price_quarterly = df_price_quarterly[['YearQuarter', '全国平均']].copy()
df_price_quarterly.columns = ['YearQuarter', 'Price_yen_per_liter']

print(f"価格データ（四半期平均）: {len(df_price_quarterly)}行")
print(f"価格データの期間: {df_price_quarterly['YearQuarter'].min()} - {df_price_quarterly['YearQuarter'].max()}")
print(f"価格データのYearQuarterサンプル: {df_price_quarterly['YearQuarter'].head(10).tolist()}")

# 3. 1990年から1993年までの行を追加（まだ存在しない場合）
existing_years = set(df_main['Year'].unique())
needed_years = []
for year in range(1990, 1994):
    for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
        year_quarter = f"{year}{quarter}"
        if year_quarter not in existing_years:
            needed_years.append(year_quarter)

if needed_years:
    print(f"\n1990-1993年の欠けている行を追加: {len(needed_years)}行")
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
df_price_quarterly['YearQuarter'] = df_price_quarterly['YearQuarter'].astype(str).str.replace('.0', '')

print(f"\nデータをマージ中...")

# 価格データをマージ
df_main = df_main.merge(df_price_quarterly[['YearQuarter', 'Price_yen_per_liter']], 
                        on='YearQuarter', how='left')

# 価格列を更新（既存の価格列があれば上書き、なければ新規作成）
df_main['P (yen/liter)'] = df_main['Price_yen_per_liter'].round(1)

# 不要な列を削除
df_main = df_main.drop(columns=['Price_yen_per_liter', 'YearQuarter'], errors='ignore')

# 5. 保存
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

# データサンプルを表示
print(f"\n最初の20行:")
print(df_main.head(20).to_string())

print("\n完了しました！")

