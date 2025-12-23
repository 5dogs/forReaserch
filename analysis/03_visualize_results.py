"""
分析結果の可視化スクリプト
需要関数の推定結果と消費者余剰の計算結果を可視化

研究用グラフ（英語、シンプル、PNG形式）を作成します。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
import os

# 出力ディレクトリ
output_dir = 'analysis/results'
figures_dir = 'analysis/figures'
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
print("分析結果の可視化")
print("="*60)

# 1. データの読み込み
print("\nデータを読み込み中...")

# 需要関数の係数（年次データ版）
with open(f'{output_dir}/01_coefficients_annual_level_model.json', 'r', encoding='utf-8') as f:
    coefficients = json.load(f)

# 分析データ（年次データ版）
df_analysis = pd.read_csv(f'{output_dir}/01_analysis_data_annual_level_model.csv')

# 消費者余剰の結果
df_cs = pd.read_csv(f'{output_dir}/02_consumer_surplus_results.csv')

# Yearをdatetimeに変換（年次データの場合）
def year_to_date(year_str):
    """Convert '2007' to datetime (January 1st of that year)"""
    try:
        year = int(str(year_str)[:4])
        return pd.Timestamp(year=year, month=1, day=1)
    except:
        return pd.NaT

def year_quarter_to_date(year_quarter_str):
    """Convert '2007Q2' to datetime"""
    try:
        year_str = str(year_quarter_str)
        if 'Q' in year_str:
            year = int(year_str[:4])
            quarter = int(year_str[year_str.index('Q')+1])
            month = (quarter - 1) * 3 + 1
            return pd.Timestamp(year=year, month=month, day=1)
        else:
            # 年次データの場合
            year = int(year_str[:4])
            return pd.Timestamp(year=year, month=1, day=1)
    except:
        return pd.NaT

# 年次データか四半期データかを判定
# Year列を文字列に変換してから判定
df_analysis['Year'] = df_analysis['Year'].astype(str)
if 'YearQuarter' in df_analysis.columns or df_analysis['Year'].str.contains('Q', na=False).any():
    # 四半期データの場合
    df_analysis['Date'] = df_analysis['Year'].apply(year_quarter_to_date)
    if 'Year' in df_cs.columns:
        df_cs['Year'] = df_cs['Year'].astype(str)
        df_cs['Date'] = df_cs['Year'].apply(year_quarter_to_date)
else:
    # 年次データの場合
    df_analysis['Date'] = df_analysis['Year'].apply(year_to_date)
    if 'Year' in df_cs.columns:
        df_cs['Year'] = df_cs['Year'].astype(str)
        df_cs['Date'] = df_cs['Year'].apply(year_to_date)

print(f"分析期間: {df_analysis['Year'].min()} - {df_analysis['Year'].max()}")

# ============================================================================
# Graph 1: 需要関数の推定結果（係数の可視化）
# ============================================================================
print("\nCreating Graph 1: Demand Function Coefficients...")
fig, ax = plt.subplots(figsize=(12, 6))

# 弾力性係数
coeff_names = ['Income\nElasticity (α)', 'Price\nElasticity (β)', 'Tax Rate\nElasticity (γ)']
coeff_values = [coefficients['alpha'], coefficients['beta'], coefficients['gamma']]
colors = ['#2E86AB', '#A23B72', '#06A77D']

# ダミー変数の係数（2008→2009→2020の順）
dummy_names = []
dummy_values = []
dummy_colors = []
dummy_labels = {'D2008': 'δ₁ (D2008)', 'D2009': 'δ₂ (D2009)', 'D2020': 'δ₃ (D2020)'}
dummy_color_map = {'D2008': '#F18F01', 'D2009': '#C73E1D', 'D2020': '#6A994E'}

# 順番を2008→2009→2020に統一
dummy_order = ['D2008', 'D2009', 'D2020']
if 'dummy_variables' in coefficients:
    for dummy_var in dummy_order:
        if dummy_var in coefficients['dummy_variables']:
            dummy_names.append(dummy_labels[dummy_var])
            dummy_values.append(coefficients['dummy_variables'][dummy_var])
            dummy_colors.append(dummy_color_map[dummy_var])

# すべての係数を結合
all_names = coeff_names + dummy_names
all_values = coeff_values + dummy_values
all_colors = colors + dummy_colors

bars = ax.bar(all_names, all_values, color=all_colors, alpha=0.7, edgecolor='black', linewidth=1)

# 値をバーの上に表示
for bar, val in zip(bars, all_values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.4f}',
            ha='center', va='bottom' if height > 0 else 'top', fontweight='bold', fontsize=8)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_ylabel('Coefficient Value', fontweight='bold')
ax.set_title('Estimated Demand Function Coefficients', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(f'{figures_dir}/01_demand_function_coefficients.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {figures_dir}/01_demand_function_coefficients.png")
plt.close()

# ============================================================================
# Graph 2: 消費者余剰の増分推移
# ============================================================================
print("\nCreating Graph 2: Consumer Surplus Increase Trend...")
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(df_cs['Date'], df_cs['CS_Increase'] / 1e12, 
        linewidth=1.5, color='#2E86AB', marker='o', markersize=3)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# 重要な政策イベントをマーカー（年次データの場合）
policy_events = {
    '2008': {'label': 'Temporary Tax Rate\nTemporarily Expired', 'color': 'red'},
    '2009': {'label': 'Financial Crisis', 'color': 'orange'},
    '2020': {'label': 'COVID-19\nPandemic', 'color': 'red'},
}

for event_date_str, event_info in policy_events.items():
    event_date = year_quarter_to_date(event_date_str)
    if not pd.isna(event_date) and event_date >= df_cs['Date'].min():
        ax.axvline(x=event_date, color=event_info['color'], 
                  linestyle='--', linewidth=1, alpha=0.7)
        ax.text(event_date, ax.get_ylim()[1] * 0.95, event_info['label'],
               rotation=90, verticalalignment='top', horizontalalignment='right',
               fontsize=8, color=event_info['color'])

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Consumer Surplus Increase (trillion yen)', fontweight='bold')
ax.set_title('Consumer Surplus Increase Trend (Annual)', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_minor_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{figures_dir}/02_consumer_surplus_increase.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {figures_dir}/02_consumer_surplus_increase.png")
plt.close()

# ============================================================================
# Graph 3: 累積消費者余剰の推移
# ============================================================================
print("\nCreating Graph 3: Cumulative Consumer Surplus Trend...")
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(df_cs['Date'], df_cs['Cumulative_CS'] / 1e12, 
        linewidth=2, color='#A23B72', marker='s', markersize=3)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# 政策イベントのマーカー
for event_date_str, event_info in policy_events.items():
    event_date = year_quarter_to_date(event_date_str)
    if not pd.isna(event_date) and event_date >= df_cs['Date'].min():
        ax.axvline(x=event_date, color=event_info['color'], 
                  linestyle='--', linewidth=1, alpha=0.7)

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Cumulative Consumer Surplus (trillion yen)', fontweight='bold')
ax.set_title('Cumulative Consumer Surplus Trend', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_minor_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{figures_dir}/03_cumulative_consumer_surplus.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {figures_dir}/03_cumulative_consumer_surplus.png")
plt.close()

# ============================================================================
# Graph 4: 需要関数の推定結果（回帰診断）- 削除：論文内で使用しないため
# ============================================================================
print("\nSkipping Graph 4 (Regression Diagnostics): Not used in the paper")

print("\n" + "="*60)
print("All graphs created successfully!")
print(f"Output directory: {figures_dir}/")
print("Note: Graph 4 (Price vs Surplus) and Graph 5 (Regression Diagnostics) were removed.")
print("="*60)

