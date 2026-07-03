import React, { useState, useEffect, useRef, useMemo } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Search, MapPin, BedDouble, Bath, Maximize, Heart, Map as MapIcon, List, ChevronLeft } from 'lucide-react';
import { getImoveis } from './api';

const VC_CENTER = [-14.8615, -40.8442];

// Coordenadas conhecidas dos principais bairros (fallback: geocoda via OSM).
const BAIRRO_COORDS = {
  candeias: [-14.8780, -40.8540], 'boa vista': [-14.8520, -40.8480], centro: [-14.8530, -40.8390],
  recreio: [-14.8680, -40.8620], primavera: [-14.8400, -40.8280], universidade: [-14.7980, -40.8720],
  'alto maron': [-14.8650, -40.8350], 'espirito santo': [-14.8580, -40.8520], brasil: [-14.8470, -40.8560],
};

export default function BuscaMapa({ onBack, onPropertyClick, buscaInicial = '', finalidadeInicial = 'todos' }) {
  const [imoveis, setImoveis] = useState([]);
  const [busca, setBusca] = useState(buscaInicial);
  const [finalidade, setFinalidade] = useState(finalidadeInicial);
  const [ativo, setAtivo] = useState(null);
  const [viewMode, setViewMode] = useState('list');
  const mapDiv = useRef(null);
  const mapInst = useRef(null);
  const markers = useRef({});

  useEffect(() => { getImoveis().then(setImoveis).catch(() => {}); }, []);

  const filtrados = useMemo(() => {
    const q = busca.trim().toLowerCase();
    return imoveis.filter((im) => {
      if (finalidade !== 'todos' && im.finalidade !== finalidade) return false;
      if (!q) return true;
      return `${im.titulo} ${im.bairro} ${im.tipo}`.toLowerCase().includes(q);
    });
  }, [imoveis, busca, finalidade]);

  // Contagem por finalidade (pra mostrar nas abas)
  const contagem = useMemo(() => ({
    todos: imoveis.length,
    venda: imoveis.filter((im) => im.finalidade === 'venda').length,
    aluguel: imoveis.filter((im) => im.finalidade === 'aluguel').length,
  }), [imoveis]);

  // Inicializa o mapa uma vez
  useEffect(() => {
    if (mapInst.current || !mapDiv.current) return;
    const m = L.map(mapDiv.current, { zoomControl: true, scrollWheelZoom: true }).setView(VC_CENTER, 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap', maxZoom: 19,
    }).addTo(m);
    mapInst.current = m;
    setTimeout(() => m.invalidateSize(), 200);
  }, []);

  // Geocoda os bairros e cria os pinos quando os imóveis carregam
  useEffect(() => {
    const map = mapInst.current;
    if (!map || !imoveis.length) return;
    let cancel = false;

    (async () => {
      Object.values(markers.current).forEach((mk) => map.removeLayer(mk));
      markers.current = {};
      const cache = { ...BAIRRO_COORDS };
      const bounds = [];

      for (const im of imoveis) {
        if (cancel) return;
        const chave = (im.bairro || '').trim().toLowerCase();
        let base = cache[chave];
        if (!base) {
          try {
            const r = await fetch(`https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(im.bairro + ', Vitória da Conquista, Bahia, Brasil')}`);
            const d = await r.json();
            if (d && d[0]) base = [parseFloat(d[0].lat), parseFloat(d[0].lon)];
          } catch { /* segue */ }
          base = base || VC_CENTER;
          cache[chave] = base;
        }
        const pos = [base[0] + Math.sin(im.id) * 0.004, base[1] + Math.cos(im.id) * 0.004];
        bounds.push(pos);

        const curto = im.preco ? 'R$ ' + Math.round(im.preco / 1000) + 'k' : 'consulte';
        const icon = L.divIcon({ className: 'pin-wrap', html: `<div class="pin">${curto}</div>`, iconSize: [64, 30], iconAnchor: [32, 30] });
        const mk = L.marker(pos, { icon }).addTo(map);
        mk.bindPopup(
          `<div style="width:190px;font-family:Inter,sans-serif">
             ${im.capaUrl ? `<img src="${im.capaUrl}" style="width:100%;height:110px;object-fit:cover"/>` : ''}
             <div style="padding:8px 10px 6px"><div style="font-weight:600;color:#16284B;font-size:13px">${im.titulo}</div>
             <div style="color:#c9943a;font-family:Playfair Display,serif">${im.precoFmt}<span style="color:#5d6b86;font-family:Inter,sans-serif;font-size:11px">${im.precoSufixo}</span></div>
             <div style="color:#5d6b86;font-size:11px">${im.bairro}</div></div>
           </div>`,
          { minWidth: 190, closeButton: false }
        );
        mk.on('mouseover', () => { setAtivo(im.id); mk.openPopup(); });
        mk.on('click', () => onPropertyClick(im.slug));
        markers.current[im.id] = mk;
      }
      if (bounds.length && !cancel) map.fitBounds(bounds, { padding: [60, 60], maxZoom: 14 });
    })();

    return () => { cancel = true; };
  }, [imoveis, onPropertyClick]);

  // Hover na lista → abre o popup (foto) do pino no mapa
  useEffect(() => {
    const mk = ativo && markers.current[ativo];
    if (mk) mk.openPopup();
  }, [ativo]);

  return (
    <div className="h-screen bg-[#FBFCFE] text-[#16284B] font-sans overflow-hidden flex flex-col selection:bg-[#c9943a] selection:text-white">
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .pin { background:#fff; color:#16284B; border:1px solid #dde5f0; border-radius:9999px; padding:3px 10px; font-size:12px; font-weight:700; box-shadow:0 4px 10px rgba(0,0,0,.18); white-space:nowrap; }
        .pin:hover { background:#16284B; color:#fff; }
        .leaflet-popup-content { margin:0 } .leaflet-popup-content-wrapper { border-radius:10px; overflow:hidden; padding:0 } .leaflet-popup-tip { background:#fff }
      `}} />

      {/* Navbar */}
      <header className="h-20 bg-white border-b border-[#dde5f0] flex items-center justify-between px-6 z-20 flex-shrink-0">
        <button onClick={onBack} className="flex items-center gap-2 text-sm uppercase tracking-widest font-medium text-[#16284B] hover:text-[#c9943a]">
          <ChevronLeft size={18} /> Início
        </button>
        <div className="hidden md:flex items-center flex-1 max-w-2xl mx-8 bg-[#f5f0e8]/50 border border-[#dde5f0] rounded-full px-4 py-2 focus-within:border-[#c9943a] transition-all">
          <Search size={18} className="text-[#5d6b86]" />
          <input value={busca} onChange={(e) => setBusca(e.target.value)} type="text" placeholder="Buscar por bairro, tipo ou título..." className="w-full bg-transparent border-none px-3 text-sm text-[#16284B] focus:outline-none placeholder-[#7b95c8]" />
        </div>
        <span className="text-xs text-[#5d6b86] whitespace-nowrap">{filtrados.length} imóveis</span>
      </header>

      <main className="flex-1 flex overflow-hidden relative">
        {/* Lista */}
        <div className={`w-full lg:w-[45%] flex flex-col h-full bg-[#FBFCFE] z-10 transition-transform duration-300 ${viewMode === 'map' ? '-translate-x-full lg:translate-x-0 absolute lg:relative' : 'translate-x-0 relative'}`}>
          <div className="p-4 md:hidden border-b border-[#dde5f0]">
            <div className="flex items-center bg-[#f5f0e8]/50 border border-[#dde5f0] rounded-xl px-4 py-3">
              <Search size={18} className="text-[#5d6b86] mr-2" />
              <input value={busca} onChange={(e) => setBusca(e.target.value)} type="text" placeholder="Buscar..." className="w-full bg-transparent border-none text-sm focus:outline-none" />
            </div>
          </div>
          {/* Abas: venda × aluguel */}
          <div className="flex gap-2 px-4 md:px-6 pt-4 pb-1 flex-shrink-0">
            {[['todos', 'Todos'], ['venda', 'À venda'], ['aluguel', 'Para alugar']].map(([val, label]) => (
              <button key={val} onClick={() => setFinalidade(val)}
                className={`px-4 py-1.5 rounded-full text-xs uppercase tracking-widest font-semibold transition-colors ${finalidade === val ? 'bg-[#16284B] text-white' : 'bg-[#f5f0e8]/60 text-[#5d6b86] border border-[#dde5f0] hover:text-[#16284B]'}`}>
                {label} <span className="opacity-60">{contagem[val]}</span>
              </button>
            ))}
          </div>
          <div className="flex-1 overflow-y-auto p-4 md:p-6 pt-3 pb-24 lg:pb-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {filtrados.map((prop) => (
                <div key={prop.id} className={`group cursor-pointer flex flex-col rounded-2xl transition-all ${ativo === prop.id ? 'ring-2 ring-[#c9943a]/60' : ''}`}
                  onMouseEnter={() => setAtivo(prop.id)} onMouseLeave={() => setAtivo(null)} onClick={() => onPropertyClick(prop.slug)}>
                  <div className="relative aspect-[4/3] overflow-hidden rounded-2xl mb-3 border border-[#dde5f0]">
                    {prop.capaUrl && <img src={prop.capaUrl} alt={prop.titulo} className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700" />}
                    <div className="absolute top-3 left-3 flex gap-1.5">
                      <span className="bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-md text-[10px] tracking-widest uppercase text-[#16284B] font-semibold">{prop.tipo}</span>
                      <span className={`px-2.5 py-1 rounded-md text-[10px] tracking-widest uppercase font-semibold text-white ${prop.finalidade === 'aluguel' ? 'bg-[#c9943a]' : 'bg-[#16284B]'}`}>{prop.finalidade === 'aluguel' ? 'Aluguel' : 'Venda'}</span>
                    </div>
                    <button className="absolute top-3 right-3 p-1.5 rounded-full bg-white/70 backdrop-blur-sm text-[#5d6b86] hover:text-[#c9943a]"><Heart size={18} /></button>
                  </div>
                  <div className="px-1">
                    <div className="flex justify-between items-start mb-1 gap-2">
                      <h3 className="font-semibold text-[#16284B] text-base line-clamp-1">{prop.titulo}</h3>
                      <span className="font-serif text-[#16284B] font-medium whitespace-nowrap">{prop.precoFmt}{prop.precoSufixo && <span className="text-xs font-sans text-[#5d6b86] font-normal">{prop.precoSufixo}</span>}</span>
                    </div>
                    <p className="text-xs text-[#5d6b86] mb-2 flex items-center gap-1"><MapPin size={12} /> {prop.bairro}</p>
                    <div className="flex items-center gap-3 text-xs text-[#7b95c8] font-medium">
                      {prop.quartos > 0 && <span className="flex items-center gap-1"><BedDouble size={14} className="text-[#c9943a]" /> {prop.quartos}</span>}
                      {prop.suites > 0 && <span className="flex items-center gap-1"><Bath size={14} className="text-[#c9943a]" /> {prop.suites}</span>}
                      {prop.area > 0 && <span className="flex items-center gap-1"><Maximize size={14} className="text-[#c9943a]" /> {prop.area}m²</span>}
                    </div>
                  </div>
                </div>
              ))}
              {!filtrados.length && <p className="text-[#5d6b86] col-span-2 text-center py-10">Nenhum imóvel encontrado.</p>}
            </div>
          </div>
        </div>

        {/* Mapa real */}
        <div className={`w-full lg:w-[55%] h-full relative transition-transform duration-300 ${viewMode === 'list' ? 'translate-x-full lg:translate-x-0 absolute lg:relative' : 'translate-x-0 relative'}`}>
          <div ref={mapDiv} className="absolute inset-0 z-0" />
        </div>

        {/* Toggle mobile */}
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-30 lg:hidden">
          <button onClick={() => { setViewMode(viewMode === 'list' ? 'map' : 'list'); setTimeout(() => mapInst.current?.invalidateSize(), 300); }}
            className="bg-[#16284B] text-white px-6 py-3 rounded-full shadow-2xl flex items-center gap-2 font-medium text-sm hover:bg-[#0f1c38]">
            {viewMode === 'list' ? <><MapIcon size={16} /> Mostrar Mapa</> : <><List size={16} /> Mostrar Lista</>}
          </button>
        </div>
      </main>
    </div>
  );
}
