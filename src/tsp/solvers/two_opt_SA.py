from __future__ import annotations

import math
import random

from tsp.models.geometry_point import GeometryPoint
from tsp.solvers.nearest_neighbor import SolverContext
from tsp.models.route import Route
from tsp.models.tsp_answer import TSPAnswer

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]

_DEFAULT_ITERATIONS = 10000
_COOLING_RATE = 0.9995
_MIN_TEMPERATURE = 1e-3


def solve(
    context: SolverContext,
    initial: TSPAnswer,
    iterations: int = _DEFAULT_ITERATIONS,
    cooling_rate: float = _COOLING_RATE,
    seed: int | None = None,
) -> TSPAnswer:
    edges = _build_edge_map(context)
    rng = random.Random(seed)

    current_tour = [context.start_point, *(r.to for r in initial.routes)]
    current_distance = _tour_distance(current_tour, edges)

    best_tour = list(current_tour)
    best_distance = current_distance

    temperature = current_distance / max(len(current_tour) - 1, 1)

    for _ in range(iterations):
        if temperature < _MIN_TEMPERATURE:
            break

        candidate = _perturb(current_tour, rng)
        candidate_distance = _tour_distance(candidate, edges)
        delta = candidate_distance - current_distance

        if delta < 0 or rng.random() < math.exp(-delta / temperature):
            current_tour, current_distance = candidate, candidate_distance
            if current_distance < best_distance:
                best_tour, best_distance = list(current_tour), current_distance

        temperature *= cooling_rate

    routes = [edges[(best_tour[k], best_tour[k + 1])] for k in range(len(best_tour) - 1)]
    return context.submit_answer(routes)


def _build_edge_map(context: SolverContext) -> EdgeMap:
    edges: EdgeMap = {}
    for point in context.michinoekis:
        for route in context.find_edge_from(point):
            edges[(point, route.to)] = route
    return edges


def _tour_distance(tour: list[GeometryPoint], edges: EdgeMap) -> int:
    return sum(edges[(tour[k], tour[k + 1])].distance_meters for k in range(len(tour) - 1))


def _perturb(tour: list[GeometryPoint], rng: random.Random) -> list[GeometryPoint]:
    inner = tour[:-1]
    if len(inner) < 4:
        return list(tour)

    i, j = sorted(rng.sample(range(1, len(inner)), 2))
    inner[i : j + 1] = reversed(inner[i : j + 1])
    return [*inner, inner[0]]
