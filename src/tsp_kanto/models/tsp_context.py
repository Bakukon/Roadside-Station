from __future__ import annotations

from collections.abc import Sequence

from tsp_kanto.clients.distance_client import DistanceClient
from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.route import Route
from tsp_kanto.models.tsp_answer import TSPAnswer


class TspContext:
    def __init__(
        self,
        michinoekis: Sequence[GeometryPoint],
        start_point: GeometryPoint,
        distance_client: DistanceClient,
    ) -> None:
        self.michinoekis = michinoekis
        self.start_point = start_point
        self._distance_client = distance_client

    def find_edge_from(self, point: GeometryPoint) -> list[Route]:
        return [
            self._distance_client.get_route(point, candidate)
            for candidate in self.michinoekis
            if candidate != point
        ]

    def submit_answer(self, routes: list[Route]) -> TSPAnswer:
        return TSPAnswer(routes)
