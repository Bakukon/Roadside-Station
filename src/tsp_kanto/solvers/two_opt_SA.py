from __future__ import annotations

import math
import random

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.solvers.nearest_neighbor import SolverContext
from tsp_kanto.models.route import Route
from tsp_kanto.models.tsp_answer import TSPAnswer

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]

_DEFAULT_ITERATIONS = 10000
_COOLING_RATE = 0.9995
_MIN_TEMPERATURE = 1e-3
_TEMPERATURE_SAMPLE_SIZE = 2000
_TARGET_ACCEPTANCE_RATE = 0.01
_BISECTION_STEPS = 50


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

    temperature = _calibrate_initial_temperature(current_tour, edges, rng)

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


def _calibrate_initial_temperature(
    tour: list[GeometryPoint],
    edges: EdgeMap,
    rng: random.Random,
    sample_size: int = _TEMPERATURE_SAMPLE_SIZE,
    target_acceptance_rate: float = _TARGET_ACCEPTANCE_RATE,
) -> float:
    # deltaの分布は歪みが大きいため単純平均ではなく、受理率が目標値に一致する温度を二分探索で求める
    tour_distance = _tour_distance(tour, edges)
    deltas = [_tour_distance(_perturb(tour, rng), edges) - tour_distance for _ in range(sample_size)]
    worsening_deltas = [d for d in deltas if d > 0]

    if not worsening_deltas:
        return _MIN_TEMPERATURE

    def acceptance_rate(temperature: float) -> float:
        non_worsening_count = len(deltas) - len(worsening_deltas)
        accepted = non_worsening_count + sum(math.exp(-d / temperature) for d in worsening_deltas)
        return accepted / len(deltas)

    low, high = _MIN_TEMPERATURE, max(worsening_deltas)
    if acceptance_rate(low) >= target_acceptance_rate:
        return low
    while acceptance_rate(high) < target_acceptance_rate:
        high *= 2

    for _ in range(_BISECTION_STEPS):
        mid = (low + high) / 2
        if acceptance_rate(mid) < target_acceptance_rate:
            low = mid
        else:
            high = mid
    return high


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
