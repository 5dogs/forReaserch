"""
追加のグラフ作成スクリプト（税率除外版）
1. 本体価格と税込み価格の変動係数の比較
2. 政策イベント別の影響の分解
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# スクリプトのディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # analysis/ の親ディレクトリ

# 出力ディレクトリ
output_dir = os.path.join(project_root, 'analysis', 'results', 'excl_tax')
figures_dir = os.path.join(project_root, 'analysis', 'figures', 'excl_tax')
os.makedirs(figures_dir, exist_ok=True)

# グラフのスタイル設定（学術論文向け）
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

print("="*60)
print("追加グラフの作成（税率除外版）")
print("="*60)

# ============================================================================
# グラフ1: 本体価格と税込み価格の変動係数の比較
# ============================================================================
print("\n1. 変動係数の比較グラフを作成中...")

# CPI寄与度分析データを読み込み
cpi_file = os.path.join(output_dir, '04_cpi_contribution_analysis.csv')
df_cpi = pd.read_csv(cpi_file)

# 変動係数を計算
cv_base = (df_cpi['Price_Base'].std() / df_cpi['Price_Base'].mean()) * 100
cv_tax_inclusive = (df_cpi['Price_TaxInclusive'].std() / df_cpi['Price_TaxInclusive'].mean()) * 100

print(f"  本体価格の変動係数: {cv_base:.2f}%")
print(f"  税込み価格の変動係数: {cv_tax_inclusive:.2f}%")

# グラフ作成
fig, ax = plt.subplots(figsize=(8, 6))

categories = ['Base Price\n(Tax-Exclusive)', 'Tax-Inclusive Price']
cv_values = [cv_base, cv_tax_inclusive]
colors = ['#2E86AB', '#A23B72']

bars = ax.bar(categories, cv_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

# 値をバーの上に表示
for bar, val in zip(bars, cv_values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.2f}%',
            ha='center', va='bottom', fontweight='bold', fontsize=11)

# 比率を表示
ratio = cv_base / cv_tax_inclusive
ax.text(0.5, 0.95, f'Ratio: {ratio:.2f}x',
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        horizontalalignment='center')

ax.set_ylabel('Coefficient of Variation (%)', fontweight='bold')
ax.set_title('Price Volatility Comparison:\nBase Price vs Tax-Inclusive Price', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--', axis='y')
ax.set_ylim(0, max(cv_values) * 1.2)

plt.tight_layout()
plt.savefig(os.path.join(figures_dir, '07_coefficient_of_variation_comparison.png'), dpi=300, bbox_inches='tight')
print(f"  保存: {os.path.join(figures_dir, '07_coefficient_of_variation_comparison.png')}")
plt.close()

# ============================================================================
# グラフ2: 政策イベント別の影響の分解
# ============================================================================
print("\n2. 政策イベント別の影響の分解グラフを作成中...")

# 消費者余剰データを読み込み
cs_file = os.path.join(output_dir, '02_consumer_surplus_results.csv')
df_cs = pd.read_csv(cs_file)

# 政策イベントの年を指定
policy_years = [2008, 2009, 2020]
policy_labels = ['2008 Temporary\nTax Rate Expiration', '2009 Financial\nCrisis', '2020 COVID-19\nPandemic']

# 各イベントのデータを抽出
event_data = []
for year in policy_years:
    year_data = df_cs[df_cs['Year'] == year]
    if len(year_data) > 0:
        row = year_data.iloc[0]
        event_data.append({
            'Year': year,
            'Price_Change': row['ΔP'],  # 円/L
            'CS_Change': row['CS_Increase'] / 1e12,  # 兆円
            'Label': policy_labels[policy_years.index(year)]
        })

df_events = pd.DataFrame(event_data)
print(f"  抽出したイベント数: {len(df_events)}")

# グラフ作成（2軸）
fig, ax1 = plt.subplots(figsize=(12, 6))

x_pos = np.arange(len(df_events))
width = 0.35

# 左軸: 価格変化（円/L）
bars1 = ax1.bar(x_pos - width/2, df_events['Price_Change'], width,
                label='Price Change (yen/L)', color='#2E86AB', alpha=0.7, edgecolor='black', linewidth=1)

# 右軸: 消費者余剰変化（兆円）
ax2 = ax1.twinx()
bars2 = ax2.bar(x_pos + width/2, df_events['CS_Change'], width,
                label='Consumer Surplus Change (trillion yen)', color='#A23B72', alpha=0.7, edgecolor='black', linewidth=1)

# 値をバーの上に表示（重ならないように調整）
for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    # 価格変化
    height1 = bar1.get_height()
    # 正の値は上に、負の値は下に配置し、余白を追加
    offset1 = abs(height1) * 0.1 + 1.0  # 値の10% + 固定オフセット
    y_pos1 = height1 + offset1 if height1 > 0 else height1 - offset1
    ax1.text(bar1.get_x() + bar1.get_width()/2., y_pos1,
             f'{height1:.1f}',
             ha='center', va='bottom' if height1 > 0 else 'top', 
             fontweight='bold', fontsize=9, color='#2E86AB')
    
    # 消費者余剰変化
    height2 = bar2.get_height()
    # 正の値は上に、負の値は下に配置し、余白を追加
    offset2 = abs(height2) * 0.1 + 0.05  # 値の10% + 固定オフセット
    y_pos2 = height2 + offset2 if height2 > 0 else height2 - offset2
    ax2.text(bar2.get_x() + bar2.get_width()/2., y_pos2,
             f'{height2:.2f}',
             ha='center', va='bottom' if height2 > 0 else 'top',
             fontweight='bold', fontsize=9, color='#A23B72')

# ゼロライン
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# 軸ラベルとタイトル
ax1.set_xlabel('Policy Event', fontweight='bold')
ax1.set_ylabel('Price Change (yen/L)', fontweight='bold', color='#2E86AB')
ax2.set_ylabel('Consumer Surplus Change (trillion yen)', fontweight='bold', color='#A23B72')
ax1.set_title('Policy Event Impact Decomposition:\nPrice Change vs Consumer Surplus Change', fontweight='bold')

# X軸のラベル
ax1.set_xticks(x_pos)
ax1.set_xticklabels(df_events['Label'], rotation=0)

# 凡例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# グリッド
ax1.grid(True, alpha=0.3, linestyle='--', axis='y')

# Y軸の範囲を調整して文字が収まるようにする
y1_min, y1_max = ax1.get_ylim()
y2_min, y2_max = ax2.get_ylim()
# 上下に20%の余白を追加
ax1.set_ylim(y1_min * 1.3, y1_max * 1.3)
ax2.set_ylim(y2_min * 1.3, y2_max * 1.3)

plt.tight_layout()
plt.savefig(os.path.join(figures_dir, '08_policy_event_impact_decomposition.png'), dpi=300, bbox_inches='tight')
print(f"  保存: {os.path.join(figures_dir, '08_policy_event_impact_decomposition.png')}")
plt.close()

print("\n" + "="*60)
print("追加グラフの作成完了！")
print("="*60)
print(f"\n出力ファイル:")
print(f"  - {figures_dir}/07_coefficient_of_variation_comparison.png")
print(f"  - {figures_dir}/08_policy_event_impact_decomposition.png")

