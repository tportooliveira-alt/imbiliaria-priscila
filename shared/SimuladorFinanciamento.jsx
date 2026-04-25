// SimuladorFinanciamento — calculadora de financiamento imobiliario.
// Renderiza formulario + resultado + grafico simples das primeiras 12 parcelas.

function formatarBRL(v) {
  if (v == null) return "—";
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function SimuladorFinanciamento() {
  const [valor, setValor] = React.useState(450000);
  const [entradaPct, setEntradaPct] = React.useState(20);
  const [prazo, setPrazo] = React.useState(360);
  const [taxa, setTaxa] = React.useState(11.5);
  const [sistema, setSistema] = React.useState("SAC");
  const [renda, setRenda] = React.useState("");
  const [resultado, setResultado] = React.useState(null);
  const [erro, setErro] = React.useState("");
  const [carregando, setCarregando] = React.useState(false);

  const entrada = Math.round(valor * entradaPct / 100);

  async function simular() {
    setErro(""); setCarregando(true);
    try {
      const r = await fetch("/api/simular-financiamento", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          valor_imovel: valor,
          entrada,
          prazo_meses: prazo,
          taxa_anual: taxa,
          sistema,
          renda_mensal: renda ? Number(renda) : null,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "Erro");
      setResultado(data);
    } catch (e) { setErro(e.message); }
    finally { setCarregando(false); }
  }

  React.useEffect(() => { simular(); }, []); // primeira simulacao automatica

  return (
    <section className="sim-fin">
      <header className="sim-head">
        <span className="sim-eyebrow">Simulador</span>
        <h2>Quanto fica a parcela do seu sonho?</h2>
        <p>Calculo instantaneo SAC ou Tabela Price com taxas atuais do mercado.</p>
      </header>

      <div className="sim-grid">
        <div className="sim-form">
          <div className="sim-field">
            <label>Valor do imovel: <strong>{formatarBRL(valor)}</strong></label>
            <input type="range" min={100000} max={2000000} step={10000}
              value={valor} onChange={e => setValor(+e.target.value)} />
          </div>

          <div className="sim-field">
            <label>Entrada: <strong>{entradaPct}% ({formatarBRL(entrada)})</strong></label>
            <input type="range" min={0} max={80} step={5}
              value={entradaPct} onChange={e => setEntradaPct(+e.target.value)} />
          </div>

          <div className="sim-field">
            <label>Prazo: <strong>{prazo} meses ({Math.round(prazo/12)} anos)</strong></label>
            <div className="sim-prazo">
              {[120, 180, 240, 300, 360, 420].map(p => (
                <button key={p} type="button"
                  className={prazo === p ? "is-active" : ""}
                  onClick={() => setPrazo(p)}>{p/12}a</button>
              ))}
            </div>
          </div>

          <div className="sim-row">
            <div className="sim-field">
              <label>Taxa anual (%)</label>
              <input type="number" step={0.1} min={0} max={30}
                value={taxa} onChange={e => setTaxa(+e.target.value)} />
            </div>
            <div className="sim-field">
              <label>Sistema</label>
              <div className="sim-toggle">
                <button type="button" className={sistema === "SAC" ? "is-active" : ""}
                  onClick={() => setSistema("SAC")}>SAC</button>
                <button type="button" className={sistema === "PRICE" ? "is-active" : ""}
                  onClick={() => setSistema("PRICE")}>Price</button>
              </div>
            </div>
          </div>

          <div className="sim-field">
            <label>Sua renda mensal (opcional)</label>
            <input type="number" placeholder="R$ 8000" min={0}
              value={renda} onChange={e => setRenda(e.target.value)} />
          </div>

          <button className="sim-cta" onClick={simular} disabled={carregando}>
            {carregando ? "Calculando..." : "Recalcular"}
          </button>
          {erro && <p className="sim-erro">{erro}</p>}
        </div>

        <div className="sim-resultado">
          {resultado ? (
            <>
              <div className="sim-parcela">
                <span>Parcela inicial</span>
                <strong>{formatarBRL(resultado.parcela_inicial)}</strong>
                {sistema === "SAC" && resultado.parcela_final !== resultado.parcela_inicial && (
                  <small>final: {formatarBRL(resultado.parcela_final)}</small>
                )}
              </div>

              <ul className="sim-stats">
                <li><span>Financiado</span><b>{formatarBRL(resultado.valor_financiado)}</b></li>
                <li><span>Total a pagar</span><b>{formatarBRL(resultado.total_pago)}</b></li>
                <li><span>Total de juros</span><b>{formatarBRL(resultado.total_juros)}</b></li>
                <li><span>Renda minima sugerida</span><b>{formatarBRL(resultado.renda_minima)}</b></li>
              </ul>

              {resultado.comprometimento_renda != null && (
                <div className={`sim-flag ${resultado.comprometimento_ok ? "ok" : "alta"}`}>
                  Comprometimento da renda: <strong>
                    {(resultado.comprometimento_renda * 100).toFixed(1)}%
                  </strong>
                  {resultado.comprometimento_ok ? " — dentro do limite" : " — acima de 30%"}
                </div>
              )}

              <SimGrafico parcelas={resultado.primeiras_parcelas} />

              <a href="#chat" className="sim-fechar"
                onClick={() => window.dispatchEvent(new CustomEvent("abrir-chat", { detail: {
                  mensagem: `Simulei: imovel ${formatarBRL(valor)}, entrada ${entradaPct}%, parcela ${formatarBRL(resultado.parcela_inicial)}. Pode me orientar?`
                }}))}>
                Quero falar com a Priscila
              </a>
            </>
          ) : (
            <p className="sim-vazio">Ajuste os campos para ver a simulacao.</p>
          )}
        </div>
      </div>
    </section>
  );
}

function SimGrafico({ parcelas }) {
  if (!parcelas?.length) return null;
  const max = Math.max(...parcelas.map(p => p.parcela));
  return (
    <div className="sim-grafico">
      <span className="sim-grafico-titulo">Primeiras 12 parcelas</span>
      <div className="sim-bars">
        {parcelas.map(p => (
          <div key={p.n} className="sim-bar" title={`Mes ${p.n}: ${formatarBRL(p.parcela)}`}>
            <div className="sim-bar-fill" style={{height: `${(p.parcela / max) * 100}%`}} />
            <small>{p.n}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

window.SimuladorFinanciamento = SimuladorFinanciamento;
