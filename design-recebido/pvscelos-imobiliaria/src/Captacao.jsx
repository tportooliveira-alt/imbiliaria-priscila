import React, { useState } from 'react';
import { Camera, Coffee, Handshake, ArrowRight, MapPin, Home, ShieldCheck, Sparkles, CheckCircle2 } from 'lucide-react';
import { enviarLeadVendedor, trackLead } from './api';

export default function Captacao({ onBack }) {
  const [intent, setIntent] = useState('vender'); // 'vender' ou 'alugar'
  const [nome, setNome] = useState('');
  const [whatsapp, setWhatsapp] = useState('');
  const [bairro, setBairro] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [erro, setErro] = useState('');

  async function enviar() {
    setErro('');
    if (nome.trim().length < 2 || whatsapp.replace(/\D/g, '').length < 10) {
      setErro('Preencha seu nome e um WhatsApp válido (com DDD).');
      return;
    }
    setEnviando(true);
    try {
      await enviarLeadVendedor({
        nome: nome.trim(),
        telefone: whatsapp.replace(/\D/g, ''),
        bairro: bairro.trim(),
        observacoes: `Quer ${intent} o imóvel (via site).`,
      });
      setEnviado(true);
      trackLead('anunciar');
    } catch {
      setErro('Não consegui enviar agora. Tenta de novo, ou chama a Ana aqui no chat.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#FBFCFE] text-[#16284B] font-sans antialiased selection:bg-[#c9943a] selection:text-white">
      {/* Importando Fontes */}
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Inter', sans-serif; }
      `}} />

      {/* Navegação Simplificada */}
      <nav className="absolute w-full z-50 py-6">
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center text-[#16284B]">
          <img
            src={`${import.meta.env.BASE_URL}selo.png`}
            alt="Priscila Vasconcelos Imobiliária"
            onClick={onBack}
            className="h-16 md:h-20 object-contain opacity-90 cursor-pointer"
          />
          <button onClick={onBack} className="text-sm font-medium hover:text-[#c9943a] transition-colors">
            Voltar ao Início
          </button>
        </div>
      </nav>

      <main>
        {/* Seção Principal (Hero) com Formulário */}
        <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 px-6 overflow-hidden">
          {/* Fundo Decorativo */}
          <div className="absolute top-0 right-0 w-full lg:w-1/2 h-full bg-[#f5f0e8] rounded-bl-[100px] -z-10"></div>
          
          <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-16">
            
            {/* Textos - Lado Esquerdo */}
            <div className="w-full lg:w-1/2 space-y-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#f5f0e8] border border-[#c9943a]/20 text-[#c9943a] text-xs font-bold uppercase tracking-widest">
                <Sparkles size={14} /> Avaliação Gratuita
              </div>
              
              <h1 className="font-serif text-4xl md:text-6xl text-[#16284B] leading-tight">
                Venda ou alugue seu imóvel <br/>
                <span className="italic text-[#c9943a]">sem dor de cabeça.</span>
              </h1>
              
              <p className="text-lg text-[#5d6b86] font-light leading-relaxed max-w-lg">
                Você não precisa se preocupar em tirar fotos boas ou saber o preço exato do mercado. 
                Nós vamos até você, avaliamos seu patrimônio pessoalmente e cuidamos de todo o processo de divulgação.
              </p>

              <div className="flex flex-col sm:flex-row gap-8 pt-4">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-[#16284B]/5 flex items-center justify-center flex-shrink-0 text-[#c9943a]">
                    <ShieldCheck size={20} />
                  </div>
                  <div>
                    <h4 className="font-medium text-[#16284B]">Segurança Jurídica</h4>
                    <p className="text-sm text-[#5d6b86] mt-1">Análise de docs inclusa.</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-[#16284B]/5 flex items-center justify-center flex-shrink-0 text-[#c9943a]">
                    <Home size={20} />
                  </div>
                  <div>
                    <h4 className="font-medium text-[#16284B]">Venda Mais Rápida</h4>
                    <p className="text-sm text-[#5d6b86] mt-1">Exposição nos melhores portais.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Formulário - Lado Direito */}
            <div className="w-full lg:w-[450px] bg-white p-8 md:p-10 rounded-3xl border border-[#dde5f0] shadow-[0_8px_30px_rgb(0,0,0,0.04)] relative z-10">
              <h3 className="font-serif text-2xl text-[#16284B] mb-2">Agendar Visita Técnica</h3>
              <p className="text-sm text-[#5d6b86] mb-8 font-light">
                Preencha os dados abaixo. Priscila entrará em contato para agendar um café no seu imóvel.
              </p>

              <div className="space-y-5">
                {/* Seleção Vender/Alugar */}
                <div className="flex p-1 bg-[#f5f0e8] rounded-xl mb-6">
                  <button 
                    onClick={() => setIntent('vender')}
                    className={`flex-1 py-3 rounded-lg text-sm font-medium transition-all ${intent === 'vender' ? 'bg-white text-[#16284B] shadow-sm' : 'text-[#5d6b86] hover:text-[#16284B]'}`}
                  >
                    Quero Vender
                  </button>
                  <button 
                    onClick={() => setIntent('alugar')}
                    className={`flex-1 py-3 rounded-lg text-sm font-medium transition-all ${intent === 'alugar' ? 'bg-white text-[#16284B] shadow-sm' : 'text-[#5d6b86] hover:text-[#16284B]'}`}
                  >
                    Quero Alugar
                  </button>
                </div>

                <div>
                  <label className="text-xs uppercase tracking-widest font-semibold text-[#5d6b86] block mb-2">Seu Nome</label>
                  <input value={nome} onChange={(e) => setNome(e.target.value)} type="text" placeholder="Como gosta de ser chamado?" className="w-full px-4 py-3 bg-[#FBFCFE] border border-[#dde5f0] rounded-xl text-sm focus:outline-none focus:border-[#c9943a] transition-all" />
                </div>
                
                <div>
                  <label className="text-xs uppercase tracking-widest font-semibold text-[#5d6b86] block mb-2">WhatsApp</label>
                  <input value={whatsapp} onChange={(e) => setWhatsapp(e.target.value)} type="tel" placeholder="(77) 99999-9999" className="w-full px-4 py-3 bg-[#FBFCFE] border border-[#dde5f0] rounded-xl text-sm focus:outline-none focus:border-[#c9943a] transition-all" />
                </div>

                <div>
                  <label className="text-xs uppercase tracking-widest font-semibold text-[#5d6b86] block mb-2">Bairro do Imóvel</label>
                  <div className="relative">
                    <MapPin size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#c9943a]" />
                    <input value={bairro} onChange={(e) => setBairro(e.target.value)} type="text" placeholder="Ex: Candeias, Boa Vista..." className="w-full pl-11 pr-4 py-3 bg-[#FBFCFE] border border-[#dde5f0] rounded-xl text-sm focus:outline-none focus:border-[#c9943a] transition-all" />
                  </div>
                </div>

                {erro && <p className="text-sm text-red-500 -mt-2">{erro}</p>}
                {enviado ? (
                  <div className="bg-[#f5f0e8] border border-[#c9943a]/30 rounded-xl p-5 text-center mt-2">
                    <CheckCircle2 size={28} className="text-[#c9943a] mx-auto mb-2" />
                    <p className="text-[#16284B] font-medium">Recebido! 🎉</p>
                    <p className="text-sm text-[#5d6b86] mt-1">A Priscila vai te chamar no WhatsApp pra agendar a visita técnica.</p>
                  </div>
                ) : (
                  <button
                    onClick={enviar}
                    disabled={enviando}
                    className="w-full bg-[#16284B] text-white py-4 rounded-xl text-sm font-medium tracking-wide hover:bg-[#0f1c38] transition-colors flex items-center justify-center gap-2 mt-4 group disabled:opacity-50"
                  >
                    {enviando ? 'Enviando...' : <>Solicitar Contato <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" /></>}
                  </button>
                )}
              </div>
            </div>

          </div>
        </section>

        {/* Como Funciona - O Diferencial Priscila Vasconcelos */}
        <section className="py-24 bg-[#16284B] text-white">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="font-serif text-3xl md:text-4xl mb-4">Como funciona a nossa parceria?</h2>
              <p className="text-[#7b95c8] font-light max-w-2xl mx-auto">
                Esqueça a burocracia das imobiliárias tradicionais. Nosso processo é humano, prático e focado em valorizar o seu bem.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
              {/* Linha conectando os passos (Desktop) */}
              <div className="hidden md:block absolute top-12 left-[15%] right-[15%] h-px bg-[#c9943a]/30"></div>

              {/* Passo 1 */}
              <div className="relative text-center space-y-4">
                <div className="w-24 h-24 mx-auto bg-[#0f1c38] rounded-full border border-[#c9943a] flex items-center justify-center relative z-10 shadow-[0_0_30px_rgba(201,148,58,0.15)]">
                  <Coffee size={32} className="text-[#c9943a]" />
                </div>
                <h3 className="font-serif text-xl">1. A Visita Técnica</h3>
                <p className="text-[#7b95c8] text-sm font-light leading-relaxed px-4">
                  Priscila vai pessoalmente ao imóvel tomar um café com você, entender a história da casa e fazer a avaliação correta de mercado baseada em dados de Vitória da Conquista.
                </p>
              </div>

              {/* Passo 2 */}
              <div className="relative text-center space-y-4">
                <div className="w-24 h-24 mx-auto bg-[#0f1c38] rounded-full border border-[#c9943a] flex items-center justify-center relative z-10 shadow-[0_0_30px_rgba(201,148,58,0.15)]">
                  <Camera size={32} className="text-[#c9943a]" />
                </div>
                <h3 className="font-serif text-xl">2. Produção Visual</h3>
                <p className="text-[#7b95c8] text-sm font-light leading-relaxed px-4">
                  Uma imagem vale mais que mil palavras. Nós providenciamos fotos profissionais e vídeos que destacam o melhor do seu imóvel, sem que você precise se preocupar com nada.
                </p>
              </div>

              {/* Passo 3 */}
              <div className="relative text-center space-y-4">
                <div className="w-24 h-24 mx-auto bg-[#0f1c38] rounded-full border border-[#c9943a] flex items-center justify-center relative z-10 shadow-[0_0_30px_rgba(201,148,58,0.15)]">
                  <Handshake size={32} className="text-[#c9943a]" />
                </div>
                <h3 className="font-serif text-xl">3. Marketing e Fechamento</h3>
                <p className="text-[#7b95c8] text-sm font-light leading-relaxed px-4">
                  Seu imóvel entra no nosso portfólio e nas nossas campanhas de marketing inteligente. Encontramos o cliente ideal, cuidamos da papelada e finalizamos a negociação.
                </p>
              </div>

            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
