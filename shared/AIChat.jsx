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
  const bodyRef = React.useRef(null);

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

  const send = text => {
    const userText = (text ?? input).trim();
    if (!userText) return;
    setMsgs(m => [...m, { role: "user", text: userText, t: Date.now() }]);
    setInput("");
    setTyping(true);
    // Typing delay based on response length feel (~1.2s)
    setTimeout(() => {
      setTyping(false);
      setMsgs(m => [...m, { role: "ai", text: window.aiChatResponse(userText), t: Date.now() }]);
    }, 1200 + Math.random() * 600);
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
              <div className="aic-avatar"><span>IA</span></div>
              <div>
                <div className="aic-title">Assistente Priscila · IA</div>
                <div className="aic-status"><span className="aic-status-dot"/> Online · responde em &lt; 2 min</div>
              </div>
            </div>
            <button className="aic-close" onClick={() => setOpen(false)} aria-label="Fechar">
              <svg viewBox="0 0 12 12" width="14" height="14"><path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
            </button>
          </header>

          <div className="aic-body" ref={bodyRef}>
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
