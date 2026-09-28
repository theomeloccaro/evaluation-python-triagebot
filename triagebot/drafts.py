from triagebot.config import MAX_RETRIES
from triagebot.language import detect_language
from triagebot.llm_client import LLMClient
from triagebot.models import Status, TicketResult
from triagebot.prompts import DRAFT_SCHEMA, DRAFT_SYSTEM_PROMPT, build_draft_prompt
from triagebot.retry import ask_with_retries
from triagebot.validation import validate_draft

DRAFTABLE_STATUSES = (Status.OK, Status.TO_CHECK)


def add_draft(
    client: LLMClient, result: TicketResult, max_retries: int = MAX_RETRIES
) -> None:
    """Ajoute un brouillon de réponse au résultat (tickets exploitables seulement)."""
    if result.status not in DRAFTABLE_STATUSES:
        return
    category = result.analysis.category if result.analysis else None
    # La langue est détectée par le code, pas par le LLM : c'est plus fiable.
    language = detect_language(result.ticket.message)
    outcome = ask_with_retries(
        client,
        DRAFT_SYSTEM_PROMPT,
        build_draft_prompt(result.ticket, category, language),
        DRAFT_SCHEMA,
        lambda raw: validate_draft(raw, language),
        max_retries,
    )
    result.draft = outcome.value
    result.errors.extend(f"brouillon : {error}" for error in outcome.errors)
