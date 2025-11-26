"""
Raw Data Visualization Script for Gasoline Tax Analysis
Creates basic time series graphs for research purposes.

Phase 1: Basic Time Series Graphs
- Gasoline Price Trend (1990Q3-2025Q1)
- Gasoline Tax Rate Trend (1990Q3-2025Q1)
- GDP Trend (1994Q1-2025Q1)
- Gasoline Consumption Trend (available periods)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import os

# Set style for academic papers (simple and clean)
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

print("Loading data...")
# Load data
data_file = '../demand_regression_data_raw.csv'
if not os.path.exists(data_file):
    # Try current directory if relative path doesn't work
    data_file = 'demand_regression_data_raw.csv'
df = pd.read_csv(data_file)
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

# Define important policy events
policy_events = {
    '1974Q2': {'label': 'Temporary Tax Rate\nIntroduced', 'color': 'red'},
    '1989Q2': {'label': 'Consumption Tax\nIntroduced (3%)', 'color': 'blue'},
    '1997Q2': {'label': 'Consumption Tax\nIncreased (5%)', 'color': 'blue'},
    '2008Q2': {'label': 'Temporary Tax Rate\nTemporarily Expired', 'color': 'red'},
    '2014Q2': {'label': 'Consumption Tax\nIncreased (8%)', 'color': 'blue'},
    '2019Q4': {'label': 'Consumption Tax\nIncreased (10%)', 'color': 'blue'},
}

print(f"Data loaded: {len(df)} rows")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

# ============================================================================
# Graph 1: Gasoline Price Trend (1990Q3-2025Q1)
# ============================================================================
print("\nCreating Graph 1: Gasoline Price Trend...")
fig, ax = plt.subplots(figsize=(10, 6))

# Filter data with price information
df_price = df[df['P (yen/liter)'].notna()].copy()

ax.plot(df_price['Date'], df_price['P (yen/liter)'], 
        linewidth=1.5, color='#2E86AB', marker='o', markersize=3)

# Add policy event markers
for event_date_str, event_info in policy_events.items():
    event_date = year_quarter_to_date(event_date_str)
    if not pd.isna(event_date) and event_date >= df_price['Date'].min():
        # Find closest data point
        closest_idx = (df_price['Date'] - event_date).abs().idxmin()
        if closest_idx < len(df_price):
            ax.axvline(x=event_date, color=event_info['color'], 
                      linestyle='--', linewidth=1, alpha=0.7)
            ax.text(event_date, ax.get_ylim()[1] * 0.95, event_info['label'],
                   rotation=90, verticalalignment='top', horizontalalignment='right',
                   fontsize=8, color=event_info['color'])

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Price (yen/liter)', fontweight='bold')
ax.set_title('Gasoline Price Trend (1990Q3-2025Q1)', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_minor_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/01_gasoline_price_trend.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir}/01_gasoline_price_trend.png")
plt.close()

# ============================================================================
# Graph 2: Gasoline Tax Rate Trend (1990Q3-2025Q1)
# ============================================================================
print("\nCreating Graph 2: Gasoline Tax Rate Trend...")
fig, ax = plt.subplots(figsize=(10, 6))

# Filter data with tax rate information
df_tax = df[df['Tax_rate (%)'].notna()].copy()

ax.plot(df_tax['Date'], df_tax['Tax_rate (%)'], 
        linewidth=1.5, color='#A23B72', marker='s', markersize=3)

# Add policy event markers
for event_date_str, event_info in policy_events.items():
    event_date = year_quarter_to_date(event_date_str)
    if not pd.isna(event_date) and event_date >= df_tax['Date'].min():
        ax.axvline(x=event_date, color=event_info['color'], 
                  linestyle='--', linewidth=1, alpha=0.7)
        ax.text(event_date, ax.get_ylim()[1] * 0.95, event_info['label'],
               rotation=90, verticalalignment='top', horizontalalignment='right',
               fontsize=8, color=event_info['color'])

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Tax Rate (%)', fontweight='bold')
ax.set_title('Gasoline Tax Rate Trend (1990Q3-2025Q1)', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_minor_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/02_gasoline_tax_rate_trend.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir}/02_gasoline_tax_rate_trend.png")
plt.close()

# ============================================================================
# Graph 3: GDP Trend (1994Q1-2025Q1)
# ============================================================================
print("\nCreating Graph 3: GDP Trend...")
fig, ax = plt.subplots(figsize=(10, 6))

# Filter data with GDP information
df_gdp = df[df['GDP (trillion yen)'].notna()].copy()

ax.plot(df_gdp['Date'], df_gdp['GDP (trillion yen)'], 
        linewidth=1.5, color='#06A77D', marker='^', markersize=3)

# Add major economic events
economic_events = {
    '2008Q3': {'label': 'Lehman Shock', 'color': 'orange'},
    '2020Q2': {'label': 'COVID-19\nPandemic', 'color': 'red'},
}

for event_date_str, event_info in economic_events.items():
    event_date = year_quarter_to_date(event_date_str)
    if not pd.isna(event_date) and event_date >= df_gdp['Date'].min():
        ax.axvline(x=event_date, color=event_info['color'], 
                  linestyle='--', linewidth=1, alpha=0.7)
        ax.text(event_date, ax.get_ylim()[1] * 0.95, event_info['label'],
               rotation=90, verticalalignment='top', horizontalalignment='right',
               fontsize=8, color=event_info['color'])

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('GDP (trillion yen)', fontweight='bold')
ax.set_title('GDP Trend (1994Q1-2025Q1)', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.xaxis.set_major_locator(mdates.YearLocator(5))
ax.xaxis.set_minor_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/03_gdp_trend.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir}/03_gdp_trend.png")
plt.close()

# ============================================================================
# Graph 4: Gasoline Consumption Trend (Available Periods)
# ============================================================================
print("\nCreating Graph 4: Gasoline Consumption Trend...")
fig, ax = plt.subplots(figsize=(10, 6))

# Filter data with consumption information
# Convert Q (liters) to numeric, handling non-numeric values
df['Q_numeric'] = pd.to_numeric(df['Q (liters)'], errors='coerce')
df_consumption = df[df['Q_numeric'].notna()].copy()

# Convert to billions of liters for better readability
df_consumption['Q_billions'] = df_consumption['Q_numeric'] / 1e9

ax.plot(df_consumption['Date'], df_consumption['Q_billions'], 
        linewidth=1.5, color='#F18F01', marker='D', markersize=3)

# Add policy event markers
for event_date_str, event_info in policy_events.items():
    event_date = year_quarter_to_date(event_date_str)
    if not pd.isna(event_date) and event_date >= df_consumption['Date'].min():
        ax.axvline(x=event_date, color=event_info['color'], 
                  linestyle='--', linewidth=1, alpha=0.7)

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Consumption (billion liters)', fontweight='bold')
ax.set_title('Gasoline Consumption Trend (Available Periods)', fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_minor_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/04_gasoline_consumption_trend.png', dpi=300, bbox_inches='tight')
print(f"  Saved: {output_dir}/04_gasoline_consumption_trend.png")
plt.close()

print("\n" + "="*60)
print("All graphs created successfully!")
print(f"Output directory: {output_dir}/")
print("="*60)

