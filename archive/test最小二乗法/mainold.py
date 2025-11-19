#data.csvの読み込み
import pandas as pd
df = pd.read_csv("data.csv")
df = df.dropna().reset_index(drop=True)

print(df)

#data.csvには、xとyが含まれています。最小二乗法で回帰分析を行います。
import statsmodels.api as sm
X = df["x"]
y = df["y"]


# 最初の年（1行目）は差分が取れないため除外
model = sm.OLS(y, sm.add_constant(X)).fit()
#yの回帰係数を表示する
print("回帰係数",model.params)
residual_sum_of_squares = sum(model.resid ** 2)
print("残差平方和:", residual_sum_of_squares)
print("yの平均値",y.mean())
total_sum_of_squares = sum((y - y.mean()) ** 2)
print("総平方和:", total_sum_of_squares)

model = sm.OLS(y, X).fit()
print(model.summary())