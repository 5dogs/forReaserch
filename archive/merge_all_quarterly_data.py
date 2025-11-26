import pandas as pd
import re
import os
from datetime import datetime

print("四半期データを統合します...\n")

# 1. 既存のdemand_regression_data_raw.csvを読み込む
target_file = 'demand_regression_data_raw.csv'
df_main = pd.read_csv(target_file)
df_main['Year'] = df_main['Year'].astype(str)

print(f"既存データ: {len(df_main)}行")

# 2. ガソリン関連税データを読み込む
tax_file = r"data/-2025ガソリン関連税四半期ごと/gasoline_tax_quarterly.csv"
print(f"\n{tax_file} を読み込み中...")
df_tax = pd.read_csv(tax_file, encoding='utf-8')

# Year_Quarter列からYearQuarter形式に変換（例: 2007-Q1 → 2007Q1）
df_tax['YearQuarter'] = df_tax['Year_Quarter'].str.replace('-', '')
# 実効従量税率_円Lを使用（消費税込みの実効税率）
df_tax = df_tax[['YearQuarter', '実効従量税率_円L']].copy()
df_tax.columns = ['YearQuarter', 'Tax_rate_yen_per_liter']

# 税率を%に変換（合計従量税率は円/Lなので、価格に対する%として計算する必要があるが、
# ここでは単純に税率として扱う。実際のTax_rate (%)は別途計算が必要）
# とりあえず、合計従量税率をそのまま使用（後で価格で割って%にする）

print(f"税データ: {len(df_tax)}行")
print(f"税データのYearQuarterサンプル: {df_tax['YearQuarter'].head(10).tolist()}")

# 3. ガソリン小売価格データを読み込む
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
df_price_quarterly['YearQuarter'] = df_price_quarterly['Year'].astype(str) + df_price_quarterly['Quarter']
df_price_quarterly = df_price_quarterly[['YearQuarter', '全国平均']].copy()
df_price_quarterly.columns = ['YearQuarter', 'Price_yen_per_liter']

print(f"価格データ（四半期平均）: {len(df_price_quarterly)}行")
print(f"価格データのYearQuarterサンプル: {df_price_quarterly['YearQuarter'].head(10).tolist()}")

# 4. GDPデータを読み込む
gdp_file = r"data/1994-2025_GDP四半期ごと/gaku-jg2522.csv"
print(f"\n{gdp_file} を読み込み中...")

# GDPデータは複雑な構造なので、行を確認しながら読み込む
df_gdp_raw = pd.read_csv(gdp_file, encoding='utf-8', skiprows=7)

# 最初の列（四半期、インデックス0）と2列目（GDP、インデックス1）を取得
df_gdp = pd.DataFrame()
df_gdp['Quarter_str'] = df_gdp_raw.iloc[:, 0].astype(str)
# GDP列の値をクリーンアップ（カンマ、引用符、空白を除去）
gdp_values = df_gdp_raw.iloc[:, 1].astype(str).str.replace(',', '').str.replace('"', '').str.strip()
df_gdp['GDP_billions'] = pd.to_numeric(gdp_values, errors='coerce')

# 四半期文字列から年と四半期を抽出（例: "1994/ 1- 3" → 1994, Q1）
def parse_gdp_quarter(quarter_str, current_year=None):
    """GDP四半期文字列をパース"""
    if pd.isna(quarter_str) or quarter_str == 'nan':
        return None, None
    
    # パターン1: "1994/ 1- 3." または "1994/1-3" (年が含まれる)
    match = re.match(r'(\d{4})/\s*(\d+)\s*-\s*(\d+)', str(quarter_str))
    if match:
        year = int(match.group(1))
        start_month = int(match.group(2))
        quarter = (start_month - 1) // 3 + 1
        return year, f"Q{quarter}"
    
    # パターン2: "4- 6." または "4-6" (年が省略されている)
    match = re.match(r'(\d+)\s*-\s*(\d+)', str(quarter_str))
    if match and current_year:
        start_month = int(match.group(1))
        quarter = (start_month - 1) // 3 + 1
        return current_year, f"Q{quarter}"
    
    return None, None

# 年を引き継ぎながらパース
current_year = None
years = []
quarters = []
for quarter_str in df_gdp['Quarter_str']:
    year, quarter = parse_gdp_quarter(quarter_str, current_year)
    if year:
        current_year = year
        years.append(year)
        quarters.append(quarter)
    else:
        years.append(None)
        quarters.append(None)

df_gdp['Year'] = years
df_gdp['Quarter'] = quarters
df_gdp = df_gdp.dropna(subset=['Year', 'Quarter', 'GDP_billions'])

# 10億円を兆円に変換
df_gdp['GDP_trillion'] = df_gdp['GDP_billions'] / 1000

df_gdp_quarterly = df_gdp[['Year', 'Quarter', 'GDP_trillion']].copy()
df_gdp_quarterly['YearQuarter'] = df_gdp_quarterly['Year'].astype(str) + df_gdp_quarterly['Quarter']
df_gdp_quarterly = df_gdp_quarterly[['YearQuarter', 'GDP_trillion']].copy()

print(f"GDPデータ: {len(df_gdp_quarterly)}行")
print(f"GDPデータのYearQuarterサンプル: {df_gdp_quarterly['YearQuarter'].head(10).tolist()}")

# 5. すべてのデータをマージ
# メインデータフレームにYearQuarter列を追加
df_main['YearQuarter'] = df_main['Year']
print(f"\nメインデータのYearQuarterサンプル: {df_main['YearQuarter'].head(10).tolist()}")

# YearQuarterの形式を統一（小数点を除去）
df_price_quarterly['YearQuarter'] = df_price_quarterly['YearQuarter'].astype(str).str.replace('.0', '')
df_gdp_quarterly['YearQuarter'] = df_gdp_quarterly['YearQuarter'].astype(str).str.replace('.0', '')

print(f"\nデータをマージ中...")

# 税データをマージ
df_main = df_main.merge(df_tax[['YearQuarter', 'Tax_rate_yen_per_liter']], 
                        on='YearQuarter', how='left')

# 価格データをマージ
df_main = df_main.merge(df_price_quarterly[['YearQuarter', 'Price_yen_per_liter']], 
                        on='YearQuarter', how='left')

# GDPデータをマージ
df_main = df_main.merge(df_gdp_quarterly[['YearQuarter', 'GDP_trillion']], 
                        on='YearQuarter', how='left')

# 6. 税率を%に変換（価格に対する%として）
# Tax_rate (%) = (合計従量税率 / 価格) * 100
# 価格と税率の両方が存在する場合のみ計算
df_main['Tax_rate (%)'] = None
mask = df_main['Tax_rate_yen_per_liter'].notna() & df_main['Price_yen_per_liter'].notna()
df_main.loc[mask, 'Tax_rate (%)'] = (df_main.loc[mask, 'Tax_rate_yen_per_liter'] / 
                                      df_main.loc[mask, 'Price_yen_per_liter'] * 100).round(2)

# 7. 列を整理
df_output = pd.DataFrame()
df_output['Year'] = df_main['Year']
df_output['Q (liters)'] = df_main['Q (liters)']
df_output['P (yen/liter)'] = df_main['Price_yen_per_liter'].round(1)
df_output['Tax_rate (%)'] = df_main['Tax_rate (%)']
df_output['GDP (trillion yen)'] = df_main['GDP_trillion'].round(2)

# 8. 保存
df_output.to_csv(target_file, index=False, encoding='utf-8-sig')
print(f"\n{target_file} を更新しました")
print(f"最終データ行数: {len(df_output)}")

# 統計情報
print(f"\n=== 統計情報 ===")
print(f"データ期間: {df_output['Year'].min()} - {df_output['Year'].max()}")
print(f"\n各データの欠損状況:")
print(f"  Q (liters): {df_output['Q (liters)'].notna().sum()} / {len(df_output)}")
print(f"  P (yen/liter): {df_output['P (yen/liter)'].notna().sum()} / {len(df_output)}")
print(f"  Tax_rate (%): {df_output['Tax_rate (%)'].notna().sum()} / {len(df_output)}")
print(f"  GDP (trillion yen): {df_output['GDP (trillion yen)'].notna().sum()} / {len(df_output)}")

# データサンプルを表示
print(f"\n最初の10行:")
print(df_output.head(10).to_string())

print("\n完了しました！")

