// Páginas de detalhe — imóvel (PV-XXX) e bairro (slug).
// Roteamento via hash: #/imovel/pv-001 e #/bairro/candeias

function useHashRoute() {
  const [hash, setHash] = React.useState(() => window.location.hash || "");
  React.useEffect(() => {
    const onHash = () => setHash(window.location.hash || "");
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const m1 = hash.match(/^#\/imovel\/([a-zA-Z0-9-]+)/);
  if (m1) return { tipo: "imovel", id: m1[1].toUpperCase() };
  const m2 = hash.match(/^#\/bairro\/([a-zA-Z0-9-]+)/);
  if (m2) return { tipo: "bairro", id: m2[1].toLowerCase() };
  if (hash.match(/^#\/favoritos/)) return { tipo: "favoritos", id: null };
  if (hash.match(/^#\/favoritos/)) return { tipo: "favoritos", id: null };
  return { tipo: "home", id: null };
}

window.useHashRoute = useHashRoute;

function _setMeta(titulo, descricao) {
  document.title = titulo;
  let meta = document.querySelector('meta[name="description"]');
  if (!meta) {
    meta = document.createElement("meta");
    meta.setAttribute("name", "description");
    document.head.appendChild(meta);
  }
 

// Injeta JSON-LD do imóvel (RealEstateListing). Substitui se já existir.
function _setJsonLdImovel(imovel) {
  const id = "jsonld-imovel";
  let el = document.getElementById(id);
  if (!imovel) {
    if (el) el.remove();
    return;
  }
  const data = {
    "@context": "https://schema.org",
    "@type": "RealEstateListing",
    "name": imovel.titulo,
    "description": imovel.descricao,
    "url": `${location.origin}${location.pathname}#/imovel/${(imovel.codigo || "").toLowerCase()}`,
    "identifier": imovel.codigo,
    "image": imovel.img && (imovel.img.startsWith("http") ? imovel.img : `${location.origin}/${imovel.img.replace(/^\.+\//, "")}`),
    "datePosted": new Date().toISOString().slice(0, 10),
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Vitória da Conquista",
      "addressRegion": "BA",
      "addressCountry": "BR",
      "streetAddress": imovel.bairro
    },
    "offers": {
      "@type": "Offer",
      "price": imovel.preco,
      "priceCurrency": "BRL",
      "availability": "https://schema.org/InStock"
    },
    "numberOfRooms": imovel.quartos,
    "floorSize": { "@type": "QuantitativeValue", "value": imovel.area, "unitCode": "MTK" },
    "broker": { "@type": "RealEstateAgent", "name": "Priscila Vasconcelos", "identifier": "CRECI/BA 29.231" }
  };
  if (!el) {
    el = document.createElement("script");
    el.id = id;
    el.type = "application/ld+json";
    document.head.appendChild(el);
  }
  el.textContent = JSON.stringify(data);
} meta.setAttribute("content", descricao);
}

// Injeta JSON-LD do imóvel (RealEstateListing). Substitui se já existir.
function _setJsonLdImovel(imovel) {
  const id = "jsonld-imovel";
  let el = document.getElementById(id);
  if (!imovel) {
    if (el) el.remove();
    return;
  }
  const data = {
    "@context": "https://schema.org",
    "@type": "RealEstateListing",
    "name": imovel.titulo,
    "description": imovel.descricao,
    "url": `${location.origin}${location.pathname}#/imovel/${(imovel.codigo || "").toLowerCase()}`,
    "identifier": imovel.codigo,
    "image": imovel.img && (imovel.img.startsWith("http") ? imovel.img : `${location.origin}/${imovel.img.replace(/^\.+\//, "")}`),
    "datePosted": new Date().toISOString().slice(0, 10),
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Vitória da Conquista",
      "addressRegion": "BA",
      "addressCountry": "BR",
      "streetAddress": imovel.bairro
    },
    "offers": {
      "@type": "Offer",
      "price": imovel.preco,
      _setJsonLdImovel(imovel);
      window.scrollTo({ top: 0, behavior: "instant" });
    }
    return () => _setJsonLdImovel(null); "availability": "https://schema.org/InStock"
    },
    "numberOfRooms": imovel.quartos,
    "floorSize": { "@type": "QuantitativeValue", "value": imovel.area, "unitCode": "MTK" },
    "broker": { "@type": "RealEstateAgent", "name": "Priscila Vasconcelos", "identifier": "CRECI/BA 29.231" }
  };
  if (!el) {
    el = document.createElement("script");
    el.id = id;
    el.type = "application/ld+json";
    document.head.appendChild(el);
  }
  el.textContent = JSON.stringify(data);
}

function _slugBairro(nome) {
  return (nome || "").toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "-");
}

function _fmtMi(v) {
  if (v >= 1_000_000) return `R$ ${(v / 1_000_000).toFixed(2).replace(".", ",")} mi`;
  return `R$ ${(v / 1000).toFixed(0)} mil`;
}

const PANORAMA_FALLBACK_POR_CODIGO = {
  "PV-001": "https://pannellum.org/images/alma.jpg",
};

// ─────────── IMÓVEL ───────────
function ImovelDetalhe({ codigo, onVoltar }) {
  const [agendarOpen, setAgendarOpen] = React.useState(false);
  const imovel = React.useMemo(() => {
    return window.IMOVEIS.find(i => i.codigo === codigo) || null;
  }, [codigo]);

  React.useEffect(() => {
    if (imovel) {
      _setMeta(
        `${imovel.titulo} · ${imovel.precoLabel} · ${imovel.bairro} | Priscila Vasconcelos`,
        `${imovel.tipo} ${imovel.bairro}: ${imovel.descricao}. ${imovel.quartos} quartos, ${imovel.area} m². Código ${imovel.codigo}.`
      );
      _setJsonLdImovel(imovel);
      window.scrollTo({ top: 0, behavior: "instant" });
    }
    return () => _setJsonLdImovel(null);
  }, [imovel]);

  if (!imovel) {
    return (
      <div className="detalhe-wrap">
        <button className="detalhe-back" onClick={onVoltar}>← voltar</button>
        <div className="detalhe-erro">
          <h1>Imóvel não encontrado</h1>
          <p>Esse código não existe ou foi vendido. <a href="#imoveis" onClick={onVoltar}>Ver os disponíveis</a></p>
        </div>
      </div>
    );
  }

  const txtWhats = `Oi Priscila, vi o imóvel ${imovel.codigo} (${imovel.titulo}) no site. Quero saber mais.`;
  const linkWhats = `https://wa.me/5577988193344?text=${encodeURIComponent(txtWhats)}`;
  const panoramaUrl = imovel.panorama_url || PANORAMA_FALLBACK_POR_CODIGO[imovel.codigo] || "";

  const Tour360Comp = window.Tour360;
  const MiniMapaComp = window.MiniMapaImovel;

  const similares = window.IMOVEIS
    .filter(i => i.bairro === imovel.bairro && i.codigo !== imovel.codigo)
    .slice(0, 3);

  return (
    <div className="detalhe-wrap">
      <a href="#" className="detalhe-back" onClick={(e) => { e.preventDefault(); onVoltar(); }}>← voltar à listagem</a>

      <header className="detalhe-head">
        <div>
          <span className="detalhe-codigo">{imovel.codigo}</span>
          <span className="detalhe-status">{imovel.status}</span>
        </div>
        <h1 className="detalhe-title">{imovel.titulo}</h1>
        <div className="detalhe-meta">
          <a href={`#/bairro/${_slugBairro(imovel.bairro)}`} className="detalhe-bairro">📍 {imovel.bairro}</a>
          <span className="detalhe-tipo">{imovel.tipo}</span>
          <span className="detalhe-preco">{imovel.precoLabel}</span>
        </div>
      </header>

      <figure className="detalhe-foto">
        <img src={imovel.img} alt={imovel.titulo}/>
        <figcaption>Foto ilustrativa · solicite o dossiê completo com todas as imagens.</figcaption>
      </figure>

      {panoramaUrl && Tour360Comp && (
        <Tour360Comp panoramaUrl={panoramaUrl} titulo={imovel.titulo}/>
      )}

      {imovel.tour_360_url && (
        <section className="detalhe-tour-externo" aria-label="Tour virtual 360 graus">
          <h2>Tour virtual 360°</h2>
          <div className="detalhe-tour-frame">
            <iframe
              src={imovel.tour_360_url}
              title={`Tour 360 — ${imovel.titulo}`}
              allow="xr-spatial-tracking; gyroscope; accelerometer; fullscreen"
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
            />
          </div>
        </section>
      )}

      {MiniMapaComp && (
        <MiniMapaComp bairro={imovel.bairro} titulo={imovel.titulo}/>
      )}

      <div className="detalhe-cols">
        <section className="detalhe-corpo">
          <h2>Sobre o imóvel</h2>
          <p className="detalhe-desc">{imovel.descricao}</p>

          <h3>Especificações</h3>
          <dl className="detalhe-specs">
            <div><dt>Área útil</dt><dd>{imovel.area} m²</dd></div>
            <div><dt>Quartos</dt><dd>{imovel.quartos}</dd></div>
            <div><dt>Suítes</dt><dd>{imovel.suites}</dd></div>
            <div><dt>Vagas</dt><dd>{imovel.vagas}</dd></div>
            <div><dt>Match IA</dt><dd>{imovel.iaMatch}%</dd></div>
            <div><dt>Bairro</dt><dd>{imovel.bairro}</dd></div>
          </dl>

          <h3>Diferenciais</h3>
          <ul className="detalhe-tags">
            {imovel.tags.map(t => <li key={t}>{t}</li>)}
          </ul>

          <div className="detalhe-aviso">
            <strong>Sobre o anúncio:</strong> a Priscila visita o imóvel pessoalmente antes de listar.
            Os dados acima foram conferidos in loco. Se algo não bater na visita, ela tira do site.
          </div>
        </section>

        <aside className="detalhe-lateral">
          <button type="button" className="detalhe-cta-agendar" onClick={() => setAgendarOpen(true)}>
            📅 Agendar visita
          </button>

          <div className="detalhe-cta-card">
            <span className="detalhe-cta-label">Quanto fica financiando?</span>
            <p>Use o simulador com o valor já pré-carregado.</p>
            <a href="#simulador" className="detalhe-cta-secondary" onClick={() => {
              setTimeout(() => {
                window.dispatchEvent(new CustomEvent("simulador:prefill", {
                  detail: { valor: imovel.preco, bairro: imovel.bairro, tipo: imovel.tipo }
                }));
              }, 100);
            }}>Simular financiamento →</a>
          </div>

          <a href={linkWhats} target="_blank" rel="noopener" className="detalhe-whats">
            <svg viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M13.6 2.4A7.5 7.5 0 001.5 12.3L.5 15.5l3.3-1A7.5 7.5 0 1013.6 2.4z"/></svg>
            <div>
              <strong>Falar agora pelo WhatsApp</strong>
              <span>(77) 9 8819-3344 · resposta em minutos</span>
            </div>
          </a>

          <div className="detalhe-mini-priscila">
            <img src="../assets/priscila-new-hero.jpeg" alt="Priscila Vasconcelos"/>
            <div>
              <strong>Priscila Vasconcelos</strong>
              <span>CRECI/BA 29.231 · 184 fechamentos</span>
            </div>
          </div>
        </aside>
      </div>

      {similares.length > 0 && (
        <section className="detalhe-similares">
          <h2>Outros imóveis em {imovel.bairro}</h2>
          <div className="detalhe-similares-grid">
            {similares.map(s => (
              <a key={s.codigo} href={`#/imovel/${s.codigo.toLowerCase()}`} className="detalhe-similar-card">
                <img src={s.img} alt={s.titulo} loading="lazy"/>
                <div>
                  <span className="detalhe-similar-codigo">{s.codigo}</span>
                  <strong>{s.titulo}</strong>
                  <span className="detalhe-similar-preco">{s.precoLabel} · {s.area} m²</span>
                </div>
              </a>
            ))}
          </div>
        </section>
      )}

      {agendarOpen && (
        <AgendarVisita
          codigo={imovel.codigo}
          titulo={imovel.titulo}
          bairro={imovel.bairro}
          precoLabel={imovel.precoLabel}
          onClose={() => setAgendarOpen(false)}
        />
      )}
    </div>
  );
}

// ─────────── BAIRRO ───────────
function BairroDetalhe({ slug, onVoltar }) {
  const bairro = React.useMemo(() => {
    return window.BAIRROS.find(b => _slugBairro(b.nome) === slug || b.id === slug) || null;
  }, [slug]);

  const imoveis = React.useMemo(() => {
    if (!bairro) return [];
    return window.IMOVEIS.filter(i => _slugBairro(i.bairro) === _slugBairro(bairro.nome));
  }, [bairro]);

  React.useEffect(() => {
    if (bairro) {
      _setMeta(
        `Imóveis em ${bairro.nome} · Vitória da Conquista | Priscila Vasconcelos`,
        `${bairro.nome}: ${bairro.perfil || "imóveis selecionados pela corretora Priscila"}. ${imoveis.length} imóveis ativos curados.`
      );
      window.scrollTo({ top: 0, behavior: "instant" });
    }
  }, [bairro, imoveis.length]);

  if (!bairro) {
    return (
      <div className="detalhe-wrap">
        <button className="detalhe-back" onClick={onVoltar}>← voltar</button>
        <div className="detalhe-erro">
          <h1>Bairro não encontrado</h1>
          <p>Talvez ainda não tenhamos imóveis nesse bairro. <a href="#bairros" onClick={onVoltar}>Ver bairros disponíveis</a></p>
        </div>
      </div>
    );
  }

  const valorMin = imoveis.length ? Math.min(...imoveis.map(i => i.preco)) : 0;
  const valorMax = imoveis.length ? Math.max(...imoveis.map(i => i.preco)) : 0;

  return (
    <div className="detalhe-wrap detalhe-wrap-bairro">
      <a href="#" className="detalhe-back" onClick={(e) => { e.preventDefault(); onVoltar(); }}>← voltar</a>

      <header className="detalhe-head">
        <span className="detalhe-codigo">📍 Bairro · Vitória da Conquista — BA</span>
        <h1 className="detalhe-title">{bairro.emoji} {bairro.nome}</h1>
        {bairro.perfil && <p className="detalhe-perfil">{bairro.perfil}</p>}
      </header>

      <div className="bairro-stats">
        <div><b>{imoveis.length}</b><span>imóveis ativos</span></div>
        {valorMin > 0 && <div><b>{_fmtMi(valorMin)}</b><span>a partir de</span></div>}
        {valorMax > 0 && <div><b>{_fmtMi(valorMax)}</b><span>até</span></div>}
      </div>

      {imoveis.length > 0 ? (
        <PropertyGrid filter={{ bairro: bairro.nome }} variant="editorial" subtitle={`Imóveis em ${bairro.nome}`}/>
      ) : (
        <div className="detalhe-vazio">
          <p>No momento não há imóveis ativos em {bairro.nome}.</p>
          <p>Quer que a Priscila te avise quando aparecer? <a href="https://wa.me/5577988193344" target="_blank" rel="noopener">Mande um WhatsApp.</a></p>
        </div>
      )}

      <section className="bairro-tipico">
        <h2>O que esperar de {bairro.nome}</h2>
        <div className="bairro-tipico-grid">
          <div>
            <h4>Perfil</h4>
            <p>{bairro.perfil || "Bairro residencial com mix variado de tipologias."}</p>
          </div>
          <div>
            <h4>Para quem indicaria</h4>
            <p>Use o chat com a IA — ela cruza seu perfil (família, deslocamento, orçamento) com os bairros e diz se {bairro.nome} faz sentido.</p>
          </div>
          <div>
            <h4>Quer avaliar um imóvel aqui?</h4>
            <p><a href="#avaliacao" onClick={onVoltar}>Use o avaliador de m²</a> — devolve faixa de valor em 30 segundos.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

window.ImovelDetalhe = ImovelDetalhe;
window.BairroDetalhe = BairroDetalhe;
