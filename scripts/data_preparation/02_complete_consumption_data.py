"""
既存データから欠損しているQ (liters)データを補完するスクリプト
data/2007-2024ガソリン販売量/四半期データ_まとめ.csvから
2015Q2-2018Q4と2020Q2-2023Q4のデータをマージ
"""

import pandas as pd
import numpy as np

print("既存データからQ (liters)の欠損を補完します...\n")

# 1. メインデータを読み込む
target_file = 'demand_regression_data_raw.csv'
df_main = pd.read_csv(target_file)
df_main['Year'] = df_main['Year'].astype(str)

print(f"メインデータ: {len(df_main)}行")
print(f"現在のQ (liters)データ数: {df_main['Q (liters)'].notna().sum()}行")

# 2. 四半期データを読み込む
consumption_file = r"data/2007-2024ガソリン販売量/四半期データ_まとめ.csv"
print(f"\n{consumption_file} を読み込み中...")

df_consumption = pd.read_csv(consumption_file, encoding='utf-8')

# YearとQuarterからYearQuarter形式を作成（例: 2009Q1）
# Quarter列が文字列の場合、'Q1'のような形式になっている可能性がある
if 'Quarter' in df_consumption.columns:
    # Quarter列が'Q1'形式の場合
    if df_consumption['Quarter'].dtype == object and df_consumption['Quarter'].str.startswith('Q').any():
        df_consumption['YearQuarter'] = df_consumption['Year'].astype(str) + df_consumption['Quarter'].astype(str)
    else:
        df_consumption['YearQuarter'] = df_consumption['Year'].astype(str) + 'Q' + df_consumption['Quarter'].astype(str)
else:
    print("エラー: Quarter列が見つかりません")

# Q (liters)の単位を確認
# 既存データを確認：2007Q1は10億リットル単位、2014Q2以降はリットル単位の可能性
existing_q_2007 = pd.to_numeric(df_main[df_main['Year'] == '2007Q1']['Q (liters)'].values[0], errors='coerce')
existing_q_2014q2 = pd.to_numeric(df_main[df_main['Year'] == '2014Q2']['Q (liters)'].values[0], errors='coerce')

df_consumption['Q_liters'] = pd.to_numeric(df_consumption['Q (liters)'], errors='coerce')

# 2014Q2以降のデータはリットル単位の可能性が高い
# 補完対象期間（2015Q2以降、2020Q2以降）に合わせて単位を決定
if pd.notna(existing_q_2014q2) and existing_q_2014q2 < 100000000:  # 1億未満ならリットル単位
    # 2014Q2以降はリットル単位なので、そのまま使用
    print(f"2014Q2以降のデータ単位を確認: {existing_q_2014q2} (リットル単位と判断)")
    print("四半期データはリットル単位のまま使用します")
else:
    # 2007Q1の単位に合わせる（10億リットル単位）
    if pd.notna(existing_q_2007) and existing_q_2007 > 1000000000:
        df_consumption['Q_liters'] = df_consumption['Q_liters'] * 1000
        print(f"既存データの単位を確認: {existing_q_2007} (10億リットル単位と判断)")
        print("四半期データを10億リットル単位に変換しました（1000倍）")

print(f"四半期データ: {len(df_consumption)}行")
print(f"四半期データの期間: {df_consumption['YearQuarter'].min()} - {df_consumption['YearQuarter'].max()}")
print(f"\n四半期データのサンプル:")
print(df_consumption[['YearQuarter', 'Q (liters)']].head(10))

# 3. メインデータにYearQuarter列を追加
df_main['YearQuarter'] = df_main['Year']

# 4. マージ前の欠損状況を確認
# Q (liters)が欠損している、または'-'などの文字列になっている行を確認
df_main['Q_numeric'] = pd.to_numeric(df_main['Q (liters)'], errors='coerce')
missing_before = df_main[(df_main['Q_numeric'].isna()) & 
                        (df_main['YearQuarter'].isin(df_consumption['YearQuarter']))].copy()
print(f"\n補完可能な欠損データ: {len(missing_before)}行")
if len(missing_before) > 0:
    print("補完対象期間:")
    print(missing_before[['YearQuarter', 'Q (liters)', 'P (yen/liter)', 'Tax_rate (%)', 'GDP (trillion yen)']].head(20).to_string())

# 5. 四半期データをマージ（Q (liters)が欠損している行のみ更新）
# 既存のQ (liters)がある場合は上書きしない
df_consumption_merge = df_consumption[['YearQuarter', 'Q_liters']].copy()

# マージ（左結合）
df_main = df_main.merge(df_consumption_merge, on='YearQuarter', how='left')

# Q (liters)が欠損している、または'-'などの文字列になっている場合のみ、マージしたデータで補完
# 既存のQ (liters)を数値に変換して確認
df_main['Q_existing'] = pd.to_numeric(df_main['Q (liters)'], errors='coerce')
mask_missing = df_main['Q_existing'].isna() & df_main['Q_liters'].notna()
df_main.loc[mask_missing, 'Q (liters)'] = df_main.loc[mask_missing, 'Q_liters']

# 不要な列を削除
df_main = df_main.drop(columns=['Q_liters', 'YearQuarter', 'Q_numeric', 'Q_existing'], errors='ignore')

# 6. 補完後の状況を確認
print(f"\n補完後のQ (liters)データ数: {df_main['Q (liters)'].notna().sum()}行")
print(f"補完された行数: {mask_missing.sum()}行")

# 補完されたデータを表示
if mask_missing.sum() > 0:
    print(f"\n補完されたデータ:")
    completed = df_main[mask_missing].copy()
    print(completed[['Year', 'Q (liters)', 'P (yen/liter)', 'Tax_rate (%)', 'GDP (trillion yen)']].to_string())

# 7. 2014Q2のデータ単位を確認・修正
print(f"\n2014Q2のデータを確認中...")
row_2014q2 = df_main[df_main['Year'] == '2014Q2'].iloc[0]
if pd.notna(row_2014q2['Q (liters)']):
    q_value = pd.to_numeric(row_2014q2['Q (liters)'], errors='coerce')
    print(f"現在の値: {q_value}")
    # 他のデータと比較（例: 2014Q1は13196561000）
    q_2014q1_val = df_main[df_main['Year'] == '2014Q1']['Q (liters)'].values[0]
    q_2014q1 = pd.to_numeric(q_2014q1_val, errors='coerce')
    if pd.notna(q_2014q1) and pd.notna(q_value):
        print(f"2014Q1の値: {q_2014q1}")
        # 2014Q2が異常に小さい場合は、単位が間違っている可能性
        if q_value < q_2014q1 / 100:  # 100分の1以下なら単位が間違っている可能性
            print(f"警告: 2014Q2の値が異常に小さいです。単位を確認してください。")
            print(f"修正案: {q_value * 1000} (1000倍) または {q_value * 1000000} (1000000倍)")
            # 四半期データから正しい値を取得
            q_correct = df_consumption[df_consumption['YearQuarter'] == '2014Q2']['Q (liters)'].values
            if len(q_correct) > 0:
                print(f"四半期データからの値: {q_correct[0]}")
                # 四半期データの値で更新
                df_main.loc[df_main['Year'] == '2014Q2', 'Q (liters)'] = q_correct[0]
                print(f"2014Q2の値を修正しました: {q_correct[0]}")

# 8. データの統計情報
print(f"\n=== 補完後の統計情報 ===")
print(f"データ期間: {df_main['Year'].min()} - {df_main['Year'].max()}")
print(f"\n各データの欠損状況:")
print(f"  Q (liters): {df_main['Q (liters)'].notna().sum()} / {len(df_main)} ({df_main['Q (liters)'].notna().sum()/len(df_main)*100:.1f}%)")
print(f"  P (yen/liter): {df_main['P (yen/liter)'].notna().sum()} / {len(df_main)} ({df_main['P (yen/liter)'].notna().sum()/len(df_main)*100:.1f}%)")
print(f"  Tax_rate (%): {df_main['Tax_rate (%)'].notna().sum()} / {len(df_main)} ({df_main['Tax_rate (%)'].notna().sum()/len(df_main)*100:.1f}%)")
print(f"  GDP (trillion yen): {df_main['GDP (trillion yen)'].notna().sum()} / {len(df_main)} ({df_main['GDP (trillion yen)'].notna().sum()/len(df_main)*100:.1f}%)")

# 全変数が揃っている期間
df_complete = df_main[df_main['Q (liters)'].notna() & 
                      df_main['P (yen/liter)'].notna() & 
                      df_main['Tax_rate (%)'].notna() & 
                      df_main['GDP (trillion yen)'].notna()]
print(f"\n全変数が揃っている期間: {len(df_complete)}行")
if len(df_complete) > 0:
    print(f"期間: {df_complete['Year'].min()} - {df_complete['Year'].max()}")

# 9. 保存
df_main.to_csv(target_file, index=False, encoding='utf-8-sig')
print(f"\n{target_file} を更新しました")
print("完了しました！")

