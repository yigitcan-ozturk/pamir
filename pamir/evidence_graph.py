from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from .evidence_object import EvidenceObject

@dataclass(frozen=True)
class EvidenceEdge:
    source_id: str
    target_id: str
    relation: str
    basis: str

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
            "basis": self.basis,
        }

class EvidenceGraph:
    def __init__(self, objects: Iterable[EvidenceObject] = (), edges: Iterable[EvidenceEdge] = ()):
        self.objects = {obj.object_id: obj for obj in objects}
        self.edges = list(edges)

    def add_object(self, obj: EvidenceObject) -> None:
        if obj.object_id in self.objects and self.objects[obj.object_id] != obj:
            raise ValueError(f"conflicting evidence object id: {obj.object_id}")
        self.objects[obj.object_id] = obj

    def add_edge(self, edge: EvidenceEdge) -> None:
        if edge.source_id not in self.objects or edge.target_id not in self.objects:
            raise ValueError("evidence edges must reference existing objects")
        self.edges.append(edge)

    def first_divergence(self) -> EvidenceObject | None:
        candidates = [
            obj for obj in self.objects.values()
            if obj.kind == "deviation" and obj.timestamp_us is not None
        ]
        return min(candidates, key=lambda obj: (obj.timestamp_us, obj.object_id), default=None)

    def to_dict(self) -> dict:
        return {
            "schema": "pamir-evidence-graph/v0.1",
            "objects": [self.objects[k].to_dict() for k in sorted(self.objects)],
            "edges": [
                e.to_dict()
                for e in sorted(self.edges, key=lambda x: (x.source_id, x.target_id, x.relation, x.basis))
            ],
        }
