from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Any, Literal

EvidenceKind = Literal["observation", "deviation", "claim", "unknown", "counterfactual"]

@dataclass(frozen=True)
class EvidenceObject:
    object_id: str
    kind: EvidenceKind
    timestamp_us: int | None
    subject: str
    payload: dict[str, Any]
    source: str
    provenance: dict[str, Any] = field(default_factory=dict)
    supports: tuple[str, ...] = ()
    contradicts: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()

    def canonical_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @property
    def digest(self) -> str:
        return sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        data = self.canonical_dict()
        data["sha256"] = self.digest
        return data


def evidence_id(kind: str, subject: str, timestamp_us: int | None, payload: dict[str, Any]) -> str:
    raw = json.dumps(
        {"kind": kind, "subject": subject, "timestamp_us": timestamp_us, "payload": payload},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return f"peo-{sha256(raw.encode('utf-8')).hexdigest()[:16]}"
