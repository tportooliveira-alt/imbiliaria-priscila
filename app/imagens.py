"""Pipeline de processamento de imagens.

Recebe bytes de upload (JPEG/PNG/WebP/HEIC), valida magic bytes, remove EXIF,
gera 4 versões em WebP otimizadas e mantém a original.

Hierarquia gerada por imagem:
    assets/imoveis/{slug}/{uuid}/original.jpg
    assets/imoveis/{slug}/{uuid}/2400.webp
    assets/imoveis/{slug}/{uuid}/1200.webp
    assets/imoveis/{slug}/{uuid}/600.webp
    assets/imoveis/{slug}/{uuid}/200.webp
"""
from __future__ import annotations

import io
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:  # pragma: no cover
    pass


MAX_BYTES = 15 * 1024 * 1024  # 15 MB
ALLOWED_MIME_PREFIXES = ("image/",)
TAMANHOS_WEBP = [
    (2400, 85),
    (1200, 82),
    (600, 78),
    (200, 60),
]

# Magic bytes reconhecidos (primeiros bytes do arquivo)
ASSINATURAS = {
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"RIFF": "webp",                     # RIFF + WEBP no offset 8
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"BM": "bmp",
    b"II*\x00": "tiff",
    b"MM\x00*": "tiff",
    b"\x00\x00\x00\x18ftypheic": "heic",
    b"\x00\x00\x00\x18ftypheix": "heic",
    b"\x00\x00\x00\x18ftypmif1": "heic",
    b"\x00\x00\x00\x18ftypheis": "heic",
    b"\x00\x00\x00\x18ftypmsf1": "heic",
    b"\x00\x00\x00\x20ftypheic": "heic",
    b"\x00\x00\x00\x1cftypheic": "heic",
    b"\x00\x00\x00\x1cftypavif": "avif",
    b"\x00\x00\x00\x18ftypavif": "avif",
    b"\x00\x00\x00\x20ftypavif": "avif",
}


class ImagemInvalida(ValueError):
    """Upload rejeitado por validação."""


@dataclass(frozen=True)
class ImagemProcessada:
    arquivo: str          # caminho relativo ao /assets, p.ex. "imoveis/slug/uuid"
    formato_original: str
    largura: int
    altura: int


def _detectar_formato(blob: bytes) -> str:
    if len(blob) < 12:
        raise ImagemInvalida("arquivo muito pequeno")
    head = blob[:32]
    for prefixo, formato in ASSINATURAS.items():
        if head.startswith(prefixo):
            return formato
    # WebP: RIFF????WEBP
    if head[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "webp"
    # ftyp genérico (HEIC/AVIF/HEIF variações): byte 4-7 == "ftyp"
    if len(blob) >= 12 and blob[4:8] == b"ftyp":
        marca = blob[8:12]
        if marca in (b"avif", b"avis"):
            return "avif"
        # tudo que tem ftyp e não é avif tratamos como heic/heif (Pillow + pillow_heif decodificam)
        return "heic"
    # Fallback: tenta abrir com Pillow — se funcionar, aceita.
    try:
        with Image.open(io.BytesIO(blob)) as probe:
            probe.verify()
        with Image.open(io.BytesIO(blob)) as probe:
            return (probe.format or "desconhecido").lower()
    except Exception:
        raise ImagemInvalida("formato de imagem nao suportado") from None


def _abrir_e_normalizar(blob: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(blob))
    img.load()
    img = ImageOps.exif_transpose(img)  # respeita rotação do celular
    # Normaliza modos exóticos (CMYK, P, L, 1, I, F, YCbCr) para RGB/RGBA
    if img.mode == "P":
        # paleta com transparência → RGBA, sem → RGB
        img = img.convert("RGBA" if "transparency" in img.info else "RGB")
    elif img.mode in ("LA",):
        img = img.convert("RGBA")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    return img


def processar_upload(
    blob: bytes,
    *,
    slug: str,
    pasta_destino: Path,
) -> ImagemProcessada:
    """Valida, remove EXIF e gera as 5 versões. Retorna metadados."""
    if not blob:
        raise ImagemInvalida("arquivo vazio")
    if len(blob) > MAX_BYTES:
        raise ImagemInvalida(f"arquivo maior que {MAX_BYTES // (1024 * 1024)} MB")

    formato = _detectar_formato(blob)
    img = _abrir_e_normalizar(blob)
    largura, altura = img.size

    file_id = uuid.uuid4().hex
    base = pasta_destino / "imoveis" / slug / file_id
    base.mkdir(parents=True, exist_ok=True)

    # Original — sem EXIF, mas preservando qualidade ao salvar como JPEG q=95
    sem_exif = Image.new(img.mode, img.size)
    sem_exif.putdata(list(img.getdata()))
    # JPEG não suporta alpha: achata RGBA/LA/P sobre fundo branco antes de salvar
    if sem_exif.mode in ("RGBA", "LA", "P"):
        rgba = sem_exif.convert("RGBA")
        fundo = Image.new("RGB", rgba.size, (255, 255, 255))
        fundo.paste(rgba, mask=rgba.split()[-1])
        para_jpeg = fundo
    else:
        para_jpeg = sem_exif if sem_exif.mode == "RGB" else sem_exif.convert("RGB")
    para_jpeg.save(base / "original.jpg", format="JPEG", quality=95, optimize=True)

    # Variantes WebP, mantendo aspect ratio
    for largura_alvo, qualidade in TAMANHOS_WEBP:
        if largura_alvo >= largura:
            copia = sem_exif.copy()
        else:
            ratio = largura_alvo / largura
            nova_altura = int(altura * ratio)
            copia = sem_exif.resize((largura_alvo, nova_altura), Image.LANCZOS)
        copia.save(base / f"{largura_alvo}.webp", format="WEBP", quality=qualidade, method=6)

    return ImagemProcessada(
        arquivo=f"imoveis/{slug}/{file_id}",
        formato_original=formato,
        largura=largura,
        altura=altura,
    )
