from datetime import datetime

from triagebot.escalation import ESCALATION_LABELS, needs_escalation
from triagebot.models import Escalation, Status, TicketResult
from triagebot.stats import Stats, compute_stats

CATEGORY_LABELS: dict[str, str] = {
    "bug": "Bugs",
    "payment": "Paiements",
    "account": "Comptes / connexion",
    "suggestion": "Suggestions",
    "toxicity": "Messages toxiques",
    "autre": "Autres demandes",
}


def md_cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def excerpt(text: str, limit: int = 90) -> str:
    clean = md_cell(text)
    return clean if len(clean) <= limit else clean[: limit - 1] + "…"


def summary_section(stats: Stats) -> list[str]:
    by_status = stats.by_status
    average = "-"
    if stats.average_severity is not None:
        average = f"{stats.average_severity:.1f}"
    lines = [
        "## 1. Synthèse chiffrée",
        "",
        "| Indicateur | Valeur |",
        "|---|---|",
        f"| Tickets reçus | {stats.total} |",
        f"| Tickets analysés automatiquement | {by_status[Status.OK]} |",
        f"| Tickets à vérifier par un humain | {by_status[Status.TO_CHECK]} |",
        f"| Doublons (déjà traités) | {by_status[Status.DUPLICATE]} |",
        f"| Tickets vides ou inutilisables | {by_status[Status.IGNORED]} |",
        f"| Urgence moyenne (1 à 5) | {average} |",
        "",
        "**Répartition par type de demande :**",
        "",
        "| Type | Nombre |",
        "|---|---|",
    ]
    lines += [
        f"| {CATEGORY_LABELS[category]} | {count} |"
        for category, count in stats.by_category.items()
    ]
    return lines


def escalation_row(result: TicketResult) -> str:
    analysis = result.analysis
    summary = analysis.summary if analysis else result.ticket.message
    severity = f"{analysis.severity}/5" if analysis else "-"
    label = ESCALATION_LABELS[result.escalation or Escalation.NONE]
    return (
        f"| {result.ticket.label} | {md_cell(result.ticket.player)} | {label} "
        f"| {severity} | {md_cell(summary)} |"
    )


def escalation_section(results: list[TicketResult]) -> list[str]:
    escalated = [r for r in results if r.escalation and needs_escalation(r.escalation)]
    lines = ["## 2. Tickets à escalader", ""]
    if not escalated:
        return lines + ["Aucun ticket à escalader."]
    return lines + [
        "| Ticket | Joueur | Transmettre à | Urgence | Résumé |",
        "|---|---|---|---|---|",
        *(escalation_row(r) for r in escalated),
    ]


def to_check_row(result: TicketResult) -> str:
    ticket = result.ticket
    return f"| {ticket.label} | {md_cell(ticket.player)} | {excerpt(ticket.message)} |"


def to_check_section(results: list[TicketResult]) -> list[str]:
    to_check = [r for r in results if r.escalation is Escalation.HUMAN_REVIEW]
    lines = [
        "## 3. Tickets à vérifier",
        "",
        "L'analyse automatique n'a pas donné de résultat fiable pour ces tickets :"
        " un membre de l'équipe doit les lire et les classer lui-même.",
        "",
    ]
    if not to_check:
        return lines + ["Aucun ticket à vérifier."]
    return lines + [
        "| Ticket | Joueur | Message |",
        "|---|---|---|",
        *(to_check_row(r) for r in to_check),
    ]


def skip_reason(result: TicketResult) -> str:
    if result.status is Status.DUPLICATE:
        return f"doublon du ticket #{result.duplicate_of}"
    return result.ignored_reason or "ticket inutilisable"


def skipped_section(results: list[TicketResult]) -> list[str]:
    skipped = [r for r in results if r.status in (Status.IGNORED, Status.DUPLICATE)]
    lines = ["## 4. Tickets écartés automatiquement", ""]
    if not skipped:
        return lines + ["Aucun ticket écarté."]
    return lines + [
        f"- Ticket {r.ticket.label} ({md_cell(r.ticket.player)}) : {skip_reason(r)}"
        for r in skipped
    ]


def render_report(results: list[TicketResult], model: str) -> str:
    """Construit le rapport Markdown complet."""
    stats = compute_stats(results)
    generated_at = datetime.now().strftime("%d/%m/%Y à %H:%M")
    lines = [
        "# Rapport de tri des tickets - Dungeon Delivery",
        "",
        f"*Généré le {generated_at} par TriageBot (modèle `{model}`).*",
        "",
        *summary_section(stats),
        "",
        *escalation_section(results),
        "",
        *to_check_section(results),
        "",
        *skipped_section(results),
        "",
        "---",
        "*Les brouillons de réponse aux joueurs se trouvent dans `results.json`"
        " (champ `draft`). Ils doivent être relus avant envoi.*",
    ]
    return "\n".join(lines) + "\n"
