from __future__ import annotations

import random

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.helpers import EdgeMap, build_edge_map, double_bridge, tour_distance
from tsp_kanto.solvers.nearest_neighbor import SolverContext
from tsp_kanto.models.tsp_answer import TSPAnswer

_DEFAULT_ITERATIONS = 100
_SEGMENT_LENGTHS = (1, 2, 3)


def solve(
    context: SolverContext,
    initial: TSPAnswer,
    iterations: int = _DEFAULT_ITERATIONS,
    seed: int | None = None,
) -> TSPAnswer:
    edges = build_edge_map(context)
    rng = random.Random(seed)

    best_tour = _local_search([context.start_point, *(r.to for r in initial.routes)], edges)
    best_distance = tour_distance(best_tour, edges)

    for _ in range(iterations):
        candidate = _local_search(double_bridge(best_tour, rng), edges)
        candidate_distance = tour_distance(candidate, edges)
        if candidate_distance < best_distance:
            best_tour, best_distance = candidate, candidate_distance

    routes = [edges[(best_tour[k], best_tour[k + 1])] for k in range(len(best_tour) - 1)]
    return context.submit_answer(routes)


def _local_search(tour: list[GeometryPoint], edges: EdgeMap) -> list[GeometryPoint]:
    tour = list(tour)
    improved = True
    while improved:
        improved = False
        for length in _SEGMENT_LENGTHS:
            for i in range(1, len(tour) - length):
                candidate = _best_or_opt_move(tour, edges, i, length)
                if candidate is not None:
                    tour = candidate
                    improved = True
    return tour


def _best_or_opt_move(
    tour: list[GeometryPoint], edges: EdgeMap, i: int, length: int
) -> list[GeometryPoint] | None:
    # 開始/終了ノード(道の駅の出発点)を保持したまま、長さlengthの区間を他の位置へ移動する。
    # 移動後のコストは、区間の付け根2辺と挿入先の1辺だけで決まる（区間内部の辺は不変）ため、
    # O(N)の巡回路全体再計算は不要。ただし距離が対称(d(A,B)=d(B,A))であることが前提。
    # 挿入先が区間を取り除いた直後の隙間(remainder[i-1]の位置)の場合だけ、
    # 迂回辺がまだ存在しないため式が変わる。
    segment = tour[i : i + length]
    remainder = tour[:i] + tour[i + length :]
    s_first, s_last = segment[0], segment[-1]
    prev, after = tour[i - 1], tour[i + length]

    def dist(x: GeometryPoint, y: GeometryPoint) -> int:
        return edges[(x, y)].distance_meters

    boundary_removed = dist(prev, s_first) + dist(s_last, after)
    bypass = dist(prev, after)

    best_gain = 0
    best_j: int | None = None
    best_reversed = False

    for j in range(len(remainder) - 1):
        x, y = remainder[j], remainder[j + 1]
        if j == i - 1:
            removed = boundary_removed
            forward_added = boundary_removed
            reversed_added = dist(prev, s_last) + dist(s_first, after)
        else:
            removed = boundary_removed + dist(x, y)
            forward_added = bypass + dist(x, s_first) + dist(s_last, y)
            reversed_added = bypass + dist(x, s_last) + dist(s_first, y)

        if removed - forward_added > best_gain:
            best_gain = removed - forward_added
            best_j, best_reversed = j, False
        if removed - reversed_added > best_gain:
            best_gain = removed - reversed_added
            best_j, best_reversed = j, True

    if best_j is None:
        return None

    seg = segment[::-1] if best_reversed else segment
    return remainder[: best_j + 1] + seg + remainder[best_j + 1 :]
