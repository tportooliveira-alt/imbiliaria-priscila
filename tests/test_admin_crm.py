"""Testes dos endpoints admin de CRM (leads + dashboard) e do hook do funil."""
from __future__ import annotations

import gc
import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    monkeypatch.setenv("DEV_OPEN_ADMIN", "0")
    monkeypatch.setenv(
        "JWT_SECRET",
        "test-secret-key-com-tamanho-suficiente-para-hmac-sha256-aaaaaa",
    )
    from app import db as db_mod
    importlib.reload(db_mod)
    from app import auth as auth_mod
    importlib.reload(auth_mod)
    from app import leads as leads_mod
    importlib.reload(leads_mod)
    from app import routes_admin as ra
    importlib.reload(ra)
    from app import routes_publicas as rp
    importlib.reload(rp)
    from app import routes_crm as rc
    importlib.reload(rc)

    db_mod.init_db()
    auth_mod.criar_usuario("priscila@vdc.com", "senha-segura-123", role="admin")

    import server as server_mod
    importlib.reload(server_mod)

    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()


def _login(cli: TestClient) -> dict:
    r = cli.post("/api/auth/login", json={"email": "priscila@vdc.com", "senha": "senha-segura-123"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_dashboard_exige_token(cliente):
    r = cliente.get("/api/admin/dashboard")
    assert r.status_code == 401


def test_dashboard_retorna_estrutura(cliente):
    h = _login(cliente)
    r = cliente.get("/api/admin/dashboard", headers=h)
    assert r.status_code == 200
    body = r.json()
    for k in ("total_leads", "por_estagio", "por_temperatura", "por_origem",
              "novos_7d", "simulacoes", "avaliacoes", "imoveis_ativos", "ultimos_leads"):
        assert k in body


def test_listar_leads_vazio(cliente):
    h = _login(cliente)
    r = cliente.get("/api/admin/leads", headers=h)
    assert r.status_code == 200
    assert r.json() == {"leads": [], "total": 0}


def test_criar_lead_manual(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/leads", headers=h,
        json={"nome": "Teste", "telefone": "43911111111", "origem": "manual"},
    )
    assert r.status_code == 201
    lid = r.json()["id"]
    r = cliente.get(f"/api/admin/leads/{lid}", headers=h)
    assert r.status_code == 200
    assert r.json()["nome"] == "Teste"


def test_criar_lead_sem_dados_falha(cliente):
    h = _login(cliente)
    r = cliente.post("/api/admin/leads", headers=h, json={})
    assert r.status_code == 400


def test_atualizar_estagio_e_recalcular_temperatura(cliente):
    h = _login(cliente)
    r = cliente.post("/api/admin/leads", headers=h,
                     json={"nome": "x", "telefone": "43922222222", "origem": "manual"})
    lid = r.json()["id"]
    r = cliente.patch(f"/api/admin/leads/{lid}", headers=h, json={"estagio": "visita"})
    assert r.status_code == 200
    r = cliente.get(f"/api/admin/leads/{lid}", headers=h)
    assert r.json()["temperatura"] == "quente"


def test_estagio_invalido(cliente):
    h = _login(cliente)
    r = cliente.post("/api/admin/leads", headers=h,
                     json={"nome": "x", "telefone": "43933333333"})
    lid = r.json()["id"]
    r = cliente.patch(f"/api/admin/leads/{lid}", headers=h, json={"estagio": "banana"})
    assert r.status_code == 400


def test_simulacao_publica_cria_lead_automaticamente(cliente):
    # endpoint publico -> hook
    r = cliente.post("/api/simular-financiamento", json={
        "valor_imovel": 500000, "entrada": 100000, "prazo_meses": 360,
        "taxa_anual": 0.1149, "sistema": "SAC",
        "renda_mensal": 15000,
        "nome": "Cliente Teste", "contato": "43944445555",
    })
    assert r.status_code == 200, r.text
    h = _login(cliente)
    r = cliente.get("/api/admin/leads?origem=simulador", headers=h)
    leads = r.json()["leads"]
    assert len(leads) == 1
    assert leads[0]["nome"] == "Cliente Teste"
    # comprometimento ok deve ter classificado quente
    assert leads[0]["temperatura"] == "quente"


def test_avaliacao_publica_cria_lead_vendedor(cliente):
    r = cliente.post("/api/avaliar-imovel", json={
        "bairro": "candeias", "area_util": 120, "quartos": 3,
        "suites": 1, "vagas": 2, "padrao": "medio", "estado": "bom", "idade": "0_10",
        "nome": "Vendedor Teste", "contato": "43955556666",
    })
    assert r.status_code == 200, r.text
    h = _login(cliente)
    r = cliente.get("/api/admin/leads?origem=avaliacao", headers=h)
    leads = r.json()["leads"]
    assert len(leads) == 1
    assert "vendedor" in cliente.get(f"/api/admin/leads/{leads[0]['id']}", headers=h).json()["tags"]


def test_adicionar_nota(cliente):
    h = _login(cliente)
    r = cliente.post("/api/admin/leads", headers=h,
                     json={"nome": "x", "telefone": "43966667777"})
    lid = r.json()["id"]
    r = cliente.post(f"/api/admin/leads/{lid}/notas", headers=h,
                     json={"descricao": "ligacao feita, vai pensar"})
    assert r.status_code == 201
    detalhe = cliente.get(f"/api/admin/leads/{lid}", headers=h).json()
    assert any(i["tipo"] == "nota" for i in detalhe["interacoes"])


def test_operacao_ia_metricas_exige_token(cliente):
    r = cliente.get("/api/admin/operacao-ia/metricas")
    assert r.status_code == 401


def test_operacao_ia_metricas_e_conversas_retorna_estrutura(cliente):
    h = _login(cliente)

    # Gera uma conversa para popular o painel
    r = cliente.post("/api/chat", json={"message": "oi"})
    assert r.status_code == 200
    conversa_id = r.json()["conversation_id"]

    r = cliente.get("/api/admin/operacao-ia/metricas", headers=h)
    assert r.status_code == 200
    body = r.json()
    for k in ("total_execucoes", "sucesso_percentual", "fallback_percentual", "latencia_media_ms", "por_modelo", "por_agente"):
        assert k in body

    r = cliente.get("/api/admin/operacao-ia/conversas", headers=h)
    assert r.status_code == 200
    lista = r.json()
    assert "items" in lista
    assert "total" in lista
    assert lista["total"] >= 1

    r = cliente.get(f"/api/admin/operacao-ia/conversas/{conversa_id}", headers=h)
    assert r.status_code == 200
    detalhe = r.json()
    assert "conversa" in detalhe
    assert "mensagens" in detalhe
    assert "execucoes" in detalhe
    assert "eventos" in detalhe


def test_copilot_lead_retorna_resumo_e_proxima_acao(cliente):
    """C.3: heuristica local de co-pilot do lead."""
    h = _login(cliente)
    # cria lead via avaliacao publica
    r = cliente.post(
        "/api/avaliar-imovel",
        json={
            "bairro": "Candeias",
            "area_util": 120,
            "quartos": 3,
            "nome": "Maria",
            "contato": "77988887777",
        },
    )
    assert r.status_code == 200
    # encontra o lead criado
    leads = cliente.get("/api/admin/leads", headers=h).json()["leads"]
    assert leads
    lead_id = leads[0]["id"]

    r = cliente.get(f"/api/admin/leads/{lead_id}/copilot", headers=h)
    assert r.status_code == 200
    body = r.json()
    for k in ("resumo", "proxima_acao", "perguntas_sugeridas", "objecoes_detectadas", "perfil"):
        assert k in body
    assert isinstance(body["perguntas_sugeridas"], list)
    assert isinstance(body["objecoes_detectadas"], list)


def test_copilot_lead_404_quando_nao_existe(cliente):
    h = _login(cliente)
    r = cliente.get("/api/admin/leads/99999/copilot", headers=h)
    assert r.status_code == 404


def test_alerta_busca_cria_e_lista(cliente):
    """C.4: visitante salva filtro, admin lista."""
    h = _login(cliente)
    r = cliente.post(
        "/api/alerta-busca",
        json={
            "nome": "Ana",
            "contato": "ana@example.com",
            "filtros": {"bairro": "Boa Vista", "tipo": "apartamento", "faixa": "500 a 1mi"},
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["alerta_id"] > 0
    assert body["lead_id"] > 0

    r = cliente.get("/api/admin/alertas", headers=h)
    assert r.status_code == 200
    alertas = r.json()["alertas"]
    assert len(alertas) >= 1
    assert alertas[0]["nome"] == "Ana"
    assert alertas[0]["filtros"]["bairro"] == "Boa Vista"


def test_alerta_busca_rejeita_filtros_vazios(cliente):
    r = cliente.post(
        "/api/alerta-busca",
        json={"nome": "Joao", "contato": "77999999999", "filtros": {}},
    )
    assert r.status_code == 400


def test_alerta_desativar(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/alerta-busca",
        json={"nome": "Bia", "contato": "bia@x.com", "filtros": {"bairro": "Recreio"}},
    )
    alerta_id = r.json()["alerta_id"]
    r = cliente.delete(f"/api/admin/alertas/{alerta_id}", headers=h)
    assert r.status_code == 200
    # nao aparece mais na listagem (so as ativas)
    alertas = cliente.get("/api/admin/alertas", headers=h).json()["alertas"]
    assert all(a["id"] != alerta_id for a in alertas)

