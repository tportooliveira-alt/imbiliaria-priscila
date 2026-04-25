"""Clientes LLM (Gemini + Claude) com lazy loading e fallback.

Princípios:
- Não importa SDK até que precise → testes rodam sem chave.
- Se a chave não existe, devolve resposta fallback informando o usuário.
- Cada cliente tem `available()` que diz se está configurado.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


@dataclass
class RespostaLLM:
    texto: str
    modelo: str
    fallback: bool = False
    metadata: dict | None = None


class LLMClient(Protocol):
    def available(self) -> bool: ...
    def gerar(self, system: str, mensagem: str, historico: list[dict] | None = None) -> RespostaLLM: ...


# ─────────────────────────────────────────────────────────────────────────────
# Fallback (sem chave)
# ─────────────────────────────────────────────────────────────────────────────
class ClienteFallback:
    """Usado quando nenhuma chave está configurada — devolve mensagem fixa."""

    def available(self) -> bool:
        return True

    def gerar(self, system: str, mensagem: str, historico: list[dict] | None = None) -> RespostaLLM:
        return RespostaLLM(
            texto=(
                "Olá! Sou a assistente da Priscila Vasconcelos. "
                "No momento estou em modo offline (sem chaves de IA configuradas). "
                "Deixe seu telefone que ela retorna assim que possível."
            ),
            modelo="fallback",
            fallback=True,
            metadata=None,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Gemini
# ─────────────────────────────────────────────────────────────────────────────
class ClienteGemini:
    def __init__(self, modelo: str = "gemini-2.0-flash", *, use_google_search: bool = False):
        self.modelo = modelo
        self.use_google_search = use_google_search
        self._client = None

    def available(self) -> bool:
        return bool(os.getenv("GOOGLE_API_KEY"))

    def _ensure_client(self):
        if self._client is None:
            from google import genai  # import preguiçoso
            self._client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        return self._client

    def _build_config(self, system: str):
        from google.genai import types

        kwargs = {
            "system_instruction": system,
        }
        if self.use_google_search:
            kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
        return types.GenerateContentConfig(**kwargs)

    def gerar(self, system: str, mensagem: str, historico: list[dict] | None = None) -> RespostaLLM:
        if not self.available():
            return ClienteFallback().gerar(system, mensagem, historico)
        client = self._ensure_client()
        try:
            resp = client.models.generate_content(
                model=self.modelo,
                contents=f"Usuário: {mensagem}",
                config=self._build_config(system),
            )
            metadata = {
                "grounded": bool(getattr(resp.candidates[0], "grounding_metadata", None)) if getattr(resp, "candidates", None) else False,
            }
            return RespostaLLM(texto=resp.text or "", modelo=self.modelo, metadata=metadata)
        except Exception as exc:  # rede / cota / etc.
            return RespostaLLM(
                texto=f"(erro Gemini: {type(exc).__name__}) — retornando ao fallback.",
                modelo=self.modelo,
                fallback=True,
                metadata=None,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Claude
# ─────────────────────────────────────────────────────────────────────────────
class ClienteClaude:
    def __init__(self, modelo: str = "claude-sonnet-4-5"):
        self.modelo = modelo
        self._client = None

    def available(self) -> bool:
        return bool(os.getenv("ANTHROPIC_API_KEY"))

    def _ensure_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        return self._client

    def gerar(self, system: str, mensagem: str, historico: list[dict] | None = None) -> RespostaLLM:
        if not self.available():
            return ClienteFallback().gerar(system, mensagem, historico)
        client = self._ensure_client()
        msgs = list(historico or []) + [{"role": "user", "content": mensagem}]
        try:
            resp = client.messages.create(
                model=self.modelo,
                max_tokens=800,
                system=system,
                messages=msgs,
            )
            texto = "".join(b.text for b in resp.content if hasattr(b, "text"))
            return RespostaLLM(texto=texto, modelo=self.modelo, metadata=None)
        except Exception as exc:
            return RespostaLLM(
                texto=f"(erro Claude: {type(exc).__name__}) — retornando ao fallback.",
                modelo=self.modelo,
                fallback=True,
                metadata=None,
            )
