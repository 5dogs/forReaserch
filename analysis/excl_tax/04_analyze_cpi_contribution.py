"""
CPIへのガソリン価格寄与度分析スクリプト（税率除外版）
本体価格（税抜き）と税込み価格のCPIへの影響を分析

処理内容:
1. CPIデータからガソリン指数とウェイトを抽出（2007-2025年）
2. ガソリン価格を本体価格と税込み価格に分解
3. CPIへの寄与度計算
4. グラフ作成

注意: このスクリプトは税率変数に依存しないため、税率除外版でも同じ結果が得られます。
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非対話型バックエンドを使用
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

# スクリプトのディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # analysis/ の親ディレクトリ

# 出力ディレクトリ
output_dir = os.path.join(project_root, 'analysis', 'results', 'excl_tax')
figures_dir = os.path.join(project_root, 'analysis', 'figures', 'excl_tax')
os.makedirs(output_dir, exist_ok=True)
os.makedirs(figures_dir, exist_ok=True)

print("="*60)
print("CPIへのガソリン価格寄与度分析（税率除外版）")
print("="*60)

# ============================================================================
# 1. データ読み込み
# ============================================================================
print("\n1. データ読み込み中...")

# CPIデータ（品目別）
print("  - CPIデータ（品目別）を読み込み中...")
cpi_file = os.path.join(project_root, 'data', '-2025消費者物価指数', '自由帳 - zni2020a-品目別.csv')
df_cpi_items = pd.read_csv(
    cpi_file,
    encoding='utf-8-sig',
    header=None
)

# ガソリンの列を特定（1行目のヘッダーから）
japanese_headers = df_cpi_items.iloc[0]
gasoline_col_index = None
for idx, col_name in enumerate(japanese_headers):
    if isinstance(col_name, str) and "ガソリン" in col_name:
        gasoline_col_index = idx
        break

if gasoline_col_index is None:
    raise ValueError("CPIデータで「ガソリン」の列が見つかりませんでした。")

print(f"  - ガソリンの列インデックス: {gasoline_col_index}")

# CPIのガソリンウェイトを取得（5行目のウエイト）
weights_row = df_cpi_items.iloc[4]  # ウエイトの行（0-indexedなので4行目）
total_weight = float(weights_row[1])  # 総合のウエイト（2列目）
gasoline_weight = float(weights_row[gasoline_col_index])

# ウェイトの割合を計算
gasoline_weight_percentage = (gasoline_weight / total_weight) * 100
print(f"  - CPI総合のウエイト: {total_weight:,.0f}")
print(f"  - ガソリンのウエイト: {gasoline_weight:,.0f}")
print(f"  - CPIに占めるガソリンのウェイト: {gasoline_weight_percentage:.2f}%")

# CPIデータの年次データを抽出（7行目以降がデータ）
# 列名を設定
df_cpi_data = df_cpi_items.iloc[6:].copy()  # 7行目以降
df_cpi_data.columns = df_cpi_items.iloc[0]  # 1行目を列名に

# 年列とガソリン指数列を抽出
cpi_years = []
cpi_gasoline_index = []

for idx, row in df_cpi_data.iterrows():
    year_str = str(row.iloc[0])  # 1列目が年
    if year_str.isdigit():
        year = int(year_str)
        if 2007 <= year <= 2025:
            cpi_years.append(year)
            gasoline_index_val = row.iloc[gasoline_col_index]
            try:
                cpi_gasoline_index.append(float(gasoline_index_val))
            except (ValueError, TypeError):
                cpi_gasoline_index.append(np.nan)

df_cpi_gasoline = pd.DataFrame({
    'Year': cpi_years,
    'CPI_Gasoline_Index': cpi_gasoline_index
})

print(f"  - CPIガソリン指数データ: {len(df_cpi_gasoline)}年分")

# ガソリン価格データ
print("  - ガソリン価格データを読み込み中...")
price_file = os.path.join(project_root, 'demand_regression_data_raw.csv')
df_price = pd.read_csv(price_file, encoding='utf-8-sig')

# Year列を解析（YearQuarter形式: 2007Q1など）
# まず文字列として扱う
df_price['Year_Quarter_Str'] = df_price['Year'].astype(str)
df_price['Year'] = df_price['Year_Quarter_Str'].str.extract(r'(\d{4})').astype(float)
df_price['Quarter'] = df_price['Year_Quarter_Str'].str.extract(r'Q(\d)').astype(float)

# 2007-2025年のデータを抽出
df_price = df_price[(df_price['Year'] >= 2007) & (df_price['Year'] <= 2025)].copy()
df_price = df_price.dropna(subset=['P (yen/liter)'])

print(f"  - ガソリン価格データ: {len(df_price)}行")

# ガソリン税額データ
print("  - ガソリン税額データを読み込み中...")
tax_file = os.path.join(project_root, 'data', '-2025ガソリン関連税四半期ごと', 'gasoline_tax_quarterly.csv')
df_tax = pd.read_csv(
    tax_file,
    encoding='utf-8-sig'
)

# 2007-2025年のデータを抽出
df_tax = df_tax[(df_tax['Year'] >= 2007) & (df_tax['Year'] <= 2025)].copy()

# Year_Quarter列を作成してマージ
df_tax['Year_Quarter'] = df_tax['Year'].astype(int).astype(str) + '-Q' + df_tax['Quarter'].astype(int).astype(str)
df_price['Year_Quarter'] = df_price['Year'].astype(int).astype(str) + '-Q' + df_price['Quarter'].astype(int).astype(str)

# マージ
df_price = df_price.merge(
    df_tax[['Year_Quarter', '合計従量税率_円L', '消費税率_%']],
    on='Year_Quarter',
    how='left'
)

print(f"  - マージ後のデータ: {len(df_price)}行")

# ============================================================================
# 2. ガソリン価格の分解
# ============================================================================
print("\n2. ガソリン価格の分解中...")

# 税込み価格 = P (yen/liter)
df_price['Price_TaxInclusive'] = df_price['P (yen/liter)']

# ガソリン税額（円/L）= 合計従量税率_円L
df_price['Gasoline_Tax_Amount'] = df_price['合計従量税率_円L']

# 消費税額の計算
# 消費税は、ガソリン税を除いた価格（本体価格 + ガソリン税）に課される
# 税込み価格 = 本体価格 + ガソリン税 + 消費税
# 消費税 = (本体価格 + ガソリン税) × 消費税率 / (1 + 消費税率)
# または: 消費税 = (税込み価格 - ガソリン税) × 消費税率 / (1 + 消費税率)

# 消費税率を取得（%から小数に変換）
df_price['Consumption_Tax_Rate'] = df_price['消費税率_%'] / 100.0

# 消費税額を計算
# 税込み価格からガソリン税を引いた額が、消費税課税対象額（本体価格 + ガソリン税）
# 消費税 = 消費税課税対象額 × 消費税率 / (1 + 消費税率)
tax_base = df_price['Price_TaxInclusive'] - df_price['Gasoline_Tax_Amount']
df_price['Consumption_Tax_Amount'] = tax_base * df_price['Consumption_Tax_Rate'] / (1 + df_price['Consumption_Tax_Rate'])

# 本体価格（税抜き）= 税込み価格 - ガソリン税額 - 消費税額
df_price['Price_Base'] = df_price['Price_TaxInclusive'] - df_price['Gasoline_Tax_Amount'] - df_price['Consumption_Tax_Amount']

# 年次データに集約
df_annual = df_price.groupby('Year').agg({
    'Price_TaxInclusive': 'mean',
    'Price_Base': 'mean',
    'Gasoline_Tax_Amount': 'mean',
    'Consumption_Tax_Amount': 'mean',
    'Consumption_Tax_Rate': 'mean'
}).reset_index()

print(f"  - 年次データ: {len(df_annual)}年分")
print("\n  価格内訳（例: 2024年）:")
if 2024 in df_annual['Year'].values:
    row_2024 = df_annual[df_annual['Year'] == 2024].iloc[0]
    print(f"    税込み価格: {row_2024['Price_TaxInclusive']:.2f}円/L")
    print(f"    本体価格: {row_2024['Price_Base']:.2f}円/L")
    print(f"    ガソリン税: {row_2024['Gasoline_Tax_Amount']:.2f}円/L")
    print(f"    消費税: {row_2024['Consumption_Tax_Amount']:.2f}円/L")

# ============================================================================
# 3. CPIデータとのマージ
# ============================================================================
print("\n3. CPIデータとのマージ中...")

# CPIガソリン指数を年次データにマージ
df_annual = df_annual.merge(
    df_cpi_gasoline,
    on='Year',
    how='left'
)

# CPIガソリン指数の前年比変化率を計算
df_annual = df_annual.sort_values('Year')
df_annual['CPI_Gasoline_Index_Prev'] = df_annual['CPI_Gasoline_Index'].shift(1)
df_annual['CPI_Gasoline_Change_Rate'] = (
    (df_annual['CPI_Gasoline_Index'] - df_annual['CPI_Gasoline_Index_Prev']) 
    / df_annual['CPI_Gasoline_Index_Prev'] * 100
)

# 本体価格と税込み価格の前年比変化率を計算
df_annual['Price_Base_Prev'] = df_annual['Price_Base'].shift(1)
df_annual['Price_TaxInclusive_Prev'] = df_annual['Price_TaxInclusive'].shift(1)

df_annual['Price_Base_Change_Rate'] = (
    (df_annual['Price_Base'] - df_annual['Price_Base_Prev']) 
    / df_annual['Price_Base_Prev'] * 100
)

df_annual['Price_TaxInclusive_Change_Rate'] = (
    (df_annual['Price_TaxInclusive'] - df_annual['Price_TaxInclusive_Prev']) 
    / df_annual['Price_TaxInclusive_Prev'] * 100
)

# CPIへの寄与度を計算
# 寄与度 = 価格変化率 × CPIウェイト（%）
df_annual['CPI_Contribution_Base'] = (
    df_annual['Price_Base_Change_Rate'] * gasoline_weight_percentage / 100
)
df_annual['CPI_Contribution_TaxInclusive'] = (
    df_annual['Price_TaxInclusive_Change_Rate'] * gasoline_weight_percentage / 100
)

print(f"  - マージ完了: {len(df_annual)}年分")

# ============================================================================
# 4. 結果をCSVに保存
# ============================================================================
print("\n4. 結果をCSVに保存中...")
output_file = os.path.join(output_dir, '04_cpi_contribution_analysis.csv')
df_annual.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"  - 保存完了: {output_file}")

# ============================================================================
# 5. グラフ作成
# ============================================================================
print("\n5. グラフ作成中...")

# グラフ1: 本体価格と税込み価格の推移
print("  - グラフ1: 本体価格と税込み価格の推移")
fig, ax = plt.subplots(figsize=(12, 6))

years = df_annual['Year'].values
ax.plot(years, df_annual['Price_Base'].values, 
        label='Base Price (Tax-Exclusive)', linewidth=2, color='#2E86AB', marker='o', markersize=4)
ax.plot(years, df_annual['Price_TaxInclusive'].values, 
        label='Tax-Inclusive Price', linewidth=2, color='#A23B72', marker='s', markersize=4)

ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Price (yen/L)', fontweight='bold')
ax.set_title('Gasoline Price: Base vs Tax-Inclusive (2007-2025)', fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(2007, 2025)

plt.tight_layout()
plt.savefig(os.path.join(figures_dir, '04_gasoline_price_base_vs_tax_inclusive.png'), dpi=300, bbox_inches='tight')
print(f"    - 保存: {os.path.join(figures_dir, '04_gasoline_price_base_vs_tax_inclusive.png')}")
plt.close()

# グラフ2: CPIへの寄与度の比較
print("  - グラフ2: CPIへの寄与度の比較")
fig, ax = plt.subplots(figsize=(12, 6))

# 欠損値を除外
valid_data = df_annual.dropna(subset=['CPI_Contribution_Base', 'CPI_Contribution_TaxInclusive'])

ax.bar(valid_data['Year'].values - 0.2, valid_data['CPI_Contribution_Base'].values,
       width=0.4, label='Base Price Contribution', color='#2E86AB', alpha=0.7)
ax.bar(valid_data['Year'].values + 0.2, valid_data['CPI_Contribution_TaxInclusive'].values,
       width=0.4, label='Tax-Inclusive Price Contribution', color='#A23B72', alpha=0.7)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('CPI Contribution (percentage points)', fontweight='bold')
ax.set_title('CPI Contribution: Base Price vs Tax-Inclusive Price', fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3, linestyle='--', axis='y')
ax.set_xlim(2007, 2025)

plt.tight_layout()
plt.savefig(os.path.join(figures_dir, '05_cpi_contribution_comparison.png'), dpi=300, bbox_inches='tight')
print(f"    - 保存: {os.path.join(figures_dir, '05_cpi_contribution_comparison.png')}")
plt.close()

# グラフ3: 価格構成の内訳（積み上げ棒グラフ + 税額の折れ線を統合）
print("  - グラフ3: 価格構成の内訳（税額の推移を統合）")
plt.close('all')  # 前のグラフを閉じる
fig, ax1 = plt.subplots(figsize=(14, 6))

# 積み上げ棒グラフ（価格構成）
# Base Priceを一番上に表示するため、順序を変更
ax1.bar(years, df_annual['Gasoline_Tax_Amount'].values,
       label='Gasoline Tax', color='#06A77D', alpha=0.7)
ax1.bar(years, df_annual['Consumption_Tax_Amount'].values,
       bottom=df_annual['Gasoline_Tax_Amount'].values,
       label='Consumption Tax', color='#A23B72', alpha=0.7)
ax1.bar(years, df_annual['Price_Base'].values,
       bottom=df_annual['Gasoline_Tax_Amount'].values + df_annual['Consumption_Tax_Amount'].values,
       label='Base Price', color='#2E86AB', alpha=0.7)

# 右軸: ガソリン税額の折れ線（固定されていることを可視化）
ax2 = ax1.twinx()
ax2.plot(years, df_annual['Gasoline_Tax_Amount'].values,
         label='Gasoline Tax Amount (Fixed)', linewidth=3, color='#06A77D', 
         marker='o', markersize=6, linestyle='--', alpha=0.9)

# 2008年の暫定税率失効をマーク
if 2008 in df_annual['Year'].values:
    ax1.axvline(x=2008, color='red', linestyle='--', linewidth=1.5, alpha=0.7, 
                label='2008 Temporary Tax Rate Expiration')

ax1.set_xlabel('Year', fontweight='bold', fontsize=11)
ax1.set_ylabel('Price (yen/L)', fontweight='bold', fontsize=11)
ax2.set_ylabel('Tax Amount (yen/L)', fontweight='bold', fontsize=11, color='#06A77D')
ax1.set_title('Gasoline Price Composition with Fixed Tax Amount Trend', fontweight='bold', fontsize=12)

# 凡例を統合（グラフ外に配置）
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, bbox_to_anchor=(1.15, 1.0), loc='upper left', fontsize=9)

ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
ax1.set_xlim(2006.5, 2025.5)
ax2.tick_params(axis='y', labelcolor='#06A77D')

plt.tight_layout()
plt.savefig(os.path.join(figures_dir, '06_gasoline_price_composition.png'), dpi=300, bbox_inches='tight')
print(f"    - 保存: {os.path.join(figures_dir, '06_gasoline_price_composition.png')}")
plt.close()

print("\n" + "="*60)
print("分析完了！")
print("="*60)
print(f"\n出力ファイル:")
print(f"  - 結果CSV: {output_file}")
print(f"  - グラフ: {figures_dir}/04_*.png, 05_*.png, 06_*.png")

