#!/usr/bin/env python3
"""Gera a home de produção (v3-editorial/index.html) a partir de assets/preview.html.

Reproduz o transform que era feito à mão no deploy: remove barra de preview/noindex,
ajusta título e links, injeta tags de produção (canonical/og/manifest) e registra o
service worker com cache-bust baseado em HASH do conteúdo (só muda quando a home muda).
Também sincroniza o nome do cache no v3-editorial/sw.js.

Uso: python3 scripts/build_home.py   (chamado pelo deploy.sh)
"""
from __future__ import annotations
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "preview.html"
DST = ROOT / "v3-editorial" / "index.html"
SW = ROOT / "v3-editorial" / "sw.js"

HEAD_INJECT = (
    '<link rel="canonical" href="https://pvscelosimobiliaria.com/v3-editorial/"/>\n'
    '<meta property="og:image" content="https://pvscelosimobiliaria.com/assets/priscila-tech.jpg"/>\n'
    '<link rel="manifest" href="./manifest.webmanifest"/><meta name="theme-color" content="#16284B"/>\n'
    '<link rel="apple-touch-icon" href="/assets/logo-icone.jpeg"/>\n</head>'
)


def build() -> str:
    h = SRC.read_text(encoding="utf-8")
    for a, b in [
        ('<meta name="robots" content="noindex"/>\n', ""),
        ('<div class="previewbar">✦ PREVIEW do novo site — moderno, com a Ana funcionando de verdade</div>\n', ""),
        ("<title>Priscila Vasconcelos · Imóveis com IA — PREVIEW</title>",
         "<title>Priscila Vasconcelos · Imóveis em Vitória da Conquista</title>"),
        ("location.href='/assets/imovel.html?slug='+it.slug;",
         "location.href='imovel.html?slug='+it.slug;"),
    ]:
        h = h.replace(a, b)
    h = h.replace("</head>", HEAD_INJECT, 1)
    # cache-bust = hash do conteúdo (antes de injetar o SW)
    ver = hashlib.md5(h.encode("utf-8")).hexdigest()[:8]
    sw_reg = (
        '<script>if("serviceWorker" in navigator){window.addEventListener("load",'
        'function(){navigator.serviceWorker.register("./sw.js?v=' + ver + '")'
        '.catch(function(){});});}</script>\n</body>'
    )
    h = h.replace("</body>", sw_reg, 1)
    DST.write_text(h, encoding="utf-8")
    # sincroniza o nome do cache no sw.js (purga cache velho no cliente)
    if SW.exists():
        sw = SW.read_text(encoding="utf-8")
        sw2 = re.sub(r"pv-shell-[0-9a-zA-Z]+", f"pv-shell-{ver}", sw, count=1)
        if sw2 != sw:
            SW.write_text(sw2, encoding="utf-8")
    return ver


if __name__ == "__main__":
    v = build()
    print(f"✅ home gerada → {DST.relative_to(ROOT)} (cache v={v})")
