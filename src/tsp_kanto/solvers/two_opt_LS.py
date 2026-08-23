from __future__ import annotations

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.helpers import EdgeMap, build_edge_map, tour_distance
from tsp_kanto.solvers.nearest_neighbor import SolverContext
from tsp_kanto.models.tsp_answer import TSPAnswer


def solve(context: SolverContext, initial: TSPAnswer) -> TSPAnswer:
    edges = build_edge_map(context)
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


def _try_reverse(tour: list[GeometryPoint], edges: EdgeMap, i: int, j: int) -> bool:
    before = tour_distance(tour, edges)
    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
    after = tour_distance(tour, edges)
    if after < before:
        return True
    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
    return False
