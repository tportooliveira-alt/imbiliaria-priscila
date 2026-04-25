// OpeningVideo — sequência cinematográfica em 3 fases:
//   FASE 1 — 18s de cenas Ken Burns (cidade, bairros, imóveis, Priscila, outro)
//   FASE 2 — vídeo real gerado por IA (ia-falando.mp4)
//   FASE 3 — vídeo da Priscila falando (priscila-fala.mp4) [opcional]
// Props: variant = "cerulean" | "cinema" | "editorial", onSkip = fn,
//        aspect = "21:9" | "16:9" | "full",
//        videoIa = caminho do mp4 da IA (default ../assets/ia-falando.mp4),
//        videoPriscila = caminho do mp4 da Priscila falando (opcional)

function OpeningVideo({
  variant = "cerulean",
  onSkip,
  aspect = "16:9",
  assetBase = "../assets/",
  videoIa = "../assets/ia-falando.mp4",
  videoPriscila = "../assets/priscila-fala.mp4",
}) {
  // phase: 'kenburns' | 'video-ia' | 'video-priscila' | 'done'
  const [phase, setPhase] = React.useState("kenburns");
  const [elapsed, setElapsed] = React.useState(0);
  const DURATION = 18; // seconds da fase Ken Burns
  const startRef = React.useRef(performance.now());
  const videoIaRef = React.useRef(null);
  const videoPriscilaRef = React.useRef(null);

  // Loop de tempo só durante a fase Ken Burns
  React.useEffect(() => {
    if (phase !== "kenburns") return;
    let raf;
    const loop = t => {
      const e = (t - startRef.current) / 1000;
      setElapsed(Math.min(DURATION, e));
      if (e >= DURATION) {
        setPhase("video-ia");
        return;
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [phase]);

  // Detecta se vídeo da Priscila existe (HEAD request); se 404, pula direto pra done
  const [hasPriscilaVideo, setHasPriscilaVideo] = React.useState(null);
  React.useEffect(() => {
    if (phase !== "video-ia") return;
    fetch(videoPriscila, { method: "HEAD" })
      .then(r => setHasPriscilaVideo(r.ok))
      .catch(() => setHasPriscilaVideo(false));
  }, [phase, videoPriscila]);

  const done = phase === "done";

  // 6 scenes, each ~3 seconds
  const SCENES = [
    { t0: 0,  t1: 3.2, label: "01 · VITÓRIA DA CONQUISTA", type: "drone-wide",
      img: "https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=1600&q=80",
      caption: "Bahia · Sul" },
    { t0: 3.0, t1: 6.4, label: "02 · CANDEIAS · ALTO PADRÃO", type: "drone-neighborhood",
      img: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1600&q=80",
      caption: "42 imóveis ativos" },
    { t0: 6.2, t1: 9.6, label: "03 · INTERIOR · CASA CONTEMPORÂNEA", type: "interior",
      img: "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1600&q=80",
      caption: "4 suítes · R$ 1,48 mi" },
    { t0: 9.4, t1: 12.8, label: "04 · BOA VISTA · CRESCIMENTO", type: "interior",
      img: "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1600&q=80",
      caption: "Primeira compra · R$ 545 mil" },
    { t0: 12.6, t1: 16.0, label: "05 · CORRETORA · PRISCILA VASCONCELOS", type: "portrait",
      img: assetBase + "priscila-new-hero.jpeg",
      caption: "CRECI/BA 29.231" },
    { t0: 15.8, t1: 18.0, label: "06 · ENCONTRE SEU IMÓVEL", type: "outro",
      img: null,
      caption: "IA + toque humano" },
  ];

  const current = SCENES.findLast ? SCENES.findLast(s => elapsed >= s.t0) : [...SCENES].reverse().find(s => elapsed >= s.t0);
  const sceneProgress = current ? Math.min(1, (elapsed - current.t0) / (current.t1 - current.t0)) : 0;
  const pct = elapsed / DURATION;

  const skip = () => {
    // Avança fase a fase: kenburns → video-ia → video-priscila → done
    if (phase === "kenburns") setPhase("video-ia");
    else if (phase === "video-ia") setPhase(hasPriscilaVideo ? "video-priscila" : "done");
    else if (phase === "video-priscila") setPhase("done");
    else { setPhase("done"); onSkip && onSkip(); }
  };

  // Quando atinge 'done', dispara onSkip uma vez
  React.useEffect(() => {
    if (phase === "done") onSkip && onSkip();
  }, [phase]);

  const handleVideoIaEnded = () => {
    setPhase(hasPriscilaVideo ? "video-priscila" : "done");
  };
  const handleVideoPriscilaEnded = () => setPhase("done");

  const aspectCls = aspect === "21:9" ? "ov-21x9" : aspect === "full" ? "ov-full" : "ov-16x9";
  const variantCls = `ov-${variant}`;

  if (done) return null;

  // ───── FASE 2: vídeo real gerado por IA ─────
  if (phase === "video-ia") {
    return (
      <div className={`ov ${aspectCls} ${variantCls} ov-realvideo`}>
        <div className="ov-letterbox ov-letterbox-top" aria-hidden="true"/>
        <div className="ov-letterbox ov-letterbox-bot" aria-hidden="true"/>
        <video
          ref={videoIaRef}
          className="ov-realvideo-el"
          src={videoIa}
          autoPlay
          muted={false}
          playsInline
          onEnded={handleVideoIaEnded}
          onError={handleVideoIaEnded}
        />
        <div className="ov-hud ov-hud-tl">
          <span className="ov-hud-dot"/>
          <span>VÍDEO GERADO POR IA · TEMPO REAL</span>
        </div>
        <div className="ov-hud ov-hud-tr">
          <span className="ov-rec-dot"/>
          <span>07 · A IA APRESENTA</span>
        </div>
        <button className="ov-skip" onClick={skip}>
          Pular
          <svg viewBox="0 0 16 16" width="14" height="14" fill="none">
            <path d="M3 4l5 4-5 4M9 4l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <span className="ov-bracket ov-br-tl"/>
        <span className="ov-bracket ov-br-tr"/>
        <span className="ov-bracket ov-br-bl"/>
        <span className="ov-bracket ov-br-br"/>
      </div>
    );
  }

  // ───── FASE 3: vídeo real da Priscila falando ─────
  if (phase === "video-priscila") {
    return (
      <div className={`ov ${aspectCls} ${variantCls} ov-realvideo`}>
        <div className="ov-letterbox ov-letterbox-top" aria-hidden="true"/>
        <div className="ov-letterbox ov-letterbox-bot" aria-hidden="true"/>
        <video
          ref={videoPriscilaRef}
          className="ov-realvideo-el"
          src={videoPriscila}
          autoPlay
          muted={false}
          playsInline
          onEnded={handleVideoPriscilaEnded}
          onError={handleVideoPriscilaEnded}
        />
        <div className="ov-hud ov-hud-tl">
          <span className="ov-hud-dot"/>
          <span>PRISCILA VASCONCELOS · AO VIVO</span>
        </div>
        <div className="ov-hud ov-hud-tr">
          <span className="ov-rec-dot"/>
          <span>08 · A CORRETORA FALA</span>
        </div>
        <button className="ov-skip" onClick={skip}>
          Pular
          <svg viewBox="0 0 16 16" width="14" height="14" fill="none">
            <path d="M3 4l5 4-5 4M9 4l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <span className="ov-bracket ov-br-tl"/>
        <span className="ov-bracket ov-br-tr"/>
        <span className="ov-bracket ov-br-bl"/>
        <span className="ov-bracket ov-br-br"/>
      </div>
    );
  }

  // ───── FASE 1: cenas Ken Burns (original) ─────
  return (
    <div className={`ov ${aspectCls} ${variantCls}`}>
      {/* letterbox bars */}
      <div className="ov-letterbox ov-letterbox-top" aria-hidden="true"/>
      <div className="ov-letterbox ov-letterbox-bot" aria-hidden="true"/>

      {/* scenes — crossfade */}
      <div className="ov-scenes">
        {SCENES.map((s, i) => {
          const active = elapsed >= s.t0 && elapsed < s.t1;
          const prog = active ? (elapsed - s.t0) / (s.t1 - s.t0) : (elapsed >= s.t1 ? 1 : 0);
          // Ken Burns: zoom 1.05 → 1.18, pan slight
          const scale = 1.05 + prog * 0.13;
          const tx = s.type === "portrait" ? 0 : (prog - 0.5) * 4;
          const ty = s.type === "drone-wide" ? prog * -3 : (prog - 0.5) * 2;
          return (
            <div key={i} className="ov-scene" style={{
              opacity: active ? 1 : 0,
              transition: "opacity 0.6s ease-out",
              zIndex: active ? 2 : 1,
            }}>
              {s.img ? (
                <div className="ov-scene-img-wrap">
                  <img src={s.img} alt="" className="ov-scene-img" style={{
                    transform: `scale(${scale}) translate(${tx}%, ${ty}%)`,
                  }}/>
                  <div className="ov-scene-grade" data-type={s.type}/>
                </div>
              ) : (
                <div className="ov-outro">
                  <div className="ov-outro-mono">PRISCILA VASCONCELOS</div>
                  <div className="ov-outro-title">
                    Imóveis <em>encontrados<br/>pela IA.</em>
                  </div>
                  <div className="ov-outro-sub">Negociados com a seriedade que seu patrimônio exige.</div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* film grain */}
      <div className="ov-grain" aria-hidden="true"/>

      {/* HUD overlay — IA generation label */}
      <div className="ov-hud ov-hud-tl">
        <span className="ov-hud-dot"/>
        <span>RENDERIZADO COM IA · 4K · 60fps</span>
      </div>

      {/* scene label TR */}
      <div className="ov-hud ov-hud-tr">
        <span className="ov-rec-dot"/>
        <span>{current ? current.label : ""}</span>
      </div>

      {/* caption bottom-left */}
      {current && current.caption && (
        <div className="ov-caption" key={current.label}>
          <div className="ov-caption-bar"/>
          <div className="ov-caption-text">{current.caption}</div>
        </div>
      )}

      {/* timecode bottom-right */}
      <div className="ov-hud ov-hud-br ov-mono">
        {formatTimecode(elapsed)} / {formatTimecode(DURATION)}
      </div>

      {/* progress bar */}
      <div className="ov-progress">
        <div className="ov-progress-fill" style={{ width: `${pct * 100}%` }}/>
        <div className="ov-progress-ticks">
          {SCENES.map((s, i) => (
            <span key={i} className="ov-progress-tick" style={{ left: `${(s.t0 / DURATION) * 100}%` }}/>
          ))}
        </div>
      </div>

      {/* skip button */}
      <button className="ov-skip" onClick={skip}>
        Pular intro
        <svg viewBox="0 0 16 16" width="14" height="14" fill="none">
          <path d="M3 4l5 4-5 4M9 4l5 4-5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* corner brackets */}
      <span className="ov-bracket ov-br-tl"/>
      <span className="ov-bracket ov-br-tr"/>
      <span className="ov-bracket ov-br-bl"/>
      <span className="ov-bracket ov-br-br"/>
    </div>
  );
}

function formatTimecode(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = Math.floor(sec % 60).toString().padStart(2, "0");
  const f = Math.floor((sec % 1) * 60).toString().padStart(2, "0");
  return `${m}:${s}:${f}`;
}

Object.assign(window, { OpeningVideo });
