"""
2014Q2以降のQ (liters)データの単位を統一するスクリプト
2014Q1以前は10億リットル単位、2014Q2以降はリットル単位になっているため、
2014Q2以降を10億リットル単位に変換（1000倍）
"""

import pandas as pd
import numpy as np

print("2014Q2以降のQ (liters)データの単位を統一します...\n")

# データを読み込む
target_file = 'demand_regression_data_raw.csv'
df = pd.read_csv(target_file)
df['Year'] = df['Year'].astype(str)

# 2014Q2以降のデータを特定
df['Q_num'] = pd.to_numeric(df['Q (liters)'], errors='coerce')

# 2014Q1の値を基準に単位を判断
q_2014q1 = df[df['Year'] == '2014Q1']['Q_num'].values[0]
print(f"2014Q1の値（基準）: {q_2014q1}")

# 2014Q2以降で、値が2014Q1の1000分の1以下なら単位が間違っている
# 2014Q2以降を10億リットル単位に変換
mask_2014q2_onwards = (df['Year'] >= '2014Q2') & df['Q_num'].notna()
df_2014q2_onwards = df[mask_2014q2_onwards].copy()

if len(df_2014q2_onwards) > 0:
    print(f"\n2014Q2以降のデータ: {len(df_2014q2_onwards)}行")
    print("変換前のサンプル:")
    print(df_2014q2_onwards[['Year', 'Q (liters)']].head(10).to_string())
    
    # 値が1000万未満なら、リットル単位と判断して1000倍
    # 2014Q2以降のデータを確認
    q_2014q2 = df[df['Year'] == '2014Q2']['Q_num'].values[0]
    if pd.notna(q_2014q2) and q_2014q2 < q_2014q1 / 100:  # 100分の1以下なら単位が間違っている
        print(f"\n2014Q2の値: {q_2014q2} (リットル単位と判断)")
        print("2014Q2以降のデータを10億リットル単位に変換します（1000倍）")
        
        # 2014Q2以降のデータを1000倍
        df.loc[mask_2014q2_onwards, 'Q (liters)'] = df.loc[mask_2014q2_onwards, 'Q_num'] * 1000
        
        print("\n変換後のサンプル:")
        df_after = df[mask_2014q2_onwards].copy()
        print(df_after[['Year', 'Q (liters)']].head(10).to_string())
    else:
        print("単位は既に統一されているようです。")

# 不要な列を削除
df = df.drop(columns=['Q_num'], errors='ignore')

# 保存
df.to_csv(target_file, index=False, encoding='utf-8-sig')
print(f"\n{target_file} を更新しました")
print("完了しました！")

