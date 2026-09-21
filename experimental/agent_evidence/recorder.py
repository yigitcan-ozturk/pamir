"""Experimental PAMIR Agent Evidence recorder.

This module is isolated from the frozen PAMIR v0.1 package.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidenceObject:
    evidence_id: str
    run_id: str
    event_type: str
    event_time: str
    observed_time: str
    source: str
    source_version: str
    subject_identity: str
    input_hash: str
    output_hash: str
    parent_evidence_ids: tuple[str, ...] = ()
    content_reference: str = ""
    integrity_status: str = "VERIFIED"
    capture_policy: str = "full-hash"

    def digest(self) -> str:
        return sha256_value(asdict(self))


@dataclass(frozen=True)
class DecisionSnapshot:
    decision_id: str
    run_id: str
    decision_time: str
    available_evidence_ids: tuple[str, ...]
    unavailable_expected_evidence_ids: tuple[str, ...] = ()
    conflicting_evidence_ids: tuple[str, ...] = ()
    model_identity: str = ""
    model_version: str = ""
    context_hash: str = ""
    policy_identity: str = ""
    policy_version: str = ""


@dataclass(frozen=True)
class ReconstructionReport:
    run_id: str
    decision_id: str
    status: str
    verified_evidence_ids: tuple[str, ...]
    missing_evidence_ids: tuple[str, ...]
    conflicting_evidence_ids: tuple[str, ...]
    observed_facts: tuple[str, ...] = ()
    causal_hypotheses: tuple[str, ...] = ()
    unsupported_claims: tuple[str, ...] = ()


@dataclass
class EvidenceRecorder:
    run_id: str
    objects: dict[str, EvidenceObject] = field(default_factory=dict)
    payloads: dict[str, dict[str, Any]] = field(default_factory=dict)

    def capture(
        self,
        *,
        evidence_id: str,
        event_type: str,
        source: str,
        source_version: str,
        subject_identity: str,
        input_value: Any,
        output_value: Any,
        event_time: str,
        observed_time: str | None = None,
        parent_evidence_ids: tuple[str, ...] = (),
    ) -> EvidenceObject:
        observed_time = observed_time or datetime.now(timezone.utc).isoformat()
        payload = {"input": input_value, "output": output_value}
        obj = EvidenceObject(
            evidence_id=evidence_id,
            run_id=self.run_id,
            event_type=event_type,
            event_time=event_time,
            observed_time=observed_time,
            source=source,
            source_version=source_version,
            subject_identity=subject_identity,
            input_hash=sha256_value(input_value),
            output_hash=sha256_value(output_value),
            parent_evidence_ids=parent_evidence_ids,
            content_reference=f"memory://{self.run_id}/{evidence_id}",
        )
        self.objects[evidence_id] = obj
        self.payloads[evidence_id] = payload
        return obj

    def verify(self, evidence_id: str) -> bool:
        obj = self.objects[evidence_id]
        payload = self.payloads[evidence_id]
        return (
            sha256_value(payload["input"]) == obj.input_hash
            and sha256_value(payload["output"]) == obj.output_hash
        )

    def snapshot(
        self,
        *,
        decision_id: str,
        decision_time: str,
        available_evidence_ids: tuple[str, ...],
        expected_evidence_ids: tuple[str, ...],
        conflicting_evidence_ids: tuple[str, ...] = (),
        model_identity: str = "",
        model_version: str = "",
        context_value: Any = None,
    ) -> DecisionSnapshot:
        available = set(available_evidence_ids)
        missing = tuple(e for e in expected_evidence_ids if e not in available)
        return DecisionSnapshot(
            decision_id=decision_id,
            run_id=self.run_id,
            decision_time=decision_time,
            available_evidence_ids=available_evidence_ids,
            unavailable_expected_evidence_ids=missing,
            conflicting_evidence_ids=conflicting_evidence_ids,
            model_identity=model_identity,
            model_version=model_version,
            context_hash=sha256_value(context_value),
        )

    def reconstruct(self, snapshot: DecisionSnapshot) -> ReconstructionReport:
        verified = tuple(
            e for e in snapshot.available_evidence_ids
            if e in self.objects and self.verify(e)
        )
        integrity_failures = tuple(
            e for e in snapshot.available_evidence_ids
            if e in self.objects and not self.verify(e)
        )
        missing = snapshot.unavailable_expected_evidence_ids + tuple(
            e for e in snapshot.available_evidence_ids if e not in self.objects
        )
        conflicts = snapshot.conflicting_evidence_ids

        if conflicts:
            status = "CONFLICTED"
        elif integrity_failures:
            status = "INSUFFICIENT"
        elif missing:
            status = "PARTIAL"
        elif len(verified) == len(snapshot.available_evidence_ids):
            status = "VERIFIED"
        else:
            status = "INSUFFICIENT"

        unsupported = ()
        if missing or integrity_failures:
            unsupported = ("causal conclusion requiring unavailable or unverified evidence",)

        return ReconstructionReport(
            run_id=self.run_id,
            decision_id=snapshot.decision_id,
            status=status,
            verified_evidence_ids=verified,
            missing_evidence_ids=missing + integrity_failures,
            conflicting_evidence_ids=conflicts,
            observed_facts=(
                f"{len(verified)} captured evidence object(s) passed integrity verification",
            ),
            unsupported_claims=unsupported,
        )
