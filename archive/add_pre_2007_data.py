import pandas as pd
import re
from datetime import datetime

print("2007年以前のデータを追加します...\n")

# 1. 既存のdemand_regression_data_raw.csvを読み込む
target_file = 'demand_regression_data_raw.csv'
df_main = pd.read_csv(target_file)
df_main['Year'] = df_main['Year'].astype(str)

print(f"既存データ: {len(df_main)}行")
print(f"既存データの期間: {df_main['Year'].min()} - {df_main['Year'].max()}")

# 2. ガソリン関連税データを読み込む（1990年から）
tax_file = r"data/-2025ガソリン関連税四半期ごと/gasoline_tax_quarterly.csv"
print(f"\n{tax_file} を読み込み中...")
df_tax = pd.read_csv(tax_file, encoding='utf-8')
df_tax['YearQuarter'] = df_tax['Year_Quarter'].str.replace('-', '')
df_tax = df_tax[['YearQuarter', '実効従量税率_円L']].copy()
df_tax.columns = ['YearQuarter', 'Tax_rate_yen_per_liter']

# 2007年以前の税データを抽出
df_tax_pre2007 = df_tax[df_tax['YearQuarter'].str[:4].astype(int) < 2007].copy()
print(f"2007年以前の税データ: {len(df_tax_pre2007)}行")

# 3. ガソリン小売価格データを読み込む（1990年から）
price_file = r"data/1990-2025_ガソリン小売価格四半期ごと/1990-2025レギュラー現金価格.csv"
print(f"\n{price_file} を読み込み中...")

df_price_raw = pd.read_csv(price_file, encoding='utf-8', skiprows=2)
df_price = pd.DataFrame()
df_price['調査日'] = df_price_raw.iloc[:, 1]
df_price['全国平均'] = pd.to_numeric(df_price_raw.iloc[:, 2], errors='coerce')

def extract_year_quarter(date_str):
    """日付文字列から年と四半期を抽出"""
    if pd.isna(date_str):
        return None, None
    try:
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

# 2007年以前の価格データを抽出
df_price_pre2007 = df_price_quarterly[df_price_quarterly['YearQuarter'].str[:4].astype(int) < 2007].copy()
print(f"2007年以前の価格データ: {len(df_price_pre2007)}行")

# 4. GDPデータを読み込む（1994年から）
gdp_file = r"data/1994-2025_GDP四半期ごと/gaku-jg2522.csv"
print(f"\n{gdp_file} を読み込み中...")

df_gdp_raw = pd.read_csv(gdp_file, encoding='utf-8', skiprows=7)
df_gdp = pd.DataFrame()
df_gdp['Quarter_str'] = df_gdp_raw.iloc[:, 0].astype(str)
gdp_values = df_gdp_raw.iloc[:, 1].astype(str).str.replace(',', '').str.replace('"', '').str.strip()
df_gdp['GDP_billions'] = pd.to_numeric(gdp_values, errors='coerce')

def parse_gdp_quarter(quarter_str, current_year=None):
    """GDP四半期文字列をパース"""
    if pd.isna(quarter_str) or quarter_str == 'nan':
        return None, None
    
    match = re.match(r'(\d{4})/\s*(\d+)\s*-\s*(\d+)', str(quarter_str))
    if match:
        year = int(match.group(1))
        start_month = int(match.group(2))
        quarter = (start_month - 1) // 3 + 1
        return year, f"Q{quarter}"
    
    match = re.match(r'(\d+)\s*-\s*(\d+)', str(quarter_str))
    if match and current_year:
        start_month = int(match.group(1))
        quarter = (start_month - 1) // 3 + 1
        return current_year, f"Q{quarter}"
    
    return None, None

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
df_gdp['GDP_trillion'] = df_gdp['GDP_billions'] / 1000

df_gdp_quarterly = df_gdp[['Year', 'Quarter', 'GDP_trillion']].copy()
df_gdp_quarterly['YearQuarter'] = df_gdp_quarterly['Year'].astype(str) + df_gdp_quarterly['Quarter']
df_gdp_quarterly = df_gdp_quarterly[['YearQuarter', 'GDP_trillion']].copy()

# 2007年以前のGDPデータを抽出
df_gdp_pre2007 = df_gdp_quarterly[df_gdp_quarterly['YearQuarter'].str[:4].astype(int) < 2007].copy()
print(f"2007年以前のGDPデータ: {len(df_gdp_pre2007)}行")

# 5. ガソリン販売量データを確認（統合.csvから2007年以前の年次データを取得）
sales_file = r"data/2007-2024ガソリン販売量/統合.csv"
print(f"\n{sales_file} を確認中...")

df_sales_raw = pd.read_csv(sales_file, header=None, encoding='utf-8')

# 2007年以前の年次データを抽出（平成15-18年 = 2003-2006年）
sales_pre2007 = {}
heisei_to_year = {15: 2003, 16: 2004, 17: 2005, 18: 2006}

for idx, row in df_sales_raw.iterrows():
    # 行をリストに変換（NaNも含める）
    row_list = [v if pd.notna(v) else '' for v in row.values]
    if len(row_list) < 10:
        continue
    
    # 最後の列にC.Y.が含まれているか確認
    last_col = str(row_list[-1]) if row_list else ""
    if 'C.Y.' not in last_col:
        continue
    
    # 平成年を探す（列2: "平成", 列3: "15年"など）
    heisei = None
    if len(row_list) > 3:
        col2 = str(row_list[2]) if row_list[2] != '' else ''
        col3 = str(row_list[3]) if row_list[3] != '' else ''
        
        if '平成' in col2 and len(col3) > 0:
            # 列3から年を抽出（例: "15年" → 15）
            match = re.search(r'(\d+)', col3)
            if match:
                heisei = int(match.group(1))
    
    if heisei and heisei in heisei_to_year:
        year = heisei_to_year[heisei]
        # ガソリン列は列7（インデックス7）
        if len(row_list) > 7:
            gasoline_str = str(row_list[7]).replace(',', '').replace('"', '').strip()
            # 数値チェック
            try:
                gasoline_kl = float(gasoline_str)
                if 50000000 < gasoline_kl < 70000000:  # 有効な値かチェック（5000万-7000万kl）
                    sales_pre2007[year] = gasoline_kl * 1000  # kl to liters
                    print(f"  {year}年の年次ガソリン販売量: {gasoline_kl:,.0f} kl = {sales_pre2007[year]:,.0f} liters")
            except (ValueError, TypeError):
                pass

print(f"\n2007年以前の年次ガソリン販売量データ: {len(sales_pre2007)}年分")

# 6. 2007年以前の四半期データを作成
# すべての四半期のYearQuarterを生成（1994年から2006年まで、GDPデータがある期間）
all_quarters = []
for year in range(1994, 2007):
    for quarter in [1, 2, 3, 4]:
        all_quarters.append(f"{year}Q{quarter}")

df_new = pd.DataFrame({'YearQuarter': all_quarters})
df_new['Year'] = df_new['YearQuarter']

# ガソリン販売量：年次データを4等分（簡易的な方法）
df_new['Q (liters)'] = None
for year in sales_pre2007:
    annual_sales = sales_pre2007[year]
    # 年次データを4等分（季節変動を考慮しない簡易的な方法）
    quarterly_sales = annual_sales / 4
    for q in [1, 2, 3, 4]:
        df_new.loc[df_new['YearQuarter'] == f"{year}Q{q}", 'Q (liters)'] = int(quarterly_sales)

# YearQuarterの形式を統一（文字列型に変換）
df_new['YearQuarter'] = df_new['YearQuarter'].astype(str)
df_tax_pre2007['YearQuarter'] = df_tax_pre2007['YearQuarter'].astype(str)
df_price_pre2007['YearQuarter'] = df_price_pre2007['YearQuarter'].astype(str)
df_gdp_pre2007['YearQuarter'] = df_gdp_pre2007['YearQuarter'].astype(str)

# 価格、税率、GDPをマージ
df_new = df_new.merge(df_tax_pre2007[['YearQuarter', 'Tax_rate_yen_per_liter']], 
                      on='YearQuarter', how='left')
df_new = df_new.merge(df_price_pre2007[['YearQuarter', 'Price_yen_per_liter']], 
                      on='YearQuarter', how='left')
df_new = df_new.merge(df_gdp_pre2007[['YearQuarter', 'GDP_trillion']], 
                      on='YearQuarter', how='left')

# 税率を%に変換
df_new['Tax_rate (%)'] = None
mask = df_new['Tax_rate_yen_per_liter'].notna() & df_new['Price_yen_per_liter'].notna()
df_new.loc[mask, 'Tax_rate (%)'] = (df_new.loc[mask, 'Tax_rate_yen_per_liter'] / 
                                    df_new.loc[mask, 'Price_yen_per_liter'] * 100).round(2)

# 7. 新しいデータを整理
df_new_output = pd.DataFrame()
df_new_output['Year'] = df_new['Year']
df_new_output['Q (liters)'] = df_new['Q (liters)']
df_new_output['P (yen/liter)'] = df_new['Price_yen_per_liter'].round(1)
df_new_output['Tax_rate (%)'] = df_new['Tax_rate (%)']
df_new_output['GDP (trillion yen)'] = df_new['GDP_trillion'].round(2)

# 8. 既存データと結合（2007年以前のデータを先頭に追加）
df_output = pd.concat([df_new_output, df_main], ignore_index=True)

# 9. 保存
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
print(f"\n最初の10行（2007年以前）:")
print(df_output.head(10).to_string())
print(f"\n2007年付近のデータ:")
print(df_output[df_output['Year'].str[:4].astype(int).between(2006, 2008)].to_string())

print("\n完了しました！")

