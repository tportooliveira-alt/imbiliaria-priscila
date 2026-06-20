import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Sparkles } from 'lucide-react';
import { enviarChat } from './api';

const SAUDACAO = 'Oi! Aqui é a Ana, assistente da Priscila Vasconcelos 😊 Posso te ajudar a encontrar um imóvel, tirar dúvidas de financiamento ou avaliar o seu. Como posso te ajudar?';

export default function ChatAna() {
  const [aberto, setAberto] = useState(false);
  const [bolha, setBolha] = useState(false);
  const [msgs, setMsgs] = useState([{ role: 'assistant', content: SAUDACAO }]);
  const [texto, setTexto] = useState('');
  const [enviando, setEnviando] = useState(false);
  const fimRef = useRef(null);

  useEffect(() => {
    fimRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [msgs, aberto]);

  // Bolha de saudação automática após 8 segundos (só na primeira vez)
  useEffect(() => {
    const jaViu = sessionStorage.getItem('ana-bolha');
    if (jaViu) return;
    const t = setTimeout(() => {
      setBolha(true);
      sessionStorage.setItem('ana-bolha', '1');
    }, 8000);
    return () => clearTimeout(t);
  }, []);

  // Qualquer botão do site pode abrir a Ana (dispara o evento 'abrir-ana').
  useEffect(() => {
    const abrir = () => { setAberto(true); setBolha(false); };
    window.addEventListener('abrir-ana', abrir);
    return () => window.removeEventListener('abrir-ana', abrir);
  }, []);

  async function enviar(e) {
    e?.preventDefault();
    const pergunta = texto.trim();
    if (!pergunta || enviando) return;
    setTexto('');
    const novo = [...msgs, { role: 'user', content: pergunta }];
    setMsgs(novo);
    setEnviando(true);
    try {
      // histórico = só as trocas reais (tira a saudação inicial)
      const historico = novo.filter((m, i) => !(i === 0 && m.content === SAUDACAO));
      const data = await enviarChat(pergunta, historico.slice(0, -1));
      setMsgs((m) => [...m, { role: 'assistant', content: data.resposta || 'Desculpa, não consegui responder agora.' }]);
    } catch {
      setMsgs((m) => [...m, { role: 'assistant', content: 'Tive um probleminha aqui 😕 Pode tentar de novo? Se preferir, falo com a Priscila pra te retornar.' }]);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      {/* Botão flutuante */}
      {!aberto && (
        <button
          onClick={() => setAberto(true)}
          className="fixed bottom-6 right-6 z-[60] flex items-center gap-3 bg-[#16284B] text-white pl-4 pr-5 py-3.5 rounded-full shadow-2xl hover:bg-[#0f1c38] transition-all group"
        >
          <span className="relative flex items-center justify-center w-9 h-9 bg-grad-gold rounded-full text-[#16284B]">
            <Sparkles size={18} />
            <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-[#c9943a] rounded-full border-2 border-[#16284B] animate-pulse"></span>
          </span>
          <span className="text-sm font-medium tracking-wide">Falar com a Ana</span>
        </button>
      )}

      {/* Painel do chat */}
      {aberto && (
        <div className="fixed bottom-6 right-6 z-[60] w-[92vw] max-w-[380px] h-[70vh] max-h-[600px] bg-white rounded-3xl shadow-2xl border border-[#dde5f0] flex flex-col overflow-hidden font-sans">
          <style dangerouslySetInnerHTML={{__html: `.bg-grad-gold{background:linear-gradient(120deg,#c9943a,#e8b55a);}`}} />
          {/* Header */}
          <div className="bg-[#16284B] text-white px-5 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="flex items-center justify-center w-10 h-10 bg-grad-gold rounded-full text-[#16284B]">
                <Sparkles size={20} />
              </span>
              <div>
                <p className="font-serif text-lg leading-none" style={{ fontFamily: "'Playfair Display', serif" }}>Ana</p>
                <p className="text-[11px] text-white/70 mt-1">Assistente da Priscila · online</p>
              </div>
            </div>
            <button onClick={() => setAberto(false)} className="text-white/70 hover:text-white transition-colors">
              <X size={20} />
            </button>
          </div>

          {/* Mensagens */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-[#FBFCFE]">
            {msgs.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
                  m.role === 'user'
                    ? 'bg-[#16284B] text-white rounded-br-sm'
                    : 'bg-[#f5f0e8] text-[#16284B] rounded-bl-sm'
                }`}>
                  {m.content}
                </div>
              </div>
            ))}
            {enviando && (
              <div className="flex justify-start">
                <div className="bg-[#f5f0e8] text-[#5d6b86] px-4 py-3 rounded-2xl rounded-bl-sm flex gap-1">
                  <span className="w-1.5 h-1.5 bg-[#c9943a] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-[#c9943a] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-[#c9943a] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            )}
            <div ref={fimRef} />
          </div>

          {/* Input */}
          <form onSubmit={enviar} className="border-t border-[#dde5f0] p-3 flex items-center gap-2 bg-white">
            <input
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder="Escreva sua mensagem..."
              className="flex-1 px-4 py-2.5 bg-[#f5f0e8] rounded-full text-sm text-[#16284B] placeholder-[#5d6b86]/70 focus:outline-none focus:ring-2 focus:ring-[#c9943a]/40"
            />
            <button
              type="submit"
              disabled={enviando || !texto.trim()}
              className="w-11 h-11 flex items-center justify-center bg-[#16284B] text-white rounded-full hover:bg-[#0f1c38] disabled:opacity-40 transition-all flex-shrink-0"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
