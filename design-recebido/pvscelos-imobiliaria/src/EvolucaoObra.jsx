import React, { useState, useEffect } from 'react';

// Timelapse "Acompanhe a Obra" — crossfade entre as imagens (passa sozinho).
// imagens: [{ img, title }]. Hoje usa as fotos REAIS do empreendimento; quando o dono
// enviar as imagens de estágio (planta / render 3D / obra), é só passar elas aqui.
export default function EvolucaoObra({ titulo, imagens = [] }) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (imagens.length < 2) return;
    const t = setInterval(() => setStep((p) => (p + 1) % imagens.length), 3500);
    return () => clearInterval(t);
  }, [imagens.length]);

  if (imagens.length < 2) return null;

  return (
    <section className="py-24 bg-[#0f1c38] text-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <span className="text-[#c9943a] tracking-widest text-xs uppercase font-semibold mb-3 block">Acompanhe a Obra</span>
          <h2 className="text-3xl md:text-4xl font-serif mb-3">{titulo}</h2>
          <p className="text-[#7b95c8] max-w-2xl mx-auto font-light">
            Da planta ao pronto — acompanhe a evolução do empreendimento em um tour visual.
          </p>
        </div>

        <div className="relative max-w-5xl mx-auto h-[420px] md:h-[560px] rounded-3xl overflow-hidden shadow-2xl border border-white/10">
          {imagens.map((it, i) => (
            <div
              key={i}
              className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${i === step ? 'opacity-100 z-10' : 'opacity-0 z-0'}`}
            >
              <img src={it.img} alt={it.title || ''} className="w-full h-full object-cover scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#0f1c38]/90 via-transparent to-transparent"></div>
            </div>
          ))}

          <div className="absolute bottom-0 left-0 w-full p-6 md:p-10 z-20">
            <div className="flex items-center justify-between gap-2 md:gap-4">
              {imagens.map((it, i) => (
                <div key={i} className="flex-1 cursor-pointer group" onClick={() => setStep(i)}>
                  <span className={`text-[10px] md:text-sm tracking-widest uppercase mb-3 block font-semibold transition-colors duration-500 ${i === step ? 'text-[#c9943a]' : 'text-[#7b95c8] group-hover:text-white'}`}>
                    {it.title || `Etapa ${i + 1}`}
                  </span>
                  <div className="h-1 md:h-1.5 w-full bg-white/20 rounded-full overflow-hidden">
                    <div className={`h-full bg-[#c9943a] rounded-full ${i === step ? 'w-full transition-all duration-[3500ms] ease-linear' : i < step ? 'w-full' : 'w-0'}`}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
