from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from triagebot.llm_client import LLMClient
from triagebot.validation import InvalidLLMResponseError


@dataclass
class RetryOutcome:
    """Résultat d'un appel avec retries : la valeur validée ou les erreurs."""

    value: Any = None
    attempts: int = 0
    errors: list[str] = field(default_factory=list)


def ask_with_retries(
    client: LLMClient,
    system: str,
    prompt: str,
    schema: dict[str, Any],
    validate: Callable[[str], Any],
    max_retries: int,
) -> RetryOutcome:
    """Interroge le LLM jusqu'à obtenir une réponse que `validate` accepte.

    Au plus 1 essai + `max_retries` nouvelles tentatives. Si aucune réponse
    n'est valide, `value` reste None et `errors` explique pourquoi.
    """
    outcome = RetryOutcome()
    for _ in range(1 + max_retries):
        outcome.attempts += 1
        raw = client.ask(system, prompt, schema)
        try:
            outcome.value = validate(raw)
            return outcome
        except InvalidLLMResponseError as error:
            outcome.errors.append(str(error))
    return outcome
