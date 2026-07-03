import React, { useState, useEffect } from 'react';
import Home from './Home';
import DetalhesImovel from './DetalhesImovel';
import Lancamentos from './Lancamentos';
import Login from './Login';
import Captacao from './Captacao';
import Sobre from './Sobre';
import BuscaMapa from './BuscaMapa';
import ChatAna from './ChatAna';
import Calculadoras from './Calculadoras';

export default function App() {
  // slug do imóvel: do caminho bonito /i/<slug> (com preview no WhatsApp) OU do
  // formato antigo ?imovel=<slug> (links já compartilhados continuam funcionando).
  const slugDaUrl = () => {
    const m = window.location.pathname.match(/^\/i\/([^/?#]+)/);
    return m ? decodeURIComponent(m[1]) : new URLSearchParams(window.location.search).get('imovel');
  };
  // Estado inicial vem da URL
  const params0 = new URLSearchParams(window.location.search);
  const slug0 = slugDaUrl();
  // Página de calculadoras é de TESTE: só abre por ?calc=1 (fora do menu).
  const calc0 = params0.has('calc');
  const [currentPage, setCurrentPage] = useState(calc0 ? 'calculadoras' : slug0 ? 'detalhes' : 'home');
  const [imovelSlug, setImovelSlug] = useState(slug0 || null);
  const [buscaTermo, setBuscaTermo] = useState('');
  const [buscaFinalidade, setBuscaFinalidade] = useState('todos');

  // Abre um imóvel e reflete na URL (pra copiar/compartilhar no WhatsApp).
  const abrirImovel = (slug) => {
    setImovelSlug(slug);
    setCurrentPage('detalhes');
    // URL bonita /i/<slug> — é a que mostra a capa quando colada no WhatsApp.
    window.history.pushState({}, '', '/i/' + slug);
    window.scrollTo(0, 0);
  };

  const voltarHome = () => {
    setCurrentPage('home');
    setImovelSlug(null);
    window.history.pushState({}, '', '/');
    window.scrollTo(0, 0);
  };

  const ir = (pg) => { setCurrentPage(pg); window.scrollTo(0, 0); };

  // Botão "voltar" do navegador / celular
  useEffect(() => {
    const onPop = () => {
      const slug = slugDaUrl();
      if (slug) { setImovelSlug(slug); setCurrentPage('detalhes'); }
      else { setCurrentPage('home'); }
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  let page;
  if (currentPage === 'calculadoras') {
    page = <Calculadoras onBack={() => { const u = new URL(window.location); u.searchParams.delete('calc'); window.history.pushState({}, '', u); ir('home'); }} />;
  } else if (currentPage === 'detalhes') {
    page = <DetalhesImovel slug={imovelSlug} onBack={voltarHome} />;
  } else if (currentPage === 'lancamentos') {
    page = <Lancamentos onBack={() => ir('home')} onLoginClick={() => ir('login')} />;
  } else if (currentPage === 'login') {
    page = <Login onBack={() => ir('home')} />;
  } else if (currentPage === 'captacao') {
    page = <Captacao onBack={() => ir('home')} />;
  } else if (currentPage === 'sobre') {
    page = <Sobre onBack={() => ir('home')} />;
  } else if (currentPage === 'busca') {
    page = <BuscaMapa onBack={() => ir('home')} onPropertyClick={abrirImovel} buscaInicial={buscaTermo} finalidadeInicial={buscaFinalidade} />;
  } else {
    page = (
      <Home
        onPropertyClick={abrirImovel}
        onLancamentosClick={() => ir('lancamentos')}
        onLoginClick={() => ir('login')}
        onCaptacaoClick={() => ir('captacao')}
        onSobreClick={() => ir('sobre')}
        onBuscaClick={(arg) => {
          const termo = typeof arg === 'string' ? arg : (arg?.termo || '');
          const fin = (arg && typeof arg === 'object' && arg.finalidade) ? arg.finalidade : 'todos';
          setBuscaTermo(termo); setBuscaFinalidade(fin); ir('busca');
        }}
        onCalculadorasClick={() => { const u = new URL(window.location); u.searchParams.set('calc', '1'); window.history.pushState({}, '', u); ir('calculadoras'); }}
      />
    );
  }

  return (
    <>
      {page}
      {/* A Ana acompanha o cliente em todas as telas — MENOS na calculadora,
          que tem o próprio agente-guia (só sabe do sistema). */}
      {currentPage !== 'calculadoras' && <ChatAna />}
      {/* Botão WhatsApp fixo — sempre visível em todas as páginas */}
      <a
        href="https://wa.me/5577999395511?text=Olá%20Priscila!%20Vi%20seu%20site%20e%20gostaria%20de%20mais%20informações."
        target="_blank"
        rel="noreferrer"
        title="Falar com a Priscila no WhatsApp"
        style={{ bottom: '7.5rem' }}
        className="fixed right-6 z-[60] flex items-center gap-2.5 bg-[#25D366] text-white pl-2 pr-5 py-2 rounded-full shadow-2xl hover:scale-105 transition-transform animate-pulse-slow"
      >
        <span dangerouslySetInnerHTML={{__html: `<style>@keyframes pulseSlow{0%,100%{box-shadow:0 0 0 0 rgba(37,211,102,.5)}50%{box-shadow:0 0 0 12px rgba(37,211,102,0)}}.animate-pulse-slow{animation:pulseSlow 2s infinite}</style>`}} />
        <svg viewBox="0 0 48 48" width="40" height="40" xmlns="http://www.w3.org/2000/svg">
          <circle cx="24" cy="24" r="24" fill="white"/>
          <path fill="#25D366" d="M24 10.5C16.5 10.5 10.5 16.5 10.5 24c0 2.4.65 4.7 1.8 6.7L10.5 37.5l6.95-1.8A13.4 13.4 0 0 0 24 37.5c7.5 0 13.5-6 13.5-13.5S31.5 10.5 24 10.5zm6.6 18.4c-.28.78-1.6 1.5-2.2 1.56-.57.06-1.1.28-3.7-.77-3.1-1.27-5.1-4.44-5.25-4.65-.15-.2-1.2-1.6-1.2-3.06 0-1.45.76-2.17 1.03-2.47.27-.3.6-.37.8-.37h.57c.18 0 .44-.07.68.52l.97 2.37c.08.2.04.43-.07.6l-.55.8-.2.3c.14.24.7 1.1 1.5 1.78.97.83 1.8 1.1 2.06 1.22.25.12.4.1.55-.06l.73-.87c.15-.2.3-.14.5-.08l2.3.93c.22.09.36.13.4.22.04.1.04.55-.24 1.33z"/>
        </svg>
        <span className="text-sm font-semibold tracking-wide">WhatsApp</span>
      </a>
    </>
  );
}
