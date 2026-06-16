# 🔬 PESQUISA — Melhores skills/ferramentas de design no GitHub (deep-research, 16/06)

Deep-research verificada (105 agentes). O que dá pra aproveitar pra a skill de design + o site da Priscila.

## ⭐ Top recomendados (os que mais valem)
1. **Anthropic `frontend-design` plugin** — github.com/anthropics/claude-code/tree/main/plugins/frontend-design.
   Plugin OFICIAL de design pra Claude Code: usa **CSS variables + paleta de acento por cor dominante**. Estudar e
   espelhar os padrões dele na nossa `design-priscila`.
2. **Style Dictionary** — github.com/style-dictionary/style-dictionary (primary). Padrão de **design tokens → CSS
   variables** (e outras plataformas). Se um dia formalizarmos tokens em build, é a ferramenta.
3. **Adobe Leonardo** — github.com/adobe/leonardo. Gera **paletas por contraste** (acessibilidade APCA), DTCG→CSS, tem
   MCP server. Útil pra gerar as escalas de navy/dourado com contraste garantido. _(ressalva: nome exato da função npm refutado)_
4. **Radix Colors** — radix-ui.com/colors + /custom. **Escalas de cor de 12 passos** + gerador custom — modelo pra
   derivar navy/dourado consistentes. **uicolors.app/generate** é uma alternativa rápida (gera escala Tailwind de uma cor).
5. **awesome-design-md (VoltAgent)** — github.com/VoltAgent/awesome-design-md + awesome-claude-design (90k★). Codificam
   **design system como markdown legível por agente** — exatamente a abordagem da nossa skill (valida o que fizemos).

## 🧰 Outras úteis (por categoria)
- **Skills/plugins de design p/ IA:** rohitg00/awesome-claude-design, travisvn/awesome-claude-skills, wilwaldon/Claude-Code-Frontend-Design-Toolkit.
- **Tokens:** Terrazzo (terrazzo.app), Tokens Studio (tokens.studio); **DTCG** — spec W3C de design tokens chegou à **1ª versão estável (out/2025)**.
- **Design-to-code / UI gen (open-source):** abi/screenshot-to-code, tldraw/make-real, builder.io.
- **Templates imobiliários HTML/CSS:** M-YasirGhaffar/real-estate-static-website, davidfrear/Responsive-Website-RealEstate (+ `codewithsadee/homeverse` da pesquisa de arquitetura).
- **Boas práticas / checklists:** designsystemchecklist.com, alexpate/awesome-design-systems, klaufel/awesome-design-systems.

## 🎯 Recomendação pra nós (3 ações)
1. **Estudar o plugin `frontend-design` da Anthropic** e alinhar a `design-priscila` com os padrões dele (CSS vars + acento).
2. **Gerar as escalas navy/dourado** com Radix Colors custom ou uicolors.app (12 passos consistentes) e colocar no `tokens.css`.
3. **Usar `codewithsadee/homeverse`** como referência de estrutura HTML/CSS quando refatorar o site pro sistema.

_Caveat da pesquisa: alguns repos podem estar deprecados — validar atividade antes de adotar._
