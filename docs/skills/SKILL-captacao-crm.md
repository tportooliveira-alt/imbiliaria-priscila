# 💰 SKILL — Captação / CRM

## O que faz
Capta **vendedores/locadores** (quem quer anunciar) e gerencia os leads, a agenda e o financeiro da Priscila.

## Onde está o código
- **Captação (público):** `app/routes_publicas.py`
  - `POST /api/lead-vendedor` — formulário "Anuncie seu imóvel" → cria lead com origem `vendedor`.
  - `POST /api/avaliar-imovel` — se vier nome/contato, também vira lead `vendedor` (tag) com a faixa avaliada.
  - `POST /api/agendar-visita` — pedido de visita.
  - Front: `anunciar.html` (avaliação + captura) e a faixa "Quer vender?" na home.
- **CRM/gestão (admin):** `app/routes_crm.py`
  - Leads: `/leads` (listar/criar/editar), notas, tags, **copiloto** (`/leads/{id}/copilot/sugerir-resposta`), enviar WhatsApp.
  - Agenda: `/agenda` (criar/listar/editar) + `/agenda/lembretes/enviar`.
  - Financeiro: `/financeiro/comissoes`, `/metas`, `/contas` (a pagar/receber + pagar), `/dashboard`.
  - Alertas: `/alertas` + `/alertas/matches` (casa lead ↔ imóvel).
- **Ponte lead quente → dossiê** (Paperclip): `app/paperclip_bridge.py` (`escalar_se_quente`) — monta dossiê
  com a conversa + simulação de financiamento quando o lead esquenta.

## Materiais de captação prontos
- Links curtos: **/anunciar** e **/avaliar** (redirects em server.py).
- QR Code: `assets/qr-anunciar.png` (aponta pra /anunciar).

## Como testar
```bash
curl -s -X POST https://pvscelosimobiliaria.com/api/lead-vendedor -H "Content-Type: application/json" \
  -d '{"nome":"Teste","telefone":"77999999999","tipo":"Casa","bairro":"Candeias"}'
```

## Erros comuns
- **Lead não aparece no CRM** → conferir se o POST retornou 200/201; ver tabela `leads`/`lead_interacoes` no `data/site.db`.
- **Dossiê não escala** → `escalar_se_quente` só roda se temperatura = "quente" e ainda não escalado.
- **WhatsApp não envia** → Evolution API (gateway) precisa estar `open`; ver SKILL/infra do WhatsApp.
