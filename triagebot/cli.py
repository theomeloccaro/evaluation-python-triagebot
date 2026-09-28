import argparse
import sys
from pathlib import Path

from triagebot.config import (
    DEFAULT_MODEL,
    DEFAULT_REPORT_PATH,
    DEFAULT_RESULTS_PATH,
    DEFAULT_TICKETS_PATH,
)
from triagebot.dashboard import render_dashboard
from triagebot.errors import TriageBotError
from triagebot.exporter import save_report, save_results
from triagebot.llm_client import OllamaClient
from triagebot.loader import load_raw_tickets
from triagebot.pipeline import triage


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="triagebot",
        description="Trie les tickets du support avec un LLM local (Ollama).",
    )
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_TICKETS_PATH)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument("-r", "--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--no-drafts",
        action="store_true",
        help="ne pas générer de brouillons de réponse (plus rapide)",
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> None:
    raw_entries = load_raw_tickets(args.input)
    client = OllamaClient(args.model)
    client.check_ready()
    results = triage(raw_entries, client, with_drafts=not args.no_drafts)
    save_results(results, args.output)
    save_report(results, args.report, args.model)
    print(render_dashboard(results))
    print(f"Résultats : {args.output} | Rapport : {args.report}")


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    """Lance TriageBot et renvoie le code de sortie (0 = succès)."""
    configure_console()
    args = parse_args(argv)
    try:
        run(args)
    except TriageBotError as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur.", file=sys.stderr)
        return 130
    return 0
