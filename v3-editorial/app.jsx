// Variation 3 — EDITORIAL HARVEST
// Revista de arquitetura/imobiliário, tipografia grande, crema+azul, vídeo em frame retangular,
// numbered sections, big quote, layouts assimétricos.

function App() {
  const [filter, setFilter] = React.useState({ bairro: "", tipo: "", faixa: "", tema: "" });
  const [transacao, setTransacao] = React.useState("comprar");
  const [anuncieOpen, setAnuncieOpen] = React.useState(false);
  const [introOpen, setIntroOpen] = React.useState(() => {
    // Intro de videos desativada por padrao; usar ?intro=1 para reativar quando quiser.
    const params = new URLSearchParams(window.location.search);
    return params.get("intro") === "1";
  });

  const setTema = (tema) => setFilter(f => ({ ...f, tema: f.tema === tema ? "" : tema }));

  return (
    <>
      {introOpen && (
        <div className="introH">
          <div className="introH-inner">
            <OpeningVideo variant="editorial" aspect="16:9" onSkip={() => setIntroOpen(false)}/>
          </div>
        </div>
      )}

      {/* ═══════ NAV ═══════ */}
      <nav className="navH">
        <div className="navH-inner">
          <a href="#" className="navH-mark">
            <span className="navH-mark-name">Priscila Vasconcelos</span>
            <span className="navH-mark-sub">Imóveis · IA · Vitória da Conquista</span>
          </a>
          <div className="navH-links">
            <a href="#imoveis">Imóveis</a>
            <a href="#bairros">Bairros</a>
            <a href="#priscila">A corretora</a>
            <a href="#metodo">O método</a>
            <a href="#" onClick={(e) => { e.preventDefault(); setAnuncieOpen(true); }}>Anuncie seu imóvel</a>
          </div>
          <a href="#contato" className="btnH btnH-solid">Falar comigo</a>
        </div>
      </nav>

      {/* ═══════ HERO EDITORIAL ═══════ */}
      <header className="heroH">
        <div className="heroH-grid">
          <div className="heroH-meta">
            <span className="heroH-vol">VOL. 01</span>
            <span className="heroH-date">{new Date().toLocaleDateString("pt-BR", { month: "long", year: "numeric" })}</span>
            <span className="heroH-issue">EDIÇÃO PERMANENTE</span>
          </div>
          <h1 className="heroH-title">
            <span>Inteligência</span>
            <span className="heroH-amp">&amp;</span>
            <span><em>imóveis</em>,</span>
            <span>em Vitória</span>
            <span>da Conquista.</span>
          </h1>
          <div className="heroH-side">
            <p className="heroH-deck">
              Uma corretora local, uma IA que filtra <strong>1.842 imóveis ativos</strong>,
              e um método que separa o que <em>parece</em> bom no anúncio do que
              <em> é</em> bom para você.
            </p>
            <div className="heroH-byline">
              <span>Curadoria por</span>
              <strong>Priscila Vasconcelos</strong>
              <span>· CRECI/BA 29.231</span>
            </div>
          </div>
          <div className="heroH-figure">
            <img src="../assets/priscila-new-hero.jpeg" alt="Priscila Vasconcelos"/>
            <span className="heroH-cap"><em>Fig. 01</em> — Priscila no escritório, manhã de quinta.</span>
          </div>
          <div className="heroH-stats">
            <div><b>184</b><span>fechamentos</span></div>
            <div><b>4,9</b><span>★ avaliação</span></div>
            <div><b>94 ms</b><span>resposta IA</span></div>
          </div>
        </div>
      </header>

      {/* ═══════ BUSCA ═══════ */}
      <section className="buscaH">
        <div className="buscaH-inner">
          <div className="buscaH-num">§ 01</div>
          <div className="buscaH-head">
            <h2 className="buscaH-title">Comece pelo bairro.</h2>
            <p className="buscaH-deck">A pergunta certa não é “quanto custa” — é <em>“em qual rua”</em>.
              Escolha um bairro, deixe a IA filtrar.</p>
          </div>

          <div className="transacao-toggle" role="tablist" aria-label="Tipo de transação">
            <button role="tab" aria-selected={transacao === "comprar"} className={`transacao-tab ${transacao === "comprar" ? "is-active" : ""}`} onClick={() => setTransacao("comprar")}>
              Comprar
            </button>
            <button role="tab" aria-selected={transacao === "alugar"} className={`transacao-tab ${transacao === "alugar" ? "is-active" : ""}`} onClick={() => setTransacao("alugar")} disabled title="Em breve — Priscila trabalha hoje só com venda">
              Alugar <span className="transacao-em-breve">em breve</span>
            </button>
            <button role="tab" aria-selected={transacao === "lancamento"} className={`transacao-tab ${transacao === "lancamento" ? "is-active" : ""}`} onClick={() => setTransacao("lancamento")} disabled title="Em breve — lançamentos chegam quando a Priscila assinar parceria com a construtora">
              Lançamento <span className="transacao-em-breve">em breve</span>
            </button>
          </div>

          <BuscaBairros variant="editorial" onFilterChange={(f) => setFilter(prev => ({ ...prev, ...f }))}/>

          <div className="temas-grid">
            {window.TEMAS.map(t => (
              <button
                key={t.id}
                type="button"
                className={`tema-card ${filter.tema === t.id ? "is-active" : ""}`}
                onClick={() => setTema(t.id)}
                aria-pressed={filter.tema === t.id}
              >
                <span className="tema-emoji" aria-hidden="true">{t.emoji}</span>
                <span className="tema-nome">{t.nome}</span>
                <span className="tema-desc">{t.desc}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════ IMÓVEIS ═══════ */}
      <PropertyGrid filter={filter} variant="editorial" subtitle="A IA já cruzou perfil, orçamento e bairro. Estes são os matches."/>

      {/* ═══════ SIMULADOR DE FINANCIAMENTO ═══════ */}
      <SimuladorFinanciamento/>

      {/* ═══════ MANIFESTO / QUOTE ═══════ */}
      <section className="manifestoH">
        <div className="manifestoH-inner">
          <div className="manifestoH-num">§ 03</div>
          <blockquote>
            <span className="manifestoH-mark">“</span>
            <p>
              A IA <em>não</em> substitui a Priscila. Ela <em>liberta</em> a Priscila —
              de filtrar 1.842 anúncios para conversar com você sobre os 8 que importam.
            </p>
            <footer>— Manifesto da casa</footer>
          </blockquote>
        </div>
      </section>

      {/* ═══════ MÉTODO 4 ETAPAS ═══════ */}
      <section className="metodoH" id="metodo">
        <div className="metodoH-inner">
          <div className="metodoH-num">§ 04</div>
          <header>
            <h2>O método.</h2>
            <p className="metodoH-deck">Quatro etapas. Sem corrida, sem pressão, sem grupo de WhatsApp com 200 imóveis aleatórios.</p>
          </header>
          <ol className="metodoH-list">
            {window.IA_CAPACIDADES.map((c, i) => (
              <li key={i}>
                <span className="metodoH-step">0{i + 1}</span>
                <div className="metodoH-body">
                  <h3>{c.titulo}</h3>
                  <p>{c.detalhe}</p>
                </div>
                <span className="metodoH-icon">{c.icone}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* ═══════ BAIRROS — atlas ═══════ */}
      <section className="atlasH" id="bairros">
        <div className="atlasH-inner">
          <div className="metodoH-num">§ 05</div>
          <header>
            <h2>Atlas de bairros.</h2>
            <p>Dez bairros em Vitória da Conquista. Cada um com sua própria gramática.</p>
          </header>
          <div className="atlasH-grid">
            {window.BAIRROS.map((b, i) => (
              <article key={b.id} className={`atlasH-card ${filter.bairro === b.nome ? "active" : ""}`}
                onClick={() => { setFilter({ bairro: b.nome, tipo: "", faixa: "" }); document.getElementById("imoveis")?.scrollIntoView({ behavior: "smooth" }); }}>
                <div className="atlasH-head">
                  <span className="atlasH-num-card">{String(i + 1).padStart(2, "0")}</span>
                  <span className="atlasH-emoji">{b.emoji}</span>
                </div>
                <h3>{b.nome}</h3>
                <p className="atlasH-destaque">{b.destaque}</p>
                <p className="atlasH-perfil">{b.perfil}</p>
                <div className="atlasH-meta">
                  <span><b>{b.imoveis}</b> imóveis</span>
                  <span>{b.precoMedio}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════ PRISCILA — entrevista ═══════ */}
      <section className="entrevistaH" id="priscila">
        <div className="entrevistaH-inner">
          <div className="metodoH-num">§ 06</div>
          <div className="entrevistaH-grid">
            <div className="entrevistaH-photo">
              <img src="../assets/priscila-sobre.jpg" alt="Priscila Vasconcelos"/>
              <span className="heroH-cap"><em>Fig. 02</em> — Visita guiada, bairro Candeias.</span>
            </div>
            <div className="entrevistaH-copy">
              <h2>Conversa com a corretora.</h2>
              <div className="entrevistaH-qa">
                <p className="entrevistaH-q">Por que IA, se você é uma corretora?</p>
                <p>“Porque ninguém quer perder sábado vendo 40 imóveis errados. Eu uso a IA pra te mostrar 4 — e usar o tempo bom pra entender o que você realmente quer.”</p>
              </div>
              <div className="entrevistaH-qa">
                <p className="entrevistaH-q">E se eu não souber o bairro ainda?</p>
                <p>“A gente conversa. Cinco perguntas, e o sistema já sabe se você é mais Candeias ou mais Recreio. É rápido, mas a decisão é sua.”</p>
              </div>
              <div className="entrevistaH-qa">
                <p className="entrevistaH-q">Quanto tempo leva, em média?</p>
                <p>“De primeira mensagem a chave na mão? <strong>22 dias</strong>, é a minha média. Mas tem gente que fecha em 9.”</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════ AVALIACAO DE IMOVEL ═══════ */}
      <AvaliacaoImovel/>

      {/* ═══════ CTA ═══════ */}
      <section className="ctaH" id="contato">
        <div className="ctaH-inner">
          <span className="metodoH-num" style={{position:"static", marginBottom:"1.5rem", display:"inline-block"}}>§ 07</span>
          <h2>Vamos começar?</h2>
          <p>Mande seu bairro, sua faixa de preço, ou só um “oi”. A IA prepara as opções, eu falo com você.</p>
          <div className="ctaH-row">
            <a href="#" className="btnH btnH-solid btnH-big">
              <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M13.6 2.4A7.5 7.5 0 001.5 12.3L.5 15.5l3.3-1A7.5 7.5 0 1013.6 2.4z"/></svg>
              WhatsApp · (77) 9 8819-3344
            </a>
            <a href="#" className="btnH btnH-ghost btnH-big">Iniciar com a IA</a>
          </div>
        </div>
      </section>

      <footer className="footH">
        <div className="footH-inner">
          <div className="footH-mark">
            <span className="footH-mark-name">Priscila Vasconcelos</span>
            <span className="footH-mark-sub">Imóveis com IA · Vitória da Conquista · CRECI/BA 29.231</span>
          </div>
          <span className="footH-copy">© {new Date().getFullYear()} · Edição Permanente · Vol. 01</span>
          <div className="footH-links">
            <a href="./privacidade.html">Política de privacidade</a>
            <span aria-hidden="true">·</span>
            <a href="#" onClick={(e) => { e.preventDefault(); setAnuncieOpen(true); }}>Anuncie seu imóvel</a>
          </div>
        </div>
      </footer>

      <AIChat variant="editorial"/>
      {anuncieOpen && <AnuncieImovel onClose={() => setAnuncieOpen(false)}/>}
      <CookieBanner/>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("app"));
root.render(<App/>);
