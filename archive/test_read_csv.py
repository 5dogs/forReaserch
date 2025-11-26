import pandas as pd
import os

# ファイルパス
file_path = r"data/-2024ガソリン販売量/統合.csv"

print(f"ファイルパス: {file_path}")
print(f"ファイル存在確認: {os.path.exists(file_path)}")

# CSVファイルを読み込む
try:
    df = pd.read_csv(file_path, encoding='utf-8', header=None)
    print(f"\n読み込み成功！")
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")
    
    # データの構造を確認
    print(f"\n=== データ構造の確認 ===")
    print(f"\n行6-10（データ行の例）:")
    print(df.iloc[6:11].to_string())
    
    # ガソリンの列を探す（列6がガソリンの可能性が高い）
    print(f"\n=== ガソリン販売量の列を確認 ===")
    print(f"列6の最初の20行（ガソリン販売量の可能性）:")
    print(df.iloc[6:26, 6].to_string())
    
    # 年と月の情報を含む行を探す
    print(f"\n=== 年月情報を含む行 ===")
    # 列2（年号）、列3（年）、列4（月/四半期）を含む行
    for i in range(6, min(30, len(df))):
        if pd.notna(df.iloc[i, 2]) and pd.notna(df.iloc[i, 3]):
            print(f"行{i}: {df.iloc[i, 2]} {df.iloc[i, 3]} {df.iloc[i, 4] if pd.notna(df.iloc[i, 4]) else ''} - ガソリン: {df.iloc[i, 6] if pd.notna(df.iloc[i, 6]) else 'N/A'}")
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()

