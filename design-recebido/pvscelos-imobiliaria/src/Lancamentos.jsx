import React, { useState, useEffect } from 'react';
import { MapPin, Building2, CheckCircle2, Sparkles, ArrowRight, Compass, Clock, Camera, ChevronLeft } from 'lucide-react';
import { getEmpreendimentos, abrirAna } from './api';
import EvolucaoObra from './EvolucaoObra';

export default function Lancamentos({ onBack, onLoginClick }) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [emps, setEmps] = useState([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    let vivo = true;
    getEmpreendimentos()
      .then((lista) => { if (vivo) setEmps(lista); })
      .catch(() => { if (vivo) setEmps([]); })
      .finally(() => { if (vivo) setCarregando(false); });
    return () => { vivo = false; };
  }, []);

  const heroFoto = emps.find((e) => e.capaUrl)?.capaUrl;

  return (
    <div className="min-h-screen bg-[#FBFCFE] font-sans text-[#16284B] selection:bg-[#c9943a] selection:text-white">
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Inter', sans-serif; }
      `}} />

      {/* Navegação */}
      <nav className={`fixed w-full z-50 transition-all duration-500 ${isScrolled ? 'bg-[#0f1c38]/95 backdrop-blur-md border-b border-white/10 py-4' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center text-white">
          <button className="flex items-center gap-2 text-xs uppercase tracking-widest font-medium hover:text-[#c9943a] transition-colors" onClick={onBack}>
            <ChevronLeft size={16} /> Voltar
          </button>
          <img
            src={`${import.meta.env.BASE_URL}selo-branco.png`}
            alt="Priscila Vasconcelos Imobiliária"
            onClick={onBack}
            className="h-16 md:h-20 object-contain opacity-90 cursor-pointer [filter:drop-shadow(0_2px_8px_rgba(0,0,0,0.3))]"
          />
          <button onClick={onLoginClick} className="text-xs uppercase tracking-widest font-medium border border-white/30 px-6 py-2 rounded-full hover:bg-white hover:text-[#16284B] transition-colors">
            Acesso Restrito
          </button>
        </div>
      </nav>

      {/* Hero */}
      <header className="relative h-[70vh] min-h-[560px] flex items-center justify-center overflow-hidden bg-[#0f1c38]">
        <div className="absolute inset-0 z-0">
          {heroFoto && <img src={heroFoto} alt="Empreendimentos" className="w-full h-full object-cover opacity-40 scale-105" />}
          <div className="absolute inset-0 bg-gradient-to-t from-[#0f1c38] via-[#0f1c38]/40 to-[#0f1c38]/60"></div>
        </div>
        <div className="relative z-10 text-center text-white px-6 max-w-4xl mx-auto mt-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 mb-8">
            <span className="w-2 h-2 bg-[#c9943a] rounded-full animate-ping"></span>
            <span className="text-[10px] uppercase tracking-widest font-semibold">Curadoria PVSCELOS</span>
          </div>
          <h1 className="font-serif text-5xl md:text-7xl font-light mb-6 leading-tight">
            Os Melhores <span className="italic text-[#c9943a]">Empreendimentos</span>
          </h1>
          <p className="font-light text-lg md:text-xl text-white/80 max-w-2xl mx-auto leading-relaxed">
            Os lançamentos e condomínios de alto padrão de Vitória da Conquista, selecionados pela Priscila Vasconcelos.
          </p>
        </div>
      </header>

      {/* Evolução da Obra (timelapse) — destaque de um empreendimento na planta, fotos reais.
          Quando o dono enviar as imagens de estágio (planta / 3D / obra), é só trocar aqui. */}
      {(() => {
        const np = emps.find((e) => e.statusRaw === 'na_planta' && e.fotos.length > 1);
        if (!np) return null;
        const imgs = np.fotos.slice(0, 4).map((f, i) => ({ img: f.grande, title: f.legenda || `Vista ${i + 1}` }));
        return <EvolucaoObra titulo={np.nome} imagens={imgs} />;
      })()}

      {/* Galeria dos empreendimentos reais */}
      <section className="py-24 bg-[#FBFCFE]">
        <div className="max-w-7xl mx-auto px-6 space-y-28">

          {carregando && (
            <div className="flex justify-center py-20">
              <div className="w-12 h-12 rounded-full border-4 border-[#dde5f0] border-t-[#c9943a] animate-spin" />
            </div>
          )}

          {!carregando && emps.length === 0 && (
            <p className="text-center text-[#5d6b86] py-20">Nenhum empreendimento disponível no momento.</p>
          )}

          {emps.map((e, i) => (
            <article key={e.id} className={`flex flex-col ${i % 2 === 1 ? 'lg:flex-row-reverse' : 'lg:flex-row'} gap-10 lg:gap-16 items-center`}>

              {/* Foto principal + faixa de mini-fotos */}
              <div className="w-full lg:w-1/2">
                <div className="relative rounded-3xl overflow-hidden shadow-xl border border-[#dde5f0] aspect-[4/3]">
                  {e.capaUrl && <img src={e.capaUrl} alt={e.nome} className="w-full h-full object-cover" />}
                  {e.status && (
                    <span className={`absolute top-5 left-5 px-4 py-1.5 text-[10px] uppercase tracking-widest rounded-full font-semibold ${e.statusRaw === 'pronto' ? 'bg-[#c9943a] text-[#16284B]' : 'bg-[#16284B] text-white'}`}>
                      {e.status}
                    </span>
                  )}
                  {e.fotos.length > 1 && (
                    <span className="absolute bottom-5 right-5 flex items-center gap-2 bg-black/50 backdrop-blur-sm text-white px-3 py-1.5 text-[11px] rounded-full">
                      <Camera size={13} /> {e.fotos.length} fotos
                    </span>
                  )}
                </div>
                {e.fotos.length > 1 && (
                  <div className="grid grid-cols-4 gap-2 mt-2">
                    {e.fotos.slice(1, 5).map((f, idx) => (
                      <div key={idx} className="aspect-square rounded-xl overflow-hidden border border-[#dde5f0]">
                        <img src={f.thumb} alt="" className="w-full h-full object-cover" />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Conteúdo */}
              <div className="w-full lg:w-1/2 space-y-5">
                <div className="flex items-center gap-3 text-xs uppercase tracking-widest text-[#5d6b86]">
                  <span className="flex items-center gap-1.5"><MapPin size={14} className="text-[#c9943a]" /> {e.bairro}</span>
                  {e.construtora && <span className="flex items-center gap-1.5 border-l border-[#dde5f0] pl-3"><Building2 size={14} className="text-[#c9943a]" /> {e.construtora}</span>}
                </div>

                <h2 className="font-serif text-3xl md:text-4xl text-[#16284B] leading-tight">{e.nome}</h2>

                {/* Stats reais (só o que existe) */}
                <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm text-[#5d6b86]">
                  {e.unidades ? <span><strong className="text-[#16284B] font-serif text-lg">{e.unidades}</strong> unidades</span> : null}
                  {e.torres ? <span><strong className="text-[#16284B] font-serif text-lg">{e.torres}</strong> torres</span> : null}
                  {e.andares ? <span><strong className="text-[#16284B] font-serif text-lg">{e.andares}</strong> andares</span> : null}
                  {e.entrega ? <span className="flex items-center gap-1.5"><Clock size={14} className="text-[#c9943a]" /> Entrega {e.entrega}</span> : null}
                </div>

                {e.descricao && (
                  <p className="text-[#5d6b86] leading-relaxed font-light whitespace-pre-line line-clamp-[10]">
                    {e.descricao}
                  </p>
                )}

                {/* Lazer (chips) */}
                {e.lazer.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-2">
                    {e.lazer.slice(0, 10).map((l, idx) => (
                      <span key={idx} className="flex items-center gap-1.5 bg-[#f5f0e8] text-[#16284B] px-3 py-1 rounded-full text-xs">
                        <CheckCircle2 size={12} className="text-[#c9943a]" /> {l}
                      </span>
                    ))}
                    {e.lazer.length > 10 && <span className="text-xs text-[#5d6b86] px-2 py-1">+{e.lazer.length - 10}</span>}
                  </div>
                )}

                {/* Ações */}
                <div className="flex flex-wrap gap-3 pt-4">
                  <button onClick={abrirAna} className="bg-[#16284B] text-white px-6 py-3 rounded-xl text-sm uppercase tracking-widest font-medium hover:bg-[#0f1c38] transition-all flex items-center gap-2 group">
                    Falar com a Priscila <ArrowRight size={16} className="text-[#c9943a] group-hover:translate-x-1 transition-transform" />
                  </button>
                  {e.tour360 && (
                    <a href={e.tour360} target="_blank" rel="noreferrer" className="border border-[#16284B] text-[#16284B] px-6 py-3 rounded-xl text-sm uppercase tracking-widest font-medium hover:bg-[#f5f0e8] transition-colors flex items-center gap-2">
                      <Compass size={16} /> Tour 360°
                    </a>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Fechamento */}
      <section className="py-20 bg-[#0f1c38] text-white text-center">
        <div className="max-w-3xl mx-auto px-6">
          <Sparkles size={28} className="text-[#c9943a] mx-auto mb-6" />
          <h2 className="font-serif text-3xl md:text-4xl mb-4">Quer condições e tabela de valores?</h2>
          <p className="text-[#7b95c8] font-light mb-8">A Priscila te passa as melhores condições de cada empreendimento, com sigilo total.</p>
          <button onClick={abrirAna} className="bg-[#c9943a] text-[#16284B] px-8 py-4 rounded-full text-sm font-bold uppercase tracking-widest hover:bg-[#e8b55a] transition-all inline-flex items-center gap-3">
            Falar com a Priscila <ArrowRight size={18} />
          </button>
        </div>
      </section>
    </div>
  );
}
