from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class Sample:
    timestamp_us: int
    signal: str
    value: float

@dataclass(frozen=True)
class Deviation:
    timestamp_us: int
    signal: str
    value: float
    baseline: float
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
