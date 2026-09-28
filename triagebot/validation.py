import json
from typing import Any

from triagebot.config import (
    CATEGORIES,
    MAX_DRAFT_LENGTH,
    MAX_SEVERITY,
    MIN_SEVERITY,
    SENTIMENTS,
)
from triagebot.language import detect_language
from triagebot.models import Analysis, Draft

REQUIRED_FIELDS = {"category", "severity", "sentiment", "summary"}


class InvalidLLMResponseError(ValueError):
    """La réponse du LLM ne respecte pas le format attendu."""


def parse_json_object(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as error:
        raise InvalidLLMResponseError(f"JSON invalide : {error}") from error
    if not isinstance(data, dict):
        raise InvalidLLMResponseError("la réponse n'est pas un objet JSON")
    return data


def check_fields(data: dict[str, Any]) -> None:
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        raise InvalidLLMResponseError(f"champs manquants : {sorted(missing)}")
    unexpected = data.keys() - REQUIRED_FIELDS
    if unexpected:
        raise InvalidLLMResponseError(f"champs inattendus : {sorted(unexpected)}")


def check_category(value: Any) -> str:
    if value not in CATEGORIES:
        raise InvalidLLMResponseError(f"catégorie non autorisée : {value!r}")
    return value


def check_severity(value: Any) -> int:
    """Vérifie que l'urgence est un entier compris entre 1 et 5."""
    # bool est une sous-classe de int en Python : on l'exclut explicitement.
    if not isinstance(value, int) or isinstance(value, bool):
        raise InvalidLLMResponseError(f"urgence non entière : {value!r}")
    if not MIN_SEVERITY <= value <= MAX_SEVERITY:
        raise InvalidLLMResponseError(f"urgence hors de [1, 5] : {value}")
    return value


def check_sentiment(value: Any) -> str:
    if value not in SENTIMENTS:
        raise InvalidLLMResponseError(f"sentiment non autorisé : {value!r}")
    return value


def check_summary(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidLLMResponseError("résumé vide ou absent")
    return value.strip()


def validate_analysis(raw: str) -> Analysis:
    """Transforme la réponse brute du LLM en Analysis, ou lève une erreur."""
    data = parse_json_object(raw)
    check_fields(data)
    return Analysis(
        category=check_category(data["category"]),
        severity=check_severity(data["severity"]),
        sentiment=check_sentiment(data["sentiment"]),
        summary=check_summary(data["summary"]),
    )


def validate_draft(raw: str, expected_language: str) -> Draft:
    """Vérifie le brouillon renvoyé par le LLM, y compris sa langue."""
    reply = parse_json_object(raw).get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise InvalidLLMResponseError("brouillon vide ou absent")
    if len(reply) > MAX_DRAFT_LENGTH:
        raise InvalidLLMResponseError("brouillon anormalement long")
    language = detect_language(reply)
    if language != expected_language:
        raise InvalidLLMResponseError(
            f"brouillon rédigé en '{language}' au lieu de '{expected_language}'"
        )
    return Draft(language=language, text=reply.strip())
