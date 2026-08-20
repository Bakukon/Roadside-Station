from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime, timedelta

from app.json_route import JsonRoute
from app.models.geometry_point import GeometryPoint


class Route:
    def __init__(
        self,
        from_: GeometryPoint,
        to: GeometryPoint,
        title: str,
        distance_meters: int,
        duration: timedelta,
        average_speed: float,
        polyline: str,
    ) -> None:
        self.from_ = from_
        self.to = to
        self.title = title
        self.distance_meters = distance_meters
        self.duration = duration
        self.average_speed = average_speed
        self.polyline = polyline
        self._hash: int | None = None

    @property
    def polyline_decoded(self) -> list[GeometryPoint]:
        coordinates = json.loads(self.polyline)
        return [GeometryPoint(None, latitude, longitude) for longitude, latitude in coordinates]

    def to_json(self) -> str:
        json_obj = JsonRoute(
            timestamp=datetime.now(),
            from_=self.from_.name,
            to=self.to.name,
            title=self.title,
            distance_meters=self.distance_meters,
            duration=self.duration,
            polyline=self.polyline,
        )
        return json_obj.to_json()

    @classmethod
    def from_json_object(cls, json_obj: JsonRoute, michinoekis: Sequence[GeometryPoint]) -> Route:
        average = json_obj.distance_meters / (json_obj.duration.total_seconds() / 3600) * 1000

        from_point: GeometryPoint | None = None
        to_point: GeometryPoint | None = None
        for m in michinoekis:
            if m.name == json_obj.from_:
                from_point = m
            if m.name == json_obj.to:
                to_point = m

        if from_point is None:
            raise ValueError(f"point in json '{json_obj.from_}' was not found")
        if to_point is None:
            raise ValueError(f"point in json '{json_obj.to}' was not found")

        return cls(
            from_point,
            to_point,
            json_obj.title,
            json_obj.distance_meters,
            json_obj.duration,
            average,
            json_obj.polyline,
        )

    @classmethod
    def from_json(cls, json_str: str, michinoekis: Sequence[GeometryPoint]) -> Route:
        return cls.from_json_object(JsonRoute.from_json(json_str), michinoekis)

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash((self.from_.latitude, self.from_.longitude, self.to.latitude, self.to.longitude))
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Route):
            return NotImplemented
        return self.from_ == other.from_ and self.to == other.to
