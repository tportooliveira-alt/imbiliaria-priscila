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
  const [enviando, setEnviando] = React.useState(false);
  const [tipo, setTipo] = React.useState("sala");
  const [over, setOver] = React.useState(false);

  React.useEffect(() => { recarregar(); }, []);

  async function recarregar() {
    const r = await api(`/api/imoveis/${imovel.slug}`);
    setImagens(r.imagens || []);
  }

  async function enviar(arquivos) {
    if (!arquivos?.length) return;
    setEnviando(true);
    const fd = new FormData();
    Array.from(arquivos).forEach(a => fd.append("files", a));
    fd.append("tipo", tipo);
    try {
      await api(`/api/admin/imoveis/${imovel.id}/imagens`, { method: "POST", body: fd });
      await recarregar();
    } catch (e) { alert(e.message); }
    finally { setEnviando(false); }
  }

  async function remover(id) {
    if (!confirm("Remover esta imagem?")) return;
    await api(`/api/admin/imagens/${id}`, { method: "DELETE" });
    await recarregar();
  }

  return (
    <div>
      <div className={`dropzone ${over ? "is-over" : ""}`}
        onDragOver={e => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={e => { e.preventDefault(); setOver(false); enviar(e.dataTransfer.files); }}
      >
        <p style={{margin: "0 0 12px"}}>Arraste fotos aqui ou</p>
        <label htmlFor="upl">Selecionar arquivos</label>
        <input id="upl" type="file" multiple accept="image/*" onChange={e => enviar(e.target.files)} />
        <div style={{marginTop: 14}}>
          <label style={{display: "inline", marginRight: 8}}>Comodo:</label>
          <select value={tipo} onChange={e => setTipo(e.target.value)} style={{display: "inline-block", width: "auto"}}>
            {TIPOS_COMODO.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        {enviando && <p style={{marginTop: 12, color: "#2d4a3e"}}>Enviando e otimizando...</p>}
      </div>

      <div className="imgs-grid">
        {imagens.map(img => (
          <div key={img.id} className="img-item" style={{backgroundImage: `url(/assets/${img.arquivo}/200.webp)`}}>
            <span className="badge">{TIPOS_COMODO.find(t => t[0] === img.tipo)?.[1] || img.tipo}</span>
            <button onClick={() => remover(img.id)} title="Remover">×</button>
          </div>
        ))}
      </div>
      {imagens.length === 0 && <p style={{textAlign: "center", color: "#555"}}>Nenhuma imagem ainda.</p>}

      <div className="modal-foot" style={{padding: "16px 0 0"}}>
        <button className="btn-secondary" onClick={aoFechar}>Concluir</button>
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = React.useState(null);
  const [carregando, setCarregando] = React.useState(true);
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

  function logout() { clearToken(); setUser(null); }

  if (carregando) return <div className="login-screen"><p>Carregando...</p></div>;
  if (!user) return <Login onLogin={setUser} />;

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>Painel · Priscila Vasconcelos Imoveis</h1>
        <div>
          <span className="user">{user.email}</span>
          {" "}
          <button onClick={logout}>Sair</button>
        </div>
      </header>

      <main className="main">
        <div className="toolbar">
          <h2>Imoveis ({imoveis.length})</h2>
          <button className="btn-add" onClick={() => setEditando({})}>+ Novo imovel</button>
        </div>

        <div className="grid-imoveis">
          {imoveis.map(im => {
            const capa = im.imagens?.find(i => i.tipo === "capa") || im.imagens?.[0];
            return (
              <div key={im.id} className="card-imovel">
                <div className="capa" style={{backgroundImage: capa ? `url(/assets/${capa.arquivo}/600.webp)` : ""}} />
                <div className="body">
                  <h3>{im.titulo}</h3>
                  <span className="meta">{im.bairro} · {im.tipo} · {im.quartos}q</span>
                  <span className="preco">R$ {im.preco.toLocaleString("pt-BR")}</span>
                  {!im.ativo && <span style={{color: "#a23a2c", fontSize: 12}}>Desativado</span>}
                </div>
                <div className="acoes">
                  <button onClick={() => setEditando(im)}>Editar</button>
                  <button onClick={() => setGaleria(im)}>Fotos ({im.imagens?.length || 0})</button>
                  <button className="danger" onClick={() => deletar(im.id)}>Excluir</button>
                </div>
              </div>
            );
          })}
        </div>
        {imoveis.length === 0 && <p style={{textAlign: "center", color: "#555", marginTop: 40}}>Nenhum imovel cadastrado ainda.</p>}
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
