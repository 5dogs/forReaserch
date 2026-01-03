"""
固定税額（従量税）と従価税率の比較シミュレーション

目的: 固定税額であることで、税率より値動きが穏やかであることを示す
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 日本語フォント設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.switch_backend('Agg')

print("="*60)
print("固定税額 vs 従価税率 シミュレーション")
print("="*60)

# ============================================================================
# 1. データの読み込み
# ============================================================================
print("\n1. データ読み込み中...")

# CPI寄与度分析結果から本体価格と固定税額を取得
cpi_file = 'analysis/results/04_cpi_contribution_analysis.csv'
df_cpi = pd.read_csv(cpi_file)
print(f"  - CPI分析データ: {len(df_cpi)}年分")

# 年次データから平均Tax_rate (%)を取得（仮想的な従価税率として使用）
annual_file = 'demand_regression_data_annual.csv'
df_annual = pd.read_csv(annual_file)
df_annual = df_annual[df_annual['Year'] >= 2007].copy()

# Tax_rate (%)の平均を計算（欠損値を除外）
avg_tax_rate = df_annual['Tax_rate (%)'].dropna().mean()
print(f"  - 平均Tax_rate (%): {avg_tax_rate:.2f}%")

# 必要な列を抽出
df = df_cpi[['Year', 'Price_Base', 'Gasoline_Tax_Amount']].copy()
df = df.dropna(subset=['Price_Base', 'Gasoline_Tax_Amount'])

print(f"  - 分析対象期間: {df['Year'].min():.0f} - {df['Year'].max():.0f}")
print(f"  - データ行数: {len(df)}行")

# ============================================================================
# 2. シミュレーション計算
# ============================================================================
print("\n2. シミュレーション計算中...")

# ケース1: 固定税額（現実）
df['Price_Case1_Fixed'] = df['Price_Base'] + df['Gasoline_Tax_Amount']
print(f"  - ケース1（固定税額）: 税込み価格 = 本体価格 + 固定税額")

# ケース2: 従価税率（仮想）
# 平均Tax_rate (%)を使用して仮想的な従価税率を設定
df['Price_Case2_AdValorem'] = df['Price_Base'] * (1 + avg_tax_rate / 100)
print(f"  - ケース2（従価税率）: 税込み価格 = 本体価格 × (1 + {avg_tax_rate:.2f}%)")

# 価格差を計算
df['Price_Difference'] = df['Price_Case2_AdValorem'] - df['Price_Case1_Fixed']

# ============================================================================
# 3. 統計指標の計算
# ============================================================================
print("\n3. 統計指標の計算中...")

# 変動係数（Coefficient of Variation）
cv_case1 = (df['Price_Case1_Fixed'].std() / df['Price_Case1_Fixed'].mean()) * 100
cv_case2 = (df['Price_Case2_AdValorem'].std() / df['Price_Case2_AdValorem'].mean()) * 100

# 標準偏差
std_case1 = df['Price_Case1_Fixed'].std()
std_case2 = df['Price_Case2_AdValorem'].std()

# 平均値
mean_case1 = df['Price_Case1_Fixed'].mean()
mean_case2 = df['Price_Case2_AdValorem'].mean()

print(f"\n  統計指標:")
print(f"    ケース1（固定税額）:")
print(f"      平均: {mean_case1:.2f}円/L")
print(f"      標準偏差: {std_case1:.2f}円/L")
print(f"      変動係数: {cv_case1:.2f}%")
print(f"    ケース2（従価税率）:")
print(f"      平均: {mean_case2:.2f}円/L")
print(f"      標準偏差: {std_case2:.2f}円/L")
print(f"      変動係数: {cv_case2:.2f}%")
print(f"    変動係数の差: {cv_case2 - cv_case1:.2f}ポイント")

# ============================================================================
# 4. グラフ作成
# ============================================================================
print("\n4. グラフ作成中...")

figures_dir = 'analysis/figures'
os.makedirs(figures_dir, exist_ok=True)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# 上段: 時系列比較
years = df['Year'].values
ax1.plot(years, df['Price_Case1_Fixed'].values, 
         label=f'Fixed Tax Amount (CV={cv_case1:.2f}%)', 
         linewidth=2, color='#2E86AB', marker='o', markersize=4)
ax1.plot(years, df['Price_Case2_AdValorem'].values, 
         label=f'Ad Valorem Tax Rate (CV={cv_case2:.2f}%)', 
         linewidth=2, color='#A23B72', marker='s', markersize=4, linestyle='--')

# 主要イベントのマーカー
if 2008 in years:
    ax1.axvline(x=2008, color='red', linestyle='--', linewidth=1, alpha=0.5, label='2008 Tax Expiration')
if 2009 in years:
    ax1.axvline(x=2009, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='2009 Financial Crisis')
if 2020 in years:
    ax1.axvline(x=2020, color='green', linestyle='--', linewidth=1, alpha=0.5, label='2020 COVID-19')

ax1.set_xlabel('Year', fontweight='bold', fontsize=11)
ax1.set_ylabel('Price (yen/L)', fontweight='bold', fontsize=11)
ax1.set_title('Comparison: Fixed Tax Amount vs Ad Valorem Tax Rate', fontweight='bold', fontsize=12)
ax1.legend(loc='best', fontsize=9)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_xlim(2006.5, 2025.5)

# 下段: 変動係数の比較
categories = ['Fixed Tax\nAmount', 'Ad Valorem\nTax Rate']
cv_values = [cv_case1, cv_case2]
colors = ['#2E86AB', '#A23B72']

bars = ax2.bar(categories, cv_values, color=colors, alpha=0.7, width=0.5)
ax2.set_ylabel('Coefficient of Variation (%)', fontweight='bold', fontsize=11)
ax2.set_title('Price Volatility Comparison: Coefficient of Variation', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

# 値をバーの上に表示
for bar, value in zip(bars, cv_values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{value:.2f}%',
             ha='center', va='bottom', fontweight='bold', fontsize=10)

# 差を表示
diff_text = f'Difference: {cv_case2 - cv_case1:.2f} percentage points'
ax2.text(0.5, 0.95, diff_text, transform=ax2.transAxes,
         ha='center', va='top', fontsize=10, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
output_file = f'{figures_dir}/09_fixed_vs_advalorem_tax_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"  - 保存: {output_file}")
plt.close()

# ============================================================================
# 5. 結果をCSVに保存
# ============================================================================
print("\n5. 結果をCSVに保存中...")

output_dir = 'analysis/results'
os.makedirs(output_dir, exist_ok=True)

# 結果データフレームを作成
df_result = df[['Year', 'Price_Base', 'Gasoline_Tax_Amount', 
                'Price_Case1_Fixed', 'Price_Case2_AdValorem', 'Price_Difference']].copy()

# 統計指標を追加
df_result['CV_Case1'] = cv_case1
df_result['CV_Case2'] = cv_case2
df_result['CV_Difference'] = cv_case2 - cv_case1
df_result['Avg_Tax_Rate_Pct'] = avg_tax_rate

result_file = f'{output_dir}/06_fixed_vs_advalorem_simulation.csv'
df_result.to_csv(result_file, index=False, encoding='utf-8-sig')
print(f"  - 保存: {result_file}")

print("\n" + "="*60)
print("シミュレーション完了！")
print("="*60)
print(f"\n出力ファイル:")
print(f"  - グラフ: {output_file}")
print(f"  - 結果CSV: {result_file}")
print(f"\n主な結果:")
print(f"  - 固定税額の変動係数: {cv_case1:.2f}%")
print(f"  - 従価税率の変動係数: {cv_case2:.2f}%")
print(f"  - 変動係数の差: {cv_case2 - cv_case1:.2f}ポイント")
print(f"  → 固定税額の方が値動きが{'穏やか' if cv_case1 < cv_case2 else '激しい'}")

