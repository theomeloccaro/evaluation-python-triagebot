from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Status(StrEnum):
    OK = "ok"  # analyse valide
    TO_CHECK = "to_check"  # le LLM n'a pas donné de réponse valide
    IGNORED = "ignored"  # ticket inutilisable, non envoyé au LLM
    DUPLICATE = "duplicate"  # doublon d'un ticket déjà analysé


class Escalation(StrEnum):
    MODERATION = "moderation"  # équipe modération
    SUPPORT_MANAGER = "support_manager"  # responsable support
    HUMAN_REVIEW = "human_review"  # relecture humaine obligatoire
    STANDARD = "standard"  # traitement standard
    NONE = "none"  # ticket écarté (vide, invalide ou doublon) : rien à faire


@dataclass(frozen=True)
class Ticket:
    """Un ticket envoyé par un joueur."""

    id: int | None  # None si l'identifiant fourni était absent ou invalide
    player: str
    message: str

    @property
    def label(self) -> str:
        return "(sans id)" if self.id is None else f"#{self.id}"


@dataclass(frozen=True)
class Analysis:
    category: str
    severity: int
    sentiment: str
    summary: str


@dataclass(frozen=True)
class Draft:
    language: str
    text: str


@dataclass
class TicketResult:
    """Résultat complet du traitement d'un ticket."""

    ticket: Ticket
    status: Status
    analysis: Analysis | None = None
    attempts: int = 0
    errors: list[str] = field(default_factory=list)
    duplicate_of: int | None = None
    ignored_reason: str | None = None
    draft: Draft | None = None
    escalation: Escalation | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
