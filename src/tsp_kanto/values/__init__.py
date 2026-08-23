from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass(frozen=True)
class ConstType:
    TARGET_PREFECTURES: tuple[str, ...] = (
        "東京都",
        "千葉県",
        "神奈川県",
        "埼玉県",
        "茨城県",
        "群馬県",
        "栃木県",
        "山梨県",
        "長野県",
    )
    DEPARTURE_STATION_NAME: str = "いちかわ"
    OUTPUT_PATH: Path = _PROJECT_ROOT / "tsp_kanto" / "output" / "tsp_route.geojson"


Const = ConstType()
