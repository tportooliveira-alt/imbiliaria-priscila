# MCP (SSE proxy) — imobiliária

Este pequeno serviço encaminha requisições do frontend/backend para um gateway de LLM
(ex.: Codex / OpenAI / outro proxy) e retransmite o stream de resposta para o cliente.

Instalação:

```bash
cd mcp
npm ci
cp .env.example .env
# editar .env: CODEX_API_URL, CODEX_API_KEY, CLIENT_TOKEN
npm start
```

Uso (exemplos):

POST streaming proxy:

```bash
curl -N -H "X-CLIENT-TOKEN: $TOKEN" -H "Content-Type: application/json" \
  -d '{"prompt":"Olá"}' "http://localhost:3001/mcp"
```

GET proxy (encaminha querystring):

```bash
curl -N -H "X-CLIENT-TOKEN: $TOKEN" "http://localhost:3001/mcp?stream=true&prompt=ola"
```

Segurança:

- Nunca comite chaves no repositório.
- `DEV_SKIP_AUTH=1` é apenas para desenvolvimento local — não usar em produção.
