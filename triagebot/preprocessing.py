import re
from dataclasses import dataclass, field
from typing import Any

from triagebot.models import Status, Ticket, TicketResult

UNKNOWN_PLAYER = "inconnu"


@dataclass
class PreparedTickets:
    to_analyze: list[Ticket] = field(default_factory=list)
    skipped: list[TicketResult] = field(default_factory=list)


def coerce_ticket(raw: Any) -> Ticket:
    """Construit un Ticket « au mieux » à partir d'une entrée brute quelconque."""
    entry = raw if isinstance(raw, dict) else {}
    raw_id = entry.get("id")
    player = entry.get("player")
    message = entry.get("message")
    clean_player = player.strip() if isinstance(player, str) else ""
    return Ticket(
        id=raw_id if is_valid_id(raw_id) else None,
        player=clean_player or UNKNOWN_PLAYER,
        message=message if isinstance(message, str) else "",
    )


def is_valid_id(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def rejection_reason(raw: Any) -> str | None:
    if not isinstance(raw, dict):
        return "entrée qui n'est pas un objet JSON"
    if not is_valid_id(raw.get("id")):
        return "identifiant absent ou invalide"
    message = raw.get("message")
    if not isinstance(message, str):
        return "message absent ou qui n'est pas du texte"
    if not re.search(r"\w", message):
        return "message vide ou sans contenu exploitable"
    return None


def duplicate_key(ticket: Ticket) -> tuple[str, str]:
    normalized = " ".join(ticket.message.split()).casefold()
    return ticket.player.casefold(), normalized


class Deduplicator:
    """Mémorise les tickets déjà vus pour repérer identifiants et doublons."""

    def __init__(self) -> None:
        self._ids: set[int] = set()
        self._first_id_by_key: dict[tuple[str, str], int] = {}

    def check(self, ticket: Ticket) -> TicketResult | None:
        if ticket.id is None or ticket.id in self._ids:
            reason = f"identifiant {ticket.label} déjà utilisé par un autre ticket"
            return TicketResult(ticket, Status.IGNORED, ignored_reason=reason)
        key = duplicate_key(ticket)
        if key in self._first_id_by_key:
            original_id = self._first_id_by_key[key]
            return TicketResult(ticket, Status.DUPLICATE, duplicate_of=original_id)
        self._ids.add(ticket.id)
        self._first_id_by_key[key] = ticket.id
        return None


def prepare_tickets(raw_entries: list[Any]) -> PreparedTickets:
    """Sépare les tickets exploitables des entrées inutilisables et des doublons."""
    prepared = PreparedTickets()
    deduplicator = Deduplicator()
    for raw in raw_entries:
        ticket = coerce_ticket(raw)
        reason = rejection_reason(raw)
        skipped: TicketResult | None
        if reason is not None:
            skipped = TicketResult(ticket, Status.IGNORED, ignored_reason=reason)
        else:
            skipped = deduplicator.check(ticket)
        if skipped is None:
            prepared.to_analyze.append(ticket)
        else:
            prepared.skipped.append(skipped)
    return prepared
