"""Read-only Verification review listing."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from progress_engine.evidence.evidence_list import EvidenceListError, load_evidence


class VerificationListError(Exception):
    """Raised when verification reviews cannot be loaded as minimal valid objects."""


BASE_STATUSES = ("pass", "fail", "not_tested")


def load_verification_reviews(root: Path) -> list[dict[str, Any]]:
    try:
        evidence_items = load_evidence(root)
    except EvidenceListError as exc:
        raise VerificationListError(str(exc)) from exc

    return [_review_from_evidence(evidence) for evidence in evidence_items]


def render_verification_reviews(reviews: list[dict[str, Any]]) -> str:
    lines = ["Verification reviews:"]
    if not reviews:
        lines.append("- none")
        return "\n".join(lines)

    for review in reviews:
        lines.append(
            f"- {review['evidence_id']} {review['run_id']} / {review['intervention_id']} "
            f"({review['reviewer_result']}; acceptance: {_format_counts(review['status_counts'])})"
        )

    return "\n".join(lines)


def _review_from_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    claims = evidence.get("claims")
    if not isinstance(claims, list):
        raise VerificationListError(
            f"evidence {evidence['id']} is missing list field: claims"
        )

    status_counts: Counter[str] = Counter()
    for claim_index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            raise VerificationListError(
                f"evidence {evidence['id']} claim {claim_index} must be a mapping"
            )
        mappings = claim.get("acceptance_mapping")
        if not isinstance(mappings, list):
            raise VerificationListError(
                f"evidence {evidence['id']} claim {claim_index} is missing list field: "
                "acceptance_mapping"
            )
        for mapping_index, mapping in enumerate(mappings, start=1):
            if not isinstance(mapping, dict):
                raise VerificationListError(
                    f"evidence {evidence['id']} claim {claim_index} mapping {mapping_index} "
                    "must be a mapping"
                )
            status = mapping.get("status")
            if not isinstance(status, str) or not status:
                raise VerificationListError(
                    f"evidence {evidence['id']} claim {claim_index} mapping {mapping_index} "
                    "is missing string field: status"
                )
            status_counts[status] += 1

    return {
        "evidence_id": evidence["id"],
        "run_id": evidence["run_id"],
        "intervention_id": evidence["intervention_id"],
        "reviewer_result": evidence["reviewer"]["result"],
        "status_counts": dict(status_counts),
    }


def _format_counts(status_counts: dict[str, int]) -> str:
    parts = [f"{status_counts.get(status, 0)} {status}" for status in BASE_STATUSES]
    extra_statuses = sorted(status for status in status_counts if status not in BASE_STATUSES)
    parts.extend(f"{status_counts[status]} {status}" for status in extra_statuses)
    return ", ".join(parts)
