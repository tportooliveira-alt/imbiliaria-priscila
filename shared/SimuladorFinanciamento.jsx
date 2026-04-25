// SimuladorFinanciamento — calculadora REAL com captura de lead.
// Fluxo:
//   1) Gate: tipo, bairro, valor, nome, telefone (obrigatorios) → grava lead
//   2) Simulacao com taxas reais por banco (abril/2026) + comparativo
// Persiste contato em sessionStorage pra nao pedir de novo na mesma visita.

const TIPOS_IMOVEL = [
  { v: "apartamento", l: "Apartamento" },
  { v: "casa",        l: "Casa" },
  { v: "casa_condominio", l: "Casa em condominio" },
  { v: "terreno",     l: "Terreno" },
  { v: "comercial",   l: "Comercial" },
];

const BAIRROS_VDC = [
  "Candeias", "Boa Vista", "Brasil", "Recreio", "Centro",
  "Patagonia", "Jurema", "Felicia", "Universidade",
  "Anel da Soberania", "Conquistinha", "Outro / Nao sei",
];

function formatarBRL(v) {
  if (v == null) return "—";
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function formatarTelefone(s) {
  const d = (s || "").replace(/\D/g, "").slice(0, 11);
  if (d.length <= 2) return d;
  if (d.length <= 6) return `(${d.slice(0,2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0,2)}) ${d.slice(2,6)}-${d.slice(6)}`;
  return `(${d.slice(0,2)}) ${d.slice(2,7)}-${d.slice(7)}`;
}

function SimuladorFinanciamento() {
  // ── Identificacao do lead (gate) ──
  const cache = (() => {
    try { return JSON.parse(sessionStorage.getItem("sim_lead") || "{}"); }
    catch { return {}; }
  })();
  const [nome, setNome] = React.useState(cache.nome || "");
  const [telefone, setTelefone] = React.useState(cache.telefone || "");
  const [tipoImovel, setTipoImovel] = React.useState(cache.tipoImovel || "apartamento");
  const [bairro, setBairro] = React.useState(cache.bairro || "Candeias");
  const [valor, setValor] = React.useState(cache.valor || 450000);
  const [identificado, setIdentificado] = React.useState(!!cache.telefone);

  // ── Parametros da simulacao ──
  const [entradaPct, setEntradaPct] = React.useState(20);
  const [prazo, setPrazo] = React.useState(360);
  const [taxa, setTaxa] = React.useState(11.49);
  const [sistema, setSistema] = React.useState("SAC");
  const [renda, setRenda] = React.useState("");
  const [resultado, setResultado] = React.useState(null);
  const [erro, setErro] = React.useState("");
  const [carregando, setCarregando] = React.useState(false);

  const entrada = Math.round(valor * entradaPct / 100);
  const telefoneValido = telefone.replace(/\D/g, "").length >= 10;
  const podeSimular = nome.trim().length >= 2 && telefoneValido;

  function iniciarPesquisa(e) {
    e?.preventDefault?.();
    if (!podeSimular) {
      setErro("Preencha nome e telefone para ver as taxas reais.");
      return;
    }
    sessionStorage.setItem("sim_lead", JSON.stringify({
      nome, telefone, tipoImovel, bairro, valor,
    }));
    setIdentificado(true);
    setErro("");
    simular();
  }

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
          nome: nome || null,
          contato: telefone || null,
          bairro: bairro || null,
          tipo_imovel: tipoImovel || null,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "Erro");
      setResultado(data);
    } catch (e) { setErro(e.message); }
    finally { setCarregando(false); }
  }

  // Recalcula automaticamente quando o usuario ajusta parametros (ja identificado)
  React.useEffect(() => {
    if (identificado) simular();
    // eslint-disable-next-line
  }, [entradaPct, prazo, taxa, sistema, valor]);

  // ─────────── PASSO 1: gate de captura ───────────
  if (!identificado) {
    return (
      <section className="sim-fin sim-gate">
        <header className="sim-head">
          <span className="sim-eyebrow">Simulador real · taxas de abril/2026</span>
          <h2>Quanto fica a parcela do seu sonho?</h2>
          <p>
            Calculo com as taxas <strong>reais</strong> dos principais bancos
            (Caixa, Banco do Brasil, Itau, Bradesco, Santander). Em 30 segundos
            voce ve o comparativo completo.
          </p>
        </header>

        <form className="sim-form sim-form-gate" onSubmit={iniciarPesquisa}>
          <div className="sim-row">
            <div className="sim-field">
              <label>Tipo do imovel</label>
              <select value={tipoImovel} onChange={e => setTipoImovel(e.target.value)}>
                {TIPOS_IMOVEL.map(t => <option key={t.v} value={t.v}>{t.l}</option>)}
              </select>
            </div>
            <div className="sim-field">
              <label>Bairro de interesse</label>
              <select value={bairro} onChange={e => setBairro(e.target.value)}>
                {BAIRROS_VDC.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
          </div>

          <div className="sim-field">
            <label>Valor desejado: <strong>{formatarBRL(valor)}</strong></label>
            <input type="range" min={100000} max={2000000} step={10000}
              value={valor} onChange={e => setValor(+e.target.value)} />
          </div>

          <div className="sim-row">
            <div className="sim-field">
              <label>Seu nome</label>
              <input type="text" placeholder="Como podemos te chamar?"
                value={nome} onChange={e => setNome(e.target.value)} required />
            </div>
            <div className="sim-field">
              <label>WhatsApp</label>
              <input type="tel" placeholder="(77) 9 9999-9999"
                value={telefone}
                onChange={e => setTelefone(formatarTelefone(e.target.value))}
                required />
            </div>
          </div>

          <button className="sim-cta sim-cta-grande" type="submit"
            disabled={!podeSimular || carregando}>
            {carregando ? "Carregando taxas..." : "Ver minha simulacao real"}
          </button>
          {erro && <p className="sim-erro">{erro}</p>}
          <p className="sim-privacidade">
            Seus dados ficam apenas com a Priscila Vasconcelos (CRECI/BA 29.231).
            Nao compartilhamos com terceiros.
          </p>
        </form>
      </section>
    );
  }

  // ─────────── PASSO 2: simulacao real + comparativo ───────────
  return (
    <section className="sim-fin">
      <header className="sim-head">
        <span className="sim-eyebrow">Simulacao real · {nome.split(" ")[0]}</span>
        <h2>Sua parcela com taxas reais de hoje</h2>
        {resultado?.fonte_taxas && (
          <p className="sim-fonte">Fonte: {resultado.fonte_taxas}</p>
        )}
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
                <span>Parcela inicial · {sistema}</span>
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

              <ComparativoBancos bancos={resultado.comparativo_bancos} prazo={prazo} />

              <SimGrafico parcelas={resultado.primeiras_parcelas} />

              <a href="#chat" className="sim-fechar"
                onClick={() => window.dispatchEvent(new CustomEvent("abrir-chat", { detail: {
                  mensagem: `Simulei ${tipoImovel} em ${bairro}, ${formatarBRL(valor)}, entrada ${entradaPct}%, parcela ${formatarBRL(resultado.parcela_inicial)}. Pode me orientar?`
                }}))}>
                Quero falar com a Priscila
              </a>
            </>
          ) : (
            <p className="sim-vazio">Carregando taxas reais...</p>
          )}
        </div>
      </div>
    </section>
  );
}

function ComparativoBancos({ bancos, prazo }) {
  if (!bancos?.length) return null;
  const melhor = bancos[0];
  return (
    <div className="sim-bancos">
      <div className="sim-bancos-titulo">
        Comparativo entre bancos · prazo {prazo/12} anos
        <small>Taxas reais SBPE · abril/2026</small>
      </div>
      <ul className="sim-bancos-lista">
        {bancos.map(b => (
          <li key={b.chave} className={b === melhor ? "is-melhor" : ""}>
            <div className="sim-banco-nome">
              {b.banco}
              {b === melhor && <span className="sim-banco-flag">Menor parcela</span>}
            </div>
            <div className="sim-banco-tax">{b.taxa_anual.toFixed(2)}% a.a.</div>
            <div className="sim-banco-parc">{(b.parcela_inicial).toLocaleString("pt-BR", {style:"currency", currency:"BRL", maximumFractionDigits:0})}</div>
          </li>
        ))}
      </ul>
      <p className="sim-bancos-nota">
        Os valores acima sao referenciais e dependem de aprovacao de credito,
        relacionamento com o banco e uso do FGTS. A Priscila negocia condicoes
        melhores para clientes da carteira.
      </p>
    </div>
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
