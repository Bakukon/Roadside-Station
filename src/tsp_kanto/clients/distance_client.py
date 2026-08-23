from __future__ import annotations

import json
from datetime import timedelta
from math import atan2, cos, radians, sin, sqrt

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.route import Route

_EARTH_RADIUS_METERS = 6_371_000
_ASSUMED_SPEED_KMH = 40.0

class DistanceClient:
    """実際の道路は考慮せず、2地点間の直線距離(大圏距離)をルートとして扱う"""

    def get_route(self, from_: GeometryPoint, to: GeometryPoint) -> Route:
        distance_meters = int(_haversine_meters(from_, to))
        duration = timedelta(hours=(distance_meters / 1000) / _ASSUMED_SPEED_KMH)

        return Route(
            from_,
            to,
            f"{from_.name} → {to.name}",
            distance_meters,
            duration,
            _ASSUMED_SPEED_KMH,
            json.dumps([[from_.longitude, from_.latitude], [to.longitude, to.latitude]]),
        )


def _haversine_meters(from_: GeometryPoint, to: GeometryPoint) -> float:
    lat1, lon1, lat2, lon2 = (radians(v) for v in (from_.latitude, from_.longitude, to.latitude, to.longitude))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * _EARTH_RADIUS_METERS * atan2(sqrt(a), sqrt(1 - a))
