# 🧠 CENTRO — Marca, Persona e Marketing da Priscila (ler SEMPRE antes de divulgação)

Este é o "cérebro" pra QUALQUER trabalho de divulgação/marketing/design da imobiliária. O cowork
(e qualquer IA) deve ler isto antes de gerar conteúdo, pra entender quem é a Priscila e falar na voz
certa. Cresce com o tempo — adicione aqui o que for aprendendo sobre a marca.

## 👤 Quem é a Priscila
- **Priscila Vasconcelos** — corretora de imóveis, **CRECI/BA 29.231**, em **Vitória da Conquista (Bahia)**.
- Conhece VDC de cabeça (bairros, escolas, comércio, perfil). Atendimento humano, próximo, honesto.
- Dono/dev/sócio: **Thiago** (esposo). A **Ana** é a assistente virtual (1º contato), NUNCA se passa pela Priscila.
- Princípio da marca: **"people buy from people"** — a PESSOA (a corretora, o rosto, a logo) vem na frente;
  a tecnologia/IA é discreta. Imóvel-primeiro.

## 🎨 Identidade visual (usar em TUDO: site, redes, carrossel, impresso)
- **Cores:** navy `#16284B` (principal) + `#5C7CB8` (apoio) + **dourado** `#c9943a` (só no CTA/destaque).
- **Fontes:** Playfair Display (títulos) + Inter (texto).
- **Logo** no rodapé; **foto da Priscila** na capa quando for marca/educação.
- Tom: elegante, confiável, caloroso — nada de "agência fria" nem IA chamando atenção.

## 📣 Marketing — o que já existe (USE, não refaça)
- **10 carrosséis prontos** (copy + estrutura): `docs/CARROSSEIS-INSTAGRAM.md`. Abrir o perfil com o
  #1 ("vale seu imóvel") e #10 ("conheça a Priscila").
- **Plano de Instagram:** `docs/CAMPANHA-INSTAGRAM-PRISCILA.md` (pilares: guia de bairros, "quanto vale seu
  imóvel", dicas, bastidores, depoimentos).
- **Campanha Meta paga:** `docs/CAMPANHA-META-1.md`. Calculadora de investimento: página `/ads`.
- **Meta Pixel** (já medindo no site): `27844979038460971` (público, não é segredo). GA4 ainda vazio.
- **Postar:** Postiz (`docs/POSTIZ-SETUP.md`) — onde o login do Instagram/Facebook fica pra publicar.
- **Keywords por imóvel:** `docs/ADS-KEYWORDS-POR-IMOVEL.md`.

## 🔌 Como o cowork trabalha divulgação (fluxo)
1. **Dados reais** → sempre do MCP (`panorama_geral`, `listar_imoveis`, `imovel_fotos`, `buscar_imovel`).
   NUNCA invente preço, bairro, m² — pegue do sistema.
2. **Gera o conteúdo** (carrossel/arte/legenda) no PC do Thiago, com as ferramentas instaladas lá,
   seguindo a identidade visual acima.
3. **Regra de ouro do conteúdo:** nada inventado. Onde precisa de número real de VDC e não tem, marca
   `[PREENCHER]` — a Priscila/Thiago completam. Sem dado real, NÃO publica o slide.
4. Legenda termina com CTA + "salva/compartilha" + hashtags. Sempre assina com CRECI/BA 29.231.

## ⚠️ Pendências de marca (Thiago preenche)
- **@ do Instagram da Priscila:** `[PREENCHER]` — colocar o handle real aqui.
- **GA4 ID:** vazio — quando o Thiago pegar, ligar (igual o Pixel).
- **Depoimentos reais** (≥3-5): `docs/PEDIR-DEPOIMENTOS.md`.

## 📚 Aprofundar
- Persona completa da Ana: `app/prompts.py` (`PRISCILA_PERSONA`).
- Estado geral do sistema: `docs/HANDOFF-<data>.md` (o mais recente) + skill `contexto-imobiliaria`.
- Método de pesquisa profunda (quando precisar estudar um tema a fundo): `/deep-research`.
