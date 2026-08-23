from __future__ import annotations

import random
from collections.abc import Sequence

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.route import Route
from tsp_kanto.solvers.nearest_neighbor import SolverContext

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]
NeighborLists = dict[GeometryPoint, list[GeometryPoint]]

_MIN_POINTS_FOR_PERTURBATION = 8


def build_edge_map(context: SolverContext) -> EdgeMap:
    edges: EdgeMap = {}
    for point in context.michinoekis:
        for route in context.find_edge_from(point):
            edges[(point, route.to)] = route
    return edges


def build_neighbor_lists(points: Sequence[GeometryPoint], edges: EdgeMap) -> NeighborLists:
    return {
        point: sorted(
            (other for other in points if other != point),
            key=lambda other: edges[(point, other)].distance_meters,
        )
        for point in points
    }


def tour_distance(tour: list[GeometryPoint], edges: EdgeMap) -> int:
    return sum(edges[(tour[k], tour[k + 1])].distance_meters for k in range(len(tour) - 1))


def double_bridge(tour: list[GeometryPoint], rng: random.Random) -> list[GeometryPoint]:
    inner = tour[:-1]
    if len(inner) < _MIN_POINTS_FOR_PERTURBATION:
        return list(tour)

    p1, p2, p3 = sorted(rng.sample(range(1, len(inner)), 3))
    a, b, c, d = inner[:p1], inner[p1:p2], inner[p2:p3], inner[p3:]
    new_inner = a + c + b + d
    return [*new_inner, new_inner[0]]
