"""Base de m² medio por bairro de Vitoria da Conquista (BA).

Valores indicativos coletados de portais imobiliarios + experiencia local
da Priscila (atualizado 04/2026). Devem ser revisados trimestralmente.

Unidade: R$/m² medio para imoveis de padrao medio prontos para morar.
"""
from __future__ import annotations

from typing import Literal

PadraoConstrucao = Literal["simples", "medio", "alto", "luxo"]
EstadoConservacao = Literal["reformado", "bom", "regular", "precisa_reforma"]
FaixaIdade = Literal["novo", "0_10", "10_20", "20_mais"]


# R$/m² medio de AREA CONSTRUIDA por bairro (padrao medio, conservacao bom).
# Medianas de OFERTA dos portais imobiliarios + experiencia local (estudo 2024-2025).
# Sao referencia de mercado (ask price) — a avaliacao final/de fechamento e da Priscila.
M2_VDC: dict[str, float] = {
    "recreio": 5000,     # recalibrado 16/06 (era 6060): backtest 11 anuncios reais, mediana apto ~4630/m² [estava ancorado no topo]
    "candeias": 5000,    # [n=43] bairro nobre Zona Leste
    "boa_vista": 4710,   # [n=33]
    "alto_maron": 4400,  # [n=11] (estava subestimado antes)
    "centro": 4330,      # [n=11]
    "brasil": 4270,      # [n=6] amostra menor
    "ibirapuera": 2800,  # recalibrado 16/06 (era 4300): backtest 9 anuncios reais, mediana apto ~2870 / casa ~2530
    "felicia": 3400,     # recalibrado 16/06 (era 3700): backtest mediana apto ~3535 / casa ~3175
    "primavera": 3700,   # sem amostra OLX — mantido
    "guarani": 3700,     # sem amostra OLX — mantido
    "panorama": 3400,    # mantido
    "urbis": 3000,       # mantido
    "zabele": 2900,      # mantido
    "bateias": 2800,     # mantido
    "vila_serrana": 1600,# [amostra pequena]
    "patagonia": 2600,   # recalibrado 16/06 (era 1900): backtest casas reais ~2969/m² (estava subestimado)
    "outro": 3800,       # fallback
}

# R$/m² de TERRENO (terra nua) por bairro — onde ha dado de mercado.
# Para bairros sem dado, usa-se fracao do m² construido (ver terreno_do_bairro).
M2_TERRENO_VDC: dict[str, float] = {
    "felicia": 1185,   # OLX jun/2026 [n=2]
    "recreio": 1042,   # [n=1] amostra pequena
    "centro": 1021,    # [n=4]
    "boa_vista": 900,  # [n=3]
    "candeias": 836,   # [n=4] (modelo antigo punha 1620 — superestimava)
    "brasil": 700,     # estimado
    "alto_maron": 600, # estimado
    "patagonia": 1226,  # estimado (periferico)
    "vila_serrana": 512,
    "zabele": 260,     # extremo metropolitano
}

# Multiplicadores aplicados sobre o m² do bairro
FATOR_PADRAO: dict[PadraoConstrucao, float] = {
    "simples": 0.78,
    "medio": 1.00,
    "alto": 1.12,   # recalibrado 16/06 (backtest 66 anuncios reais VDC: alto premium/m2 menor que 1.25)
    "luxo": 1.30,   # recalibrado 16/06 (luxo grande NAO comanda +55%/m2 em VDC; era 1.55)
}

FATOR_ESTADO: dict[EstadoConservacao, float] = {
    "reformado": 1.10,
    "bom": 1.00,
    "regular": 0.90,
    "precisa_reforma": 0.75,
}

FATOR_IDADE: dict[FaixaIdade, float] = {
    "novo": 1.08,
    "0_10": 1.00,
    "10_20": 0.93,
    "20_mais": 0.85,
}

# ── Fatores adicionais (calculadora avancada) ────────────────────────────────
TipoImovel = Literal["casa", "apartamento", "cobertura", "terreno", "comercial"]
Mobilia = Literal["vazio", "semi", "mobiliado"]
Lazer = Literal["sem", "basico", "completo"]
Vista = Literal["comum", "livre", "privilegiada"]

# Tipo: cobertura agrega valor; terreno e avaliado pelo m² de TERRENO (fracao do construido);
# comercial tem leve premio por ponto/fluxo.
FATOR_TIPO: dict[TipoImovel, float] = {
    "casa": 1.00,
    "apartamento": 1.00,
    "cobertura": 1.12,
    "terreno": 0.42,
    "comercial": 1.20,
}

FATOR_MOBILIA: dict[Mobilia, float] = {
    "vazio": 1.00,
    "semi": 1.03,
    "mobiliado": 1.07,
}

# Lazer/condominio: piscina, academia, portaria 24h, salao etc.
FATOR_LAZER: dict[Lazer, float] = {
    "sem": 1.00,
    "basico": 1.03,    # 1-2 itens
    "completo": 1.08,  # lazer completo / condominio clube
}

FATOR_VISTA: dict[Vista, float] = {
    "comum": 1.00,
    "livre": 1.03,
    "privilegiada": 1.06,
}


# Multiplicador de CASA por bairro (relacao casa/apto NAO e constante: 0,62 a 1,29).
# casaMult = mediana casa R$/m² ÷ base apto do bairro (OLX jun/2026, 812 anuncios).
M2_CASA_MULT: dict[str, float] = {
    "boa_vista": 1.286,  # casas valem MAIS que aptos aqui [n=42]
    "felicia": 1.051,
    "candeias": 1.022,
    "brasil": 0.870,
    "alto_maron": 0.751,
    "recreio": 0.632,    # aptos valem mais (verticalizacao) [n=27]
    "vila_serrana": 1.43, # n=57 (regiao Zabele, 2 portais) — horizontal
    "patagonia": 1.17,    # n=19
    "centro": 0.615,
    "_def": 1.000,
}


def normalizar_bairro(bairro: str) -> str:
    """Normaliza nome do bairro para chave da base."""
    import unicodedata

    s = unicodedata.normalize("NFKD", bairro).encode("ascii", "ignore").decode()
    s = s.lower().strip().replace(" ", "_").replace("-", "_")
    return s if s in M2_VDC else "outro"


def m2_do_bairro(bairro: str) -> tuple[str, float]:
    """Retorna (chave_normalizada, valor_m2)."""
    chave = normalizar_bairro(bairro)
    return chave, M2_VDC[chave]


def terreno_do_bairro(chave: str, m2_construido: float) -> float:
    """R$/m² de terreno do bairro. Usa dado de mercado quando ha;
    senao estima como ~30% do m² construido (heuristica transparente)."""
    if chave in M2_TERRENO_VDC:
        return M2_TERRENO_VDC[chave]
    return round(m2_construido * 0.30, 2)


def fator_area(area: float) -> float:
    """Elasticidade NAO LINEAR do m² pela metragem (documentada nos portais de VDC):
    unidades pequenas tem premio por m² (alta demanda/locacao); plantas muito
    grandes sofrem desagio (superadequacao, baixa liquidez)."""
    if area <= 45:
        return 1.05
    if area <= 60:
        return 1.03
    if area <= 90:
        return 0.99
    if area <= 120:
        return 1.00
    if area <= 150:
        return 1.01
    if area <= 200:
        return 0.90   # recalibrado 16/06 (era 0.95): casas 150-200m2 sofrem mais desagio em VDC
    if area <= 300:
        return 0.80   # recalibrado 16/06 (era 0.88): casas 200-300m2 com R$/m2 bem menor (backtest)
    if area <= 450:
        return 0.72
    return 0.60  # casarao/planta colossal: forte desagio (superadequacao)


BAIRROS_DISPONIVEIS = sorted(k for k in M2_VDC if k != "outro")
