"""Core axiomatic integrity helpers for XI-IO."""

from __future__ import annotations

from typing import Any


class AxiomEngine:
    """Lightweight integrity engine used by framework validation flows."""

    def verify_integrity(self, axiom: str, payload: Any) -> bool:
        """Return conservative truthy checks for known axioms.

        The historical framework used a richer engine that may be absent in
        dehydrated snapshots. This implementation preserves runtime behavior by
        keeping checks deterministic and side-effect free.
        """
        key = (axiom or "").upper()
        if key == "LEDGER":
            return payload is not None
        if key == "REAPER":
            return True
        return payload is not None
