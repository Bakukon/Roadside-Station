# geojsonから道の駅の座標情報を抽出する
from collections.abc import Collection

import geojson

from tsp_kanto.models.geometry_point import GeometryPoint


def extract_target_stations(
    stations: geojson.FeatureCollection,
    prefectures: Collection[str],
    excluded_names: Collection[str],
) -> list[GeometryPoint]:
    # trimmed_roadside_station.geojsonのうち、指定した都道府県かつexcluded_namesに含まれないものだけ抽出する
    excluded = {_normalize_station_name(name) for name in excluded_names}

    points = []
    for feature in stations["features"]:
        properties = feature["properties"]
        if properties["P35_003"] not in prefectures:
            continue
        name = properties["P35_006"]
        if _normalize_station_name(name) in excluded:
            continue
        longitude, latitude = feature["geometry"]["coordinates"]
        points.append(GeometryPoint(name, latitude, longitude))
    return points


def extract_stations(stations: geojson.FeatureCollection) -> list[GeometryPoint]:
    # roadside_station_diff.geojson, roadside_station_abolished.geojson, departure_point.geojsonの全featureを座標情報に変換する
    points = []
    for feature in stations["features"]:
        name = feature["properties"]["P35_006"]
        longitude, latitude = feature["geometry"]["coordinates"]
        points.append(GeometryPoint(name, latitude, longitude))
    return points


def _normalize_station_name(name: str) -> str:
    # 「道の駅」の接頭辞や全角/半角スペースの有無が揺れているため、比較できる形に揃える
    return name.replace("道の駅", "").replace(" ", "").replace("　", "")
