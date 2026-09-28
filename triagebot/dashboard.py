from triagebot.models import Status, TicketResult
from triagebot.stats import Stats, compute_stats

WIDTH = 60
BAR_CHAR = "█"
STATUS_LABELS: dict[Status, str] = {
    Status.OK: "Analysés",
    Status.TO_CHECK: "À vérifier (to_check)",
    Status.DUPLICATE: "Doublons",
    Status.IGNORED: "Ignorés (inutilisables)",
}


def title(text: str) -> str:
    return f"\n{text}\n{'─' * WIDTH}"


def format_severity(average: float | None) -> str:
    return "-" if average is None else f"{average:.2f} / 5"


def status_lines(stats: Stats) -> list[str]:
    return [f"  {STATUS_LABELS[s]:<26}{n:>4}" for s, n in stats.by_status.items()]


def category_lines(stats: Stats) -> list[str]:
    return [
        f"  {category:<12}{count:>4}  {BAR_CHAR * count}"
        for category, count in stats.by_category.items()
    ]


def urgent_lines(stats: Stats) -> list[str]:
    if not stats.most_urgent:
        return ["  (aucun ticket analysé)"]
    lines = []
    for rank, result in enumerate(stats.most_urgent, start=1):
        analysis = result.analysis
        if analysis:
            lines.append(
                f"  {rank}. {result.ticket.label} [{analysis.severity}/5] "
                f"{analysis.category} - {analysis.summary}"
            )
    return lines


def render_dashboard(results: list[TicketResult]) -> str:
    """Construit le texte complet du tableau de bord."""
    stats = compute_stats(results)
    lines = [
        "═" * WIDTH,
        "TRIAGEBOT - Dungeon Delivery".center(WIDTH),
        "═" * WIDTH,
        f"  Tickets reçus : {stats.total}",
        f"  Urgence moyenne : {format_severity(stats.average_severity)}",
        title("Statuts"),
        *status_lines(stats),
        title("Tickets par catégorie"),
        *category_lines(stats),
        title(f"Top {len(stats.most_urgent)} des tickets les plus urgents"),
        *urgent_lines(stats),
        "═" * WIDTH,
    ]
    return "\n".join(lines)
