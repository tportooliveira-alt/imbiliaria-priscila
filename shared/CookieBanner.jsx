// Banner LGPD: pergunta consentimento, salva em localStorage.
// Aparece apenas se ainda nao houve aceite/recusa.

function CookieBanner() {
  const [visivel, setVisivel] = React.useState(() => {
    try {
      return !localStorage.getItem("pv-cookie-consent");
    } catch (_) {
      return false;
    }
  });

  if (!visivel) return null;

  const decidir = (escolha) => {
    try { localStorage.setItem("pv-cookie-consent", escolha); } catch (_) { /* ignore */ }
    setVisivel(false);
  };

  return (
    <div className="cookie-banner" role="region" aria-label="Aviso de cookies">
      <div className="cookie-inner">
        <p>
          Usamos cookies essenciais para o site funcionar e dados de navegação para melhorar a experiência.
          Sem rastreio de terceiros para anúncios. Veja a <a href="./privacidade.html">política completa</a>.
        </p>
        <div className="cookie-actions">
          <button className="cookie-btn cookie-btn-ghost" onClick={() => decidir("recusou")}>Só essenciais</button>
          <button className="cookie-btn cookie-btn-solid" onClick={() => decidir("aceitou")}>Concordo</button>
        </div>
      </div>
    </div>
  );
}

window.CookieBanner = CookieBanner;
