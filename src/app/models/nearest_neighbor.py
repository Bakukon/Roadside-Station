from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from app.models.geometry_point import GeometryPoint
from app.models.route import Route
from app.models.tsp_answer import TSPAnswer

class SolverContext(Protocol):
    michinoekis: Sequence[GeometryPoint]
    start_point: GeometryPoint

    def find_edge_from(self, point: GeometryPoint) -> list[Route]: ...
    def submit_answer(self, routes: list[Route]) -> TSPAnswer: ...

def solve(context: SolverContext) -> TSPAnswer:
    unvisited: set[GeometryPoint] = set(context.michinoekis)
    unvisited.discard(context.start_point)
    
    ans: list[Route] = []
    current = context.start_point

    while unvisited:
        selected = _nearest_unvisited(context.find_edge_from(current), unvisited)
        if selected is None:
            msg = f"no reachable unvisited station found from {current}"
            raise ValueError(msg)
        ans.append(selected)
        unvisited.discard(selected.to)
        current = selected.to

    if ans:
        return_route = next(r for r in context.find_edge_from(current) if r.to == context.start_point)
        ans.append(return_route)

    return context.submit_answer(ans)

def _nearest_unvisited(routes: list[Route], unvisited: set[GeometryPoint]) -> Route | None:
    min_route: Route | None = None
    for r in routes:
        if r.to not in unvisited:
            continue
        if min_route is None or min_route.duration > r.duration:
            min_route = r
    return min_route