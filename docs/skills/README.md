# 🧭 Skills do site Priscila Vasconcelos — índice

Documentação por área pra **achar e corrigir erro rápido**. Cada skill diz: o que faz, onde está o
código, como testar e os erros mais comuns + como resolver.

Projeto: **FastAPI + uvicorn** em `/var/www/imobiliaria`, no ar em **pvscelosimobiliaria.com**
(serviço systemd `imobiliaria` · porta 8001 · nginx na frente).

| Skill | Área | Arquivo |
|---|---|---|
| 🧮 Calculadora de Avaliação (AVM) | preço por bairro/m², calibrada com 1.016 anúncios | [SKILL-calculadora-avaliacao.md](SKILL-calculadora-avaliacao.md) |
| 🤖 Ana (IA de atendimento) | chat, contexto da carteira, voz/áudio | [SKILL-ana-ia.md](SKILL-ana-ia.md) |
| 🔧 Admin / Cadastro de imóvel | painel da Priscila (foto, descrição IA, preço) | [SKILL-admin-cadastro.md](SKILL-admin-cadastro.md) |
| 🖥️ Páginas do site | home, imóvel, anunciar, mercado + deploy | [SKILL-paginas-site.md](SKILL-paginas-site.md) |
| 🏦 Simulador de financiamento | parcela + comparação de bancos | [SKILL-simulador-financiamento.md](SKILL-simulador-financiamento.md) |
| 💰 Captação / CRM | lead vendedor, agenda, financeiro | [SKILL-captacao-crm.md](SKILL-captacao-crm.md) |

## Comandos rápidos (na raiz /var/www/imobiliaria)
```bash
systemctl restart imobiliaria          # reinicia o site (após mudar código .py)
systemctl status imobiliaria           # ver se está no ar
journalctl -u imobiliaria -n 50        # ver logs/erros
./venv/bin/python -c "import server"   # checar erro de sintaxe antes de reiniciar
python3 /root/treino/teste_calculadora.py   # validar a calculadora (24+ alvos)
```

## Regras de ouro
- **Nunca** commitar segredos (`.env`, `*.db`, chaves) — o `.gitignore` protege.
- **Nunca** push direto na `main` — usar branch.
- **Frontend:** edite `assets/preview.html` (dev) e **regenere** `v3-editorial/index.html` (ver SKILL-paginas-site).
- **Site em soft-launch:** `noindex` global no `server.py` (middleware). Remover pra lançar no Google.
