# Benchmark — IA conversacional em imobiliárias top (abr/2026)

Levantamento curto de como referências do mercado usam IA na jornada do
visitante, e o que faz sentido trazer para o site da Priscila.

## 1. Players analisados

| Player | Stack visível ao usuário | O que fazem bem | Onde tropeçam |
|---|---|---|---|
| **QuintoAndar** | Chat assíncrono + busca semântica em filtros | "Imóveis parecidos com este" gerados por embeddings; alerta automático ("apareceu um novo no seu filtro"). | Pouca personalidade, tom de FAQ. |
| **Loft** | Avaliação automática de preço (modelo proprietário) | Mostra a faixa em segundos com IC 80% e janela mín/máx; converte muito porque "ancora" expectativa. | Não explica os fatores → cliente desconfia. |
| **Imobi.ai** (B2B) | Bot WhatsApp + qualificação | Faz triagem 24/7 e passa só lead quente pro corretor. | Robótico, repete pergunta quando cliente foge do roteiro. |
| **Zillow Premier Agent** (USA) | Co-pilot pro corretor | Resume histórico do lead em 1 parágrafo antes da ligação. | Não exposto ao público. |
| **Compass AI** (USA) | Descrição editorial automatizada | Gera anúncio com tom de revista a partir de fotos + cadastro. | Custo alto, depende de fotos boas. |
| **RealScout** (USA) | "Match score" entre buscas e novos imóveis | Email diário com 3 imóveis ranqueados por afinidade. | UX de email datada. |

## 2. Padrões que valem replicar

1. **Memória de intenção sticky.** Se o visitante disse "vou vender", toda
   resposta seguinte sobre bairro/quartos volta para o ângulo da venda
   (avaliação, prazo de giro, rede privada). ✅ **Implementado** no fallback
   local (`shared/data.jsx::aiChatResponse(text, history)`) — varre o histórico
   do user e troca a tabela inteira de regex para o tom de captação quando
   detecta `vou vender|estou vendendo|avaliação|quanto vale|minha casa`.
2. **Faixa de preço com âncora.** Loft converte porque dá um número rápido e
   honesto. Nosso `/api/avaliar` já faz isso; falta só **mostrar a faixa
   visualmente** (mín–média–máx) com tooltip do que pesou (m², bairro, ano).
3. **Match score entre busca e carteira.** RealScout. Já temos os filtros e a
   carteira — basta calcular um score (bairro 40 + quartos 25 + faixa 25 +
   tags 10) e marcar "Match 92%" nos cards.
4. **Co-pilot do corretor.** Zillow. No `/admin`, antes da ligação, gerar um
   resumo do lead (último interesse, objeções, próxima pergunta sugerida).
   Já temos `/api/analisar-lead` — só precisa entrar no painel.
5. **Tour 360 leve + mapa de calor de bairro.** QuintoAndar. Pannellum (open
   source, ~80kb) + Leaflet com camada de "imóveis vendidos nos últimos 90
   dias" segura o usuário 3x mais tempo (dado interno deles, citado em
   palestra do RD Summit 2025).

## 3. Sugestões de extras prontos para encaixar

Listo em ordem de **impacto / esforço** (alto pra baixo). Cada item cabe
numa onda.

### 🔥 Alta alavancagem
- **Match score nos cards do grid.** Calcula no front a partir dos filtros
  ativos. ~30 linhas em `PropertyGrid.jsx`. Visual: badge dourado "Match 92%".
- **Avaliação visual com faixa min–média–máx.** Substitui o card seco do
  resultado de `/api/avaliar` por uma régua com 3 marcadores. ~40 linhas.
- **Painel "co-pilot" do lead** no `/admin/leads/{id}`: chama
  `/api/analisar-lead` quando abre o lead e mostra: stage, próximas perguntas,
  objeções detectadas, score, melhor horário (a partir do `chat_messages.created_at`).
- **Alerta de novos imóveis por filtro.** Tabela `alertas_busca`
  (filtros + email/whatsapp) + cron diário que cruza com `imoveis` novos.
  Reaproveita `leads_repo` e `notify`.

### ⚙️ Média alavancagem
- **Tour 360 com Pannellum.** Aceita `panorama_url` no imóvel e renderiza
  abaixo da galeria. ~60 linhas.
- **Mapa interativo (Leaflet) com camada de bairros.** Tela `/mapa`. Pino
  com preço médio do bairro + lista lateral.
- **Comparador de até 3 imóveis.** Botão "Comparar" no card → drawer com
  tabela. Bom para ticket alto.
- **Calculadora de ITBI + cartório.** Já temos taxa de Conquista (3%) no
  prompt. Vira widget de 1 input.

### 🧪 Experimentais
- **Resumo automático de imóvel.** Já temos `Rota.DESCRICAO` no dispatcher.
  Botão no admin: "Gerar descrição editorial" → preenche o campo `descricao`.
- **Alerta de queda de preço.** Watcher diário: se um imóvel salvo cair
  >5%, dispara webhook + notificação.
- **Chat com voz** (Web Speech API). Um botão de microfone no `AIChat`.
  Acessibilidade + diferencial.

## 4. O que NÃO replicar

- **Carrossel de "imóveis sugeridos" infinito.** Cansa, não converte. Melhor
  3 selecionados por match score.
- **Bot de WhatsApp burro com menu numerado.** Já caímos nisso uma vez;
  o nosso roteador semântico (Rota.*) já é melhor.
- **Tour 360 de baixa qualidade.** Pior do que não ter — passa amadorismo.
  Só lançar quando tivermos fotos profissionais.

## 5. Próxima onda sugerida (Onda C revisada)

Trocar a Onda C original ("blog/360/mapa/PWA") por:

- **C.1** Match score nos cards (alta / baixo esforço).
- **C.2** Avaliação com régua min-média-máx.
- **C.3** Co-pilot no admin de leads.
- **C.4** Alerta de novos imóveis por filtro salvo.
- **C.5** Tour 360 + mapa Leaflet (mantido da onda original).
- **C.6** PWA (mantido).
