class TriageBotError(Exception):
    """Erreur attendue, affichée proprement à l'utilisateur (sans traceback)."""


class TicketFileError(TriageBotError):
    """Le fichier de tickets est absent, illisible ou mal formé."""


class OllamaUnavailableError(TriageBotError):
    """Ollama n'est pas lancé, pas joignable, ou le modèle est introuvable."""
