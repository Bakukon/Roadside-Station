import json
from pathlib import Path

DATA_DIR = Path(__file__).parent
INPUT_PATH = DATA_DIR / "P35-18_Roadside_Station.geojson"
OUTPUT_PATH = DATA_DIR / "trimmed_roadside_station.geojson"
REMOVE_KEYS = [f"P35_{i:03d}" for i in range(7, 29)]


def main() -> None:
    geojson = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    geojson["features"] = [remove_properties(feature) for feature in geojson["features"]]
    OUTPUT_PATH.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")


def remove_properties(feature: dict) -> dict:
    properties = {key: value for key, value in feature["properties"].items() if key not in REMOVE_KEYS}
    return {**feature, "properties": properties}


if __name__ == "__main__":
    main()
