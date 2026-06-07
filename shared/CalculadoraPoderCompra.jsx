// Calculadora de Poder de Compra — quanto de imovel cabe no seu bolso
// Logica: parcela max = 30% renda - parcelas existentes; aplica Price reverso

function CalculadoraPoderCompra() {
  const [renda, setRenda] = React.useState(8000);
  const [entrada, setEntrada] = React.useState(60000);
  const [dividas, setDividas] = React.useState(0);
  const [prazo, setPrazo] = React.useState(30); // anos
  const [taxa, setTaxa] = React.useState(11.5); // a.a.
  const [comprometimento, setComprometimento] = React.useState(30); // %

  const fmt = (v) => {
    if (!isFinite(v) || v < 0) return "R$ 0";
    return "R$ " + Math.round(v).toLocaleString("pt-BR");
  };

  const result = React.useMemo(() => {
    const parcelaMax = (renda * comprometimento / 100) - dividas;
    if (parcelaMax <= 0) {
      return { ok: false, motivo: "comprometimento", parcelaMax: 0 };
    }
    const i = taxa / 100 / 12;
    const n = prazo * 12;
    // Price: PV = PMT * (1 - (1+i)^-n) / i
    const financiavel = parcelaMax * (1 - Math.pow(1 + i, -n)) / i;
    const imovelMax = financiavel + entrada;
    // Renda comprometida real
    const pctComprometido = ((parcelaMax + dividas) / renda) * 100;
    return {
      ok: true,
      parcelaMax,
      financiavel,
      imovelMax,
      pctComprometido,
      ltv: financiavel > 0 ? (financiavel / imovelMax) * 100 : 0,
    };
  }, [renda, entrada, dividas, prazo, taxa, comprometimento]);

  const compativeis = React.useMemo(() => {
    if (!result.ok || !window.IMOVEIS) return [];
    return window.IMOVEIS
      .filter(im => im.preco <= result.imovelMax)
      .sort((a, b) => b.preco - a.preco)
      .slice(0, 6);
  }, [result]);

  const txtWhats = result.ok
    ? `Oi Priscila, fiz a calculadora de poder de compra no site. Renda R$ ${renda.toLocaleString("pt-BR")}, entrada R$ ${entrada.toLocaleString("pt-BR")}, posso comprar ate ${fmt(result.imovelMax)}. Quero ver opcoes.`
    : `Oi Priscila, fiz a calculadora no site mas o resultado nao deu. Quero conversar sobre as opcoes pra mim.`;
  const linkWhats = `https://wa.me/5577999395511?text=${encodeURIComponent(txtWhats)}`;

  return (
    <section className="cpc-wrap" id="poder-compra">
      <div className="cpc-head">
        <span className="cpc-eyebrow">Calculadora · poder de compra</span>
        <h2 className="cpc-title">Quanto de imóvel cabe no seu bolso?</h2>
        <p className="cpc-sub">
          Em 10 segundos você descobre o valor máximo de imóvel que o banco aprovaria
          pra você — sem cadastro, sem login, sem ligação chata.
        </p>
      </div>

      <div className="cpc-grid">
        <div className="cpc-form">
          <div className="cpc-row">
            <label>
              <span className="cpc-label">Sua renda mensal (líquida)</span>
              <span className="cpc-help">Soma da família · descontados impostos</span>
              <div className="cpc-input-money">
                <span>R$</span>
                <input
                  type="number"
                  inputMode="numeric"
                  min="1000" step="500"
                  value={renda}
                  onChange={(e) => setRenda(Math.max(0, Number(e.target.value) || 0))}
                />
              </div>
            </label>
          </div>

          <div className="cpc-row">
            <label>
              <span className="cpc-label">Entrada disponível</span>
              <span className="cpc-help">Inclui FGTS · poupança · venda de outro imóvel</span>
              <div className="cpc-input-money">
                <span>R$</span>
                <input
                  type="number"
                  inputMode="numeric"
                  min="0" step="5000"
                  value={entrada}
                  onChange={(e) => setEntrada(Math.max(0, Number(e.target.value) || 0))}
                />
              </div>
            </label>
          </div>

          <div className="cpc-row">
            <label>
              <span className="cpc-label">Parcelas que você já paga (carros, outros financiamentos)</span>
              <span className="cpc-help">Some todas as parcelas mensais fixas</span>
              <div className="cpc-input-money">
                <span>R$</span>
                <input
                  type="number"
                  inputMode="numeric"
                  min="0" step="100"
                  value={dividas}
                  onChange={(e) => setDividas(Math.max(0, Number(e.target.value) || 0))}
                />
              </div>
            </label>
          </div>

          <div className="cpc-row cpc-row-split">
            <label>
              <span className="cpc-label">Prazo</span>
              <select value={prazo} onChange={(e) => setPrazo(Number(e.target.value))}>
                <option value="15">15 anos</option>
                <option value="20">20 anos</option>
                <option value="25">25 anos</option>
                <option value="30">30 anos</option>
                <option value="35">35 anos</option>
              </select>
            </label>
            <label>
              <span className="cpc-label">Taxa a.a. (%)</span>
              <input
                type="number"
                inputMode="decimal"
                min="6" max="20" step="0.1"
                value={taxa}
                onChange={(e) => setTaxa(Math.max(1, Number(e.target.value) || 0))}
              />
            </label>
          </div>

          <div className="cpc-row">
            <label>
              <span className="cpc-label">Comprometimento da renda: <strong>{comprometimento}%</strong></span>
              <span className="cpc-help">Banco aceita até 30% — abaixo disso é mais saudável</span>
              <input
                type="range"
                min="15" max="35" step="1"
                value={comprometimento}
                onChange={(e) => setComprometimento(Number(e.target.value))}
              />
            </label>
          </div>
        </div>

        <aside className="cpc-resultado">
          {result.ok ? (
            <>
              <div className="cpc-result-card">
                <span className="cpc-result-label">Você pode comprar até</span>
                <strong className="cpc-result-valor">{fmt(result.imovelMax)}</strong>
                <p className="cpc-result-desc">
                  Com entrada de {fmt(entrada)} ({Math.round((entrada / result.imovelMax) * 100) || 0}%)
                  e parcela de até {fmt(result.parcelaMax)}/mês.
                </p>
              </div>
              <ul className="cpc-detalhes">
                <li>
                  <span>Valor a financiar</span>
                  <strong>{fmt(result.financiavel)}</strong>
                </li>
                <li>
                  <span>Parcela máxima</span>
                  <strong>{fmt(result.parcelaMax)}/mês</strong>
                </li>
                <li>
                  <span>Renda comprometida</span>
                  <strong>{Math.round(result.pctComprometido)}%</strong>
                </li>
                <li>
                  <span>LTV (financiamento)</span>
                  <strong>{Math.round(result.ltv)}%</strong>
                </li>
              </ul>
              <a href={linkWhats} target="_blank" rel="noopener" className="cpc-cta-whats">
                <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M13.6 2.4A7.5 7.5 0 001.5 12.3L.5 15.5l3.3-1A7.5 7.5 0 1013.6 2.4z"/></svg>
                <span>Ver opções pra mim no WhatsApp</span>
              </a>
              <p className="cpc-aviso">
                <strong>Importante:</strong> esta é uma estimativa. O valor final depende do
                seu score, relacionamento bancário e modalidade (SBPE, FGTS, MCMV).
                A Priscila já reduziu até 1,5 ponto da taxa de tabela em casos com bom perfil.
              </p>
            </>
          ) : (
            <div className="cpc-erro">
              <strong>Suas parcelas atuais já comprometem mais de {comprometimento}% da renda.</strong>
              <p>Pra liberar financiamento, você precisaria reduzir as dívidas existentes ou aumentar a renda. Posso te ajudar a montar um plano:</p>
              <a href={linkWhats} target="_blank" rel="noopener" className="cpc-cta-whats">
                <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M13.6 2.4A7.5 7.5 0 001.5 12.3L.5 15.5l3.3-1A7.5 7.5 0 1013.6 2.4z"/></svg>
                <span>Falar com a Priscila</span>
              </a>
            </div>
          )}
        </aside>
      </div>

      {result.ok && compativeis.length > 0 && (
        <div className="cpc-imoveis">
          <h3 className="cpc-imoveis-titulo">Imóveis que cabem no seu orçamento agora</h3>
          <p className="cpc-imoveis-sub">{compativeis.length} dos {window.IMOVEIS?.length || 0} imóveis ativos da carteira da Priscila estão dentro do que o banco te aprovaria.</p>
          <div className="cpc-imoveis-grid">
            {compativeis.map(im => (
              <a
                key={im.codigo}
                href={`#/imovel/${im.codigo.toLowerCase()}`}
                className="cpc-imovel-card"
              >
                <img src={im.img} alt={im.titulo} loading="lazy"/>
                <div className="cpc-imovel-body">
                  <span className="cpc-imovel-codigo">{im.codigo} · {im.bairro}</span>
                  <strong>{im.titulo}</strong>
                  <span className="cpc-imovel-preco">{im.precoLabel}</span>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
      {result.ok && compativeis.length === 0 && (
        <div className="cpc-imoveis-vazio">
          <p>Nenhum imóvel da carteira ativa cabe nesse orçamento agora — mas a Priscila tem opções off-market.</p>
          <a href={linkWhats} target="_blank" rel="noopener">Pedir opções no WhatsApp →</a>
        </div>
      )}
    </section>
  );
}

window.CalculadoraPoderCompra = CalculadoraPoderCompra;
