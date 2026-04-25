// BuscaBairros — horizontal search bar with ONLY bairro filter (plus optional tipo + faixa)
// Inspired by Paulo Victor reference but simpler: bairro is the primary axis.
// Live-filters the IMOVEIS grid when changed.
// Props: variant, onFilterChange(filter)

function BuscaBairros({ variant = "cerulean", onFilterChange, defaultBairro = "" }) {
  const [bairro, setBairro] = React.useState(defaultBairro);
  const [tipo, setTipo]     = React.useState("");
  const [faixa, setFaixa]   = React.useState("");
  const [showBairros, setShowBairros] = React.useState(false);

  React.useEffect(() => {
    onFilterChange && onFilterChange({ bairro, tipo, faixa });
  }, [bairro, tipo, faixa]);

  const count = React.useMemo(() => {
    return window.IMOVEIS.filter(i => {
      if (bairro && i.bairro !== bairro) return false;
      if (tipo && i.tipo !== tipo) return false;
      if (faixa === "até 500") return i.preco <= 500000;
      if (faixa === "500 a 1mi") return i.preco > 500000 && i.preco <= 1000000;
      if (faixa === "1mi a 2mi") return i.preco > 1000000 && i.preco <= 2000000;
      if (faixa === "acima 2mi") return i.preco > 2000000;
      return true;
    }).length;
  }, [bairro, tipo, faixa]);

  return (
    <div className={`bbsearch bbsearch-${variant}`}>
      <div className="bb-row">
        {/* Bairro — primary */}
        <div className="bb-field bb-field-primary">
          <label className="bb-label">Bairro</label>
          <button className="bb-select bb-select-bairro" onClick={() => setShowBairros(v => !v)} type="button">
            <svg viewBox="0 0 16 16" width="14" height="14" fill="none" className="bb-icon">
              <path d="M8 1c-2.8 0-5 2.2-5 5 0 3.8 5 9 5 9s5-5.2 5-9c0-2.8-2.2-5-5-5z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/>
              <circle cx="8" cy="6" r="1.8" stroke="currentColor" strokeWidth="1.3"/>
            </svg>
            <span className={bairro ? "bb-value" : "bb-placeholder"}>
              {bairro || "Todos os bairros"}
            </span>
            <svg viewBox="0 0 12 12" width="10" height="10" className="bb-chev" fill="none">
              <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          {showBairros && (
            <div className="bb-dropdown" onClick={() => setShowBairros(false)}>
              <button className="bb-opt" onClick={() => setBairro("")}>
                <span>Todos os bairros</span>
                <span className="bb-opt-count">{window.IMOVEIS.length}</span>
              </button>
              {window.BAIRROS.map(b => (
                <button key={b.id} className={`bb-opt ${bairro === b.nome ? "active" : ""}`} onClick={() => setBairro(b.nome)}>
                  <span className="bb-opt-emoji">{b.emoji}</span>
                  <div className="bb-opt-main">
                    <span className="bb-opt-nome">{b.nome}</span>
                    <span className="bb-opt-det">{b.destaque}</span>
                  </div>
                  <span className="bb-opt-count">{b.imoveis}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Tipo */}
        <div className="bb-field">
          <label className="bb-label">Tipo</label>
          <select className="bb-select" value={tipo} onChange={e => setTipo(e.target.value)}>
            <option value="">Todos os tipos</option>
            <option value="Casa">Casa</option>
            <option value="Apartamento">Apartamento</option>
          </select>
        </div>

        {/* Faixa */}
        <div className="bb-field">
          <label className="bb-label">Faixa de preço</label>
          <select className="bb-select" value={faixa} onChange={e => setFaixa(e.target.value)}>
            <option value="">Qualquer valor</option>
            <option value="até 500">Até R$ 500 mil</option>
            <option value="500 a 1mi">R$ 500 mil – R$ 1 mi</option>
            <option value="1mi a 2mi">R$ 1 mi – R$ 2 mi</option>
            <option value="acima 2mi">Acima de R$ 2 mi</option>
          </select>
        </div>

        {/* CTA */}
        <button className="bb-submit" type="button">
          <svg viewBox="0 0 16 16" width="14" height="14" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/><path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
          <span>Encontrar imóvel</span>
          <span className="bb-submit-count">{count}</span>
        </button>
      </div>

      {/* Live status */}
      <div className="bb-status">
        <span className="bb-live-dot"/>
        <span>IA buscando em tempo real · {count} imóveis encontrados</span>
      </div>
    </div>
  );
}

Object.assign(window, { BuscaBairros });
