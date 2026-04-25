// Painel admin — Priscila Vasconcelos Imoveis
const TOKEN_KEY = "pv_admin_token";
const TIPOS_COMODO = [
  ["capa", "Capa"],
  ["sala", "Sala"],
  ["cozinha", "Cozinha"],
  ["quarto", "Quarto"],
  ["banheiro", "Banheiro"],
  ["area_externa", "Area externa"],
  ["planta", "Planta"],
];

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }

async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  const tok = getToken();
  if (tok) headers["Authorization"] = `Bearer ${tok}`;
  if (opts.body && !(opts.body instanceof FormData) && typeof opts.body !== "string") {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(opts.body);
  }
  const r = await fetch(path, { ...opts, headers });
  if (r.status === 401) { clearToken(); window.location.reload(); }
  if (r.status === 204) return null;
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `Erro ${r.status}`);
  return data;
}

function Login({ onLogin }) {
  const [email, setEmail] = React.useState("");
  const [senha, setSenha] = React.useState("");
  const [erro, setErro] = React.useState("");
  const [carregando, setCarregando] = React.useState(false);

  async function submit(e) {
    e.preventDefault();
    setErro(""); setCarregando(true);
    try {
      const r = await api("/api/auth/login", { method: "POST", body: { email, senha } });
      setToken(r.token);
      onLogin({ email: r.email, role: r.role });
    } catch (err) {
      setErro(err.message);
    } finally { setCarregando(false); }
  }

  return (
    <div className="login-screen">
      <form className="login-card" onSubmit={submit}>
        <h1>Painel administrativo</h1>
        <p>Priscila Vasconcelos Imoveis</p>
        {erro && <div className="alerta">{erro}</div>}
        <div className="field">
          <label>E-mail</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required autoFocus />
        </div>
        <div className="field">
          <label>Senha</label>
          <input type="password" value={senha} onChange={e => setSenha(e.target.value)} required minLength={6} />
        </div>
        <button className="btn-primary" disabled={carregando}>
          {carregando ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}

function FormImovel({ inicial, aoSalvar, aoCancelar }) {
  const [dados, setDados] = React.useState(inicial || {
    titulo: "", bairro: "", tipo: "Casa", quartos: 0, suites: 0, vagas: 0,
    area_util: 0, preco: 0, descricao: "", caracteristicas: [], destaque: false, ativo: true,
  });
  const [erro, setErro] = React.useState("");
  const [salvando, setSalvando] = React.useState(false);

  function up(k, v) { setDados(d => ({ ...d, [k]: v })); }

  async function submit(e) {
    e.preventDefault();
    setErro(""); setSalvando(true);
    try {
      if (inicial?.id) {
        await api(`/api/admin/imoveis/${inicial.id}`, { method: "PUT", body: dados });
      } else {
        await api("/api/admin/imoveis", { method: "POST", body: dados });
      }
      aoSalvar();
    } catch (err) { setErro(err.message); }
    finally { setSalvando(false); }
  }

  return (
    <form onSubmit={submit}>
      {erro && <div className="alerta">{erro}</div>}
      <div className="field"><label>Titulo</label><input value={dados.titulo} onChange={e => up("titulo", e.target.value)} required /></div>
      <div className="grid-2">
        <div className="field"><label>Bairro</label><input value={dados.bairro} onChange={e => up("bairro", e.target.value)} required /></div>
        <div className="field"><label>Tipo</label>
          <select value={dados.tipo} onChange={e => up("tipo", e.target.value)}>
            <option>Casa</option><option>Apartamento</option><option>Cobertura</option><option>Terreno</option><option>Comercial</option>
          </select>
        </div>
      </div>
      <div className="grid-3">
        <div className="field"><label>Quartos</label><input type="number" min={0} value={dados.quartos} onChange={e => up("quartos", +e.target.value)} /></div>
        <div className="field"><label>Suites</label><input type="number" min={0} value={dados.suites} onChange={e => up("suites", +e.target.value)} /></div>
        <div className="field"><label>Vagas</label><input type="number" min={0} value={dados.vagas} onChange={e => up("vagas", +e.target.value)} /></div>
      </div>
      <div className="grid-2">
        <div className="field"><label>Area util (m²)</label><input type="number" min={0} step="0.01" value={dados.area_util} onChange={e => up("area_util", +e.target.value)} /></div>
        <div className="field"><label>Preco (R$)</label><input type="number" min={0} step="0.01" value={dados.preco} onChange={e => up("preco", +e.target.value)} required /></div>
      </div>
      <div className="field"><label>Descricao</label><textarea value={dados.descricao} onChange={e => up("descricao", e.target.value)} /></div>
      <div className="field" style={{display: "flex", gap: 18}}>
        <label style={{display: "flex", alignItems: "center", gap: 8, textTransform: "none", letterSpacing: 0, fontSize: 14, color: "#1a1a1a", marginBottom: 0}}>
          <input type="checkbox" style={{width: "auto"}} checked={dados.destaque} onChange={e => up("destaque", e.target.checked)} /> Destaque
        </label>
        <label style={{display: "flex", alignItems: "center", gap: 8, textTransform: "none", letterSpacing: 0, fontSize: 14, color: "#1a1a1a", marginBottom: 0}}>
          <input type="checkbox" style={{width: "auto"}} checked={dados.ativo} onChange={e => up("ativo", e.target.checked)} /> Ativo
        </label>
      </div>
      <div className="modal-foot" style={{padding: 0, borderTop: 0}}>
        <button type="button" className="btn-secondary" onClick={aoCancelar}>Cancelar</button>
        <button className="btn-primary" style={{display: "inline-block", width: "auto"}} disabled={salvando}>
          {salvando ? "Salvando..." : "Salvar"}
        </button>
      </div>
    </form>
  );
}

function GerenciadorImagens({ imovel, aoFechar }) {
  const [imagens, setImagens] = React.useState([]);
  const [enviando, setEnviando] = React.useState(0);
  const [over, setOver] = React.useState(false);
  const [arrastando, setArrastando] = React.useState(null);

  React.useEffect(() => { recarregar(); }, []);

  async function recarregar() {
    const r = await api(`/api/imoveis/${imovel.slug}`);
    setImagens(r.imagens || []);
  }

  async function enviar(arquivos) {
    if (!arquivos?.length) return;
    const lista = Array.from(arquivos).filter(a => a.type.startsWith("image/"));
    if (!lista.length) return;
    setEnviando(lista.length);
    // Define tipo automaticamente: primeira foto vira capa se ainda nao houver
    const temCapa = imagens.some(i => i.tipo === "capa");
    let tipoAuto = temCapa ? "sala" : "capa";
    try {
      for (const arq of lista) {
        const fd = new FormData();
        fd.append("files", arq);
        fd.append("tipo", tipoAuto);
        await api(`/api/admin/imoveis/${imovel.id}/imagens`, { method: "POST", body: fd });
        tipoAuto = "sala";
      }
      await recarregar();
    } catch (e) { alert(e.message); }
    finally { setEnviando(0); }
  }

  async function remover(id) {
    if (!confirm("Remover esta foto?")) return;
    await api(`/api/admin/imagens/${id}`, { method: "DELETE" });
    await recarregar();
  }

  async function mudarTipo(id, tipo) {
    await api(`/api/admin/imagens/${id}`, { method: "PATCH", body: { tipo } });
    await recarregar();
  }

  async function marcarCapa(id) {
    await api(`/api/admin/imagens/${id}`, { method: "PATCH", body: { tipo: "capa" } });
    await recarregar();
  }

  async function reordenar(de, para) {
    if (de === para || de == null || para == null) return;
    const lista = [...imagens];
    const [m] = lista.splice(de, 1);
    lista.splice(para, 0, m);
    setImagens(lista);
    await api(`/api/admin/imoveis/${imovel.id}/imagens/ordem`, {
      method: "PUT", body: { ordem: lista.map(i => i.id) },
    });
    await recarregar();
  }

  return (
    <div>
      <div className={`dropzone ${over ? "is-over" : ""}`}
        onDragOver={e => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={e => { e.preventDefault(); setOver(false); enviar(e.dataTransfer.files); }}
      >
        <p style={{margin: "0 0 6px", fontSize: 15, color: "#1a1a1a"}}>
          <b>Arraste as fotos aqui</b> ou clique no botao
        </p>
        <p style={{margin: "0 0 14px", fontSize: 13, color: "#777"}}>
          A primeira foto vira capa automaticamente. Voce pode trocar depois clicando em <b>Definir capa</b>.
        </p>
        <label htmlFor="upl" className="btn-primary" style={{display: "inline-block", width: "auto", padding: "10px 22px", cursor: "pointer"}}>
          Selecionar fotos do computador
        </label>
        <input id="upl" type="file" multiple accept="image/*" style={{display: "none"}} onChange={e => enviar(e.target.files)} />
        {enviando > 0 && (
          <p style={{marginTop: 14, color: "#2d4a3e"}}>
            Enviando e otimizando {enviando} {enviando === 1 ? "foto" : "fotos"}...
          </p>
        )}
      </div>

      {imagens.length > 0 && (
        <p style={{fontSize: 12, color: "#888", margin: "16px 0 8px"}}>
          {imagens.length} {imagens.length === 1 ? "foto" : "fotos"} · arraste os cards para reordenar · a ordem aqui e a ordem que aparece no site
        </p>
      )}

      <div className="galeria">
        {imagens.map((img, idx) => {
          const ehCapa = img.tipo === "capa";
          return (
            <div
              key={img.id}
              className={`foto-card ${ehCapa ? "is-capa" : ""} ${arrastando === idx ? "is-drag" : ""}`}
              draggable
              onDragStart={() => setArrastando(idx)}
              onDragOver={e => e.preventDefault()}
              onDrop={e => { e.preventDefault(); reordenar(arrastando, idx); setArrastando(null); }}
              onDragEnd={() => setArrastando(null)}
            >
              <div className="foto-thumb" style={{backgroundImage: `url(/assets/${img.arquivo}/600.webp)`}}>
                {ehCapa && <span className="foto-flag">★ CAPA</span>}
                <span className="foto-pos">#{idx + 1}</span>
              </div>
              <div className="foto-acoes">
                <select value={img.tipo} onChange={e => mudarTipo(img.id, e.target.value)} title="Onde foi tirada esta foto">
                  {TIPOS_COMODO.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
                {!ehCapa && (
                  <button type="button" className="btn-mini" onClick={() => marcarCapa(img.id)} title="Usar esta foto como capa">
                    ★ Definir capa
                  </button>
                )}
                <button type="button" className="btn-mini danger" onClick={() => remover(img.id)} title="Remover">
                  ✕ Remover
                </button>
              </div>
            </div>
          );
        })}
      </div>
      {imagens.length === 0 && (
        <p style={{textAlign: "center", color: "#777", marginTop: 24}}>
          Nenhuma foto ainda. Arraste fotos acima para comecar.
        </p>
      )}

      <div className="modal-foot" style={{padding: "16px 0 0"}}>
        <button className="btn-secondary" onClick={aoFechar}>Concluir</button>
      </div>
    </div>
  );
}

function fmtMoeda(n) {
  if (n == null) return "—";
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function fmtData(s) {
  if (!s) return "—";
  const d = new Date(s.replace(" ", "T") + (s.endsWith("Z") ? "" : "Z"));
  return d.toLocaleDateString("pt-BR") + " " + d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

const TEMP_LABEL = { quente: "🔥 Quente", morno: "🟡 Morno", frio: "🧊 Frio" };
const ESTAGIO_LABEL = {
  novo: "Novo", contatado: "Contatado", qualificado: "Qualificado",
  visita: "Visita", proposta: "Proposta", fechado: "Fechado", perdido: "Perdido",
};

function Dashboard() {
  const [d, setD] = React.useState(null);
  const [erro, setErro] = React.useState("");

  React.useEffect(() => {
    api("/api/admin/dashboard").then(setD).catch(e => setErro(e.message));
  }, []);

  if (erro) return <div className="alerta">{erro}</div>;
  if (!d) return <p>Carregando KPIs...</p>;

  const cards = [
    { label: "Leads totais", v: d.total_leads, sub: `+${d.novos_7d} em 7 dias` },
    { label: "Quentes", v: d.por_temperatura?.quente || 0, sub: "alta intencao" },
    { label: "Mornos", v: d.por_temperatura?.morno || 0, sub: "nutrir" },
    { label: "Simulacoes", v: d.simulacoes, sub: "no funil" },
    { label: "Avaliacoes", v: d.avaliacoes, sub: "vendedores" },
    { label: "Imoveis ativos", v: d.imoveis_ativos, sub: "publicados" },
  ];

  return (
    <div>
      <div className="kpi-grid">
        {cards.map(c => (
          <div key={c.label} className="kpi-card">
            <span className="kpi-label">{c.label}</span>
            <span className="kpi-value">{c.v}</span>
            <span className="kpi-sub">{c.sub}</span>
          </div>
        ))}
      </div>

      <h3 style={{marginTop: 32}}>Funil por estagio</h3>
      <div className="funil">
        {Object.keys(ESTAGIO_LABEL).map(k => (
          <div key={k} className="funil-item">
            <span className="funil-label">{ESTAGIO_LABEL[k]}</span>
            <span className="funil-bar"><span style={{width: `${Math.min(100, (d.por_estagio?.[k] || 0) * 10)}%`}} /></span>
            <span className="funil-n">{d.por_estagio?.[k] || 0}</span>
          </div>
        ))}
      </div>

      <h3 style={{marginTop: 32}}>Ultimos leads</h3>
      <table className="tab">
        <thead><tr><th>Quando</th><th>Nome</th><th>Origem</th><th>Estagio</th><th>Temp</th></tr></thead>
        <tbody>
          {(d.ultimos_leads || []).map(l => (
            <tr key={l.id}>
              <td>{fmtData(l.criado_em)}</td>
              <td>{l.nome || l.telefone || "—"}</td>
              <td>{l.origem}</td>
              <td>{ESTAGIO_LABEL[l.estagio] || l.estagio}</td>
              <td>{TEMP_LABEL[l.temperatura] || l.temperatura}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Leads() {
  const [filtros, setFiltros] = React.useState({ estagio: "", temperatura: "", origem: "", busca: "" });
  const [leads, setLeads] = React.useState([]);
  const [sel, setSel] = React.useState(null);
  const [erro, setErro] = React.useState("");

  React.useEffect(() => { recarregar(); }, []);

  async function recarregar() {
    setErro("");
    const qs = new URLSearchParams();
    Object.entries(filtros).forEach(([k, v]) => v && qs.append(k, v));
    try {
      const r = await api("/api/admin/leads?" + qs.toString());
      setLeads(r.leads || []);
    } catch (e) { setErro(e.message); }
  }

  function up(k, v) { setFiltros(f => ({ ...f, [k]: v })); }

  return (
    <div>
      {erro && <div className="alerta">{erro}</div>}
      <div className="filtros">
        <input placeholder="buscar por nome, telefone ou email..."
          value={filtros.busca} onChange={e => up("busca", e.target.value)}
          onKeyDown={e => e.key === "Enter" && recarregar()} />
        <select value={filtros.estagio} onChange={e => { up("estagio", e.target.value); }}>
          <option value="">Todos estagios</option>
          {Object.entries(ESTAGIO_LABEL).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
        </select>
        <select value={filtros.temperatura} onChange={e => up("temperatura", e.target.value)}>
          <option value="">Todas temperaturas</option>
          <option value="quente">🔥 Quente</option>
          <option value="morno">🟡 Morno</option>
          <option value="frio">🧊 Frio</option>
        </select>
        <select value={filtros.origem} onChange={e => up("origem", e.target.value)}>
          <option value="">Todas origens</option>
          <option value="site">Site</option>
          <option value="simulador">Simulador</option>
          <option value="avaliacao">Avaliacao</option>
          <option value="chat">Chat</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="manual">Manual</option>
        </select>
        <button className="btn-secondary" onClick={recarregar}>Filtrar</button>
      </div>

      <table className="tab">
        <thead><tr><th>Atualizado</th><th>Nome</th><th>Contato</th><th>Origem</th><th>Estagio</th><th>Temp</th><th>Score</th><th></th></tr></thead>
        <tbody>
          {leads.map(l => (
            <tr key={l.id}>
              <td>{fmtData(l.atualizado_em)}</td>
              <td>{l.nome || "—"}</td>
              <td>{l.telefone || l.email || "—"}</td>
              <td>{l.origem}</td>
              <td>{ESTAGIO_LABEL[l.estagio] || l.estagio}</td>
              <td>{TEMP_LABEL[l.temperatura] || l.temperatura}</td>
              <td>{l.score}</td>
              <td><button onClick={() => setSel(l.id)}>Abrir</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      {leads.length === 0 && <p style={{textAlign: "center", color: "#555"}}>Nenhum lead encontrado.</p>}

      {sel && <DetalheLead id={sel} aoFechar={() => { setSel(null); recarregar(); }} />}
    </div>
  );
}

function DetalheLead({ id, aoFechar }) {
  const [lead, setLead] = React.useState(null);
  const [nota, setNota] = React.useState("");
  const [erro, setErro] = React.useState("");

  React.useEffect(() => { carregar(); }, [id]);

  async function carregar() {
    try { setLead(await api(`/api/admin/leads/${id}`)); }
    catch (e) { setErro(e.message); }
  }

  async function mudar(campo, valor) {
    await api(`/api/admin/leads/${id}`, { method: "PATCH", body: { [campo]: valor } });
    await carregar();
  }

  async function addNota() {
    if (!nota.trim()) return;
    await api(`/api/admin/leads/${id}/notas`, { method: "POST", body: { descricao: nota } });
    setNota(""); await carregar();
  }

  if (!lead) return null;

  return (
    <div className="modal-bg" onClick={e => e.target === e.currentTarget && aoFechar()}>
      <div className="modal">
        <div className="modal-head">
          <h2>{lead.nome || "Lead #" + lead.id} · {TEMP_LABEL[lead.temperatura]}</h2>
          <button onClick={aoFechar}>×</button>
        </div>
        <div className="modal-body">
          {erro && <div className="alerta">{erro}</div>}
          <div className="grid-2">
            <div>
              <p><b>Telefone:</b> {lead.telefone || "—"}</p>
              <p><b>Email:</b> {lead.email || "—"}</p>
              <p><b>Origem:</b> {lead.origem}</p>
              <p><b>Score:</b> {lead.score}/100</p>
              <p><b>Tags:</b> {(lead.tags || []).join(", ") || "—"}</p>
            </div>
            <div>
              <div className="field">
                <label>Estagio</label>
                <select value={lead.estagio} onChange={e => mudar("estagio", e.target.value)}>
                  {Object.entries(ESTAGIO_LABEL).map(([k, l]) => <option key={k} value={k}>{l}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Observacoes</label>
                <textarea defaultValue={lead.observacoes || ""}
                  onBlur={e => e.target.value !== (lead.observacoes || "") && mudar("observacoes", e.target.value)} />
              </div>
            </div>
          </div>

          <h3 style={{marginTop: 24}}>Adicionar nota</h3>
          <div style={{display: "flex", gap: 8}}>
            <input value={nota} onChange={e => setNota(e.target.value)} placeholder="ligacao feita, falou que..." style={{flex: 1}} />
            <button className="btn-primary" style={{width: "auto"}} onClick={addNota}>Salvar nota</button>
          </div>

          <h3 style={{marginTop: 24}}>Historico ({lead.interacoes?.length || 0})</h3>
          <div className="historico">
            {(lead.interacoes || []).map(i => (
              <div key={i.id} className="hist-item">
                <span className="hist-tipo">{i.tipo}</span>
                <span className="hist-quando">{fmtData(i.criado_em)}</span>
                <p>{i.descricao}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = React.useState(null);
  const [carregando, setCarregando] = React.useState(true);
  const [aba, setAba] = React.useState("dashboard");
  const [imoveis, setImoveis] = React.useState([]);
  const [editando, setEditando] = React.useState(null);
  const [galeria, setGaleria] = React.useState(null);

  React.useEffect(() => {
    if (!getToken()) { setCarregando(false); return; }
    api("/api/auth/me").then(setUser).catch(() => clearToken()).finally(() => setCarregando(false));
  }, []);

  React.useEffect(() => { if (user) recarregar(); }, [user]);

  async function recarregar() {
    const r = await api("/api/imoveis");
    setImoveis(r.items || []);
  }

  async function deletar(id) {
    if (!confirm("Desativar este imovel?")) return;
    await api(`/api/admin/imoveis/${id}`, { method: "DELETE" });
    await recarregar();
  }

  async function togglePublicar(im) {
    const novo = !im.ativo;
    const acao = novo ? "Publicar este imovel no site publico?" : "Tirar este imovel do site (vai virar rascunho)?";
    if (!confirm(acao)) return;
    await api(`/api/admin/imoveis/${im.id}`, { method: "PUT", body: { ...im, ativo: novo } });
    await recarregar();
  }

  function logout() { clearToken(); setUser(null); }

  if (carregando) return <div className="login-screen"><p>Carregando...</p></div>;
  if (!user) return <Login onLogin={setUser} />;

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>Painel · Priscila Vasconcelos Imoveis</h1>
        <nav className="tabs">
          <button className={aba === "dashboard" ? "tab on" : "tab"} onClick={() => setAba("dashboard")}>Dashboard</button>
          <button className={aba === "leads" ? "tab on" : "tab"} onClick={() => setAba("leads")}>Leads</button>
          <button className={aba === "imoveis" ? "tab on" : "tab"} onClick={() => setAba("imoveis")}>Imoveis</button>
        </nav>
        <div>
          <span className="user">{user.email}</span>
          {" "}
          <button onClick={logout}>Sair</button>
        </div>
      </header>

      <main className="main">
        {aba === "dashboard" && <Dashboard />}
        {aba === "leads" && <Leads />}
        {aba === "imoveis" && (<>
        <div className="toolbar">
          <h2>Imoveis ({imoveis.length})</h2>
          <button className="btn-add" onClick={() => setEditando({})}>+ Novo imovel</button>
        </div>

        <div className="grid-imoveis">
          {imoveis.map(im => {
            const capa = im.imagens?.find(i => i.tipo === "capa") || im.imagens?.[0];
            return (
              <div key={im.id} className={`card-imovel ${!im.ativo ? "rascunho" : ""}`}>
                <div className="capa" style={{backgroundImage: capa ? `url(/assets/${capa.arquivo}/600.webp)` : ""}}>
                  {!capa && <span className="capa-vazia">sem foto</span>}
                  <span className={`status-pill ${im.ativo ? "publicado" : "rascunho"}`}>
                    {im.ativo ? "● PUBLICADO" : "○ RASCUNHO"}
                  </span>
                </div>
                <div className="body">
                  <h3>{im.titulo}</h3>
                  <span className="meta">{im.bairro} · {im.tipo} · {im.quartos}q</span>
                  <span className="preco">R$ {im.preco.toLocaleString("pt-BR")}</span>
                </div>
                <div className="acoes">
                  <button onClick={() => setGaleria(im)} className="acao-fotos">
                    📷 Fotos ({im.imagens?.length || 0})
                  </button>
                  <button onClick={() => setEditando(im)}>Editar dados</button>
                  <button
                    className={im.ativo ? "btn-despublicar" : "btn-publicar"}
                    onClick={() => togglePublicar(im)}
                  >
                    {im.ativo ? "Tirar do site" : "Publicar no site"}
                  </button>
                  <button className="danger" onClick={() => deletar(im.id)}>Excluir</button>
                </div>
              </div>
            );
          })}
        </div>
        {imoveis.length === 0 && <p style={{textAlign: "center", color: "#555", marginTop: 40}}>Nenhum imovel cadastrado ainda.</p>}
        </>)}
      </main>

      {editando && (
        <div className="modal-bg" onClick={e => e.target === e.currentTarget && setEditando(null)}>
          <div className="modal">
            <div className="modal-head">
              <h2>{editando.id ? "Editar imovel" : "Novo imovel"}</h2>
              <button onClick={() => setEditando(null)}>×</button>
            </div>
            <div className="modal-body">
              <FormImovel
                inicial={editando.id ? editando : null}
                aoSalvar={() => { setEditando(null); recarregar(); }}
                aoCancelar={() => setEditando(null)}
              />
            </div>
          </div>
        </div>
      )}

      {galeria && (
        <div className="modal-bg" onClick={e => e.target === e.currentTarget && setGaleria(null)}>
          <div className="modal">
            <div className="modal-head">
              <h2>Fotos · {galeria.titulo}</h2>
              <button onClick={() => { setGaleria(null); recarregar(); }}>×</button>
            </div>
            <div className="modal-body">
              <GerenciadorImagens imovel={galeria} aoFechar={() => { setGaleria(null); recarregar(); }} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
