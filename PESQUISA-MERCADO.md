# Estudo de mercado — Sites imobiliários de referência

> Análise comparativa feita em 26/04/2026 contra ZAP, VivaReal, QuintoAndar, Loft,
> Lopes e Coelho da Fonseca. Foco: identificar o que falta no site da Priscila
> (corretora solo em Vitória da Conquista) **sem copiar o que faz sentido só pra
> portal nacional**.

---

## 1. Estado atual do nosso site (v3-editorial)

```
HERO editorial → Busca por bairro → Grid de imóveis → Simulador financiamento
→ Manifesto → Método 4 etapas → Atlas de bairros → Entrevista Priscila
→ Avaliação imóvel → CTA WhatsApp → Footer
```

**Pontos fortes únicos** (nenhum concorrente tem):
- Tom editorial / revista (Vol. 01, §, big quote, byline)
- IA com persona de corretora real (chat híbrido Gemini+Claude)
- Simulador HONESTO (MIP+DFI+tarifa+idade) — *acabamos de implementar*
- Avaliação de imóvel heurística por bairro (m²/VDC)
- Painel admin completo (CRUD imóveis + leads + chat)

**O que já existe e funciona:**
- ✅ Busca por bairro
- ✅ Grid de imóveis com filtros
- ✅ Simulador financiamento (com seguros)
- ✅ Avaliação de imóvel
- ✅ Chat IA com captura de lead
- ✅ Lightbox de fotos
- ✅ Pipeline de imagens (4 WebPs + EXIF strip)
- ✅ Auth + CRM no admin
- ✅ Persistência de conversas

---

## 2. Padrões observados nos concorrentes

### ZAP / VivaReal (portais — 7M imóveis)
- Header: **Comprar / Alugar / Lançamento** + busca por cidade
- Cards visuais por categoria: "aceita pet", "perto do metrô", "varanda gourmet", "mobiliado"
- **Guia de bairros** com SEO (página dedicada por bairro com infos da região)
- Calculadora de **poder de compra** (não só parcela — quanto eu posso comprar com X de renda)
- Blog massivo (mercado, lugares, dicas)
- App iOS/Android
- Filtros avançados (80+ filtros no ZAP)

### QuintoAndar
- **Visita online agendada** (botão grande)
- **Tour 360º virtual**
- **Consórcio próprio** integrado
- Assessoria de financiamento integrada (parceria com bancos)
- Cashback (10%) como gancho comercial
- Pôster grande de cada bairro com infos de mobilidade/serviços
- "Indique um imóvel" (programa de indicação)

### Loft
- Cards temáticos: "tour virtual", "cozinha grande", "academia no prédio", "preço abaixo do mercado"
- Curadoria editorial ("IMÓVEIS EM DESTAQUE", "selecionados por nós")
- "Loft IA" — busca por linguagem natural ("encontre lar com varanda e academia")
- Calculadora de avaliação de imóvel (calculadora-de-precos-imoveis)

### Lopes (90 anos, alto padrão)
- **Lançamentos** em destaque (na planta, breves, lançados)
- **CrediPronto** — financiamento próprio (taxa promocional + 24h aprovação)
- Blog editorial denso (consórcio vs financiamento, ITBI explicado, comissão corretor)
- Filtros: valor, área, dormitórios, vagas + **busca por código**
- **Simulador Minha Casa Minha Vida** dedicado
- Calculadora poder de compra
- App próprio

### Coelho da Fonseca (luxo, 50 anos)
- Stepper de 7 etapas pra busca (regional → tipo → área → quartos → suítes → vagas → valor)
- Curadoria explícita: "Acabaram de chegar", "Private Selection: a poucos passos do Clube Paulistano"
- **Newsletter** ("Tenha propriedade sobre o mercado imobiliário")
- "Family business" — fotos da família dona (storytelling)
- Mídia: Forbes, Harper's Bazaar, entrevistas no YouTube
- "Anuncie seu imóvel" — formulário direto na home
- Imóveis com **código** (CF624270) + breadcrumb por região

### Padrões transversais (todos têm)
- Header: comprar/alugar/lançamento como toggle principal
- Filtros expansíveis (valor min/max, área, dormitórios, vagas)
- Cards com badge de categoria (NOVO, ABAIXO MERCADO, etc.)
- "Anuncie seu imóvel" (lead vendedor) — porta de entrada
- Simulador de financiamento (todos têm, alguns terceirizam)
- Calculadora de avaliação de imóvel (Loft, ZAP/VivaReal, QA)
- Blog/Conteúdo (SEO + autoridade)
- App mobile
- Newsletter
- Política de privacidade + LGPD + cookies

---

## 3. GAP analysis — o que falta no nosso site

### 🟥 Crítico (perda de conversão direta)

| Gap | Por quê dói | Esforço |
|-----|-------------|---------|
| **Toggle Comprar / Alugar / Lançamento** no hero | Visitante chega esperando — sem isso pensa "só vendem" | XS |
| **Botão "Anuncie seu imóvel"** visível | Lado vendedor é o lado escasso e mais lucrativo | S |
| **Agendar visita** (com calendário) | QA construiu império em cima disso | M |
| **Cards temáticos** ("varanda", "pet", "perto do centro de VDC") | Entrada lateral pra quem não sabe bairro | S |
| **Calculadora poder de compra** (renda → quanto compro) | Inverso do simulador atual; capta quem não sabe valor | S |
| **Página de bairro** com SEO (1 URL por bairro c/ infos da região) | Google manda tráfego orgânico pra essas páginas | M |
| **Código do imóvel** + busca por código | Cliente liga falando "vi o imóvel CF624270" | XS |
| **Compartilhar imóvel via WhatsApp** (botão no card/lightbox) | Multiplicador orgânico | XS |

### 🟧 Importante (autoridade + retenção)

| Gap | Por quê | Esforço |
|-----|---------|---------|
| **Blog editorial** (5-10 posts iniciais) | SEO + autoridade + alimenta IA com contexto local | M |
| **Newsletter** (lead frio que vira morno) | Lista própria > qualquer Instagram | S |
| **Tour virtual / 360º** em pelo menos 1 imóvel destaque | QA fez disso commodity | M |
| **Lançamentos** (seção separada de pronto/usado) | Lopes e Coelho dedicam home inteira a isso | S |
| **Comparador** (selecionar 3 imóveis e ver lado a lado) | Não tem nenhum site brasileiro fazendo bem ainda | M |
| **Página de imóvel individual** com URL própria (`/imovel/{slug}`) | Hoje o site é SPA — não dá pra compartilhar link de 1 imóvel | M |
| **Mapa interativo** dos imóveis | "Quero perto da praça da Cultura" é 1 frase comum em VDC | M |
| **App PWA** (instalável no celular) | Sem custo de loja, push notification de novos imóveis | M |

### 🟨 Estratégico (Priscila como marca)

| Gap | Por quê | Esforço |
|-----|---------|---------|
| **Depoimentos reais** (foto + nome + bairro + texto + estrelas) | Hoje só tem stat "4,9 estrelas" — sem quem disse | S |
| **Mídia** (se houver entrevistas, prêmios CRECI) | Coelho usa muito; cria autoridade | XS |
| **Indicação** (programa "indique e ganhe") | QA: principal canal orgânico deles | M |
| **Página /sobre** detalhada (história da Priscila, anos, fechamentos) | Hoje é só uma "entrevista" curta no meio do home | S |
| **Casos de sucesso** ("Vendi em 22 dias — caso Maria, Candeias") | Diferencia de portal frio | M |

### 🟩 Conformidade / técnico

| Gap | Por quê | Esforço |
|-----|---------|---------|
| **Política de privacidade** | LGPD obrigatório | XS |
| **Cookie banner** | LGPD se usar analytics | XS |
| **Sitemap.xml + robots.txt** | SEO básico, hoje faltando | XS |
| **OG tags + Schema.org RealEstateListing** | Compartilhamento social bonito + Google entende imóveis | S |
| **Headers de segurança completos** (CSP) | Plano já lista, falta CSP | S |
| **Rotas com URL** (hoje SPA `/#contato`) | `/imoveis`, `/bairro/candeias`, `/imovel/{slug}` | M |

### 🟦 Não vale a pena copiar (pra solo VDC)

- App nativo iOS/Android (PWA resolve)
- 80+ filtros (5-6 boas é suficiente)
- Crédito próprio tipo CrediPronto (parceria com correspondente local resolve)
- Consórcio próprio (idem)
- Marketplace de corretores associados
- Newsletter diária (semanal/quinzenal basta)

---

## 4. Plano priorizado de execução

### Onda A — *Já dá pra mexer essa semana* (quick wins)

1. **Toggle Comprar / Alugar / Lançamento** no hero (mesmo que catálogo só tenha "venda" hoje, marca a posição).
2. **Cards temáticos** abaixo do grid: "Aceita pet", "Pra primeira casa (até 500 mil)", "Alto padrão (acima 1M)", "Perto do centro", "Casa com quintal" — cada um filtra o grid já existente.
3. **Botão "Anuncie seu imóvel"** no header, abre modal com formulário curto (nome + telefone + endereço + foto opcional) → cria lead vendedor no CRM.
4. **Compartilhar via WhatsApp** em cada card e no lightbox (1 botão, abre wa.me com link e título).
5. **Código do imóvel** visível no card (`PV-001`, `PV-042`) — formato `PV-` + ID.
6. **Política de privacidade + cookie banner** LGPD básico.

### Onda B — *Próximo sprint* (estrutura)

7. **Página por imóvel** `/imovel/{slug}` com URL real (não só `#`).
8. **Página por bairro** `/bairro/{slug}` com infos de VDC, ticket médio, imóveis ativos.
9. **Calculadora poder de compra**: "Tenho R$ 5.000 de renda — quanto consigo comprar?" (inverso do simulador, reaproveita 90% do código).
10. **Agendar visita** (slot da agenda da Priscila + Google Calendar) — já está no plano-mestre admin.
11. **Sitemap.xml + Schema.org RealEstateListing** + OG tags por imóvel.
12. **Depoimentos reais** com foto/nome/bairro (3-5 iniciais que a Priscila tem).

### Onda C — *Maturação* (autoridade)

13. **Blog editorial** com 5 posts iniciais escritos pela IA + revisados pela Priscila:
    - "Como funciona o financiamento da Caixa em VDC?"
    - "Os 3 erros que ninguém te conta antes de comprar em Candeias"
    - "Quanto custa o m² em cada bairro de VDC (2026)"
    - "ITBI em VDC: 3% que pegam o cliente de surpresa"
    - "Pro-Cotista FGTS: como conseguir 9,49% a.a."
14. **Tour virtual / 360º** em 1 imóvel destaque (Matterport ou parecido).
15. **Mapa interativo** com pinos dos imóveis (Leaflet + OSM, gratuito).
16. **PWA** instalável + manifest + service worker básico.
17. **Newsletter** quinzenal automatizada (1 imóvel novo + 1 dica de mercado).

### Onda D — *Já é fase de tração* (escala)

18. **Comparador** lado a lado (3 imóveis).
19. **Programa de indicação** ("Indique um amigo, ganhe R$ X").
20. **Lançamentos** seção própria se a Priscila pegar incorporadora local.
21. **Casos de sucesso** com foto antes/depois + tempo de venda.

---

## 5. Recomendação de execução *agora*

**Ordem sugerida pra próxima sessão (1 commit cada):**

1. Toggle Comprar/Alugar no hero + Cards temáticos (Onda A 1 e 2) — frontend puro, ~1h
2. Botão "Anuncie seu imóvel" + endpoint de lead vendedor (Onda A 3) — full-stack, ~2h
3. Compartilhar WhatsApp + Código PV-XXX (Onda A 4 e 5) — frontend puro, ~30min
4. LGPD: política + banner + headers CSP (Onda A 6) — ~1h
5. Página por imóvel `/imovel/{slug}` + Schema.org (Onda B 7 e 11) — ~3h, transforma SPA em multi-página

Depois: agenda + bairro + blog (já é Onda B/C, sprint maior).

---

## 6. Diferencial editorial — não perder o tom

Concorrentes nacionais são **frios e funcionais**. Nossa edge:

- **Vol. 01 / § / Edição Permanente** — manter sempre
- **Big quote / manifesto** — manter
- **Atlas de bairros** com perfil escrito — manter e expandir (cada bairro = 1 página com texto real, não tabela)
- **Entrevista da corretora** — manter, expandir pra 5-7 perguntas
- **IA como assistente da corretora** (não como substituta) — esse posicionamento é único

O risco de copiar Loft/QA é virar "mais um portal frio". A Priscila ganha sendo
**a corretora local com IA editorial**, não competindo em volume com ZAP.
