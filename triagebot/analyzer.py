from triagebot.config import MAX_RETRIES
from triagebot.llm_client import LLMClient
from triagebot.models import Status, Ticket, TicketResult
from triagebot.prompts import (
    ANALYSIS_SCHEMA,
    ANALYSIS_SYSTEM_PROMPT,
    build_analysis_prompt,
)
from triagebot.retry import ask_with_retries
from triagebot.validation import validate_analysis


def analyze_ticket(
    client: LLMClient, ticket: Ticket, max_retries: int = MAX_RETRIES
) -> TicketResult:
    """Analyse un ticket ; si aucune réponse n'est valide -> statut to_check."""
    outcome = ask_with_retries(
        client,
        ANALYSIS_SYSTEM_PROMPT,
        build_analysis_prompt(ticket),
        ANALYSIS_SCHEMA,
        validate_analysis,
        max_retries,
    )
    return TicketResult(
        ticket=ticket,
        status=Status.OK if outcome.value else Status.TO_CHECK,
        analysis=outcome.value,
        attempts=outcome.attempts,
        errors=outcome.errors,
    )
