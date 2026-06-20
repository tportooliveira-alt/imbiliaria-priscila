import React, { useState, useEffect, useRef } from 'react';
import { Search, Menu, X, MapPin, BedDouble, Car, Maximize, ArrowRight, Sparkles, BrainCircuit, ChevronRight } from 'lucide-react';
import { getImoveis, abrirAna, enviarLeadVendedor, trackLead } from './api';

export default function Home({ onPropertyClick, onLancamentosClick, onLoginClick, onCaptacaoClick, onSobreClick, onBuscaClick }) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [buscaHero, setBuscaHero] = useState('');
  const [properties, setProperties] = useState([]);
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
  }, []);

  // Carrossel: passa sozinho devagar E permite arrastar (swipe). Pausa ao tocar/passar o mouse.
  const carRef = useRef(null);
  const pausaCar = useRef(false);
  useEffect(() => {
    const el = carRef.current;
    if (!el) return;
    const id = setInterval(() => {
      if (pausaCar.current) return;
      el.scrollLeft += 1;
      if (el.scrollLeft >= el.scrollWidth / 2) el.scrollLeft = 0; // loop (lista duplicada)
    }, 25);
    return () => clearInterval(id);
  }, [properties]);

  // Efeito para mudar o estilo da navbar ao rolar a página
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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
        /* Pausa a animação ao passar o mouse */
        .animate-scroll:hover {
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
            <a href="#" onClick={(e) => { e.preventDefault(); onBuscaClick(); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Imóveis</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onLancamentosClick(); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Lançamentos</a>
            <a href="#" onClick={(e) => { e.preventDefault(); onCaptacaoClick(); }} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}>Anunciar Imóvel</a>
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
              { label: 'Imóveis', fn: onBuscaClick },
              { label: 'Lançamentos', fn: onLancamentosClick },
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
            alt="Mansão de Luxo" 
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
            Curadoria especializada em imóveis de alto padrão. Encontre seu próximo refúgio nos melhores bairros, de Candeias à Boa Vista.
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
              Na PVSCELOS, não vendemos apenas metros quadrados. Apresentamos cenários onde a sua história será vivida. Nossa curadoria une a estética "Quiet Luxury" ao conforto essencial que o clima da nossa cidade exige.
            </p>
            <p className="text-[#5d6b86] text-lg font-light leading-relaxed">
              Trabalhamos com sigilo absoluto e um nível de detalhamento técnico ímpar, conectando você às propriedades mais exclusivas do mercado.
            </p>
            <button className="group flex items-center gap-4 mt-8 text-[#16284B] font-medium tracking-wide hover:text-[#c9943a] transition-colors">
              <span className="uppercase text-sm tracking-widest border-b border-[#16284B] group-hover:border-[#c9943a] pb-1 transition-colors">Conheça nossa História</span>
              <ArrowRight size={18} className="transform group-hover:translate-x-2 transition-transform" />
            </button>
          </div>
        </div>
      </section>

      {}
      <section className="py-32 bg-[#FBFCFE] overflow-hidden relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
            <div>
              <span className="text-[#c9943a] text-xs font-bold tracking-[0.2em] uppercase mb-4 block">Coleção Exclusiva</span>
              <h2 className="font-serif text-4xl md:text-5xl text-[#16284B]">Imóveis em Destaque</h2>
            </div>
            <button onClick={onBuscaClick} className="text-sm uppercase tracking-widest text-[#5d6b86] hover:text-[#c9943a] transition-colors flex items-center gap-2">
              Ver Catálogo <ChevronRight size={16} />
            </button>
          </div>
        </div>

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
          ) : erroProps || properties.length === 0 ? (
            <p className="text-center text-[#5d6b86] font-light py-12 px-6">
              Não foi possível carregar os imóveis agora. Tente novamente em instantes.
            </p>
          ) : (
            <div
              ref={carRef}
              onMouseEnter={() => (pausaCar.current = true)}
              onMouseLeave={() => (pausaCar.current = false)}
              onTouchStart={() => (pausaCar.current = true)}
              onTouchEnd={() => setTimeout(() => (pausaCar.current = false), 2500)}
              className="flex gap-10 px-10 overflow-x-auto no-scrollbar snap-x"
            >
              {/* Lista duplicada pro loop suave; arrastável (swipe) */}
              {[...properties, ...properties].map((prop, index) => (
                <div
                  key={`car-${prop.slug}-${index}`}
                  className="w-[85vw] md:w-[400px] flex-shrink-0 group cursor-pointer"
                  onClick={() => onPropertyClick(prop.slug)}
                >
                  <div className="relative overflow-hidden aspect-[4/3] mb-6 rounded-t-xl bg-[#EEF2F8]">
                    {prop.capaUrl ? (
                      <img
                        src={prop.capaUrl}
                        alt={prop.titulo}
                        loading="lazy"
                        className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-in-out"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-[#5d6b86] text-xs uppercase tracking-widest">
                        Sem foto
                      </div>
                    )}
                    <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-4 py-1 text-[10px] tracking-widest uppercase text-[#16284B] font-semibold rounded-full shadow-sm">
                      {prop.bairro}
                    </div>
                    {/* Overlay escuro sutil que aparece junto com o zoom para destacar a foto */}
                    <div className="absolute inset-0 bg-[#16284B]/0 group-hover:bg-[#16284B]/10 transition-colors duration-500"></div>
                  </div>

                  <div className="space-y-3 px-2">
                    <h3 className="font-serif text-2xl text-[#16284B] group-hover:text-[#c9943a] transition-colors line-clamp-2">{prop.titulo}</h3>
                    <p className="text-xl text-[#5d6b86] font-light">{prop.precoFmt}</p>
                    <div className="flex items-center gap-5 text-sm text-[#5d6b86] border-t border-[#dde5f0] pt-4 mt-4">
                      {prop.suites > 0 ? (
                        <span className="flex items-center gap-1.5"><BedDouble size={16} className="text-[#c9943a]"/> {prop.suites} Suítes</span>
                      ) : prop.quartos > 0 ? (
                        <span className="flex items-center gap-1.5"><BedDouble size={16} className="text-[#c9943a]"/> {prop.quartos} Quartos</span>
                      ) : null}
                      {prop.vagas > 0 && (
                        <span className="flex items-center gap-1.5"><Car size={16} className="text-[#c9943a]"/> {prop.vagas} Vagas</span>
                      )}
                      {prop.area > 0 && (
                        <span className="flex items-center gap-1.5"><Maximize size={16} className="text-[#c9943a]"/> {prop.area} m²</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
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
              Avaliamos seu patrimônio com <br/><span className="text-[#c9943a] italic">precisão preditiva</span>
            </h2>
            <p className="text-[#7b95c8] text-lg font-light leading-relaxed max-w-xl">
              Nossa plataforma não apenas lista imóveis, ela compreende o mercado. Através da nossa Inteligência Artificial proprietária, cruzamos dados geoespaciais, infraestrutura local e valorização histórica de Vitória da Conquista para gerar avaliações exatas.
            </p>
            
            <div className="pt-8 flex flex-col sm:flex-row gap-6">
              <button onClick={abrirAna} className="bg-grad-gold px-8 py-4 text-[#16284B] font-semibold text-sm uppercase tracking-widest hover:shadow-[0_0_30px_rgba(201,148,58,0.4)] transition-all duration-300 flex items-center justify-center gap-3">
                <Sparkles size={18} /> Avaliar com a Ana
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
                  <span className="text-sm font-light text-white">Avalie seu imóvel — grátis</span>
                  <span className="text-xs uppercase tracking-widest bg-[#c9943a]/20 text-[#e8b55a] px-3 py-1 rounded-full">Resultado no zap</span>
                </div>
                
                {avEnviado ? (
                  <div className="text-center py-6">
                    <Sparkles size={34} className="text-[#c9943a] mx-auto mb-3" />
                    <h3 className="font-serif text-2xl text-white mb-2">Recebido! 🎉</h3>
                    <p className="text-[#7b95c8] font-light">A Priscila vai te enviar a avaliação do seu imóvel no seu WhatsApp.</p>
                  </div>
                ) : (
                  <div className="space-y-3.5">
                    <div className="grid grid-cols-2 gap-3">
                      <select value={av.tipo} onChange={setAvCampo('tipo')} className="bg-white/10 border border-white/15 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-[#c9943a] [&>option]:text-[#16284B]">
                        <option>Casa</option><option>Apartamento</option><option>Cobertura</option><option>Terreno</option><option>Comercial</option>
                      </select>
                      <input value={av.bairro} onChange={setAvCampo('bairro')} placeholder="Bairro" className="bg-white/10 border border-white/15 rounded-lg px-3 py-2.5 text-sm text-white placeholder-[#7b95c8] focus:outline-none focus:border-[#c9943a]" />
                      <input value={av.area} onChange={setAvCampo('area')} type="number" placeholder="Área (m²)" className="bg-white/10 border border-white/15 rounded-lg px-3 py-2.5 text-sm text-white placeholder-[#7b95c8] focus:outline-none focus:border-[#c9943a]" />
                      <input value={av.quartos} onChange={setAvCampo('quartos')} type="number" placeholder="Quartos" className="bg-white/10 border border-white/15 rounded-lg px-3 py-2.5 text-sm text-white placeholder-[#7b95c8] focus:outline-none focus:border-[#c9943a]" />
                    </div>
                    <input value={av.nome} onChange={setAvCampo('nome')} placeholder="Seu nome" className="w-full bg-white/10 border border-white/15 rounded-lg px-3 py-2.5 text-sm text-white placeholder-[#7b95c8] focus:outline-none focus:border-[#c9943a]" />
                    <input value={av.whatsapp} onChange={setAvCampo('whatsapp')} type="tel" placeholder="WhatsApp (pra enviar o resultado)" className="w-full bg-white/10 border border-white/15 rounded-lg px-3 py-2.5 text-sm text-white placeholder-[#7b95c8] focus:outline-none focus:border-[#c9943a]" />
                    <input value={av.email} onChange={setAvCampo('email')} type="email" placeholder="E-mail (opcional)" className="w-full bg-white/10 border border-white/15 rounded-lg px-3 py-2.5 text-sm text-white placeholder-[#7b95c8] focus:outline-none focus:border-[#c9943a]" />
                    {avErro && <p className="text-sm text-[#e8b55a]">{avErro}</p>}
                    <button onClick={avaliar} disabled={avEnviando} className="w-full bg-grad-gold text-[#16284B] font-semibold py-3.5 rounded-lg text-sm uppercase tracking-widest hover:shadow-[0_0_30px_rgba(201,148,58,0.4)] transition-all disabled:opacity-50">
                      {avEnviando ? 'Enviando...' : 'Quero minha avaliação'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-[#0f1c38] text-white/60 py-20 px-6 border-t border-white/10">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
          
          <div className="col-span-1 md:col-span-2 space-y-6">
            <div className="flex flex-col">
              <span className="font-serif font-bold tracking-widest text-2xl uppercase text-white">
                PVSCELOS
              </span>
              <span className="text-xs tracking-[0.3em] uppercase text-[#c9943a]">
                Imobiliária de Alto Padrão
              </span>
            </div>
            <p className="text-sm font-light leading-relaxed max-w-sm">
              Elevando o padrão de excelência no mercado imobiliário do Sudoeste Baiano. A discrição e a precisão que seu patrimônio merece.
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
                <a href="https://instagram.com/priscilavasconcelosvca" target="_blank" rel="noreferrer" className="text-[#c9943a] border-b border-[#c9943a] hover:text-white hover:border-white transition-colors pb-1">@priscilavasconcelosvca</a>
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
