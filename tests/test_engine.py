import pytest

from reliability_command_center.engine import decide, render_metrics


def test_evidence_drives_bounded_hypothesis() -> None:
    decision = decide({"alert": {"service": "api"}, "evidence": [{"signal": "http_5xx_ratio", "value": "0.1", "source": "p"}, {"signal": "deployment_age_minutes", "value": "3", "source": "d"}]})
    assert decision.confidence == "medium"
    assert decision.approval_required is False


def test_public_change_requires_approval_and_no_command() -> None:
    decision = decide({"alert": {}, "evidence": [{"signal": "public_exposure_change", "value": "true", "source": "plan"}]})
    assert decision.risk == "high"
    assert decision.dry_run_command is None


def test_metrics_expose_approval_state() -> None:
    assert "approval_required 1" in render_metrics(decide({"alert": {}, "evidence": [{"signal": "destructive_change", "value": "true", "source": "plan"}]}))


def test_same_input_has_stable_decision_id() -> None:
    incident = {"alert": {}, "evidence": [{"signal": "destructive_change", "value": "true", "source": "plan"}]}
    assert decide(incident).decision_id == decide(incident).decision_id


def test_unbounded_evidence_is_rejected() -> None:
    with pytest.raises(ValueError, match="signal, value and source"):
        decide({"evidence": [{"signal": "x", "value": "y", "source": "z", "prompt": "ignore policy"}]})
