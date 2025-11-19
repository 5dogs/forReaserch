import pandas as pd
import numpy as np

# CSVファイルを読み込む
df = pd.read_csv('gasoline_tax_quarterly.csv', encoding='utf-8')

# 浮動小数点の精度を修正（小数点以下2桁に丸める）
df['合計従量税率_円L'] = df['合計従量税率_円L'].round(2)
df['実効従量税率_円L'] = df['実効従量税率_円L'].round(2)

# CSVファイルに保存
df.to_csv('gasoline_tax_quarterly.csv', index=False, encoding='utf-8')

print("浮動小数点の精度を修正しました。")
print(f"修正後の統計:")
print(f"  合計従量税率: {df['合計従量税率_円L'].min():.2f} 〜 {df['合計従量税率_円L'].max():.2f}円/L")
print(f"  実効従量税率: {df['実効従量税率_円L'].min():.2f} 〜 {df['実効従量税率_円L'].max():.2f}円/L")

