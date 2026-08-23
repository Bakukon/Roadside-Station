from __future__ import annotations

import json
import time
from datetime import timedelta

import requests

from tsp.models.geometry_point import GeometryPoint
from tsp.models.route import Route
from tsp.values import Const

_MAX_ATTEMPTS = 3
_RETRY_WAIT_SECONDS = 5.0
_TIMEOUT_SECONDS = 30.0

class OrsClient:
    def __init__(self, api_key: str, profile: str) -> None:
        self._api_key = api_key
        self._profile = profile

    def get_route(self, from_: GeometryPoint, to: GeometryPoint) -> Route:
        response = self._request(from_, to)
        feature = response.json()["features"][0]
        summary = feature["properties"]["summary"]

        distance_meters = int(summary["distance"])
        duration = timedelta(seconds=summary["duration"])
        average_speed = (distance_meters / 1000) / (duration.total_seconds() / 3600)

        return Route(
            from_,
            to,
            f"{from_.name} → {to.name}",
            distance_meters,
            duration,
            average_speed,
            json.dumps(feature["geometry"]["coordinates"]),
        )

    def _request(self, from_: GeometryPoint, to: GeometryPoint) -> requests.Response:
        url = f"{Const.ORS_BASE_URL}/{self._profile}"
        params = {
            "api_key": self._api_key,
            "start": f"{from_.longitude},{from_.latitude}",
            "end": f"{to.longitude},{to.latitude}",
            "options": json.dumps({"avoid_features": ["tollways"]}),
        }

        response = requests.get(url, params=params, timeout=_TIMEOUT_SECONDS)
        for attempt in range(1, _MAX_ATTEMPTS):
            if response.status_code != 429:
                break
            time.sleep(_RETRY_WAIT_SECONDS * attempt)
            response = requests.get(url, params=params, timeout=_TIMEOUT_SECONDS)

        response.raise_for_status()
        return response