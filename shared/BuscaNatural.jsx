/* global React */
// BuscaNatural — caixa de busca em linguagem natural acima do PropertyGrid.
// Chama POST /api/busca-natural e dispara um evento "busca-natural:resultado"
// que o app pode capturar para sincronizar com filtros visuais.

const { useState, useCallback } = React;

const EXEMPLOS = [
  "apartamento em Candeias com 3 quartos ate 600 mil",
  "casa com quintal no centro",
  "cobertura com vista e piscina",
  "lote em Patagonia",
];

function BuscaNatural({ onResultado }) {
  const [texto, setTexto] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState("");

  const buscar = useCallback(async (q) => {
    const consulta = (q ?? texto).trim();
    if (consulta.length < 2) return;
    setCarregando(true);
    setErro("");
    try {
      const r = await fetch("/api/busca-natural", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: consulta, usar_ia: true, limite: 30 }),
      });
      if (!r.ok) throw new Error("HTTP " + r.status);
      const data = await r.json();
      setResultado(data);
      if (typeof onResultado === "function") onResultado(data);
      window.dispatchEvent(new CustomEvent("busca-natural:resultado", { detail: data }));
    } catch (e) {
      setErro("Não foi possível buscar. Tente novamente em alguns segundos.");
    } finally {
      setCarregando(false);
    }
  }, [texto, onResultado]);

  const limpar = () => {
    setTexto("");
    setResultado(null);
    setErro("");
    window.dispatchEvent(new CustomEvent("busca-natural:resultado", { detail: null }));
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      buscar();
    }
  };

  return (
    <section className="busca-natural" aria-label="Busca em linguagem natural">
      <div className="busca-natural-card">
        <p className="busca-natural-titulo">Busca inteligente</p>
        <p className="busca-natural-sub">
          Descreva o que você procura como falaria com a Priscila — a IA entende e filtra.
        </p>
        <div className="busca-natural-form">
          <input
            type="text"
            className="busca-natural-input"
            placeholder='Ex: "apartamento 3 quartos em Candeias até 600 mil"'
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            onKeyDown={onKeyDown}
            maxLength={500}
            aria-label="Descreva o imóvel desejado"
          />
          <button
            type="button"
            className="busca-natural-btn"
            onClick={() => buscar()}
            disabled={carregando || texto.trim().length < 2}
          >
            {carregando ? "Buscando…" : "Buscar"}
          </button>
        </div>
        <div className="busca-natural-exemplos" role="list">
          {EXEMPLOS.map((ex) => (
            <button
              key={ex}
              type="button"
              className="busca-natural-chip-exemplo"
              onClick={() => { setTexto(ex); buscar(ex); }}
            >
              {ex}
            </button>
          ))}
        </div>
        {erro && <p className="busca-natural-erro">{erro}</p>}
        {resultado && (
          <div className="busca-natural-resultado" role="status" aria-live="polite">
            <span className="busca-natural-resultado-total">
              {resultado.total} {resultado.total === 1 ? "imóvel" : "imóveis"}
            </span>
            <span className="busca-natural-resultado-explicacao">{resultado.explicacao}</span>
            <button type="button" className="busca-natural-resultado-limpar" onClick={limpar}>
              Limpar
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

window.BuscaNatural = BuscaNatural;
