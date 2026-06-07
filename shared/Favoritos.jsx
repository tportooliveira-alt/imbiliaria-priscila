// Favoritos — wishlist persistida em localStorage, hook + botão + página dedicada.
// Eventos globais:
//   - "favoritos:mudou"  → dispara quando lista muda (qualquer aba)
//   - "comparador:abrir" → escuta para abrir drawer

const FAV_KEY = "pv-favoritos-v1";

function _lerFavoritos() {
  try {
    const raw = localStorage.getItem(FAV_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch { return []; }
}

function _gravarFavoritos(lista) {
  try {
    localStorage.setItem(FAV_KEY, JSON.stringify(lista));
    window.dispatchEvent(new CustomEvent("favoritos:mudou", { detail: { lista } }));
  } catch {}
}

function useFavoritos() {
  const [lista, setLista] = React.useState(_lerFavoritos);
  React.useEffect(() => {
    const onMudou = (e) => setLista(e.detail?.lista || _lerFavoritos());
    const onStorage = (e) => { if (e.key === FAV_KEY) setLista(_lerFavoritos()); };
    window.addEventListener("favoritos:mudou", onMudou);
    window.addEventListener("storage", onStorage);
    return () => {
      window.removeEventListener("favoritos:mudou", onMudou);
      window.removeEventListener("storage", onStorage);
    };
  }, []);

  const ehFavorito = React.useCallback((codigo) => lista.includes(codigo), [lista]);

  const alternar = React.useCallback((codigo) => {
    if (!codigo) return;
    const atual = _lerFavoritos();
    const nova = atual.includes(codigo)
      ? atual.filter(c => c !== codigo)
      : [...atual, codigo];
    _gravarFavoritos(nova);
  }, []);

  const limpar = React.useCallback(() => _gravarFavoritos([]), []);

  return { lista, ehFavorito, alternar, limpar };
}

function BotaoFavoritar({ codigo, variant = "card" }) {
  const { ehFavorito, alternar } = useFavoritos();
  const ativo = ehFavorito(codigo);
  const onClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    alternar(codigo);
  };
  return (
    <button
      type="button"
      className={`pcard-fav ${ativo ? "is-fav" : ""} pcard-fav-${variant}`}
      onClick={onClick}
      aria-label={ativo ? "Remover dos favoritos" : "Adicionar aos favoritos"}
      aria-pressed={ativo}
      title={ativo ? "Remover dos favoritos" : "Salvar para depois"}
    >
      <svg viewBox="0 0 16 16" width="14" height="14"
        fill={ativo ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.4">
        <path d="M8 14s-5-3-5-7.5A3 3 0 018 4a3 3 0 015 2.5C13 11 8 14 8 14z" strokeLinejoin="round"/>
      </svg>
    </button>
  );
}

function ContadorFavoritosNav({ onClick }) {
  const { lista } = useFavoritos();
  if (lista.length === 0) {
    return (
      <a href="#/favoritos" className="navH-fav" onClick={(e) => { e.preventDefault(); onClick && onClick(); window.location.hash = "#/favoritos"; }} title="Favoritos">
        <svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.4">
          <path d="M8 14s-5-3-5-7.5A3 3 0 018 4a3 3 0 015 2.5C13 11 8 14 8 14z" strokeLinejoin="round"/>
        </svg>
      </a>
    );
  }
  return (
    <a href="#/favoritos" className="navH-fav navH-fav-ativo" onClick={(e) => { e.preventDefault(); onClick && onClick(); window.location.hash = "#/favoritos"; }} title="Ver favoritos">
      <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor" stroke="currentColor" strokeWidth="1.4">
        <path d="M8 14s-5-3-5-7.5A3 3 0 018 4a3 3 0 015 2.5C13 11 8 14 8 14z" strokeLinejoin="round"/>
      </svg>
      <span className="navH-fav-contador">{lista.length}</span>
    </a>
  );
}

function PaginaFavoritos({ onVoltar }) {
  const { lista, alternar, limpar } = useFavoritos();
  const PropertyCardComp = window.PropertyCard;

  const imoveis = React.useMemo(() => {
    if (!Array.isArray(window.IMOVEIS)) return [];
    return window.IMOVEIS.filter(i => lista.includes(i.codigo));
  }, [lista]);

  React.useEffect(() => {
    document.title = `Meus favoritos (${imoveis.length}) · Priscila Vasconcelos`;
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [imoveis.length]);

  const abrirComparador = () => {
    if (imoveis.length < 2) return;
    window.dispatchEvent(new CustomEvent("comparador:abrir", { detail: { codigos: imoveis.slice(0, 3).map(i => i.codigo) } }));
  };

  const enviarPraPriscila = () => {
    if (imoveis.length === 0) return;
    const linhas = imoveis.map(i => `• ${i.codigo} — ${i.titulo} (${i.precoLabel})`).join("\n");
    const txt = `Oi Priscila! Selecionei estes imóveis no seu site, queria conversar sobre eles:\n\n${linhas}\n\nPode me passar mais detalhes?`;
    window.open(`https://wa.me/5577999395511?text=${encodeURIComponent(txt)}`, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="favoritos-pag">
      <a href="#" className="detalhe-back" onClick={(e) => { e.preventDefault(); onVoltar && onVoltar(); }}>← voltar</a>

      <header className="favoritos-head">
        <span className="eyebrow">§ Sua seleção</span>
        <h1>Meus favoritos</h1>
        <p className="favoritos-deck">
          {imoveis.length === 0
            ? "Você ainda não salvou nenhum imóvel. Clique no coração de qualquer card para guardar aqui."
            : `${imoveis.length} ${imoveis.length === 1 ? "imóvel salvo" : "imóveis salvos"} para você revisitar com calma.`}
        </p>
        {imoveis.length > 0 && (
          <div className="favoritos-acoes">
            <button className="aval-cta" type="button" onClick={enviarPraPriscila}>
              Enviar lista para Priscila (WhatsApp)
            </button>
            {imoveis.length >= 2 && (
              <button className="btn-secondary" type="button" onClick={abrirComparador}>
                Comparar lado a lado
              </button>
            )}
            <button className="btn-secondary" type="button" onClick={limpar}>
              Limpar lista
            </button>
          </div>
        )}
      </header>

      {imoveis.length === 0 ? (
        <div className="favoritos-vazio">
          <a href="#imoveis" className="aval-cta" onClick={onVoltar}>Ver imóveis disponíveis</a>
        </div>
      ) : (
        <div className="pgrid-list favoritos-grid">
          {imoveis.map(i => PropertyCardComp
            ? <PropertyCardComp key={i.codigo} imovel={i} variant="editorial"/>
            : <div key={i.codigo}>{i.titulo}</div>
          )}
        </div>
      )}
    </div>
  );
}

Object.assign(window, { useFavoritos, BotaoFavoritar, ContadorFavoritosNav, PaginaFavoritos });
