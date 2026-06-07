// AgendarVisita — modal disparado pelo botão na página de detalhe.
// Campos: nome, whatsapp, data preferida (próximos 7 dias), turno (manhã/tarde/noite),
// observações opcionais. POST /api/agendar-visita.
// Exposto como window.AgendarVisita e ouvinte global "agendar-visita:abrir".

function _proximosDias(qtd = 7) {
  const dias = [];
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  for (let i = 1; i <= qtd; i++) {
    const d = new Date(hoje);
    d.setDate(d.getDate() + i);
    dias.push(d);
  }
  return dias;
}

function _fmtData(d) {
  const dias = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];
  const meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  return `${dias[d.getDay()]} · ${d.getDate()} ${meses[d.getMonth()]}`;
}

function _isoData(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function AgendarVisita({ codigo, titulo, bairro, precoLabel, onClose }) {
  const dias = React.useMemo(() => _proximosDias(7), []);
  const [nome, setNome] = React.useState("");
  const [tel, setTel] = React.useState("");
  const [data, setData] = React.useState(_isoData(dias[0]));
  const [turno, setTurno] = React.useState("manha");
  const [obs, setObs] = React.useState("");
  const [enviando, setEnviando] = React.useState(false);
  const [resultado, setResultado] = React.useState(null);
  const [erro, setErro] = React.useState(null);

  const formValido =
    nome.trim().length >= 2 &&
    tel.replace(/\D/g, "").length >= 10 &&
    data &&
    !!turno;

  React.useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  async function enviar(e) {
    e.preventDefault();
    if (!formValido || enviando) return;
    setEnviando(true);
    setErro(null);
    try {
      const resp = await fetch("/api/agendar-visita", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nome: nome.trim(),
          telefone: tel.trim(),
          data_preferida: data,
          turno,
          codigo_imovel: codigo || null,
          titulo_imovel: titulo || null,
          bairro: bairro || null,
          observacoes: obs.trim() || null,
        }),
      });
      if (!resp.ok) {
        const t = await resp.text();
        throw new Error(t || "Falha ao enviar");
      }
      const respData = await resp.json();
      setResultado(respData);
    } catch (ex) {
      setErro(ex.message || "Erro de rede. Tenta de novo ou fala direto no WhatsApp.");
    } finally {
      setEnviando(false);
    }
  }

  // Mensagem WhatsApp pré-formatada (CTA secundário ou fallback de erro)
  const turnoLabel = { manha: "manhã", tarde: "tarde", noite: "noite" }[turno] || turno;
  const dataPt = (() => {
    if (!data) return "";
    const [y, m, d] = data.split("-");
    return `${d}/${m}/${y}`;
  })();
  const txtWhats =
    `Oi Priscila! Quero agendar visita ao imóvel ${codigo || ""}${titulo ? " (" + titulo + ")" : ""}.\n` +
    `Nome: ${nome || "(preencher)"}\n` +
    `Data preferida: ${dataPt} · ${turnoLabel}` +
    (obs ? `\nObs: ${obs}` : "");
  const linkWhats = `https://wa.me/5577999395511?text=${encodeURIComponent(txtWhats)}`;

  return (
    <div className="agvi-overlay" onClick={onClose}>
      <div className="agvi-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="agvi-title">
        <button className="agvi-close" onClick={onClose} aria-label="Fechar">×</button>

        {!resultado ? (
          <>
            <header className="agvi-head">
              <span className="agvi-eyebrow">Agendar visita</span>
              <h2 id="agvi-title" className="agvi-title">
                {codigo ? `${codigo} · ${titulo || "Visita guiada"}` : "Visita guiada com a Priscila"}
              </h2>
              {bairro && <p className="agvi-sub">{bairro}{precoLabel ? ` · ${precoLabel}` : ""}</p>}
            </header>

            <form className="agvi-form" onSubmit={enviar}>
              <div className="agvi-row">
                <label className="agvi-label" htmlFor="agvi-nome">Seu nome</label>
                <input
                  id="agvi-nome"
                  type="text"
                  className="agvi-input"
                  placeholder="Como podemos te chamar?"
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  maxLength={120}
                  required
                />
              </div>

              <div className="agvi-row">
                <label className="agvi-label" htmlFor="agvi-tel">WhatsApp</label>
                <input
                  id="agvi-tel"
                  type="tel"
                  className="agvi-input"
                  placeholder="(77) 9 9999-9999"
                  value={tel}
                  onChange={(e) => setTel(e.target.value)}
                  maxLength={30}
                  required
                />
              </div>

              <div className="agvi-row">
                <span className="agvi-label">Quando você prefere?</span>
                <div className="agvi-dias">
                  {dias.map((d) => {
                    const iso = _isoData(d);
                    return (
                      <button
                        type="button"
                        key={iso}
                        className={`agvi-dia${data === iso ? " agvi-dia-on" : ""}`}
                        onClick={() => setData(iso)}
                      >
                        {_fmtData(d)}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="agvi-row">
                <span className="agvi-label">Turno</span>
                <div className="agvi-turnos">
                  {[
                    { id: "manha", label: "Manhã", sub: "8h–12h" },
                    { id: "tarde", label: "Tarde", sub: "13h–18h" },
                    { id: "noite", label: "Noite", sub: "18h–20h" },
                  ].map((t) => (
                    <button
                      type="button"
                      key={t.id}
                      className={`agvi-turno${turno === t.id ? " agvi-turno-on" : ""}`}
                      onClick={() => setTurno(t.id)}
                    >
                      <strong>{t.label}</strong>
                      <span>{t.sub}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="agvi-row">
                <label className="agvi-label" htmlFor="agvi-obs">Algo a destacar? <em>(opcional)</em></label>
                <textarea
                  id="agvi-obs"
                  className="agvi-textarea"
                  placeholder="Ex: vou levar minha esposa, prefiro ver com luz natural, posso só amanhã pela manhã…"
                  value={obs}
                  onChange={(e) => setObs(e.target.value)}
                  maxLength={1000}
                  rows={3}
                />
              </div>

              {erro && (
                <div className="agvi-erro">
                  {erro} <a href={linkWhats} target="_blank" rel="noopener">Falar direto no WhatsApp →</a>
                </div>
              )}

              <button type="submit" className="agvi-btn" disabled={!formValido || enviando}>
                {enviando ? "Enviando…" : "Solicitar visita"}
              </button>

              <p className="agvi-aviso">
                Seus dados ficam apenas com a Priscila Vasconcelos (CRECI/BA 29.231). Não compartilhamos com terceiros.
                A confirmação chega no seu WhatsApp em até 2 horas.
              </p>
            </form>
          </>
        ) : (
          <div className="agvi-ok">
            <div className="agvi-ok-icon">✓</div>
            <h2 className="agvi-title">Visita solicitada!</h2>
            <p className="agvi-ok-sub">{resultado.mensagem}</p>
            <div className="agvi-ok-detalhes">
              <div><span>Imóvel</span><strong>{codigo || "—"}</strong></div>
              <div><span>Data</span><strong>{dataPt}</strong></div>
              <div><span>Turno</span><strong>{turnoLabel}</strong></div>
            </div>
            <a href={linkWhats} target="_blank" rel="noopener" className="agvi-ok-whats">
              Adiantar a conversa no WhatsApp →
            </a>
            <button type="button" className="agvi-ok-fechar" onClick={onClose}>Fechar</button>
          </div>
        )}
      </div>
    </div>
  );
}

window.AgendarVisita = AgendarVisita;
