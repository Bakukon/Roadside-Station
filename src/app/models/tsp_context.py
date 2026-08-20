from __future__ import annotations

from collections.abc import Sequence

from app.clients.ors_client import OrsClient
from app.clients.route_cache import RouteCache
from app.models.geometry_point import GeometryPoint
from app.models.route import Route
from app.models.tsp_answer import TSPAnswer


class TspContext:
    def __init__(
        self,
        michinoekis: Sequence[GeometryPoint],
        start_point: GeometryPoint,
        ors_client: OrsClient,
        route_cache: RouteCache,
    ) -> None:
        self.michinoekis = michinoekis
        self.start_point = start_point
        self._ors_client = ors_client
        self._route_cache = route_cache

    def find_edge_from(self, point: GeometryPoint) -> list[Route]:
        return [self._get_route(point, candidate) for candidate in self.michinoekis if candidate != point]

    def submit_answer(self, routes: list[Route]) -> TSPAnswer:
        return TSPAnswer(routes)

    def _get_route(self, from_: GeometryPoint, to: GeometryPoint) -> Route:
        cached = self._route_cache.get(from_, to)
        if cached is not None:
            return cached

        route = self._ors_client.get_route(from_, to)
        self._route_cache.put(route)
        return route
