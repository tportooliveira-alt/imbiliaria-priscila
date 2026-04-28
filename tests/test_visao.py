"""Testes do classificador de comodos (Studio W3) - Gemini Vision."""
from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from app import visao


def _jpeg_dummy() -> bytes:
    img = Image.new("RGB", (200, 200), color=(50, 90, 120))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return buf.getvalue()


def test_disponivel_sem_chave(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert visao.disponivel() is False


def test_classificar_sem_chave_retorna_none(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    p = tmp_path / "x.jpg"
    p.write_bytes(_jpeg_dummy())
    assert visao.classificar_comodo(p) is None


def test_classificar_arquivo_inexistente(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake")
    assert visao.classificar_comodo(tmp_path / "naoexiste.jpg") is None


def test_normalizar_mapeia_fachada_para_capa():
    assert visao._normalizar("fachada") == "capa"
    assert visao._normalizar("FACHADA.") == "capa"


def test_normalizar_aceita_tipos_validos():
    for t in ["sala", "cozinha", "quarto", "banheiro", "area_externa", "planta"]:
        assert visao._normalizar(t) == t


def test_normalizar_sinonimos_comuns():
    assert visao._normalizar("suite") == "quarto"
    assert visao._normalizar("dormitorio") == "quarto"
    assert visao._normalizar("lavabo") == "banheiro"
    assert visao._normalizar("piscina") == "area_externa"
    assert visao._normalizar("varanda") == "area_externa"


def test_normalizar_resposta_invalida_retorna_none():
    assert visao._normalizar("") is None
    assert visao._normalizar("nao sei") is None
    assert visao._normalizar("xyz123") is None


def test_ordenar_editorial_capa_primeiro():
    imgs = [
        {"id": 1, "tipo": "quarto"},
        {"id": 2, "tipo": "capa"},
        {"id": 3, "tipo": "cozinha"},
        {"id": 4, "tipo": "sala"},
        {"id": 5, "tipo": "banheiro"},
    ]
    ordem = visao.ordenar_editorial(imgs)
    assert ordem == [2, 4, 3, 1, 5]


def test_ordenar_editorial_estavel_dentro_do_bucket():
    imgs = [
        {"id": 10, "tipo": "quarto"},
        {"id": 11, "tipo": "quarto"},
        {"id": 12, "tipo": "sala"},
    ]
    ordem = visao.ordenar_editorial(imgs)
    # sala primeiro (capa nao existe), depois quartos preservando ordem
    assert ordem == [12, 10, 11]


def test_classificar_com_chave_chama_genai(monkeypatch, tmp_path: Path):
    """Mocka o cliente genai para verificar fluxo feliz."""
    monkeypatch.setenv("GOOGLE_API_KEY", "fake")
    p = tmp_path / "foto.jpg"
    p.write_bytes(_jpeg_dummy())

    chamadas = {"n": 0}

    class FakeResp:
        text = "cozinha"

    class FakeModels:
        def generate_content(self, *, model, contents):
            chamadas["n"] += 1
            return FakeResp()

    class FakeClient:
        models = FakeModels()

    import sys
    import types as pytypes
    fake_genai = pytypes.SimpleNamespace(Client=lambda api_key: FakeClient())
    fake_types = pytypes.SimpleNamespace(
        Part=pytypes.SimpleNamespace(from_bytes=lambda data, mime_type: ("PART", mime_type, len(data)))
    )
    fake_google = pytypes.ModuleType("google")
    fake_google_genai = pytypes.ModuleType("google.genai")
    fake_google_genai.Client = fake_genai.Client
    fake_google_genai_types = pytypes.ModuleType("google.genai.types")
    fake_google_genai_types.Part = fake_types.Part
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_google_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_google_genai_types)

    resultado = visao.classificar_comodo(p)
    assert resultado == "cozinha"
    assert chamadas["n"] == 1
