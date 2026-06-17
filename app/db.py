"""SQLite local — usuarios, imoveis, imagens.

Banco fica em `data/site.db`. Conexão é por requisição (FastAPI dependency).
Migrations são idempotentes: rodam sempre no startup.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("SITE_DB_PATH", ROOT / "data" / "site.db"))


SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS imoveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    titulo TEXT NOT NULL,
    bairro TEXT NOT NULL,
    tipo TEXT NOT NULL,
    quartos INTEGER DEFAULT 0,
    suites INTEGER DEFAULT 0,
    vagas INTEGER DEFAULT 0,
    area_util REAL DEFAULT 0,
    preco REAL NOT NULL,
    descricao TEXT,
    caracteristicas TEXT DEFAULT '[]',
    destaque INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS imagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imovel_id INTEGER NOT NULL,
    arquivo TEXT NOT NULL,
    legenda TEXT DEFAULT '',
    ordem INTEGER DEFAULT 0,
    tipo TEXT DEFAULT 'sala',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (imovel_id) REFERENCES imoveis(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_imagens_imovel ON imagens(imovel_id);
CREATE INDEX IF NOT EXISTS idx_imoveis_bairro ON imoveis(bairro);
CREATE INDEX IF NOT EXISTS idx_imoveis_ativo ON imoveis(ativo);

CREATE TABLE IF NOT EXISTS login_attempts (
    ip TEXT NOT NULL,
    quando TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_login_ip ON login_attempts(ip, quando);

CREATE TABLE IF NOT EXISTS simulacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor_imovel REAL NOT NULL,
    entrada REAL NOT NULL,
    prazo_meses INTEGER NOT NULL,
    taxa_anual REAL NOT NULL,
    sistema TEXT NOT NULL,
    parcela_inicial REAL NOT NULL,
    total_pago REAL NOT NULL,
    renda_minima REAL NOT NULL,
    nome TEXT,
    contato TEXT,
    bairro TEXT,
    tipo_imovel TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bairro TEXT NOT NULL,
    area_util REAL NOT NULL,
    quartos INTEGER DEFAULT 0,
    suites INTEGER DEFAULT 0,
    vagas INTEGER DEFAULT 0,
    padrao TEXT,
    estado TEXT,
    idade TEXT,
    valor_central REAL NOT NULL,
    valor_minimo REAL NOT NULL,
    valor_maximo REAL NOT NULL,
    confianca TEXT,
    nome TEXT,
    contato TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────
-- CRM / Leads
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT,
    email TEXT,
    origem TEXT NOT NULL DEFAULT 'site',     -- site | simulador | avaliacao | chat | whatsapp | manual
    estagio TEXT NOT NULL DEFAULT 'novo',     -- novo | contatado | qualificado | visita | proposta | fechado | perdido
    temperatura TEXT NOT NULL DEFAULT 'frio', -- quente | morno | frio
    score INTEGER NOT NULL DEFAULT 0,         -- 0-100
    observacoes TEXT DEFAULT '',
    responsavel_id INTEGER,                   -- usuario admin responsavel
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_leads_estagio ON leads(estagio);
CREATE INDEX IF NOT EXISTS idx_leads_temperatura ON leads(temperatura);
CREATE INDEX IF NOT EXISTS idx_leads_telefone ON leads(telefone);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);

CREATE TABLE IF NOT EXISTS lead_interacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,                       -- simulacao | avaliacao | chat | visita | nota | email | whatsapp
    descricao TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',                -- json com detalhes (valor_simulado, etc)
    referencia_id INTEGER,                    -- id da simulacao/avaliacao/conversa relacionada
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_interacoes_lead ON lead_interacoes(lead_id);

CREATE TABLE IF NOT EXISTS lead_tags (
    lead_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (lead_id, tag),
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id TEXT NOT NULL UNIQUE,
    canal TEXT NOT NULL DEFAULT 'site',
    lead_id INTEGER,
    status TEXT NOT NULL DEFAULT 'aberta',
    rota_atual TEXT,
    ultimo_score INTEGER,
    ultimo_stage TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_conversas_sessao ON conversas(sessao_id);
CREATE INDEX IF NOT EXISTS idx_conversas_lead ON conversas(lead_id);
CREATE INDEX IF NOT EXISTS idx_conversas_stage ON conversas(ultimo_stage);

CREATE TABLE IF NOT EXISTS mensagens_conversa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversa_id INTEGER NOT NULL,
    papel TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    chave_mensagem TEXT UNIQUE,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversa_id) REFERENCES conversas(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_mensagens_conversa ON mensagens_conversa(conversa_id, criado_em);

CREATE TABLE IF NOT EXISTS execucoes_ia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversa_id INTEGER,
    lead_id INTEGER,
    agente TEXT NOT NULL,
    evento TEXT,
    provedor TEXT NOT NULL,
    modelo TEXT NOT NULL,
    fallback INTEGER NOT NULL DEFAULT 0,
    sucesso INTEGER NOT NULL DEFAULT 1,
    duracao_ms INTEGER,
    metadata TEXT DEFAULT '{}',
    erro TEXT,
    chave_idempotencia TEXT UNIQUE,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversa_id) REFERENCES conversas(id) ON DELETE SET NULL,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_execucoes_ia_conversa ON execucoes_ia(conversa_id, criado_em);
CREATE INDEX IF NOT EXISTS idx_execucoes_ia_agente ON execucoes_ia(agente, criado_em);

CREATE TABLE IF NOT EXISTS eventos_funil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    origem TEXT NOT NULL DEFAULT 'site',
    lead_id INTEGER,
    conversa_id INTEGER,
    payload TEXT DEFAULT '{}',
    idempotency_key TEXT UNIQUE,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL,
    FOREIGN KEY (conversa_id) REFERENCES conversas(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_eventos_funil_nome ON eventos_funil(nome, criado_em);
CREATE INDEX IF NOT EXISTS idx_eventos_funil_lead ON eventos_funil(lead_id, criado_em);

CREATE TABLE IF NOT EXISTS alertas_busca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    nome TEXT,
    contato TEXT NOT NULL,
    filtros TEXT NOT NULL DEFAULT '{}',
    ativa INTEGER NOT NULL DEFAULT 1,
    notificacoes_enviadas INTEGER NOT NULL DEFAULT 0,
    ultima_notificacao TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_alertas_busca_ativa ON alertas_busca(ativa, criado_em);

-- ─────────────────────────────────────────────────────────────────────────
-- Agenda (W4) — visitas, reunioes, follow-ups
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agenda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    inicio TEXT NOT NULL,                     -- ISO8601 (UTC)
    fim TEXT NOT NULL,                        -- ISO8601 (UTC)
    tipo TEXT NOT NULL DEFAULT 'visita',      -- visita | reuniao | captacao | followup | bloqueio
    status TEXT NOT NULL DEFAULT 'agendado',  -- agendado | confirmado | cancelado | realizado
    lead_id INTEGER,
    imovel_id INTEGER,
    observacoes TEXT DEFAULT '',
    lembrete_enviado INTEGER NOT NULL DEFAULT 0,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL,
    FOREIGN KEY (imovel_id) REFERENCES imoveis(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_agenda_inicio ON agenda(inicio);
CREATE INDEX IF NOT EXISTS idx_agenda_status ON agenda(status, inicio);

-- ─────────────────────────────────────────────────────────────────────────
-- Documentos (W5) — RG, comprovante, contracheque, contrato etc.
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    imovel_id INTEGER,
    tipo TEXT NOT NULL DEFAULT 'outro',       -- rg | cpf | comprovante_renda | comprovante_residencia | contrato | proposta | outro
    nome_original TEXT NOT NULL,
    caminho TEXT NOT NULL,                    -- caminho relativo no disco
    mime TEXT,
    tamanho_bytes INTEGER NOT NULL DEFAULT 0,
    observacoes TEXT DEFAULT '',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (imovel_id) REFERENCES imoveis(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_documentos_lead ON documentos(lead_id, criado_em);
CREATE INDEX IF NOT EXISTS idx_documentos_imovel ON documentos(imovel_id);

-- Consentimentos LGPD (rastro de aceite explicito)
CREATE TABLE IF NOT EXISTS consentimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    email TEXT,
    telefone TEXT,
    tipo TEXT NOT NULL DEFAULT 'contato',     -- contato | marketing | cookies | termos
    aceito INTEGER NOT NULL DEFAULT 1,
    ip TEXT,
    user_agent TEXT,
    texto_versao TEXT DEFAULT 'v1',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_consentimentos_lead ON consentimentos(lead_id, criado_em);
CREATE INDEX IF NOT EXISTS idx_consentimentos_email ON consentimentos(email);

-- ============================================================
-- W7 — Financeiro (comissoes, metas, contas)
-- ============================================================
CREATE TABLE IF NOT EXISTS comissoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    imovel_id INTEGER,
    corretor_email TEXT,
    descricao TEXT NOT NULL,
    valor_venda REAL NOT NULL,
    percentual REAL NOT NULL DEFAULT 0,
    valor_comissao REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'previsto',  -- previsto | recebido | cancelado
    data_venda TEXT NOT NULL,
    data_recebimento TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL,
    FOREIGN KEY (imovel_id) REFERENCES imoveis(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_comissoes_status ON comissoes(status, data_venda);
CREATE INDEX IF NOT EXISTS idx_comissoes_corretor ON comissoes(corretor_email);

CREATE TABLE IF NOT EXISTS metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    corretor_email TEXT,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    meta_vendas REAL NOT NULL DEFAULT 0,
    meta_comissao REAL NOT NULL DEFAULT 0,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(corretor_email, ano, mes)
);
CREATE INDEX IF NOT EXISTS idx_metas_periodo ON metas(ano, mes);

CREATE TABLE IF NOT EXISTS contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,                        -- pagar | receber
    descricao TEXT NOT NULL,
    categoria TEXT DEFAULT 'geral',
    valor REAL NOT NULL,
    vencimento TEXT NOT NULL,
    pago INTEGER NOT NULL DEFAULT 0,
    data_pagamento TEXT,
    observacoes TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_contas_vencimento ON contas(vencimento, pago);
CREATE INDEX IF NOT EXISTS idx_contas_tipo ON contas(tipo, pago);

CREATE TABLE IF NOT EXISTS depoimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,                        -- nome do cliente real (consentido)
    texto TEXT NOT NULL,
    estrelas INTEGER NOT NULL DEFAULT 5,       -- 1..5
    contexto TEXT,                             -- ex.: "Compra em Candeias", "Venda Boa Vista"
    foto_url TEXT,
    ativo INTEGER NOT NULL DEFAULT 1,
    ordem INTEGER NOT NULL DEFAULT 0,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_depoimentos_ativo ON depoimentos(ativo, ordem);

-- Empreendimentos (lançamentos de construtora): entidade PAI com tipologias filhas
CREATE TABLE IF NOT EXISTS empreendimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    construtora TEXT DEFAULT '',
    bairro TEXT DEFAULT '',
    descricao TEXT DEFAULT '',
    video_url TEXT,                            -- link YouTube/Vimeo (sem carga no servidor)
    status_obra TEXT DEFAULT 'na_planta',      -- na_planta | em_obras | pronto
    entrega_prevista TEXT DEFAULT '',          -- ex.: "Dez/2027"
    destaque INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS empreendimento_tipologias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empreendimento_id INTEGER NOT NULL,
    nome TEXT NOT NULL,                         -- "Apartamento Tipo 1", "Cobertura"...
    area_util REAL DEFAULT 0,
    quartos INTEGER DEFAULT 0,
    suites INTEGER DEFAULT 0,
    vagas INTEGER DEFAULT 0,
    preco_a_partir REAL DEFAULT 0,             -- exibido como "A partir de R$"
    ordem INTEGER DEFAULT 0,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empreendimento_id) REFERENCES empreendimentos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS empreendimento_imagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empreendimento_id INTEGER NOT NULL,
    arquivo TEXT NOT NULL,
    legenda TEXT DEFAULT '',
    ordem INTEGER DEFAULT 0,
    tipo TEXT DEFAULT 'sala',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empreendimento_id) REFERENCES empreendimentos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_emp_tipologias ON empreendimento_tipologias(empreendimento_id);
CREATE INDEX IF NOT EXISTS idx_emp_imagens ON empreendimento_imagens(empreendimento_id);
CREATE INDEX IF NOT EXISTS idx_empreendimentos_ativo ON empreendimentos(ativo);
"""


def conectar() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # WAL + busy_timeout: escritas concorrentes (2 workers + threads) nao dao
    # "database is locked" — esperam ate 5s em vez de falhar. (estudo arquitetura #1)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db() -> None:
    """Cria tabelas se não existirem. Seguro chamar várias vezes."""
    with conectar() as conn:
        conn.executescript(SCHEMA)
        # Migracoes idempotentes (ALTER TABLE so se coluna nao existir)
        _migrar_coluna(conn, "simulacoes", "bairro", "TEXT")
        _migrar_coluna(conn, "simulacoes", "tipo_imovel", "TEXT")
        # W6: tour 360 por imovel
        _migrar_coluna(conn, "imoveis", "tour_360_url", "TEXT")
        # Ponte Google Calendar: id do evento espelhado no Google (NULL = nao espelhado)
        _migrar_coluna(conn, "agenda", "gcal_event_id", "TEXT")
        # Empreendimentos: ficha tecnica rica (condominio/obra grande)
        for _col, _tipo in (
            ("endereco", "TEXT"), ("area_total", "TEXT"),
            ("num_torres", "INTEGER"), ("num_unidades", "INTEGER"), ("num_andares", "INTEGER"),
            ("vagas_info", "TEXT"), ("data_lancamento", "TEXT"), ("tour_360_url", "TEXT"),
            ("lazer", "TEXT"), ("diferenciais", "TEXT"),
            ("proximidades", "TEXT"), ("condicoes_pagamento", "TEXT"),
        ):
            _migrar_coluna(conn, "empreendimentos", _col, _tipo)
        conn.commit()


def _migrar_coluna(conn: sqlite3.Connection, tabela: str, coluna: str, tipo: str) -> None:
    cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({tabela})")]
    if coluna not in cols:
        conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")


@contextmanager
def db_session():
    conn = conectar()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
