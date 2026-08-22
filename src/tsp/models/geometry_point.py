from dataclasses import dataclass

@dataclass(frozen=True)
class GeometryPoint:
    """地図上の点を表現します"""

    name: str | None
    latitude: float
    longitude: float