from __future__ import annotations

from app.models.geometry_point import GeometryPoint
from app.models.nearest_neighbor import SolverContext
from app.models.route import Route
from app.models.tsp_answer import TSPAnswer

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]


def solve(context: SolverContext, initial: TSPAnswer) -> TSPAnswer:
    edges = _build_edge_map(context)
    tour = [context.start_point, *(r.to for r in initial.routes)]

    improved = True
    while improved:
        improved = False
        for i in range(len(tour) - 2):
            for j in range(i + 2, len(tour) - 1):
                if _try_reverse(tour, edges, i, j):
                    improved = True

    routes = [edges[(tour[k], tour[k + 1])] for k in range(len(tour) - 1)]
    return context.submit_answer(routes)


def _build_edge_map(context: SolverContext) -> EdgeMap:
    edges: EdgeMap = {}
    for point in context.michinoekis:
        for route in context.find_edge_from(point):
            edges[(point, route.to)] = route
    return edges


def _try_reverse(tour: list[GeometryPoint], edges: EdgeMap, i: int, j: int) -> bool:
    before = _tour_distance(tour, edges)
    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
    after = _tour_distance(tour, edges)
    if after < before:
        return True
    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
    return False


def _tour_distance(tour: list[GeometryPoint], edges: EdgeMap) -> int:
    return sum(edges[(tour[k], tour[k + 1])].distance_meters for k in range(len(tour) - 1))
