from typing import Any

from triagebot.analyzer import analyze_ticket
from triagebot.drafts import add_draft
from triagebot.escalation import decide_escalation
from triagebot.llm_client import LLMClient
from triagebot.models import Ticket, TicketResult
from triagebot.preprocessing import prepare_tickets


def sort_key(result: TicketResult) -> tuple[bool, int]:
    ticket_id = result.ticket.id
    return ticket_id is None, ticket_id or 0


def process_ticket(client: LLMClient, ticket: Ticket, with_draft: bool) -> TicketResult:
    result = analyze_ticket(client, ticket)
    if with_draft:
        add_draft(client, result)
    return result


def triage(
    raw_entries: list[Any], client: LLMClient, with_drafts: bool = True
) -> list[TicketResult]:
    """Trie tous les tickets ; seuls les tickets exploitables vont au LLM."""
    prepared = prepare_tickets(raw_entries)
    total = len(prepared.to_analyze)
    print(f"{len(prepared.skipped)} ticket(s) écarté(s) sans appel au LLM.")
    analyzed: list[TicketResult] = []
    for index, ticket in enumerate(prepared.to_analyze, start=1):
        print(f"[{index}/{total}] Analyse du ticket {ticket.label}...", flush=True)
        analyzed.append(process_ticket(client, ticket, with_drafts))
    results = sorted(prepared.skipped + analyzed, key=sort_key)
    for result in results:
        result.escalation = decide_escalation(result)
    return results
