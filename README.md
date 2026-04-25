# Site Priscila Vasconcelos — Imóveis com IA

Site editorial + IA híbrida (Gemini + Claude) pra captação e qualificação de leads imobiliários em Vitória da Conquista — BA.

## Estrutura

```
site-imobiliaria/
├── v3-editorial/         # Site (HTML/CSS/JS estático)
│   ├── index.html        # Página principal
│   └── assets/
│       ├── abertura.mp4  # Vídeo de Priscila falando
│       ├── predios.mp4   # Vídeo dos prédios (abre primeiro)
│       ├── priscila-new-hero.jpeg
│       └── priscila-sobre.jpg
│
├── server.py             # (a ser adicionado) Backend Python com roteamento Gemini + Claude
├── .env.exemplo          # (a ser adicionado) Modelo de variáveis — copia pra .env
├── requirements.txt      # (a ser adicionado) Dependências Python
└── .gitignore            # Protege .env, chaves, node_modules, etc.
```

## Como rodar (local — em desenvolvimento)

Em construção. Próximo passo: adicionar `server.py` + `.env`.

## Stack planejada

| Camada | Tecnologia |
|---|---|
| Front | HTML/CSS/JS estático (já feito) |
| Backend | FastAPI (Python) |
| IA triagem | Gemini Flash |
| IA pesquisa BR | Gemini Pro + Search |
| IA negociação | Claude Sonnet 4.6 |
| IA follow-up | Claude Haiku 4.5 |
| WhatsApp | Meta Cloud API (oficial) |
| Hospedagem | VPS Hostinger |
| Domínio | priscilavasconcelos.com.br |

## Roadmap

- [x] Site editorial v3 funcional
- [x] Vídeos de abertura encadeados (prédios → Priscila)
- [ ] Backend `server.py` com roteamento IA
- [ ] Chat real plugado no `aic` do site
- [ ] 8–15 imóveis reais cadastrados
- [ ] WhatsApp Cloud API conectada
- [ ] Régua de follow-up no n8n
- [ ] Voice agent ElevenLabs PT-BR
- [ ] Likely-to-Sell BR (scraper + scorer)
- [ ] Mortgage IA (simulador Caixa)

## Segurança

- `.env` com chaves NUNCA é commitado (protegido pelo `.gitignore`)
- Chaves de API ficam só no PC local até subir pra VPS
