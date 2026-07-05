"""Preflight seguro da configuracao Meta/Instagram.

Uso:
    python scripts/verificar_instagram_meta.py
    python scripts/verificar_instagram_meta.py --media-url https://site/arquivo.mp4

O comando nunca imprime token, app secret ou qualquer segredo.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - ambiente minimo
    load_dotenv = None

from app import instagram  # noqa: E402


def _carregar_env(no_env: bool) -> None:
    if no_env or load_dotenv is None:
        return
    load_dotenv(ROOT / ".env")


def _preflight(media_urls: list[str]) -> dict[str, Any]:
    status = instagram.status_config()
    midias = [
        {"url": url, "ok": instagram.validar_url_midia_publica(url)}
        for url in media_urls
    ]
    status["midias"] = midias
    status["preflight_ok"] = (
        status["disponivel"]
        and status["graph_version_configurada"]
        and all(item["ok"] for item in midias)
    )
    return status


def _texto(status: dict[str, Any]) -> str:
    linhas = ["Instagram/Meta - preflight seguro"]
    linhas.append(f"Conexao minima: {'OK' if status['disponivel'] else 'PENDENTE'}")
    linhas.append(
        f"Graph version: {status['graph_version']} "
        f"({'configurada' if status['graph_version_configurada'] else 'fallback local'})"
    )
    faltando = ", ".join(status["faltando"]) if status["faltando"] else "nenhum"
    linhas.append(f"Faltando: {faltando}")
    if status["avisos"]:
        linhas.append("Avisos:")
        linhas.extend(f"- {aviso}" for aviso in status["avisos"])
    linhas.append(
        "Publicacao MCP: "
        + ("habilitada" if status["mcp_publicacao_habilitada"] else "desligada")
    )
    if status["midias"]:
        linhas.append("Midias:")
        for item in status["midias"]:
            linhas.append(f"- {item['url']}: {'OK' if item['ok'] else 'REJEITADA'}")
    linhas.append(f"Resultado: {'PRONTO' if status['preflight_ok'] else 'PENDENTE'}")
    return "\n".join(linhas)


def _badge(valor: bool, ok: str = "OK", pendente: str = "Pendente") -> str:
    classe = "ok" if valor else "pendente"
    texto = ok if valor else pendente
    return f'<span class="badge {classe}">{html.escape(texto)}</span>'


def _html_relatorio(status: dict[str, Any], logo_src: str) -> str:
    faltando = status["faltando"] or ["nenhum"]
    avisos = status["avisos"] or ["nenhum"]
    midias = status["midias"] or []
    midias_html = "\n".join(
        f"""
        <tr>
          <td>{html.escape(item["url"])}</td>
          <td>{_badge(bool(item["ok"]))}</td>
        </tr>
        """
        for item in midias
    ) or '<tr><td>Nenhuma midia informada</td><td><span class="badge neutro">Aguardando</span></td></tr>'

    faltando_html = "\n".join(f"<li>{html.escape(item)}</li>" for item in faltando)
    avisos_html = "\n".join(f"<li>{html.escape(item)}</li>" for item in avisos)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Preflight Instagram Meta - Priscila Vasconcelos</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy:#16284B;
      --navy-2:#0f1c38;
      --gold:#c9943a;
      --ink:#172033;
      --muted:#667085;
      --line:#e3e8f1;
      --soft:#f7f9fc;
      --off:#F5F1E9;
      --ok:#0f7a4f;
      --warn:#a36312;
      --bad:#b42318;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0;
      background:#fff;
      color:var(--ink);
      font-family:Inter,system-ui,sans-serif;
      line-height:1.5;
    }}
    .top {{
      background:linear-gradient(135deg,var(--navy),var(--navy-2));
      color:#fff;
      padding:28px clamp(18px,4vw,52px);
      border-bottom:4px solid var(--gold);
    }}
    .brand {{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:18px;
      max-width:1180px;
      margin:0 auto 28px;
    }}
    .brand img {{ width:min(230px,48vw); height:auto; display:block; }}
    .app-id {{
      color:rgba(255,255,255,.74);
      font-size:.9rem;
      font-weight:600;
      text-align:right;
    }}
    .hero {{
      max-width:1180px;
      margin:0 auto;
      display:grid;
      grid-template-columns:minmax(0,1.35fr) minmax(280px,.65fr);
      gap:28px;
      align-items:end;
    }}
    h1 {{
      font-family:"Playfair Display",Georgia,serif;
      font-size:clamp(2rem,4vw,4.4rem);
      line-height:1.02;
      margin:0;
      letter-spacing:0;
    }}
    .sub {{
      max-width:720px;
      margin:16px 0 0;
      color:rgba(255,255,255,.82);
      font-size:1rem;
    }}
    .result {{
      border:1px solid rgba(255,255,255,.22);
      background:rgba(255,255,255,.08);
      padding:18px;
      border-radius:8px;
    }}
    .result strong {{
      display:block;
      font-size:2rem;
      line-height:1;
      margin-top:7px;
      color:{'#bff0d5' if status['preflight_ok'] else '#ffd7a3'};
    }}
    main {{
      max-width:1180px;
      margin:0 auto;
      padding:28px clamp(18px,4vw,52px) 48px;
    }}
    .grid {{
      display:grid;
      grid-template-columns:repeat(4,minmax(0,1fr));
      gap:12px;
      margin-bottom:26px;
    }}
    .metric {{
      min-height:118px;
      border:1px solid var(--line);
      border-radius:8px;
      padding:16px;
      background:#fff;
    }}
    .metric span {{
      display:block;
      color:var(--muted);
      font-size:.82rem;
      font-weight:700;
      text-transform:uppercase;
      letter-spacing:.06em;
    }}
    .metric strong {{
      display:block;
      margin-top:12px;
      font-size:1.45rem;
      color:var(--navy);
    }}
    .ops {{
      border:1px solid var(--line);
      background:linear-gradient(180deg,#fff,#fbfcfe);
      border-radius:8px;
      padding:18px;
      margin:0 0 26px;
      display:grid;
      grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);
      gap:22px;
    }}
    .ops h2 {{
      margin:0 0 8px;
    }}
    .ops p {{
      color:var(--muted);
      margin:0;
    }}
    .campaign {{
      display:grid;
      gap:10px;
      align-content:start;
    }}
    .campaign-row {{
      display:grid;
      grid-template-columns:112px minmax(0,1fr);
      gap:12px;
      padding:10px 0;
      border-bottom:1px solid var(--line);
    }}
    .campaign-row:last-child {{ border-bottom:0; }}
    .campaign-row span {{
      color:var(--muted);
      font-size:.78rem;
      font-weight:800;
      text-transform:uppercase;
      letter-spacing:.06em;
    }}
    .campaign-row strong {{
      color:var(--navy);
      font-size:.95rem;
    }}
    .band {{
      border-top:1px solid var(--line);
      padding:26px 0;
      display:grid;
      grid-template-columns:minmax(220px,.42fr) minmax(0,.58fr);
      gap:28px;
    }}
    h2 {{
      font-family:"Playfair Display",Georgia,serif;
      color:var(--navy);
      font-size:1.8rem;
      margin:0;
      letter-spacing:0;
    }}
    .panel {{
      border:1px solid var(--line);
      border-radius:8px;
      background:var(--soft);
      padding:18px;
    }}
    .list {{
      margin:0;
      padding-left:19px;
    }}
    .list li {{ margin:6px 0; }}
    .badge {{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      min-width:88px;
      min-height:30px;
      padding:5px 10px;
      border-radius:999px;
      font-size:.82rem;
      font-weight:800;
      border:1px solid transparent;
    }}
    .badge.ok {{ color:var(--ok); background:#e8f7ef; border-color:#bfe8d0; }}
    .badge.pendente {{ color:var(--warn); background:#fff4e5; border-color:#f3d19b; }}
    .badge.neutro {{ color:var(--muted); background:#fff; border-color:var(--line); }}
    table {{
      width:100%;
      border-collapse:collapse;
      overflow:hidden;
      background:#fff;
      border:1px solid var(--line);
      border-radius:8px;
    }}
    th,td {{
      padding:12px 14px;
      border-bottom:1px solid var(--line);
      text-align:left;
      vertical-align:top;
      overflow-wrap:anywhere;
    }}
    th {{
      font-size:.78rem;
      text-transform:uppercase;
      letter-spacing:.06em;
      color:var(--muted);
      background:#fbfcfe;
    }}
    tr:last-child td {{ border-bottom:0; }}
    code {{
      display:block;
      background:var(--navy);
      color:#fff;
      border-radius:8px;
      padding:14px;
      overflow:auto;
      font-size:.9rem;
      line-height:1.6;
    }}
    .step-list {{
      display:grid;
      gap:10px;
    }}
    .step {{
      display:grid;
      grid-template-columns:38px minmax(0,1fr);
      gap:12px;
      align-items:start;
      padding:12px;
      border:1px solid var(--line);
      border-radius:8px;
      background:#fff;
    }}
    .num {{
      width:32px;
      height:32px;
      border-radius:50%;
      display:inline-flex;
      align-items:center;
      justify-content:center;
      background:var(--navy);
      color:#fff;
      font-weight:800;
    }}
    .step strong {{
      display:block;
      color:var(--navy);
      margin-bottom:2px;
    }}
    .step span {{
      color:var(--muted);
      font-size:.92rem;
    }}
    .guard-grid {{
      display:grid;
      grid-template-columns:repeat(2,minmax(0,1fr));
      gap:10px;
    }}
    .guard {{
      background:#fff;
      border:1px solid var(--line);
      border-left:4px solid var(--gold);
      border-radius:8px;
      padding:12px;
      min-height:82px;
    }}
    .guard strong {{
      display:block;
      color:var(--navy);
      margin-bottom:5px;
    }}
    .guard span {{
      color:var(--muted);
      font-size:.9rem;
    }}
    .foot {{
      color:var(--muted);
      font-size:.88rem;
      border-top:1px solid var(--line);
      padding-top:18px;
    }}
    @media (max-width:900px) {{
      .hero,.band,.ops {{ grid-template-columns:1fr; }}
      .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
      .guard-grid {{ grid-template-columns:1fr; }}
      .app-id {{ text-align:left; }}
      .brand {{ align-items:flex-start; flex-direction:column; }}
    }}
    @media (max-width:560px) {{
      .grid {{ grid-template-columns:1fr; }}
      th,td {{ display:block; width:100%; }}
      th {{ border-bottom:0; }}
    }}
  </style>
</head>
<body>
  <header class="top">
    <div class="brand">
      <img src="{html.escape(logo_src)}" alt="Priscila Vasconcelos Imoveis"/>
      <div class="app-id">Priscila Social API<br/>App ID 2485154298661482</div>
    </div>
    <section class="hero">
      <div>
        <h1>Preflight Instagram e Meta</h1>
        <p class="sub">Operacao de leitura, publicacao organica e preparo de campanha para a Priscila Vasconcelos Imoveis.</p>
      </div>
      <div class="result">
        Status geral
        <strong>{'Pronto' if status['preflight_ok'] else 'Pendente'}</strong>
      </div>
    </section>
  </header>
  <main>
    <section class="grid" aria-label="Resumo">
      <div class="metric"><span>Conexao minima</span><strong>{'OK' if status['disponivel'] else 'Pendente'}</strong></div>
      <div class="metric"><span>Graph version</span><strong>{html.escape(status['graph_version'])}</strong></div>
      <div class="metric"><span>Publicacao MCP</span><strong>{'Ligada' if status['mcp_publicacao_habilitada'] else 'Desligada'}</strong></div>
      <div class="metric"><span>Midia publica</span><strong>{'OK' if midias and all(item['ok'] for item in midias) else 'Aguardando'}</strong></div>
    </section>

    <section class="ops" aria-label="Operacao foco">
      <div>
        <h2>Operação Multiplace</h2>
        <p>Pré-voo para publicar o Reels do ponto comercial com leitura segura, revisão humana e zero exposição de credenciais.</p>
      </div>
      <div class="campaign">
        <div class="campaign-row"><span>Peça</span><strong>Reels vertical - Ponto Comercial Multiplace</strong></div>
        <div class="campaign-row"><span>Canal</span><strong>Instagram orgânico primeiro; tráfego pago apenas depois da conferência de metragem.</strong></div>
        <div class="campaign-row"><span>CTA</span><strong>Agendar visita com a Priscila.</strong></div>
        <div class="campaign-row"><span>Regra</span><strong>Qualquer publicação externa exige confirmação humana.</strong></div>
      </div>
    </section>

    <section class="band">
      <h2>Credenciais</h2>
      <div class="panel">
        <table>
          <tr><th>Campo</th><th>Status</th></tr>
          <tr><td>META_PAGE_TOKEN</td><td>{_badge(bool(status['credenciais']['META_PAGE_TOKEN']))}</td></tr>
          <tr><td>IG_BUSINESS_ACCOUNT_ID</td><td>{_badge(bool(status['credenciais']['IG_BUSINESS_ACCOUNT_ID']))}</td></tr>
          <tr><td>META_GRAPH_VERSION</td><td>{_badge(bool(status['graph_version_configurada']), 'Configurada', 'Fallback')}</td></tr>
        </table>
      </div>
    </section>

    <section class="band">
      <h2>Pendencias</h2>
      <div class="panel">
        <ul class="list">{faltando_html}</ul>
      </div>
    </section>

    <section class="band">
      <h2>Avisos</h2>
      <div class="panel">
        <ul class="list">{avisos_html}</ul>
      </div>
    </section>

    <section class="band">
      <h2>Midias</h2>
      <div class="panel">
        <table>
          <tr><th>URL</th><th>Status</th></tr>
          {midias_html}
        </table>
      </div>
    </section>

    <section class="band">
      <h2>Sequência segura</h2>
      <div class="step-list">
        <div class="step"><div class="num">1</div><div><strong>Configurar Graph API do Instagram</strong><span>No app Meta `Priscila Social API`, sem arquivar o app duplicado ainda.</span></div></div>
        <div class="step"><div class="num">2</div><div><strong>Salvar token e IDs no ambiente seguro</strong><span>Nunca em Markdown, chat, git ou print público.</span></div></div>
        <div class="step"><div class="num">3</div><div><strong>Rodar este pré-voo</strong><span>Validar credenciais mínimas, versão Graph e URL pública da mídia.</span></div></div>
        <div class="step"><div class="num">4</div><div><strong>Publicar só com aprovação</strong><span>Reels, carrossel, anúncio ou verba continuam bloqueados sem confirmação humana.</span></div></div>
      </div>
    </section>

    <section class="band">
      <h2>Proteções ativas</h2>
      <div class="guard-grid">
        <div class="guard"><strong>Sem segredos</strong><span>O painel exibe apenas status booleano e nomes de campos faltantes.</span></div>
        <div class="guard"><strong>Publicação desligada</strong><span>`MCP_IG_PUBLISH_ENABLED=0` é o padrão seguro.</span></div>
        <div class="guard"><strong>Mídia pública</strong><span>URLs locais, `.local` e IPs privados são rejeitados antes da Graph API.</span></div>
        <div class="guard"><strong>Campanha imobiliária</strong><span>Se virar anúncio, nasce `PAUSED` e com categoria especial `HOUSING`.</span></div>
      </div>
    </section>

    <section class="band">
      <h2>Comando seguro</h2>
      <div>
        <code>python scripts\\verificar_instagram_meta.py --media-url https://pvscelosimobiliaria.com/ig-media/reels-multiplace-em-construcao.mp4 --html _marketing_ia\\relatorios\\meta-instagram-preflight.html --allow-pending</code>
      </div>
    </section>

    <p class="foot">Relatorio local sem segredos. Publicacao, anuncio, verba e mensagens externas continuam dependentes de confirmacao humana.</p>
  </main>
</body>
</html>
"""


def _escrever_html(status: dict[str, Any], output: str) -> Path:
    destino = (ROOT / output).resolve() if not Path(output).is_absolute() else Path(output)
    destino.parent.mkdir(parents=True, exist_ok=True)
    logo = ROOT / "assets" / "marketing" / "logo-mono-offwhite.png"
    logo_src = os.path.relpath(logo, destino.parent).replace("\\", "/")
    destino.write_text(_html_relatorio(status, logo_src), encoding="utf-8")
    return destino


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifica configuracao Meta/Instagram sem expor segredos."
    )
    parser.add_argument(
        "--media-url",
        action="append",
        default=[],
        help="URL publica HTTPS de midia que a Meta precisa conseguir buscar.",
    )
    parser.add_argument("--json", action="store_true", help="Imprime JSON seguro.")
    parser.add_argument("--html", help="Salva relatorio HTML seguro no caminho informado.")
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="Retorna sucesso mesmo com pendencias, util para gerar relatorio visual.",
    )
    parser.add_argument("--no-env", action="store_true", help="Nao carrega .env.")
    args = parser.parse_args(argv)

    _carregar_env(args.no_env)
    status = _preflight(args.media_url)

    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.html:
        destino = _escrever_html(status, args.html)
        print(f"Relatorio salvo em {destino}")
    else:
        print(_texto(status))
    return 0 if (status["preflight_ok"] or args.allow_pending) else 2


if __name__ == "__main__":
    raise SystemExit(main())
