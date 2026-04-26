// Shared data for all 3 variations — properties, bairros, testimonials, AI chat responses

// Bairros de Vitória da Conquista — bairros nobres + crescimento + investidor
const BAIRROS = [
  { id: "candeias",   nome: "Candeias",      emoji: "🏡", perfil: "Alto padrão · famílias · casas de luxo",                ticket: "R$ 650 mil — R$ 1,8 mi", velocidade: "Liquidez alta",          destaque: "Bairro nobre nº 1 da cidade",   imoveis: 42 },
  { id: "boavista",   nome: "Boa Vista",     emoji: "🌿", perfil: "Primeira compra · jovens casais · apartamentos",        ticket: "R$ 320 mil — R$ 780 mil", velocidade: "Liquidez média-alta",   destaque: "Crescimento acelerado",         imoveis: 38 },
  { id: "recreio",    nome: "Recreio",       emoji: "📈", perfil: "Perfil investidor · valorização constante",             ticket: "R$ 420 mil — R$ 980 mil", velocidade: "Liquidez crescente",    destaque: "Melhor custo × benefício",       imoveis: 27 },
  { id: "patagonia",  nome: "Patagônia",     emoji: "🌳", perfil: "Luxo · lotes grandes · condomínios fechados",           ticket: "R$ 1,2 mi — R$ 3,5 mi", velocidade: "Seletivo",                destaque: "Condomínios de alto padrão",    imoveis: 18 },
  { id: "centro",     nome: "Centro",        emoji: "🏛️", perfil: "Comercial · residencial misto · apartamentos clássicos", ticket: "R$ 280 mil — R$ 620 mil", velocidade: "Liquidez média",        destaque: "Coração da cidade",             imoveis: 31 },
  { id: "brasil",     nome: "Brasil",        emoji: "🌆", perfil: "Tradicional · residencial · excelente infraestrutura",   ticket: "R$ 380 mil — R$ 890 mil", velocidade: "Liquidez alta",         destaque: "Bairro consolidado",            imoveis: 24 },
  { id: "urbis",      nome: "Urbis",         emoji: "🏘️", perfil: "Popular · primeira moradia · casas e apartamentos",      ticket: "R$ 180 mil — R$ 420 mil", velocidade: "Muito rápida",          destaque: "Primeira casa",                  imoveis: 36 },
  { id: "guarani",    nome: "Guarani",       emoji: "🌅", perfil: "Emergente · valorização forte · residencial",           ticket: "R$ 250 mil — R$ 540 mil", velocidade: "Liquidez crescente",    destaque: "Próximo boom imobiliário",      imoveis: 19 },
  { id: "sivuca",     nome: "Sivuca",        emoji: "🌱", perfil: "Novo polo · investimento · condomínios",                ticket: "R$ 320 mil — R$ 680 mil", velocidade: "Liquidez crescente",    destaque: "Polo em expansão",              imoveis: 15 },
  { id: "primavera",  nome: "Primavera",     emoji: "🌺", perfil: "Residencial · famílias · casas tradicionais",            ticket: "R$ 290 mil — R$ 560 mil", velocidade: "Liquidez média",        destaque: "Tranquilo e arborizado",        imoveis: 22 },
];

// Imóveis simulados — cobrindo os 3 bairros principais + variedade de perfis
const IMOVEIS = [
  {
    id: "ca-01",
    bairro: "Candeias",
    tipo: "Casa",
    titulo: "Casa Contemporânea · Alameda das Mangabeiras",
    descricao: "Projeto arquitetônico assinado · 4 suítes · piscina com raia · home theater",
    preco: 1_480_000, precoLabel: "R$ 1,48 mi",
    quartos: 4, suites: 4, vagas: 4, area: 420,
    img: "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=1200&q=80",
    tags: ["Alto padrão", "Piscina", "4 suítes"],
    status: "Exclusivo",
    iaMatch: 94,
  },
  {
    id: "ca-02",
    bairro: "Candeias",
    tipo: "Casa",
    titulo: "Residência Clássica · Rua das Acácias",
    descricao: "Arquitetura neoclássica · 5 quartos · jardim de 380 m² · área gourmet",
    preco: 1_750_000, precoLabel: "R$ 1,75 mi",
    quartos: 5, suites: 3, vagas: 4, area: 510,
    img: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&q=80",
    tags: ["Alto padrão", "Jardim", "5 quartos"],
    status: "Novo",
    iaMatch: 88,
  },
  {
    id: "bv-01",
    bairro: "Boa Vista",
    tipo: "Apartamento",
    titulo: "Apartamento Novo · Edifício Jequitibá",
    descricao: "3 quartos (1 suíte) · 2 vagas · varanda gourmet · lazer completo",
    preco: 545_000, precoLabel: "R$ 545 mil",
    quartos: 3, suites: 1, vagas: 2, area: 118,
    img: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80",
    tags: ["Primeira compra", "Varanda", "Lazer completo"],
    status: "Lançamento",
    iaMatch: 91,
  },
  {
    id: "bv-02",
    bairro: "Boa Vista",
    tipo: "Apartamento",
    titulo: "Cobertura Duplex · Residencial Aurora",
    descricao: "Cobertura · 4 quartos · terraço de 80 m² · 2 vagas · vista panorâmica",
    preco: 780_000, precoLabel: "R$ 780 mil",
    quartos: 4, suites: 2, vagas: 2, area: 186,
    img: "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=1200&q=80",
    tags: ["Cobertura", "Terraço", "Vista"],
    status: "Pronto",
    iaMatch: 86,
  },
  {
    id: "re-01",
    bairro: "Recreio",
    tipo: "Apartamento",
    titulo: "Apartamento Investidor · Edifício Ipê",
    descricao: "2 quartos · pronto · perfil locação · retorno 0,72 %/mês",
    preco: 425_000, precoLabel: "R$ 425 mil",
    quartos: 2, suites: 1, vagas: 1, area: 72,
    img: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&q=80",
    tags: ["Investimento", "Rentável", "Pronto"],
    status: "Oportunidade",
    iaMatch: 97,
  },
  {
    id: "re-02",
    bairro: "Recreio",
    tipo: "Casa",
    titulo: "Casa Térrea · Rua Verbena",
    descricao: "3 quartos · quintal amplo · ótima para revenda · valorizou 18 % em 24 meses",
    preco: 580_000, precoLabel: "R$ 580 mil",
    quartos: 3, suites: 1, vagas: 2, area: 180,
    img: "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1200&q=80",
    tags: ["Valorização", "Quintal", "Casa térrea"],
    status: "Destaque",
    iaMatch: 82,
  },
  {
    id: "pa-01",
    bairro: "Patagônia",
    tipo: "Casa",
    titulo: "Mansão em Condomínio · Villa Toscana",
    descricao: "Terreno 1.200 m² · 6 suítes · piscina aquecida · quadra poliesportiva",
    preco: 2_950_000, precoLabel: "R$ 2,95 mi",
    quartos: 6, suites: 6, vagas: 6, area: 780,
    img: "https://images.unsplash.com/photo-1613977257363-707ba9348227?w=1200&q=80",
    tags: ["Luxo", "Condomínio", "6 suítes"],
    status: "Premium",
    iaMatch: 76,
  },
  {
    id: "pa-02",
    bairro: "Patagônia",
    tipo: "Casa",
    titulo: "Casa Térrea · Condomínio Alphaville",
    descricao: "Projeto minimalista · 4 suítes · automação completa · spa privativo",
    preco: 1_950_000, precoLabel: "R$ 1,95 mi",
    quartos: 4, suites: 4, vagas: 4, area: 520,
    img: "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=1200&q=80",
    tags: ["Minimalista", "Automação", "4 suítes"],
    status: "Exclusivo",
    iaMatch: 90,
  },
];

const DEPOIMENTOS = [
  { nome: "Ana Carla S.",  texto: "Encontrei meu apartamento em Candeias em menos de uma semana. Atendimento incrível, todo automatizado mas muito humanizado!", estrelas: 5, bairro: "Candeias", ano: 2026 },
  { nome: "Roberto M.",    texto: "Vendi minha casa no Recreio pelo preço que queria. A Priscila e a IA dela fizeram tudo direitinho, sem complicação.", estrelas: 5, bairro: "Recreio", ano: 2025 },
  { nome: "Juliana P.",    texto: "Primeira compra da minha vida! Recebi orientação em cada etapa, até às 22 h. Recomendo demais.", estrelas: 5, bairro: "Boa Vista", ano: 2025 },
];

const IA_CAPACIDADES = [
  { icone: "⚡", titulo: "Atendimento IA 24 / 7", detalhe: "Responde em segundos no WhatsApp e no site. Nenhum lead fica sem atenção — nem às 23 h." },
  { icone: "🎯", titulo: "Match inteligente de imóvel", detalhe: "Cruza orçamento, bairro preferido, prazo e perfil para indicar as melhores opções automaticamente." },
  { icone: "🔔", titulo: "Follow-up automático",    detalhe: "Régua de contatos em 1 h, 24 h, 72 h e 7 dias. Nunca mais perde um cliente por falta de retorno." },
  { icone: "📊", titulo: "Dashboard de decisão",    detalhe: "Mostra CPL, visitas, propostas e taxa de conversão em tempo real para decisões certeiras." },
];

// Fake AI chat — canned responses matched by keyword, otherwise fallback
const IA_CHAT_INTRO = "Oi, aqui e da equipe da Priscila Vasconcelos. Me conta o que voce esta procurando hoje em Vitoria da Conquista — bairro, faixa de valor ou se voce esta vendendo. Com isso ja consigo te dar um caminho.";
const IA_CHAT_SUGESTOES = [
  "Apartamento em Candeias, ate 800 mil",
  "Casa com 3 quartos pra primeira compra",
  "Quero investir pra alugar",
  "Vou vender meu imovel, vale quanto?",
];
const IA_CHAT_RESPONSES = [
  { match: /candeias|nobre|alto padr/i,      resposta: "Candeias hoje e o bairro mais consolidado de alto padrao em Conquista — ticket medio rodando R$ 1,1 milhao, 42 imoveis ativos na nossa carteira. Pra te indicar 3 que batem com seu perfil, qual o tamanho ideal: 3, 4 ou 5 quartos?" },
  { match: /boa vista|primeira|jovem/i,      resposta: "Boa Vista e a melhor relacao para quem esta comprando o primeiro imovel. Apartamentos novos saindo de R$ 320 a 780 mil, com financiamento facilitado. Voce ja tem alguma entrada guardada ou ainda esta planejando?" },
  { match: /recreio|investimento|investir|aluga|renda/i, resposta: "Recreio esta com o melhor retorno de aluguel agora — yield medio de 0,68% ao mes, ocupacao alta por causa da Uesb. Posso te mostrar 5 opcoes com potencial de valorizacao. Qual sua faixa de investimento?" },
  { match: /vender|vendo|minha casa|avalia/i,resposta: "A Priscila avalia pessoalmente em ate 24h, gratis. Pra ja adiantar a faixa, me diz: bairro, area aproximada e quantos quartos. Costumamos fechar precos 8-12% acima da media de portal porque trabalhamos a venda em rede privada." },
  { match: /500|400|300|orçamento|orcamento/i, resposta: "Nessa faixa de R$ 300-500 mil temos 27 opcoes em Boa Vista e 12 em Recreio. Pra filtrar, o que pesa mais pra voce: bairro, metragem ou ter elevador/garagem coberta?" },
  { match: /suite|quarto/i,                  resposta: "Anotado. Quantas suites e vagas voce precisa? Cruzo com seu orcamento e ja te mando aqui as opcoes com match acima de 85%." },
  { match: /priscila|humana|corretora|falar/i, resposta: "A Priscila atende pessoalmente toda negociacao — eu cuido da triagem pra ela chegar com tudo na mao. Me passa seu WhatsApp e o melhor horario, que ela te liga ainda hoje." },
  { match: /financiamento|caixa|parcela|sbpe/i, resposta: "Caixa SBPE hoje em 11,49% a.a., Pro-Cotista FGTS em 9,49% (essa e a taxa mais barata, mas exige 3+ anos de FGTS e nao ter outro imovel financiado). Importante: a parcela do banco SEMPRE inclui MIP (seguro morte/invalidez, varia com idade), DFI (seguro do imovel) e tarifa adm — soma R$ 200-500 alem do que muito simulador mostra. No nosso simulador a gente mostra a parcela cheia, com tudo. Qual valor voce esta considerando?" },
  { match: /seguro|mip|dfi|por que.*var|varia.*pessoa/i, resposta: "Otima pergunta — financiamento varia mesmo. Tres motivos: (1) MIP (seguro do banco) e cobrado sobre saldo devedor e MUDA com sua idade — quem tem 30 anos paga ~0,025% a.m., quem tem 55 paga ~0,08%; (2) sua taxa final depende do seu relacionamento com o banco, score e modalidade (FGTS, SBPE, MCMV); (3) tem custos fixos (DFI ~0,014% sobre imovel, tarifa adm ~R$ 25). A Priscila ja conseguiu reduzir 1 a 1,5 ponto da tabela em casos com bom perfil. Quer que ela analise o seu?" },
];
const IA_CHAT_FALLBACK = "Entendi. Pra eu te indicar com precisao: qual bairro voce tem em mente, quantos quartos, e ate quanto voce pretende investir? Com esses tres pontos eu ja filtro as melhores opcoes da carteira ativa.";

function aiChatResponse(text) {
  for (const r of IA_CHAT_RESPONSES) if (r.match.test(text)) return r.resposta;
  return IA_CHAT_FALLBACK;
}

// Live ticker data
const TICKER_ITEMS = [
  "12 imóveis adicionados hoje",
  "Candeias · ticket médio R$ 1,12 mi · alta de 8,2 %",
  "Boa Vista · 487 buscas/sem · demanda recorde",
  "Recreio · yield 0,68 % a.m. · perfil investidor",
  "27 bairros monitorados · 1.842 imóveis ativos",
  "Tempo médio de 1ª resposta · 94 ms",
];

Object.assign(window, { BAIRROS, IMOVEIS, DEPOIMENTOS, IA_CAPACIDADES, IA_CHAT_INTRO, IA_CHAT_SUGESTOES, aiChatResponse, TICKER_ITEMS });
