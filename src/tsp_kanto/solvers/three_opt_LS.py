from __future__ import annotations

from tsp_kanto.models.geometry_point import GeometryPoint
from tsp_kanto.solvers.nearest_neighbor import SolverContext
from tsp_kanto.models.route import Route
from tsp_kanto.models.tsp_answer import TSPAnswer

EdgeMap = dict[tuple[GeometryPoint, GeometryPoint], Route]


def solve(context: SolverContext, initial: TSPAnswer) -> TSPAnswer:
    edges = _build_edge_map(context)
    tour = [context.start_point, *(r.to for r in initial.routes)]

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

    routes = [edges[(tour[k], tour[k + 1])] for k in range(len(tour) - 1)]
    return context.submit_answer(routes)


def _build_edge_map(context: SolverContext) -> EdgeMap:
    edges: EdgeMap = {}
    for point in context.michinoekis:
        for route in context.find_edge_from(point):
            edges[(point, route.to)] = route
    return edges


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
