from __future__ import annotations

import random

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.models.helpers import (
    EdgeMap,
    NeighborLists,
    build_edge_map,
    build_neighbor_lists,
    double_bridge,
    tour_distance,
)
from tsp_kanto.solvers.nearest_neighbor import SolverContext
from tsp_kanto.models.tsp_answer import TSPAnswer
from tsp_kanto.solvers.or_ops import _local_search as _or_opt_local_search

_DEFAULT_ITERATIONS = 500


def solve(
    context: SolverContext,
    initial: TSPAnswer,
    iterations: int = _DEFAULT_ITERATIONS,
    seed: int | None = None,
) -> TSPAnswer:
    edges = build_edge_map(context)
    neighbor_lists = build_neighbor_lists(context.michinoekis, edges)
    rng = random.Random(seed)

    best_tour = _local_search(
        [context.start_point, *(r.to for r in initial.routes)], edges, neighbor_lists
    )
    best_distance = tour_distance(best_tour, edges)

    for _ in range(iterations):
        candidate = _local_search(double_bridge(best_tour, rng), edges, neighbor_lists)
        candidate_distance = tour_distance(candidate, edges)
        if candidate_distance < best_distance:
            best_tour, best_distance = candidate, candidate_distance

    routes = [edges[(best_tour[k], best_tour[k + 1])] for k in range(len(best_tour) - 1)]
    return context.submit_answer(routes)


def _local_search(
    tour: list[GeometryPoint], edges: EdgeMap, neighbor_lists: NeighborLists
) -> list[GeometryPoint]:
    # 3-optとOr-optは改善できる局所最適の形が異なるため、
    # 一方が変化を生まなくなるまで交互に適用してから終了する。
    tour = list(tour)
    changed = True
    while changed:
        changed = False
        three_opt_tour = _three_opt_local_search(tour, edges, neighbor_lists)
        if three_opt_tour != tour:
            tour = three_opt_tour
            changed = True
        or_opt_tour = _or_opt_local_search(tour, edges)
        if or_opt_tour != tour:
            tour = or_opt_tour
            changed = True
    return tour


def _three_opt_local_search(
    tour: list[GeometryPoint], edges: EdgeMap, neighbor_lists: NeighborLists
) -> list[GeometryPoint]:
    tour = list(tour)
    position = {point: index for index, point in enumerate(tour)}
    improved = True
    while improved:
        improved = False
        for i in range(len(tour) - 4):
            candidate = _find_improving_reconnection(tour, position, edges, neighbor_lists, i)
            if candidate is not None:
                tour = candidate
                position = {point: index for index, point in enumerate(tour)}
                improved = True
    return tour


def _find_improving_reconnection(
    tour: list[GeometryPoint],
    position: dict[GeometryPoint, int],
    edges: EdgeMap,
    neighbor_lists: NeighborLists,
    i: int,
) -> list[GeometryPoint] | None:
    # 2-optの近傍リスト枝刈りと同じ理屈をj, kそれぞれの選定に適用する。
    # 改善が成り立つには少なくとも1本の新しい辺が対応する除去辺より短い必要があるため、
    # 距離昇順の近傍リストをしきい値で打ち切りながら候補だけに絞り込める。
    n = len(tour)
    p1, p2 = tour[i], tour[i + 1]
    d12 = edges[(p1, p2)].distance_meters

    j_candidates = _candidate_positions(position, edges, neighbor_lists, p1, p2, d12, i + 1, n - 3)
    for j in j_candidates:
        p3, p4 = tour[j], tour[j + 1]
        d34 = edges[(p3, p4)].distance_meters
        k_candidates = _candidate_positions(
            position, edges, neighbor_lists, p3, p4, d34, j + 1, n - 2
        )
        for k in k_candidates:
            candidate = _best_reconnection(tour, edges, i, j, k)
            if candidate is not None:
                return candidate
    return None


def _candidate_positions(
    position: dict[GeometryPoint, int],
    edges: EdgeMap,
    neighbor_lists: NeighborLists,
    a: GeometryPoint,
    b: GeometryPoint,
    removed_distance: int,
    lo: int,
    hi: int,
) -> list[int]:
    # aの近傍は「その点が次の辺の始点(p3)になる」ケース、
    # bの近傍は「その点が次の辺の終点(p4)になる」ケースに対応する。
    candidates: set[int] = set()
    for near in neighbor_lists[a]:
        if edges[(a, near)].distance_meters >= removed_distance:
            break
        idx = position[near]
        if lo <= idx <= hi:
            candidates.add(idx)
    for near in neighbor_lists[b]:
        if edges[(b, near)].distance_meters >= removed_distance:
            break
        idx = position[near] - 1
        if lo <= idx <= hi:
            candidates.add(idx)
    return sorted(candidates)


def _best_reconnection(
    tour: list[GeometryPoint], edges: EdgeMap, i: int, j: int, k: int
) -> list[GeometryPoint] | None:
    # 3本の辺 (p1,p2) (p3,p4) (p5,p6) を切り離す際、7通りの繋ぎ変えはいずれも
    # この6点間の辺だけで新しいコストが決まる（セグメント内部の辺は変わらない）。
    # そのためO(N)の巡回路全体再計算は不要で、6点間の距離だけを比較すればよい。
    # ただしこれは距離が対称(d(A,B)=d(B,A))であることが前提。
    p1, p2, p3, p4, p5, p6 = tour[i], tour[i + 1], tour[j], tour[j + 1], tour[k], tour[k + 1]

    def dist(x: GeometryPoint, y: GeometryPoint) -> int:
        return edges[(x, y)].distance_meters

    removed = dist(p1, p2) + dist(p3, p4) + dist(p5, p6)
    added = (
        dist(p1, p3) + dist(p2, p4) + dist(p5, p6),
        dist(p1, p2) + dist(p3, p5) + dist(p4, p6),
        dist(p1, p3) + dist(p2, p5) + dist(p4, p6),
        dist(p1, p4) + dist(p5, p2) + dist(p3, p6),
        dist(p1, p5) + dist(p4, p2) + dist(p3, p6),
        dist(p1, p4) + dist(p5, p3) + dist(p2, p6),
        dist(p1, p5) + dist(p4, p3) + dist(p2, p6),
    )

    best_index = min(range(len(added)), key=lambda idx: added[idx])
    if added[best_index] >= removed:
        return None

    a, b, c, d = tour[: i + 1], tour[i + 1 : j + 1], tour[j + 1 : k + 1], tour[k + 1 :]
    reconnections = (
        a + b[::-1] + c + d,
        a + b + c[::-1] + d,
        a + b[::-1] + c[::-1] + d,
        a + c + b + d,
        a + c[::-1] + b + d,
        a + c + b[::-1] + d,
        a + c[::-1] + b[::-1] + d,
    )
    return reconnections[best_index]
