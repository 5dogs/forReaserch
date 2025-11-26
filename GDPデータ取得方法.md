# GDPデータ取得方法

## ✅ データ取得完了

**取得済みファイル**: `data/1994-2025_GDP四半期ごと/gaku-jg2522.csv`
- 四半期データ（1994年Q1〜2025年Q2）
- 実質GDP（2015年基準、10億円単位）
- 名目GDP（10億円単位）

**処理済み**: `demand_regression_data_raw.csv`に統合済み
- 期間: 1994Q1-2025Q1（125四半期）
- 単位: 兆円（10億円から変換）

## 📊 内閣府経済社会総合研究所（ESRI）の公式サイト

### 1. 四半期別GDP速報のメインページ
**URL**: https://www.esri.cao.go.jp/jp/sna/sokuhou/sokuhou_top.html

### 2. 統計表のダウンロードページ
**URL**: https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/files_sokuhou.html

#### 最新データ（2025年第2四半期）
**URL**: https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2025/qe252_2/gdemenuja.html

#### 過去データの例（2001年第1四半期）
**URL**: https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2001/qe011/gdemenuja.html

### 3. e-Stat（政府統計の総合窓口）
**URL**: https://www.e-stat.go.jp/

#### 検索方法
1. 「統計データを探す」→「統計データ検索」
2. キーワード: 「四半期別GDP速報」
3. 統計表ID: 0003410379（四半期別GDP速報）

## 📋 必要なデータ項目

### 先行研究で使用されている指標
- **実質GDP**: 2015年基準、10億円単位（または兆円単位）
- **名目GDP**: 10億円単位（または兆円単位）
- **四半期データ**: 1994Q1-2025Q1の期間が必要

### データの形式
- **基準年**: 2015年=100（実質GDP）
- **単位**: 10億円（または兆円）
- **頻度**: 四半期データ（Q1, Q2, Q3, Q4）

## 🔧 データ処理の手順（✅ 完了）

### ✅ 1. CSVファイルのダウンロード
- `data/1994-2025_GDP四半期ごと/gaku-jg2522.csv` を取得済み
- ファイル名「gaku-jg2522」は内閣府の統計表番号

### ✅ 2. データの読み込みと処理
- `scripts/data_preparation/add_gdp_data.py` で実行済み
- エンコーディング: UTF-8, Shift-JIS, CP932 を自動検出
- スキップ行数: 6-8行目を自動検出

### ✅ 3. 四半期データの抽出
- 四半期文字列（例: "1994/ 1- 3."）から年と四半期を抽出
- 10億円単位を兆円単位に変換（÷1000）

### ✅ 4. メインデータへの統合
- `demand_regression_data_raw.csv` に `GDP (trillion yen)` 列を追加
- YearQuarter列でマージ

## 📝 処理結果

### GDPデータの統計
- **期間**: 1994Q1 - 2025Q1（125四半期）
- **単位**: 兆円（名目GDP）
- **データソース**: 内閣府「四半期別GDP速報」

### データの特徴
- **名目GDP**: 物価変動を含むGDP
- **実質GDP**: 物価変動を除去したGDP（2015年基準）
- **注意**: 現在の分析では名目GDPを使用（実質GDPへの変換が必要な場合あり）

## 📊 分析での使用状況

### 現在の使用
- **変数名**: `GDP (trillion yen)`
- **単位**: 兆円
- **期間**: 1994Q1-2025Q1（125四半期）
- **使用モデル**: 差分モデル、レベルモデル

### 先行研究との違い
- **先行研究**: 実質GDPを使用（物価変動を除去）
- **現在の方法**: 名目GDPを使用（物価変動が含まれる）
- **改善の余地**: 実質GDPを使用することで、より純粋な所得効果を測定可能

## 🔗 参考リンク

- **内閣府経済社会総合研究所（ESRI）**: https://www.esri.cao.go.jp/
- **四半期別GDP速報**: https://www.esri.cao.go.jp/jp/sna/sokuhou/sokuhou_top.html
- **統計表一覧**: https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/files_sokuhou.html
- **e-Stat**: https://www.e-stat.go.jp/

## 📊 データファイルの保存場所

- **元データ**: `data/1994-2025_GDP四半期ごと/gaku-jg2522.csv`
- **メモファイル**: `data/1994-2025_GDP四半期ごと/memo.text`
- **統合済みデータ**: `demand_regression_data_raw.csv`（GDP列を追加）

## 📝 メモファイルの内容

`data/1994-2025_GDP四半期ごと/memo.text` には以下のURLが記載されています：

1. **統計表一覧**: https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/files_sokuhou.html
2. **最新データ（2025年第2四半期）**: https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2025/qe252_2/gdemenuja.html
3. **過去データの例（2001年第1四半期）**: https://www.esri.cao.go.jp/jp/sna/data/data_list/sokuhou/files/2001/qe011/gdemenuja.html

## 🔄 データ更新方法

### 新しい四半期データの追加
1. 内閣府の四半期別GDP速報ページから最新データをダウンロード
2. `data/1994-2025_GDP四半期ごと/gaku-jg2522.csv` に追加
3. `scripts/data_preparation/add_gdp_data.py` を再実行

### 実質GDPへの変換（今後の改善）
1. 実質GDPデータを取得（同じソースから）
2. 名目GDPを実質GDPに置き換える
3. レベルモデルで再推定（R²の改善が期待される）

