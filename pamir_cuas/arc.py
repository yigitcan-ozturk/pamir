"""Deterministic, non-engagement resilience controller for PAMIR-CUAS.

The controller is deliberately bounded to mission-assurance actions: alerting,
isolation, degraded operation, candidate validation, promotion, and rollback.
It does not implement targeting, engagement, guidance, or effector control.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResilienceState(str, Enum):
    NOMINAL = "NOMINAL"
    DEGRADED = "DEGRADED"
    ISOLATED = "ISOLATED"
    VALIDATING = "VALIDATING"
    RECOVERED = "RECOVERED"
    ROLLBACK = "ROLLBACK"


@dataclass
class ResilienceController:
    state: ResilienceState = ResilienceState.NOMINAL
    audit: list[dict[str, Any]] = field(default_factory=list)
    isolated_sources: set[str] = field(default_factory=set)

    def _record(self, event: str, **details: Any) -> dict[str, Any]:
        row = {
            "sequence": len(self.audit) + 1,
            "event": event,
            "state": self.state.value,
            **details,
        }
        self.audit.append(row)
        return row

    def detect_degradation(self, source_id: str, reason: str) -> list[str]:
        """Alert and isolate a degraded evidence source, then request validation."""
        if not source_id:
            raise ValueError("source_id is required")
        if not reason:
            raise ValueError("reason is required")

        actions = ["ALERT", "ISOLATE_SOURCE", "ENTER_DEGRADED_MODE", "VALIDATE_CANDIDATE"]
        self.state = ResilienceState.DEGRADED
        self._record("ALERT", source_id=source_id, reason=reason)
        self.isolated_sources.add(source_id)
        self.state = ResilienceState.ISOLATED
        self._record("ISOLATE_SOURCE", source_id=source_id)
        self.state = ResilienceState.VALIDATING
        self._record("VALIDATE_CANDIDATE", source_id=source_id)
        return actions

    def validation_result(self, passed: bool, candidate_id: str) -> str:
        """Promote a validated safe candidate or roll back deterministically."""
        if self.state is not ResilienceState.VALIDATING:
            raise RuntimeError("validation result requires VALIDATING state")
        if not candidate_id:
            raise ValueError("candidate_id is required")

        if passed:
            self.state = ResilienceState.RECOVERED
            self._record("PROMOTE", candidate_id=candidate_id, validation_pass=True)
            return "PROMOTE"

        self.state = ResilienceState.ROLLBACK
        self._record("ROLLBACK", candidate_id=candidate_id, validation_pass=False)
        return "ROLLBACK"

    def snapshot(self) -> dict[str, Any]:
        """Return deterministic machine-readable controller evidence."""
        return {
            "state": self.state.value,
            "isolated_sources": sorted(self.isolated_sources),
            "audit": [dict(row) for row in self.audit],
        }
