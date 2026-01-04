# 税率除外版モデル分析

このフォルダには、税率変数を除外した需要関数推定スクリプトが含まれています。

## 概要

多重共線性の問題を解決するため、相対価格（P_relative）と税率（Tax_rate）の強い負の相関（-0.9671）により、税率変数を除外したモデルを推定します。

## モデル仕様

**推定式：**
```
ln(Q) = C + α×ln(GDP) + β×ln(P_relative) + δ1×D2008 + δ2×D2020 + δ3×D2009 + ε
```

**説明変数：**
- ln(GDP): 実質GDPの対数
- ln(P_relative): 相対価格の対数（名目価格/CPI）
- D2008: 2008年暫定税率失効ダミー
- D2020: 2020年COVID-19ダミー
- D2009: 2009年金融危機ダミー

**除外した変数：**
- ln(Tax_rate): 実効従量税率の対数（多重共線性の問題により除外）

## スクリプト一覧

このフォルダには以下のスクリプトが含まれています：

1. **01_estimate_demand_function_annual_level_model_excl_tax.py**
   - 需要関数の推定（税率除外版）
   - 出力: 係数結果（JSON、CSV）、分析データ

2. **02_calculate_consumer_surplus.py**
   - 消費者余剰の計算
   - 入力: 01の推定結果
   - 出力: 消費者余剰計算結果（CSV）

3. **03_visualize_results.py**
   - 分析結果の可視化（グラフ01-03）
   - 入力: 01の推定結果、02の消費者余剰結果
   - 出力: グラフ（PNG形式）
   - **注意**: グラフ01から税率弾力性（γ）を除外

4. **04_analyze_cpi_contribution.py**
   - CPIへのガソリン価格寄与度分析
   - 出力: CPI寄与度分析結果（CSV）、グラフ（04-06）

5. **05_create_additional_graphs.py**
   - 追加グラフの作成（グラフ07-08）
   - 入力: 04のCPI分析結果、02の消費者余剰結果
   - 出力: グラフ（PNG形式）

6. **06_simulate_fixed_vs_advalorem_tax.py**
   - 固定税額と従価税率の比較シミュレーション
   - 入力: 04のCPI分析結果
   - 出力: シミュレーション結果（CSV）、グラフ（09）

## 実行方法

プロジェクトのルートディレクトリから順番に実行：

```bash
# 1. 需要関数の推定
python3 analysis/excl_tax/01_estimate_demand_function_annual_level_model_excl_tax.py

# 2. 消費者余剰の計算
python3 analysis/excl_tax/02_calculate_consumer_surplus.py

# 3. 分析結果の可視化（グラフ01-03）
python3 analysis/excl_tax/03_visualize_results.py

# 4. CPI寄与度分析（グラフ04-06）
python3 analysis/excl_tax/04_analyze_cpi_contribution.py

# 5. 追加グラフの作成（グラフ07-08）
python3 analysis/excl_tax/05_create_additional_graphs.py

# 6. 固定税vs従価税シミュレーション（グラフ09）
python3 analysis/excl_tax/06_simulate_fixed_vs_advalorem_tax.py
```

## 出力ファイル

### 結果ファイル（`analysis/results/excl_tax/`）

- `01_analysis_data_annual_level_model_excl_tax.csv`: 分析データ
- `01_demand_function_coefficients_annual_level_model_excl_tax.csv`: 係数結果
- `01_coefficients_annual_level_model_excl_tax.json`: 係数結果（JSON形式、VIF値含む）
- `02_consumer_surplus_results.csv`: 消費者余剰計算結果
- `04_cpi_contribution_analysis.csv`: CPI寄与度分析結果
- `06_fixed_vs_advalorem_simulation.csv`: 固定税vs従価税シミュレーション結果

### グラフファイル（`analysis/figures/excl_tax/`）

- `01_demand_function_coefficients.png`: 需要関数の係数（税率弾力性除外）
- `02_consumer_surplus_increase.png`: 消費者余剰の増分推移
- `03_cumulative_consumer_surplus.png`: 累積消費者余剰の推移
- `04_gasoline_price_base_vs_tax_inclusive.png`: 本体価格と税込み価格の推移
- `05_cpi_contribution_comparison.png`: CPIへの寄与度の比較
- `06_gasoline_price_composition.png`: 価格構成の内訳
- `07_coefficient_of_variation_comparison.png`: 変動係数の比較
- `08_policy_event_impact_decomposition.png`: 政策イベント別の影響の分解
- `09_fixed_vs_advalorem_tax_comparison.png`: 固定税vs従価税の比較

## 主な特徴

1. **多重共線性の診断**
   - VIF値の計算と表示
   - VIF > 10 の変数があれば警告を表示

2. **相関マトリックスの表示**
   - 変数間の相関を確認

3. **価格弾力性の符号チェック**
   - βが負の値かどうかを確認し、理論との整合性を表示

## 元のモデルとの比較

元のモデル（税率含む）との比較については、以下を参照：
- `analysis/results/model_comparison_and_methodology_changes.md`

