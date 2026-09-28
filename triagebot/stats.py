from collections import Counter
from dataclasses import dataclass

from triagebot.config import CATEGORIES
from triagebot.models import Status, TicketResult

TOP_URGENT_COUNT = 3


@dataclass(frozen=True)
class Stats:
    total: int
    by_status: dict[Status, int]
    by_category: dict[str, int]
    average_severity: float | None
    most_urgent: list[TicketResult]


def analyzed_results(results: list[TicketResult]) -> list[TicketResult]:
    return [r for r in results if r.status is Status.OK and r.analysis]


def severity_of(result: TicketResult) -> int:
    return result.analysis.severity if result.analysis else 0


def count_by_status(results: list[TicketResult]) -> dict[Status, int]:
    counts = {status: 0 for status in Status}
    for result in results:
        counts[result.status] += 1
    return counts


def compute_stats(results: list[TicketResult]) -> Stats:
    """Calcule les statistiques affichées dans le dashboard et le rapport."""
    analyzed = analyzed_results(results)
    categories = Counter(r.analysis.category for r in analyzed if r.analysis)
    severities = [severity_of(r) for r in analyzed]
    ranked = sorted(analyzed, key=lambda r: (-severity_of(r), r.ticket.id or 0))
    return Stats(
        total=len(results),
        by_status=count_by_status(results),
        by_category={c: categories.get(c, 0) for c in CATEGORIES},
        average_severity=sum(severities) / len(severities) if severities else None,
        most_urgent=ranked[:TOP_URGENT_COUNT],
    )
