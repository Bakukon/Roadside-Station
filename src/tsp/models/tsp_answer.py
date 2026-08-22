from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta

from tsp.models import route


class TSPAnswer:
    def __init__(self, routes: Sequence[route.Route]) -> None:
        self._routes = tuple(routes)

    @property
    def routes(self) -> tuple[route.Route, ...]:
        return self._routes

    @property
    def total_distance(self) -> int:
        return sum(r.distance_meters for r in self._routes)

    @property
    def total_time(self) -> timedelta:
        total = timedelta()
        for r in self._routes:
            total += r.duration
        return total

    def compare_to(self, other: TSPAnswer | None) -> int:
        if other is None:
            return 1
        if self.total_time < other.total_time:
            return -1
        if self.total_time > other.total_time:
            return 1
        return 0

    def __lt__(self, other: TSPAnswer) -> bool:
        return self.compare_to(other) < 0

    def __gt__(self, other: TSPAnswer) -> bool:
        return self.compare_to(other) > 0

    def __le__(self, other: TSPAnswer) -> bool:
        return self.compare_to(other) <= 0

    def __ge__(self, other: TSPAnswer) -> bool:
        return self.compare_to(other) >= 0
