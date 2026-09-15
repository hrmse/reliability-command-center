"""Deterministic domain logic; production adapters stay outside this module."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Evidence:
    signal: str
    value: str
    source: str


@dataclass(frozen=True)
class Decision:
    decision_id: str
    severity: str
    hypothesis: str
    confidence: str
    risk: str
    approval_required: bool
    dry_run_command: str | None
    observations: list[Evidence]


def _evidence_from(payload: dict[str, Any]) -> list[Evidence]:
    raw_evidence = payload.get("evidence", [])
    if not isinstance(raw_evidence, list):
        raise TypeError("evidence must be a list")
    evidence: list[Evidence] = []
    for item in raw_evidence:
        if not isinstance(item, dict) or set(item) != {"signal", "value", "source"}:
            raise ValueError("each evidence item must contain only signal, value and source")
        if not all(isinstance(item[key], str) and item[key].strip() for key in item):
            raise ValueError("evidence values must be non-empty strings")
        evidence.append(Evidence(**item))
    return evidence


def _decision_id(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()[:16]


def decide(payload: dict[str, Any]) -> Decision:
    alert = payload.get("alert", {})
    if not isinstance(alert, dict):
        raise TypeError("alert must be an object")
    evidence = _evidence_from(payload)
    signals = {item.signal: item.value for item in evidence}
    deployment = signals.get("deployment_age_minutes")
    errors = signals.get("http_5xx_ratio", "0")
    public_change = signals.get("public_exposure_change") == "true"
    if errors != "0" and deployment:
        hypothesis, confidence = "Recent deployment correlates with elevated errors.", "medium"
    else:
        hypothesis, confidence = "No corroborated root-cause hypothesis from supplied evidence.", "low"
    risk = "high" if public_change or signals.get("destructive_change") == "true" else "medium"
    approval = risk == "high"
    command = None if approval else "kubectl get pods --namespace {namespace} --selector app={service} --output wide".format(
        namespace=alert.get("namespace", "default"), service=alert.get("service", "unknown")
    )
    return Decision(
        _decision_id(payload),
        str(alert.get("severity", "unknown")),
        hypothesis,
        confidence,
        risk,
        approval,
        command,
        evidence,
    )


def decision_dict(decision: Decision) -> dict[str, object]:
    return asdict(decision)


def render_metrics(decision: Decision) -> str:
    risk_value = {"low": 1, "medium": 2, "high": 3}[decision.risk]
    return "\n".join([
        "# HELP reliability_command_center_decision_risk Incident decision risk (1 low, 2 medium, 3 high).",
        "# TYPE reliability_command_center_decision_risk gauge",
        f'reliability_command_center_decision_risk{{severity="{decision.severity}",risk="{decision.risk}"}} {risk_value}',
        "# HELP reliability_command_center_approval_required Whether a human approval is required.",
        "# TYPE reliability_command_center_approval_required gauge",
        f"reliability_command_center_approval_required {int(decision.approval_required)}",
        "",
    ])
