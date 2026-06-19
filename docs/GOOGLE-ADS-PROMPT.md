# 🎯 Google Ads — prompt pronto + estudo de negativas (Priscila Vasconcelos)

Base: `docs/ADS-KEYWORDS-POR-IMOVEL.md`, `docs/PESQUISA-LEADS-2026.md`, `docs/GOOGLE-ADS-SETUP.md`.
Conta: Vitória da Conquista/BA. Site no ar: **pvscelosimobiliaria.com**. GA4: **G-RDZY8DPY32**
(conversão `generate_lead` já dispara nos 3 formulários do site).

## Lógica das negativas (por que cada bloco corta dinheiro à toa)
1. **Outras cidades** → segmentação por raio vaza em buscas como "apto Salvador". Corta gente de fora.
2. **Emprego/curso/CRECI** → quem quer *trabalhar* com imóvel, não comprar. Lixo puro.
3. **Grátis/info/planta baixa/PDF** → pesquisa escolar/curiosidade, nunca compra.
4. **Aluguel/temporada/Airbnb** → foco da campanha é **VENDA + CAPTAÇÃO** (comissão alta). Aluguel é
   baixo valor; cortamos pra não gastar. *(Se a Priscila quiser anúncio de aluguel, faz campanha à parte.)*
5. **Leilão/Caixa/MCMV/financiamento Caixa** → outro público (super sensível a preço, processo diferente).
6. **Reforma/construção/decoração/móveis** → serviços, não compra de imóvel.
7. **Portais concorrentes (OLX, ZAP, Viva Real, QuintoAndar)** → quem busca a plataforma, não a corretora.

## Estrutura (2 campanhas — separa porque o público e a página de destino são diferentes)
- **Campanha A — COMPRADOR** → leva pra home/catálogo. Otimiza `generate_lead`.
- **Campanha B — VENDEDOR/CAPTAÇÃO** → leva pra /anunciar (avaliação). Lead mais valioso.

Começar com **orçamento pequeno**, **lance = Maximizar cliques com teto de CPC** (sem histórico de
conversão ainda), e só depois de ~15–30 conversões trocar pra **Maximizar conversões**.

---

## 📋 PROMPT PRA COLAR NO CLAUDE DO CHROME (ele opera o Google Ads)

> Você está logado no Google Ads da imobiliária **Priscila Vasconcelos** (Vitória da Conquista/BA).
> O site é **pvscelosimobiliaria.com** e o GA4 (ID **G-RDZY8DPY32**) já está instalado, com o evento de
> conversão **`generate_lead`**. NÃO ative gasto sem eu confirmar — apenas deixe tudo configurado e PAUSADO.
>
> **1) Conversão:** Em Ferramentas → Conversões, importe do GA4 o evento **`generate_lead`** e marque como
> **conversão principal**. Se ainda não aparecer, crie o vínculo GA4 ↔ Google Ads primeiro.
>
> **2) Segmentação de local (CRÍTICO p/ não gastar à toa):** Vitória da Conquista/BA + raio de **35 km**.
> Em "Opções de local", escolha **"Presença: pessoas que estão na sua região"** (NÃO use "Presença ou
> interesse"). Como o local já prende a campanha na cidade, NÃO precisa repetir "Vitória da Conquista"
> nas palavras-chave. Idioma: Português.
>
> **3) Campanha A — "PVSCELOS | Comprador" (Rede de Pesquisa):** destino **https://pvscelosimobiliaria.com**.
> Lance: **Maximizar cliques** com **CPC máximo de R$ 2,50**. Palavras-chave SOLTAS, em **correspondência de
> frase** (curtas — o geo já limita à cidade):
> "comprar casa", "comprar apartamento", "casa à venda", "apartamento à venda", "imóveis à venda",
> "imobiliária", "corretor de imóveis", "comprar imóvel", "apartamento 3 quartos", "casa com quintal",
> "apartamento Candeias", "casa no Recreio", "imóveis Boa Vista".
> + 1 palavra em **correspondência exata** (marca): [Priscila Vasconcelos imóveis].
>
> **4) Campanha B — "PVSCELOS | Vendedor" (Rede de Pesquisa):** destino **https://pvscelosimobiliaria.com/?p=anunciar**
> (ou a home, se a rota não abrir direto). Lance: **Maximizar cliques**, **CPC máx R$ 3,00**. Frase (soltas):
> "quanto vale meu imóvel", "avaliar imóvel", "avaliação de imóvel grátis", "vender imóvel", "vender casa",
> "vender apartamento", "anunciar imóvel", "quanto vale minha casa".
>
> **5) Palavras-chave NEGATIVAS (aplique a LISTA abaixo nas DUAS campanhas):**
> aluguel, alugar, alugo, locação, locacao, temporada, airbnb, diária, pousada, hotel, hostel,
> emprego, vaga, vagas, salário, salario, concurso, estágio, estagio, trainee, curso, "creci curso", "como ser corretor", faculdade,
> grátis, gratis, "planta baixa", modelo, "como fazer", "como calcular", "passo a passo", pdf, download, significado, "o que é",
> salvador, "feira de santana", ilhéus, ilheus, itabuna, jequié, jequie, brumado, guanambi, barreiras, brasília, brasilia, "são paulo", goiânia,
> leilão, leilao, "imóveis caixa", "minha casa minha vida", "financiamento caixa", fgts, subsídio, subsidio,
> reforma, reformar, construir, construção, construcao, pedreiro, arquiteto, decoração, decoracao, móveis, moveis, marcenaria, "material de construção",
> olx, "viva real", vivareal, zap, zapimoveis, quintoandar, "quinto andar", loft, imovelweb, "chaves na mão"
>
> **6) Anúncios (RSA — 1 por campanha).** Títulos (use vários):
> Comprador → "Imóveis em Vitória da Conquista", "Casa e Apto à Venda em VDC", "Corretora Priscila Vasconcelos",
> "Atendimento Humano e Direto", "Veja Fotos e Agende a Visita", "Do Simples ao Alto Padrão".
> Vendedor → "Quanto Vale Seu Imóvel?", "Avaliação Gratuita do Imóvel", "Venda com a Priscila Vasconcelos",
> "Anuncie Sem Dor de Cabeça", "Visita Técnica e Fotos Profissionais".
> Descrições → "Imóvel é confiança. E confiança tem nome. Fale com a Priscila e encontre o lar certo em Vitória da Conquista.",
> "Avaliação gratuita, fotos profissionais e atendimento humano de verdade. Agende sua visita.".
>
> **7) DEIXE TUDO PAUSADO** e me mostre um resumo (campanhas, orçamento sugerido/dia, conversão vinculada).
> Eu confirmo o orçamento e ativo. Não gaste nada sem meu "ok".

---

## 🔎 Achados verificados do deep-research (parei na síntese, mas peguei o essencial)
- **Geo:** pra negócio local, usar **"Presença"** (quem está na cidade), NÃO "Presença ou interesse" —
  o "interesse" pega gente de fora e gasta à toa. *(fonte: doc oficial Google + prática de locais)* → aplicado.
- **Lance:** "Maximizar conversões desde o dia 1" (que circula em blog de imobiliária) é **furado pra conta
  nova sem histórico**. O certo: **Maximizar cliques com teto de CPC** primeiro, migrar depois. → aplicado.
- **Estrutura:** Rede de Pesquisa com grupos separados por categoria (residencial / lançamento / comercial). → bate com nossas 2 campanhas.
- **Negativas (blog Tecimob, 2025):** emprego, doação, aluguel temporada, "fotos de", decoração — lista
  fina; a nossa já é mais completa (corta CRECI/curso, leilão, outras cidades, portais concorrentes).

## 🪜 Escada de orçamento (subir devagar, conforme o site/sistema vão sendo ajustados)
Filosofia: verba pequena → medir → ajustar o funil → só então escalar. **Nunca pôr dinheiro num funil furado.**

- **Degrau 1 (semana 1–2) — R$ 15/dia por campanha** (~R$ 30/dia, ~R$ 900/mês).
  Objetivo: medir **CPL real** + ver na aba "Termos de pesquisa" quais buscas reais trouxeram clique →
  e **adicionar negativas** dos termos-lixo que aparecerem. Lance ainda em Maximizar cliques.
- **Ajuste do funil (entre degraus):** olhar ONDE o lead cai — formulário, resposta da Ana, retorno da
  Priscila. Consertar antes de subir verba. (É o "ajustar site e sistema".)
- **Degrau 2 — R$ 30/dia por campanha**, só se o CPL veio bom e os leads estão virando conversa real.
  Quando juntar **~15–30 conversões**, trocar lance pra **Maximizar conversões**.
- **Degrau 3 — escalar** no que funciona (a campanha/palavra que traz lead barato), pausar o que não rende.

---

# 📱 META ADS (Instagram + Facebook) — plano

Meta = descoberta (não busca). Sem palavra-chave: segmenta por **local + idade + interesses + criativo**.
O algoritmo trabalha melhor com público **amplo** + criativo bom (foto real da Priscila/imóveis).

Foco no **Instagram** (vitrine da Priscila, @priscilavasconcelosvca). Os 3 destinos que o dono quer —
**na ordem de ligar, um degrau de cada vez** (não acender as 3 juntas):

### Degrau 1 (ligar primeiro) — Instagram → **SITE** (lead cai na Ana, que já funciona)
- **Objetivo:** "Tráfego" (ou "Vendas/Leads" se o Pixel já estiver instalado) → destino site.
- **Destino:** https://pvscelosimobiliaria.com · **Posicionamento:** só **Instagram** (feed, stories, reels).
- **Local:** VDC + 35 km · **Idade:** 28–60 · **Público amplo** (Advantage+).
- **Criativo:** carrossel de fotos reais (com marca d'água) + foto da Priscila. **Orçamento:** R$ 15/dia.

### Degrau 2 (depois) — Instagram → **DIRECT (DM)**
- **Objetivo:** "Engajamento → Mensagens" → destino **Instagram Direct**.
- ⚠️ **A Ana NÃO está no Instagram** (só WhatsApp). Os Directs a **Priscila responde na mão**, ou a gente
  vê automação de IG depois (projeto à parte). Decidir antes de ligar.

### Degrau 3 (em paralelo, barato) — **Crescer o perfil @**
- **Objetivo:** "Engajamento/Seguidores" — vitrine de marca, longo prazo (não é lead direto).
- **Orçamento baixo:** R$ 5–10/dia, rodando de fundo.

### Pra otimizar por conversão no site → **precisa do Pixel da Meta**
- Instalar o Pixel no site (igual ao GA4) — preciso do **ID do Pixel** do Gerenciador da Priscila.
- Libera: otimizar por `generate_lead` + **retargeting** de quem já visitou o site.

---

## Decisões que dependem da Priscila (confirmar antes de ligar)
- **Aluguel entra como negativo?** (estudo assume que sim — foco em venda/captação). Se ela trabalha
  aluguel forte, fazemos campanha separada.
- **"Minha Casa Minha Vida"** está negativado (público sensível a preço). Se ela tem unidade econômica
  e quer esse público, a gente tira da lista.
- **Orçamento/dia** — ela decide. Sugestão pra começar e medir CPL: R$ 20–30/dia por campanha.
