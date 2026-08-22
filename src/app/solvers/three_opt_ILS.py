from __future__ import annotations

import random

from app.models.geometry_point import GeometryPoint
from app.solvers.nearest_neighbor import SolverContext
from app.models.route import Route
from app.models.tsp_answer import TSPAnswer

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]

_DEFAULT_ITERATIONS = 100
_MIN_POINTS_FOR_PERTURBATION = 8


def solve(
    context: SolverContext,
    initial: TSPAnswer,
    iterations: int = _DEFAULT_ITERATIONS,
    seed: int | None = None,
) -> TSPAnswer:
    edges = _build_edge_map(context)
    rng = random.Random(seed)

    best_tour = _local_search([context.start_point, *(r.to for r in initial.routes)], edges)
    best_distance = _tour_distance(best_tour, edges)

    for _ in range(iterations):
        candidate = _local_search(_double_bridge(best_tour, rng), edges)
        candidate_distance = _tour_distance(candidate, edges)
        if candidate_distance < best_distance:
            best_tour, best_distance = candidate, candidate_distance

    routes = [edges[(best_tour[k], best_tour[k + 1])] for k in range(len(best_tour) - 1)]
    return context.submit_answer(routes)


def _build_edge_map(context: SolverContext) -> EdgeMap:
    edges: EdgeMap = {}
    for point in context.michinoekis:
        for route in context.find_edge_from(point):
            edges[(point, route.to)] = route
    return edges


def _local_search(tour: list[GeometryPoint], edges: EdgeMap) -> list[GeometryPoint]:
    tour = list(tour)
    improved = True
    while improved:
        improved = False
        for i in range(len(tour) - 4):
            for j in range(i + 1, len(tour) - 2):
                for k in range(j + 1, len(tour) - 1):
                    candidate = _best_reconnection(tour, edges, i, j, k)
                    if candidate is not None:
                        tour = candidate
                        improved = True
    return tour


def _best_reconnection(
    tour: list[GeometryPoint], edges: EdgeMap, i: int, j: int, k: int
) -> list[GeometryPoint] | None:
    a, b, c, d = tour[: i + 1], tour[i + 1 : j + 1], tour[j + 1 : k + 1], tour[k + 1 :]

    best_distance = _tour_distance(tour, edges)
    best_tour: list[GeometryPoint] | None = None

    for candidate in (
        a + b[::-1] + c + d,
        a + b + c[::-1] + d,
        a + b[::-1] + c[::-1] + d,
        a + c + b + d,
        a + c[::-1] + b + d,
        a + c + b[::-1] + d,
        a + c[::-1] + b[::-1] + d,
    ):
        distance = _tour_distance(candidate, edges)
        if distance < best_distance:
            best_distance = distance
            best_tour = candidate

    return best_tour


def _tour_distance(tour: list[GeometryPoint], edges: EdgeMap) -> int:
    return sum(edges[(tour[k], tour[k + 1])].distance_meters for k in range(len(tour) - 1))


def _double_bridge(tour: list[GeometryPoint], rng: random.Random) -> list[GeometryPoint]:
    inner = tour[:-1]
    if len(inner) < _MIN_POINTS_FOR_PERTURBATION:
        return list(tour)

    p1, p2, p3 = sorted(rng.sample(range(1, len(inner)), 3))
    a, b, c, d = inner[:p1], inner[p1:p2], inner[p2:p3], inner[p3:]
    new_inner = a + c + b + d
    return [*new_inner, new_inner[0]]
