import React, { useState, useEffect, useRef } from 'react';
import { Search, Menu, X, MapPin, BedDouble, Car, Maximize, ArrowRight, Sparkles, BrainCircuit, ChevronRight, ChevronLeft } from 'lucide-react';
import { getImoveis, getEmpreendimentos, abrirAna, enviarLeadVendedor, trackLead } from './api';

// Linha que passa sozinha (marquee). reverse = sentido contrário (pra alternar entre linhas).
// Pausa ao passar o mouse (desktop) e por alguns segundos ao tocar (celular) — pra dar
// tempo de clicar nas setinhas de foto dos cards.
function MarqueeRow({ children, reverse = false }) {
  const trackRef = useRef(null);
  const lento = useRef(false); // true = desacelerado (pessoa interagindo) — NUNCA para de vez
  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    const sentido = reverse ? 1 : -1;   // -1 = direita→esquerda · 1 = esquerda→direita
    const V_NORMAL = 1.5 * sentido;     // px/frame (~90px/s)
    const V_LENTA = 0.18 * sentido;     // bem devagar ao interagir (fácil clicar as setinhas), mas continua andando
    let pos = null;
    let vel = 0;
    let raf;
    const passo = () => {
      const meio = track.scrollWidth / 2 || 1;
      if (pos === null) pos = reverse ? -meio : 0;
      vel += ((lento.current ? V_LENTA : V_NORMAL) - vel) * 0.06; // transição suave, sem pulo
      pos += vel;
      if (pos <= -meio) pos += meio;
      else if (pos >= 0) pos -= meio;
      track.style.transform = `translateX(${pos}px)`;
      raf = requestAnimationFrame(passo);
    };
    raf = requestAnimationFrame(passo);
    return () => cancelAnimationFrame(raf);
  }, [reverse, children]);
  return (
    <div
      className="w-full overflow-hidden"
      onMouseEnter={() => (lento.current = true)}
      onMouseLeave={() => (lento.current = false)}
      onTouchStart={() => (lento.current = true)}
      onTouchEnd={() => (lento.current = false)}
    >
      <div ref={trackRef} className="flex gap-10 w-max will-change-transform">
        {children}
      </div>
    </div>
  );
}

// Slider de fotos dentro do card: setinhas pra passar TODAS as fotos do imóvel/empreendimento.
function FotoSlider({ fotos, alt, badge }) {
  const lista = (fotos && fotos.length) ? fotos : [];
  const [idx, setIdx] = useState(0);
  const varias = lista.length > 1;
  const ir = (e, d) => { e.stopPropagation(); setIdx((i) => (i + d + lista.length) % lista.length); };
  return (
    <div className="relative overflow-hidden aspect-[4/3] mb-6 rounded-t-xl bg-[#EEF2F8]">
      {lista.length ? (
        <img src={lista[idx].thumb} alt={alt} loading="lazy" className="w-full h-full object-cover transition-transform duration-700 ease-in-out group-hover:scale-105" />
      ) : (
        <div className="w-full h-full flex items-center justify-center text-[#5d6b86] text-xs uppercase tracking-widest">Sem foto</div>
      )}
      {badge}
      {varias && (
        <>
          <button onClick={(e) => ir(e, -1)} aria-label="Foto anterior" className="absolute left-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-white/85 hover:bg-white text-[#16284B] flex items-center justify-center shadow-md transition-colors z-20">
            <ChevronLeft size={18} />
          </button>
          <button onClick={(e) => ir(e, 1)} aria-label="Próxima foto" className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-white/85 hover:bg-white text-[#16284B] flex items-center justify-center shadow-md transition-colors z-20">
            <ChevronRight size={18} />
          </button>
          <div className="absolute bottom-3 right-3 bg-black/55 text-white text-[11px] px-2 py-0.5 rounded-full z-20">{idx + 1}/{lista.length}</div>
        </>
      )}
      <div className="absolute inset-0 bg-[#16284B]/0 group-hover:bg-[#16284B]/10 transition-colors duration-500 pointer-events-none"></div>
    </div>
  );
}

// Card de imóvel do carrossel
function ImovelCard({ prop, onClick }) {
  const fotos = (prop.fotos && prop.fotos.length) ? prop.fotos : (prop.capaUrl ? [{ thumb: prop.capaUrl }] : []);
  return (
    <div className="w-[80vw] sm:w-[360px] flex-shrink-0 group cursor-pointer" onClick={onClick}>
      <FotoSlider fotos={fotos} alt={prop.titulo} badge={
        <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-4 py-1 text-[10px] tracking-widest uppercase text-[#16284B] font-semibold rounded-full shadow-sm z-10">{prop.bairro}</div>
      } />
      <div className="space-y-3 px-2">
        <h3 className="font-serif text-2xl text-[#16284B] group-hover:text-[#c9943a] transition-colors line-clamp-2">{prop.titulo}</h3>
        <p className="text-xl text-[#5d6b86] font-light">{prop.precoFmt}{prop.precoSufixo && <span className="text-sm">{prop.precoSufixo}</span>}</p>
        <div className="flex items-center gap-5 text-sm text-[#5d6b86] border-t border-[#dde5f0] pt-4 mt-4">
          {prop.suites > 0 ? (<span className="flex items-center gap-1.5"><BedDouble size={16} className="text-[#c9943a]"/> {prop.suites} Suítes</span>) : prop.quartos > 0 ? (<span className="flex items-center gap-1.5"><BedDouble size={16} className="text-[#c9943a]"/> {prop.quartos} Quartos</span>) : null}
          {prop.vagas > 0 && (<span className="flex items-center gap-1.5"><Car size={16} className="text-[#c9943a]"/> {prop.vagas} Vagas</span>)}
          {prop.area > 0 && (<span className="flex items-center gap-1.5"><Maximize size={16} className="text-[#c9943a]"/> {prop.area} m²</span>)}
        </div>
      </div>
    </div>
  );
}

// Card de empreendimento do carrossel
function EmpreendimentoCard({ emp, onClick }) {
  const fotos = (emp.fotos && emp.fotos.length) ? emp.fotos : (emp.capaUrl ? [{ thumb: emp.capaUrl }] : []);
  return (
    <div className="w-[80vw] sm:w-[360px] flex-shrink-0 group cursor-pointer" onClick={onClick}>
      <FotoSlider fotos={fotos} alt={emp.nome} badge={
        emp.status ? <div className="absolute top-4 left-4 bg-[#16284B] text-white px-4 py-1 text-[10px] tracking-widest uppercase font-semibold rounded-full shadow-sm z-10">{emp.status}</div> : null
      } />
      <div className="space-y-2 px-2">
        <h3 className="font-serif text-2xl text-[#16284B] group-hover:text-[#c9943a] transition-colors line-clamp-2">{emp.nome}</h3>
        <p className="text-sm text-[#5d6b86] flex items-center gap-1.5"><MapPin size={14} className="text-[#c9943a]"/> {emp.bairro}{emp.construtora ? ` · ${emp.construtora}` : ''}</p>
      </div>
    </div>
  );
}

export default function Home({ onPropertyClick, onLancamentosClick, onLoginClick, onCaptacaoClick, onSobreClick, onBuscaClick, onCalculadorasClick }) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [buscaHero, setBuscaHero] = useState('');
  const [properties, setProperties] = useState([]);
  const [empreendimentos, setEmpreendimentos] = useState([]);
  const [loadingProps, setLoadingProps] = useState(true);
  const [erroProps, setErroProps] = useState(false);

  // Avaliação grátis (captura de lead): cliente cadastra o imóvel + contato; resultado vai no WhatsApp.
  const [av, setAv] = useState({ tipo: 'Casa', bairro: '', area: '', quartos: '', nome: '', whatsapp: '', email: '' });
  const [avEnviando, setAvEnviando] = useState(false);
  const [avEnviado, setAvEnviado] = useState(false);
  const [avErro, setAvErro] = useState('');

  const setAvCampo = (k) => (e) => setAv((s) => ({ ...s, [k]: e.target.value }));

  async function avaliar() {
    setAvErro('');
    if (av.nome.trim().length < 2 || av.whatsapp.replace(/\D/g, '').length < 10) {
      setAvErro('Preencha seu nome e um WhatsApp válido (com DDD) pra gente te enviar a avaliação.');
      return;
    }
    setAvEnviando(true);
    try {
      await enviarLeadVendedor({
        nome: av.nome.trim(),
        telefone: av.whatsapp.replace(/\D/g, ''),
        bairro: av.bairro.trim(),
        tipo: av.tipo,
        area: av.area,
        quartos: av.quartos,
        observacoes: `AVALIAÇÃO solicitada pelo site.${av.email ? ' Email: ' + av.email.trim() : ''}`,
      });
      setAvEnviado(true);
      trackLead('avaliacao');
    } catch {
      setAvErro('Não consegui enviar agora. Tenta de novo, ou fala com a Ana aqui.');
    } finally {
      setAvEnviando(false);
    }
  }

  // Busca os imóveis reais da carteira (backend PVSCELOS)
  useEffect(() => {
    getImoveis()
      .then((lista) => setProperties(lista))
      .catch(() => setErroProps(true))
      .finally(() => setLoadingProps(false));
    getEmpreendimentos()
      .then((lista) => setEmpreendimentos(lista))
      .catch(() => setEmpreendimentos([]));
  }, []);

  // Efeito para mudar o estilo da navbar ao rolar a página
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Linhas do carrossel por categoria
  const vendaList = properties.filter((p) => (p.finalidade || 'venda') !== 'aluguel');
  const aluguelList = properties.filter((p) => (p.finalidade || 'venda') === 'aluguel');
  // Repete a lista até ter no mínimo `min` cards (linha curta não enche a tela / loop feio)
  const repetir = (lista, min = 8) => {
    if (!lista.length) return [];
    const out = [];
    while (out.length < min) out.push(...lista);
    return out;
  };

  return (
    <div className="min-h-screen bg-[#FBFCFE] font-sans antialiased selection:bg-[#c9943a] selection:text-white">
      {}
      {/* Importando as fontes elegantes (Playfair e Inter) e a animação do carrossel */}
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Inter', sans-serif; }
        .bg-grad-gold { background: linear-gradient(120deg, #c9943a, #e8b55a); }
        .text-grad-gold { 
          background: linear-gradient(120deg, #c9943a, #e8b55a); 
          -webkit-background-clip: text; 
          -webkit-text-fill-color: transparent; 
        }
        /* Animação matemática para loop infinito perfeito */
        @keyframes scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(calc(-50% - 1.25rem)); }
        }
        .animate-scroll {
          animation: scroll 40s linear infinite;
        }
        /* Mesma animação, sentido contrário (linhas alternadas) */
        .animate-scroll-rev {
          animation: scroll 40s linear infinite reverse;
        }
        /* Pausa a animação ao passar o mouse */
        .animate-scroll:hover, .animate-scroll-rev:hover {
          animation-play-state: paused;
        }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}} />

      {}
      <nav className={`fixed w-full z-50 transition-all duration-500 ${isScrolled ? 'bg-white/90 backdrop-blur-md border-b border-[#dde5f0] py-4' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          {/* Logo da marca (selo da Priscila) — BRANCA, BEM grande, transparente, tamanho FIXO (nao encolhe) */}
          <img
            src={`${import.meta.env.BASE_URL}${isScrolled ? 'selo.png' : 'selo-branco.png'}`}
            alt="Priscila Vasconcelos Imobiliária"
            className="h-28 md:h-36 object-contain opacity-90 [filter:drop-shadow(0_2px_8px_rgba(0,0,0,0.25))]"
          />

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-10">
            <a href="#" onClick={(e) => { e.preventDefault(); onBuscaClick({ finalidade: 'venda' }); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Imóveis</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onLancamentosClick(); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Empreendimentos</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onBuscaClick({ finalidade: 'aluguel' }); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Aluguel</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onCalculadorasClick(); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Simuladores</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onCaptacaoClick(); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Anunciar</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onSobreClick(); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>A Marca</a>
            
            <button onClick={onLoginClick} className={`px-6 py-2.5 rounded-none border text-xs tracking-widest uppercase transition-all duration-300 ${isScrolled ? 'border-[#16284B] text-[#16284B] hover:bg-[#16284B] hover:text-white' : 'border-white text-white hover:bg-white hover:text-[#16284B]'}`}>
              Área do Cliente
            </button>
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className={isScrolled ? 'text-[#16284B]' : 'text-white'} /> : <Menu className={isScrolled ? 'text-[#16284B]' : 'text-white'} />}
          </button>
        </div>

        {/* Menu mobile (gaveta) — abre ao tocar nos tracinhos */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-[#16284B] border-t border-white/10 px-6 py-6 space-y-1 shadow-2xl">
            {[
              { label: 'Imóveis', fn: () => onBuscaClick({ finalidade: 'venda' }) },
              { label: 'Empreendimentos', fn: onLancamentosClick },
              { label: 'Para Alugar', fn: () => onBuscaClick({ finalidade: 'aluguel' }) },
              { label: 'Simuladores', fn: onCalculadorasClick },
              { label: 'Anunciar Imóvel', fn: onCaptacaoClick },
              { label: 'A Marca', fn: onSobreClick },
            ].map((it) => (
              <button
                key={it.label}
                onClick={() => { it.fn(); setIsMobileMenuOpen(false); }}
                className="block w-full text-left text-white text-base py-3 border-b border-white/10 hover:text-[#c9943a] transition-colors"
              >
                {it.label}
              </button>
            ))}
            <button
              onClick={() => { onLoginClick(); setIsMobileMenuOpen(false); }}
              className="mt-5 w-full border border-white text-white py-3 text-xs tracking-widest uppercase hover:bg-white hover:text-[#16284B] transition-all"
            >
              Área do Cliente
            </button>
          </div>
        )}
      </nav>

      {}
      <header className="relative h-screen min-h-[700px] flex items-center justify-center overflow-hidden">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=2000" 
            alt="Imóvel à venda em Vitória da Conquista"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-[#16284B]/40 mix-blend-multiply"></div>
          {/* Efeito sutil de gradiente simulando a luz/neblina */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#16284B]/80 via-transparent to-transparent"></div>
        </div>

        <div className="relative z-10 text-center text-white px-6 max-w-4xl mx-auto mt-20">
          <span className="text-xs uppercase tracking-[0.4em] mb-6 block text-[#e8b55a]">
            Vitória da Conquista & Região
          </span>
          <h1 className="font-serif text-4xl md:text-7xl font-light mb-8 leading-[1.1]">
            Imóvel é confiança. <br className="hidden md:block" /> E confiança <span className="italic text-[#c9943a]">tem nome.</span>
          </h1>
          <p className="font-sans font-light text-lg md:text-xl text-white/90 mb-12 max-w-2xl mx-auto leading-relaxed">
A corretora certa pra cada momento: compra, venda e aluguel em todos os bairros de Vitória da Conquista — do primeiro imóvel ao da vida toda.
          </p>

          {/* Search Bar Elegante */}
          <div className="max-w-2xl mx-auto bg-white/10 backdrop-blur-md border border-white/20 p-2 rounded-full flex items-center shadow-2xl">
            <input
              type="text"
              value={buscaHero}
              onChange={(e) => setBuscaHero(e.target.value)}
              placeholder="Busque por bairro, condomínio ou referência..."
              onKeyDown={(e) => { if (e.key === 'Enter') onBuscaClick(buscaHero); }}
              className="bg-transparent w-full px-6 text-white placeholder-white/60 focus:outline-none font-light"
            />
            <button onClick={() => onBuscaClick(buscaHero)} className="bg-grad-gold p-4 rounded-full text-[#16284B] hover:opacity-90 transition-opacity">
              <Search size={20} />
            </button>
          </div>
        </div>
      </header>

      {}
      <section className="py-32 px-6 bg-[#f5f0e8] relative">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-16 md:gap-24">
          <div className="w-full md:w-1/2">
            <img
              src="/assets/priscila-sentada.jpg"
              alt="Priscila Vasconcelos"
              className="w-full h-auto aspect-[4/5] object-cover object-top rounded-t-full shadow-2xl shadow-[#16284B]/10"
            />
          </div>
          <div className="w-full md:w-1/2 space-y-8">
            <h2 className="font-serif text-4xl md:text-5xl text-[#16284B] font-light leading-tight">
              A Arte do <br/><span className="text-[#c9943a] italic">Morar Bem</span>
            </h2>
            <div className="w-12 h-[1px] bg-[#c9943a]"></div>
            <p className="text-[#5d6b86] text-lg font-light leading-relaxed">
              Nossa carteira é diversa: casas, apartamentos, terrenos, imóveis comerciais e empreendimentos, em todos os bairros de Vitória da Conquista. E a gente cuida de tudo — a <span className="text-[#16284B] font-medium">compra</span>, a <span className="text-[#16284B] font-medium">venda</span> e o <span className="text-[#16284B] font-medium">aluguel</span> do seu imóvel — com atenção de verdade, do começo ao fim.
            </p>
            <p className="text-[#5d6b86] text-lg font-light leading-relaxed">
              O foco é <span className="text-[#16284B] font-medium">você</span>. Seja o primeiro imóvel, a casa pra família crescer, um ponto pra empreender ou um <span className="text-[#16284B] font-medium">investimento que rende</span>, a Priscila te ajuda a encontrar o lugar certo — porque é aqui que sua próxima história começa.
            </p>
            <button onClick={onSobreClick} className="group flex items-center gap-4 mt-8 text-[#16284B] font-medium tracking-wide hover:text-[#c9943a] transition-colors">
              <span className="uppercase text-sm tracking-widest border-b border-[#16284B] group-hover:border-[#c9943a] pb-1 transition-colors">Conheça nossa História</span>
              <ArrowRight size={18} className="transform group-hover:translate-x-2 transition-transform" />
            </button>
          </div>
        </div>
      </section>

      {}
      <section className="py-32 bg-[#FBFCFE] overflow-hidden relative">
        {/* Container do Carrossel */}
        <div className="w-full relative group/carousel">
          
          {/* Sombras laterais elegantes (Fade) para o carrossel sumir suavemente nas bordas */}
          <div className="absolute top-0 left-0 w-16 md:w-48 h-full bg-gradient-to-r from-[#FBFCFE] to-transparent z-10 pointer-events-none"></div>
          <div className="absolute top-0 right-0 w-16 md:w-48 h-full bg-gradient-to-l from-[#FBFCFE] to-transparent z-10 pointer-events-none"></div>

          {/* Trilho Animado do Carrossel — imóveis REAIS da carteira (backend) */}
          {loadingProps ? (
            <div className="flex w-max gap-10 px-10">
              {[0, 1, 2].map((i) => (
                <div key={i} className="w-[85vw] md:w-[400px] flex-shrink-0">
                  <div className="aspect-[4/3] mb-6 rounded-t-xl bg-[#EEF2F8] animate-pulse"></div>
                  <div className="h-6 w-2/3 bg-[#EEF2F8] rounded mb-3 animate-pulse"></div>
                  <div className="h-5 w-1/3 bg-[#EEF2F8] rounded animate-pulse"></div>
                </div>
              ))}
            </div>
          ) : erroProps || (vendaList.length === 0 && empreendimentos.length === 0) ? (
            <p className="text-center text-[#5d6b86] font-light py-12 px-6">
              Não foi possível carregar os imóveis agora. Tente novamente em instantes.
            </p>
          ) : (
            <div className="space-y-12">
              {/* Linha 1 — À VENDA (passa pra um lado) */}
              {vendaList.length > 0 && (
                <div>
                  <div className="max-w-7xl mx-auto px-6 md:px-10 mb-6 flex flex-col md:flex-row md:justify-between md:items-end gap-3">
                    <div>
                      <span className="text-[#c9943a] text-xs font-bold tracking-[0.2em] uppercase mb-2 block">Em destaque</span>
                      <h2 className="font-serif text-3xl md:text-4xl text-[#16284B]">Imóveis em Destaque</h2>
                    </div>
                    <button onClick={() => onBuscaClick({ finalidade: 'venda' })} className="text-sm uppercase tracking-widest text-[#5d6b86] hover:text-[#c9943a] transition-colors flex items-center gap-2 self-start md:self-auto">
                      Ver Catálogo <ChevronRight size={16} />
                    </button>
                  </div>
                  <MarqueeRow reverse={false}>
                    {[...repetir(vendaList), ...repetir(vendaList)].map((prop, index) => (
                      <ImovelCard key={`v-${prop.slug}-${index}`} prop={prop} onClick={() => onPropertyClick(prop.slug)} />
                    ))}
                  </MarqueeRow>
                </div>
              )}
              {/* Linha 2 — EMPREENDIMENTOS (passa pro lado CONTRÁRIO) */}
              {empreendimentos.length > 0 && (
                <div>
                  <div className="max-w-7xl mx-auto px-6 md:px-10 mb-6 flex flex-col md:flex-row md:justify-between md:items-end gap-3">
                    <div>
                      <span className="text-[#c9943a] text-xs font-bold tracking-[0.2em] uppercase mb-2 block">Em destaque</span>
                      <h2 className="font-serif text-3xl md:text-4xl text-[#16284B]">Empreendimentos em Destaque</h2>
                    </div>
                    <button onClick={onLancamentosClick} className="text-sm uppercase tracking-widest text-[#5d6b86] hover:text-[#c9943a] transition-colors flex items-center gap-2 self-start md:self-auto">
                      Ver Catálogo <ChevronRight size={16} />
                    </button>
                  </div>
                  <MarqueeRow reverse={true}>
                    {[...repetir(empreendimentos), ...repetir(empreendimentos)].map((emp, index) => (
                      <EmpreendimentoCard key={`e-${emp.slug}-${index}`} emp={emp} onClick={onLancamentosClick} />
                    ))}
                  </MarqueeRow>
                </div>
              )}
              {/* Linha 3 — ALUGUEL (direita pra esquerda) */}
              {aluguelList.length > 0 && (
                <div>
                  <div className="max-w-7xl mx-auto px-6 md:px-10 mb-6 flex flex-col md:flex-row md:justify-between md:items-end gap-3">
                    <div>
                      <span className="text-[#c9943a] text-xs font-bold tracking-[0.2em] uppercase mb-2 block">Em destaque</span>
                      <h2 className="font-serif text-3xl md:text-4xl text-[#16284B]">Para Alugar em Destaque</h2>
                    </div>
                    <button onClick={() => onBuscaClick({ finalidade: 'aluguel' })} className="text-sm uppercase tracking-widest text-[#5d6b86] hover:text-[#c9943a] transition-colors flex items-center gap-2 self-start md:self-auto">
                      Ver Catálogo <ChevronRight size={16} />
                    </button>
                  </div>
                  <MarqueeRow reverse={false}>
                    {[...repetir(aluguelList), ...repetir(aluguelList)].map((prop, index) => (
                      <ImovelCard key={`a-${prop.slug}-${index}`} prop={prop} onClick={() => onPropertyClick(prop.slug)} />
                    ))}
                  </MarqueeRow>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {}
      <section className="py-32 px-6 bg-[#16284B] text-white">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-20">
          <div className="lg:w-1/2 space-y-8">
            <span className="text-[#e8b55a] text-xs font-bold tracking-[0.2em] uppercase flex items-center gap-2">
              <BrainCircuit size={16} /> Inovação Imobiliária
            </span>
            <h2 className="font-serif text-4xl md:text-6xl font-light leading-tight">
              Avaliamos seu patrimônio com <br/><span className="text-[#c9943a] italic">precisão de mercado</span>
            </h2>
            <p className="text-[#7b95c8] text-lg font-light leading-relaxed max-w-xl">
              Nossa plataforma não apenas lista imóveis, ela compreende o mercado. Cruzamos dados de localização, infraestrutura do bairro e valorização histórica de Vitória da Conquista para gerar avaliações precisas e justas.
            </p>
            
            <div className="pt-8 flex flex-col sm:flex-row gap-6">
              <button onClick={abrirAna} className="bg-grad-gold px-8 py-4 text-[#16284B] font-semibold text-sm uppercase tracking-widest hover:shadow-[0_0_30px_rgba(201,148,58,0.4)] transition-all duration-300 flex items-center justify-center gap-3">
                <Sparkles size={18} /> Avaliar meu imóvel
              </button>
              <button onClick={abrirAna} className="border border-[#5C7CB8] px-8 py-4 text-white font-medium text-sm uppercase tracking-widest hover:bg-[#5C7CB8]/10 transition-colors flex items-center justify-center">
                Falar com Consultor
              </button>
            </div>
          </div>
          
          <div className="lg:w-1/2 w-full">
            {/* Visualização de Interface Futurista / Elegante */}
            <div className="bg-gradient-to-br from-white/10 to-white/5 border border-white/10 p-8 backdrop-blur-lg rounded-2xl shadow-2xl relative">
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-[#c9943a] rounded-full blur-[60px] opacity-50"></div>
              
              <div className="space-y-6">
                <div className="flex justify-between items-center border-b border-white/10 pb-4">
                  <span className="text-sm font-light text-white">Avalie e simule — grátis</span>
                  <span className="text-xs uppercase tracking-widest bg-[#c9943a]/20 text-[#e8b55a] px-3 py-1 rounded-full">Resultado na hora</span>
                </div>
                <div className="text-center py-4 space-y-5">
                  <p className="text-[#7b95c8] font-light leading-relaxed">
                    Descubra quanto vale seu imóvel e qual seu enquadramento no financiamento — com os
                    números reais de Vitória da Conquista. É uma estimativa, mas já te dá clareza.
                  </p>
                  <button onClick={onCalculadorasClick} className="w-full bg-grad-gold text-[#16284B] font-semibold py-3.5 rounded-lg text-sm uppercase tracking-widest hover:shadow-[0_0_30px_rgba(201,148,58,0.4)] transition-all flex items-center justify-center gap-2">
                    <Sparkles size={18} /> Abrir as calculadoras
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-[#0f1c38] text-white/60 py-20 px-6 border-t border-white/10">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
          
          <div className="col-span-1 md:col-span-2 space-y-6">
            <div className="flex flex-col">
              <span className="font-serif font-bold tracking-wide text-2xl text-white">
                Priscila Vasconcelos
              </span>
              <span className="text-xs tracking-[0.3em] uppercase text-[#c9943a]">
                Compra · Venda · Aluguel
              </span>
            </div>
            <p className="text-sm font-light leading-relaxed max-w-sm">
              Imóveis pra todo sonho e cada momento da vida, em Vitória da Conquista e região. Atendimento humano e honesto, do primeiro contato à entrega das chaves.
            </p>
          </div>

          <div className="space-y-6">
            <h4 className="text-white text-sm tracking-widest uppercase">Endereço</h4>
            <div className="space-y-2 text-sm font-light flex items-start gap-3">
              <MapPin size={18} className="text-[#c9943a] flex-shrink-0 mt-1" />
              <p>Vitória da Conquista — BA<br/>Atendimento por WhatsApp e visitas agendadas</p>
            </div>
          </div>

          <div className="space-y-6">
            <h4 className="text-white text-sm tracking-widest uppercase">Contato</h4>
            <ul className="space-y-3 text-sm font-light">
              <li><a href="https://wa.me/5577999395511" target="_blank" rel="noreferrer" className="hover:text-[#c9943a] transition-colors">WhatsApp: (77) 99939-5511</a></li>
              <li className="pt-2">
                <a href="https://instagram.com/priscilavasconcelosvca" target="_blank" rel="noreferrer" className="group inline-flex items-center gap-2 text-[#c9943a] hover:text-white transition-colors">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="shrink-0">
                    <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
                    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37Z" />
                    <line x1="17.5" y1="6.5" x2="17.5" y2="6.5" />
                  </svg>
                  <span className="border-b border-[#c9943a] group-hover:border-white pb-1">@priscilavasconcelosvca</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="max-w-7xl mx-auto border-t border-white/10 mt-16 pt-8 flex flex-col md:flex-row justify-between items-center text-xs tracking-wider">
          <p>&copy; 2026 Priscila Vasconcelos Imobiliária. Todos os direitos reservados.</p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="/admin/" className="hover:text-[#c9943a] transition-colors">Painel da corretora</a>
            <a href="#" className="hover:text-white transition-colors">Política de Privacidade</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
