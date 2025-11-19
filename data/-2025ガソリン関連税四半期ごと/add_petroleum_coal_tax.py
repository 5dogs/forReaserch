import pandas as pd
import numpy as np

# CSVファイルを読み込む
df = pd.read_csv('gasoline_tax_quarterly.csv', encoding='utf-8')

# 石油石炭税を決定する関数
def get_petroleum_coal_tax_rate(year, quarter):
    """
    石油石炭税を返す（ガソリンに対する税率）
    - 1978年Q1以前: 0円/L（石油石炭税創設前）
    - 1978年Q1〜2003年Q3: 0円/L（ガソリンは対象外）
    - 2003年Q4〜2012年Q3: 約2.04円/L（ガソリンへの適用開始、地球温暖化対策税導入前）
    - 2012年Q4〜: 2.8円/L（地球温暖化対策税上乗せ後）
    
    注: 正確な税率変遷は要確認。一般的には2003年10月からガソリンにも適用。
    2012年10月から地球温暖化対策税が上乗せされ、現在は2.8円/L。
    """
    if year < 2003:
        return 0.0
    elif year == 2003:
        if quarter < 4:
            return 0.0
        else:
            # 2003年10月からガソリンへの適用開始（概算値）
            return 2.04
    elif year < 2012:
        return 2.04
    elif year == 2012:
        if quarter < 4:
            return 2.04
        else:
            # 2012年10月から地球温暖化対策税上乗せ
            return 2.8
    else:
        return 2.8

# 石油石炭税カラムを追加
df['石油石炭税_円L'] = df.apply(lambda row: get_petroleum_coal_tax_rate(row['Year'], row['Quarter']), axis=1)

# 合計従量税率を計算（揮発油税+地方揮発油税+石油石炭税）
df['合計従量税率_円L'] = (
    df['揮発油税_本則_円L'] + 
    df['地方揮発油税_本則_円L'] + 
    df['揮発油税_暫定_円L'] + 
    df['地方揮発油税_暫定_円L'] + 
    df['石油石炭税_円L']
)

# 実効従量税率を計算（二重課税考慮：従量税に消費税がかかる）
# 実効従量税率 = 従量税率 × (1 + 消費税率/100)
df['実効従量税率_円L'] = df['合計従量税率_円L'] * (1 + df['消費税率_%'] / 100)

# カラムの順序を調整
cols = ['Year', 'Quarter', 'Year_Quarter', 
        '揮発油税_本則_円L', '地方揮発油税_本則_円L', 
        '揮発油税_暫定_円L', '地方揮発油税_暫定_円L', 
        '石油石炭税_円L',
        '合計税率_円L',  # 既存の合計（揮発油税+地方揮発油税のみ）
        '合計従量税率_円L',  # 新規：揮発油税+地方揮発油税+石油石炭税
        '実効従量税率_円L',  # 新規：二重課税考慮
        '消費税率_%', 
        '制度変更', '備考']
df = df[cols]

# CSVファイルに保存
df.to_csv('gasoline_tax_quarterly.csv', index=False, encoding='utf-8')

print(f"石油石炭税と実効税率を追加しました。")
print(f"データ件数: {len(df)}件")
print(f"\n石油石炭税の変遷ポイント:")
petroleum_changes = df[df['石油石炭税_円L'].diff() != 0][['Year', 'Quarter', 'Year_Quarter', '石油石炭税_円L', '合計従量税率_円L', '実効従量税率_円L']]
print(petroleum_changes)

print(f"\n合計従量税率の統計:")
print(df['合計従量税率_円L'].describe())

print(f"\n実効従量税率の統計:")
print(df['実効従量税率_円L'].describe())

