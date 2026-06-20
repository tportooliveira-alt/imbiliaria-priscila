import React, { useState } from 'react';
import { Phone, Mail, ArrowRight, ShieldCheck, Home, CheckCircle2 } from 'lucide-react';

export default function Login({ onBack }) {
  const [loginMethod, setLoginMethod] = useState('whatsapp'); // 'whatsapp' ou 'email'
  const [step, setStep] = useState(1); // 1: Inserir dado, 2: Inserir código OTP

  return (
    <div className="min-h-screen bg-[#FBFCFE] text-[#16284B] font-sans flex flex-col md:flex-row selection:bg-[#c9943a] selection:text-white">
      {/* Importando Fontes */}
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Inter', sans-serif; }
      `}} />

      {/* LADO ESQUERDO - Imagem e Mensagem Acolhedora */}
      <div className="hidden md:flex w-1/2 bg-[#16284B] relative items-center justify-center p-12 overflow-hidden">
        {/* Imagem de Fundo (Mais acolhedora, pessoas reais ou casa convidativa) */}
        <div className="absolute inset-0">
          <img 
            src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1600" 
            alt="Cliente feliz com a chave" 
            className="w-full h-full object-cover opacity-30 mix-blend-overlay"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0f1c38] via-[#16284B]/80 to-transparent"></div>
        </div>

        <div className="relative z-10 max-w-lg text-white space-y-8">
          <div className="flex flex-col cursor-pointer" onClick={onBack}>
            <span className="font-serif font-bold tracking-widest text-3xl uppercase text-white hover:text-[#c9943a] transition-colors">
              PVSCELOS
            </span>
            <span className="text-xs tracking-[0.3em] uppercase text-[#c9943a] mt-1">
              Imobiliária
            </span>
          </div>

          <h1 className="font-serif text-4xl md:text-5xl font-light leading-tight">
            Encontre o lugar perfeito para a sua história.
          </h1>
          
          <div className="space-y-4 pt-6">
            <div className="flex items-center gap-4 text-[#7b95c8]">
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                <Home size={16} className="text-[#c9943a]" />
              </div>
              <p className="text-sm font-light">Do primeiro aluguel à casa dos sonhos em Vitória da Conquista.</p>
            </div>
            <div className="flex items-center gap-4 text-[#7b95c8]">
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                <CheckCircle2 size={16} className="text-[#c9943a]" />
              </div>
              <p className="text-sm font-light">Salve seus imóveis favoritos e acompanhe propostas.</p>
            </div>
            <div className="flex items-center gap-4 text-[#7b95c8]">
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                <ShieldCheck size={16} className="text-[#c9943a]" />
              </div>
              <p className="text-sm font-light">Acesso rápido e seguro aos seus documentos de locação ou compra.</p>
            </div>
          </div>
        </div>
      </div>

      {/* LADO DIREITO - Formulário de Login Limpo e Moderno */}
      <div className="w-full md:w-1/2 flex items-center justify-center p-6 md:p-12 relative bg-white">
        
        {/* Voltar para Home (Mobile) */}
        <div className="absolute top-6 left-6 md:hidden cursor-pointer" onClick={onBack}>
          <span className="font-serif font-bold tracking-widest text-xl uppercase text-[#16284B] hover:text-[#c9943a]">
            PVSCELOS
          </span>
        </div>

        <div className="w-full max-w-md space-y-8">
          
          <div className="text-center md:text-left">
            <h2 className="font-serif text-3xl text-[#16284B]">Acesse sua conta</h2>
            <p className="text-[#5d6b86] mt-2 font-light text-sm">
              A Área do Cliente está chegando 🔒 Por enquanto, fale direto com a Priscila pelo WhatsApp.
            </p>
          </div>

          {step === 1 ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Seletor de Método (Abas) */}
              <div className="flex p-1 bg-[#f5f0e8] rounded-xl">
                <button 
                  onClick={() => setLoginMethod('whatsapp')}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-medium transition-all ${loginMethod === 'whatsapp' ? 'bg-white text-[#16284B] shadow-sm' : 'text-[#5d6b86] hover:text-[#16284B]'}`}
                >
                  <Phone size={16} /> WhatsApp
                </button>
                <button 
                  onClick={() => setLoginMethod('email')}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-medium transition-all ${loginMethod === 'email' ? 'bg-white text-[#16284B] shadow-sm' : 'text-[#5d6b86] hover:text-[#16284B]'}`}
                >
                  <Mail size={16} /> E-mail
                </button>
              </div>

              {/* Input Dinâmico */}
              <div className="space-y-4">
                <label className="text-sm font-medium text-[#16284B] block">
                  {loginMethod === 'whatsapp' ? 'Qual é o seu WhatsApp?' : 'Qual é o seu E-mail?'}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    {loginMethod === 'whatsapp' ? <Phone size={18} className="text-[#c9943a]" /> : <Mail size={18} className="text-[#c9943a]" />}
                  </div>
                  <input 
                    type={loginMethod === 'whatsapp' ? 'tel' : 'email'} 
                    placeholder={loginMethod === 'whatsapp' ? '(77) 99999-9999' : 'seu@email.com'}
                    className="w-full pl-11 pr-4 py-4 bg-[#FBFCFE] border border-[#dde5f0] rounded-xl text-sm focus:outline-none focus:border-[#c9943a] focus:ring-1 focus:ring-[#c9943a]/20 transition-all"
                  />
                </div>
                
                <button 
                  onClick={() => window.open('https://wa.me/5577999395511', '_blank')}
                  className="w-full bg-[#16284B] text-white py-4 rounded-xl text-sm font-medium tracking-wide hover:bg-[#0f1c38] transition-colors flex items-center justify-center gap-2 mt-2"
                >
                  <Phone size={16} /> Em breve — falar no WhatsApp
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
              <div className="p-4 bg-[#f5f0e8] rounded-xl border border-[#dde5f0]">
                <p className="text-sm text-[#5d6b86] text-center">
                  Enviamos um código de 6 dígitos para o {loginMethod === 'whatsapp' ? 'WhatsApp' : 'e-mail'} <br/>
                  <strong className="text-[#16284B]">
                    {loginMethod === 'whatsapp' ? '(77) 99999-9999' : 'seu@email.com'}
                  </strong>
                </p>
                <button onClick={() => setStep(1)} className="text-xs text-[#c9943a] hover:underline block text-center mt-2 font-medium">
                  Corrigir informação
                </button>
              </div>

              <div className="space-y-4">
                <label className="text-sm font-medium text-[#16284B] block text-center">
                  Digite o código abaixo
                </label>
                <div className="flex justify-center gap-3">
                  {[1, 2, 3, 4, 5, 6].map((num) => (
                    <input 
                      key={num}
                      type="text" 
                      maxLength="1"
                      className="w-12 h-14 text-center text-xl font-serif border border-[#dde5f0] rounded-lg bg-[#FBFCFE] focus:outline-none focus:border-[#c9943a] focus:ring-1 focus:ring-[#c9943a]/20 transition-all"
                    />
                  ))}
                </div>
                
                <button className="w-full bg-[#c9943a] text-white py-4 rounded-xl text-sm font-medium tracking-wide hover:bg-[#e8b55a] transition-colors mt-6 shadow-lg shadow-[#c9943a]/20">
                  Acessar Minha Conta
                </button>

                <p className="text-center text-sm text-[#5d6b86] mt-4">
                  Não recebeu? <button className="text-[#16284B] font-medium hover:text-[#c9943a] transition-colors">Reenviar código</button>
                </p>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
