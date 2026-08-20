from __future__ import annotations

from app.models.geometry_point import GeometryPoint

_PRECISION = 1e5

class PolylineEncoder:
    @staticmethod
    def decode(polyline: str) -> list[GeometryPoint]:
        points: list[GeometryPoint] = []
        index = 0
        latitude = 0
        longitude = 0

        while index < len(polyline):
            delta_lat, index = _decode_signed_value(polyline, index)
            delta_lng, index = _decode_signed_value(polyline, index)
            latitude += delta_lat
            longitude += delta_lng
            points.append(GeometryPoint(None, latitude / _PRECISION, longitude / _PRECISION))

        return points
    
def _decode_signed_value(polyline: str, start: int) -> tuple[int, int]:
    result = 0
    shift = 0
    index = start
    while True:
        byte = ord(polyline[index]) - 63
        index += 1
        result |= (byte & 0x1F) << shift
        if byte < 0x20:
            break
        shift += 5

    if result & 1:
        value = ~(result >> 1)
    else:
        value = result >> 1

    return value, index