from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass(frozen=True)
class ConstType:
    ORS_PROFILE: str = "driving-car"
    ORS_BASE_URL: str = "https://api.openrouteservice.org/v2/directions"
    TARGET_PREFECTURES: tuple[str, ...] = ("茨城県", "千葉県")
    ROUTE_CACHE_PATH: Path = _PROJECT_ROOT / "cache" / "route_cache.json"
    OUTPUT_PATH: Path = _PROJECT_ROOT / "output" / "tsp_route.geojson"


@dataclass(frozen=True)
class EnvType:
    ORS_API_KEY: str = os.environ["ORS_API_KEY"]


Const = ConstType()
Env = EnvType()
