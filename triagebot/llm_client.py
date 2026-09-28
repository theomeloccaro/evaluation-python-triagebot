from typing import Any

import httpx
import ollama

from triagebot.config import LLM_OPTIONS, LLM_TIMEOUT_SECONDS
from triagebot.errors import OllamaUnavailableError

OLLAMA_DOWN_MESSAGE = (
    "Impossible de joindre Ollama. Vérifiez qu'il est installé et lancé "
    "(commande `ollama serve` ou application Ollama ouverte)."
)


def to_triagebot_error(error: Exception, model: str) -> OllamaUnavailableError:
    """Transforme une erreur de la bibliothèque ollama en message clair."""
    if isinstance(error, ollama.ResponseError):
        if error.status_code == 404:
            return OllamaUnavailableError(
                f"Le modèle '{model}' n'est pas installé. Lancez : ollama pull {model}"
            )
        return OllamaUnavailableError(f"Erreur Ollama : {error.error}")
    return OllamaUnavailableError(OLLAMA_DOWN_MESSAGE)


class LLMClient:
    """Classe de base d'un client LLM (les tests utilisent un faux client)."""

    def ask(
        self, system: str, prompt: str, schema: dict[str, Any] | None = None
    ) -> str:
        raise NotImplementedError


class OllamaClient(LLMClient):
    """Client LLM qui interroge un serveur Ollama local."""

    def __init__(self, model: str, host: str | None = None) -> None:
        # host=None : la bibliothèque utilise OLLAMA_HOST ou localhost:11434.
        self.model = model
        self._client = ollama.Client(host=host, timeout=LLM_TIMEOUT_SECONDS)

    def check_ready(self) -> None:
        try:
            self._client.show(self.model)
        except (ollama.ResponseError, ConnectionError, httpx.HTTPError) as error:
            raise to_triagebot_error(error, self.model) from error

    def ask(
        self, system: str, prompt: str, schema: dict[str, Any] | None = None
    ) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        try:
            response = self._client.chat(
                model=self.model, messages=messages, format=schema, options=LLM_OPTIONS
            )
        except (ollama.ResponseError, ConnectionError, httpx.HTTPError) as error:
            raise to_triagebot_error(error, self.model) from error
        return response.message.content or ""
