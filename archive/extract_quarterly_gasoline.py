import pandas as pd
import re
import os

# ファイルパス
file_path = r"data/-2024ガソリン販売量/統合.csv"

print("統合.csvから四半期ガソリン販売量データを抽出します...\n")

# CSVファイルを読み込む
df = pd.read_csv(file_path, encoding='utf-8', header=None)

# 年号から西暦への変換マッピング
era_to_year = {
    '平成': 1988,  # 平成1年 = 1989年なので、1988を基準にする
}

def convert_era_to_year(era, year_str):
    """年号と年文字列から西暦を計算"""
    if pd.isna(era) or pd.isna(year_str):
        return None
    
    era = str(era).strip()
    year_str = str(year_str).strip()
    
    # 年文字列から数字を抽出（例：「19年」→19）
    year_match = re.search(r'(\d+)', year_str)
    if not year_match:
        return None
    
    year_num = int(year_match.group(1))
    
    if era == '平成':
        return 1988 + year_num  # 平成19年 = 1988 + 19 = 2007
    
    return None

def extract_quarter(quarter_str):
    """四半期文字列から四半期番号を抽出"""
    if pd.isna(quarter_str):
        return None
    
    quarter_str = str(quarter_str).strip()
    
    # 「1～ 3月」→Q1, 「4～ 6」→Q2, 「7～ 9」→Q3, 「10～12」→Q4
    if '1～ 3月' in quarter_str or quarter_str.startswith('1～'):
        return 'Q1'
    elif '4～ 6' in quarter_str:
        return 'Q2'
    elif '7～ 9' in quarter_str:
        return 'Q3'
    elif '10～12' in quarter_str:
        return 'Q4'
    
    # 英語表記もチェック（Q1 2007, Q2, Q3, Q4）
    q_match = re.search(r'Q([1-4])', quarter_str, re.IGNORECASE)
    if q_match:
        return f"Q{q_match.group(1)}"
    
    return None

def clean_number(value):
    """数値文字列をクリーンアップ（カンマ、引用符を除去）"""
    if pd.isna(value):
        return None
    
    value_str = str(value).strip()
    # 引用符とカンマを除去
    value_str = value_str.replace('"', '').replace(',', '').replace('r', '').strip()
    
    # 数値以外の文字が含まれている場合はNoneを返す
    if not re.match(r'^-?\d+\.?\d*$', value_str):
        return None
    
    try:
        return float(value_str)
    except:
        return None

# 四半期データを抽出
quarterly_data = []
current_year = None  # 現在の年を保持

for idx, row in df.iterrows():
    # 列23にQ1, Q2, Q3, Q4が含まれている行を探す
    quarter_col = row[23] if len(row) > 23 else None
    
    # 年号と年を取得（年が明示されている場合）
    era = row[2] if len(row) > 2 else None
    year_str = row[3] if len(row) > 3 else None
    
    # 年が明示されている場合は更新
    if pd.notna(era) and pd.notna(year_str):
        calculated_year = convert_era_to_year(era, year_str)
        if calculated_year:
            current_year = calculated_year
    
    # 四半期情報を取得
    quarter_info = row[4] if len(row) > 4 else None
    
    # 四半期を抽出（列4または列23から）
    quarter = None
    if pd.notna(quarter_info):
        quarter = extract_quarter(quarter_info)
    if not quarter and pd.notna(quarter_col):
        quarter = extract_quarter(quarter_col)
    
    # 四半期が見つかった場合
    if quarter:
        # 四半期文字列から年を抽出（Q1 2007形式の場合）
        year_from_quarter = None
        if pd.notna(quarter_col):
            year_match = re.search(r'(\d{4})', str(quarter_col))
            if year_match:
                year_from_quarter = int(year_match.group(1))
        
        # 年を決定（優先順位: 四半期文字列 > 計算された年 > 現在の年）
        final_year = None
        if year_from_quarter:
            final_year = year_from_quarter
            current_year = year_from_quarter  # 更新
        elif current_year:
            final_year = current_year
        
        # ガソリン販売量を取得（列7）
        gasoline_kl = row[7] if len(row) > 7 else None
        gasoline_kl_clean = clean_number(gasoline_kl)
        
        if final_year and gasoline_kl_clean:
            # リットルに変換（1kl = 1000リットル）
            gasoline_liters = gasoline_kl_clean * 1000
            
            quarterly_data.append({
                'Year': final_year,
                'Quarter': quarter,
                'YearQuarter': f"{final_year}{quarter}",
                'Gasoline_kl': gasoline_kl_clean,
                'Gasoline_liters': gasoline_liters,
                'Row': idx + 1,
                'Era': era,
                'YearStr': year_str,
                'QuarterInfo': quarter_info,
                'QuarterCol': quarter_col
            })

# DataFrameに変換
df_quarterly = pd.DataFrame(quarterly_data)

# 重複を除去（同じYearQuarterが複数ある場合、最初のものを使用）
df_quarterly = df_quarterly.drop_duplicates(subset=['YearQuarter'], keep='first')

# YearとQuarterでソート
df_quarterly = df_quarterly.sort_values(['Year', 'Quarter']).reset_index(drop=True)

print(f"抽出された四半期データ: {len(df_quarterly)}件\n")
print("最初の20件:")
print(df_quarterly[['Year', 'Quarter', 'YearQuarter', 'Gasoline_kl', 'Gasoline_liters']].head(20).to_string())
print(f"\n最後の10件:")
print(df_quarterly[['Year', 'Quarter', 'YearQuarter', 'Gasoline_kl', 'Gasoline_liters']].tail(10).to_string())

# 統計情報
print(f"\n=== 統計情報 ===")
print(f"期間: {df_quarterly['Year'].min()}年 - {df_quarterly['Year'].max()}年")
print(f"四半期数: {len(df_quarterly)}")
print(f"ガソリン販売量（kl）: 最小={df_quarterly['Gasoline_kl'].min():,.0f}, 最大={df_quarterly['Gasoline_kl'].max():,.0f}, 平均={df_quarterly['Gasoline_kl'].mean():,.0f}")

# demand_regression_data_raw.csvの形式に合わせて出力
output_data = []
for _, row in df_quarterly.iterrows():
    output_data.append({
        'Year': f"{int(row['Year'])}{row['Quarter']}",
        'Q (liters)': int(row['Gasoline_liters']),
        'P (yen/liter)': '',
        'Tax_rate (%)': '',
        'GDP (trillion yen)': ''
    })

df_output = pd.DataFrame(output_data)

# 既存のdemand_regression_data_raw.csvを読み込んで、ガソリン販売量を更新
existing_file = 'demand_regression_data_raw.csv'
if os.path.exists(existing_file):
    df_existing = pd.read_csv(existing_file)
    
    # Year列をキーにしてマージ
    df_existing = df_existing.set_index('Year')
    df_output = df_output.set_index('Year')
    
    # ガソリン販売量を更新（既存データがある場合は上書き、ない場合は追加）
    df_existing['Q (liters)'] = df_output['Q (liters)'].combine_first(df_existing['Q (liters)'])
    
    # 新しいデータ（2007-2008年など）を追加
    new_rows = df_output[~df_output.index.isin(df_existing.index)]
    if len(new_rows) > 0:
        # 新しい行を既存のDataFrameに追加
        for idx, row in new_rows.iterrows():
            df_existing.loc[idx] = {
                'Q (liters)': row['Q (liters)'],
                'P (yen/liter)': '',
                'Tax_rate (%)': '',
                'GDP (trillion yen)': ''
            }
    
    # インデックスをリセット
    df_existing = df_existing.reset_index()
    
    # ソート
    df_existing = df_existing.sort_values('Year').reset_index(drop=True)
    
    # 保存
    df_existing.to_csv(existing_file, index=False, encoding='utf-8-sig')
    print(f"\n{existing_file} を更新しました")
    print(f"更新された行数: {len(df_existing)}")
    print(f"追加された新しいデータ: {len(new_rows)}件")
else:
    # 新規作成
    df_output = df_output.reset_index()
    df_output.to_csv(existing_file, index=False, encoding='utf-8-sig')
    print(f"\n{existing_file} を新規作成しました")

# 詳細データも保存（デバッグ用）
df_quarterly.to_csv('gasoline_quarterly_extracted.csv', index=False, encoding='utf-8-sig')
print(f"詳細データを 'gasoline_quarterly_extracted.csv' に保存しました")

print("\n完了しました！")

