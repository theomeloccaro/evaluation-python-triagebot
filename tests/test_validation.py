import json

import pytest

from tests.conftest import analysis_json
from triagebot.models import Analysis
from triagebot.validation import (
    InvalidLLMResponseError,
    validate_analysis,
    validate_draft,
)


def test_valid_response_is_accepted() -> None:
    assert validate_analysis(analysis_json()) == Analysis(
        "bug", 3, "negative", "Le jeu plante."
    )


@pytest.mark.parametrize("category", ["remboursement", "BUG", "", None, 3])
def test_unknown_category_is_rejected(category: object) -> None:
    with pytest.raises(InvalidLLMResponseError, match="catégorie"):
        validate_analysis(analysis_json(category=category))


@pytest.mark.parametrize("severity", [0, 6, -1, 100])
def test_severity_out_of_range_is_rejected(severity: int) -> None:
    with pytest.raises(InvalidLLMResponseError, match="hors de"):
        validate_analysis(analysis_json(severity=severity))


@pytest.mark.parametrize("severity", ["3", 3.5, 3.0, True, None])
def test_non_integer_severity_is_rejected(severity: object) -> None:
    with pytest.raises(InvalidLLMResponseError, match="non entière"):
        validate_analysis(analysis_json(severity=severity))


@pytest.mark.parametrize("severity", [1, 5])
def test_severity_bounds_are_accepted(severity: int) -> None:
    assert validate_analysis(analysis_json(severity=severity)).severity == severity


def test_unknown_sentiment_is_rejected() -> None:
    with pytest.raises(InvalidLLMResponseError, match="sentiment"):
        validate_analysis(analysis_json(sentiment="furious"))


@pytest.mark.parametrize("summary", ["", "   ", None, 42])
def test_empty_summary_is_rejected(summary: object) -> None:
    with pytest.raises(InvalidLLMResponseError, match="résumé"):
        validate_analysis(analysis_json(summary=summary))


def test_missing_field_is_rejected() -> None:
    raw = '{"category": "bug", "severity": 3, "sentiment": "neutral"}'
    with pytest.raises(InvalidLLMResponseError, match="manquants"):
        validate_analysis(raw)


def test_extra_field_is_rejected() -> None:
    with pytest.raises(InvalidLLMResponseError, match="inattendus"):
        validate_analysis(analysis_json(refund=1000))


@pytest.mark.parametrize("raw", ["", "pas du json", "[1, 2]", '"bug"', "null"])
def test_invalid_json_is_rejected(raw: str) -> None:
    with pytest.raises(InvalidLLMResponseError):
        validate_analysis(raw)


FRENCH_REPLY = "Bonjour, merci pour votre message, notre équipe va regarder."
GERMAN_REPLY = "Hallo, danke für Ihre Nachricht, unser Team prüft Ihre Anfrage."


def draft_json(reply: object) -> str:
    return json.dumps({"reply": reply})


def test_valid_draft_is_accepted() -> None:
    draft = validate_draft(draft_json(f"  {GERMAN_REPLY}  "), expected_language="de")
    assert (draft.language, draft.text) == ("de", GERMAN_REPLY)


def test_draft_in_wrong_language_is_rejected() -> None:
    with pytest.raises(InvalidLLMResponseError, match="au lieu de 'de'"):
        validate_draft(draft_json(FRENCH_REPLY), expected_language="de")


@pytest.mark.parametrize("raw", [draft_json(""), draft_json(None), "{}", "pas du json"])
def test_invalid_draft_is_rejected(raw: str) -> None:
    with pytest.raises(InvalidLLMResponseError):
        validate_draft(raw, expected_language="fr")
