import React, { useState, useEffect } from 'react';
import Home from './Home';
import DetalhesImovel from './DetalhesImovel';
import Lancamentos from './Lancamentos';
import Login from './Login';
import Captacao from './Captacao';
import Sobre from './Sobre';
import BuscaMapa from './BuscaMapa';
import ChatAna from './ChatAna';

export default function App() {
  // Estado inicial vem da URL (?imovel=slug abre o detalhe — link compartilhável)
  const slug0 = new URLSearchParams(window.location.search).get('imovel');
  const [currentPage, setCurrentPage] = useState(slug0 ? 'detalhes' : 'home');
  const [imovelSlug, setImovelSlug] = useState(slug0 || null);
  const [buscaTermo, setBuscaTermo] = useState('');

  // Abre um imóvel e reflete na URL (pra copiar/compartilhar no WhatsApp).
  const abrirImovel = (slug) => {
    setImovelSlug(slug);
    setCurrentPage('detalhes');
    const u = new URL(window.location);
    u.searchParams.set('imovel', slug);
    window.history.pushState({}, '', u);
    window.scrollTo(0, 0);
  };

  const voltarHome = () => {
    setCurrentPage('home');
    setImovelSlug(null);
    const u = new URL(window.location);
    u.searchParams.delete('imovel');
    window.history.pushState({}, '', u);
    window.scrollTo(0, 0);
  };

  const ir = (pg) => { setCurrentPage(pg); window.scrollTo(0, 0); };

  // Botão "voltar" do navegador / celular
  useEffect(() => {
    const onPop = () => {
      const slug = new URLSearchParams(window.location.search).get('imovel');
      if (slug) { setImovelSlug(slug); setCurrentPage('detalhes'); }
      else { setCurrentPage('home'); }
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  let page;
  if (currentPage === 'detalhes') {
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
    page = <BuscaMapa onBack={() => ir('home')} onPropertyClick={abrirImovel} buscaInicial={buscaTermo} />;
  } else {
    page = (
      <Home
        onPropertyClick={abrirImovel}
        onLancamentosClick={() => ir('lancamentos')}
        onLoginClick={() => ir('login')}
        onCaptacaoClick={() => ir('captacao')}
        onSobreClick={() => ir('sobre')}
        onBuscaClick={(termo) => { setBuscaTermo(typeof termo === 'string' ? termo : ''); ir('busca'); }}
      />
    );
  }

  return (
    <>
      {page}
      {/* A Ana acompanha o cliente em todas as telas */}
      <ChatAna />
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
