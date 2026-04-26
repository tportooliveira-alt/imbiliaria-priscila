// TourMapa — tour 360 (Pannellum, lazy) + mapa Leaflet (lazy) para o detalhe do imóvel.
// Os scripts/CSS são injetados sob demanda (não pesam o bundle inicial).

const _LIBS_CACHE = {};

function _carregarLib(key, css, js) {
  if (_LIBS_CACHE[key]) return _LIBS_CACHE[key];
  _LIBS_CACHE[key] = new Promise((resolve, reject) => {
    if (css) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = css;
      document.head.appendChild(link);
    }
    const s = document.createElement("script");
    s.src = js;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`Falha ao carregar ${key}`));
    document.head.appendChild(s);
  });
  return _LIBS_CACHE[key];
}

function carregarPannellum() {
  return _carregarLib(
    "pannellum",
    "https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.css",
    "https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.js"
  );
}

function carregarLeaflet() {
  return _carregarLib(
    "leaflet",
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css",
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"
  );
}

// Coordenadas aproximadas dos bairros de Vitória da Conquista (centro)
const COORDS_BAIRROS = {
  "Candeias":      [-14.8595, -40.8628],
  "Boa Vista":     [-14.8729, -40.8447],
  "Recreio":       [-14.8634, -40.8332],
  "Patagônia":     [-14.8520, -40.8530],
  "Centro":        [-14.8615, -40.8442],
  "Ibirapuera":    [-14.8721, -40.8512],
  "Alto Maron":    [-14.8783, -40.8612],
  "Felícia":       [-14.8666, -40.8388],
  "Primavera":     [-14.8485, -40.8470],
};

function Tour360({ panoramaUrl, titulo }) {
  const ref = React.useRef(null);
  const [erro, setErro] = React.useState("");

  React.useEffect(() => {
    let viewer = null;
    let cancelado = false;
    carregarPannellum()
      .then(() => {
        if (cancelado || !ref.current) return;
        try {
          viewer = window.pannellum.viewer(ref.current, {
            type: "equirectangular",
            panorama: panoramaUrl,
            autoLoad: true,
            compass: false,
            showZoomCtrl: true,
            showFullscreenCtrl: true,
            hfov: 110,
          });
        } catch (e) {
          setErro("Não foi possível abrir o tour 360 desta foto.");
        }
      })
      .catch(() => setErro("Tour 360 indisponível no momento."));
    return () => {
      cancelado = true;
      try { viewer && viewer.destroy && viewer.destroy(); } catch (e) { /* noop */ }
    };
  }, [panoramaUrl]);

  if (erro) return <div className="tour360-erro">{erro}</div>;
  return (
    <figure className="tour360" aria-label={`Tour 360 · ${titulo || ""}`}>
      <div ref={ref} className="tour360-viewer"/>
      <figcaption>Arraste para girar · scroll para zoom · clique no ícone de tela cheia</figcaption>
    </figure>
  );
}

function MiniMapaImovel({ bairro, titulo }) {
  const ref = React.useRef(null);
  const [erro, setErro] = React.useState("");

  React.useEffect(() => {
    const coords = COORDS_BAIRROS[bairro];
    if (!coords) {
      setErro("Localização aproximada indisponível para este bairro.");
      return;
    }
    let mapa = null;
    let cancelado = false;
    carregarLeaflet()
      .then(() => {
        if (cancelado || !ref.current) return;
        const L = window.L;
        mapa = L.map(ref.current, { scrollWheelZoom: false, zoomControl: true }).setView(coords, 15);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 19,
          attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }).addTo(mapa);
        L.marker(coords).addTo(mapa).bindPopup(`<strong>${titulo || "Imóvel"}</strong><br/>${bairro}`).openPopup();
      })
      .catch(() => setErro("Mapa indisponível no momento."));
    return () => {
      cancelado = true;
      try { mapa && mapa.remove(); } catch (e) { /* noop */ }
    };
  }, [bairro, titulo]);

  if (erro) return <div className="minimapa-erro">{erro}</div>;
  return (
    <figure className="minimapa" aria-label={`Localização aproximada · ${bairro}`}>
      <div ref={ref} className="minimapa-viewer"/>
      <figcaption>Localização aproximada do bairro · endereço exato é compartilhado após a visita</figcaption>
    </figure>
  );
}

Object.assign(window, { Tour360, MiniMapaImovel });
