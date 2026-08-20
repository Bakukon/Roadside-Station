# Resources/にあるgeojson, csvを読み取る
from pathlib import Path

import geojson
import pandas as pd

RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"


def read_trimmed_roadside_station() -> geojson.FeatureCollection:
    # P35-18_Roadside_Station.geojsonをトリムしたもの
    return _read_geojson(RESOURCES_DIR / "trimmed_roadside_station.geojson")


def read_roadside_station_diff() -> geojson.FeatureCollection:
    # H30年度版から新規登録された道の駅
    return _read_geojson(RESOURCES_DIR / "roadside_station_diff.geojson")


def read_departure_point() -> geojson.FeatureCollection:
    # 出発地情報
    return _read_geojson(RESOURCES_DIR / "departure_point.geojson")


def read_visit_plan() -> pd.DataFrame:
    # 訪問予定の道の駅名、GoogleMapのURL
    df = pd.read_csv(RESOURCES_DIR / "list_issue20.csv", usecols=["タイトル", "URL"])
    df = df.dropna(subset=["タイトル"])
    return df.rename(columns={"タイトル": "道の駅名", "URL": "GoogleMapURL"})


def _read_geojson(file_path: Path) -> geojson.FeatureCollection:
    with file_path.open(encoding="utf-8") as f:
        return geojson.load(f)
