const snapshot = {
  data: "04/07/2026",
  leads: 76,
  novos7d: 27,
  quentes: 37,
  mornos: 17,
  frios: 22,
  whatsapp: 68,
  avaliacoes: 25,
  simulacoes: 24,
  imoveisAtivos: 12
};

const properties = [
  {
    slug: "ponto-comercial-multiplace-para-locacao-felicia",
    titulo: "Ponto Comercial Multiplace para Locacao",
    bairro: "Felicia",
    tipo: "Comercial",
    finalidade: "aluguel",
    quartos: 0,
    suites: 0,
    vagas: 1,
    area: 81,
    preco: 6500,
    destaque: true,
    hooks: ["locacao comercial", "Shopping Conquista Sul", "planta versatil"],
    features: ["visibilidade", "fluxo", "estacionamento"]
  },
  {
    slug: "apartamento-a-venda-candeias",
    titulo: "Apartamento Mansao Leonardo da Vinci",
    bairro: "Candeias",
    tipo: "Apartamento",
    finalidade: "venda",
    quartos: 4,
    suites: 4,
    vagas: 4,
    area: 190,
    preco: 1300000,
    destaque: true,
    hooks: ["alto padrao", "Candeias", "4 suites"],
    features: ["andar alto", "cozinha planejada", "condominio"]
  },
  {
    slug: "casa-duplex-a-venda-boa-vista",
    titulo: "Casa Duplex no Boa Vista",
    bairro: "Boa Vista",
    tipo: "Casa",
    finalidade: "venda",
    quartos: 5,
    suites: 3,
    vagas: 3,
    area: 500,
    preco: 1500000,
    destaque: true,
    hooks: ["alto padrao", "piscina aquecida", "energia solar"],
    features: ["area de lazer", "ofuro", "suite master", "energia solar"]
  },
  {
    slug: "casa-terrea-a-venda-alphaville-i-primavera",
    titulo: "Casa Terrea Alphaville I",
    bairro: "Primavera",
    tipo: "Casa",
    finalidade: "venda",
    quartos: 4,
    suites: 4,
    vagas: 2,
    area: 395,
    preco: 1420000,
    destaque: false,
    hooks: ["casa terrea", "Alphaville I", "projeto contemporaneo"],
    features: ["area gourmet", "piscina", "home office", "cozinha integrada"]
  },
  {
    slug: "casa-terrea-a-venda-horto-premier-primavera",
    titulo: "Casa Terrea Horto Premier",
    bairro: "Primavera",
    tipo: "Casa",
    finalidade: "venda",
    quartos: 3,
    suites: 3,
    vagas: 2,
    area: 310,
    preco: 950000,
    destaque: false,
    hooks: ["casa terrea", "Horto Premier", "3 suites"],
    features: ["area gourmet", "moveis planejados", "lavabo"]
  },
  {
    slug: "terreno-a-venda-haras-camping-club-rodovia-conquista-ba-415-barra-do-choca",
    titulo: "Terreno Haras Camping Club",
    bairro: "Rodovia Conquista BA-415 - Barra do Choca",
    tipo: "Terreno",
    finalidade: "venda",
    quartos: 0,
    suites: 0,
    vagas: 0,
    area: 1022,
    preco: 210000,
    destaque: false,
    hooks: ["natureza", "privacidade", "final de rua"],
    features: ["nascente", "sem vizinho lateral", "condominio"]
  },
  {
    slug: "terreno-de-esquina-a-venda-haras-camping-club-rodovia-conquista-ba-415-barra-do-choca",
    titulo: "Terreno de Esquina Haras Camping Club",
    bairro: "Rodovia Conquista BA-415 - Barra do Choca",
    tipo: "Terreno",
    finalidade: "venda",
    quartos: 0,
    suites: 0,
    vagas: 0,
    area: 1000,
    preco: 290000,
    destaque: false,
    hooks: ["esquina", "empreendimento", "area lateral comum"],
    features: ["lazer", "areas verdes", "portaria"]
  },
  {
    slug: "casa-a-venda-caminho-do-parque-caminho-do-parque-bela-vista",
    titulo: "Casa Caminho do Parque",
    bairro: "Caminho do Parque - Bela Vista",
    tipo: "Casa",
    finalidade: "venda",
    quartos: 3,
    suites: 3,
    vagas: 4,
    area: 755,
    preco: 2600000,
    destaque: false,
    hooks: ["alto padrao", "area gourmet", "piscina aquecida"],
    features: ["area gourmet", "sala de jogos", "piscina aquecida", "suite master"]
  },
  {
    slug: "casa-terrea-a-venda-parque-dos-ipes-i-boa-vista",
    titulo: "Casa Parque dos Ipes I",
    bairro: "Boa Vista",
    tipo: "Casa",
    finalidade: "venda",
    quartos: 3,
    suites: 3,
    vagas: 2,
    area: 450,
    preco: 2000000,
    destaque: false,
    hooks: ["alto padrao", "automacao residencial", "piscina aquecida"],
    features: ["area gourmet", "energia solar", "automacao", "suite master"]
  },
  {
    slug: "apartamento-a-venda-bairro-candeias-candeias-2",
    titulo: "Apartamento Maison du Soleil",
    bairro: "Candeias",
    tipo: "Apartamento",
    finalidade: "venda",
    quartos: 3,
    suites: 1,
    vagas: 2,
    area: 105,
    preco: 500000,
    destaque: false,
    hooks: ["Candeias", "praticidade", "condominio"],
    features: ["dependencia", "deposito", "lazer"]
  },
  {
    slug: "apartamento-a-venda-bairro-candeias-candeias",
    titulo: "Apartamento Mansao Joaquim Gusmao Sales",
    bairro: "Candeias",
    tipo: "Apartamento",
    finalidade: "venda",
    quartos: 3,
    suites: 3,
    vagas: 3,
    area: 172,
    preco: 1600000,
    destaque: false,
    hooks: ["alto padrao", "area gourmet", "piscina aquecida"],
    features: ["area gourmet", "churrasqueira", "forno de pizza", "piscina aquecida"]
  },
  {
    slug: "terreno-a-venda-av-brasil-candeias",
    titulo: "Terreno Av. Brasil",
    bairro: "Candeias",
    tipo: "Terreno",
    finalidade: "venda",
    quartos: 0,
    suites: 0,
    vagas: 0,
    area: 396,
    preco: 430000,
    destaque: false,
    hooks: ["investimento", "Av. Brasil", "visibilidade"],
    features: ["12 metros de frente", "33 metros de profundidade", "fluxo"]
  }
];

const agents = [
  {
    nome: "Validador de Criativo",
    funcao: "Confere se o post usa dados reais, localidade correta, foto coerente e CTA seguro.",
    ferramentas: ["Carteira de imoveis", "Fila Instagram", "Regras da marca"]
  },
  {
    nome: "Curador de Noticias",
    funcao: "Busca noticias atuais, resume com fonte/data e manda para revisao.",
    ferramentas: ["Web search", "Fila Make", "Fonte oficial"]
  },
  {
    nome: "Triador de Leads",
    funcao: "Classifica lead de avaliacao, simulacao, WhatsApp ou Lead Ads sem expor PII.",
    ferramentas: ["CRM", "Planilha backup", "Alerta interno"]
  },
  {
    nome: "Relator Semanal",
    funcao: "Monta leitura de funil, conteudo e proximas acoes usando dados agregados.",
    ferramentas: ["Resumo de leads", "Posts", "Calculadoras"]
  },
  {
    nome: "Operador de Fila",
    funcao: "Organiza status PENDENTE_REVISAO, APROVADO, PUBLICADO e ERRO.",
    ferramentas: ["Google Sheets", "Data Store", "Make MCP"]
  },
  {
    nome: "Planejador de Campanha",
    funcao: "Transforma prioridade em briefing de publico, oferta, CTA e medicao.",
    ferramentas: ["MCP Priscila", "Meta Ads pausado", "Site oficial"]
  }
];

const forbidden = [
  "america bahia",
  "valoriza garantido",
  "venda garantida",
  "financiamento aprovado",
  "laudo gratis",
  "imperdivel",
  "vende rapido"
];

const cityTerms = ["vitoria da conquista", "conquista", "vdc"];

const calculatorSnippets = {
  financiamento: "Quer entender se esse imovel cabe no seu planejamento? Acesse o site oficial da Priscila e use a calculadora de financiamento antes de decidir a visita.",
  avaliacao: "Pensando em vender? Comece pela avaliacao online gratuita para ter uma primeira estimativa. O laudo formal e um servico profissional pago, feito com criterio tecnico.",
  rota: "Site -> evento calculadora_concluida ou avaliacao_concluida -> CRM -> classificacao -> alerta interno -> relatorio semanal sem PII."
};

const $ = (id) => document.getElementById(id);

function money(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0
  }).format(value);
}

function normalizeText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function selectedProperty(selectId) {
  const slug = $(selectId).value;
  return properties.find((item) => item.slug === slug) || properties[0];
}

function showToast(message) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2400);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast("Copiado.");
  } catch {
    const helper = document.createElement("textarea");
    helper.value = text;
    document.body.appendChild(helper);
    helper.select();
    document.execCommand("copy");
    helper.remove();
    showToast("Copiado.");
  }
}

function renderMetrics() {
  const items = [
    ["Leads totais", snapshot.leads],
    ["Leads quentes", snapshot.quentes],
    ["Novos em 7 dias", snapshot.novos7d],
    ["Imoveis ativos", snapshot.imoveisAtivos],
    ["Origem WhatsApp", snapshot.whatsapp],
    ["Simulacoes", snapshot.simulacoes],
    ["Avaliacoes", snapshot.avaliacoes],
    ["Leads mornos/frios", `${snapshot.mornos}/${snapshot.frios}`]
  ];

  $("metrics").innerHTML = items
    .map(([label, value]) => `<article class="metric"><strong>${value}</strong><span>${label}</span></article>`)
    .join("");

  $("priorityText").textContent = "O volume de leads quentes e WhatsApp pede rotina forte de qualificacao e follow-up. O melhor motor agora e combinar posts de imoveis reais com calculadoras do site para captar comprador e proprietario.";
}

function renderProperties() {
  const options = properties
    .map((item) => `<option value="${item.slug}">${item.titulo} - ${item.bairro}</option>`)
    .join("");
  ["postProperty", "validatorProperty"].forEach((id) => {
    $(id).innerHTML = options;
  });

  $("propertyStrip").innerHTML = properties
    .slice(0, 6)
    .map((item) => {
      const details = [
        item.tipo,
        item.finalidade === "aluguel" ? "aluguel" : "venda",
        `${item.area} m2`
      ].join(" · ");
      return `<article class="property-card">
        <h3>${item.titulo}</h3>
        <p>${details}</p>
        <p>${item.bairro} · ${money(item.preco)}</p>
        <small>${item.hooks.slice(0, 2).join(" / ")}</small>
      </article>`;
    })
    .join("");
}

function propertyLine(property) {
  const parts = [];
  if (property.quartos) parts.push(`${property.quartos} quartos`);
  if (property.suites) parts.push(`${property.suites} suites`);
  if (property.vagas) parts.push(`${property.vagas} vagas`);
  parts.push(`${property.area} m2`);
  return parts.join(", ");
}

function goalCta(goal) {
  const map = {
    visita: "Fale com a Priscila e agende uma visita.",
    site: "Veja os detalhes no site oficial da Priscila.",
    whatsapp: "Me chama no WhatsApp para entender se faz sentido para voce.",
    avaliacao: "Se voce tambem tem um imovel, comece pela avaliacao online no site."
  };
  return map[goal] || map.visita;
}

function generatePostText() {
  const property = selectedProperty("postProperty");
  const format = $("postFormat").value;
  const goal = $("postGoal").value;
  const finalidade = property.finalidade === "aluguel" ? "para aluguel" : "a venda";
  const categoria = `${property.tipo} ${finalidade}`;
  const lines = [];

  if (format === "story") {
    lines.push(`${property.titulo}`);
    lines.push(`${categoria} em ${property.bairro}, Vitoria da Conquista - BA.`);
    lines.push(propertyLine(property));
    lines.push(`Valor anunciado: ${money(property.preco)}.`);
    lines.push(goalCta(goal));
  } else if (format === "carrossel") {
    lines.push(`Slide 1: ${property.titulo}`);
    lines.push(`Slide 2: ${categoria} em ${property.bairro}, Vitoria da Conquista - BA.`);
    lines.push(`Slide 3: ${propertyLine(property)}.`);
    lines.push(`Slide 4: Destaques: ${property.hooks.join(", ")}.`);
    lines.push(`Slide 5: ${goalCta(goal)}`);
  } else if (format === "reel") {
    lines.push(`Roteiro curto: ${property.titulo}.`);
    lines.push(`Cena 1: detalhe do imovel e bairro ${property.bairro}.`);
    lines.push(`Cena 2: mostrar ${property.hooks.slice(0, 2).join(" e ")}.`);
    lines.push(`Cena 3: ${propertyLine(property)}. Valor anunciado: ${money(property.preco)}.`);
    lines.push(`Fechamento: ${goalCta(goal)}`);
  } else {
    lines.push(`${property.titulo}`);
    lines.push("");
    lines.push(`${categoria} em ${property.bairro}, Vitoria da Conquista - BA.`);
    lines.push("");
    lines.push(`${propertyLine(property)} e valor anunciado de ${money(property.preco)}.`);
    lines.push(`Destaques: ${property.hooks.join(", ")}.`);
    lines.push("");
    lines.push(goalCta(goal));
    lines.push("Priscila Vasconcelos Imoveis | CRECI-BA 29.231");
  }

  $("postOutput").value = lines.join("\n");
  $("makeTitle").value = property.titulo;
  return $("postOutput").value;
}

function validateCreative() {
  const property = selectedProperty("validatorProperty");
  const text = $("validatorText").value || "";
  const status = $("approvalStatus").value;
  const normalized = normalizeText(text);
  const results = [];

  function add(type, message) {
    results.push({ type, message });
  }

  if (!text.trim()) {
    add("bad", "Cole um texto para validar.");
  }

  if (status !== "APROVADO") {
    add("warn", `Status atual: ${status}. Isso nao deve publicar, apenas entrar/rester na fila.`);
  } else {
    add("ok", "Status APROVADO. Ainda assim, a ferramenta final precisa conferir as travas antes de publicar.");
  }

  if (!cityTerms.some((term) => normalized.includes(term))) {
    add("warn", "Inclua a localidade correta: Vitoria da Conquista - BA ou bairro/regiao real.");
  } else {
    add("ok", "Localidade de Vitoria da Conquista/regiao encontrada.");
  }

  if (!normalized.includes(normalizeText(property.tipo))) {
    add("warn", `O texto nao identifica claramente o tipo: ${property.tipo}.`);
  } else {
    add("ok", `Tipo identificado: ${property.tipo}.`);
  }

  const saleWords = ["venda", "a venda", "comprar"];
  const rentWords = ["aluguel", "locacao", "locar"];
  const hasSale = saleWords.some((word) => normalized.includes(word));
  const hasRent = rentWords.some((word) => normalized.includes(word));

  if (property.finalidade === "venda" && hasRent) {
    add("bad", "O imovel e de venda, mas o texto fala em aluguel/locacao.");
  }
  if (property.finalidade === "aluguel" && hasSale) {
    add("bad", "O imovel e de aluguel, mas o texto fala em venda.");
  }
  if (!hasSale && !hasRent) {
    add("warn", `Informe a finalidade: ${property.finalidade}.`);
  }

  forbidden.forEach((word) => {
    if (normalized.includes(word)) {
      add("bad", `Evite promessa ou termo proibido: "${word}".`);
    }
  });

  if (normalized.includes("area gourmet") && !property.features.includes("area gourmet")) {
    add("bad", "O texto fala em area gourmet, mas esse imovel nao tem esse destaque registrado aqui.");
  }

  if (normalized.includes("noticia") && !normalized.includes("fonte")) {
    add("warn", "Conteudo de noticia precisa fonte e data antes de entrar na fila.");
  }

  if (!normalized.includes("priscila") && !normalized.includes("site") && !normalized.includes("whatsapp")) {
    add("warn", "Inclua um CTA claro para Priscila, site oficial ou WhatsApp.");
  }

  if (!results.some((item) => item.type === "bad")) {
    add("ok", "Nao encontrei erro critico. Revise a foto antes de aprovar.");
  }

  $("validatorResult").innerHTML = results
    .map((item) => `<div class="result-item ${item.type}">${item.message}</div>`)
    .join("");
}

function campaignBrief() {
  const priority = $("campaignPriority").value;
  const channel = $("campaignChannel").value;
  const briefs = {
    captacao: {
      objetivo: "Captar proprietarios que pensam em vender com mais criterio.",
      publico: "Proprietarios em Vitoria da Conquista com duvida de preco, prazo ou estrategia de venda.",
      oferta: "Avaliacao online como primeiro passo; laudo formal segue como servico profissional pago.",
      criativo: "Carrossel educativo com erros comuns ao precificar e CTA para avaliacao online.",
      metrica: "Leads de avaliacao, proprietarios identificados e conversas iniciadas."
    },
    alto_padrao: {
      objetivo: "Gerar interesse qualificado nos imoveis acima de R$ 950 mil.",
      publico: "Compradores buscando conforto, seguranca, condominio e localizacao premium.",
      oferta: "Curadoria de imoveis selecionados, com dados reais e visita consultiva.",
      criativo: "Post/carrossel com foto real, bairro, metragem, suites e diferenciais.",
      metrica: "Cliques no site, WhatsApp e visitas agendadas."
    },
    aluguel_comercial: {
      objetivo: "Atrair empresas para o ponto comercial Multiplace.",
      publico: "Clinicas, escritorios, lojas, consultorios e negocios de servico.",
      oferta: "Espaco de 81 m2 ao lado do Shopping Conquista Sul.",
      criativo: "Antes/depois de ocupacao imaginada sem simular foto falsa do imovel.",
      metrica: "Contatos comerciais e visitas ao espaco."
    },
    calculadoras: {
      objetivo: "Transformar curiosidade em lead qualificado.",
      publico: "Compradores que querem simular financiamento e proprietarios que querem estimativa.",
      oferta: "Ferramentas gratuitas no site: financiamento e avaliacao online.",
      criativo: "Infografico simples explicando quando usar cada calculadora.",
      metrica: "Simulacoes, avaliacoes e origem dos leads."
    },
    lead_ads: {
      objetivo: "Testar captacao paga com formularios Meta sem ativar gasto sem aprovacao.",
      publico: "Compradores e proprietarios por interesse local.",
      oferta: "Atendimento consultivo, simulacao e avaliacao.",
      criativo: "Anuncios pausados, categoria HOUSING e UTM.",
      metrica: "CPL qualificado, temperatura e taxa de resposta."
    },
    noticias: {
      objetivo: "Fortalecer autoridade local com conteudo atual.",
      publico: "Seguidores interessados em mercado, juros, financiamento e bairros.",
      oferta: "Boletim curto com fonte, data e leitura pratica.",
      criativo: "Story ou post infografico sem sensacionalismo.",
      metrica: "Salvamentos, respostas e cliques no site."
    }
  };

  const selected = briefs[priority];
  const brief = {
    data: snapshot.data,
    canal: channel,
    status: channel === "meta_ads" ? "RASCUNHO_PAUSADO" : "PENDENTE_REVISAO",
    objetivo: selected.objetivo,
    publico: selected.publico,
    oferta: selected.oferta,
    criativo: selected.criativo,
    cta: "Fale com a Priscila / Veja no site oficial",
    make: "Entrar na fila como PENDENTE_REVISAO. Publicar somente se APROVADO.",
    metrica: selected.metrica,
    restricoes: [
      "Sem promessa de valorizacao ou venda rapida",
      "Sem PII de lead em criativo",
      "Ads imobiliarios sempre HOUSING e pausados",
      "Fotos de imovel devem ser do mesmo slug"
    ]
  };

  $("campaignOutput").textContent = JSON.stringify(brief, null, 2);
  return brief;
}

function currentPublishDate() {
  if ($("makeDate").value) return $("makeDate").value;
  const date = new Date(Date.now() + 24 * 60 * 60 * 1000);
  date.setMinutes(0, 0, 0);
  return date.toISOString().slice(0, 16);
}

function buildPayload() {
  const property = selectedProperty("postProperty");
  const item = {
    id: `ig-${Date.now()}`,
    status: "PENDENTE_REVISAO",
    canal: "instagram",
    tipo_make: $("makeType").value,
    titulo: $("makeTitle").value || property.titulo,
    legenda: $("postOutput").value || generatePostText(),
    media_url: "",
    media_urls_json: "[]",
    publish_at: currentPublishDate(),
    localidade: "Vitoria da Conquista - BA",
    slug: property.slug,
    fonte_url: "",
    fonte_nome: "",
    aprovado_por: "",
    observacao: "Gerado pela Suite de Marketing. Revisar foto e texto antes de aprovar."
  };

  const payload = {
    ferramenta: "registrar_pacote_criativo_pendente",
    criado_em: new Date().toISOString(),
    origem: "codex_marketing_suite",
    items: [item]
  };

  $("payloadOutput").textContent = JSON.stringify(payload, null, 2);
  return payload;
}

function csvFromPayload(payload) {
  const headers = Object.keys(payload.items[0]);
  const rows = payload.items.map((item) =>
    headers.map((key) => `"${String(item[key] ?? "").replace(/"/g, '""')}"`).join(",")
  );
  return [headers.join(","), ...rows].join("\n");
}

function downloadCsv() {
  const payload = buildPayload();
  const blob = new Blob([csvFromPayload(payload)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fila-make-priscila-pendente.csv";
  link.click();
  URL.revokeObjectURL(url);
}

function renderAgents() {
  $("agentGrid").innerHTML = agents
    .map((agent) => `<article class="agent-card">
      <h3>${agent.nome}</h3>
      <p>${agent.funcao}</p>
      <ul>${agent.ferramentas.map((tool) => `<li>${tool}</li>`).join("")}</ul>
    </article>`)
    .join("");
}

function bindNavigation() {
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-button").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".tool-section").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      $(button.dataset.target).classList.add("active");
    });
  });
}

function bindActions() {
  $("generatePost").addEventListener("click", generatePostText);
  $("copyPost").addEventListener("click", () => copyText($("postOutput").value));
  $("runValidator").addEventListener("click", validateCreative);
  $("useGenerated").addEventListener("click", () => {
    $("validatorText").value = $("postOutput").value || generatePostText();
    validateCreative();
  });
  $("generateCampaign").addEventListener("click", campaignBrief);
  $("copyCampaign").addEventListener("click", () => copyText($("campaignOutput").textContent));
  $("buildPayload").addEventListener("click", buildPayload);
  $("copyPayload").addEventListener("click", () => copyText($("payloadOutput").textContent || JSON.stringify(buildPayload(), null, 2)));
  $("downloadCsv").addEventListener("click", downloadCsv);
  document.querySelectorAll(".mini-copy").forEach((button) => {
    button.addEventListener("click", () => {
      $("calculatorCopy").value = calculatorSnippets[button.dataset.copy];
      copyText($("calculatorCopy").value);
    });
  });
}

function init() {
  renderMetrics();
  renderProperties();
  renderAgents();
  bindNavigation();
  bindActions();
  generatePostText();
  campaignBrief();
  buildPayload();
}

init();
