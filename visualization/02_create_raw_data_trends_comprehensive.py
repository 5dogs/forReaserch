"""
Raw Data Comprehensive Trends Visualization
生データ（ガソリン価格、相対価格、GDP、CPI）の推移グラフを作成

作成するグラフ:
1. ガソリン価格と相対価格の推移（2軸）
2. GDPとCPIの推移（2軸）
3. 統合グラフ（すべての変数を表示）
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import os

# Set style for academic papers
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

# Create output directory
output_dir = 'visualization/figures'
os.makedirs(output_dir, exist_ok=True)

print("="*60)
print("Raw Data Comprehensive Trends Visualization")
print("="*60)

# Load data
print("\n1. データの読み込み中...")
data_file = 'demand_regression_data_raw.csv'
if not os.path.exists(data_file):
    data_file = '../demand_regression_data_raw.csv'

df = pd.read_csv(data_file, encoding='utf-8-sig')
df['Year'] = df['Year'].astype(str)

# Convert Year to datetime for plotting
def year_quarter_to_date(year_quarter_str):
    """Convert '1990Q3' to datetime"""
    try:
        year = int(year_quarter_str[:4])
        quarter = int(year_quarter_str[5])
        month = (quarter - 1) * 3 + 1
        return pd.Timestamp(year=year, month=month, day=1)
    except:
        return pd.NaT

df['Date'] = df['Year'].apply(year_quarter_to_date)
df = df.sort_values('Date').reset_index(drop=True)

# Filter data from 2007 onwards
df = df[df['Date'] >= pd.Timestamp(year=2007, month=1, day=1)].reset_index(drop=True)

# Convert numeric columns
df['P (yen/liter)'] = pd.to_numeric(df['P (yen/liter)'], errors='coerce')
df['P_relative'] = pd.to_numeric(df['P_relative'], errors='coerce')
df['GDP (trillion yen)'] = pd.to_numeric(df['GDP (trillion yen)'], errors='coerce')
df['CPI'] = pd.to_numeric(df['CPI'], errors='coerce')

print(f"  データ行数: {len(df)}")
print(f"  データ期間: {df['Date'].min()} から {df['Date'].max()}")

# Define important policy events
policy_events = {
    '2008Q2': {'label': '2008Q2\n暫定税率失効', 'color': 'red'},
    '2009Q1': {'label': '2009Q1\n金融危機', 'color': 'orange'},
    '2020Q2': {'label': '2020Q2\nCOVID-19', 'color': 'purple'},
}

# ============================================================================
# Graph 1: ガソリン価格と相対価格の推移
# ============================================================================
print("\n2. グラフ1: ガソリン価格と相対価格の推移を作成中...")

# Filter data with both price and relative price
df_price = df[(df['P (yen/liter)'].notna()) & (df['P_relative'].notna())].copy()

if len(df_price) > 0:
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Left axis: ガソリン価格（円/L）
    color1 = '#2E86AB'
    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Gasoline Price (yen/liter)', fontweight='bold', color=color1)
    line1 = ax1.plot(df_price['Date'], df_price['P (yen/liter)'], 
                     linewidth=2, color=color1, marker='o', markersize=4, 
                     label='Gasoline Price (yen/L)', alpha=0.8)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Right axis: 相対価格
    ax2 = ax1.twinx()
    color2 = '#A23B72'
    ax2.set_ylabel('Relative Price (P/CPI)', fontweight='bold', color=color2)
    line2 = ax2.plot(df_price['Date'], df_price['P_relative'], 
                     linewidth=2, color=color2, marker='s', markersize=4, 
                     label='Relative Price (P/CPI)', linestyle='--', alpha=0.8)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Add policy event markers
    for event_date_str, event_info in policy_events.items():
        event_date = year_quarter_to_date(event_date_str)
        if not pd.isna(event_date) and event_date >= df_price['Date'].min():
            ax1.axvline(x=event_date, color=event_info['color'], 
                       linestyle=':', linewidth=1.5, alpha=0.6)
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=9)
    
    ax1.set_title('Gasoline Price and Relative Price Trends', fontweight='bold')
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_minor_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/05_gasoline_price_and_relative_price_trends.png', 
                dpi=300, bbox_inches='tight')
    print(f"  保存: {output_dir}/05_gasoline_price_and_relative_price_trends.png")
    plt.close()

# ============================================================================
# Graph 2: GDPとCPIの推移
# ============================================================================
print("\n3. グラフ2: GDPとCPIの推移を作成中...")

# Filter data with both GDP and CPI
df_macro = df[(df['GDP (trillion yen)'].notna()) & (df['CPI'].notna())].copy()

if len(df_macro) > 0:
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Left axis: GDP（兆円）
    color1 = '#06A77D'
    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('GDP (trillion yen)', fontweight='bold', color=color1)
    line1 = ax1.plot(df_macro['Date'], df_macro['GDP (trillion yen)'], 
                     linewidth=2, color=color1, marker='^', markersize=4, 
                     label='GDP (trillion yen)', alpha=0.8)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Right axis: CPI
    ax2 = ax1.twinx()
    color2 = '#F18F01'
    ax2.set_ylabel('CPI (2015=100)', fontweight='bold', color=color2)
    line2 = ax2.plot(df_macro['Date'], df_macro['CPI'], 
                     linewidth=2, color=color2, marker='D', markersize=4, 
                     label='CPI (2015=100)', linestyle='--', alpha=0.8)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Add policy event markers
    for event_date_str, event_info in policy_events.items():
        event_date = year_quarter_to_date(event_date_str)
        if not pd.isna(event_date) and event_date >= df_macro['Date'].min():
            ax1.axvline(x=event_date, color=event_info['color'], 
                       linestyle=':', linewidth=1.5, alpha=0.6)
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=9)
    
    ax1.set_title('GDP and CPI Trends', fontweight='bold')
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_minor_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/06_gdp_and_cpi_trends.png', 
                dpi=300, bbox_inches='tight')
    print(f"  保存: {output_dir}/06_gdp_and_cpi_trends.png")
    plt.close()

# ============================================================================
# Graph 3: 統合グラフ（すべての変数を正規化して表示）
# ============================================================================
print("\n4. グラフ3: 統合グラフ（正規化）を作成中...")

# Filter data with all variables
df_all = df[
    (df['P (yen/liter)'].notna()) & 
    (df['P_relative'].notna()) & 
    (df['GDP (trillion yen)'].notna()) & 
    (df['CPI'].notna())
].copy()

if len(df_all) > 0:
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Normalize all variables to 100 at the first available data point
    first_idx = df_all.index[0]
    base_date = df_all.loc[first_idx, 'Date']
    
    # Calculate normalized values (100 = first value)
    df_all['P_normalized'] = (df_all['P (yen/liter)'] / df_all.loc[first_idx, 'P (yen/liter)']) * 100
    df_all['P_relative_normalized'] = (df_all['P_relative'] / df_all.loc[first_idx, 'P_relative']) * 100
    df_all['GDP_normalized'] = (df_all['GDP (trillion yen)'] / df_all.loc[first_idx, 'GDP (trillion yen)']) * 100
    df_all['CPI_normalized'] = (df_all['CPI'] / df_all.loc[first_idx, 'CPI']) * 100
    
    # Plot all normalized variables
    ax.plot(df_all['Date'], df_all['P_normalized'], 
            linewidth=2, color='#2E86AB', marker='o', markersize=3, 
            label='Gasoline Price (normalized)', alpha=0.8)
    ax.plot(df_all['Date'], df_all['P_relative_normalized'], 
            linewidth=2, color='#A23B72', marker='s', markersize=3, 
            label='Relative Price (normalized)', linestyle='--', alpha=0.8)
    ax.plot(df_all['Date'], df_all['GDP_normalized'], 
            linewidth=2, color='#06A77D', marker='^', markersize=3, 
            label='GDP (normalized)', alpha=0.8)
    ax.plot(df_all['Date'], df_all['CPI_normalized'], 
            linewidth=2, color='#F18F01', marker='D', markersize=3, 
            label='CPI (normalized)', linestyle='--', alpha=0.8)
    
    # Add horizontal line at 100 (base level)
    ax.axhline(y=100, color='gray', linestyle='-', linewidth=1, alpha=0.3)
    
    # Add policy event markers
    for event_date_str, event_info in policy_events.items():
        event_date = year_quarter_to_date(event_date_str)
        if not pd.isna(event_date) and event_date >= df_all['Date'].min():
            ax.axvline(x=event_date, color=event_info['color'], 
                      linestyle=':', linewidth=1.5, alpha=0.6)
            ax.text(event_date, ax.get_ylim()[1] * 0.98, event_info['label'],
                   rotation=90, verticalalignment='top', horizontalalignment='right',
                   fontsize=8, color=event_info['color'])
    
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('Normalized Index (First Value = 100)', fontweight='bold')
    ax.set_title('Comprehensive Trends: Gasoline Price, Relative Price, GDP, and CPI (Normalized)', 
                fontweight='bold')
    ax.legend(loc='best', fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_minor_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/07_comprehensive_trends_normalized.png', 
                dpi=300, bbox_inches='tight')
    print(f"  保存: {output_dir}/07_comprehensive_trends_normalized.png")
    plt.close()

# ============================================================================
# Graph 4: ガソリン価格、相対価格、GDP、CPIの個別グラフ（4分割）
# ============================================================================
print("\n5. グラフ4: 個別グラフ（4分割）を作成中...")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Raw Data Trends: Comprehensive View', fontweight='bold', fontsize=14)

# 1. ガソリン価格
ax1 = axes[0, 0]
df_price_plot = df[df['P (yen/liter)'].notna()].copy()
if len(df_price_plot) > 0:
    ax1.plot(df_price_plot['Date'], df_price_plot['P (yen/liter)'], 
             linewidth=2, color='#2E86AB', marker='o', markersize=3, alpha=0.8)
    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Price (yen/liter)', fontweight='bold')
    ax1.set_title('(a) Gasoline Price Trend', fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
# 2. 相対価格
ax2 = axes[0, 1]
df_rel_plot = df[df['P_relative'].notna()].copy()
if len(df_rel_plot) > 0:
    ax2.plot(df_rel_plot['Date'], df_rel_plot['P_relative'], 
             linewidth=2, color='#A23B72', marker='s', markersize=3, alpha=0.8)
    ax2.set_xlabel('Year', fontweight='bold')
    ax2.set_ylabel('Relative Price (P/CPI)', fontweight='bold')
    ax2.set_title('(b) Relative Price Trend', fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 3. GDP
ax3 = axes[1, 0]
df_gdp_plot = df[df['GDP (trillion yen)'].notna()].copy()
if len(df_gdp_plot) > 0:
    ax3.plot(df_gdp_plot['Date'], df_gdp_plot['GDP (trillion yen)'], 
             linewidth=2, color='#06A77D', marker='^', markersize=3, alpha=0.8)
    ax3.set_xlabel('Year', fontweight='bold')
    ax3.set_ylabel('GDP (trillion yen)', fontweight='bold')
    ax3.set_title('(c) GDP Trend', fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 4. CPI
ax4 = axes[1, 1]
df_cpi_plot = df[df['CPI'].notna()].copy()
if len(df_cpi_plot) > 0:
    ax4.plot(df_cpi_plot['Date'], df_cpi_plot['CPI'], 
             linewidth=2, color='#F18F01', marker='D', markersize=3, alpha=0.8)
    ax4.set_xlabel('Year', fontweight='bold')
    ax4.set_ylabel('CPI (2015=100)', fontweight='bold')
    ax4.set_title('(d) CPI Trend', fontweight='bold')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.tight_layout()
plt.savefig(f'{output_dir}/08_comprehensive_trends_individual.png', 
            dpi=300, bbox_inches='tight')
print(f"  保存: {output_dir}/08_comprehensive_trends_individual.png")
plt.close()

print("\n" + "="*60)
print("すべてのグラフの作成が完了しました！")
print(f"出力ディレクトリ: {output_dir}/")
print("="*60)
print("\n作成されたグラフ:")
print("  - 05_gasoline_price_and_relative_price_trends.png")
print("  - 06_gdp_and_cpi_trends.png")
print("  - 07_comprehensive_trends_normalized.png")
print("  - 08_comprehensive_trends_individual.png")

