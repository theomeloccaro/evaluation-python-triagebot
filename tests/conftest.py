import json
from typing import Any

from triagebot.models import Analysis, Status, Ticket, TicketResult


def analysis_json(**overrides: Any) -> str:
    data: dict[str, Any] = {
        "category": "bug",
        "severity": 3,
        "sentiment": "negative",
        "summary": "Le jeu plante.",
    }
    data.update(overrides)
    return json.dumps(data)


def make_result(
    status: Status = Status.OK, category: str = "bug", severity: int = 3
) -> TicketResult:
    analysis = (
        Analysis(category, severity, "neutral", "Résumé.")
        if status is Status.OK
        else None
    )
    return TicketResult(Ticket(1, "Joueur", "Message"), status, analysis)
