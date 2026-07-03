import React, { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import { ArrowLeft, Calculator, Home as HomeIcon, TrendingUp, Sparkles, Info, User, Building2, Landmark, BadgeCheck, MessageCircle, Send, X } from 'lucide-react';
import {
  perfilFinanciamento, simularFinanciamento, analiseFinanciamento, avaliarImovel,
  getBairrosAvaliacao, getPanorama, formatBRL, abrirAna, agendarVisita, guiaSimulador, trackLead,
} from './api';

// ─────────────────────────────────────────────────────────────────────────────
// Página de Calculadoras (TESTE — ?calc=1, fora do menu).
// Estrutura inspirada na referência do Thiago: tema claro/areia, perfil completo
// (cadastro + perguntas pra alinhar), enquadramento + taxa + subsídio, gráficos
// Chart.js, análise pela Ana (nossa IA), custos e bairros reais. Tudo ESTIMATIVA.
// ─────────────────────────────────────────────────────────────────────────────

const card = 'bg-white/70 backdrop-blur border border-[#dde5f0] rounded-2xl shadow-[0_10px_30px_-12px_rgba(22,40,75,0.12)]';
const inputCls = 'w-full bg-white border border-[#dde5f0] rounded-lg px-3 py-2.5 text-sm text-[#16284B] focus:outline-none focus:ring-2 focus:ring-[#5C7CB8]/40 [&>option]:text-[#16284B]';
const labelCls = 'block text-xs font-semibold text-[#5d6b86] mb-1.5';
const gold = { background: 'linear-gradient(120deg,#c9943a,#e8b55a)' };

const AvisoEstimativa = ({ children }) => (
  <div className="flex gap-3 items-start bg-[#f5f0e8] border border-[#e8d9bf] rounded-xl px-4 py-3 text-sm text-[#8a6a2b]">
    <Info size={18} className="shrink-0 mt-0.5" />
    <p className="font-light leading-relaxed">{children}</p>
  </div>
);

export default function Calculadoras({ onBack }) {
  const [aba, setAba] = useState('financiamento');
  return (
    <div className="min-h-screen text-[#16284B]" style={{ background: 'linear-gradient(135deg,#FBFCFE 0%,#f5f0e8 100%)' }}>
      <header className="border-b border-[#dde5f0] bg-white/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
          <button onClick={onBack} className="flex items-center gap-2 text-sm text-[#5d6b86] hover:text-[#16284B] transition-colors">
            <ArrowLeft size={18} /> <span className="hidden sm:inline">Voltar ao site</span>
          </button>
          <img src="/selo.png" alt="Priscila Vasconcelos" className="h-10 md:h-12 w-auto" />
          <span className="text-xs uppercase tracking-[0.2em] text-[#c9943a] font-bold hidden sm:flex items-center gap-2">
            <HomeIcon size={15} /> Simuladores
          </span>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="text-center mb-8 space-y-3">
          <h1 className="text-3xl md:text-5xl font-bold tracking-tight">
            Simule o valor da sua <span style={{ background: 'linear-gradient(120deg,#c9943a,#e8b55a)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>casa</span>
          </h1>
          <p className="text-[#5d6b86] max-w-2xl mx-auto">
            Simule o valor da sua casa, do seu financiamento ou do seu aluguel — com os números reais
            de Vitória da Conquista.
          </p>
          <p className="text-xs text-[#7b95c8] max-w-2xl mx-auto bg-[#f5f0e8]/60 border border-[#e8dcc4] rounded-xl px-4 py-2.5">
            ⚠️ É uma <strong>estimativa</strong> — nossa avaliação é bem calibrada e chega <strong>perto do valor real</strong>,
            mas o preço final depende de detalhes como padrão de acabamento, estado de conservação e a localização exata.
            Para o valor certo, a <strong>Priscila avalia pessoalmente</strong>.
          </p>
        </div>

        <div className="flex justify-center mb-10">
          <div className="inline-flex bg-white border border-[#dde5f0] rounded-full p-1 shadow-sm">
            {[['financiamento', 'Simule seu financiamento', Calculator], ['avaliacao', 'Avalie sua casa', HomeIcon]].map(([k, l, Icon]) => (
              <button key={k} onClick={() => setAba(k)}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold transition-all ${aba === k ? 'text-[#16284B]' : 'text-[#5d6b86] hover:text-[#16284B]'}`}
                style={aba === k ? gold : {}}>
                <Icon size={16} /> {l}
              </button>
            ))}
          </div>
        </div>

        {aba === 'financiamento' ? <Financiamento /> : <Avaliacao />}
      </div>

      <footer className="border-t border-[#dde5f0] py-8 px-6 text-center text-xs text-[#5d6b86]">
        Priscila Vasconcelos · CRECI/BA 29.231 — simulações são estimativas e não substituem o parecer oficial do banco.
      </footer>

      {/* Agente-guia: só sabe do sistema (como usar a calculadora). Não é a Ana. */}
      <GuiaChat />
    </div>
  );
}

// Chat-guia flutuante: explica COMO a calculadora funciona (cada campo/botão). Só o sistema.
function GuiaChat() {
  const [aberto, setAberto] = useState(false);
  const [msgs, setMsgs] = useState([
    { de: 'bot', txt: 'Oi! Sou o guia desta página 😊 Posso explicar como usar a calculadora. Ex.: "como funciona?", "o que é SAC?", "como recebo o resultado?"' },
  ]);
  const [txt, setTxt] = useState('');
  const [carregando, setCarregando] = useState(false);
  const fimRef = useRef(null);

  useEffect(() => { fimRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs, aberto]);

  async function enviar() {
    const m = txt.trim();
    if (!m || carregando) return;
    setTxt('');
    const novo = [...msgs, { de: 'user', txt: m }];
    setMsgs(novo);
    setCarregando(true);
    try {
      const hist = novo.slice(-8).map((x) => ({ role: x.de === 'user' ? 'user' : 'assistant', content: x.txt }));
      const r = await guiaSimulador(m, hist);
      setMsgs((s) => [...s, { de: 'bot', txt: r.resposta || 'Preenche seu perfil e clica em Analisar — o resultado chega no seu WhatsApp! 💛' }]);
    } catch {
      setMsgs((s) => [...s, { de: 'bot', txt: 'Tive um probleminha agora. Mas é simples: preenche o perfil e clica em "Analisar meu perfil" — o resultado vai pro seu WhatsApp.' }]);
    } finally { setCarregando(false); }
  }

  if (!aberto) {
    return (
      <button onClick={() => setAberto(true)}
        className="fixed bottom-6 right-6 z-[60] flex items-center gap-2 text-[#16284B] pl-3 pr-4 py-3 rounded-full shadow-2xl hover:scale-105 transition-transform" style={gold}>
        <MessageCircle size={20} /> <span className="text-sm font-bold">Como funciona?</span>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-[60] w-[92vw] max-w-sm h-[70vh] max-h-[520px] flex flex-col bg-white rounded-2xl shadow-2xl border border-[#dde5f0] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 text-white" style={{ background: 'linear-gradient(120deg,#16284B,#2c4a82)' }}>
        <div className="flex items-center gap-2"><MessageCircle size={18} /><div><div className="text-sm font-bold">Guia da calculadora</div><div className="text-[10px] text-[#9db4dd]">explica como usar — só o sistema</div></div></div>
        <button onClick={() => setAberto(false)} className="text-white/70 hover:text-white"><X size={20} /></button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#FBFCFE]">
        {msgs.map((m, i) => (
          <div key={i} className={`max-w-[85%] text-sm rounded-2xl px-3 py-2 ${m.de === 'user' ? 'ml-auto bg-[#16284B] text-white rounded-tr-sm' : 'bg-[#eef2f8] text-[#16284B] rounded-tl-sm'}`}>{m.txt}</div>
        ))}
        {carregando && <div className="bg-[#eef2f8] text-[#5d6b86] text-sm rounded-2xl px-3 py-2 w-fit">digitando…</div>}
        <div ref={fimRef} />
      </div>
      <div className="p-3 border-t border-[#dde5f0] flex items-center gap-2">
        <input value={txt} onChange={(e) => setTxt(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && enviar()}
          placeholder="Pergunte como usar…" className="flex-1 bg-[#eef2f8] rounded-lg px-3 py-2.5 text-sm text-[#16284B] focus:outline-none" />
        <button onClick={enviar} disabled={carregando} className="text-[#16284B] p-2.5 rounded-lg disabled:opacity-50" style={gold}><Send size={18} /></button>
      </div>
    </div>
  );
}

// Panorama econômico (valores reais 2026)
function PanoramaEconomico() {
  const itens = [
    ['Taxa Selic', '14,25% a.a.'],
    ['MCMV Faixa 1', '4,5% a.a. · teto R$ 264.000'],
    ['MCMV Faixa 2', '6,0% a.a. · teto R$ 264.000'],
    ['MCMV Faixa 3', '7,9% a.a. · teto R$ 400.000'],
    ['MCMV Faixa 4', '10,0% a.a. · teto R$ 600.000'],
    ['ITBI Vitória da Conquista', '3,0%'],
  ];
  return (
    <div className={`${card} p-6 border-l-4 border-[#5C7CB8]`}>
      <h3 className="font-bold text-lg mb-4">Panorama econômico 2026</h3>
      <div className="space-y-3">
        {itens.map(([k, v]) => (
          <div key={k} className="flex justify-between items-baseline gap-3 border-b border-[#eef2f8] pb-2">
            <span className="text-[#5d6b86] text-sm shrink-0">{k}</span><span className="font-bold text-sm text-right">{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// SIMULADOR DE FINANCIAMENTO — perfil completo → enquadramento + simulação
// ═════════════════════════════════════════════════════════════════════════════
const VINCULOS = [['clt', 'CLT'], ['autonomo_mei', 'Autônomo / MEI'], ['servidor_publico', 'Servidor público'], ['aposentado', 'Aposentado']];
const SITUACOES = [['usado', 'Usado'], ['novo', 'Novo'], ['planta', 'Na planta']];

function Financiamento() {
  const [p, setP] = useState({
    nome: '', contato: '', email: '', idade: 35, vinculo: 'clt', renda: 4500, dependentes: 0,
    valor: 250000, entrada: 50000, situacao: 'usado', bairro: '', finalidade: 'morar',
    prazo: 360, sistema: 'SAC', temFgts: true, anosFgts: 3, primeiroImovel: true, nomeLimpo: true,
  });
  const [bairros, setBairros] = useState([]);
  const [res, setRes] = useState(null);   // { perfil, sim }
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [liberado, setLiberado] = useState(() => { try { return localStorage.getItem('pv_avaliou') === '1'; } catch { return false; } });
  const [soZap, setSoZap] = useState(false); // 1a vez: resultado foi so pro WhatsApp
  const [analise, setAnalise] = useState('');
  const [analisando, setAnalisando] = useState(false);

  useEffect(() => { getBairrosAvaliacao().then(setBairros).catch(() => {}); }, []);
  const set = (k, v) => setP((s) => ({ ...s, [k]: v }));

  const telOk = p.contato.replace(/\D/g, '').length >= 10;
  const podeAnalisar = p.nome.trim().length >= 2 && telOk;

  async function analisar() {
    setErro('');
    if (!podeAnalisar) { setErro('Preencha seu nome e um WhatsApp válido (com DDD) — é assim que a Priscila te retorna.'); return; }
    setCarregando(true); setAnalise('');
    try {
      const perfil = await perfilFinanciamento({
        renda: Number(p.renda), valor_imovel: Number(p.valor), entrada: Number(p.entrada),
        idade: Number(p.idade), tem_fgts: p.temFgts, anos_fgts: p.temFgts ? Number(p.anosFgts) : null,
        vinculo: p.vinculo, primeiro_imovel: p.primeiroImovel, imovel_situacao: p.situacao,
        finalidade: p.finalidade, dependentes: Number(p.dependentes), nome_limpo: p.nomeLimpo,
        nome: p.nome.trim(), contato: p.contato.replace(/\D/g, ''), email: p.email.trim() || null, bairro: p.bairro || null,
      });
      const sim = await simularFinanciamento({
        valor_imovel: Number(p.valor), entrada: Number(p.entrada), prazo_meses: Number(p.prazo),
        taxa_anual: perfil.taxa_anual, sistema: p.sistema, renda_mensal: Number(p.renda), idade_tomador: Number(p.idade),
      });
      setRes({ perfil, sim });
      trackLead('financiamento'); // conversão: GA4 generate_lead + Meta Lead
      // 1a vez: resultado vai so pro WhatsApp (gera a conversa/lead). Depois libera na tela.
      if (!liberado) {
        setSoZap(!!perfil.enviado_whatsapp);
        try { localStorage.setItem('pv_avaliou', '1'); } catch {}
        setLiberado(true);
      } else {
        setSoZap(false);
      }
    } catch (e) { setErro(String(e.message || e)); }
    finally { setCarregando(false); }
  }

  async function pedirAnalise() {
    if (!res) return;
    setAnalisando(true); setAnalise('');
    const _vinc = VINCULOS.find((v) => v[0] === p.vinculo)?.[1] || p.vinculo;
    try {
      const r = await analiseFinanciamento({
        enquadramento: res.perfil.enquadramento, taxa_anual: res.perfil.taxa_anual,
        subsidio_estimado: res.perfil.subsidio_estimado, renda: Number(p.renda),
        valor_imovel: Number(p.valor), entrada: Number(p.entrada),
        parcela_estimada: res.sim?.parcela_inicial_com_seguros, vinculo: _vinc,
        tem_fgts: p.temFgts, primeiro_imovel: p.primeiroImovel, sistema: p.sistema, nome: p.nome.trim(),
      });
      setAnalise(r.analise || 'Não consegui gerar agora — fale com a Priscila.');
    } catch { setAnalise('Não consegui gerar agora — fale com a Priscila aqui do site.'); }
    finally { setAnalisando(false); }
  }

  return (
    <div className="space-y-8">
      {/* Hero + panorama */}
      <div className="grid lg:grid-cols-2 gap-6 items-stretch">
        <div className={`${card} p-6 flex flex-col justify-center`}>
          <span className="text-xs font-bold tracking-widest text-[#c9943a] uppercase mb-2">Simulador paramétrico</span>
          <h2 className="text-2xl font-bold mb-2">Qual o seu enquadramento?</h2>
          <p className="text-[#5d6b86] text-sm leading-relaxed">
            Preencha seu perfil e a nossa inteligência aplica as regras do MCMV, Pró-Cotista (FGTS) e o mercado
            (SBPE) de 2026 pra dizer a faixa, a taxa e o subsídio que cabem em você.
          </p>
        </div>
        <PanoramaEconomico />
      </div>

      <div className="grid lg:grid-cols-5 gap-8">
        {/* ── Formulário de perfil (cadastro + perguntas) ── */}
        <div className={`lg:col-span-2 ${card} p-6 space-y-6 h-fit`}>
          {/* Passo 1 — Você */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-[#16284B] font-bold text-sm"><User size={16} className="text-[#c9943a]" /> 1. Você</div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className={labelCls}>Nome completo</label><input value={p.nome} onChange={(e) => set('nome', e.target.value)} placeholder="Seu nome" className={inputCls} /></div>
              <div><label className={labelCls}>WhatsApp</label><input value={p.contato} onChange={(e) => set('contato', e.target.value)} type="tel" placeholder="(77) 9 9999-9999" className={inputCls} /></div>
            </div>
            <div><label className={labelCls}>E-mail <small className="text-[#7b95c8]">(pra receber o resultado)</small></label><input value={p.email} onChange={(e) => set('email', e.target.value)} type="email" placeholder="voce@email.com" className={inputCls} /></div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className={labelCls}>Vínculo</label>
                <select value={p.vinculo} onChange={(e) => set('vinculo', e.target.value)} className={inputCls}>
                  {VINCULOS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
              </div>
              <div><label className={labelCls}>Idade</label><input type="number" min={18} max={80} value={p.idade} onChange={(e) => set('idade', Math.max(18, Math.min(80, +e.target.value || 35)))} className={inputCls} /></div>
            </div>
            <Slider label="Renda familiar (R$)" value={p.renda} min={1200} max={20000} step={100} onChange={(v) => set('renda', v)} fmt={formatBRL} />
            <div><label className={labelCls}>Dependentes</label><input type="number" min={0} max={20} value={p.dependentes} onChange={(e) => set('dependentes', +e.target.value || 0)} className={inputCls} /></div>
          </div>

          {/* Passo 2 — O imóvel */}
          <div className="space-y-3 border-t border-[#eef2f8] pt-5">
            <div className="flex items-center gap-2 text-[#16284B] font-bold text-sm"><Building2 size={16} className="text-[#c9943a]" /> 2. O imóvel</div>
            <Slider label="Valor do imóvel (R$)" value={p.valor} min={80000} max={2000000} step={10000} onChange={(v) => set('valor', v)} fmt={formatBRL} />
            <Slider label={`Entrada (${Math.round((p.entrada / p.valor) * 100) || 0}%)`} value={p.entrada} min={0} max={Math.round(p.valor * 0.8)} step={5000} onChange={(v) => set('entrada', v)} fmt={formatBRL} />
            <div className="grid grid-cols-2 gap-3">
              <div><label className={labelCls}>Situação</label>
                <select value={p.situacao} onChange={(e) => set('situacao', e.target.value)} className={inputCls}>
                  {SITUACOES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
              </div>
              <div><label className={labelCls}>Finalidade</label>
                <select value={p.finalidade} onChange={(e) => set('finalidade', e.target.value)} className={inputCls}>
                  <option value="morar">Morar</option><option value="investir">Investir</option>
                </select>
              </div>
            </div>
            <div><label className={labelCls}>Bairro de interesse</label>
              <select value={p.bairro} onChange={(e) => set('bairro', e.target.value)} className={inputCls}>
                <option value="">Indiferente / não sei</option>
                {bairros.map((b) => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className={labelCls}>Prazo</label>
                <select value={p.prazo} onChange={(e) => set('prazo', +e.target.value)} className={inputCls}>
                  {[120, 180, 240, 300, 360, 420].map((m) => <option key={m} value={m}>{m / 12} anos</option>)}
                </select>
              </div>
              <div><label className={labelCls}>Sistema</label>
                <div className="inline-flex w-full bg-[#eef2f8] rounded-lg p-1">
                  {['SAC', 'PRICE'].map((s) => (
                    <button key={s} onClick={() => set('sistema', s)}
                      className={`flex-1 py-1.5 rounded-md text-xs font-bold transition-colors ${p.sistema === s ? 'text-[#16284B] bg-white shadow-sm' : 'text-[#5d6b86]'}`}>
                      {s === 'PRICE' ? 'Price' : 'SAC'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Passo 3 — Crédito */}
          <div className="space-y-3 border-t border-[#eef2f8] pt-5">
            <div className="flex items-center gap-2 text-[#16284B] font-bold text-sm"><Landmark size={16} className="text-[#c9943a]" /> 3. Crédito</div>
            <label className="flex items-center justify-between gap-3 cursor-pointer text-sm text-[#16284B]">
              <span>Tenho FGTS</span>
              <input type="checkbox" checked={p.temFgts} onChange={(e) => set('temFgts', e.target.checked)} className="w-4 h-4 accent-[#c9943a]" />
            </label>
            {p.temFgts && (
              <div><label className={labelCls}>Anos de FGTS <small className="text-[#7b95c8]">(3+ libera o Pró-Cotista)</small></label>
                <input type="number" min={0} max={50} value={p.anosFgts} onChange={(e) => set('anosFgts', +e.target.value || 0)} className={inputCls} /></div>
            )}
            <label className="flex items-center justify-between gap-3 cursor-pointer text-sm text-[#16284B]">
              <span>É meu primeiro imóvel <small className="text-[#7b95c8]">(exigido no MCMV)</small></span>
              <input type="checkbox" checked={p.primeiroImovel} onChange={(e) => set('primeiroImovel', e.target.checked)} className="w-4 h-4 accent-[#c9943a]" />
            </label>
            <label className="flex items-center justify-between gap-3 cursor-pointer text-sm text-[#16284B]">
              <span>Nome sem restrição (limpo)</span>
              <input type="checkbox" checked={p.nomeLimpo} onChange={(e) => set('nomeLimpo', e.target.checked)} className="w-4 h-4 accent-[#c9943a]" />
            </label>
          </div>

          <button onClick={analisar} disabled={carregando}
            className="w-full py-3.5 rounded-xl text-sm font-bold uppercase tracking-widest text-[#16284B] transition-all hover:shadow-[0_8px_24px_-6px_rgba(201,148,58,0.5)] disabled:opacity-50" style={gold}>
            {carregando ? 'Analisando…' : 'Analisar meu perfil'}
          </button>
          {erro && <p className="text-sm text-red-600">{erro}</p>}
          {!p.nomeLimpo && <p className="text-xs text-[#8a6a2b]">Nome com restrição reduz muito a aprovação — vale limpar/negociar antes. A Priscila te orienta.</p>}
        </div>

        {/* ── Resultado ── */}
        <div className="lg:col-span-3 space-y-5">
          {res && soZap ? (
            <div className={`${card} p-8 text-center space-y-3`}>
              <div className="text-4xl">📲</div>
              <h4 className="font-bold text-xl text-[#16284B]">Enviamos sua análise no seu WhatsApp!</h4>
              <p className="text-sm text-[#5d6b86] max-w-sm mx-auto">Confere lá — a Priscila acompanha você pra chegar no financiamento e no imóvel certo. E agora você já pode simular <strong>à vontade aqui na tela</strong>! 💛</p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center pt-1">
                <button onClick={() => { setRes(null); setSoZap(false); }} className="border border-[#16284B] text-[#16284B] font-bold py-3 px-6 rounded-xl text-sm uppercase tracking-widest hover:bg-[#f5f0e8] transition-all inline-flex items-center justify-center gap-2">
                  Fazer outra simulação
                </button>
                <button onClick={abrirAna} className="text-[#16284B] font-bold py-3 px-6 rounded-xl text-sm uppercase tracking-widest transition-all hover:shadow-[0_8px_24px_-6px_rgba(201,148,58,0.5)] inline-flex items-center justify-center gap-2" style={gold}>
                  <Sparkles size={18} /> Falar com a Priscila
                </button>
              </div>
            </div>
          ) : res ? (
            <>
              {/* 3 cartões */}
              <div className="grid sm:grid-cols-3 gap-4">
                <CartaoResultado titulo="Enquadramento" valor={res.perfil.enquadramento} cor="#5C7CB8" />
                <CartaoResultado titulo="Taxa de juros" valor={`${res.perfil.taxa_anual?.toFixed(2)}% a.a.`} cor="#16284B" />
                <CartaoResultado titulo="Subsídio estimado" valor={formatBRL(res.perfil.subsidio_estimado)} cor="#c9943a" />
              </div>

              {/* Você também pode se enquadrar em (alternativas) */}
              {res.perfil.alternativas?.length > 0 && (
                <div className={`${card} p-4`}>
                  <p className="text-xs uppercase tracking-widest text-[#7b95c8] mb-2">Você também pode se enquadrar em</p>
                  <div className="flex flex-wrap gap-2">
                    {res.perfil.alternativas.map((a) => (
                      <span key={a.nome} className="text-xs bg-[#eef2f8] text-[#33415c] rounded-full px-3 py-1.5" title={a.obs || ''}>
                        {a.nome} · <b className="text-[#16284B]">{a.taxa_anual?.toFixed(2)}%</b>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className={`${card} p-6`}>
                <span className="text-xs uppercase tracking-widest text-[#5d6b86]">Parcela inicial · {res.sim.sistema} · com seguros</span>
                <div className="text-4xl md:text-5xl font-bold mt-1">{formatBRL(res.sim.parcela_inicial_com_seguros)}</div>
                <div className="text-sm text-[#5d6b86] mt-1">
                  base: {formatBRL(res.sim.parcela_inicial)}{res.sim.sistema === 'SAC' && ` · última: ${formatBRL(res.sim.parcela_final_com_seguros)}`} · financia {formatBRL(res.sim.valor_financiado)}
                </div>
              </div>

              <ImoveisSugeridos imoveis={res.perfil.imoveis_sugeridos} enviado={res.perfil.enviado_whatsapp} />

              <GraficoAmortizacao
                valorFin={Math.max(0, Number(p.valor) - Number(p.entrada) - (res.perfil.subsidio_estimado || 0))}
                taxaAnual={res.perfil.taxa_anual} meses={Number(p.prazo)} sistema={p.sistema} />

              <GraficoBancos bancos={res.sim.comparativo_bancos} />

              {/* Análise pela Ana */}
              <div className={`${card} p-6`}>
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-bold flex items-center gap-2"><Sparkles size={16} className="text-[#c9943a]" /> Análise do seu perfil <span className="text-[10px] font-normal text-[#7b95c8]">· consultor de financiamento</span></h4>
                  <button onClick={pedirAnalise} disabled={analisando}
                    className="text-white px-4 py-2 rounded-lg text-sm font-bold transition disabled:opacity-50" style={{ background: 'linear-gradient(120deg,#16284B,#2c4a82)' }}>
                    {analisando ? 'Analisando…' : 'Explicar meu enquadramento'}
                  </button>
                </div>
                {analise
                  ? <p className="text-sm text-[#33415c] leading-relaxed whitespace-pre-line">{analise}</p>
                  : <p className="text-sm text-[#7b95c8]">Nosso consultor explica em detalhe o que o seu enquadramento (MCMV, FGTS, SAC/Price) significa pra você.</p>}
              </div>

              {/* Custos */}
              {res.sim.custos_aquisicao && (
                <div className={`${card} p-5`}>
                  <div className="text-sm font-bold mb-3">Custos extras <small className="text-[#5d6b86] font-normal">(pagos uma vez, fora do financiamento)</small></div>
                  <Linha k="ITBI (~3%)" v={formatBRL(res.sim.custos_aquisicao.itbi)} />
                  <Linha k="Cartório (registro + escritura)" v={formatBRL(res.sim.custos_aquisicao.cartorio)} />
                  <Linha k="Avaliação do banco" v={formatBRL(res.sim.custos_aquisicao.avaliacao_banco)} />
                  {res.perfil.subsidio_estimado > 0 && <Linha k="Subsídio MCMV (abate do imóvel)" v={`− ${formatBRL(res.perfil.subsidio_estimado)}`} />}
                  <div className="border-t border-[#eef2f8] mt-2 pt-2">
                    <Linha k="Total na compra (entrada + custos)" v={formatBRL(res.sim.custos_aquisicao.total + Number(p.entrada))} forte />
                  </div>
                </div>
              )}

              <AvisoEstimativa>{res.perfil.aviso_estimativa || 'ESTIMATIVA — o banco confirma na análise do seu perfil.'}</AvisoEstimativa>

              <MarcarHorario p={p} enquadramento={res.perfil.enquadramento} />
            </>
          ) : (
            <div className={`${card} p-12 text-center text-[#5d6b86]`}>
              Preencha seu perfil ao lado e clique em <b className="text-[#16284B]">Analisar meu perfil</b>.
              A gente diz sua faixa, taxa e subsídio — sem chute.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CartaoResultado({ titulo, valor, cor }) {
  return (
    <div className={`${card} p-4 text-center border-t-4`} style={{ borderTopColor: cor }}>
      <p className="text-[10px] uppercase tracking-widest text-[#7b95c8] mb-1">{titulo}</p>
      <p className="text-lg font-bold leading-tight">{valor}</p>
    </div>
  );
}

const Linha = ({ k, v, forte }) => (
  <div className="flex justify-between items-center py-1 text-sm">
    <span className="text-[#5d6b86]">{k}</span>
    <b className={forte ? 'text-[#c9943a]' : 'text-[#16284B]'}>{v}</b>
  </div>
);

// Imóveis REAIS da carteira que casam com o perfil + aviso de handoff pra Priscila.
function ImoveisSugeridos({ imoveis, enviado }) {
  return (
    <div className={`${card} p-6`}>
      <h4 className="font-bold flex items-center gap-2 mb-1"><HomeIcon size={16} className="text-[#c9943a]" /> Imóveis nossos que combinam com você</h4>
      <p className="text-xs text-[#7b95c8] mb-4">Da carteira da Priscila, dentro do seu orçamento{imoveis?.length ? '' : ' — no momento não achei um que encaixe certinho, mas a Priscila tem novidades toda semana'}.</p>
      {imoveis?.length > 0 && (
        <div className="grid sm:grid-cols-2 gap-3">
          {imoveis.map((i) => (
            <a key={i.slug} href={i.url} target="_blank" rel="noreferrer"
              className="block border border-[#dde5f0] rounded-xl p-4 hover:border-[#c9943a] hover:shadow-md transition-all bg-white">
              <div className="text-sm font-bold text-[#16284B] line-clamp-2">{i.titulo}</div>
              <div className="text-xs text-[#5d6b86] mt-1">{[i.bairro, i.quartos ? `${i.quartos} quartos` : null, i.area ? `${i.area} m²` : null].filter(Boolean).join(' · ')}</div>
              <div className="text-base font-bold text-[#c9943a] mt-2">{i.preco ? formatBRL(i.preco) : 'Sob consulta'}</div>
            </a>
          ))}
        </div>
      )}
      <div className="mt-4 flex gap-3 items-start bg-[#eef4ff] border border-[#cddcf5] rounded-xl px-4 py-3 text-sm text-[#33415c]">
        <BadgeCheck size={18} className="shrink-0 mt-0.5 text-[#5C7CB8]" />
        <p className="leading-relaxed">
          {enviado
            ? 'Mandamos esse resultado e os imóveis no seu WhatsApp também. '
            : 'Pronto! Seu perfil foi enviado pra Priscila. '}
          <b>A Priscila vai te chamar pra fazer a simulação oficial</b> e te mostrar tudo de perto. 💛
        </p>
      </div>
    </div>
  );
}

function Slider({ label, value, min, max, step, onChange, fmt }) {
  return (
    <div>
      <label className="flex justify-between text-xs font-semibold text-[#5d6b86] mb-1.5">
        <span>{label}</span><strong className="text-[#16284B] text-sm">{fmt ? fmt(value) : value}</strong>
      </label>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(+e.target.value)} className="w-full accent-[#16284B]" />
    </div>
  );
}

// Marcar horário com a Priscila (handoff): IA mínima → agenda direto. Usa o cadastro do perfil.
function MarcarHorario({ p, enquadramento }) {
  const hoje = new Date().toISOString().slice(0, 10);
  const [data, setData] = useState('');
  const [turno, setTurno] = useState('manha');
  const [enviando, setEnviando] = useState(false);
  const [ok, setOk] = useState(false);
  const [erro, setErro] = useState('');

  async function marcar() {
    setErro('');
    if (!data) { setErro('Escolha um dia.'); return; }
    if (p.nome.trim().length < 2 || p.contato.replace(/\D/g, '').length < 10) { setErro('Preencha nome e WhatsApp lá em cima.'); return; }
    setEnviando(true);
    try {
      await agendarVisita({
        nome: p.nome.trim(), telefone: p.contato.replace(/\D/g, ''), data_preferida: data, turno,
        bairro: p.bairro || null,
        observacoes: `Quer atendimento sobre financiamento (${enquadramento}). Veio do simulador.`,
      });
      setOk(true);
    } catch { setErro('Não consegui marcar agora. A Priscila vai te chamar no WhatsApp.'); }
    finally { setEnviando(false); }
  }

  if (ok) {
    return (
      <div className="flex gap-3 items-start bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-4 text-sm text-emerald-800">
        <BadgeCheck size={20} className="shrink-0 mt-0.5" />
        <p className="leading-relaxed"><b>Horário solicitado!</b> A Priscila vai confirmar com você no WhatsApp o dia e a hora certinhos. 💛</p>
      </div>
    );
  }

  return (
    <div className={`${card} p-6`}>
      <h4 className="font-bold flex items-center gap-2 mb-1">📅 Marcar horário com a Priscila</h4>
      <p className="text-xs text-[#7b95c8] mb-4">Quer conversar com a Priscila? Escolha um dia e o turno — ela confirma com você.</p>
      <div className="grid sm:grid-cols-2 gap-3">
        <div><label className={labelCls}>Melhor dia</label>
          <input type="date" min={hoje} value={data} onChange={(e) => setData(e.target.value)} className={inputCls} /></div>
        <div><label className={labelCls}>Turno</label>
          <div className="inline-flex w-full bg-[#eef2f8] rounded-lg p-1">
            {[['manha', 'Manhã'], ['tarde', 'Tarde'], ['noite', 'Noite']].map(([v, l]) => (
              <button key={v} onClick={() => setTurno(v)}
                className={`flex-1 py-1.5 rounded-md text-xs font-bold transition-colors ${turno === v ? 'text-[#16284B] bg-white shadow-sm' : 'text-[#5d6b86]'}`}>{l}</button>
            ))}
          </div>
        </div>
      </div>
      <button onClick={marcar} disabled={enviando}
        className="w-full mt-4 text-[#16284B] font-bold py-3.5 rounded-xl text-sm uppercase tracking-widest transition-all hover:shadow-[0_8px_24px_-6px_rgba(201,148,58,0.5)] disabled:opacity-50" style={gold}>
        {enviando ? 'Marcando…' : 'Quero falar com a Priscila'}
      </button>
      {erro && <p className="text-sm text-red-600 mt-2">{erro}</p>}
    </div>
  );
}

// Chart.js: evolução da parcela (linha) — calculada no cliente só pra ilustrar a curva.
function GraficoAmortizacao({ valorFin, taxaAnual, meses, sistema }) {
  const ref = useRef(null), inst = useRef(null);
  useEffect(() => {
    if (!ref.current || !valorFin || !taxaAnual) return;
    const i = Math.pow(1 + taxaAnual / 100, 1 / 12) - 1;
    const amortConst = valorFin / meses;
    const parcelaPrice = valorFin * (i / (1 - Math.pow(1 + i, -meses)));
    let saldo = valorFin; const labels = [], parc = [], juros = [];
    const step = Math.max(1, Math.floor(meses / 20));
    for (let m = 1; m <= meses; m++) {
      const jm = saldo * i; let pm, am;
      if (sistema === 'PRICE') { pm = parcelaPrice; am = pm - jm; } else { am = amortConst; pm = am + jm; }
      if (m === 1 || m % step === 0 || m === meses) { labels.push(`M${m}`); parc.push(pm.toFixed(0)); juros.push(jm.toFixed(0)); }
      saldo -= am;
    }
    inst.current?.destroy();
    inst.current = new Chart(ref.current, {
      type: 'line',
      data: {
        labels, datasets: [
          { label: `Parcela (${sistema})`, data: parc, borderColor: '#16284B', backgroundColor: 'rgba(22,40,75,0.10)', fill: true, tension: 0.3, pointRadius: 0 },
          { label: 'Fração de juros', data: juros, borderColor: '#c9943a', borderDash: [5, 5], fill: false, tension: 0.3, pointRadius: 0 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } },
        scales: { y: { beginAtZero: true, ticks: { callback: (v) => 'R$ ' + Number(v).toLocaleString('pt-BR') } } },
      },
    });
    return () => inst.current?.destroy();
  }, [valorFin, taxaAnual, meses, sistema]);
  return (
    <div className={`${card} p-5`}>
      <h4 className="font-bold text-sm mb-1">Evolução da parcela ({sistema})</h4>
      <p className="text-xs text-[#7b95c8] mb-3">{sistema === 'SAC' ? 'Parcelas decrescentes.' : 'Parcela fixa.'} Sem TR e seguros no gráfico — estimativa.</p>
      <div style={{ height: 260 }}><canvas ref={ref} /></div>
    </div>
  );
}

// Chart.js: comparativo de bancos (barras) — taxa a.a. por banco, menor em destaque.
function GraficoBancos({ bancos }) {
  const ref = useRef(null), inst = useRef(null);
  useEffect(() => {
    if (!ref.current || !bancos?.length) return;
    const labels = bancos.map((b) => b.banco);
    const dados = bancos.map((b) => b.taxa_anual);
    const cores = bancos.map((b, idx) => (idx === 0 ? '#c9943a' : '#5C7CB8'));
    inst.current?.destroy();
    inst.current = new Chart(ref.current, {
      type: 'bar',
      data: { labels, datasets: [{ label: 'Taxa a.a. (%)', data: dados, backgroundColor: cores, borderRadius: 6 }] },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `${Number(c.parsed.x).toFixed(2)}% a.a.` } } },
        scales: { x: { ticks: { callback: (v) => v + '%' } } },
      },
    });
    return () => inst.current?.destroy();
  }, [bancos]);
  return (
    <div className={`${card} p-5`}>
      <h4 className="font-bold text-sm mb-1">Comparativo entre bancos (SBPE + Pró-Cotista)</h4>
      <p className="text-xs text-[#7b95c8] mb-3">Menor taxa em dourado. O Pró-Cotista exige FGTS. Taxas de tabela — estimativa.</p>
      <div style={{ height: Math.max(220, (bancos?.length || 6) * 34) }}><canvas ref={ref} /></div>
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// AVALIAÇÃO DE IMÓVEL (AVM)
// ═════════════════════════════════════════════════════════════════════════════
const TIPOS = ['casa', 'apartamento', 'cobertura', 'terreno', 'comercial'];
const PADROES = [['simples', 'Simples'], ['medio', 'Médio'], ['alto', 'Alto'], ['luxo', 'Luxo']];
const ESTADOS = [['reformado', 'Reformado'], ['bom', 'Bom'], ['regular', 'Regular'], ['precisa_reforma', 'Precisa reforma']];
const IDADES = [['novo', 'Novo'], ['0_10', '0–10 anos'], ['10_20', '10–20 anos'], ['20_mais', '20+ anos']];

function Avaliacao() {
  const [bairros, setBairros] = useState([]);
  const [f, setF] = useState({ bairro: '', tipo: 'casa', area_util: 90, quartos: 3, suites: 1, vagas: 1, padrao: 'medio', estado: 'bom', idade: '0_10', nome: '', contato: '', email: '' });
  const [res, setRes] = useState(null);
  const [panorama, setPanorama] = useState([]);
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(false);
  // "Token": quem ja se cadastrou uma vez pode ver o resultado na tela nas proximas.
  const [liberado, setLiberado] = useState(() => { try { return localStorage.getItem('pv_avaliou') === '1'; } catch { return false; } });
  const [soZap, setSoZap] = useState(false); // 1a vez: resultado foi so pro WhatsApp

  useEffect(() => {
    getBairrosAvaliacao().then((bs) => { setBairros(bs); setF((s) => ({ ...s, bairro: s.bairro || bs[0] || '' })); }).catch(() => {});
    getPanorama().then(setPanorama).catch(() => {});
  }, []);

  const set = (k) => (e) => setF((s) => ({ ...s, [k]: e.target.value }));

  async function avaliar() {
    setErro('');
    // Gate de lead: nome + WhatsApp obrigatórios; e-mail OPCIONAL.
    if (f.nome.trim().length < 2 || f.contato.replace(/\D/g, '').length < 10) {
      setErro('Preencha seu nome e WhatsApp — é por lá que a Priscila te envia a avaliação.');
      return;
    }
    setCarregando(true); setRes(null);
    try {
      const data = await avaliarImovel({
        bairro: f.bairro, tipo: f.tipo, area_util: Number(f.area_util), quartos: Number(f.quartos),
        suites: Number(f.suites), vagas: Number(f.vagas), padrao: f.padrao, estado: f.estado, idade: f.idade,
        nome: f.nome.trim(), contato: f.contato.replace(/\D/g, ''), email: f.email.trim() || null,
      });
      setRes(data);
      trackLead('avaliacao'); // conversão: GA4 generate_lead + Meta Lead
      // 1a vez: manda pro WhatsApp e NAO mostra o detalhe na tela (gera a conversa/lead).
      // Depois de cadastrada, libera o resultado na tela nas proximas vezes ("token").
      if (!liberado) {
        setSoZap(!!data.enviado_whatsapp); // se o zap enviou, esconde a tela; se falhou, mostra como reserva
        try { localStorage.setItem('pv_avaliou', '1'); } catch {}
        setLiberado(true);
      } else {
        setSoZap(false);
      }
    } catch (e) { setErro(String(e.message || e)); }
    finally { setCarregando(false); }
  }

  return (
    <div className="grid lg:grid-cols-5 gap-8">
      <div className={`lg:col-span-2 ${card} p-6 space-y-4 h-fit`}>
        <div className="grid grid-cols-2 gap-3">
          <div><label className={labelCls}>Bairro</label>
            <select value={f.bairro} onChange={set('bairro')} className={inputCls}>{bairros.map((b) => <option key={b} value={b}>{b}</option>)}</select></div>
          <div><label className={labelCls}>Tipo</label>
            <select value={f.tipo} onChange={set('tipo')} className={inputCls}>{TIPOS.map((t) => <option key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</option>)}</select></div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className={labelCls}>Área útil (m²)</label><input type="number" min={1} value={f.area_util} onChange={set('area_util')} className={inputCls} /></div>
          <div><label className={labelCls}>Quartos</label><input type="number" min={0} value={f.quartos} onChange={set('quartos')} className={inputCls} /></div>
          <div><label className={labelCls}>Suítes</label><input type="number" min={0} value={f.suites} onChange={set('suites')} className={inputCls} /></div>
          <div><label className={labelCls}>Vagas</label><input type="number" min={0} value={f.vagas} onChange={set('vagas')} className={inputCls} /></div>
        </div>
        <div><label className={labelCls}>Padrão de acabamento</label>
          <div className="grid grid-cols-4 gap-1.5">
            {PADROES.map(([v, l]) => (
              <button key={v} onClick={() => setF((s) => ({ ...s, padrao: v }))}
                className={`py-2 rounded-lg text-xs font-bold transition-colors ${f.padrao === v ? 'text-[#16284B]' : 'bg-[#eef2f8] text-[#5d6b86]'}`}
                style={f.padrao === v ? gold : {}}>{l}</button>
            ))}
          </div>
        </div>
        <div><label className={labelCls}>Estado</label><select value={f.estado} onChange={set('estado')} className={inputCls}>{ESTADOS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></div>
        <div><label className={labelCls}>Idade do imóvel</label><select value={f.idade} onChange={set('idade')} className={inputCls}>{IDADES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></div>

        <div className="border-t border-[#eef2f8] pt-4 space-y-3">
          <div className="flex items-center gap-2 text-[#16284B] font-bold text-sm"><User size={16} className="text-[#c9943a]" /> Enviaremos seu resultado por WhatsApp ou e-mail</div>
          <div><label className={labelCls}>Nome</label><input value={f.nome} onChange={set('nome')} placeholder="Seu nome" className={inputCls} /></div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className={labelCls}>WhatsApp</label><input value={f.contato} onChange={set('contato')} type="tel" placeholder="(77) 9 9999-9999" className={inputCls} /></div>
            <div><label className={labelCls}>E-mail <small className="text-[#7b95c8]">(opcional)</small></label><input value={f.email} onChange={set('email')} type="email" placeholder="voce@email.com" className={inputCls} /></div>
          </div>
        </div>

        <button onClick={avaliar} disabled={carregando || !f.bairro}
          className="w-full py-3.5 rounded-xl text-sm font-bold uppercase tracking-widest text-[#16284B] transition-all hover:shadow-[0_8px_24px_-6px_rgba(201,148,58,0.5)] disabled:opacity-50" style={gold}>
          {carregando ? 'Avaliando…' : 'Quero minha avaliação'}
        </button>
        {erro && <p className="text-sm text-red-600">{erro}</p>}
      </div>

      <div className="lg:col-span-3 space-y-5">
        {res && soZap ? (
          <div className={`${card} p-8 text-center space-y-3`}>
            <div className="text-4xl">📲</div>
            <h4 className="font-bold text-xl text-[#16284B]">Enviamos sua avaliação no seu WhatsApp!</h4>
            <p className="text-sm text-[#5d6b86] max-w-sm mx-auto">Confere lá — a Priscila acompanha você de perto pra chegar no valor certo. E agora você já pode simular <strong>à vontade aqui na tela</strong>! 💛</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center pt-1">
              <button onClick={() => { setRes(null); setSoZap(false); }} className="border border-[#16284B] text-[#16284B] font-bold py-3 px-6 rounded-xl text-sm uppercase tracking-widest hover:bg-[#f5f0e8] transition-all inline-flex items-center justify-center gap-2">
                Fazer outra avaliação
              </button>
              <button onClick={abrirAna} className="text-[#16284B] font-bold py-3 px-6 rounded-xl text-sm uppercase tracking-widest transition-all hover:shadow-[0_8px_24px_-6px_rgba(201,148,58,0.5)] inline-flex items-center justify-center gap-2" style={gold}>
                <Sparkles size={18} /> Falar com a Priscila
              </button>
            </div>
          </div>
        ) : res ? (
          <>
            <div className={`${card} p-6`}>
              <span className="text-xs uppercase tracking-widest text-[#5d6b86]">Valor estimado · {res.bairro_normalizado}</span>
              <div className="text-4xl md:text-5xl font-bold mt-1">{formatBRL(res.valor_central)}</div>
              <ReguaValor min={res.valor_minimo} central={res.valor_central} max={res.valor_maximo} />
              <div className="text-sm text-[#5d6b86] mt-2">Faixa: {formatBRL(res.valor_minimo)} — {formatBRL(res.valor_maximo)} · confiança {res.confianca}</div>
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className={`${card} p-5`}>
                <div className="text-sm font-bold mb-3">Base do cálculo</div>
                <Linha k="R$/m² do bairro" v={formatBRL(res.m2_base)} />
                <Linha k="R$/m² ajustado" v={formatBRL(res.m2_ajustado)} />
                <Linha k="Área útil" v={`${f.area_util} m²`} />
              </div>
              <div className={`${card} p-5`}>
                <div className="text-sm font-bold mb-3 flex items-center gap-1.5"><TrendingUp size={15} className="text-[#c9943a]" /> Potencial de aluguel</div>
                <Linha k="Aluguel estimado/mês" v={formatBRL(res.aluguel_estimado)} />
                <Linha k="Rentabilidade anual" v={`${res.aluguel_yield_anual_pct}%`} />
                <Linha k="Líquido aprox./mês" v={formatBRL(res.aluguel_liquido_estimado)} />
              </div>
            </div>
            <PanoramaBairros dados={panorama} destaque={res.bairro_normalizado} />
            <AvisoEstimativa>
              <strong>ESTIMATIVA.</strong> Referência por dados de mercado de Vitória da Conquista — não substitui a
              avaliação presencial. O preço real varia por rua, ponto e conservação. A Priscila faz a avaliação certeira.
            </AvisoEstimativa>
            <button onClick={abrirAna} className="w-full text-[#16284B] font-bold py-3.5 rounded-xl text-sm uppercase tracking-widest transition-all hover:shadow-[0_8px_24px_-6px_rgba(201,148,58,0.5)] flex items-center justify-center gap-2" style={gold}>
              <Sparkles size={18} /> Quero a avaliação oficial com a Priscila
            </button>
          </>
        ) : (
          <div className={`${card} p-12 text-center text-[#5d6b86]`}>Preencha os dados do imóvel e clique em avaliar.</div>
        )}
      </div>
    </div>
  );
}

function ReguaValor({ min, central, max }) {
  const span = Math.max(1, max - min);
  const pos = Math.max(0, Math.min(100, ((central - min) / span) * 100));
  return (
    <div className="mt-4">
      <div className="relative h-2 rounded-full" style={{ background: 'linear-gradient(90deg,#5C7CB8 0%,#c9943a 50%,#5C7CB8 100%)' }}>
        <div className="absolute -top-1 w-4 h-4 rounded-full bg-[#c9943a] border-2 border-white shadow -translate-x-1/2" style={{ left: `${pos}%` }} />
      </div>
    </div>
  );
}

function PanoramaBairros({ dados, destaque }) {
  if (!dados?.length) return null;
  const norm = (s) => (s || '').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').trim();
  const alvo = norm(destaque);
  const lista = dados.slice(0, 12);
  const max = Math.max(...lista.map((d) => d.m2));
  return (
    <div className={`${card} p-5`}>
      <div className="flex justify-between items-center mb-3">
        <span className="text-sm font-bold">Preço do m² por bairro</span>
        <span className="text-xs text-[#7b95c8]">Vitória da Conquista · construído</span>
      </div>
      <div className="space-y-1.5">
        {lista.map((d) => {
          const eAlvo = norm(d.bairro) === alvo;
          return (
            <div key={d.bairro} className="flex items-center gap-3">
              <div className={`w-28 shrink-0 text-xs truncate ${eAlvo ? 'text-[#c9943a] font-bold' : 'text-[#33415c]'}`}>{d.bairro}</div>
              <div className="flex-1 h-5 bg-[#eef2f8] rounded overflow-hidden">
                <div className="h-full rounded" style={{ width: `${(d.m2 / max) * 100}%`, background: eAlvo ? 'linear-gradient(120deg,#c9943a,#e8b55a)' : '#5C7CB8' }} />
              </div>
              <div className={`w-20 shrink-0 text-right text-xs ${eAlvo ? 'text-[#c9943a] font-bold' : 'text-[#5d6b86]'}`}>{formatBRL(d.m2)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
