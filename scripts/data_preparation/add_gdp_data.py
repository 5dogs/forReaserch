import pandas as pd
import re

print("GDPデータを追加します...\n")

# 1. 既存のdemand_regression_data_raw.csvを読み込む
target_file = 'demand_regression_data_raw.csv'
df_main = pd.read_csv(target_file)
df_main['Year'] = df_main['Year'].astype(str)

print(f"既存データ: {len(df_main)}行")

# 2. GDPデータを読み込む
gdp_file = r"data/1994-2025_GDP四半期ごと/gaku-jg2522.csv"
print(f"\n{gdp_file} を読み込み中...")

# 複数のエンコーディングとskiprowsの組み合わせを試す
encodings = ['utf-8', 'shift-jis', 'cp932', 'latin-1']
skiprows_options = [6, 7, 8]
df_gdp_raw = None
used_encoding = None
used_skiprows = None

for enc in encodings:
    for skip in skiprows_options:
        try:
            test_df = pd.read_csv(gdp_file, encoding=enc, skiprows=skip, nrows=3)
            if len(test_df) > 0:
                first_row = str(test_df.iloc[0, 0])
                # 1994年のデータが最初に来るか確認
                if '1994' in first_row and '1- 3' in first_row:
                    df_gdp_raw = pd.read_csv(gdp_file, encoding=enc, skiprows=skip)
                    used_encoding = enc
                    used_skiprows = skip
                    print(f"エンコーディング '{enc}', skiprows={skip} で読み込み成功 (最初の行: {first_row[:40]})")
                    break
        except (UnicodeDecodeError, UnicodeError, Exception) as e:
            continue
    if df_gdp_raw is not None:
        break

if df_gdp_raw is None:
    # フォールバック: デフォルト設定で読み込み
    try:
        df_gdp_raw = pd.read_csv(gdp_file, encoding='utf-8', skiprows=7)
        used_encoding = 'utf-8'
        used_skiprows = 7
        print(f"フォールバック: エンコーディング 'utf-8', skiprows=7 で読み込み")
    except:
        raise ValueError("GDPファイルの読み込みに失敗しました。")

# 最初の列（四半期、インデックス0）と2列目（GDP、インデックス1）を取得
df_gdp = pd.DataFrame()
df_gdp['Quarter_str'] = df_gdp_raw.iloc[:, 0].astype(str)

# GDP列の値をクリーンアップ（カンマ、引用符、空白を除去）
gdp_values = df_gdp_raw.iloc[:, 1].astype(str).str.replace(',', '').str.replace('"', '').str.strip()
df_gdp['GDP_billions'] = pd.to_numeric(gdp_values, errors='coerce')

# 四半期文字列から年と四半期を抽出（例: "1994/ 1- 3." → 1994, Q1）
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
# 最初の行が年を含まない場合は、1994年から始まると仮定
current_year = None
years = []
quarters = []

# 最初の行を確認
first_row = df_gdp['Quarter_str'].iloc[0] if len(df_gdp) > 0 else None
print(f"最初の行: '{first_row}'")
first_year, first_quarter = parse_gdp_quarter(first_row, None)

if first_year:
    current_year = first_year
    print(f"最初の年を検出: {current_year} ({first_quarter})")
else:
    # 最初の行が年を含まない場合は、1994年から始まると仮定
    # これは1994年のデータが最初に来る場合に適用される
    current_year = 1994
    print(f"最初の行が年を含まないため、デフォルトで{current_year}年を使用")

for idx, quarter_str in enumerate(df_gdp['Quarter_str']):
    year, quarter = parse_gdp_quarter(quarter_str, current_year)
    if year:
        current_year = year
        years.append(year)
        quarters.append(quarter)
    else:
        years.append(None)
        quarters.append(None)
    
    # デバッグ: 最初の10行を表示
    if idx < 10:
        print(f"  行{idx}: '{quarter_str}' -> Year={year}, Quarter={quarter}")

df_gdp['Year'] = years
df_gdp['Quarter'] = quarters
df_gdp = df_gdp.dropna(subset=['Year', 'Quarter', 'GDP_billions'])

# 10億円を兆円に変換
df_gdp['GDP_trillion'] = df_gdp['GDP_billions'] / 1000

df_gdp_quarterly = df_gdp[['Year', 'Quarter', 'GDP_trillion']].copy()
# Yearを整数型に変換してから文字列に
df_gdp_quarterly['Year'] = df_gdp_quarterly['Year'].astype(int)
df_gdp_quarterly['YearQuarter'] = df_gdp_quarterly['Year'].astype(str) + df_gdp_quarterly['Quarter']
df_gdp_quarterly = df_gdp_quarterly[['YearQuarter', 'GDP_trillion']].copy()

print(f"GDPデータ: {len(df_gdp_quarterly)}行")
print(f"GDPデータのYearQuarterサンプル: {df_gdp_quarterly['YearQuarter'].head(10).tolist()}")

# 3. メインデータフレームにYearQuarter列を追加
df_main['YearQuarter'] = df_main['Year']
print(f"\nメインデータのYearQuarterサンプル: {df_main['YearQuarter'].head(10).tolist()}")

# YearQuarterの形式を統一（既に文字列なのでそのまま）

print(f"\nデータをマージ中...")

# GDPデータをマージ
df_main = df_main.merge(df_gdp_quarterly[['YearQuarter', 'GDP_trillion']], 
                        on='YearQuarter', how='left')

# GDP列を更新（既存のGDP列があれば上書き、なければ新規作成）
# マージで重複が発生した場合は、最初の値を使用
df_main['GDP (trillion yen)'] = df_main['GDP_trillion'].round(2)

# 重複行を削除（Year列で重複している場合、最初の行を保持）
df_main = df_main.drop_duplicates(subset=['Year'], keep='first')

# 不要な列を削除
df_main = df_main.drop(columns=['GDP_trillion', 'YearQuarter'], errors='ignore')

# 4. 保存
df_main.to_csv(target_file, index=False, encoding='utf-8-sig')
print(f"\n{target_file} を更新しました")
print(f"最終データ行数: {len(df_main)}")

# 統計情報
print(f"\n=== 統計情報 ===")
print(f"データ期間: {df_main['Year'].min()} - {df_main['Year'].max()}")
print(f"\nGDPデータの欠損状況:")
print(f"  GDP (trillion yen): {df_main['GDP (trillion yen)'].notna().sum()} / {len(df_main)}")

# データサンプルを表示
print(f"\n最初の10行:")
print(df_main.head(10).to_string())

print("\n完了しました！")

