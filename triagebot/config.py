from pathlib import Path

DEFAULT_MODEL = "llama3.2:3b"

DEFAULT_TICKETS_PATH = Path("tickets.json")
DEFAULT_RESULTS_PATH = Path("results.json")
DEFAULT_REPORT_PATH = Path("report.md")

CATEGORIES: tuple[str, ...] = (
    "bug",
    "payment",
    "account",
    "suggestion",
    "toxicity",
    "autre",
)
SENTIMENTS: tuple[str, ...] = ("positive", "neutral", "negative")
MIN_SEVERITY = 1
MAX_SEVERITY = 5

# Température à 0 : on veut des réponses aussi stables que possible.
LLM_OPTIONS: dict[str, float] = {"temperature": 0.0}

# Nombre de nouvelles tentatives si la réponse du LLM est invalide
# (soit 1 essai initial + 2 retries). Au-delà : statut to_check.
MAX_RETRIES = 2

# Délai maximum d'attente d'une réponse d'Ollama (en secondes).
LLM_TIMEOUT_SECONDS = 120.0

# Longueur maximale acceptée pour un brouillon de réponse (en caractères).
MAX_DRAFT_LENGTH = 1500

# Un ticket « payment » d'urgence >= à ce seuil va au responsable support.
PAYMENT_ESCALATION_SEVERITY = 4
