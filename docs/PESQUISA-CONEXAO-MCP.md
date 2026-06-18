# 🔌 PESQUISA — Melhor forma de conectar o cowork (PC) ↔ MCP da VPS (deep-research, 18/06)

Resultado da pesquisa profunda (22 fontes oficiais: docs Anthropic, spec do MCP, FastMCP).
Responde os 2 problemas que a gente teve: (a) Basic Auth quebrou o conector; (b) sessão caiu no restart.

## ✅ Recomendação final
**Pro cowork no PC, use o Claude Code CLI (terminal) com token Bearer** — é o mais estável e seguro:
```
claude mcp add --transport http imobiliaria https://pvscelosimobiliaria.com/mcp-<token> \
  --header "Authorization: Bearer <SEU_TOKEN>"
```
- O **CLI suporta auth por header** (Bearer) E OAuth 2.1. HTTP "streamable" é o transporte recomendado.
- Fonte: code.claude.com/docs/en/mcp (primária).

## ⚠️ Por que a SENHA (Basic Auth) quebrou o conector do app
- O **conector personalizado do claude.ai (web/app) só aceita OAuth 2.1 ou sem-auth** — **não** aceita
  Basic Auth. Por isso deu "não foi possível registrar no serviço de login / adicione OAuth Client ID".
- A **spec do MCP exige OAuth 2.1** pra auth em HTTP (com Dynamic Client Registration).
- Fonte: claude.com/docs/connectors/building/authentication + modelcontextprotocol.io (primárias).
- **Conclusão:** no app web → só **sem-auth** (como está agora) OU implementar **OAuth 2.1** (trabalhoso).
  Com **senha**, só pelo **CLI** (Bearer header).

## ⚠️ Por que a sessão CAIU no restart (e o conserto)
- É comportamento da **spec**: ao reiniciar, a sessão antiga vira inválida (404 no próximo request) → o
  cliente fica com dados velhos até reconectar.
- **Conserto:** no FastMCP, ligar **`stateless_http=True`** → o servidor não guarda estado de sessão,
  então **sobrevive a restart** sem derrubar o cliente. (mexer em `app/mcp_server.py` no `mcp.run(...)`).
- Caveat: existe bug conhecido (claude-code #59467) por versão — **testar de verdade**, não confiar só no
  "Connected". Fonte: modelcontextprotocol.io/specification/.../transports (primária).

## 🅿️ SSH túnel — quando vale
- Reverse/forward SSH serve pra expor MCP local do PC pra VPS (o caso "VPS alcança o PC"), mas pro nosso
  caso (cowork→VPS) o **HTTP via nginx já resolve** — túnel só adiciona complexidade. Cloudflare Tunnel é
  alternativa se um dia não quisermos abrir porta/nginx.

## 👉 O que isso muda pra gente (proposta — confirmar antes)
1. **Manter sem-auth** (atual) pro app web funcionar — OK pra agora.
2. **Ligar `stateless_http=True`** no MCP → acaba a queda de sessão no restart (o problema que te irritou).
   Precisa de 1 restart pra aplicar (fazer quando o cowork não estiver no meio de algo).
3. Se um dia quiser **senha de verdade**: usar o **CLI com Bearer** (não o app web), ou montar OAuth 2.1.

> Fontes-chave (primárias): code.claude.com/docs/en/mcp · claude.com/docs/connectors/building/authentication
> · modelcontextprotocol.io/specification · gofastmcp.com/deployment/http
