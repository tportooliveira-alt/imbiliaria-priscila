// Variation 3 — EDITORIAL HARVEST
// Revista de arquitetura/imobiliário, tipografia grande, crema+azul, vídeo em frame retangular,
// numbered sections, big quote, layouts assimétricos.

const METODO_SLIDES = [
  {
    titulo: "Atendimento IA 24 / 7",
    slides: [
      {
        titulo: "Resposta imediata, em qualquer horário",
        texto: "A IA responde em segundos no site e no WhatsApp, inclusive fora do expediente. Isso evita abandono de lead no primeiro contato e mantém o interesse vivo enquanto a decisão ainda está quente.",
      },
      {
        titulo: "Triagem inteligente já na primeira conversa",
        texto: "Nas primeiras mensagens, o sistema identifica intenção de compra ou venda, faixa de valor, bairro de preferência e urgência. Com isso, a Priscila recebe o cliente já contextualizado e com histórico organizado.",
      },
      {
        titulo: "Atendimento humano na hora certa",
        texto: "A IA não substitui a corretora: ela prepara o terreno. Quando o lead demonstra potencial real, a Priscila entra com abordagem consultiva, economizando tempo e elevando taxa de conversão.",
      },
    ],
  },
  {
    titulo: "Match inteligente de imóvel",
    slides: [
      {
        titulo: "Recomendação além do preço",
        texto: "O motor de match cruza orçamento, tipo de imóvel, bairro, tema de interesse, estágio da jornada e sinais de comportamento. O resultado prioriza imóveis com aderência real, não apenas anúncios populares.",
      },
      {
        titulo: "Ranking dinâmico e transparente",
        texto: "Cada card pode mostrar percentual de compatibilidade com a busca ativa. Ao alterar filtros, o ranking se reorganiza em tempo real para destacar opções mais coerentes com o perfil do momento.",
      },
      {
        titulo: "Menos ruído, mais decisão",
        texto: "Em vez de enviar dezenas de links genéricos, a seleção reduz ruído e acelera a escolha. O cliente entende mais rápido por que aquele imóvel apareceu e avança com mais segurança para visita e proposta.",
      },
    ],
  },
  {
    titulo: "Follow-up automático",
    slides: [
      {
        titulo: "Régua de contato com cadência real",
        texto: "A régua organiza retornos em 1h, 24h, 72h e 7 dias, com mensagens ajustadas ao estágio do lead. Isso garante consistência comercial sem parecer spam ou insistência vazia.",
      },
      {
        titulo: "Contexto preservado em cada retorno",
        texto: "As próximas interações usam o histórico do lead: bairro visto, faixa de preço, simulação feita, dúvidas anteriores e objeções. Cada contato continua a conversa, em vez de recomeçar do zero.",
      },
      {
        titulo: "Recuperação de oportunidades esquecidas",
        texto: "Leads que esfriaram voltam para a fila com gatilhos específicos (novo imóvel aderente, ajuste de preço, condição de financiamento). O resultado é maior aproveitamento da base e menor perda por falta de timing.",
      },
    ],
  },
  {
    titulo: "Dashboard de decisão",
    slides: [
      {
        titulo: "Visão executiva em tempo real",
        texto: "O painel consolida volume de leads, estágio de funil, origem, temperatura e performance de atendimento. Em poucos segundos, fica claro onde concentrar esforço comercial no dia.",
      },
      {
        titulo: "Métricas que orientam ação",
        texto: "CPL, taxa de resposta, visitas agendadas, propostas enviadas e conversão por etapa mostram o que está funcionando. A gestão sai do achismo e passa a operar com prioridade baseada em dado.",
      },
      {
        titulo: "Correção rápida de rota",
        texto: "Quando um indicador cai, a equipe ajusta copy, campanha, filtro ou abordagem imediatamente. Isso reduz desperdício de mídia, melhora previsibilidade de vendas e protege margem da operação.",
      },
    ],
  },
];

function App() {
  const route = window.useHashRoute ? window.useHashRoute() : { tipo: "home" };
  const [filter, setFilter] = React.useState({ bairro: "", tipo: "", faixa: "", tema: "" });
  const [resultadoBuscaNatural, setResultadoBuscaNatural] = React.useState(null);
  const [transacao, setTransacao] = React.useState("comprar");
  const [anuncieOpen, setAnuncieOpen] = React.useState(false);
  const [metodoAtivo, setMetodoAtivo] = React.useState(0);
  const [metodoSlide, setMetodoSlide] = React.useState(0);
  const [introOpen, setIntroOpen] = React.useState(() => {
    // Intro de videos desativada por padrao; usar ?intro=1 para reativar quando quiser.
    const params = new URLSearchParams(window.location.search);
    return params.get("intro") === "1";
  });

  const setTema = (tema) => setFilter(f => ({ ...f, tema: f.tema === tema ? "" : tema }));
  const voltarHome = () => { window.location.hash = ""; };
  const abrirChat = (mensagem) => {
    window.dispatchEvent(new CustomEvent("abrir-chat", { detail: { mensagem } }));
  };
  const aplicarBuscaNatural = (resultado) => {
    setResultadoBuscaNatural(resultado);
    if (!resultado) return;
    const filtros = resultado.filtros || {};
    setFilter(prev => ({
      ...prev,
      bairro: filtros.bairros?.[0]
        ? window.BAIRROS.find(b => b.id === filtros.bairros[0] || b.nome.toLowerCase() === filtros.bairros[0])?.nome || prev.bairro
        : prev.bairro,
      tipo: filtros.tipo ? filtros.tipo.charAt(0).toUpperCase() + filtros.tipo.slice(1) : prev.tipo,
      faixa: filtros.preco_max && filtros.preco_max <= 500000 ? "até 500" : prev.faixa,
    }));
    document.getElementById("imoveis")?.scrollIntoView({ behavior: "smooth" });
  };

  // Páginas de detalhe — só nav + footer; resto da home vira oculto
  if (route.tipo === "imovel") {
    return (
      <>
        <NavSimples onAnuncieOpen={() => setAnuncieOpen(true)}/>
        <ImovelDetalhe codigo={route.id} onVoltar={voltarHome}/>
        <FooterSimples onAnuncieOpen={() => setAnuncieOpen(true)}/>
        <AIChat variant="editorial"/>
        {window.ComparadorDrawer && <window.ComparadorDrawer/>}
        {anuncieOpen && <AnuncieImovel onClose={() => setAnuncieOpen(false)}/>}
        <CookieBanner/>
      </>
    );
  }
  if (route.tipo === "bairro") {
    return (
      <>
        <NavSimples onAnuncieOpen={() => setAnuncieOpen(true)}/>
        <BairroDetalhe slug={route.id} onVoltar={voltarHome}/>
        <FooterSimples onAnuncieOpen={() => setAnuncieOpen(true)}/>
        <AIChat variant="editorial"/>
        {window.ComparadorDrawer && <window.ComparadorDrawer/>}
        {anuncieOpen && <AnuncieImovel onClose={() => setAnuncieOpen(false)}/>}
        <CookieBanner/>
      </>
    );
  }
  if (route.tipo === "favoritos" && window.PaginaFavoritos) {
    return (
      <>
        <NavSimples onAnuncieOpen={() => setAnuncieOpen(true)}/>
        <window.PaginaFavoritos onVoltar={voltarHome}/>
        <FooterSimples onAnuncieOpen={() => setAnuncieOpen(true)}/>
        <AIChat variant="editorial"/>
        {window.ComparadorDrawer && <window.ComparadorDrawer/>}
        {anuncieOpen && <AnuncieImovel onClose={() => setAnuncieOpen(false)}/>}
        <CookieBanner/>
      </>
    );
  }

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
            <a href="/admin/?reset=1" rel="nofollow">Área interna</a>
          </div>
          {window.ContadorFavoritosNav ? <window.ContadorFavoritosNav/> : null}
          <button type="button" className="btnH btnH-solid" onClick={() => abrirChat("Oi, quero falar com a Priscila sobre imóveis em Vitória da Conquista.")}>Falar comigo</button>
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

          <BuscaBairros variant="editorial" onFilterChange={(f) => { setResultadoBuscaNatural(null); setFilter(prev => ({ ...prev, ...f })); }}/>

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

      {/* ═══════ BUSCA NATURAL (IA) ═══════ */}
      {window.BuscaNatural && <window.BuscaNatural onResultado={aplicarBuscaNatural}/>}

      {/* ═══════ IMÓVEIS ═══════ */}
      <PropertyGrid filter={filter} resultadoBusca={resultadoBuscaNatural} variant="editorial" subtitle="A IA já cruzou perfil, orçamento e bairro. Estes são os matches."/>

      {/* ═══════ SIMULADOR DE FINANCIAMENTO ═══════ */}
      <div id="simulador">
        <SimuladorFinanciamento/>
      </div>

      {/* ═══════ CALCULADORA DE PODER DE COMPRA ═══════ */}
      <CalculadoraPoderCompra/>

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
              <li
                key={i}
                className={metodoAtivo === i ? "is-active" : ""}
                onClick={() => { setMetodoAtivo(i); setMetodoSlide(0); }}
              >
                <button
                  type="button"
                  className="metodoH-itemBtn"
                  aria-expanded={metodoAtivo === i}
                  aria-label={`Abrir detalhes de ${c.titulo}`}
                >
                  <span className="metodoH-step">0{i + 1}</span>
                  <div className="metodoH-body">
                    <h3>{c.titulo}</h3>
                    <p>{c.detalhe}</p>
                  </div>
                  <span className="metodoH-icon">{c.icone}</span>
                </button>
              </li>
            ))}
          </ol>

          <section className="metodoH-slides" aria-live="polite">
            <div className="metodoH-slides-head">
              <p className="metodoH-slides-kicker">Explicação detalhada · clique nos blocos 01–04</p>
              <h3>{METODO_SLIDES[metodoAtivo].titulo}</h3>
            </div>

            <article key={`${metodoAtivo}-${metodoSlide}`} className="metodoH-slideCard">
              <span className="metodoH-slideStep">Slide {metodoSlide + 1} de {METODO_SLIDES[metodoAtivo].slides.length}</span>
              <h4>{METODO_SLIDES[metodoAtivo].slides[metodoSlide].titulo}</h4>
              <p>{METODO_SLIDES[metodoAtivo].slides[metodoSlide].texto}</p>
            </article>

            <div className="metodoH-slideNav">
              <button
                type="button"
                onClick={() => setMetodoSlide((s) => Math.max(0, s - 1))}
                disabled={metodoSlide === 0}
              >
                ← Anterior
              </button>
              <div className="metodoH-slideDots" role="tablist" aria-label="Navegação de slides do método">
                {METODO_SLIDES[metodoAtivo].slides.map((_, idx) => (
                  <button
                    key={idx}
                    type="button"
                    role="tab"
                    aria-selected={idx === metodoSlide}
                    className={idx === metodoSlide ? "is-active" : ""}
                    onClick={() => setMetodoSlide(idx)}
                    aria-label={`Ir para slide ${idx + 1}`}
                  />
                ))}
              </div>
              <button
                type="button"
                onClick={() => setMetodoSlide((s) => Math.min(METODO_SLIDES[metodoAtivo].slides.length - 1, s + 1))}
                disabled={metodoSlide === METODO_SLIDES[metodoAtivo].slides.length - 1}
              >
                Próximo →
              </button>
            </div>
          </section>
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
      <div id="avaliacao">
        <AvaliacaoImovel/>
      </div>

      {/* ═══════ CTA ═══════ */}
      <section className="ctaH" id="contato">
        <div className="ctaH-inner">
          <span className="metodoH-num" style={{position:"static", marginBottom:"1.5rem", display:"inline-block"}}>§ 07</span>
          <h2>Vamos começar?</h2>
          <p>Mande seu bairro, sua faixa de preço, ou só um “oi”. A IA prepara as opções, eu falo com você.</p>
          <div className="ctaH-row">
            <a href="https://wa.me/5577988193344" target="_blank" rel="noopener" className="btnH btnH-solid btnH-big">
              <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M13.6 2.4A7.5 7.5 0 001.5 12.3L.5 15.5l3.3-1A7.5 7.5 0 1013.6 2.4z"/></svg>
              WhatsApp · (77) 9 8819-3344
            </a>
            <button type="button" className="btnH btnH-ghost btnH-big" onClick={() => abrirChat("Oi, quero iniciar com a IA para encontrar um imóvel.")}>Iniciar com a IA</button>
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
            <span aria-hidden="true">·</span>
            <a href="/admin/?reset=1" rel="nofollow">Área interna</a>
          </div>
        </div>
      </footer>

      {window.ComparadorDrawer && <window.ComparadorDrawer/>}
      <AIChat variant="editorial"/>
      {anuncieOpen && <AnuncieImovel onClose={() => setAnuncieOpen(false)}/>}
      <CookieBanner/>
    </>
  );
}

function NavSimples({ onAnuncieOpen }) {
  return (
    <nav className="navH">
      <div className="navH-inner">
        <a href="#" className="navH-mark" onClick={(e) => { e.preventDefault(); window.location.hash = ""; }}>
          <span className="navH-mark-name">Priscila Vasconcelos</span>
          <span className="navH-mark-sub">Imóveis · IA · Vitória da Conquista</span>
        </a>
        <div className="navH-links">
          <a href="#" onClick={(e) => { e.preventDefault(); window.location.hash = ""; }}>Início</a>
          <a href="#" onClick={(e) => { e.preventDefault(); onAnuncieOpen(); }}>Anuncie seu imóvel</a>
          <a href="/admin/?reset=1" rel="nofollow">Área interna</a>
        </div>
        <a href="https://wa.me/5577988193344" target="_blank" rel="noopener" className="btnH btnH-solid">Falar comigo</a>
      </div>
    </nav>
  );
}

function FooterSimples({ onAnuncieOpen }) {
  return (
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
          <a href="#" onClick={(e) => { e.preventDefault(); onAnuncieOpen(); }}>Anuncie seu imóvel</a>
          <span aria-hidden="true">·</span>
          <a href="/admin/?reset=1" rel="nofollow">Área interna</a>
        </div>
      </div>
    </footer>
  );
}

const root = ReactDOM.createRoot(document.getElementById("app"));
root.render(<App/>);
