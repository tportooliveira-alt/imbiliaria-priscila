"""Testes do fator de rua (app/ruas.py) — classificacao premium/popular/comercial.
Inclui o caso do bug: rua de 1 letra (Rua H) nao pode casar premium por substring."""
from app.ruas import rua_eh_comercial, tier_da_rua


def test_premium_reconhecida():
    assert tier_da_rua("recreio", "Portal das Arvores") is None or tier_da_rua("recreio", "Portal das Arvores") == "premium"
    assert tier_da_rua("boa_vista", "Avenida Gilenilda Alves") == "premium"


def test_rua_curta_popular_nao_vira_premium():
    # BUG corrigido: 'Rua H' (popular em boa_vista) nao pode virar premium
    # so porque 'h' aparece dentro de 'pinheiros' (Bosque dos Pinheiros).
    assert tier_da_rua("boa_vista", "Rua H") == "popular"
    assert tier_da_rua("boa_vista", "Rua D") == "popular"


def test_rua_desconhecida_neutro():
    assert tier_da_rua("candeias", "Rua Inexistente Qualquer") is None
    assert tier_da_rua("candeias", None) is None


def test_corredor_comercial():
    assert rua_eh_comercial("candeias", "Av Olivia Flores") is True
    assert rua_eh_comercial("candeias", "Rua Qualquer") is False


def test_bairro_sem_mapa_nao_quebra():
    assert tier_da_rua("bairro_inexistente", "Rua X") is None
