// Camada de acesso aos dados reais da PVSCELOS.
// Em dev, o proxy do Vite (vite.config.js) manda /api e /assets pra produção.
// Em produção, são o mesmo domínio. Por isso usamos caminhos relativos.

// Monta a URL de uma foto a partir do campo "arquivo" do backend.
// size: 200 | 600 | 1200 | 2400 (webp) — ou "original.jpg".
export function imgUrl(arquivo, size = 600) {
  if (!arquivo) return null
  const sufixo = size === 'original' ? 'original.jpg' : `${size}.webp`
  return `/assets/${arquivo}/${sufixo}`
}

// Preço em reais, sem centavos: R$ 1.300.000
export function formatBRL(valor) {
  if (valor == null) return 'Sob consulta'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(valor)
}

// Escolhe a foto de capa de um imóvel (tipo "capa" > menor ordem > primeira).
function capa(imagens = []) {
  if (!imagens.length) return null
  const cap = imagens.find((i) => i.tipo === 'capa')
  if (cap) return cap
  return [...imagens].sort((a, b) => (a.ordem ?? 0) - (b.ordem ?? 0))[0]
}

// Normaliza o imóvel cru do backend para o formato que a UI consome.
export function normalizeImovel(im) {
  const fotos = (im.imagens || [])
    .slice()
    .sort((a, b) => (a.ordem ?? 0) - (b.ordem ?? 0))
  const cap = capa(im.imagens)
  return {
    id: im.id,
    slug: im.slug,
    titulo: im.titulo,
    bairro: im.bairro,
    tipo: im.tipo,
    quartos: im.quartos,
    suites: im.suites,
    vagas: im.vagas,
    area: im.area_util,
    preco: im.preco,
    precoFmt: formatBRL(im.preco),
    descricao: im.descricao,
    caracteristicas: im.caracteristicas || [],
    destaque: im.destaque,
    tour360: im.tour_360_url || null,
    capaUrl: cap ? imgUrl(cap.arquivo, 600) : null,
    fotos: fotos.map((f) => ({
      thumb: imgUrl(f.arquivo, 600),
      grande: imgUrl(f.arquivo, 2400),
      legenda: f.legenda || '',
      tipo: f.tipo,
    })),
  }
}

async function getJSON(url) {
  const r = await fetch(url)
  if (!r.ok) throw new Error(`${url} -> HTTP ${r.status}`)
  return r.json()
}

// Lista de imóveis ativos, já normalizados.
export async function getImoveis() {
  const data = await getJSON('/api/imoveis')
  const items = data.items || data.result || []
  return items.map(normalizeImovel)
}

// Um imóvel pelo slug (ou id), normalizado — ou null se não achar.
export async function getImovel(slugOuId) {
  const lista = await getImoveis()
  return (
    lista.find((i) => String(i.slug) === String(slugOuId) || String(i.id) === String(slugOuId)) ||
    null
  )
}

// Rótulo amigável do status da obra.
function statusObraLabel(s) {
  return { pronto: 'Pronto para morar', na_planta: 'Na planta', em_obras: 'Em obras' }[s] || (s || '')
}

// Normaliza um empreendimento cru (usa TODO o detalhe real: descrição, lazer,
// diferenciais, construtora, condições, tour 360, fotos).
export function normalizeEmpreendimento(e) {
  const fotos = (e.imagens || []).slice().sort((a, b) => (a.ordem ?? 0) - (b.ordem ?? 0))
  const cap = capa(e.imagens)
  return {
    id: e.id,
    slug: e.slug,
    nome: (e.nome || '').trim(),
    bairro: (e.bairro || '').trim(),
    construtora: (e.construtora || '').trim(),
    descricao: e.descricao || '',
    status: statusObraLabel(e.status_obra),
    statusRaw: e.status_obra || '',
    entrega: (e.entrega_prevista || '').trim(),
    unidades: e.num_unidades || null,
    torres: e.num_torres || null,
    andares: e.num_andares || null,
    lazer: e.lazer || [],
    diferenciais: e.diferenciais || [],
    condicoes: e.condicoes_pagamento || '',
    tour360: e.tour_360_url || null,
    video: e.video_url || null,
    capaUrl: cap ? imgUrl(cap.arquivo, 1200) : null,
    fotos: fotos.map((f) => ({ thumb: imgUrl(f.arquivo, 600), grande: imgUrl(f.arquivo, 2400), legenda: f.legenda || '' })),
  }
}

export async function getEmpreendimentos() {
  const data = await getJSON('/api/empreendimentos')
  const items = data.items || data.result || []
  return items.map(normalizeEmpreendimento)
}

export async function getDepoimentos() {
  const data = await getJSON('/api/depoimentos')
  return data.items || data.result || []
}

// Panorama REAL do mercado: preço do m² por bairro (calibrado). [{bairro, m2}]
export async function getPanorama() {
  const data = await getJSON('/api/avaliacao/panorama')
  return data.construido || data.items || []
}

// Abre o chat da Ana de qualquer lugar do site (o ChatAna escuta este evento).
export function abrirAna() {
  window.dispatchEvent(new Event('abrir-ana'))
}

// Conversão no GA4 (se o gtag carregou). tipo: 'avaliacao' | 'anunciar' | 'agendar_visita'
export function trackLead(tipo) {
  try {
    if (window.gtag) window.gtag('event', 'generate_lead', { lead_tipo: tipo })
  } catch { /* sem analytics, segue */ }
  try {
    if (window.fbq) window.fbq('track', 'Lead', { content_name: tipo })
  } catch { /* sem pixel, segue */ }
}

// Agendar visita a um imóvel → /api/agendar-visita (vira lead + evento na agenda).
export async function agendarVisita({ nome, telefone, data_preferida, titulo_imovel, bairro, observacoes }) {
  const r = await fetch('/api/agendar-visita', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nome,
      telefone,
      data_preferida,
      titulo_imovel: titulo_imovel || null,
      bairro: bairro || null,
      observacoes: observacoes || null,
    }),
  })
  if (!r.ok) throw new Error('agendar-visita HTTP ' + r.status)
  return r.json()
}

// ── Chat com a Ana (a assistente da Priscila) — consome /api/chat ──
let _sessionId = null
export async function enviarChat(message, history = []) {
  if (!_sessionId) {
    _sessionId = 'site-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8)
  }
  const r = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history, session_id: _sessionId }),
  })
  if (!r.ok) throw new Error('chat HTTP ' + r.status)
  const data = await r.json()
  if (data.session_id) _sessionId = data.session_id
  return data // { resposta, rota, ... }
}

// ── Captação / avaliação: quem quer anunciar ou avaliar o imóvel → /api/lead-vendedor ──
export async function enviarLeadVendedor({ nome, telefone, bairro, tipo = 'Casa', area, quartos, valor_pretendido, observacoes }) {
  const r = await fetch('/api/lead-vendedor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nome,
      telefone,
      bairro: bairro || null,
      tipo,
      area: area ? Number(area) : null,
      quartos: quartos ? Number(quartos) : null,
      valor_pretendido: valor_pretendido ? Number(valor_pretendido) : null,
      observacoes: observacoes || null,
    }),
  })
  if (!r.ok) throw new Error('lead-vendedor HTTP ' + r.status)
  return r.json()
}
