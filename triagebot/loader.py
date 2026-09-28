import json
from pathlib import Path
from typing import Any

from triagebot.errors import TicketFileError


def load_raw_tickets(path: Path) -> list[Any]:
    """Lit le fichier de tickets et renvoie la liste brute qu'il contient.

    Lève TicketFileError si le fichier est absent, illisible ou mal formé.
    """
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise TicketFileError(f"Fichier de tickets introuvable : {path}") from error
    except json.JSONDecodeError as error:
        raise TicketFileError(
            f"Le fichier {path} contient un JSON mal formé "
            f"(ligne {error.lineno}, colonne {error.colno}) : {error.msg}"
        ) from error
    except (OSError, UnicodeDecodeError) as error:
        raise TicketFileError(f"Impossible de lire {path} : {error}") from error
    if not isinstance(data, list):
        raise TicketFileError(f"{path} doit contenir une liste JSON de tickets.")
    return data
