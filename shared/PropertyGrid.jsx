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
  const linkDetalhe = imovel.codigo ? `#/imovel/${imovel.codigo.toLowerCase()}` : "#contato";
  const matchValor = typeof imovel.matchCalculado === "number" ? imovel.matchCalculado : imovel.iaMatch;
  const matchLabel = imovel.matchCalculado != null
    ? `${matchValor}% match com sua busca`
    : `${matchValor}% match IA`;
  const compartilhar = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const linha1 = `Oi, vi este imóvel no site da Priscila Vasconcelos:`;
    const linha2 = `${imovel.titulo} — ${imovel.precoLabel}`;
    const linha3 = `${imovel.bairro} · ${imovel.quartos} quartos · ${imovel.area} m²`;
    const linha4 = `Código: ${imovel.codigo || imovel.id}`;
    const txt = `${linha1}\n\n${linha2}\n${linha3}\n${linha4}\n\nQueria saber mais.`;
    const url = `https://wa.me/5577988193344?text=${encodeURIComponent(txt)}`;
    window.open(url, "_blank", "noopener,noreferrer");
  };
  return (
    <article className={`pcard pcard-${variant}`} ref={ref}>
      <div className="pcard-inner">
        <div className="pcard-photo-wrap">
          <img src={imovel.img} alt={imovel.titulo} className="pcard-photo" loading="lazy"/>
          <div className="pcard-photo-grade"/>
          <div className="pcard-tags">
            <span className="pcard-status">{imovel.status}</span>
            <span className="pcard-match" title={matchLabel}>
              <svg viewBox="0 0 12 12" width="10" height="10" fill="none">
                <circle cx="6" cy="6" r="2" fill="currentColor"/>
                <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth=".8" opacity=".4"/>
              </svg>
              {matchValor}% match{imovel.matchCalculado != null ? "" : " IA"}
            </span>
          </div>
          <div className="pcard-bairro">{imovel.bairro}</div>
          {imovel.codigo && <div className="pcard-codigo">{imovel.codigo}</div>}
        </div>
        <div className="pcard-body">
          <div className="pcard-head">
            <div className="pcard-tipo">{imovel.tipo}</div>
            <div className="pcard-preco">{imovel.precoLabel}</div>
          </div>
          <h3 className="pcard-titulo"><a href={linkDetalhe} className="pcard-titulo-link">{imovel.titulo}</a></h3>
          <p className="pcard-desc">{imovel.descricao}</p>
          <div className="pcard-stats">
            <span><strong>{imovel.quartos}</strong> quartos</span>
            <span><strong>{imovel.suites}</strong> suítes</span>
            <span><strong>{imovel.vagas}</strong> vagas</span>
            <span><strong>{imovel.area}</strong> m²</span>
          </div>
          <div className="pcard-actions">
            <a className="pcard-cta" href={linkDetalhe}>Ver detalhes →</a>
            <button className="pcard-share" type="button" onClick={compartilhar} aria-label="Compartilhar no WhatsApp" title="Enviar pra alguém pelo WhatsApp">
              <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M13.6 2.4A7.5 7.5 0 001.5 12.3L.5 15.5l3.3-1A7.5 7.5 0 1013.6 2.4zM8 13.6a5.6 5.6 0 01-2.8-.8l-.2-.1-2 .6.6-1.9-.1-.2A5.6 5.6 0 118 13.6zm3.1-4.2c-.2-.1-1-.5-1.2-.5-.2-.1-.3-.1-.4.1l-.5.6c-.1.1-.2.1-.4 0a4.5 4.5 0 01-2.2-2c-.2-.3.2-.3.5-.9 0-.1 0-.2 0-.3l-.5-1.2c-.1-.3-.3-.3-.4-.3h-.4a.7.7 0 00-.5.2 2 2 0 00-.6 1.5c0 .9.6 1.7.7 1.9a6.7 6.7 0 002.6 2.3c1.7.7 1.7.5 2 .4a1.7 1.7 0 001.2-.8c.1-.3.1-.6 0-.6 0-.1-.2-.1-.4-.2z"/></svg>
            </button>
            {window.BotaoComparar
              ? <window.BotaoComparar codigo={imovel.codigo}/>
              : null}
            {window.BotaoFavoritar
              ? <window.BotaoFavoritar codigo={imovel.codigo} variant={variant}/>
              : <button className="pcard-fav" type="button" aria-label="Favoritar" title="Salvar para depois">
                  <svg viewBox="0 0 16 16" width="14" height="14" fill="none"><path d="M8 14s-5-3-5-7.5A3 3 0 018 4a3 3 0 015 2.5C13 11 8 14 8 14z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/></svg>
                </button>}
          </div>
        </div>
      </div>
      <div className="pcard-shine" aria-hidden="true"/>
    </article>
  );
}

function AlertaBuscaBtn({ filter }) {
  const [open, setOpen] = React.useState(false);
  const [nome, setNome] = React.useState("");
  const [contato, setContato] = React.useState("");
  const [status, setStatus] = React.useState("idle"); // idle|loading|ok|err
  const [erro, setErro] = React.useState("");
  const enviar = async (e) => {
    e.preventDefault();
    if (!nome.trim() || !contato.trim()) {
      setErro("Preencha nome e contato.");
      return;
    }
    setStatus("loading");
    setErro("");
    try {
      const r = await fetch("/api/alerta-busca", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nome.trim(), contato: contato.trim(), filtros: filter || {} }),
      });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error(j.detail || "Falha ao salvar alerta");
      }
      setStatus("ok");
    } catch (ex) {
      setStatus("err");
      setErro(ex.message || "Erro ao salvar.");
    }
  };
  if (status === "ok") {
    return (
      <div className="pgrid-alerta pgrid-alerta-ok">
        ✓ Alerta criado. A Priscila avisa no seu WhatsApp quando aparecer um match.
      </div>
    );
  }
  if (!open) {
    return (
      <button type="button" className="pgrid-alerta-btn" onClick={() => setOpen(true)}>
        🔔 Me avisar quando tiver novos
      </button>
    );
  }
  return (
    <form className="pgrid-alerta-form" onSubmit={enviar}>
      <input
        type="text"
        placeholder="Seu nome"
        value={nome}
        onChange={e => setNome(e.target.value)}
        disabled={status === "loading"}
      />
      <input
        type="text"
        placeholder="WhatsApp ou e-mail"
        value={contato}
        onChange={e => setContato(e.target.value)}
        disabled={status === "loading"}
      />
      <button type="submit" disabled={status === "loading"}>
        {status === "loading" ? "Salvando…" : "Salvar"}
      </button>
      {erro && <span className="pgrid-alerta-err">{erro}</span>}
    </form>
  );
}

function PropertyGrid({ filter, variant = "cerulean", title = "Imóveis em destaque", subtitle, emptyMessage }) {
  const filtroAtivo = !!(filter && (filter.bairro || filter.tipo || filter.faixa || filter.tema));
  const imoveis = React.useMemo(() => {
    const _filtroAtivo = !!(filter && (filter.bairro || filter.tipo || filter.faixa || filter.tema));
    const lista = window.IMOVEIS.filter(i => {
      if (!filter) return true;
      if (filter.bairro && i.bairro !== filter.bairro) return false;
      if (filter.tipo && i.tipo !== filter.tipo) return false;
      if (filter.faixa === "até 500") return i.preco <= 500000;
      if (filter.faixa === "500 a 1mi") return i.preco > 500000 && i.preco <= 1000000;
      if (filter.faixa === "1mi a 2mi") return i.preco > 1000000 && i.preco <= 2000000;
      if (filter.faixa === "acima 2mi") return i.preco > 2000000;
      if (filter.tema && !(i.temas || []).includes(filter.tema)) return false;
      return true;
    });
    if (!_filtroAtivo) return lista;
    // Calcula match dinâmico (40 bairro + 25 tipo + 25 faixa + 10 tema)
    const comMatch = lista.map(i => {
      let score = 60; // base
      if (filter.bairro && i.bairro === filter.bairro) score += 15;
      if (filter.tipo && i.tipo === filter.tipo) score += 10;
      if (filter.faixa) score += 8;
      if (filter.tema && (i.temas || []).includes(filter.tema)) score += 7;
      // Ajuste fino: imovel com mais tags relacionadas ganha pontinho
      const baseIa = typeof i.iaMatch === "number" ? i.iaMatch : 80;
      const matchCalculado = Math.min(99, Math.round(score * 0.5 + baseIa * 0.5));
      return { ...i, matchCalculado };
    });
    comMatch.sort((a, b) => b.matchCalculado - a.matchCalculado);
    return comMatch;
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
      {filtroAtivo && <AlertaBuscaBtn filter={filter} />}
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

Object.assign(window, { PropertyCard, PropertyGrid, useTilt, AlertaBuscaBtn });
