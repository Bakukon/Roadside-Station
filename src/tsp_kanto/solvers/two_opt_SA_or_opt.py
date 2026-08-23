from __future__ import annotations

import math
import random

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.helpers import EdgeMap, build_edge_map, tour_distance
from tsp_kanto.solvers.nearest_neighbor import SolverContext
from tsp_kanto.models.tsp_answer import TSPAnswer
from tsp_kanto.solvers.or_ops import _local_search as _or_opt_local_search

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
    edges = build_edge_map(context)
    rng = random.Random(seed)

    current_tour = [context.start_point, *(r.to for r in initial.routes)]
    current_distance = tour_distance(current_tour, edges)

    best_tour = list(current_tour)
    best_distance = current_distance

    temperature = _calibrate_initial_temperature(current_tour, edges, rng)

    for _ in range(iterations):
        if temperature < _MIN_TEMPERATURE:
            break

        candidate, delta = _perturb(current_tour, edges, rng)
        candidate_distance = current_distance + delta

        if delta < 0 or rng.random() < math.exp(-delta / temperature):
            current_tour, current_distance = candidate, candidate_distance
            if current_distance < best_distance:
                # ベスト更新時のみOr-optで磨く。改善手しか適用しないため距離が
                # 悪化することはなく、current_tour(SAの探索軌道)には反映しない。
                best_tour = _or_opt_local_search(current_tour, edges)
                best_distance = tour_distance(best_tour, edges)

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
    deltas = [_perturb(tour, edges, rng)[1] for _ in range(sample_size)]
    worsening_deltas = [d for d in deltas if d > 0]

    if not worsening_deltas:
        return _MIN_TEMPERATURE

    def acceptance_rate(temperature: float) -> float:
        # 悪化しない手は温度に関係なく必ず採用されるため、分母・分子から除外する。
        # 混ぜると、悪化しない手の割合だけで目標値に達してしまい、
        # 温度によらず最低温度が返る(=悪化する手をほぼ受理しない)ことがある。
        return sum(math.exp(-d / temperature) for d in worsening_deltas) / len(worsening_deltas)

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


def _perturb(
    tour: list[GeometryPoint], edges: EdgeMap, rng: random.Random
) -> tuple[list[GeometryPoint], int]:
    inner = tour[:-1]
    if len(inner) < 4:
        return list(tour), 0

    i, j = sorted(rng.sample(range(1, len(inner)), 2))
    delta = _reversal_delta(tour, edges, i, j)
    inner[i : j + 1] = reversed(inner[i : j + 1])
    return [*inner, inner[0]], delta


def _reversal_delta(tour: list[GeometryPoint], edges: EdgeMap, i: int, j: int) -> int:
    # tour[i:j+1]を反転すると、変化するのは区間の両端の2辺だけ
    # (区間内部の辺は不変)。ただしこれは距離が対称であることが前提。
    a, b, c, d = tour[i - 1], tour[i], tour[j], tour[j + 1]
    before = edges[(a, b)].distance_meters + edges[(c, d)].distance_meters
    after = edges[(a, c)].distance_meters + edges[(b, d)].distance_meters
    return after - before
