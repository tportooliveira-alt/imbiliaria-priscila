// PropertyGrid — filtered property cards with 3D tilt hover
// Props: filter = {bairro, tipo, faixa}, variant

function useTilt() {
  const ref = React.useRef(null);
  React.useEffect(() => {
    const el = ref.current; if (!el) return;
    let raf;
    const onMove = e => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        el.style.setProperty("--tilt-x", `${-y * 6}deg`);
        el.style.setProperty("--tilt-y", `${x * 8}deg`);
        el.style.setProperty("--tilt-mx", `${(x + 0.5) * 100}%`);
        el.style.setProperty("--tilt-my", `${(y + 0.5) * 100}%`);
      });
    };
    const onLeave = () => {
      cancelAnimationFrame(raf);
      el.style.setProperty("--tilt-x", "0deg");
      el.style.setProperty("--tilt-y", "0deg");
    };
    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
    return () => {
      el.removeEventListener("mousemove", onMove);
      el.removeEventListener("mouseleave", onLeave);
      cancelAnimationFrame(raf);
    };
  }, []);
  return ref;
}

function PropertyCard({ imovel, variant }) {
  const ref = useTilt();
  return (
    <article className={`pcard pcard-${variant}`} ref={ref}>
      <div className="pcard-inner">
        <div className="pcard-photo-wrap">
          <img src={imovel.img} alt={imovel.titulo} className="pcard-photo" loading="lazy"/>
          <div className="pcard-photo-grade"/>
          <div className="pcard-tags">
            <span className="pcard-status">{imovel.status}</span>
            <span className="pcard-match">
              <svg viewBox="0 0 12 12" width="10" height="10" fill="none">
                <circle cx="6" cy="6" r="2" fill="currentColor"/>
                <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth=".8" opacity=".4"/>
              </svg>
              {imovel.iaMatch}% match IA
            </span>
          </div>
          <div className="pcard-bairro">{imovel.bairro}</div>
        </div>
        <div className="pcard-body">
          <div className="pcard-head">
            <div className="pcard-tipo">{imovel.tipo}</div>
            <div className="pcard-preco">{imovel.precoLabel}</div>
          </div>
          <h3 className="pcard-titulo">{imovel.titulo}</h3>
          <p className="pcard-desc">{imovel.descricao}</p>
          <div className="pcard-stats">
            <span><strong>{imovel.quartos}</strong> quartos</span>
            <span><strong>{imovel.suites}</strong> suítes</span>
            <span><strong>{imovel.vagas}</strong> vagas</span>
            <span><strong>{imovel.area}</strong> m²</span>
          </div>
          <div className="pcard-actions">
            <a className="pcard-cta" href="#contato">Tenho interesse →</a>
            <button className="pcard-fav" aria-label="Favoritar">
              <svg viewBox="0 0 16 16" width="14" height="14" fill="none"><path d="M8 14s-5-3-5-7.5A3 3 0 018 4a3 3 0 015 2.5C13 11 8 14 8 14z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/></svg>
            </button>
          </div>
        </div>
      </div>
      <div className="pcard-shine" aria-hidden="true"/>
    </article>
  );
}

function PropertyGrid({ filter, variant = "cerulean", title = "Imóveis em destaque", subtitle, emptyMessage }) {
  const imoveis = React.useMemo(() => {
    return window.IMOVEIS.filter(i => {
      if (!filter) return true;
      if (filter.bairro && i.bairro !== filter.bairro) return false;
      if (filter.tipo && i.tipo !== filter.tipo) return false;
      if (filter.faixa === "até 500") return i.preco <= 500000;
      if (filter.faixa === "500 a 1mi") return i.preco > 500000 && i.preco <= 1000000;
      if (filter.faixa === "1mi a 2mi") return i.preco > 1000000 && i.preco <= 2000000;
      if (filter.faixa === "acima 2mi") return i.preco > 2000000;
      return true;
    });
  }, [filter]);

  return (
    <section className={`pgrid pgrid-${variant}`} id="imoveis">
      <header className="pgrid-head">
        <div>
          <span className="eyebrow">{title}</span>
          {subtitle && <h2 className="pgrid-title">{subtitle}</h2>}
        </div>
        <div className="pgrid-meta">
          <span className="pgrid-count">
            <span className="pgrid-count-big">{imoveis.length}</span>
            <span className="pgrid-count-sm">imóveis<br/>filtrados</span>
          </span>
        </div>
      </header>
      {imoveis.length === 0 ? (
        <div className="pgrid-empty">
          <span>💭</span>
          <p>{emptyMessage || "Nenhum imóvel com esses filtros. Ajuste ou converse com a IA — ela ajuda a achar."}</p>
        </div>
      ) : (
        <div className="pgrid-list">
          {imoveis.map(i => <PropertyCard key={i.id} imovel={i} variant={variant}/>)}
        </div>
      )}
    </section>
  );
}

Object.assign(window, { PropertyCard, PropertyGrid, useTilt });
