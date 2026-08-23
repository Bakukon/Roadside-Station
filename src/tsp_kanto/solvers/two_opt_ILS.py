from __future__ import annotations

import random
from collections.abc import Sequence

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.solvers.nearest_neighbor import SolverContext
from tsp_kanto.models.route import Route
from tsp_kanto.models.tsp_answer import TSPAnswer

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]
NeighborLists = dict[GeometryPoint, list[GeometryPoint]]

_DEFAULT_ITERATIONS = 100
_MIN_POINTS_FOR_PERTURBATION = 8


def solve(
    context: SolverContext,
    initial: TSPAnswer,
    iterations: int = _DEFAULT_ITERATIONS,
    seed: int | None = None,
) -> TSPAnswer:
    edges = _build_edge_map(context)
    neighbor_lists = _build_neighbor_lists(context.michinoekis, edges)
    rng = random.Random(seed)

    best_tour = _local_search(
        [context.start_point, *(r.to for r in initial.routes)], edges, neighbor_lists
    )
    best_distance = _tour_distance(best_tour, edges)

    for _ in range(iterations):
        candidate = _local_search(_double_bridge(best_tour, rng), edges, neighbor_lists)
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


def _build_neighbor_lists(points: Sequence[GeometryPoint], edges: EdgeMap) -> NeighborLists:
    return {
        point: sorted(
            (other for other in points if other != point),
            key=lambda other: edges[(point, other)].distance_meters,
        )
        for point in points
    }


def _local_search(
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
