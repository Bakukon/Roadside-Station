from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class JsonRoute:
    timestamp: datetime
    from_: str | None
    to: str | None
    title: str
    distance_meters: int
    duration: timedelta
    polyline: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "timestamp": self.timestamp.isoformat(),
                "from": self.from_,
                "to": self.to,
                "title": self.title,
                "distance_meters": self.distance_meters,
                "duration_seconds": self.duration.total_seconds(),
                "polyline": self.polyline,
            },
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, json_str: str) -> JsonRoute:
        obj = json.loads(json_str)
        return cls(
            timestamp=datetime.fromisoformat(obj["timestamp"]),
            from_=obj["from"],
            to=obj["to"],
            title=obj["title"],
            distance_meters=obj["distance_meters"],
            duration=timedelta(seconds=obj["duration_seconds"]),
            polyline=obj["polyline"],
        )
