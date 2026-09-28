from triagebot.config import PAYMENT_ESCALATION_SEVERITY
from triagebot.models import Escalation, Status, TicketResult

ESCALATION_LABELS: dict[Escalation, str] = {
    Escalation.MODERATION: "Équipe modération",
    Escalation.SUPPORT_MANAGER: "Responsable support",
    Escalation.HUMAN_REVIEW: "Relecture humaine obligatoire",
    Escalation.STANDARD: "Traitement standard",
    Escalation.NONE: "Aucune action (ticket écarté)",
}


def decide_escalation(result: TicketResult) -> Escalation:
    """Applique les règles d'escalade, dans l'ordre, au résultat d'un ticket."""
    if result.status in (Status.IGNORED, Status.DUPLICATE):
        return Escalation.NONE
    analysis = result.analysis
    if result.status is Status.TO_CHECK or analysis is None:
        return Escalation.HUMAN_REVIEW
    if analysis.category == "toxicity":
        return Escalation.MODERATION
    if (
        analysis.category == "payment"
        and analysis.severity >= PAYMENT_ESCALATION_SEVERITY
    ):
        return Escalation.SUPPORT_MANAGER
    return Escalation.STANDARD


def needs_escalation(escalation: Escalation) -> bool:
    return escalation in (Escalation.MODERATION, Escalation.SUPPORT_MANAGER)
