import json
from pathlib import Path

from triagebot.errors import TriageBotError
from triagebot.models import TicketResult
from triagebot.report import render_report


def write_text(path: Path, content: str) -> None:
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        raise TriageBotError(f"Impossible d'écrire {path} : {error}") from error


def save_results(results: list[TicketResult], path: Path) -> None:
    payload = [result.to_dict() for result in results]
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def save_report(results: list[TicketResult], path: Path, model: str) -> None:
    write_text(path, render_report(results, model))
