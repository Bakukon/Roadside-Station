# tsp

道の駅（千葉県・茨城県）を巡回する経路を求める TSP（巡回セールスマン問題）ソルバー。
OpenRouteService (ORS) API から実際の道路ルートを取得し、複数のアルゴリズムで最適な巡回順序を計算、結果を GeoJSON として出力する。

## ディレクトリ構成

```
src/
├── tsp/            本体
│   ├── clients/    外部API・キャッシュ
│   ├── models/     データモデル
│   ├── solvers/    TSPソルバー（アルゴリズム本体）
│   ├── tasks/      resources/ の読み込み処理
│   ├── values/     定数・環境変数
│   ├── main.py     エントリーポイント
│   ├── geojson_writer.py  結果をGeoJSONに書き出す
│   └── json_route.py      ルートのJSONシリアライズ
├── resources/      入力データ（道の駅一覧、出発地など）
└── output/         各ソルバーの計算結果（GeoJSON）
```

## tsp/main.py

処理の起点。以下の流れで実行される。

1. `resources/` のデータから訪問対象の道の駅・出発地を読み込む
2. `OrsClient` と `RouteCache` を使って `TspContext` を構築
3. ソルバー（例: `held_karp.solve`）で巡回順序を求める
4. `geojson_writer.write_geojson` で結果を `output/` に書き出す

## tsp/clients/ — 外部連携

| ファイル | 役割 |
|---|---|
| [ors_client.py](tsp/clients/ors_client.py) | OpenRouteService API を呼び出し、2地点間の実際の道路ルート（距離・所要時間・ポリライン）を取得。リトライ処理あり |
| [route_cache.py](tsp/clients/route_cache.py) | 2地点間ルートの計算結果をJSONファイルにキャッシュし、API呼び出し回数を削減 |

## tsp/models/ — データモデル

| ファイル | 役割 |
|---|---|
| [geometry_point.py](tsp/models/geometry_point.py) | 緯度経度を持つ地点（道の駅・出発地など）を表す |
| [route.py](tsp/models/route.py) | 2地点間のルート（距離・所要時間・エンコード済みポリライン）を表す |
| [polyline_encoder.py](tsp/models/polyline_encoder.py) | Google方式のエンコード済みポリラインの符号化/復号 |
| [tsp_context.py](tsp/models/tsp_context.py) | ソルバーに渡す実行コンテキスト（対象地点、出発地、APIクライアント、キャッシュ） |
| [tsp_answer.py](tsp/models/tsp_answer.py) | TSPソルバーの計算結果（訪問順のルート列）を表す |

## tsp/solvers/ — TSPアルゴリズム

すべて共通の `SolverContext`（[nearest_neighbor.py](tsp/solvers/nearest_neighbor.py) で定義）を受け取り、`TSPAnswer` を返す。

| ファイル | アルゴリズム |
|---|---|
| [nearest_neighbor.py](tsp/solvers/nearest_neighbor.py) | 最近傍法（貪欲法）。他ソルバーの初期解生成にも利用 |
| [held_karp.py](tsp/solvers/held_karp.py) | Held-Karpアルゴリズム（動的計画法による厳密解） |
| [two_opt_LS.py](tsp/solvers/two_opt_LS.py) | 2-opt 局所探索法 |
| [two_opt_ILS.py](tsp/solvers/two_opt_ILS.py) | 2-opt + 反復局所探索法（Iterated Local Search） |
| [two_opt_SA.py](tsp/solvers/two_opt_SA.py) | 2-opt + 焼きなまし法（Simulated Annealing） |
| [three_opt_LS.py](tsp/solvers/three_opt_LS.py) | 3-opt 局所探索法 |
| [three_opt_ILS.py](tsp/solvers/three_opt_ILS.py) | 3-opt + 反復局所探索法 |

## tsp/tasks/ — 入力データ読み込み

| ファイル | 役割 |
|---|---|
| [tasks.py](tsp/tasks/tasks.py) | `resources/` 配下のGeoJSON/CSVファイルを読み込む |
| [resource_reader.py](tsp/tasks/resource_reader.py) | 読み込んだデータから道の駅の座標情報（`GeometryPoint`）を抽出・加工する |

## tsp/values/

[`__init__.py`](tsp/values/__init__.py) にて定数（対象都道府県、ORSのプロファイル/URL、キャッシュパスなど）と環境変数（`ORS_API_KEY`）を定義。

## resources/ — 入力データ

- `P35-18_Roadside_Station.geojson` / `trimmed_roadside_station.geojson`: 全国道の駅データ（国土数値情報）とその抽出版
- `departure_point.geojson`: 出発地点
- `roadside_station_diff.geojson`: 新規登録された道の駅の差分データ
- `list_issue20.csv`: 訪問対象の道の駅名一覧
- `remove_properties.py`: GeoJSONの不要なプロパティを除去する前処理スクリプト

## output/

各ソルバーで計算した巡回ルートのGeoJSON出力先（`TSP_NN_*.geojson`, `held-karp.geojson`, `two_opt_LS.geojson` など）。地図上に可視化して比較できる。
