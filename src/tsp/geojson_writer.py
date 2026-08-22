from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tsp.models.route import Route
from tsp.models.tsp_answer import TSPAnswer


def write_geojson(answer: TSPAnswer, output_path: Path) -> None:
    feature_collection = {
        "type": "FeatureCollection",
        "features": [_route_to_feature(order, route) for order, route in enumerate(answer.routes, start=1)],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(feature_collection, ensure_ascii=False, indent=2), encoding="utf-8")


def _route_to_feature(order: int, route: Route) -> dict[str, Any]:
    coordinates = [[p.longitude, p.latitude] for p in route.polyline_decoded]
    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coordinates},
        "properties": {
            "order": order,
            "from": route.from_.name,
            "to": route.to.name,
            "title": route.title,
            "distance_meters": route.distance_meters,
            "duration_seconds": route.duration.total_seconds(),
        },
    }
