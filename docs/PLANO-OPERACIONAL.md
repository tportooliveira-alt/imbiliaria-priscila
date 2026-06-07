# Plano Operacional — Sistema Multiagente Imobiliário (Vitória da Conquista)

> Data-base: 03/06/2026. Documento canônico da operação. Todos os agentes (site + Paperclip) seguem este plano.
> Objetivo: transformar pesquisa, campanhas e atendimento em uma operação diária simples, mensurável e escalável.

## 1. Arquitetura mínima (ordem)
1. Planilha/CRM — base única de leads, imóveis, proprietários e campanhas.
2. WhatsApp Business — etiquetas, respostas rápidas, histórico.
3. Meta Ads — geração de demanda e remarketing.
4. Google Ads — captura de intenção ativa.
5. Agentes de IA — pesquisa, captação, tráfego, SDR, recomendação, copy, análise.
6. Corretor humano (Priscila) — visita, negociação, documentação, fechamento.

## 2. Bases centrais (mínimo 4)
- **Leads**: id_lead, nome, telefone, origem, campanha, objetivo (comprar/alugar/vender/investir), status, score, bairro_interesse, tipo_imovel, faixa_valor, renda_familiar, entrada, fgts, prazo, garantia_aluguel, observacoes, proxima_acao, responsavel, data_criacao, ultima_interacao.
- **Imóveis**: id_imovel, tipo, bairro, rua/ref, valor, condominio, iptu, metragem, quartos, suites, banheiros, vagas, aceita_financiamento, documentacao, ocupado, fotos_ok, proprietario, comissao, exclusividade, status (captar/aprovado/ajustar_preco/pausar/vendido/alugado), observacoes.
- **Proprietários**: id, nome, telefone, bairro_imovel, valor_desejado, urgencia, flexibilidade_preco, aceita_exclusividade, documentacao_regular, proxima_acao.
- **Campanhas**: id, canal (Meta/Google/Orgânico/Indicação), objetivo, persona, bairro/produto, verba, leads, leads_respondidos, leads_qualificados, visitas_marcadas, visitas_realizadas, propostas, fechamentos, custo, receita, status.

## 3. Status de lead
novo · contato_feito · qualificado_quente · qualificado_morno · nutricao · visita_marcada · visita_realizada · proposta · fechado · perdido · descartado.
Regras: responder lead novo em até 5 min; sem resposta após 3 tentativas → nutrição; sem perfil financeiro → nutrição/campanha adequada (não é perdido); aluguel nunca no funil de compra.

## 4. Score de comprador
+3 renda compatível · +3 tem entrada/FGTS · +2 compra em ≤90 dias · +2 bairro definido · +2 aceita financiamento/simulação · +1 sabe casa/apto · +1 documentação organizada · −3 não responde · −3 sem renda · −2 sem entrada (produto que exige) · −2 bairro/ticket incompatível · −1 só pesquisando sem prazo.
Classificação: ≥8 quente · 5–7 morno · 2–4 nutrição · <2 frio/descartado.

## 5. Score de aluguel
+3 muda em ≤30 dias · +3 renda comprovada · +2 aceita garantia · +2 sabe bairro e valor máx · +1 sabe nº quartos · −3 sem garantia (quando obrigatória) · −3 renda incompatível · −2 valor muito abaixo do estoque · −1 sem prazo.
Classificação: ≥7 quente · 4–6 morno · 1–3 nutrição.

## 6. Score de imóvel para campanha
+3 preço na média do bairro · +3 aceita financiamento · +2 fotos boas · +2 bairro com demanda · +2 documentação regular · +1 condomínio competitivo · +1 diferencial claro · −3 preço >25% acima · −3 documentação problemática · −2 fotos ruins · −2 proprietário sem flexibilidade · −2 público pequeno demais.
Classificação: ≥9 pode receber tráfego pago · 6–8 orgânico + teste pequeno · 3–5 ajustar antes · <3 não priorizar.

## 7. Roteamento dos agentes
- **Lead novo de compra**: SDR qualifica → Recomendador sugere → Corretor valida/envia → se quente, marcar visita/simulação → Analista registra conversão.
- **Lead novo de aluguel**: SDR (bairro/valor/prazo/garantia) → Recomendador lista → Corretor agenda → sem imóvel = alerta de estoque.
- **Proprietário novo**: Captador coleta → Pesquisador compara preço → Captador negocia estratégia/preço/exclusividade → Copywriter cria anúncio → Gestor de Tráfego decide campanha.
- **Campanha com queda**: Analista identifica → Gestor de Tráfego ajusta público/negativos → Copywriter novo criativo → SDR informa qualidade real.

## 8. Funil positivo (priorizar)
Lead que responde rápido · bairro definido · renda/entrada/FGTS · aceita simulação · quer visitar em ≤7 dias · proprietário com preço realista · imóvel com documentação + financiamento · bairro com demanda · campanha que gera lead respondido (não só lead barato).

## 9. Funil negativo (negativar/separar)
Aluguel em campanha de compra (e vice-versa) · sem renda para o ticket · sem entrada para produto que exige · proprietário com preço irreal · imóvel sem documentação em campanha de financiamento · campanha com muito clique e pouca conversa · palavras informacionais (curso, emprego, decoração, planta, reforma) · público alto padrão em criativo MCMV (e vice-versa).

## 10. Rotina de 14 dias (resumo)
D1 CRM + cadastrar imóveis (MCMV/médio/aluguel/alto/comercial) · D2 etiquetas WhatsApp · D3 Captador em todos os imóveis · D4 Copywriter nos 10 melhores (3 criativos/esteira) · D5 Meta Ads pequenas (R$30 MCMV, R$30 Candeias/Boa Vista, R$20 aluguel, R$20 captação) · D6 Google Ads alta intenção · D7 medir (CPL, respondidos, qualificados, visitas, bairros) · D8 cortar criativos ruins + negativos + remarketing · D9 campanha de captação · D10 conteúdo orgânico · D11 Recomendador nos mornos (3 opções/lead) · D12 Analista de Funil · D13 ajustar landing/form/WhatsApp · D14 decidir escala.

## 11. Indicadores semanais
Leads totais · respondidos · qualificados · CPL · custo/lead respondido · custo/lead qualificado · visitas marcadas · visitas realizadas · propostas · fechamentos · bairros mais pedidos · produtos mais pedidos · motivos de perda.

## 12. Decisões de escala
Escalar: CPL aceitável + lead respondido + visita marcada; imóvel com muitas conversas qualificadas; bairro recorrente; criativo que gera conversa específica.
Pausar: muito lead sem resposta; lead fora de perfil; perguntas sobre produto inexistente; campanha de venda gerando aluguel; alto padrão gerando curiosos.

## 13. Risco operacional → antídoto
Riscos: anunciar imóvel indisponível · prometer financiamento sem simulação · misturar funis · não responder rápido · captar caro demais · lead barato e ruim · não registrar origem · não acompanhar o que virou visita.
Antídotos: CRM único · score simples · etiquetas no WhatsApp · reunião semanal de funil · fotos e dados completos antes de tráfego pago.
