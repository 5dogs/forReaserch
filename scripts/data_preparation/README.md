# データ準備スクリプト

このフォルダには、`demand_regression_data_raw.csv`を準備・更新するためのスクリプトが含まれています。

## スクリプト一覧

### 00_prepare_log_transformed_data.py
**対数変換済みデータの準備**

- `demand_regression_data_raw.csv`を読み込む
- 対数変換列（`ln_Q`, `ln_P`, `ln_GDP`, `ln_Tax_rate`）を追加
- 対数差分列（`Δln_Q`, `Δln_P`, `Δln_GDP`, `Δln_Tax_rate`）を計算
- `analysis/demand_regression_data_log_transformed.csv`として保存

**実行方法**:
```bash
python scripts/data_preparation/00_prepare_log_transformed_data.py
```

### 02_complete_consumption_data.py
**消費量データの補完**

- 欠損している`Q (liters)`データを`data/2007-2024ガソリン販売量/四半期データ_まとめ.csv`から補完

**実行方法**:
```bash
python scripts/data_preparation/02_complete_consumption_data.py
```

### 03_fix_units.py
**単位の統一**

- `Q (liters)`の単位を統一（すべて10億リットルに変換）

**実行方法**:
```bash
python scripts/data_preparation/03_fix_units.py
```

### add_gdp_data.py
**GDPデータの追加**

- `data/1994-2025_GDP四半期ごと/gaku-jg2522.csv`からGDPデータを追加

**実行方法**:
```bash
python scripts/data_preparation/add_gdp_data.py
```

### add_price_data_1990.py
**価格データの追加（1990年以降）**

- `data/1990-2025_ガソリン小売価格四半期ごと/1990-2025レギュラー現金価格.csv`から価格データを追加

**実行方法**:
```bash
python scripts/data_preparation/add_price_data_1990.py
```

### add_tax_rate_data.py
**税率データの追加（1950年以降）**

- `data/-2025ガソリン関連税四半期ごと/gasoline_tax_quarterly.csv`から税率データを追加
- `Tax_rate (%)`を計算

**実行方法**:
```bash
python scripts/data_preparation/add_tax_rate_data.py
```

## 実行順序

通常、以下の順序で実行します：

1. **データ追加**（必要に応じて）:
   - `add_gdp_data.py`
   - `add_price_data_1990.py`
   - `add_tax_rate_data.py`

2. **データ補完・修正**:
   - `02_complete_consumption_data.py`
   - `03_fix_units.py`

3. **対数変換済みデータの準備**:
   - `00_prepare_log_transformed_data.py`

## 出力ファイル

- **対数変換済みデータ**: `analysis/demand_regression_data_log_transformed.csv`
  - このファイルは分析スクリプト（`analysis/01_estimate_demand_function.py`）で使用されます

