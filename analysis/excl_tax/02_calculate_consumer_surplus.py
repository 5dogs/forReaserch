"""
消費者余剰の計算スクリプト（税率除外版）
測定方法総論に基づく台形近似による消費者余剰の計算

計算手順:
1. 価格要因の寄与率計算: Xt+1 = β(exp(lnPt+1－lnPt)－1)／(exp(lnQt+1－lnQt)－1)
2. 需要増加分の価格要因部分: Yt+1 = Xt+1 × (Qt+1－Qt)
3. 消費者余剰増分の台形面積: (Qt＋Qt＋Yt+1)×(Pt－Pt+1)×1/2
"""

import pandas as pd
import numpy as np
import json
import os

# スクリプトのディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # analysis/ の親ディレクトリ

# 出力ディレクトリ
output_dir = os.path.join(project_root, 'analysis', 'results', 'excl_tax')
os.makedirs(output_dir, exist_ok=True)

print("="*60)
print("消費者余剰の計算（税率除外版）")
print("="*60)

# 1. 需要関数の推定結果を読み込む（税率除外版）
print("\n需要関数の推定結果を読み込み中...")
coeff_file = os.path.join(project_root, 'analysis', 'results', 'excl_tax', '01_coefficients_annual_level_model_excl_tax.json')
if not os.path.exists(coeff_file):
    print(f"エラー: {coeff_file} が見つかりません。")
    print("先に 01_estimate_demand_function_annual_level_model_excl_tax.py を実行してください。")
    exit(1)

with open(coeff_file, 'r', encoding='utf-8') as f:
    coefficients = json.load(f)

alpha = coefficients['alpha']
beta = coefficients['beta']
# gamma は除外（税率除外版のため）

print(f"使用する係数（税率除外版）:")
print(f"  所得弾力性 (α): {alpha:.6f}")
print(f"  価格弾力性 (β): {beta:.6f}")
print(f"  モデルタイプ: {coefficients.get('model_type', 'N/A')}")
print(f"  R²: {coefficients.get('rsquared', 0):.4f}")

# 2. 分析データを読み込む（税率除外版）
print("\n分析データを読み込み中...")
data_file = os.path.join(project_root, 'analysis', 'results', 'excl_tax', '01_analysis_data_annual_level_model_excl_tax.csv')
if not os.path.exists(data_file):
    print(f"エラー: {data_file} が見つかりません。")
    exit(1)

df = pd.read_csv(data_file)
print(f"データ期間: {df['Year'].min()} - {df['Year'].max()}")
print(f"データ行数: {len(df)}行")
print(f"データタイプ: 年次データ")

# 3. 消費者余剰の計算（測定方法総論に基づく）
print("\n消費者余剰を計算中...")
results = []

for i in range(1, len(df)):  # 最初の行は除外（前年比のため）
    year = df.iloc[i]['Year']
    q_prev = df.iloc[i-1]['Q (liters)']
    q_curr = df.iloc[i]['Q (liters)']
    p_prev = df.iloc[i-1]['P (yen/liter)']
    p_curr = df.iloc[i]['P (yen/liter)']
    
    # 価格要因の寄与率を計算
    # Xt+1 = β(exp(lnPt+1－lnPt)－1)／(exp(lnQt+1－lnQt)－1)
    if q_curr != q_prev and p_curr != p_prev:
        ln_p_change = np.log(p_curr) - np.log(p_prev)
        ln_q_change = np.log(q_curr) - np.log(q_prev)
        
        if abs(ln_q_change) > 1e-10:  # ゼロ除算を避ける
            price_contribution = beta * (np.exp(ln_p_change) - 1) / (np.exp(ln_q_change) - 1)
        else:
            price_contribution = 0
    else:
        price_contribution = 0
    
    # 需要増加分のうち価格要因によって説明される部分
    # Yt+1 = Xt+1 × (Qt+1－Qt)
    demand_change = q_curr - q_prev
    price_effect = price_contribution * demand_change
    
    # 消費者余剰の増分となる台形の面積を計算
    # (Qt＋Qt＋Yt+1)×(Pt－Pt+1)×1/2
    if p_prev != p_curr:
        cs_increase = (q_prev + q_curr + price_effect) * (p_prev - p_curr) * 0.5
    else:
        cs_increase = 0
    
    # 累積消費者余剰の計算
    if i == 1:
        cumulative_cs = cs_increase
    else:
        cumulative_cs = results[-1]['Cumulative_CS'] + cs_increase
    
    results.append({
        'Year': year,
        'Q_prev': q_prev,
        'Q_curr': q_curr,
        'P_prev': p_prev,
        'P_curr': p_curr,
        'Price_Contribution': price_contribution,
        'Price_Effect': price_effect,
        'CS_Increase': cs_increase,
        'Cumulative_CS': cumulative_cs,
        'ΔQ': demand_change,
        'ΔP': p_curr - p_prev
    })

# 4. 結果をDataFrameに変換
results_df = pd.DataFrame(results)

# 5. 統計情報の表示
print("\n" + "="*60)
print("消費者余剰の計算結果")
print("="*60)
print(f"計算期間: {results_df['Year'].min()} - {results_df['Year'].max()}")
print(f"計算行数: {len(results_df)}行")

print(f"\n消費者余剰の統計:")
print(f"  平均増分: {results_df['CS_Increase'].mean():,.0f}")
print(f"  累積余剰: {results_df['Cumulative_CS'].iloc[-1]:,.0f}")
print(f"  最大増分: {results_df['CS_Increase'].max():,.0f} ({results_df.loc[results_df['CS_Increase'].idxmax(), 'Year']})")
print(f"  最小増分: {results_df['CS_Increase'].min():,.0f} ({results_df.loc[results_df['CS_Increase'].idxmin(), 'Year']})")

# 価格上昇年と価格下落年をカウント
price_increase = (results_df['ΔP'] > 0).sum()
price_decrease = (results_df['ΔP'] < 0).sum()
print(f"\n価格変動:")
print(f"  価格上昇: {price_increase}年")
print(f"  価格下落: {price_decrease}年")

# 価格と余剰の相関
correlation = results_df['ΔP'].corr(results_df['CS_Increase'])
print(f"  価格変化と余剰変化の相関係数: {correlation:.4f}")

# 6. 結果を保存
results_df.to_csv(os.path.join(output_dir, '02_consumer_surplus_results.csv'), index=False, encoding='utf-8-sig')

print(f"\n" + "="*60)
print("結果を保存しました")
print("="*60)
print(f"消費者余剰計算結果: {os.path.join(output_dir, '02_consumer_surplus_results.csv')}")

# 7. サマリーを表示
print(f"\n最初の10行:")
print(results_df[['Year', 'CS_Increase', 'Cumulative_CS', 'ΔP']].head(10).to_string())

print(f"\n最後の10行:")
print(results_df[['Year', 'CS_Increase', 'Cumulative_CS', 'ΔP']].tail(10).to_string())

print("\n完了しました！")

