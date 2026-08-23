from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.route import Route
from tsp_kanto.models.tsp_answer import TSPAnswer


def write_geojson(answer: TSPAnswer, output_path: Path) -> None:
    routes = answer.routes
    features = [_route_to_feature(order, route) for order, route in enumerate(routes, start=1)]
    points = [routes[0].from_, *(route.to for route in routes)]
    features += [_point_to_feature(order, point) for order, point in enumerate(points)]

    feature_collection = {"type": "FeatureCollection", "features": features}

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


def _point_to_feature(order: int, point: GeometryPoint) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [point.longitude, point.latitude]},
        "properties": {"order": order, "name": point.name},
    }
