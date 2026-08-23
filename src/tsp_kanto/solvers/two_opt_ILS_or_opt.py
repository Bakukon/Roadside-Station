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
    # 2-optとOr-optは改善できる局所最適の形が異なるため、
    # 一方が変化を生まなくなるまで交互に適用してから終了する。
    tour = list(tour)
    changed = True
    while changed:
        changed = False
        two_opt_tour = _two_opt_local_search(tour, edges, neighbor_lists)
        if two_opt_tour != tour:
            tour = two_opt_tour
            changed = True
        or_opt_tour = _or_opt_local_search(tour, edges)
        if or_opt_tour != tour:
            tour = or_opt_tour
            changed = True
    return tour


def _two_opt_local_search(
    tour: list[GeometryPoint], edges: EdgeMap, neighbor_lists: NeighborLists
) -> list[GeometryPoint]:
    tour = list(tour)
    position = {point: index for index, point in enumerate(tour)}
    improved = True
    while improved:
        improved = False
        for i in range(len(tour) - 1):
            if _improve_edge(tour, position, edges, neighbor_lists, i):
                improved = True
    return tour


def _improve_edge(
    tour: list[GeometryPoint],
    position: dict[GeometryPoint, int],
    edges: EdgeMap,
    neighbor_lists: NeighborLists,
    i: int,
) -> bool:
    # d(t1,t2)+d(t3,t4) > d(t1,t3)+d(t2,t4) が成り立つには、
    # d(t1,t3) < d(t1,t2) か d(t2,t4) < d(t1,t2) の少なくとも一方が必要。
    # 近傍リストは距離昇順なので、しきい値を超えた時点で探索を打ち切れる。
    t1, t2 = tour[i], tour[i + 1]
    d12 = edges[(t1, t2)].distance_meters

    for t3 in neighbor_lists[t1]:
        if edges[(t1, t3)].distance_meters >= d12:
            break
        if _apply_if_improving(tour, position, edges, i, position[t3]):
            return True

    for t4 in neighbor_lists[t2]:
        if edges[(t2, t4)].distance_meters >= d12:
            break
        if _apply_if_improving(tour, position, edges, i, position[t4] - 1):
            return True

    return False


def _apply_if_improving(
    tour: list[GeometryPoint],
    position: dict[GeometryPoint, int],
    edges: EdgeMap,
    i: int,
    j: int,
) -> bool:
    if j < 0 or j > len(tour) - 2 or j == i:
        return False
    lo, hi = (i, j) if i < j else (j, i)
    if hi == lo + 1:
        return False

    a, b, c, d = tour[lo], tour[lo + 1], tour[hi], tour[hi + 1]
    before = edges[(a, b)].distance_meters + edges[(c, d)].distance_meters
    after = edges[(a, c)].distance_meters + edges[(b, d)].distance_meters
    if after >= before:
        return False

    tour[lo + 1 : hi + 1] = reversed(tour[lo + 1 : hi + 1])
    for idx in range(lo + 1, hi + 1):
        position[tour[idx]] = idx
    return True
