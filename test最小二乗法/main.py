#data.csvの読み込み
import pandas as pd
df = pd.read_csv("data.csv")
df = df.dropna().reset_index(drop=True)

print(df)

#data.csvには、xとyが含まれています。最小二乗法で回帰分析を行います。
import statsmodels.api as sm
X = df["x"]
y = df["y"]

# ▼▼▼ モデル１：切片ありモデル ▼▼▼
# こちらのモデルでは .summary() を表示していません
model_with_intercept = sm.OLS(y, sm.add_constant(X)).fit()
print("回帰係数", model_with_intercept.params) 
#回帰式の切片を計算する
intercept = model_with_intercept.params[0]
print("切片:", intercept)
residual_sum_of_squares = sum(model_with_intercept.resid ** 2)# 残差平方和の計算式をいかに表示させる

print("残差平方和:", residual_sum_of_squares)
print("yの平均値",y.mean())
total_sum_of_squares = sum((y - y.mean()) ** 2)
print("総平方和:", total_sum_of_squares)

# 手動で R-squared (切片ありモデル) を計算すると:
r_squared_calculated = 1 - (residual_sum_of_squares / total_sum_of_squares)
print(f"手動計算の決定係数 (切片ありモデル): {r_squared_calculated}") # ★おそらくこの値がスプレッドシートの値に近いはず
