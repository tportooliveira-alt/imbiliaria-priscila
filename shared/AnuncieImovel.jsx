// Modal "Anuncie seu imóvel" — captura lead vendedor (origem=vendedor)
// Posta em /api/lead-vendedor; em caso de erro de rede, abre WhatsApp como fallback.

function AnuncieImovel({ onClose }) {
  const [form, setForm] = React.useState({
    nome: "", telefone: "", bairro: "", tipo: "Casa",
    area: "", quartos: "", valor_pretendido: "", observacoes: "",
  });
  const [status, setStatus] = React.useState("idle"); // idle | enviando | ok | erro
  const [erro, setErro] = React.useState("");

  const onChange = (campo) => (e) => setForm(f => ({ ...f, [campo]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setStatus("enviando");
    setErro("");
    try {
      const resp = await fetch("/api/lead-vendedor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          area: form.area ? Number(form.area) : null,
          quartos: form.quartos ? Number(form.quartos) : null,
          valor_pretendido: form.valor_pretendido ? Number(form.valor_pretendido) : null,
        }),
      });
      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data.detail || "Não consegui enviar agora.");
      }
      setStatus("ok");
    } catch (err) {
      setStatus("erro");
      setErro(err.message || "Falha de conexão.");
    }
  };

  const fallbackWhats = () => {
    const txt = `Olá Priscila! Quero anunciar meu imóvel:\n\n` +
      `Nome: ${form.nome}\nTelefone: ${form.telefone}\n` +
      `Bairro: ${form.bairro}\nTipo: ${form.tipo}\n` +
      (form.area ? `Área: ${form.area} m²\n` : "") +
      (form.quartos ? `Quartos: ${form.quartos}\n` : "") +
      (form.valor_pretendido ? `Valor pretendido: R$ ${form.valor_pretendido}\n` : "") +
      (form.observacoes ? `\n${form.observacoes}\n` : "");
    window.open(`https://wa.me/5577988193344?text=${encodeURIComponent(txt)}`, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="anuncie-overlay" role="dialog" aria-modal="true" aria-labelledby="anuncie-title" onClick={onClose}>
      <div className="anuncie-modal" onClick={(e) => e.stopPropagation()}>
        <button className="anuncie-close" onClick={onClose} aria-label="Fechar">×</button>

        {status !== "ok" ? (
          <>
            <header className="anuncie-head">
              <span className="anuncie-eyebrow">§ Captação</span>
              <h2 id="anuncie-title">Anuncie seu imóvel</h2>
              <p>A Priscila avalia em até <strong>24h</strong>, monta o dossiê com IA e só publica se fizer sentido pro seu objetivo. Sem contrato de exclusividade abusivo.</p>
            </header>

            <form className="anuncie-form" onSubmit={submit}>
              <div className="anuncie-row">
                <label>
                  <span>Seu nome *</span>
                  <input required type="text" value={form.nome} onChange={onChange("nome")} maxLength={120}/>
                </label>
                <label>
                  <span>Telefone / WhatsApp *</span>
                  <input required type="tel" value={form.telefone} onChange={onChange("telefone")} placeholder="(77) 9 ____-____" maxLength={30}/>
                </label>
              </div>

              <div className="anuncie-row">
                <label>
                  <span>Bairro</span>
                  <input type="text" value={form.bairro} onChange={onChange("bairro")} maxLength={80}/>
                </label>
                <label>
                  <span>Tipo</span>
                  <select value={form.tipo} onChange={onChange("tipo")}>
                    <option>Casa</option>
                    <option>Apartamento</option>
                    <option>Cobertura</option>
                    <option>Terreno</option>
                    <option>Comercial</option>
                  </select>
                </label>
              </div>

              <div className="anuncie-row anuncie-row-3">
                <label>
                  <span>Área útil (m²)</span>
                  <input type="number" min="1" value={form.area} onChange={onChange("area")}/>
                </label>
                <label>
                  <span>Quartos</span>
                  <input type="number" min="0" max="20" value={form.quartos} onChange={onChange("quartos")}/>
                </label>
                <label>
                  <span>Valor pretendido (R$)</span>
                  <input type="number" min="0" value={form.valor_pretendido} onChange={onChange("valor_pretendido")}/>
                </label>
              </div>

              <label className="anuncie-textarea">
                <span>Conta um pouco sobre o imóvel (opcional)</span>
                <textarea rows={3} maxLength={1000} value={form.observacoes} onChange={onChange("observacoes")} placeholder="Reformado em 2023, vista pra serra, vaga coberta..."/>
              </label>

              {status === "erro" && (
                <div className="anuncie-erro">
                  <p>{erro}</p>
                  <button type="button" className="anuncie-fallback" onClick={fallbackWhats}>Enviar por WhatsApp ⟶</button>
                </div>
              )}

              <div className="anuncie-actions">
                <small>Ao enviar você concorda com a <a href="./privacidade.html" target="_blank" rel="noopener">política de privacidade</a>.</small>
                <button type="submit" className="anuncie-submit" disabled={status === "enviando"}>
                  {status === "enviando" ? "Enviando..." : "Quero anunciar"}
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="anuncie-ok">
            <div className="anuncie-ok-icon">✓</div>
            <h2>Recebido!</h2>
            <p>A Priscila te chama em até <strong>24h</strong>. Se quiser adiantar, manda mensagem direto:</p>
            <a className="anuncie-whats" href="https://wa.me/5577988193344" target="_blank" rel="noopener">WhatsApp · (77) 9 8819-3344</a>
            <button className="anuncie-fechar" onClick={onClose}>Fechar</button>
          </div>
        )}
      </div>
    </div>
  );
}

window.AnuncieImovel = AnuncieImovel;
