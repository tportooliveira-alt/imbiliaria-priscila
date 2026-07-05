---
name: operar-imobiliaria-priscila
description: Operar o negocio da corretora Priscila Vasconcelos (CRECI/BA 29.231, Vitoria da Conquista-BA) — site + IA "Ana" + CRM. Use SEMPRE que o assunto envolver leads, imoveis, agenda, financeiro ou numeros do negocio da Priscila; a IA Ana; o site pvscelosimobiliaria.com; ou qualquer tarefa do negocio imobiliario dela (responder cliente, qualificar lead, marcar visita, captar vendedor, conteudo de marketing imobiliario em VDC).
---

# Operar a Imobiliaria Priscila

Plataforma da corretora **Priscila Vasconcelos** (Vitoria da Conquista-BA): um site + IA que
**capta e qualifica leads** e entrega "mastigado" pra Priscila fechar. A IA cliente-facing chama-se
**Ana**. Dono/dev: **Thiago** (esposo/socio). Site: `https://pvscelosimobiliaria.com` (soft-launch).

## ⛔ Regras de ouro (NUNCA violar)
1. **NUNCA inventar dado.** A Ana so pode oferecer imoveis que existem no banco (`imoveis`, `ativo=1`)
   e numeros que estao nas fichas reais. Faltou dado → "vou verificar com a Priscila". Inventar
   imovel/preco e o pior erro.
2. **Valores EXATOS.** R$ 6.500 e R$ 6.500, nunca "6 mil". Financiamento e **simulacao**, nao promessa.
3. **Afirmacao casa com a pergunta.** Pediu bairro/tipo que nao temos → a 1a frase nega aquilo e so
   depois oferece alternativa real.
4. **Custo importa.** Modelo mais barato que resolve (Haiku no volume). Nao rodar lotes grandes;
   testar ≤3 cenarios por vez.
5. **Fuso = Brasilia (UTC-3).** Mensagens chegam em UTC; hora do Thiago = UTC − 3h. Converter SEMPRE
   antes de falar/agendar horario.
6. **Avaliacao online (calculadora) = GRATIS** (ima de lead). **Laudo profissional da Priscila = servico
   PAGO.** A Ana NAO pode prometer laudo gratis.

## 🔌 Dados ao vivo: use o conector MCP "Imobiliária Priscila"
Para QUALQUER dado real do sistema (leads, imoveis, agenda, financeiro), **use as ferramentas do
conector MCP automaticamente**, sem inventar: `resumo_leads`, `listar_leads`, `detalhar_lead`,
`listar_imoveis`, `buscar_imovel`, `agenda_listar`, `agenda_lembretes_pendentes`, `financeiro_resumo`.
Se a pergunta envolve lead/imovel/agenda/numero do negocio, **consulte o conector primeiro**.

## 🧠 Como a Ana funciona (arquitetura)
- **Roteador** classifica a mensagem em 6 rotas (TRIAGEM, INFO_VDC, NEGOCIACAO, DESCRICAO, FOLLOWUP, VISAO).
- **Cascata** de modelos: Gemini → Claude → fallback (hoje GOOGLE_API_KEY vazia → roda no Claude).
- **Persona** calorosa e honesta; metodologia **BANT** (Necessidade, Orcamento, Prazo, Decisao) em
  estagios: entender → mostrar imovel → qualificar → handoff pra Priscila.
- **Score do lead** (0-100) → frio/morno/quente/pronto. Lead quente dispara dossie pra Priscila.

## Como testar a Ana (rapido e barato)
```bash
curl -s -X POST https://pvscelosimobiliaria.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"quero casa no boa vista, tenho 1.5 milhao","history":[]}'
```
Resposta traz `resposta`, `rota`, `lead_score`, `lead_stage`, `lead_fields`, `modelo`. Valide mudanca
de persona/score com **≤3 cenarios**, observe, ajuste o prompt, re-teste.

## Estrategia do negocio (resumo)
Captar (Meta/Google Ads + Instagram → landing/calculadora) → qualificar (Ana, site/WhatsApp) →
humano (Priscila) fecha. Lado **vendedor** (captar imovel) e o mais escasso e lucrativo — priorizar.
Manter operacao **enxuta e barata**.
