import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy import stats

# ----------------------------------------
# ガソリン税による消費者余剰分析
# 消費者余剰測定方法まとめの手法に基づく
# ----------------------------------------

def load_data():
    """データの読み込みと前処理"""
    print("データを読み込み中...")
    df = pd.read_csv("sample_demand_regression_data.csv")
    df_log = pd.read_csv("sample_demand_regression_data2.csv")
    
    print(f"データ期間: {df['Year'].min()}年 - {df['Year'].max()}年")
    print(f"データ件数: {len(df)}件")
    
    return df, df_log

def estimate_demand_function(df_log):
    """
    需要関数の推定
    ⊿lnQ = α×⊿lnGDP + β×⊿lnP + γ×⊿lnTax_rate + ε
    """
    print("\n" + "="*60)
    print("需要関数の推定")
    print("="*60)
    
    # 説明変数と被説明変数の準備
    X = df_log[['Δln(GDP)', 'Δln(P)', 'Δln(Tax_rate)']].dropna()
    y = df_log['Δln(Q)'].dropna()
    
    # 定数項を追加
    X = sm.add_constant(X)
    
    # 回帰分析の実行
    model = sm.OLS(y, X).fit()
    
    print("回帰結果:")
    print(model.summary())
    
    # 係数の取得
    alpha = model.params['Δln(GDP)']      # 所得弾力性
    beta = model.params['Δln(P)']         # 価格弾力性
    gamma = model.params['Δln(Tax_rate)'] # 税率弾力性
    const = model.params['const']         # 定数項
    
    print(f"\n推定された係数:")
    print(f"所得弾力性 (α): {alpha:.4f}")
    print(f"価格弾力性 (β): {beta:.4f}")
    print(f"税率弾力性 (γ): {gamma:.4f}")
    print(f"定数項: {const:.4f}")
    
    return model, alpha, beta, gamma, const

def calculate_consumer_surplus(df, alpha, beta, gamma):
    """
    消費者余剰の計算
    測定方法総論の手法に基づく:
    1. 価格要因の寄与率を計算
    2. 需要増加分のうち価格要因によって説明される部分を計算
    3. 消費者余剰の増分となる台形の面積を計算
    """
    print("\n" + "="*60)
    print("消費者余剰の計算")
    print("="*60)
    
    # 対数変換
    df['ln_Q'] = np.log(df['Q (liters)'])
    df['ln_P'] = np.log(df['P (yen/liter)'])
    df['ln_GDP'] = np.log(df['GDP (trillion yen)'])
    df['ln_Tax_rate'] = np.log(df['Tax_rate (%)'])
    
    # 前年比変化率の計算
    df['Δln_Q'] = df['ln_Q'].diff()
    df['Δln_P'] = df['ln_P'].diff()
    df['Δln_GDP'] = df['ln_GDP'].diff()
    df['Δln_Tax_rate'] = df['ln_Tax_rate'].diff()
    
    # 価格弾力性（消費者余剰計算用）
    epsilon = beta
    
    # 各年の消費者余剰を計算
    results = []
    
    for i in range(1, len(df)):  # 最初の年は除外
        year = df.iloc[i]['Year']
        q_prev = df.iloc[i-1]['Q (liters)']
        q_curr = df.iloc[i]['Q (liters)']
        p_prev = df.iloc[i-1]['P (yen/liter)']
        p_curr = df.iloc[i]['P (yen/liter)']
        
        # 価格要因の寄与率を計算
        # Xt+1 = β(exp(lnPt+1－lnPt)－1)／(exp(lnQt+1－lnQt)－1)
        if q_curr != q_prev:
            price_contribution = beta * (np.exp(np.log(p_curr) - np.log(p_prev)) - 1) / (np.exp(np.log(q_curr) - np.log(q_prev)) - 1)
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
        
        # 累積消費者余剰
        if i == 1:
            cumulative_cs = cs_increase
        else:
            cumulative_cs = results[-1]['Cumulative_CS'] + cs_increase
        
        # 価格弾力性を用いた近似計算（比較用）
        cs_approximation = (epsilon / (1 + epsilon)) * p_curr * q_curr
        
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
            'CS_Approximation': cs_approximation
        })
    
    return pd.DataFrame(results)

def analyze_tax_impact(df, results):
    """
    税制効果の分析
    """
    print("\n" + "="*60)
    print("税制効果の分析")
    print("="*60)
    
    # 税率が変化した年を特定（今回は全期間同じ税率なので、価格変化に焦点）
    price_changes = results[results['P_curr'] != results['P_prev']].copy()
    
    if len(price_changes) > 0:
        print(f"価格変化があった年数: {len(price_changes)}年")
        print(f"平均価格変化率: {((price_changes['P_curr'] / price_changes['P_prev'] - 1) * 100).mean():.2f}%")
        print(f"平均消費者余剰増分: {price_changes['CS_Increase'].mean():.2f}")
        
        # 価格変化と消費者余剰の関係
        correlation = price_changes['P_curr'].corr(price_changes['CS_Increase'])
        print(f"価格と消費者余剰増分の相関係数: {correlation:.4f}")
    
    return price_changes

def print_chart_legend():
    """
    グラフの英語タイトルと日本語の対応表を出力
    """
    print("\n" + "="*60)
    print("Chart Legend (English Title - Japanese Translation)")
    print("="*60)
    print("1. Gasoline Price Trend - ガソリン価格の推移")
    print("2. Gasoline Consumption Trend - ガソリン消費量の推移")
    print("3. Consumer Surplus Increase Trend - 消費者余剰増分の推移")
    print("4. Cumulative Consumer Surplus Trend - 累積消費者余剰の推移")
    print("5. Gasoline Price vs Consumer Surplus Relationship - ガソリン価格と消費者余剰増分の関係")
    print("\nAxis Labels:")
    print("- Year - 年")
    print("- Price (yen/liter) - 価格（円/リットル）")
    print("- Consumption (billion liters) - 消費量（億リットル）")
    print("- Consumer Surplus Increase - 消費者余剰増分")
    print("- Cumulative Consumer Surplus - 累積消費者余剰")
    print("="*60)

def create_visualizations(df, results):
    """
    グラフの作成（英語表記）
    """
    print("\nCreating visualizations...")
    
    # 英語タイトルと日本語の対応表を出力
    print_chart_legend()
    
    # 1. ガソリン価格と消費量の推移
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 価格推移
    axes[0, 0].plot(df['Year'], df['P (yen/liter)'], marker='o', linewidth=2, color='red')
    axes[0, 0].set_title('Gasoline Price Trend', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Price (yen/liter)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 消費量推移
    axes[0, 1].plot(df['Year'], df['Q (liters)'], marker='s', linewidth=2, color='blue')
    axes[0, 1].set_title('Gasoline Consumption Trend', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('Consumption (billion liters)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 消費者余剰増分
    axes[1, 0].bar(results['Year'], results['CS_Increase'], alpha=0.7, color='green')
    axes[1, 0].set_title('Consumer Surplus Increase Trend', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Consumer Surplus Increase')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    # 累積消費者余剰
    axes[1, 1].plot(results['Year'], results['Cumulative_CS'], marker='D', linewidth=2, color='purple')
    axes[1, 1].set_title('Cumulative Consumer Surplus Trend', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('Cumulative Consumer Surplus')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 2. 価格と消費者余剰の関係
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(results['P_curr'], results['CS_Increase'], 
                        c=results['Year'], cmap='viridis', s=60, alpha=0.7)
    ax.set_title('Gasoline Price vs Consumer Surplus Relationship', fontsize=14, fontweight='bold')
    ax.set_xlabel('Gasoline Price (yen/liter)')
    ax.set_ylabel('Consumer Surplus Increase')
    ax.grid(True, alpha=0.3)
    
    # カラーバー
    cbar = plt.colorbar(scatter)
    cbar.set_label('Year')
    
    plt.tight_layout()
    plt.show()

def print_summary(results):
    """
    分析結果のサマリー表示
    """
    print("\n" + "="*60)
    print("分析結果サマリー")
    print("="*60)
    
    print(f"分析期間: {results['Year'].min()}年 - {results['Year'].max()}年")
    print(f"総消費者余剰増分: {results['CS_Increase'].sum():.2f}")
    print(f"平均年間消費者余剰増分: {results['CS_Increase'].mean():.2f}")
    print(f"最大消費者余剰増分: {results['CS_Increase'].max():.2f} ({results.loc[results['CS_Increase'].idxmax(), 'Year']}年)")
    print(f"最小消費者余剰増分: {results['CS_Increase'].min():.2f} ({results.loc[results['CS_Increase'].idxmin(), 'Year']}年)")
    
    # 価格変化の影響
    price_increase_years = results[results['P_curr'] > results['P_prev']]
    if len(price_increase_years) > 0:
        print(f"\n価格上昇年数: {len(price_increase_years)}年")
        print(f"価格上昇時の平均消費者余剰変化: {price_increase_years['CS_Increase'].mean():.2f}")

def main():
    """メイン実行関数"""
    print("ガソリン税による消費者余剰分析を開始します...")
    print("消費者余剰測定方法まとめの手法に基づく分析")
    
    try:
        # データの読み込み
        df, df_log = load_data()
        
        # 需要関数の推定
        model, alpha, beta, gamma, const = estimate_demand_function(df_log)
        
        # 消費者余剰の計算
        results = calculate_consumer_surplus(df, alpha, beta, gamma)
        
        # 税制効果の分析
        price_changes = analyze_tax_impact(df, results)
        
        # 結果の表示
        print_summary(results)
        
        # グラフの作成
        create_visualizations(df, results)
        
        # 結果をCSVに保存
        results.to_csv("gasoline_consumer_surplus_analysis.csv", index=False, encoding='utf-8-sig')
        print(f"\n分析結果を 'gasoline_consumer_surplus_analysis.csv' に保存しました。")
        
        print("\n分析が完了しました！")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
