import pandas as pd
import numpy as np

# CSVファイルを読み込む
df = pd.read_csv('gasoline_tax_quarterly.csv', encoding='utf-8')

print("="*80)
print("データ検証レポート")
print("="*80)

# 1. 合計従量税率の計算検証
print("\n1. 合計従量税率の計算検証")
df['合計従量税率_計算値'] = (
    df['揮発油税_本則_円L'] + 
    df['地方揮発油税_本則_円L'] + 
    df['揮発油税_暫定_円L'] + 
    df['地方揮発油税_暫定_円L'] + 
    df['石油石炭税_円L']
)
df['合計従量税率_差分'] = abs(df['合計従量税率_円L'] - df['合計従量税率_計算値'])
max_diff = df['合計従量税率_差分'].max()
print(f"  最大差分: {max_diff:.10f}")
if max_diff > 0.01:
    print("  ⚠️ 警告: 合計従量税率の計算に不一致があります")
    print(df[df['合計従量税率_差分'] > 0.01][['Year', 'Quarter', '合計従量税率_円L', '合計従量税率_計算値', '合計従量税率_差分']])
else:
    print("  ✓ 合計従量税率の計算は正しいです")

# 2. 実効従量税率の計算検証
print("\n2. 実効従量税率の計算検証")
df['実効従量税率_計算値'] = df['合計従量税率_円L'] * (1 + df['消費税率_%'] / 100)
df['実効従量税率_差分'] = abs(df['実効従量税率_円L'] - df['実効従量税率_計算値'])
max_diff_effective = df['実効従量税率_差分'].max()
print(f"  最大差分: {max_diff_effective:.10f}")
if max_diff_effective > 0.01:
    print("  ⚠️ 警告: 実効従量税率の計算に不一致があります")
    print(df[df['実効従量税率_差分'] > 0.01][['Year', 'Quarter', '実効従量税率_円L', '実効従量税率_計算値', '実効従量税率_差分']])
else:
    print("  ✓ 実効従量税率の計算は正しいです")

# 3. 主要な変遷ポイントの確認
print("\n3. 主要な変遷ポイントの確認")
print("\n  消費税率の変遷:")
consumption_tax_changes = df[df['消費税率_%'].diff() != 0][['Year', 'Quarter', 'Year_Quarter', '消費税率_%', '合計従量税率_円L', '実効従量税率_円L']]
print(consumption_tax_changes.to_string(index=False))

print("\n  石油石炭税の変遷:")
petroleum_tax_changes = df[df['石油石炭税_円L'].diff() != 0][['Year', 'Quarter', 'Year_Quarter', '石油石炭税_円L', '合計従量税率_円L', '実効従量税率_円L']]
print(petroleum_tax_changes.to_string(index=False))

print("\n  暫定税率の変遷:")
provisional_tax_changes = df[df['揮発油税_暫定_円L'].diff() != 0][['Year', 'Quarter', 'Year_Quarter', '揮発油税_暫定_円L', '地方揮発油税_暫定_円L', '合計従量税率_円L']]
print(provisional_tax_changes.to_string(index=False))

# 4. 特定の年のデータ確認
print("\n4. 特定の年のデータ確認")
test_years = [1974, 1989, 1997, 2003, 2008, 2012, 2014, 2019, 2025]
for year in test_years:
    year_data = df[df['Year'] == year]
    if len(year_data) > 0:
        print(f"\n  {year}年:")
        print(f"    合計従量税率: {year_data['合計従量税率_円L'].values[0]:.2f}円/L")
        print(f"    消費税率: {year_data['消費税率_%'].values[0]:.1f}%")
        print(f"    実効従量税率: {year_data['実効従量税率_円L'].values[0]:.2f}円/L")
        # 手計算で検証
        manual_effective = year_data['合計従量税率_円L'].values[0] * (1 + year_data['消費税率_%'].values[0] / 100)
        print(f"    手計算値: {manual_effective:.2f}円/L")
        if abs(year_data['実効従量税率_円L'].values[0] - manual_effective) > 0.01:
            print(f"    ⚠️ 不一致: {abs(year_data['実効従量税率_円L'].values[0] - manual_effective):.6f}")

# 5. データの統計情報
print("\n5. データの統計情報")
print(f"  データ期間: {df['Year'].min()}年Q{df[df['Year']==df['Year'].min()]['Quarter'].min()} 〜 {df['Year'].max()}年Q{df[df['Year']==df['Year'].max()]['Quarter'].max()}")
print(f"  総データ数: {len(df)}件")
print(f"\n  合計従量税率の範囲: {df['合計従量税率_円L'].min():.2f} 〜 {df['合計従量税率_円L'].max():.2f}円/L")
print(f"  実効従量税率の範囲: {df['実効従量税率_円L'].min():.2f} 〜 {df['実効従量税率_円L'].max():.2f}円/L")
print(f"  消費税率の範囲: {df['消費税率_%'].min():.1f} 〜 {df['消費税率_%'].max():.1f}%")
print(f"  石油石炭税の範囲: {df['石油石炭税_円L'].min():.2f} 〜 {df['石油石炭税_円L'].max():.2f}円/L")

# 6. 異常値のチェック
print("\n6. 異常値のチェック")
# 負の値がないか
negative_values = df[(df['揮発油税_本則_円L'] < 0) | (df['地方揮発油税_本則_円L'] < 0) | 
                     (df['揮発油税_暫定_円L'] < 0) | (df['地方揮発油税_暫定_円L'] < 0) |
                     (df['石油石炭税_円L'] < 0) | (df['消費税率_%'] < 0)]
if len(negative_values) > 0:
    print("  ⚠️ 警告: 負の値が見つかりました")
    print(negative_values[['Year', 'Quarter', '揮発油税_本則_円L', '地方揮発油税_本則_円L', '揮発油税_暫定_円L', '地方揮発油税_暫定_円L', '石油石炭税_円L', '消費税率_%']])
else:
    print("  ✓ 負の値はありません")

# 消費税率が0-10%の範囲内か
invalid_consumption_tax = df[(df['消費税率_%'] < 0) | (df['消費税率_%'] > 10)]
if len(invalid_consumption_tax) > 0:
    print("  ⚠️ 警告: 消費税率が範囲外です")
    print(invalid_consumption_tax[['Year', 'Quarter', '消費税率_%']])
else:
    print("  ✓ 消費税率は0-10%の範囲内です")

print("\n" + "="*80)
print("検証完了")
print("="*80)

