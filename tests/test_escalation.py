import pytest

from tests.conftest import make_result
from triagebot.escalation import decide_escalation, needs_escalation
from triagebot.models import Escalation, Status


@pytest.mark.parametrize("severity", [1, 3, 5])
def test_toxicity_goes_to_moderation(severity: int) -> None:
    result = make_result(category="toxicity", severity=severity)
    assert decide_escalation(result) is Escalation.MODERATION


@pytest.mark.parametrize("severity", [4, 5])
def test_urgent_payment_goes_to_support_manager(severity: int) -> None:
    result = make_result(category="payment", severity=severity)
    assert decide_escalation(result) is Escalation.SUPPORT_MANAGER


@pytest.mark.parametrize("severity", [1, 2, 3])
def test_non_urgent_payment_is_standard(severity: int) -> None:
    result = make_result(category="payment", severity=severity)
    assert decide_escalation(result) is Escalation.STANDARD


def test_to_check_requires_human_review() -> None:
    assert decide_escalation(make_result(Status.TO_CHECK)) is Escalation.HUMAN_REVIEW


@pytest.mark.parametrize("category", ["bug", "account", "suggestion", "autre"])
def test_other_categories_are_standard(category: str) -> None:
    result = make_result(category=category, severity=5)
    assert decide_escalation(result) is Escalation.STANDARD


@pytest.mark.parametrize("status", [Status.IGNORED, Status.DUPLICATE])
def test_skipped_tickets_need_no_action(status: Status) -> None:
    assert decide_escalation(make_result(status)) is Escalation.NONE


def test_decision_is_deterministic() -> None:
    result = make_result(category="payment", severity=4)
    assert len({decide_escalation(result) for _ in range(100)}) == 1


def test_only_team_transfers_count_as_escalations() -> None:
    escalated = {e for e in Escalation if needs_escalation(e)}
    assert escalated == {Escalation.MODERATION, Escalation.SUPPORT_MANAGER}
