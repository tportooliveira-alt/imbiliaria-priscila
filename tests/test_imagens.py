"""Testes do pipeline de imagens (Pillow multi-resolucao + EXIF strip)."""
from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from app import imagens


def _gerar_jpeg(largura: int = 3000, altura: int = 2000) -> bytes:
    img = Image.new("RGB", (largura, altura), color=(120, 80, 60))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def test_processar_upload_gera_original_e_4_webps():
    blob = _gerar_jpeg()
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp)
        proc = imagens.processar_upload(blob, slug="casa-norte", pasta_destino=destino)

        pasta = destino / proc.arquivo
        assert (pasta / "original.jpg").exists()
        for largura, _ in imagens.TAMANHOS_WEBP:
            assert (pasta / f"{largura}.webp").exists(), f"falta {largura}.webp"


def test_processar_upload_rejeita_bytes_que_nao_sao_imagem():
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(imagens.ImagemInvalida):
            imagens.processar_upload(
                b"isso aqui nao eh imagem nenhuma",
                slug="x",
                pasta_destino=Path(tmp),
            )


def test_processar_upload_rejeita_arquivo_acima_do_limite():
    blob = b"\xff\xd8\xff" + b"0" * (imagens.MAX_BYTES + 100)
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(imagens.ImagemInvalida):
            imagens.processar_upload(blob, slug="x", pasta_destino=Path(tmp))


def test_processar_upload_strip_exif():
    """Verifica que metadados EXIF nao sobrevivem ao pipeline."""
    img = Image.new("RGB", (1500, 1000), color=(50, 80, 100))
    buf = io.BytesIO()
    # injeta EXIF com GPS falso
    exif = img.getexif()
    exif[0x0112] = 1  # Orientation
    img.save(buf, format="JPEG", exif=exif.tobytes(), quality=95)
    blob = buf.getvalue()

    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp)
        proc = imagens.processar_upload(blob, slug="casa", pasta_destino=destino)
        pasta = destino / proc.arquivo

        # WebP gerado nao deve ter EXIF
        for largura, _ in imagens.TAMANHOS_WEBP:
            arq = pasta / f"{largura}.webp"
            with Image.open(arq) as im:
                exif_saida = im.getexif()
                assert len(exif_saida) == 0, f"EXIF nao foi removido em {largura}.webp"


def test_uuid_unico_entre_uploads():
    blob = _gerar_jpeg(800, 600)
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp)
        a = imagens.processar_upload(blob, slug="casa", pasta_destino=destino)
        b = imagens.processar_upload(blob, slug="casa", pasta_destino=destino)
        assert a.arquivo != b.arquivo
