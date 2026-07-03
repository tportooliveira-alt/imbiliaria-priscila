# PVSCELOS Imobiliária — front (site novo)

Site da **Priscila Vasconcelos Imobiliária** (alto padrão, Vitória da Conquista/BA). Redesign que vai substituir o front atual **quando estiver funcional** — até lá, produção fica intocada.

## Stack
React 19 · Vite 8 · Tailwind 4 (`@tailwindcss/vite`) · lucide-react. Dev: `npm run dev` (localhost:5173).

## Paleta da marca (respeitar — NÃO trocar)
navy `#16284B` · navy-2 `#0f1c38` · periwinkle `#5C7CB8`/`#7b95c8` · dourado `#c9943a`/`#e8b55a` · areia `#f5f0e8` · bg `#FBFCFE` · texto `#16284B`, suave `#5d6b86` · linha `#dde5f0`. Fontes: Playfair Display (títulos) + Inter (corpo).

## Estado atual (2026-06-18)
Casca visual pronta, mas **mock/desconectada**: navegação por useState em `App.jsx` (sem router, URL `/#`), imóveis e fotos são Unsplash hardcoded (`Home.jsx:8`), form de captação (`Captacao.jsx:117`) e login OTP (`Login.jsx:120`) sem backend.

## Roadmap "ficar real" (sem Next, sem Supabase — Vite + react-router + API do backend Python existente)
1. Camada de API → imóveis reais + as 1076 fotos (substituir mock).
2. Form captação → grava lead → scoring → ponte Paperclip (já existe na VPS).
3. Router real (URL por imóvel: SEO + compartilhar no WhatsApp).
4. OTP real (Área do Cliente).

## ⚠️ Cuidados
- **Ponte Paperclip está VIVA** na produção: testar captação pode jogar lead fake no painel real da Priscila. Usar flag de ambiente (só PROD escala pro Paperclip).
- Backend (Python/SQLite + ponte Paperclip) **não se toca** neste repo — é outro sistema, na VPS.

## Disciplina
Mudança cirúrgica; casar com o estilo existente; simplicidade primeiro (ver `/karpathy`). Dívidas conhecidas a tratar quando fizer sentido: fontes via `@import` repetidas por página; cores hex inline (centralizar em token Tailwind).
