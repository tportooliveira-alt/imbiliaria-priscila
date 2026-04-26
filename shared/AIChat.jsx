// AIChat — floating conversational AI widget, fake but convincing
// Minimizable bubble → expanded chat with typing indicator, suggestions, intro
// Props: variant = "cerulean" | "cinema" | "editorial"

function AIChat({ variant = "cerulean" }) {
  const [open, setOpen] = React.useState(false);
  const [msgs, setMsgs] = React.useState([
    { role: "ai", text: window.IA_CHAT_INTRO, t: Date.now() },
  ]);
  const [typing, setTyping] = React.useState(false);
  const [input, setInput] = React.useState("");
  const [showTeaser, setShowTeaser] = React.useState(false);
  const [netError, setNetError] = React.useState("");
  const [leadMeta, setLeadMeta] = React.useState(null);
  const [analysis, setAnalysis] = React.useState(null);
  const [funnel, setFunnel] = React.useState(null);
  const [analysisBusy, setAnalysisBusy] = React.useState(false);
  const [sessionId, setSessionId] = React.useState(() => window.sessionStorage.getItem("pv-chat-session") || "");
  const bodyRef = React.useRef(null);

  React.useEffect(() => {
    if (!sessionId) return;
    window.sessionStorage.setItem("pv-chat-session", sessionId);
  }, [sessionId]);

  // Scroll to bottom on new message
  React.useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [msgs, typing]);

  // Auto-show teaser bubble after 4 seconds the first time
  React.useEffect(() => {
    if (open) return;
    const t = setTimeout(() => setShowTeaser(true), 4500);
    return () => clearTimeout(t);
  }, [open]);

  React.useEffect(() => {
    if (!open) return;
    fetch("/api/funnel")
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setFunnel(data);
      })
      .catch(() => {});
  }, [open, msgs.length]);

  const toApiHistory = list => list
    .filter(m => m.role === "user" || m.role === "ai")
    .slice(-12)
    .map(m => ({
      role: m.role === "ai" ? "assistant" : "user",
      content: m.text,
    }));

  const send = async text => {
    const userText = (text ?? input).trim();
    if (!userText) return;

    setNetError("");
    setMsgs(m => [...m, { role: "user", text: userText, t: Date.now() }]);
    setInput("");
    setTyping(true);

    const historyPayload = toApiHistory(msgs);

    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          history: historyPayload,
          session_id: sessionId || undefined,
        }),
      });

      if (!r.ok) {
        throw new Error(`HTTP ${r.status}`);
      }

      const data = await r.json();
      setTyping(false);
      if (data.session_id) setSessionId(data.session_id);
      setLeadMeta({
        score: data.lead_score,
        stage: data.lead_stage,
        nextQuestion: data.lead_next_question,
        fields: data.lead_fields,
        providerMetadata: data.provider_metadata || {},
        route: data.rota,
        model: data.modelo,
      });
      setMsgs(m => [...m, { role: "ai", text: data.resposta || "Sem resposta no momento.", t: Date.now() }]);
    } catch (err) {
      setTyping(false);
      setNetError("Conexao instavel. Vou te responder em modo local.");
      setMsgs(m => [...m, { role: "ai", text: window.aiChatResponse(userText), t: Date.now() }]);
    }
  };

  const runAnalysis = async () => {
    const historyPayload = toApiHistory(msgs);
    if (!historyPayload.length) return;

    setAnalysisBusy(true);
    try {
      const r = await fetch("/api/analisar-lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history: historyPayload, session_id: sessionId || undefined }),
      });

      if (!r.ok) {
        throw new Error(`HTTP ${r.status}`);
      }

      const data = await r.json();
      setAnalysis(data);
    } catch (err) {
      setAnalysis({ resumo: "Nao foi possivel gerar a analise agora.", fallback: true });
    } finally {
      setAnalysisBusy(false);
    }
  };

  const sugestoesVisiveis = msgs.length <= 2;

  return (
    <div className={`aic aic-${variant}`}>
      {/* Teaser bubble when closed */}
      {!open && showTeaser && (
        <div className="aic-teaser" onClick={() => { setOpen(true); setShowTeaser(false); }}>
          <span>Posso te ajudar a achar seu imóvel? 👋</span>
          <button className="aic-teaser-close" onClick={e => { e.stopPropagation(); setShowTeaser(false); }} aria-label="Fechar">
            <svg viewBox="0 0 12 12" width="10" height="10"><path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
          </button>
        </div>
      )}

      {/* Collapsed bubble */}
      {!open && (
        <button className="aic-bubble" onClick={() => { setOpen(true); setShowTeaser(false); }} aria-label="Abrir chat com IA">
          <span className="aic-bubble-dot"/>
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" aria-hidden="true">
            <path d="M12 3a9 9 0 00-9 9 9 9 0 009 9h4.5l3 3v-3a9 9 0 001.5-5.5A9 9 0 0012 3z"
              stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
            <circle cx="8.5" cy="12" r="1.1" fill="currentColor"/>
            <circle cx="12"  cy="12" r="1.1" fill="currentColor"/>
            <circle cx="15.5" cy="12" r="1.1" fill="currentColor"/>
          </svg>
        </button>
      )}

      {/* Expanded chat */}
      {open && (
        <div className="aic-panel">
          <header className="aic-header">
            <div className="aic-ident">
              <div className="aic-avatar"><span>PV</span></div>
              <div>
                <div className="aic-title">Atendimento Priscila Vasconcelos</div>
                <div className="aic-status"><span className="aic-status-dot"/> Online agora · CRECI/BA 29.231</div>
              </div>
            </div>
            <button className="aic-close" onClick={() => setOpen(false)} aria-label="Fechar">
              <svg viewBox="0 0 12 12" width="14" height="14"><path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
            </button>
          </header>

          <div className="aic-body" ref={bodyRef}>
            {(leadMeta || analysis || funnel) && (
              <section className="aic-insights">
                <div className="aic-insights-head">
                  <strong>Painel da conversa</strong>
                  <button type="button" className="aic-mini-btn" onClick={runAnalysis} disabled={analysisBusy}>
                    {analysisBusy ? "Lendo..." : "Analisar lead"}
                  </button>
                </div>

                {leadMeta && (
                  <div className="aic-cards">
                    <div className="aic-card">
                      <span>Estagio</span>
                      <strong>{leadMeta.stage}</strong>
                    </div>
                    <div className="aic-card">
                      <span>Score</span>
                      <strong>{leadMeta.score}</strong>
                    </div>
                    <div className="aic-card aic-card-wide">
                      <span>Proxima pergunta</span>
                      <strong>{leadMeta.nextQuestion}</strong>
                    </div>
                    <div className="aic-card aic-card-wide">
                      <span>Rota / modelo</span>
                      <strong>{leadMeta.route} · {leadMeta.model}</strong>
                    </div>
                    {leadMeta.providerMetadata?.grounded && (
                      <div className="aic-card aic-card-wide">
                        <span>Busca Google</span>
                        <strong>Grounding ativo nesta resposta</strong>
                      </div>
                    )}
                  </div>
                )}

                {analysis?.resumo && (
                  <div className="aic-analysis-box">
                    <span>Analise pos-conversa</span>
                    <p>{analysis.resumo}</p>
                  </div>
                )}

                {funnel?.stages && (
                  <div className="aic-funnel-box">
                    <span>Funil local</span>
                    <div className="aic-funnel-grid">
                      {Object.entries(funnel.stages).map(([stage, total]) => (
                        <div key={stage} className="aic-funnel-item">
                          <strong>{total}</strong>
                          <span>{stage}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}

            {netError && (
              <div className="aic-msg aic-msg-ai">
                <span className="aic-msg-mark">IA</span>
                <div className="aic-bubble-msg">{netError}</div>
              </div>
            )}
            {msgs.map((m, i) => (
              <div key={i} className={`aic-msg aic-msg-${m.role}`}>
                {m.role === "ai" && <span className="aic-msg-mark">IA</span>}
                <div className="aic-bubble-msg">{m.text}</div>
              </div>
            ))}
            {typing && (
              <div className="aic-msg aic-msg-ai">
                <span className="aic-msg-mark">IA</span>
                <div className="aic-bubble-msg aic-typing">
                  <span/><span/><span/>
                </div>
              </div>
            )}
            {sugestoesVisiveis && !typing && (
              <div className="aic-sugestoes">
                {window.IA_CHAT_SUGESTOES.map(s => (
                  <button key={s} className="aic-sug" onClick={() => send(s)}>{s}</button>
                ))}
              </div>
            )}
          </div>

          <form className="aic-input" onSubmit={e => { e.preventDefault(); send(); }}>
            <input
              type="text"
              placeholder="Digite sua mensagem..."
              value={input}
              onChange={e => setInput(e.target.value)}
              autoFocus
            />
            <button type="submit" aria-label="Enviar" disabled={!input.trim()}>
              <svg viewBox="0 0 16 16" width="16" height="16" fill="none">
                <path d="M2 8h12M9 4l5 4-5 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { AIChat });
