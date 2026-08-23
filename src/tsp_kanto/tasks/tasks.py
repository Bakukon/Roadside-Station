# resources_Kanto/にあるgeojson, txtを読み取る
from pathlib import Path

import geojson

RESOURCES_DIR = Path(__file__).parent.parent / "resources_Kanto"


def read_trimmed_roadside_station() -> geojson.FeatureCollection:
    # 全国の道の駅データ(2018年度版)
    return _read_geojson(RESOURCES_DIR / "trimmed_roadside_station.geojson")


def read_roadside_station_diff() -> geojson.FeatureCollection:
    # 関東整備局管内で2019年度以降に新規登録された道の駅
    return _read_geojson(RESOURCES_DIR / "roadside_station_diff.geojson")


def read_roadside_station_abolished() -> geojson.FeatureCollection:
    # 関東整備局管内で2019年度以降に登録解除された道の駅
    return _read_geojson(RESOURCES_DIR / "roadside_station_abolished.geojson")


def read_excepted_from_kanto() -> list[str]:
    # 長野県内の道の駅のうち、関東整備局管外のため対象から除外する名前一覧
    text = (RESOURCES_DIR / "excepted_from_Kanto.txt").read_text(encoding="utf-8").strip()
    return text.split("、")


def _read_geojson(file_path: Path) -> geojson.FeatureCollection:
    with file_path.open(encoding="utf-8") as f:
        return geojson.load(f)
