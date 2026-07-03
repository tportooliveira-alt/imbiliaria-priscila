import React, { useState, useEffect } from 'react';
import { ArrowRight, Award, Shield, Target, BookOpen } from 'lucide-react';

export default function Sobre({ onBack }) {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#FBFCFE] text-[#16284B] font-sans antialiased selection:bg-[#c9943a] selection:text-white">
      {/* Importando Fontes */}
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Inter', sans-serif; }
      `}} />

      {/* Navegação */}
      <nav className={`fixed w-full z-50 transition-all duration-500 ${isScrolled ? 'bg-white/95 backdrop-blur-md border-b border-[#dde5f0] py-4' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          <img
            src={`${import.meta.env.BASE_URL}selo.png`}
            alt="Priscila Vasconcelos Imobiliária"
            onClick={onBack}
            className="h-16 md:h-20 object-contain opacity-90 cursor-pointer"
          />
          <button onClick={onBack} className={`text-sm tracking-wide transition-colors ${isScrolled ? 'text-[#16284B] hover:text-[#c9943a]' : 'text-[#16284B] hover:text-[#c9943a]'}`}>
            Voltar ao Início
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 px-6 overflow-hidden">
        <div className="absolute top-0 right-0 w-full lg:w-2/3 h-full bg-[#EEF2F8] rounded-bl-[120px] -z-10"></div>
        
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-16">
          <div className="w-full lg:w-1/2 space-y-8 relative z-10">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-[#dde5f0] text-[#16284B] text-xs font-bold uppercase tracking-widest shadow-sm">
              <Award size={14} className="text-[#c9943a]" /> Nossa Essência
            </div>
            
            <h1 className="font-serif text-5xl md:text-7xl text-[#16284B] leading-tight">
              Mais que imóveis, <br/>
              <span className="italic text-[#c9943a]">histórias reais.</span>
            </h1>
            
            <p className="text-lg text-[#5d6b86] font-light leading-relaxed max-w-lg">
              Filha de corretor, Priscila Vasconcelos cresceu dentro do mercado imobiliário — e fez dele a sua vida. Ela transforma cada compra, venda ou aluguel numa experiência humana, transparente e segura, em Vitória da Conquista.
            </p>
          </div>

          {/* Imagem da Fundadora / Marca */}
          <div className="w-full lg:w-1/2 relative">
            <div className="absolute inset-0 bg-[#c9943a] rounded-[2rem] translate-x-6 translate-y-6 opacity-20"></div>
            <img
              src={`${import.meta.env.BASE_URL}priscila-sobre.jpg`}
              alt="Priscila Vasconcelos e seu pai, o corretor Pedro Ronaldo Vasconcelos"
              className="relative z-10 rounded-[2rem] shadow-2xl object-cover object-center w-full aspect-[4/3]"
            />
          </div>
        </div>
      </header>

      {/* A História de Priscila */}
      <section className="py-20 lg:py-28 px-6">
        <div className="max-w-3xl mx-auto">
          <span className="text-[#c9943a] tracking-widest text-xs uppercase font-semibold mb-3 block">Minha história</span>
          <h2 className="font-serif text-3xl md:text-4xl text-[#16284B] mb-6 leading-tight">
            O legado e a paixão pelo <span className="italic text-[#c9943a]">mercado imobiliário</span>
          </h2>
          <div className="space-y-6 text-lg text-[#5d6b86] font-light leading-relaxed">
            <p>
              No mercado imobiliário, a confiança não se constrói apenas com contratos; ela se constrói com tempo, vivência e valores passados de geração em geração. A minha trajetória é, essencialmente, a história de uma vida dedicada à credibilidade.
            </p>

            <h3 className="font-serif text-2xl text-[#16284B] pt-4">De pai para filha: uma vida alicerçada na confiança</h3>
            <p>
              Sou filha de um homem que dedicou sua carreira à arte de encontrar lares e oportunidades: <strong className="font-medium text-[#16284B]">Pedro Ronaldo Vasconcelos</strong>. Como corretor com mais de 15 anos de atuação, meu pai não apenas me ensinou a profissão; ele me mostrou, na prática, o valor de um compromisso honrado.
            </p>
            <p>
              Minhas primeiras lembranças no mercado são das tardes em que eu o acompanhava em visitas aos imóveis. Enquanto ele examinava cada detalhe com um olhar atento, eu absorvia a ética e o cuidado com que tratava cada pessoa. Todo esse aprendizado foi o alicerce sobre o qual construí a minha própria identidade profissional. Ao longo do caminho, tive o privilégio de conviver e aprender com <strong className="font-medium text-[#16284B]">grandes líderes do ramo imobiliário</strong> — experiências pelas quais sou profundamente grata e que moldaram a minha forma de atuar com excelência.
            </p>

            <h3 className="font-serif text-2xl text-[#16284B] pt-4">Meu foco: o cliente no centro de tudo</h3>
            <p>
              Mais do que mediar transações, a minha missão é ser uma facilitadora na jornada dos meus clientes. Entendo que, por trás de cada negociação — seja ela de <strong className="font-medium text-[#16284B]">compra, venda, aluguel</strong> ou uma avaliação estratégica de imóvel — existem sonhos, investimentos e expectativas que precisam ser respeitados.
            </p>
            <p>
              O meu foco é proporcionar uma experiência clara, segura e eficiente. Acredito que o mercado imobiliário, quando conduzido com profissionalismo e transparência, torna-se a base para grandes transformações na vida das pessoas.
            </p>
            <p>
              É com essa bagagem — herdada e fortalecida pelos ensinamentos de grandes referências do setor e pelo meu compromisso pessoal — que coloco todo o meu empenho a serviço de <strong className="font-medium text-[#16284B]">cada cliente que confia no meu trabalho.</strong>
            </p>

            {/* Assinatura — fecha a história com cara de carta pessoal */}
            <div className="pt-6 flex items-center gap-4">
              <span className="h-px w-12 bg-[#c9943a]"></span>
              <div>
                <p className="font-serif text-2xl text-[#16284B] italic leading-none">Priscila Vasconcelos</p>
                <p className="text-xs uppercase tracking-widest text-[#5d6b86] mt-1.5">Corretora de Imóveis · CRECI/BA 29.231</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Seção Pilares */}
      <section className="py-24 bg-[#16284B] text-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <span className="text-[#c9943a] tracking-widest text-xs uppercase font-semibold mb-3 block">No que Acreditamos</span>
            <h2 className="text-3xl md:text-5xl font-serif">Os Pilares da Priscila Vasconcelos</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="space-y-6 p-8 rounded-3xl bg-[#0f1c38] border border-white/5 hover:border-[#c9943a]/50 transition-colors">
              <Shield size={40} className="text-[#c9943a]" />
              <h3 className="font-serif text-2xl">Segurança Absoluta</h3>
              <p className="text-[#7b95c8] font-light leading-relaxed">
                Cada contrato, certidão e documentação passa por um rigoroso crivo jurídico. Garantimos que sua transação ocorra sem sobressaltos, protegendo o seu patrimônio do início ao fim.
              </p>
            </div>

            <div className="space-y-6 p-8 rounded-3xl bg-[#0f1c38] border border-white/5 hover:border-[#c9943a]/50 transition-colors">
              <BookOpen size={40} className="text-[#c9943a]" />
              <h3 className="font-serif text-2xl">Transparência</h3>
              <p className="text-[#7b95c8] font-light leading-relaxed">
                Sem asteriscos ou meias-verdades. Entregamos a real avaliação do mercado e mantemos você informado em cada etapa do processo de locação ou venda.
              </p>
            </div>

            <div className="space-y-6 p-8 rounded-3xl bg-[#0f1c38] border border-white/5 hover:border-[#c9943a]/50 transition-colors">
              <Target size={40} className="text-[#c9943a]" />
              <h3 className="font-serif text-2xl">Foco no Cliente</h3>
              <p className="text-[#7b95c8] font-light leading-relaxed">
                Nós não vendemos tijolos, conectamos pessoas aos seus sonhos. Desde o café da primeira visita até a entrega das chaves, o centro da nossa operação é você.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Seção CTA Final */}
      <section className="py-24 bg-[#FBFCFE]">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="font-serif text-3xl md:text-5xl text-[#16284B] mb-8">
            Faça parte dessa <span className="italic text-[#c9943a]">história.</span>
          </h2>
          <p className="text-lg text-[#5d6b86] font-light mb-10 leading-relaxed">
            Seja para encontrar o primeiro aluguel, comprar a casa dos sonhos, investir no próximo grande empreendimento ou vender o seu patrimônio com a dignidade que ele merece. Nós estamos prontos.
          </p>
          <button onClick={onBack} className="bg-[#16284B] text-white px-8 py-4 rounded-full text-sm font-bold uppercase tracking-widest hover:bg-[#c9943a] transition-colors inline-flex items-center gap-3">
            Explorar Catálogo <ArrowRight size={18} />
          </button>
        </div>
      </section>
    </div>
  );
}
