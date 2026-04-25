// Lightbox — galeria em tela cheia com carrossel e miniaturas agrupadas por comodo.
// Props: imagens [{arquivo, tipo, legenda}], indice, onClose, onIndice
// Espera que cada imagem tenha 4 versoes WebP em /assets/{arquivo}/{tamanho}.webp

const LIGHTBOX_LARGURAS = [200, 600, 1200, 2400];

function urlImagem(arquivo, tamanho) {
  return `/assets/${arquivo}/${tamanho}.webp`;
}

function srcSet(arquivo) {
  return LIGHTBOX_LARGURAS
    .map(w => `${urlImagem(arquivo, w)} ${w}w`)
    .join(", ");
}

const RotuloComodo = {
  capa: "Capa",
  sala: "Sala",
  cozinha: "Cozinha",
  quarto: "Quarto",
  banheiro: "Banheiro",
  area_externa: "Area externa",
  planta: "Planta",
};

function Lightbox({ imagens, indice, onClose, onIndice }) {
  const total = imagens.length;
  const atual = imagens[indice];

  React.useEffect(() => {
    const onKey = e => {
      if (e.key === "Escape") onClose();
      else if (e.key === "ArrowRight") onIndice((indice + 1) % total);
      else if (e.key === "ArrowLeft") onIndice((indice - 1 + total) % total);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [indice, total, onClose, onIndice]);

  if (!atual) return null;

  // Agrupa miniaturas por tipo de comodo, preservando ordem original
  const grupos = imagens.reduce((acc, img, i) => {
    const tipo = img.tipo || "sala";
    if (!acc[tipo]) acc[tipo] = [];
    acc[tipo].push({ ...img, _idx: i });
    return acc;
  }, {});

  return (
    <div className="lbx" role="dialog" aria-label="Galeria de fotos do imovel">
      <button className="lbx-close" onClick={onClose} aria-label="Fechar galeria">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
          <path d="M5 5l14 14M19 5L5 19" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
        </svg>
      </button>

      <div className="lbx-stage">
        <button
          className="lbx-arrow lbx-arrow-prev"
          onClick={() => onIndice((indice - 1 + total) % total)}
          aria-label="Foto anterior"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none">
            <path d="M15 6l-6 6 6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>

        <picture className="lbx-picture">
          <source srcSet={srcSet(atual.arquivo)} sizes="100vw" type="image/webp"/>
          <img
            className="lbx-img"
            src={urlImagem(atual.arquivo, 1200)}
            alt={atual.legenda || RotuloComodo[atual.tipo] || "Foto do imovel"}
            decoding="async"
            loading="eager"
          />
        </picture>

        <button
          className="lbx-arrow lbx-arrow-next"
          onClick={() => onIndice((indice + 1) % total)}
          aria-label="Proxima foto"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none">
            <path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      <div className="lbx-meta">
        <span>{indice + 1} / {total}</span>
        {atual.legenda && <em>{atual.legenda}</em>}
      </div>

      <div className="lbx-thumbs">
        {Object.entries(grupos).map(([tipo, lista]) => (
          <div key={tipo} className="lbx-thumb-group">
            <strong>{RotuloComodo[tipo] || tipo} ({lista.length})</strong>
            <div className="lbx-thumb-row">
              {lista.map(img => (
                <button
                  key={img.id}
                  className={`lbx-thumb ${img._idx === indice ? "is-active" : ""}`}
                  onClick={() => onIndice(img._idx)}
                  aria-label={`Foto ${img._idx + 1}`}
                >
                  <img src={urlImagem(img.arquivo, 200)} alt="" loading="lazy"/>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GaleriaImovel({ imagens }) {
  const [aberta, setAberta] = React.useState(false);
  const [indice, setIndice] = React.useState(0);

  if (!imagens || imagens.length === 0) return null;

  const capa = imagens.find(i => i.tipo === "capa") || imagens[0];

  return (
    <div className="gal">
      <button
        className="gal-trigger"
        onClick={() => { setIndice(imagens.indexOf(capa)); setAberta(true); }}
        aria-label="Abrir galeria"
      >
        <picture>
          <source srcSet={srcSet(capa.arquivo)} sizes="(max-width: 720px) 100vw, 720px" type="image/webp"/>
          <img
            src={urlImagem(capa.arquivo, 1200)}
            alt={capa.legenda || "Foto do imovel"}
            loading="lazy"
            decoding="async"
          />
        </picture>
        <span className="gal-badge">Ver {imagens.length} fotos</span>
      </button>

      {aberta && (
        <Lightbox
          imagens={imagens}
          indice={indice}
          onClose={() => setAberta(false)}
          onIndice={setIndice}
        />
      )}
    </div>
  );
}

Object.assign(window, { Lightbox, GaleriaImovel });
