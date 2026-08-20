# geojson, csvから道の駅の座標情報を抽出する
from collections.abc import Collection

import geojson
import pandas as pd

from app.models.geometry_point import GeometryPoint
from app.tasks import tasks


def extract_visited_stations(
    stations: geojson.FeatureCollection,
    visit_plan: pd.DataFrame,
    prefectures: Collection[str],
) -> list[GeometryPoint]:
    # trimmed_roadside_station.geojsonのうち、指定した都道府県かつlist_issue20.csvの道の駅名と一致するものだけ抽出する
    # 道の駅名は都道府県をまたいで重複することがあるため、都道府県で絞り込む
    visit_names = {_normalize_station_name(name) for name in visit_plan["道の駅名"]}

    points = []
    for feature in stations["features"]:
        properties = feature["properties"]
        if properties["P35_003"] not in prefectures:
            continue
        name = properties["P35_006"]
        if _normalize_station_name(name) not in visit_names:
            continue
        longitude, latitude = feature["geometry"]["coordinates"]
        points.append(GeometryPoint(name, latitude, longitude))
    return points


def extract_stations(stations: geojson.FeatureCollection) -> list[GeometryPoint]:
    # roadside_station_diff.geojson, departure_point.geojsonの全featureを座標情報に変換する
    points = []
    for feature in stations["features"]:
        name = feature["properties"]["P35_006"]
        longitude, latitude = feature["geometry"]["coordinates"]
        points.append(GeometryPoint(name, latitude, longitude))
    return points


def _normalize_station_name(name: str) -> str:
    # CSVのタイトルは「道の駅」の接頭辞や空白の有無が揺れているため、P35_006と比較できる形に揃える
    return name.replace("道の駅", "").replace(" ", "").replace("　", "")


if __name__ == "__main__":
    visited = extract_visited_stations(
        tasks.read_trimmed_roadside_station(),
        tasks.read_visit_plan(),
        ["茨城県", "千葉県"],
    )
    print(f"訪問予定の道の駅: {len(visited)}件")
    for point in visited:
        print(point)

    diff_stations = extract_stations(tasks.read_roadside_station_diff())
    print(f"\n新規登録の道の駅: {len(diff_stations)}件")
    for point in diff_stations:
        print(point)

    departure = extract_stations(tasks.read_departure_point())
    print(f"\n出発地: {len(departure)}件")
    for point in departure:
        print(point)
