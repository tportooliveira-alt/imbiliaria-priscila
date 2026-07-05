# Criativos — Registro e Carrossel

## Geração de imagem COM o Claude (via MCP)
Claude NÃO gera imagem nativamente. O MCP acopla ferramenta de geração.
Fluxo: Claude lê imóvel no CRM → cria prompt (Diretor de Arte) →
generate_image → upload_image (POST /act_{id}/adimages) → recebe image_hash.
> NUNCA simular imóvel inexistente. Geração só p/ peças genéricas.

## Creative de CARROSSEL (object_story_spec)
POST /act_{ad_account_id}/adcreatives
```json
{
  "name": "Carrossel_Imovel_01",
  "object_story_spec": {
    "page_id": "",
    "instagram_actor_id": "",
    "link_data": {
      "message": "Conheça este imóvel. Fale com a Priscila Vasconcelos.",
      "link": "https://site.com.br/imovel-x",
      "caption": "www.site.com.br",
      "child_attachments": [
        {"link":"https://site.com.br/imovel-x","image_hash":"",
         "name":"Fachada","description":"3 quartos · 120m²"},
        {"link":"https://site.com.br/imovel-x/contato","image_hash":"",
         "name":"Área de lazer","description":"Quintal e churrasqueira"}
      ]
    }
  }
}
```
> Termo CORRETO é `child_attachments` (não "child_attributes").
> Cada cartão tem seu image_hash. Link pode ser geral ou por cartão.

## Tabela de registro/rotação
| id | adset_id | creative_id | tipo | image_hash | data | status | frequency | ctr_inicial | ctr_atual |
|----|----------|-------------|------|------------|------|--------|-----------|-------------|-----------|

## Regras
- 2-3 criativos ativos por Ad Set · Ad novo PAUSED ·
  nunca pausar o último sem substituto pronto.
