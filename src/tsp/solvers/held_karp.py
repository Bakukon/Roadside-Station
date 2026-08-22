from __future__ import annotations

from tsp.models.geometry_point import GeometryPoint
from tsp.solvers.nearest_neighbor import SolverContext
from tsp.models.route import Route
from tsp.models.tsp_answer import TSPAnswer

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]

_UNVISITED = float("inf")


def solve(context: SolverContext) -> TSPAnswer:
    """Held-Karp法による厳密解。O(2^n * n^2)のため地点数が増えると(目安20-25点超で)非現実的になる"""
    edges = _build_edge_map(context)
    others = [p for p in context.michinoekis if p != context.start_point]
    n = len(others)

    if n == 0:
        return context.submit_answer([])

    dist = [[edges[(a, b)].distance_meters if a != b else 0 for b in others] for a in others]
    start_dist = [edges[(context.start_point, p)].distance_meters for p in others]
    return_dist = [edges[(p, context.start_point)].distance_meters for p in others]

    size = 1 << n
    cost = [[_UNVISITED] * n for _ in range(size)]
    parent = [[-1] * n for _ in range(size)]

    for j in range(n):
        cost[1 << j][j] = start_dist[j]

    for mask in range(1, size):
        for j in range(n):
            if not mask & (1 << j) or cost[mask][j] == _UNVISITED:
                continue
            current = cost[mask][j]
            for k in range(n):
                if mask & (1 << k):
                    continue
                next_mask = mask | (1 << k)
                candidate = current + dist[j][k]
                if candidate < cost[next_mask][k]:
                    cost[next_mask][k] = candidate
                    parent[next_mask][k] = j

    full = size - 1
    last = min(range(n), key=lambda j: cost[full][j] + return_dist[j])

    order = _reconstruct(parent, full, last)
    tour = [context.start_point, *(others[i] for i in order), context.start_point]
    routes = [edges[(tour[k], tour[k + 1])] for k in range(len(tour) - 1)]
    return context.submit_answer(routes)


def _build_edge_map(context: SolverContext) -> EdgeMap:
    edges: EdgeMap = {}
    for point in context.michinoekis:
        for route in context.find_edge_from(point):
            edges[(point, route.to)] = route
    return edges


def _reconstruct(parent: list[list[int]], mask: int, last: int) -> list[int]:
    order = [last]
    while True:
        prev = parent[mask][last]
        if prev == -1:
            break
        mask ^= 1 << last
        last = prev
        order.append(last)
    order.reverse()
    return order
