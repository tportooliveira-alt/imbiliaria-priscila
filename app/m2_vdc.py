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
    "candeias": 5000,    # nobre Zona Leste — confirmado no backtest de 792 anuncios reais (17/06)
    "boa_vista": 4710,   # confirmado no backtest de 792 anuncios reais (17/06)
    "alto_maron": 4400,  # [n=11] (estava subestimado antes)
    "centro": 4330,      # [n=11]
    "brasil": 3200,      # recalibrado 17/06 (era 4270): backtest n=10 supervalorizava +28% (real ~3016)
    "ibirapuera": 2800,  # recalibrado 16/06 (era 4300): backtest 9 anuncios reais, mediana apto ~2870 / casa ~2530
    "felicia": 3800,     # recalibrado 17/06 (era 3400, baixei demais): backtest n=22 subvalorizava -21%
    "primavera": 4300,   # recalibrado 17/06 (era 3700): backtest n=21 subvalorizava -17% (Horto Premier/Conde puxam)
    "guarani": 3700,     # sem amostra OLX — mantido
    "panorama": 3400,    # mantido
    "urbis": 3000,       # mantido
    "zabele": 3300,      # recalibrado 17/06 (era 2900): backtest n=11 subvalorizava -19%
    "bateias": 3400,     # recalibrado 17/06 (era 2800): backtest n=16 subvalorizava -35% (real ~3189)
    "vila_serrana": 1600,# [amostra pequena]
    "patagonia": 2600,   # recalibrado 16/06 (era 1900): backtest casas reais ~2969/m² (estava subestimado)
    "alphaville": 4600,  # add 16/06: Terras AlphaVille (condominio de luxo; casas alto/luxo)
    "universidade": 4900,# recalibrado 17/06 (era 3800): e regiao do Alphaville (luxo), subvalorizava -29% [n=21]
    "sao_pedro": 4000,   # add 16/06
    "haras": 4500,       # add 16/06: Haras Camping Club (chacaras/luxo)
    "espirito_santo": 4500,  # add 17/06: backtest n=24 (Verana Reserva premium); subvalorizava -17%
    "jatoba": 3300,      # add 17/06: backtest n=20 (Conveima popular 240-270k)
    "jurema": 4000,      # add 17/06: backtest n=10 (Vitoria Real)
    "lagoa_das_flores": 1800,# add 17/06: rural barato (80-190k)
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

# Fator de RUA dentro do bairro (do mapa calibracao/ruas_vdc.json via app/ruas.py).
# Rua nobre/condominio premium vale mais; rua popular vale menos; nao reconhecida = 1.0 (neutro).
FATOR_RUA: dict[str, float] = {
    "premium": 1.08,   # rua/condominio mais valorizado (suave: o padrao ja captura parte da qualidade)
    "popular": 0.93,   # rua simples/conjunto
}
# Premio quando o imovel e PONTO COMERCIAL numa via comercial (alem do tipo=comercial).
FATOR_PONTO_COMERCIAL = 1.12


# Multiplicador de CASA por bairro (relacao casa/apto NAO e constante: 0,62 a 1,29).
# casaMult = mediana casa R$/m² ÷ base apto do bairro. Recalibrado 16-17/06 com 792 anuncios reais
# (ver docs/CALIBRACAO-AVM-16-06.md e docs/PESQUISA-PRECOS-VDC.md).
M2_CASA_MULT: dict[str, float] = {
    "boa_vista": 1.15,   # recalibrado 16/06 (era 1.286): backtest n=17 casas reais ~6500/m² (1.286 estourava)
    "felicia": 0.88,     # recalibrado 16/06 (era 1.051): backtest casa real ~3016 < apto ~3839
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
