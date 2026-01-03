"""
Step 1: データの問題点を確認するスクリプト
- 2025年の異常値を確認
- 変数間の相関を確認
- 散布図で可視化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

print("="*60)
print("Step 1: データの問題点の確認")
print("="*60)

# データの読み込み
df = pd.read_csv('results/01_analysis_data_annual_level_model.csv')

print("\n【1. 全データの概要】")
print(f"期間: {df['Year'].min()} - {df['Year'].max()}")
print(f"行数: {len(df)}")

print("\n【2. 2025年の異常値を確認】")
df_2025 = df[df['Year'] == '2025']
if len(df_2025) > 0:
    print("\n2025年のデータ:")
    print(df_2025[['Year', 'Q (liters)', 'GDP (trillion yen)', 'P (yen/liter)', 
                   'ln_GDP', 'ln_Q', 'ln_P_relative']].to_string())
    
    print("\n他の年のGDPの範囲:")
    df_other = df[df['Year'] != '2025']
    print(f"  GDP: {df_other['GDP (trillion yen)'].min():.2f} - {df_other['GDP (trillion yen)'].max():.2f} 兆円")
    print(f"  ln_GDP: {df_other['ln_GDP'].min():.4f} - {df_other['ln_GDP'].max():.4f}")
    print(f"  2025年のGDP: {df_2025['GDP (trillion yen)'].iloc[0]:.2f} 兆円 (異常に小さい!)")
    print(f"  2025年のln_GDP: {df_2025['ln_GDP'].iloc[0]:.4f} (異常に小さい!)")

print("\n【3. 2025年を除外したデータ】")
df_excl_2025 = df[df['Year'] != '2025'].copy()
print(f"期間: {df_excl_2025['Year'].min()} - {df_excl_2025['Year'].max()}")
print(f"行数: {len(df_excl_2025)}")

print("\n【4. 変数間の相関マトリックス（2025年除外）】")
vars_for_corr = ['ln_Q', 'ln_GDP', 'ln_P_relative', 'ln_Tax_rate']
corr_matrix = df_excl_2025[vars_for_corr].corr()
print(corr_matrix.round(4))

print("\n【5. 重要な相関の確認】")
print(f"ln_Q と ln_P_relative の相関: {df_excl_2025['ln_Q'].corr(df_excl_2025['ln_P_relative']):.4f}")
print(f"  → 負の相関（価格上昇→需要減少）を示している")
print(f"\nln_Q と ln_GDP の相関: {df_excl_2025['ln_Q'].corr(df_excl_2025['ln_GDP']):.4f}")
print(f"  → 正の相関（GDP増加→需要増加）を示している")
print(f"\nln_P_relative と ln_GDP の相関: {df_excl_2025['ln_P_relative'].corr(df_excl_2025['ln_GDP']):.4f}")
print(f"  → 多重共線性の可能性")

print("\n【6. 名目価格と消費量の相関（参考）】")
print(f"Q (liters) と P (yen/liter) の相関: {df_excl_2025['Q (liters)'].corr(df_excl_2025['P (yen/liter)']):.4f}")
print(f"  → 負の相関（価格上昇→消費量減少）を示している")

print("\n【7. データの統計的概要（2025年除外）】")
print("\nln_Q (被説明変数):")
print(df_excl_2025['ln_Q'].describe())
print("\nln_P_relative (価格変数):")
print(df_excl_2025['ln_P_relative'].describe())
print("\nln_GDP (所得変数):")
print(df_excl_2025['ln_GDP'].describe())
print("\nln_Tax_rate (税率変数):")
print(df_excl_2025['ln_Tax_rate'].describe())

print("\n" + "="*60)
print("Step 1完了")
print("="*60)
print("\n【発見された問題点】")
print("1. 2025年のGDPが異常に小さい（142.01兆円 vs 他年490-556兆円）")
print("2. 2025年のln_GDPが異常に小さい（4.956 vs 他年6.19-6.32）")
print("3. 2025年の消費量も異常に小さい（10.2億L vs 他年40-60億L）")
print("4. ln_P_relativeとln_Qは負の相関（-0.29）だが、回帰係数は正")
print("5. ln_P_relativeとln_GDPに相関がある可能性（多重共線性）")
print("\n【次のステップ】")
print("→ Step 2: 2025年を除外して回帰分析を再実行")
print("→ Step 3: 変数間の相関を詳しく分析（VIF計算など）")

