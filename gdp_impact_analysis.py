import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# ----------------------------------------
# GDPによる消費者余剰増加分の分析
# ----------------------------------------

def load_and_prepare_data():
    """データの読み込みと前処理"""
    df = pd.read_csv("sample_demand_regression_data.csv")
    df = df.rename(columns={
        "Q (millions)": "Q",
        "GDP (trillion yen)": "GDP", 
        "P (thousand yen)": "P"
    })
    
    # 対数変換
    df["ln_Q"] = np.log(df["Q"])
    df["ln_GDP"] = np.log(df["GDP"])
    df["ln_P"] = np.log(df["P"])
    
    return df

def estimate_demand_function(df):
    """需要関数の推定"""
    X = df[["ln_GDP", "ln_P"]]
    X = sm.add_constant(X)
    y = df["ln_Q"]
    
    model = sm.OLS(y, X).fit()
    print("\n--- 回帰結果 ---")
    print(model.summary())
    
    return model

def calculate_gdp_impact(df, model, base_year=2011):
    """
    GDPによる消費者余剰増加分を計算
    
    アプローチ：
    1. ベースライン年（2011年）の価格・数量を基準とする
    2. 各年でGDPのみを変化させ、価格はベースライン年と同じと仮定
    3. その場合の需要量を推定
    4. 消費者余剰を計算し、ベースライン年との差分を求める
    """
    
    # ベースライン年のデータ
    base_data = df[df["Year"] == base_year].iloc[0]
    base_gdp = base_data["GDP"]
    base_price = base_data["P"]
    
    # 回帰係数
    alpha = model.params["ln_GDP"]  # GDP弾力性
    beta = model.params["ln_P"]     # 価格弾力性
    const = model.params["const"]   # 定数項
    
    # 価格弾力性（消費者余剰計算用）
    epsilon = beta
    
    print(f"\n--- ベースライン年: {base_year} ---")
    print(f"ベースGDP: {base_gdp:.1f}兆円")
    print(f"ベース価格: {base_price:.1f}千円")
    print(f"GDP弾力性(α): {alpha:.4f}")
    print(f"価格弾力性(β): {beta:.4f}")
    
    # 各年でのGDP影響を計算
    results = []
    
    for _, row in df.iterrows():
        year = row["Year"]
        actual_gdp = row["GDP"]
        actual_price = row["P"]
        actual_q = row["Q"]
        
        # GDPのみを変化させた場合の需要量を推定
        # ln(Q_gdp_only) = const + α*ln(GDP) + β*ln(P_base)
        ln_q_gdp_only = const + alpha * np.log(actual_gdp) + beta * np.log(base_price)
        q_gdp_only = np.exp(ln_q_gdp_only)
        
        # GDPのみの影響による消費者余剰
        cs_gdp_only = (epsilon / (1 + epsilon)) * base_price * q_gdp_only
        
        # ベースライン年の消費者余剰
        ln_q_base = const + alpha * np.log(base_gdp) + beta * np.log(base_price)
        q_base = np.exp(ln_q_base)
        cs_base = (epsilon / (1 + epsilon)) * base_price * q_base
        
        # GDPによる増加分
        gdp_impact = cs_gdp_only - cs_base
        
        # 実際の消費者余剰（比較用）
        cs_actual = (epsilon / (1 + epsilon)) * actual_price * actual_q
        
        results.append({
            "Year": year,
            "GDP": actual_gdp,
            "Price": actual_price,
            "Q_actual": actual_q,
            "Q_gdp_only": q_gdp_only,
            "CS_actual": cs_actual,
            "CS_gdp_only": cs_gdp_only,
            "CS_base": cs_base,
            "GDP_Impact": gdp_impact,
            "GDP_Impact_Rate": gdp_impact / cs_base * 100 if cs_base != 0 else 0
        })
    
    return pd.DataFrame(results)

def create_visualizations(df_results):
    """グラフの作成"""
    
    # 日本語フォント設定
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 1. GDPによる消費者余剰増加分の推移
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # GDP影響の推移
    axes[0, 0].plot(df_results["Year"], df_results["GDP_Impact"], 
                    marker='o', linewidth=2, markersize=6, color='blue')
    axes[0, 0].set_title("GDPによる消費者余剰増加分の推移", fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel("年")
    axes[0, 0].set_ylabel("GDP影響（千円×百万個）")
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    # GDP影響率の推移
    axes[0, 1].plot(df_results["Year"], df_results["GDP_Impact_Rate"], 
                    marker='s', linewidth=2, markersize=6, color='green')
    axes[0, 1].set_title("GDP影響率の推移（ベースライン年比）", fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel("年")
    axes[0, 1].set_ylabel("GDP影響率（%）")
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    # GDP成長率と消費者余剰増加分の関係
    gdp_growth = df_results["GDP"].pct_change() * 100
    axes[1, 0].scatter(gdp_growth[1:], df_results["GDP_Impact"][1:], 
                      s=60, alpha=0.7, color='purple')
    axes[1, 0].set_title("GDP成長率と消費者余剰増加分の関係", fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel("GDP成長率（%）")
    axes[1, 0].set_ylabel("GDP影響（千円×百万個）")
    axes[1, 0].grid(True, alpha=0.3)
    
    # 累積GDP影響
    cumulative_impact = df_results["GDP_Impact"].cumsum()
    axes[1, 1].plot(df_results["Year"], cumulative_impact, 
                    marker='D', linewidth=2, markersize=6, color='orange')
    axes[1, 1].set_title("累積GDP影響", fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel("年")
    axes[1, 1].set_ylabel("累積GDP影響（千円×百万個）")
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 2. 詳細比較グラフ
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = df_results["Year"]
    width = 0.25
    
    ax.bar(x - width, df_results["CS_actual"], width, label='実際の消費者余剰', alpha=0.8)
    ax.bar(x, df_results["CS_gdp_only"], width, label='GDPのみの影響', alpha=0.8)
    ax.bar(x + width, df_results["CS_base"], width, label='ベースライン年', alpha=0.8)
    
    ax.set_title("消費者余剰の比較：実際 vs GDP影響のみ vs ベースライン", fontsize=14, fontweight='bold')
    ax.set_xlabel("年")
    ax.set_ylabel("消費者余剰（千円×百万個）")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def print_summary_table(df_results):
    """サマリーテーブルの表示"""
    print("\n" + "="*80)
    print("GDPによる消費者余剰影響分析 - サマリーテーブル")
    print("="*80)
    
    # 主要指標の表示
    summary_cols = ["Year", "GDP", "GDP_Impact", "GDP_Impact_Rate", "Q_actual", "Q_gdp_only"]
    summary_df = df_results[summary_cols].copy()
    
    # 列名を日本語に
    summary_df.columns = ["年", "GDP(兆円)", "GDP影響", "GDP影響率(%)", "実際のQ", "GDPのみのQ"]
    
    # 数値のフォーマット
    summary_df["GDP(兆円)"] = summary_df["GDP(兆円)"].round(1)
    summary_df["GDP影響"] = summary_df["GDP影響"].round(2)
    summary_df["GDP影響率(%)"] = summary_df["GDP影響率(%)"].round(2)
    summary_df["実際のQ"] = summary_df["実際のQ"].round(2)
    summary_df["GDPのみのQ"] = summary_df["GDPのみのQ"].round(2)
    
    print(summary_df.to_string(index=False))
    
    # 統計サマリー
    print(f"\n--- 統計サマリー ---")
    print(f"平均GDP影響: {df_results['GDP_Impact'].mean():.2f} (千円×百万個)")
    print(f"最大GDP影響: {df_results['GDP_Impact'].max():.2f} (千円×百万個) - {df_results.loc[df_results['GDP_Impact'].idxmax(), 'Year']}年")
    print(f"最小GDP影響: {df_results['GDP_Impact'].min():.2f} (千円×百万個) - {df_results.loc[df_results['GDP_Impact'].idxmin(), 'Year']}年")
    print(f"累積GDP影響: {df_results['GDP_Impact'].sum():.2f} (千円×百万個)")

def main():
    """メイン実行関数"""
    print("GDPによる消費者余剰影響分析を開始します...")
    
    # データ読み込み
    df = load_and_prepare_data()
    
    # 需要関数の推定
    model = estimate_demand_function(df)
    
    # GDP影響の計算
    df_results = calculate_gdp_impact(df, model)
    
    # 結果の表示
    print_summary_table(df_results)
    
    # グラフの作成
    create_visualizations(df_results)
    
    # 結果をCSVに保存
    df_results.to_csv("gdp_impact_analysis.csv", index=False, encoding='utf-8-sig')
    print(f"\n結果を 'gdp_impact_analysis.csv' に保存しました。")

if __name__ == "__main__":
    main()
