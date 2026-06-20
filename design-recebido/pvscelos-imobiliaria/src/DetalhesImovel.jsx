import React, { useState, useEffect } from 'react';
import {
  MapPin,
  BedDouble,
  Bath,
  Maximize,
  Car,
  Sparkles,
  MessageCircle,
  Calendar,
  ChevronLeft,
  Share2,
  Heart,
  ShieldCheck,
  CheckCircle2,
  BrainCircuit,
  X,
} from 'lucide-react';
import { getImovel, abrirAna, agendarVisita, trackLead } from './api';

export default function DetalhesImovel({ slug, onBack }) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [im, setIm] = useState(null);
  const [carregando, setCarregando] = useState(true);

  // Agendamento de visita (modal)
  const [modalVisita, setModalVisita] = useState(false);
  const [vNome, setVNome] = useState('');
  const [vWhats, setVWhats] = useState('');
  const [vData, setVData] = useState('');
  const [vEnviando, setVEnviando] = useState(false);
  const [vEnviado, setVEnviado] = useState(false);
  const [vErro, setVErro] = useState('');

  async function enviarVisita() {
    setVErro('');
    if (vNome.trim().length < 2 || vWhats.replace(/\D/g, '').length < 10 || !vData) {
      setVErro('Preencha nome, um WhatsApp válido (com DDD) e a data.');
      return;
    }
    setVEnviando(true);
    try {
      await agendarVisita({
        nome: vNome.trim(),
        telefone: vWhats.replace(/\D/g, ''),
        data_preferida: vData,
        titulo_imovel: im?.titulo,
        bairro: im?.bairro,
        observacoes: 'Visita solicitada pelo site.',
      });
      setVEnviado(true);
      trackLead('agendar_visita');
    } catch {
      setVErro('Não consegui agendar agora. Tenta de novo ou fala com a Ana.');
    } finally {
      setVEnviando(false);
    }
  }

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Carrega o imóvel REAL pelo slug (dados de produção via /api/imoveis).
  useEffect(() => {
    let vivo = true;
    setCarregando(true);
    getImovel(slug)
      .then((dado) => { if (vivo) setIm(dado); })
      .catch(() => { if (vivo) setIm(null); })
      .finally(() => { if (vivo) setCarregando(false); });
    return () => { vivo = false; };
  }, [slug]);

  if (carregando) {
    return (
      <div className="min-h-screen bg-[#FBFCFE] flex items-center justify-center">
        <div className="w-12 h-12 rounded-full border-4 border-[#dde5f0] border-t-[#c9943a] animate-spin" />
      </div>
    );
  }

  if (!im) {
    return (
      <div className="min-h-screen bg-[#FBFCFE] flex flex-col items-center justify-center gap-6 text-[#16284B] px-6 text-center">
        <p className="font-serif text-2xl">Imóvel não encontrado.</p>
        <button onClick={onBack} className="bg-[#16284B] text-white px-6 py-3 rounded-xl text-sm uppercase tracking-widest hover:bg-[#0f1c38] transition-colors">
          Voltar ao Catálogo
        </button>
      </div>
    );
  }

  const fotos = im.fotos || [];
  const fotoPrincipal = fotos[0]?.grande || im.capaUrl;
  const foto2 = fotos[1]?.grande || fotoPrincipal;
  const foto3 = fotos[2]?.grande || foto2;
  const diferenciais = im.caracteristicas || [];

  // Estatísticas que o backend REALMENTE tem (nada inventado).
  const stats = [
    { icon: BedDouble, valor: im.quartos, label: 'Quartos' },
    { icon: Bath, valor: im.suites, label: 'Suítes' },
    { icon: Car, valor: im.vagas, label: 'Vagas' },
    { icon: Maximize, valor: im.area, label: 'Área Útil', sufixo: 'm²' },
  ].filter((s) => s.valor != null && s.valor !== 0);

  return (
    <div className="min-h-screen bg-[#FBFCFE] text-[#16284B] font-sans antialiased selection:bg-[#c9943a] selection:text-white pb-24">
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Inter', sans-serif; }
        .bg-grad-gold { background: linear-gradient(120deg, #c9943a, #e8b55a); }
      `}} />

      <nav className={`fixed w-full z-50 transition-all duration-500 ${isScrolled ? 'bg-white/95 backdrop-blur-md border-b border-[#dde5f0] py-4' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          <button
            onClick={onBack}
            className={`flex items-center gap-2 text-sm uppercase tracking-widest font-medium transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-white hover:text-white/70'}`}
          >
            <ChevronLeft size={18} /> Voltar ao Catálogo
          </button>

          <div className="flex gap-4">
            <button
              onClick={async () => {
                const url = window.location.href;
                try {
                  if (navigator.share) await navigator.share({ title: im.titulo, url });
                  else { await navigator.clipboard.writeText(url); alert('Link do imóvel copiado!'); }
                } catch (e) { /* usuário cancelou */ }
              }}
              className={`w-10 h-10 rounded-full flex items-center justify-center backdrop-blur-sm transition-all ${isScrolled ? 'bg-[#f5f0e8] text-[#16284B] hover:bg-[#c9943a] hover:text-white' : 'bg-white/20 text-white hover:bg-white/40'}`}
            >
              <Share2 size={16} />
            </button>
            <button
              onClick={() => setIsLiked(!isLiked)}
              className={`w-10 h-10 rounded-full flex items-center justify-center backdrop-blur-sm transition-all ${isScrolled ? 'bg-[#f5f0e8]' : 'bg-white/20'}`}
            >
              <Heart size={16} className={isLiked ? 'fill-[#c9943a] text-[#c9943a]' : (isScrolled ? 'text-[#16284B]' : 'text-white')} />
            </button>
          </div>
        </div>
      </nav>

      <header className="px-4 pt-4 md:px-6 md:pt-6 max-w-[1600px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 md:grid-rows-2 gap-2 h-[50vh] md:h-[70vh] min-h-[400px] rounded-3xl overflow-hidden">
          <div className="md:col-span-3 md:row-span-2 relative group cursor-pointer">
            {fotoPrincipal && <img src={fotoPrincipal} alt={im.titulo} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105" />}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20"></div>
          </div>
          <div className="hidden md:block col-span-1 row-span-1 relative group cursor-pointer overflow-hidden">
            {foto2 && <img src={foto2} alt="Interior 1" className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105" />}
          </div>
          <div className="hidden md:block col-span-1 row-span-1 relative group cursor-pointer overflow-hidden">
            {foto3 && <img src={foto3} alt="Interior 2" className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105" />}
            {fotos.length > 3 && (
              <div className="absolute inset-0 bg-black/40 hover:bg-black/20 transition-colors flex items-center justify-center">
                <button className="bg-white/20 backdrop-blur-md border border-white/40 text-white px-6 py-3 rounded-full text-sm tracking-widest uppercase font-medium hover:bg-white hover:text-[#16284B] transition-all">
                  Ver {fotos.length} Fotos
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 mt-12 flex flex-col lg:flex-row gap-16 relative">

        <div className="w-full lg:w-[65%] space-y-12">

          <div className="space-y-4">
            <div className="flex flex-wrap gap-3 mb-4">
              {im.tipo && <span className="bg-[#16284B] text-white px-3 py-1 text-[10px] uppercase tracking-widest rounded-full">{im.tipo}</span>}
              {im.destaque ? <span className="bg-[#f5f0e8] text-[#c9943a] px-3 py-1 text-[10px] uppercase tracking-widest rounded-full font-semibold">Destaque</span> : null}
            </div>
            <h1 className="font-serif text-4xl md:text-5xl text-[#16284B] leading-tight">{im.titulo}</h1>
            <p className="text-[#5d6b86] flex items-center gap-2 text-sm font-light tracking-wide">
              <MapPin size={16} className="text-[#c9943a]" /> {im.bairro} · Vitória da Conquista — BA
            </p>
          </div>

          {stats.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-8 border-y border-[#dde5f0]">
              {stats.map((s, i) => (
                <div key={i} className="space-y-1">
                  <s.icon size={24} className="text-[#c9943a] mb-2" />
                  <p className="text-2xl font-serif text-[#16284B]">{s.valor}{s.sufixo ? <span className="text-base font-sans font-light"> {s.sufixo}</span> : null}</p>
                  <p className="text-xs uppercase tracking-widest text-[#5d6b86]">{s.label}</p>
                </div>
              ))}
            </div>
          )}

          {/* Card Avaliação PVSCELOS — Bloco 2 plugará a AVM real (/api/avaliar-imovel + /api/avaliacao/panorama).
              Por enquanto: só dado REAL do imóvel, sem inventar número. */}
          <div className="bg-gradient-to-br from-[#fbfcfe] to-[#f5f0e8] p-8 rounded-2xl border border-[#c9943a]/30 relative overflow-hidden shadow-[0_8px_30px_rgb(201,148,58,0.05)]">
            <div className="absolute -right-10 -top-10 w-40 h-40 bg-[#c9943a] rounded-full blur-[80px] opacity-20"></div>
            <div className="flex items-start gap-4 relative z-10">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center flex-shrink-0 shadow-sm border border-[#c9943a]/20">
                <BrainCircuit size={20} className="text-[#c9943a]" />
              </div>
              <div className="space-y-2">
                <h3 className="text-sm font-bold uppercase tracking-widest text-[#16284B] flex items-center gap-2">
                  Avaliação PVSCELOS <Sparkles size={14} className="text-[#c9943a]" />
                </h3>
                <p className="text-[#5d6b86] text-sm leading-relaxed font-light">
                  Imóvel real da carteira da Priscila Vasconcelos em {im.bairro}
                  {diferenciais.length ? ` · ${diferenciais.length} diferenciais cadastrados` : ''}. Quer a
                  estimativa de valor e o panorama do bairro? Fale com a Ana aqui mesmo.
                </p>
              </div>
            </div>
          </div>

          {im.descricao && (
            <div className="space-y-6">
              <h3 className="font-serif text-2xl text-[#16284B]">O Cenário da Sua Nova Vida</h3>
              <p className="text-[#5d6b86] text-lg leading-relaxed font-light whitespace-pre-line">
                {im.descricao}
              </p>
            </div>
          )}

          {diferenciais.length > 0 && (
            <div className="space-y-6">
              <h3 className="font-serif text-2xl text-[#16284B]">Diferenciais Exclusivos</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8">
                {diferenciais.map((item, index) => (
                  <div key={index} className="flex items-center gap-3 text-[#5d6b86] text-sm font-light">
                    <CheckCircle2 size={16} className="text-[#c9943a] flex-shrink-0" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Localização — mapa do bairro (sem chave; região, não endereço exato) */}
          <div className="space-y-4">
            <h3 className="font-serif text-2xl text-[#16284B]">Localização</h3>
            <p className="text-sm text-[#5d6b86] font-light flex items-center gap-2">
              <MapPin size={16} className="text-[#c9943a]" /> {im.bairro} · Vitória da Conquista — BA
            </p>
            <div className="rounded-2xl overflow-hidden border border-[#dde5f0] shadow-sm">
              <iframe
                title={`Mapa de ${im.bairro}`}
                src={`https://maps.google.com/maps?q=${encodeURIComponent(im.bairro + ', Vitória da Conquista - BA')}&z=14&output=embed`}
                className="w-full h-72"
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            </div>
            <p className="text-xs text-[#7b95c8]">Mostramos a região do bairro — o endereço exato é informado no agendamento da visita.</p>
          </div>

        </div>

        <div className="w-full lg:w-[35%] relative">
          <div className="sticky top-32 space-y-6">

            <div className="bg-white p-8 rounded-3xl border border-[#dde5f0] shadow-[0_8px_30px_rgb(0,0,0,0.03)] space-y-8">

              <div>
                <span className="text-[10px] uppercase tracking-[0.2em] text-[#5d6b86] font-bold">Valor de Investimento</span>
                <h2 className="font-serif text-4xl text-[#16284B] mt-2">{im.precoFmt}</h2>
              </div>

              {/* Corretora REAL: Priscila Vasconcelos */}
              <div className="bg-[#f5f0e8] p-4 rounded-2xl border border-[#dde5f0]/50 flex items-center gap-4">
                <img
                  src="/assets/priscila-sorrindo.jpg"
                  alt="Priscila Vasconcelos"
                  className="w-14 h-14 rounded-full object-cover border-2 border-white shadow-sm"
                />
                <div>
                  <h4 className="text-sm font-bold text-[#16284B]">Priscila Vasconcelos</h4>
                  <p className="text-[10px] uppercase tracking-widest text-[#5d6b86]">Corretora · CRECI/BA 29.231</p>
                </div>
              </div>

              <div className="space-y-3">
                <button onClick={() => setModalVisita(true)} className="w-full bg-[#16284B] text-white py-4 rounded-xl text-sm uppercase tracking-widest font-medium hover:bg-[#0f1c38] transition-all flex items-center justify-center gap-2 group">
                  <Calendar size={18} className="text-[#c9943a] group-hover:scale-110 transition-transform" />
                  Agendar Visita Exclusiva
                </button>
                <button onClick={abrirAna} className="w-full bg-white border border-[#16284B] text-[#16284B] py-4 rounded-xl text-sm uppercase tracking-widest font-medium hover:bg-[#f5f0e8] transition-colors flex items-center justify-center gap-2">
                  <MessageCircle size={18} /> Falar com a Ana
                </button>
              </div>

              <div className="flex items-start gap-2 text-[10px] text-[#7b95c8] leading-relaxed pt-4 border-t border-[#dde5f0]/50">
                <ShieldCheck size={14} className="flex-shrink-0 mt-0.5" />
                <p>A PVSCELOS garante o sigilo total das suas negociações. Visitas apenas mediante agendamento prévio com documentação.</p>
              </div>

            </div>

          </div>
        </div>

      </main>

      {/* Modal: agendar visita */}
      {modalVisita && (
        <div className="fixed inset-0 z-[70] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4" onClick={() => setModalVisita(false)}>
          <div className="bg-white rounded-3xl w-full max-w-md p-8 relative" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setModalVisita(false)} className="absolute top-5 right-5 text-[#5d6b86] hover:text-[#16284B]"><X size={20} /></button>
            {vEnviado ? (
              <div className="text-center py-6">
                <CheckCircle2 size={36} className="text-[#c9943a] mx-auto mb-3" />
                <h3 className="font-serif text-2xl text-[#16284B]">Visita solicitada! 🎉</h3>
                <p className="text-[#5d6b86] mt-2">A Priscila confirma com você no WhatsApp.</p>
                <button onClick={() => setModalVisita(false)} className="mt-6 bg-[#16284B] text-white px-6 py-3 rounded-xl text-sm uppercase tracking-widest">Fechar</button>
              </div>
            ) : (
              <>
                <h3 className="font-serif text-2xl text-[#16284B] mb-1">Agendar visita</h3>
                <p className="text-sm text-[#5d6b86] mb-6 line-clamp-1">{im.titulo}</p>
                <div className="space-y-4">
                  <input value={vNome} onChange={(e) => setVNome(e.target.value)} placeholder="Seu nome" className="w-full px-4 py-3 bg-[#FBFCFE] border border-[#dde5f0] rounded-xl text-sm focus:outline-none focus:border-[#c9943a]" />
                  <input value={vWhats} onChange={(e) => setVWhats(e.target.value)} type="tel" placeholder="WhatsApp" className="w-full px-4 py-3 bg-[#FBFCFE] border border-[#dde5f0] rounded-xl text-sm focus:outline-none focus:border-[#c9943a]" />
                  <div>
                    <label className="text-xs uppercase tracking-widest text-[#5d6b86] block mb-1">Data preferida</label>
                    <input value={vData} onChange={(e) => setVData(e.target.value)} type="date" className="w-full px-4 py-3 bg-[#FBFCFE] border border-[#dde5f0] rounded-xl text-sm focus:outline-none focus:border-[#c9943a]" />
                  </div>
                  {vErro && <p className="text-sm text-red-500">{vErro}</p>}
                  <button onClick={enviarVisita} disabled={vEnviando} className="w-full bg-[#16284B] text-white py-4 rounded-xl text-sm uppercase tracking-widest font-medium hover:bg-[#0f1c38] disabled:opacity-50">
                    {vEnviando ? 'Enviando...' : 'Solicitar visita'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
