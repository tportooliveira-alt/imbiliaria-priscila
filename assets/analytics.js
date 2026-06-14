/* Rastreamento (Meta Pixel + Google Tag/GA4) — liga sozinho quando os IDs existem no /api/config.
   Expõe window.track(evento, params) p/ conversões nomeadas: calculadora_concluida, lead_anunciar,
   clique_whatsapp, agendar_visita. Sem IDs cadastrados, tudo vira no-op (não quebra nada). */
(function () {
  window.track = function () {}; // no-op até carregar (evita erro se chamar antes)
  var fila = [];
  window.track = function (evento, params) { fila.push([evento, params || {}]); };

  fetch('/api/config').then(function (r) { return r.json(); }).then(function (cfg) {
    var temMeta = cfg && cfg.meta_pixel_id;
    var temGA = cfg && cfg.ga4_id;
    if (!temMeta && !temGA) return; // tracking desligado

    // ── Meta Pixel ──
    if (temMeta) {
      !function (f, b, e, v, n, t, s) {
        if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
        t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
      }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
      window.fbq('init', cfg.meta_pixel_id);
      window.fbq('track', 'PageView');
    }
    // ── Google Tag (GA4) ──
    if (temGA) {
      var g = document.createElement('script'); g.async = true;
      g.src = 'https://www.googletagmanager.com/gtag/js?id=' + cfg.ga4_id;
      document.head.appendChild(g);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date()); window.gtag('config', cfg.ga4_id);
    }

    // mapeia nossos eventos -> eventos padrão do Meta (melhora otimização)
    var META_MAP = { lead_anunciar: 'Lead', calculadora_concluida: 'Lead', agendar_visita: 'Schedule', clique_whatsapp: 'Contact' };
    window.track = function (evento, params) {
      params = params || {};
      try { if (temMeta) window.fbq('trackCustom', evento, params); } catch (e) {}
      try { if (temMeta && META_MAP[evento]) window.fbq('track', META_MAP[evento], params); } catch (e) {}
      try { if (temGA) window.gtag('event', evento, params); } catch (e) {}
    };
    // descarrega o que foi disparado antes de carregar
    fila.forEach(function (x) { window.track(x[0], x[1]); });
  }).catch(function () {});
})();
