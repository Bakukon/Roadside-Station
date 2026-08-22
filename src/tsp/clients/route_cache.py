from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from tsp.json_route import JsonRoute
from tsp.models.geometry_point import GeometryPoint
from tsp.models.route import Route

class RouteCache:
    def __init__(self, cache_path: Path,  all_points: Sequence[GeometryPoint]) -> None:
        self._cache_path = cache_path
        self._all_points = all_points
        self._entries: dict[str, str] = self._load()

    def get(self, from_: GeometryPoint, to: GeometryPoint) -> Route | None:
        cached = self._entries.get(self._cache_key(from_, to))
        if cached is None:
            return None
        return Route.from_json_object(JsonRoute.from_json(cached), self._all_points)
    
    def put(self, route: Route) -> None:
        self._entries[self._cache_key(route.from_, route.to)] = route.to_json()
        self._save()

    def _load(self) -> dict[str, str]:
        if not self._cache_path.exists():
            return {}
        return json.loads(self._cache_path.read_text(encoding="utf-8"))
    
    def _save(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache_path.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def _cache_key(self, from_: GeometryPoint, to: GeometryPoint) -> str:
        return f"{from_.name}|{to.name}"
