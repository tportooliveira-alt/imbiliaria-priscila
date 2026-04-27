"""Persistencia operacional do chat: conversas, execucoes de IA e eventos."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_chat_persiste_conversa_execucao_e_eventos(tmp_path, monkeypatch) -> None:
    import app.db as db

    monkeypatch.setattr(db, "DB_PATH", Path(tmp_path) / "chat.db")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    db.init_db()

    from server import app

    with TestClient(app) as client:
        r1 = client.post("/api/chat", json={"message": "oi"})
        assert r1.status_code == 200
        body1 = r1.json()
        assert body1["session_id"]
        assert body1["conversation_id"]

        r2 = client.post(
            "/api/chat",
            json={
                "message": "meu whatsapp e 77999998888",
                "history": [
                    {"role": "user", "content": "oi"},
                    {"role": "assistant", "content": body1["resposta"]},
                ],
                "session_id": body1["session_id"],
            },
        )
        assert r2.status_code == 200
        body2 = r2.json()
        assert body2["session_id"] == body1["session_id"]
        assert body2["conversation_id"] == body1["conversation_id"]

    with db.db_session() as conn:
        conversa = conn.execute("SELECT * FROM conversas").fetchone()
        assert conversa is not None
        assert conversa["sessao_id"] == body1["session_id"]
        assert conversa["ultimo_stage"]

        mensagens = conn.execute("SELECT papel, conteudo FROM mensagens_conversa ORDER BY id").fetchall()
        assert len(mensagens) >= 4
        assert any(m["papel"] == "user" and "77999998888" in m["conteudo"] for m in mensagens)

        execucoes = conn.execute("SELECT agente, modelo FROM execucoes_ia ORDER BY id").fetchall()
        assert len(execucoes) == 2
        assert all(row["agente"] == "chat" for row in execucoes)

        eventos = conn.execute("SELECT nome FROM eventos_funil ORDER BY id").fetchall()
        nomes = [row["nome"] for row in eventos]
        assert "chat.iniciado" in nomes
        assert "chat.resposta_gerada" in nomes
        assert "lead.recebido" in nomes


def test_funnel_agora_usa_conversas_persistidas(tmp_path, monkeypatch) -> None:
    import app.db as db

    monkeypatch.setattr(db, "DB_PATH", Path(tmp_path) / "funnel.db")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    db.init_db()

    from server import app

    with TestClient(app) as client:
        client.post("/api/chat", json={"message": "quero comprar em Candeias"})
        r = client.get("/api/funnel")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert sum(body["stages"].values()) == 1