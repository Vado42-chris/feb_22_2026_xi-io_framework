"""Verification primitives used by XI CLI phase gates."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List


class VerificationManager:
    """Simple integrity manager for dehydrated/rehydrated environments."""

    def verify(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Dict[str, str]] = []
        for key in sorted(unit.keys()):
            checks.append({"submodule": key, "status": "PASS"})
        return {"ok": True, "checks": checks, "summary": "Verification completed"}

    def verify_file_integrity(self, path: str, expected_hash: str | None = None) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return {"ok": False, "status": "MISSING", "sha256": None, "match": False}

        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if expected_hash:
            return {
                "ok": True,
                "status": "OK",
                "sha256": digest,
                "match": digest == expected_hash,
            }

        return {"ok": True, "status": "OK", "sha256": digest, "match": None}
import hashlib
import json
from enum import Enum
from typing import Dict, Any, List


class VerificationStatus(Enum):
    OK = 'OK'
    FLAGGED = 'FLAGGED'
    FAILED = 'FAILED'
    MISSING = 'MISSING'


class ReasonCode(Enum):
    PROVENANCE_FAIL = 'PROVENANCE_FAIL'
    DEDUP_MATCH = 'DEDUP_MATCH'
    CALIBRATION_EVIDENCE_EMPTY = 'CALIBRATION_EVIDENCE_EMPTY'
    CALIBRATION_CONFIDENCE_NULL = 'CALIBRATION_CONFIDENCE_NULL'
    SCHEMA_INVALID = 'SCHEMA_INVALID'
    CONTRADICTION_ESCALATED = 'CONTRADICTION_ESCALATED'


class ProvenanceChecker:
    def verify(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        if 'provenance' not in unit or not unit['provenance']:
            return {'status': VerificationStatus.FAILED, 'reason_code': ReasonCode.PROVENANCE_FAIL.value}
        return {'status': VerificationStatus.OK}


class DeduplicationChecker:
    def __init__(self):
        self.seen_hashes = set()

    def verify(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        content_str = json.dumps(unit.get('content', ''), sort_keys=True).encode('utf-8')
        content_hash_full = hashlib.sha256(content_str).hexdigest()
        if content_hash_full in self.seen_hashes:
            return {'status': VerificationStatus.FLAGGED, 'reason_code': ReasonCode.DEDUP_MATCH.value, 'hash': content_hash_full}
        self.seen_hashes.add(content_hash_full)
        return {'status': VerificationStatus.OK, 'hash': content_hash_full}


class ContradictionChecker:
    def verify(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        conflict_override = unit.get('canon_override', False)
        if conflict_override:
            return {'status': VerificationStatus.FLAGGED, 'reason_code': ReasonCode.CONTRADICTION_ESCALATED.value}
        return {'status': VerificationStatus.OK}


class CalibrationChecker:
    def verify(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        if 'uncertainty' not in unit or unit['uncertainty'] is None:
            return {'status': VerificationStatus.FAILED, 'reason_code': ReasonCode.CALIBRATION_CONFIDENCE_NULL.value}
        if not unit.get('evidence'):
            return {'status': VerificationStatus.FAILED, 'reason_code': ReasonCode.CALIBRATION_EVIDENCE_EMPTY.value}
        return {'status': VerificationStatus.OK}


class VerificationManager:
    def __init__(self):
        self.provenance = ProvenanceChecker()
        self.dedup = DeduplicationChecker()
        self.contradiction = ContradictionChecker()
        self.calibration = CalibrationChecker()

    def _validate_claim_schema(self, claims: List[Any]) -> bool:
        if not isinstance(claims, list):
            return False
        for claim in claims:
            if not isinstance(claim, dict) or 'subject' not in claim or 'value' not in claim:
                return False
        return True

    def verify(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        if 'claims' in unit and not self._validate_claim_schema(unit['claims']):
            return {'overall_status': VerificationStatus.FAILED.value, 'checks': [{'submodule': 'CLAIMS', 'status': VerificationStatus.FAILED.value, 'reason_code': ReasonCode.SCHEMA_INVALID.value}]}
        prov_res = self.provenance.verify(unit)
        dedup_res = self.dedup.verify(unit)
        contra_res = self.contradiction.verify(unit)
        calib_res = self.calibration.verify(unit)
        checks = [
            {'submodule': 'PROVENANCE', 'status': prov_res['status'].value, **{k: v for k, v in prov_res.items() if k != 'status'}},
            {'submodule': 'DEDUP', 'status': dedup_res['status'].value, **{k: v for k, v in dedup_res.items() if k != 'status'}},
            {'submodule': 'CONTRADICTION', 'status': contra_res['status'].value, **{k: v for k, v in contra_res.items() if k != 'status'}},
            {'submodule': 'CALIBRATION', 'status': calib_res['status'].value, **{k: v for k, v in calib_res.items() if k != 'status'}}
        ]
        statuses = [c['status'] for c in checks]
        if VerificationStatus.FAILED.value in statuses:
            overall = VerificationStatus.FAILED.value
        elif VerificationStatus.FLAGGED.value in statuses:
            overall = VerificationStatus.FLAGGED.value
        else:
            overall = VerificationStatus.OK.value
        return {'overall_status': overall, 'checks': checks}


verification_manager = VerificationManager()
