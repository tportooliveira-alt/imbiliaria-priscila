// Comparador — drawer lateral comparando até 3 imóveis lado a lado.
// Estado vive no localStorage (chave pv-comparador-v1) para persistir entre páginas.
// Abre via evento "comparador:abrir" {codigos:[]} ou botão flutuante quando >=2 selecionados.

const COMP_KEY = "pv-comparador-v1";
const COMP_MAX = 3;

function _lerComp() {
  try {
    const raw = localStorage.getItem(COMP_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr.slice(0, COMP_MAX) : [];
  } catch { return []; }
}

function _gravarComp(lista) {
  try {
    localStorage.setItem(COMP_KEY, JSON.stringify(lista));
    window.dispatchEvent(new CustomEvent("comparador:mudou", { detail: { lista } }));
  } catch {}
}

function useComparador() {
  const [lista, setLista] = React.useState(_lerComp);
  React.useEffect(() => {
    const onMudou = (e) => setLista(e.detail?.lista || _lerComp());
    window.addEventListener("comparador:mudou", onMudou);
    return () => window.removeEventListener("comparador:mudou", onMudou);
  }, []);

  const noComp = React.useCallback((codigo) => lista.includes(codigo), [lista]);

  const alternar = React.useCallback((codigo) => {
    if (!codigo) return;
    const atual = _lerComp();
    if (atual.includes(codigo)) {
      _gravarComp(atual.filter(c => c !== codigo));
    } else if (atual.length < COMP_MAX) {
      _gravarComp([...atual, codigo]);
    } else {
      window.dispatchEvent(new CustomEvent("toast", { detail: { msg: `Máximo ${COMP_MAX} imóveis no comparador.` } }));
    }
  }, []);

  const limpar = React.useCallback(() => _gravarComp([]), []);

  const definir = React.useCallback((codigos) => {
    _gravarComp((codigos || []).slice(0, COMP_MAX));
  }, []);

  return { lista, noComp, alternar, limpar, definir };
}

function BotaoComparar({ codigo }) {
  const { noComp, alternar } = useComparador();
  const ativo = noComp(codigo);
  return (
    <button
      type="button"
      className={`pcard-cmp ${ativo ? "is-cmp" : ""}`}
      onClick={(e) => { e.preventDefault(); e.stopPropagation(); alternar(codigo); }}
      aria-pressed={ativo}
      title={ativo ? "Remover do comparador" : "Adicionar ao comparador"}
      aria-label={ativo ? "Remover do comparador" : "Adicionar ao comparador"}
    >
      <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.4">
        <path d="M2 4h5v8H2zM9 4h5v8H9z"/>
      </svg>
    </button>
  );
}

function _fmtNum(v) {
  if (v == null || v === "") return "—";
  return typeof v === "number" ? v.toLocaleString("pt-BR") : v;
}

function _fmtBool(v) {
  if (v === true) return "✓";
  if (v === false) return "—";
  return v || "—";
}

function ComparadorDrawer() {
  const { lista, alternar, limpar, definir } = useComparador();
  const [aberto, setAberto] = React.useState(false);

  React.useEffect(() => {
    const onAbrir = (e) => {
      const cods = e.detail?.codigos;
      if (Array.isArray(cods) && cods.length > 0) {
        definir(cods);
      }
      setAberto(true);
    };
    window.addEventListener("comparador:abrir", onAbrir);
    return () => window.removeEventListener("comparador:abrir", onAbrir);
  }, [definir]);

  React.useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") setAberto(false); };
    if (aberto) document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [aberto]);

  const imoveis = React.useMemo(() => {
    if (!Array.isArray(window.IMOVEIS)) return [];
    return lista
      .map(c => window.IMOVEIS.find(i => i.codigo === c))
      .filter(Boolean);
  }, [lista]);

  if (lista.length === 0 && !aberto) return null;

  // FAB flutuante quando há itens mas drawer fechado
  if (!aberto) {
    return (
      <button
        type="button"
        className="cmp-fab"
        onClick={() => setAberto(true)}
        aria-label={`Abrir comparador com ${lista.length} imóveis`}
      >
        <svg viewBox="0 0 16 16" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6">
          <path d="M2 4h5v8H2zM9 4h5v8H9z"/>
        </svg>
        <span>Comparar</span>
        <span className="cmp-fab-badge">{lista.length}</span>
      </button>
    );
  }

  const enviarWhats = () => {
    if (imoveis.length === 0) return;
    const linhas = imoveis.map(i => `• ${i.codigo} — ${i.titulo} (${i.precoLabel})`).join("\n");
    const txt = `Oi Priscila! Tô comparando estes imóveis e queria sua opinião:\n\n${linhas}\n\nQual você indicaria?`;
    window.open(`https://wa.me/5577999395511?text=${encodeURIComponent(txt)}`, "_blank", "noopener,noreferrer");
  };

  const linhas = [
    { label: "Preço", get: i => i.precoLabel },
    { label: "Bairro", get: i => i.bairro },
    { label: "Tipo", get: i => i.tipo },
    { label: "Área útil", get: i => i.area ? `${i.area} m²` : "—" },
    { label: "Quartos", get: i => _fmtNum(i.quartos) },
    { label: "Suítes", get: i => _fmtNum(i.suites) },
    { label: "Vagas", get: i => _fmtNum(i.vagas) },
    { label: "Match", get: i => i.matchCalculado != null ? `${i.matchCalculado}%` : (i.iaMatch ? `${i.iaMatch}%` : "—") },
    { label: "Status", get: i => i.status || "—" },
    { label: "Tags", get: i => Array.isArray(i.temas) && i.temas.length ? i.temas.join(", ") : "—" },
  ];

  return (
    <>
      <div className="cmp-overlay" onClick={() => setAberto(false)}/>
      <aside className="cmp-drawer" role="dialog" aria-modal="true" aria-label="Comparador de imóveis">
        <header className="cmp-head">
          <div>
            <span className="eyebrow">§ Comparador</span>
            <h2>{imoveis.length} {imoveis.length === 1 ? "imóvel" : "imóveis"} lado a lado</h2>
          </div>
          <button type="button" className="cmp-close" onClick={() => setAberto(false)} aria-label="Fechar">×</button>
        </header>

        {imoveis.length === 0 ? (
          <div className="cmp-vazio">
            <p>Selecione até {COMP_MAX} imóveis usando o ícone de comparar nos cards.</p>
          </div>
        ) : (
          <>
            <div className="cmp-cards">
              {imoveis.map(i => (
                <div key={i.codigo} className="cmp-card">
                  <button className="cmp-card-rm" onClick={() => alternar(i.codigo)} aria-label="Remover">×</button>
                  <a href={`#/imovel/${i.codigo.toLowerCase()}`} onClick={() => setAberto(false)}>
                    <img src={i.img} alt={i.titulo} loading="lazy"/>
                  </a>
                  <strong>{i.titulo}</strong>
                  <span className="cmp-card-cod">{i.codigo}</span>
                </div>
              ))}
              {Array.from({ length: COMP_MAX - imoveis.length }).map((_, idx) => (
                <div key={`empty-${idx}`} className="cmp-card cmp-card-empty">
                  <span>Vazio</span>
                </div>
              ))}
            </div>

            <table className="cmp-tabela">
              <tbody>
                {linhas.map(l => (
                  <tr key={l.label}>
                    <th scope="row">{l.label}</th>
                    {imoveis.map(i => <td key={i.codigo}>{l.get(i)}</td>)}
                    {Array.from({ length: COMP_MAX - imoveis.length }).map((_, idx) => (
                      <td key={`e-${idx}`} className="cmp-empty">—</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>

            <footer className="cmp-foot">
              <button className="aval-cta" onClick={enviarWhats}>
                Pedir opinião da Priscila
              </button>
              <button className="btn-secondary" onClick={limpar}>Limpar comparador</button>
            </footer>
          </>
        )}
      </aside>
    </>
  );
}

Object.assign(window, { useComparador, BotaoComparar, ComparadorDrawer });
