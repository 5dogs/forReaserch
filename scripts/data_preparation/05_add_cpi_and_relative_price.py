"""
CPIデータをメインデータにマージし、相対価格を計算するスクリプト
"""

import pandas as pd
import numpy as np
import os

print("="*60)
print("CPIデータのマージと相対価格の計算")
print("="*60)

# 1. CPI四半期データの読み込み
cpi_file = 'data/-2025消費者物価指数/CPI_quarterly.csv'
if not os.path.exists(cpi_file):
    print(f"エラー: {cpi_file} が見つかりません。")
    print("先に 04_process_cpi_data.py を実行してください。")
    exit(1)

print(f"\nCPI四半期データを読み込み中: {cpi_file}")
df_cpi = pd.read_csv(cpi_file, encoding='utf-8-sig')
print(f"CPIデータ数: {len(df_cpi)}")
print(f"CPI期間: {df_cpi['YearQuarter'].min()} - {df_cpi['YearQuarter'].max()}")

# 2. メインデータの読み込み
main_file = 'demand_regression_data_raw.csv'
if not os.path.exists(main_file):
    print(f"エラー: {main_file} が見つかりません。")
    exit(1)

print(f"\nメインデータを読み込み中: {main_file}")
df_main = pd.read_csv(main_file, encoding='utf-8-sig')
print(f"メインデータ数: {len(df_main)}")

# 3. YearQuarter列の作成（メインデータにない場合）
if 'YearQuarter' not in df_main.columns:
    if 'Year' in df_main.columns:
        # Year列が「1950Q1」形式の場合、そのまま使用
        if df_main['Year'].dtype == 'object' and df_main['Year'].str.contains('Q', na=False).any():
            df_main['YearQuarter'] = df_main['Year'].astype(str)
        elif 'Quarter' in df_main.columns:
            df_main['YearQuarter'] = df_main['Year'].astype(str) + 'Q' + df_main['Quarter'].astype(str)
        else:
            print("エラー: Year列の形式が不明です。")
            exit(1)
    else:
        print("エラー: Year列が見つかりません。")
        exit(1)

# 4. CPIデータのマージ
print("\nCPIデータをマージ中...")
df_merged = df_main.merge(
    df_cpi[['YearQuarter', 'CPI']],
    on='YearQuarter',
    how='left'
)

print(f"マージ後のデータ数: {len(df_merged)}")
print(f"CPIがマージされたデータ数: {df_merged['CPI'].notna().sum()}")

# 5. 相対価格の計算
print("\n相対価格を計算中...")
# 相対価格 = ガソリン小売価格 / 消費者物価指数
df_merged['P_relative'] = df_merged['P (yen/liter)'] / df_merged['CPI']

print(f"相対価格が計算されたデータ数: {df_merged['P_relative'].notna().sum()}")

# 6. データの確認
print("\n" + "="*60)
print("マージ結果の確認")
print("="*60)
print("\nCPIがマージされた期間:")
cpi_merged = df_merged[df_merged['CPI'].notna()].copy()
if len(cpi_merged) > 0:
    print(f"  期間: {cpi_merged['YearQuarter'].min()} - {cpi_merged['YearQuarter'].max()}")
    print(f"  データ数: {len(cpi_merged)}")
    
    print("\n最初の5行（CPIと相対価格）:")
    print(cpi_merged[['YearQuarter', 'P (yen/liter)', 'CPI', 'P_relative']].head().to_string())
    
    print("\n最後の5行（CPIと相対価格）:")
    print(cpi_merged[['YearQuarter', 'P (yen/liter)', 'CPI', 'P_relative']].tail().to_string())
    
    print("\n相対価格の統計:")
    print(f"  平均: {cpi_merged['P_relative'].mean():.4f}")
    print(f"  最小値: {cpi_merged['P_relative'].min():.4f}")
    print(f"  最大値: {cpi_merged['P_relative'].max():.4f}")
    print(f"  標準偏差: {cpi_merged['P_relative'].std():.4f}")

# 7. データの保存
output_file = 'demand_regression_data_raw.csv'
print(f"\nマージ済みデータを保存中: {output_file}")
df_merged.to_csv(output_file, index=False, encoding='utf-8-sig')
print("保存完了！")

# 8. 次のステップの案内
print("\n" + "="*60)
print("次のステップ")
print("="*60)
print("1. 対数変換済みデータを再作成:")
print("   python scripts/data_preparation/00_prepare_log_transformed_data.py")
print("\n2. レベルモデルで再推定（相対価格使用）:")
print("   python analysis/01_estimate_demand_function_level_model.py")
print("\n3. 相対価格を使用した推定式:")
print("   ln(Q) = C + α×ln(GDP) + β×ln(P_relative) + γ×ln(Tax_rate) + ε")

print("\n完了しました！")

