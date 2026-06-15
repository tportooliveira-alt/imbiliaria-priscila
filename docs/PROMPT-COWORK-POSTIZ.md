# 📋 Prompt pra colar no Cowork (instalar Postiz no PC do Thiago)

Copie TODO o bloco abaixo e cole no Cowork (o Claude do seu PC).

---

Quero instalar o **Postiz** (agendador de redes sociais, open-source) aqui no meu PC com Docker, pra rodar local.
Faça você os passos, conferindo cada um:

1. Verifique se o **Docker Desktop** está instalado e rodando (`docker --version` e `docker ps`).
   Se não estiver, me avise o link pra instalar e pare aqui.

2. Crie a pasta `C:\postiz` e dentro dela um arquivo `docker-compose.yml` com este conteúdo
   (gere você dois segredos aleatórios e substitua onde indico `<GERAR>`):

```yaml
services:
  postiz:
    image: ghcr.io/gitroomhq/postiz-app:latest
    container_name: postiz
    restart: always
    environment:
      MAIN_URL: "http://localhost:5000"
      FRONTEND_URL: "http://localhost:5000"
      NEXT_PUBLIC_BACKEND_URL: "http://localhost:5000/api"
      JWT_SECRET: "<GERAR-64-hex>"
      DATABASE_URL: "postgresql://postiz-user:<GERAR-senha>@postiz-postgres:5432/postiz-db-local"
      REDIS_URL: "redis://postiz-redis:6379"
      BACKEND_INTERNAL_URL: "http://localhost:3000"
      IS_GENERAL: "true"
      DISABLE_REGISTRATION: "false"
      STORAGE_PROVIDER: "local"
      UPLOAD_DIRECTORY: "/uploads"
      NEXT_PUBLIC_UPLOAD_DIRECTORY: "/uploads"
    volumes:
      - postiz-config:/config/
      - postiz-uploads:/uploads/
    ports:
      - "5000:5000"
    networks: [postiz-network]
    depends_on:
      postiz-postgres: { condition: service_healthy }
      postiz-redis: { condition: service_healthy }
  postiz-postgres:
    image: postgres:17-alpine
    container_name: postiz-postgres
    restart: always
    environment:
      POSTGRES_PASSWORD: "<GERAR-senha>"
      POSTGRES_USER: "postiz-user"
      POSTGRES_DB: "postiz-db-local"
    volumes: [postgres-volume:/var/lib/postgresql/data]
    networks: [postiz-network]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postiz-user -d postiz-db-local"]
      interval: 10s
      timeout: 3s
      retries: 5
  postiz-redis:
    image: redis:7.2-alpine
    container_name: postiz-redis
    restart: always
    volumes: [postiz-redis-data:/data]
    networks: [postiz-network]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
volumes:
  postgres-volume:
  postiz-redis-data:
  postiz-config:
  postiz-uploads:
networks:
  postiz-network:
```

   ⚠️ Os DOIS `<GERAR-senha>` (o do postiz e o do postgres) precisam ser **iguais**. Gere um valor só e use nos dois.

3. Dentro de `C:\postiz`, rode `docker compose up -d` e aguarde o download (a imagem do Postiz é grande).

4. Quando subir, abra **http://localhost:5000** no navegador, crie a conta (primeiro login = admin) e me confirme que entrou.

5. Me mostre `docker ps` pra confirmar os 3 containers (postiz, postiz-postgres, postiz-redis) rodando.

Observação: este Postiz é LOCAL (só funciona com o PC ligado). O Postiz "de produção" que agenda 24/7 fica na VPS.
Use este aqui pra TESTAR/criar posts; o da VPS é o que publica sozinho.
