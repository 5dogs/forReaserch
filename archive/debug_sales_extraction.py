import pandas as pd
import re

sales_file = r"data/2007-2024ガソリン販売量/統合.csv"
df_sales_raw = pd.read_csv(sales_file, header=None, encoding='utf-8')

print("統合.csvの行7-10を確認:")
for idx in range(6, 11):
    row = df_sales_raw.iloc[idx]
    print(f"\n行{idx+1} (index {idx}):")
    # 最初の10列と最後の5列を表示
    row_list = [str(v) if pd.notna(v) else '' for v in row]
    print(f"  最初の10列: {row_list[:10]}")
    print(f"  最後の5列: {row_list[-5:]}")
    print(f"  全列数: {len(row_list)}")
    
    # C.Y.を含む行を探す
    if any('C.Y.' in str(v) for v in row if pd.notna(v)):
        print(f"  → C.Y.を含む行です")
        # 平成年を探す
        for i, val in enumerate(row_list[:10]):
            if '平成' in str(val):
                print(f"    列{i}: {val}")
                if i + 1 < len(row_list):
                    print(f"    列{i+1}: {row_list[i+1]}")
        # ガソリン列を探す（列6-8あたり）
        for i in range(5, min(10, len(row_list))):
            val = row_list[i]
            if val and val.replace(',', '').replace('.', '').isdigit():
                num = float(val.replace(',', ''))
                if 50000000 < num < 70000000:  # ガソリン販売量の範囲（5000万-7000万kl）
                    print(f"    ガソリン候補 列{i}: {val} ({num:,.0f} kl)")

