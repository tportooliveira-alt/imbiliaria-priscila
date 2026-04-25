// AvaliacaoImovel — AVM editorial: faixa de valor estimada por bairro/caracteristicas.

function formatarValor(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

const PADROES = [
  ["simples", "Simples"], ["medio", "Medio"], ["alto", "Alto"], ["luxo", "Luxo"],
];
const ESTADOS = [
  ["reformado", "Reformado"], ["bom", "Bom"], ["regular", "Regular"], ["precisa_reforma", "Precisa reforma"],
];
const IDADES = [
  ["novo", "Novo"], ["0_10", "Ate 10 anos"], ["10_20", "10-20 anos"], ["20_mais", "Mais de 20"],
];

function AvaliacaoImovel() {
  const [passo, setPasso] = React.useState(0);
  const [bairros, setBairros] = React.useState([]);
  const [dados, setDados] = React.useState({
    bairro: "candeias", area_util: 90, quartos: 3, suites: 1, vagas: 1,
    padrao: "medio", estado: "bom", idade: "0_10", tem_area_externa: false,
    nome: "", contato: "",
  });
  const [resultado, setResultado] = React.useState(null);
  const [erro, setErro] = React.useState("");
  const [carregando, setCarregando] = React.useState(false);

  React.useEffect(() => {
    fetch("/api/avaliacao/bairros").then(r => r.json()).then(d => setBairros(d.bairros || []));
  }, []);

  function up(k, v) { setDados(d => ({ ...d, [k]: v })); }

  async function avaliar() {
    setErro(""); setCarregando(true);
    try {
      const r = await fetch("/api/avaliar-imovel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "Erro");
      setResultado(data);
      setPasso(5);
    } catch (e) { setErro(e.message); }
    finally { setCarregando(false); }
  }

  const passos = [
    {
      titulo: "Em qual bairro fica o imovel?",
      campo: (
        <select value={dados.bairro} onChange={e => up("bairro", e.target.value)}>
          {bairros.map(b => <option key={b} value={b}>{b.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</option>)}
        </select>
      ),
    },
    {
      titulo: "Qual a area util?",
      campo: (
        <div>
          <input type="number" min={20} max={2000} value={dados.area_util}
            onChange={e => up("area_util", +e.target.value)} />
          <span className="aval-hint">m²</span>
        </div>
      ),
    },
    {
      titulo: "Quantos quartos, suites e vagas?",
      campo: (
        <div className="aval-grid3">
          <label>Quartos<input type="number" min={0} max={10} value={dados.quartos} onChange={e => up("quartos", +e.target.value)} /></label>
          <label>Suites<input type="number" min={0} max={10} value={dados.suites} onChange={e => up("suites", +e.target.value)} /></label>
          <label>Vagas<input type="number" min={0} max={10} value={dados.vagas} onChange={e => up("vagas", +e.target.value)} /></label>
        </div>
      ),
    },
    {
      titulo: "Padrao de acabamento e estado?",
      campo: (
        <div className="aval-grid2">
          <div>
            <label>Padrao</label>
            <div className="aval-chips">
              {PADROES.map(([v, l]) => (
                <button key={v} type="button" className={dados.padrao === v ? "is-active" : ""}
                  onClick={() => up("padrao", v)}>{l}</button>
              ))}
            </div>
          </div>
          <div>
            <label>Estado</label>
            <div className="aval-chips">
              {ESTADOS.map(([v, l]) => (
                <button key={v} type="button" className={dados.estado === v ? "is-active" : ""}
                  onClick={() => up("estado", v)}>{l}</button>
              ))}
            </div>
          </div>
        </div>
      ),
    },
    {
      titulo: "Idade do imovel e area externa?",
      campo: (
        <div>
          <div className="aval-chips">
            {IDADES.map(([v, l]) => (
              <button key={v} type="button" className={dados.idade === v ? "is-active" : ""}
                onClick={() => up("idade", v)}>{l}</button>
            ))}
          </div>
          <label className="aval-check">
            <input type="checkbox" checked={dados.tem_area_externa}
              onChange={e => up("tem_area_externa", e.target.checked)} />
            Tem quintal, varanda gourmet ou area externa
          </label>
        </div>
      ),
    },
  ];

  if (passo === 5 && resultado) {
    return (
      <section className="aval-result">
        <span className="aval-eyebrow">Avaliacao online</span>
        <h2>Faixa estimada do seu imovel</h2>
        <div className="aval-faixa">
          <div className="aval-min"><small>Minimo</small><strong>{formatarValor(resultado.valor_minimo)}</strong></div>
          <div className="aval-central"><small>Valor central</small><strong>{formatarValor(resultado.valor_central)}</strong></div>
          <div className="aval-max"><small>Maximo</small><strong>{formatarValor(resultado.valor_maximo)}</strong></div>
        </div>
        <p className="aval-texto">{resultado.texto}</p>
        <p className="aval-confianca">Confianca da estimativa: <strong>{resultado.confianca}</strong></p>
        <div className="aval-acoes">
          <button className="btn-secondary" onClick={() => { setResultado(null); setPasso(0); }}>
            Refazer
          </button>
          <button className="aval-cta" onClick={() => window.dispatchEvent(new CustomEvent("abrir-chat", { detail: {
            mensagem: `Avaliei meu imovel em ${dados.bairro}: faixa ${formatarValor(resultado.valor_minimo)} a ${formatarValor(resultado.valor_maximo)}. Quero conversar sobre vender com a Priscila.`
          }}))}>
            Quero avaliacao presencial
          </button>
        </div>
      </section>
    );
  }

  const atual = passos[passo];
  return (
    <section className="aval-stepper">
      <header className="aval-head">
        <span className="aval-eyebrow">Avaliacao gratuita</span>
        <h2>Quanto vale o seu imovel em VDC?</h2>
        <div className="aval-progress">
          {passos.map((_, i) => (
            <span key={i} className={i <= passo ? "is-active" : ""} />
          ))}
        </div>
      </header>

      <div className="aval-corpo">
        <h3>{atual.titulo}</h3>
        {atual.campo}
        {erro && <p className="sim-erro">{erro}</p>}
      </div>

      <div className="aval-nav">
        {passo > 0 && <button className="btn-secondary" onClick={() => setPasso(passo - 1)}>Voltar</button>}
        {passo < passos.length - 1 ? (
          <button className="aval-cta" onClick={() => setPasso(passo + 1)}>Proximo</button>
        ) : (
          <button className="aval-cta" onClick={avaliar} disabled={carregando}>
            {carregando ? "Avaliando..." : "Ver avaliacao"}
          </button>
        )}
      </div>
    </section>
  );
}

window.AvaliacaoImovel = AvaliacaoImovel;
