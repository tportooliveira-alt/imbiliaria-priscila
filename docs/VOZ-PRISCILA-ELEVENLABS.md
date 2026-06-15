# 🎙️ Criar a VOZ da Priscila no ElevenLabs

Objetivo: clonar a **voz real da Priscila** pra usar em **reels e áudios** do conteúdo (voz autêntica engaja muito mais).
Não confunde com a **Ana** (voz de atendimento) nem o **João** (voz de agenda) — esta é a voz da própria Priscila, pra conteúdo.

## ⚠️ Consentimento
A clonagem é da própria Priscila, com o consentimento DELA (o ElevenLabs pede marcar essa caixa). Só a voz dela. ✔️

## Passo 1 — Gravar uma amostra LIMPA
- **Ambiente silencioso** (sem TV, ventilador, eco). Celular serve, perto da boca, ou um microfone.
- Falar **no tom natural dela**: próxima, calma, didática — como ela fala com um cliente. Sem pressa, sem "ler robótico".
- **Duração:** ~**1 a 3 minutos** (clone instantâneo). Pra qualidade máxima (clone profissional), ~10-30 min.
- Grave em **um arquivo só** (mp3/wav/m4a).

### Roteiro pra ela ler (natural, variado — cobre bem os sons)
> "Oi! Eu sou a Priscila Vasconcelos, corretora de imóveis aqui em Vitória da Conquista, na Bahia.
> Trabalho com muito cuidado: pra mim, cada cliente é único, e meu objetivo é te dar clareza antes de qualquer decisão.
> Seja pra comprar a casa própria, vender seu imóvel ou só entender quanto ele vale hoje, eu te acompanho do começo ao fim.
> Conheço cada bairro da nossa cidade — Candeias, Recreio, Boa Vista — e explico cada passo: financiamento, documentação, negociação.
> Sem pressão e sem enrolação. Se fizer sentido pra você, a gente fecha; se não, eu falo com sinceridade.
> Por exemplo: um apartamento de dois ou três quartos, com garagem, numa boa localização, pode ser um ótimo negócio agora.
> Quer tirar uma dúvida ou agendar uma visita? Me chama no WhatsApp, vai ser um prazer te ajudar a realizar esse sonho."

(Pode falar mais coisas no fim, naturalmente, pra ter mais material — quanto mais áudio limpo, melhor a voz.)

## Passo 2 — Criar a voz no ElevenLabs
1. Entrar no **elevenlabs.io** (a conta que já usamos).
2. Ir em **Voices → Add a new voice → Instant Voice Clone** (ou *Professional Voice Clone* se for gravar 30 min).
3. Subir o áudio, **nome:** `Priscila Vasconcelos`, marcar o consentimento, criar.
4. Abrir a voz criada e **copiar o Voice ID** (string tipo `AbC123...`).

## Passo 3 — Me mandar o Voice ID
Cola o **Voice ID** aqui pra mim que eu adiciono no sistema (`ELEVENLABS_VOICE_ID_PRISCILA` no `.env`) — aí a rotina de
conteúdo passa a gerar **áudio/reel na voz dela**. (O Voice ID não é segredo crítico, mas fica no `.env`, fora do git.)

## Como vai ser usado
- Reels: roteiro curto no tom dela → áudio na voz dela → vídeo (Canva/Gamma) → **ela aprova** → publica.
- Stories em áudio, recados, "notícia do dia" narrada por ela — sem ela precisar gravar toda vez.
