"""
================================================================================
 MCP Server — Marketing Priscila Vasconcelos Imobiliária
================================================================================
 Roda como usuário 'priscila'. Fuso UTC-3. Secrets em .env (fora do git).
 NUNCA expor token ao LLM. Nenhuma mutação em produção sem confirmação.
 Versões: Meta Marketing API v24.0+ | Google Ads API v24.2

 ATENÇÃO: este arquivo é um ESQUELETO. Os pontos marcados com TODO precisam
 da lógica real de chamada de API, autenticação e tratamento de erro antes
 de ir a produção. Versões/datas foram levantadas via NotebookLM — confirme
 na doc oficial (developers.facebook.com / developers.google.com).
================================================================================
"""
import os, time, random, hashlib, logging
from datetime import datetime
from typing import Annotated, Optional
from zoneinfo import ZoneInfo
from pydantic import Field
from fastmcp import FastMCP

mcp = FastMCP(name="marketing-prisvasconcelos", mask_error_details=True)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mcp.priscila")
TZ = ZoneInfo("America/Bahia")  # UTC-3

# ---------- Injeção oculta de credenciais (LLM nunca vê) ----------
def _get_meta_client():
    return {"token": os.environ["META_ACCESS_TOKEN"],
            "ad_account": os.environ["META_AD_ACCOUNT_ID"]}

def _get_google_client():
    return {"dev_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
            "customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"]}

# ---------- Helpers ----------
def reais_from_micros(micros: int) -> float:
    return round(micros / 1_000_000, 2)

def reais_to_centavos(reais: float) -> int:
    return int(round(reais * 100))

def sha256_norm(valor: str, eh_email: bool = False) -> str:
    v = valor.strip().lower()
    if eh_email and "@" in v:
        local, dom = v.split("@", 1)
        if dom in ("gmail.com", "googlemail.com"):
            local = local.split("+")[0].replace(".", "")
        v = f"{local}@{dom}"
    return hashlib.sha256(v.encode()).hexdigest()

def conversion_date_time_agora() -> str:
    s = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S%z")
    return s[:-2] + ":" + s[-2:]   # yyyy-mm-dd HH:mm:ss-03:00

def _backoff_jitter(tentativa: int):
    espera = (2 ** tentativa) + random.uniform(0, 1)
    log.info(f"Backoff {espera:.2f}s (tentativa {tentativa}).")
    time.sleep(espera)

def _check_rate_limit(headers: dict):
    buc = headers.get("X-Business-Use-Case-Usage")
    if not buc:
        return
    uso = _maior_uso(buc)            # parse JSON do header
    if uso >= 80:
        log.warning(f"Rate limit {uso}%. Pausa preventiva.")
        time.sleep(300)             # Standard ~60s / Development ~300s

def _maior_uso(buc_header: str) -> int:
    return 0  # TODO: json.loads e max(total_cputime, total_time, call_count)

# ==============================================================================
#  FERRAMENTAS (9)
# ==============================================================================

@mcp.tool(readOnlyHint=False, destructiveHint=True)
def create_campaign(
    name: Annotated[str, Field(description="Nome da campanha", max_length=120)],
    objective: Annotated[str, Field(
        description="Objetivo: OUTCOME_ENGAGEMENT | OUTCOME_LEADS | OUTCOME_AWARENESS")],
) -> dict:
    """Cria campanha Meta SEMPRE PAUSED e com HOUSING. Pede confirmação p/ ativar."""
    payload = {"name": name, "objective": objective, "status": "PAUSED",
               "special_ad_categories": ["HOUSING"]}  # OBRIGATÓRIO
    # TODO: client = _get_meta_client(); POST /act_{id}/campaigns
    return {"status": "criada_pausada", "payload": payload}

@mcp.tool(readOnlyHint=False, destructiveHint=True)
def create_adset(
    name: Annotated[str, Field(max_length=120, description="Nome do Ad Set")],
    campaign_id: Annotated[str, Field(description="ID da campanha")],
    daily_budget_centavos: Annotated[int, Field(
        ge=1, description="Orçamento diário em CENTAVOS (R$50 = 5000)")],
    optimization_goal: Annotated[str, Field(
        description="CONVERSATIONS (WhatsApp) | LEAD_GENERATION | OFFSITE_CONVERSIONS")] = "CONVERSATIONS",
) -> dict:
    """Cria Ad Set. HOUSING trava idade/gênero, proíbe CEP, raio >=25km."""
    payload = {"name": name, "campaign_id": campaign_id,
               "daily_budget": daily_budget_centavos,
               "billing_event": "IMPRESSIONS",
               "optimization_goal": optimization_goal}
    # TODO: client = _get_meta_client(); POST /act_{id}/adsets (targeting HOUSING)
    return {"status": "criado", "payload": payload}

@mcp.tool(readOnlyHint=True, destructiveHint=False)
def generate_image(
    prompt: Annotated[str, Field(description="Prompt descritivo do criativo")],
) -> dict:
    """Claude = Diretor de Arte. Chama API de imagem (ex: DALL-E). Retorna URL."""
    # TODO: chamar API de geração de imagem e retornar a URL real
    return {"image_url": "https://.../gerada.png"}

@mcp.tool(readOnlyHint=False, destructiveHint=False)
def upload_image(
    image_url: Annotated[str, Field(description="URL da imagem a enviar")],
) -> dict:
    """POST /act_{id}/adimages → retorna image_hash p/ usar no creative."""
    # TODO: baixar a imagem e fazer POST em /act_{id}/adimages
    return {"image_hash": "<HASH>"}

@mcp.tool(readOnlyHint=False, destructiveHint=False)
def create_creative_carousel(
    name: Annotated[str, Field(max_length=120, description="Nome do criativo")],
    child_attachments: Annotated[list, Field(
        description="Lista de cartões: {link, image_hash, name, description}")],
) -> dict:
    """Cria creative de carrossel (object_story_spec.link_data.child_attachments)."""
    # TODO: montar object_story_spec e POST /act_{id}/adcreatives
    return {"status": "criado", "creative_id": "<ID>"}

@mcp.tool(readOnlyHint=False, destructiveHint=True)
def create_ad(
    name: Annotated[str, Field(max_length=120)],
    adset_id: Annotated[str, Field(description="ID do Ad Set")],
    creative_id: Annotated[str, Field(description="ID do creative")],
) -> dict:
    """Cria Ad SEMPRE PAUSED. Só ativa após confirmação da Priscila."""
    payload = {"name": name, "adset_id": adset_id,
               "creative": {"creative_id": creative_id}, "status": "PAUSED"}
    # TODO: client = _get_meta_client(); POST /act_{id}/ads
    return {"status": "criado_pausado", "payload": payload}

@mcp.tool(readOnlyHint=True, destructiveHint=False)
def get_insights(
    level: Annotated[str, Field(description="ad | adset | campaign")] = "ad",
    date_preset: Annotated[str, Field(description="ex: last_14d")] = "last_14d",
) -> dict:
    """Lê frequency/CTR p/ detecção de fadiga (freq>4 e CTR -20% WoW)."""
    # TODO: GET /insights com level e date_preset
    return {"insights": []}

@mcp.tool(readOnlyHint=False, destructiveHint=True)
def upload_conversion_google(
    gclid: Annotated[str, Field(description="GCLID capturado do clique")],
    value: Annotated[float, Field(ge=0, description="Valor = comissão (ex: 21000)")],
    order_id: Annotated[str, Field(description="ID único do lead (dedup)")],
) -> dict:
    """Envia conversão offline (Data Manager API). currency BRL, UTC-3."""
    conv = {"gclid": gclid,
            "conversion_value": value,
            "currency_code": "BRL",
            "order_id": order_id,                              # dedup
            "conversion_action": "UPLOAD_CLICKS",
            "conversion_date_time": conversion_date_time_agora()}
    # TODO: client = _get_google_client(); enviar via Data Manager API
    return {"status": "enviada", "conversion": conv}

@mcp.tool(readOnlyHint=True, destructiveHint=False)
def read_recommendations(
    customer_id: Annotated[str, Field(
        description="ID da conta Google (sem hífens). Vazio = conta padrão do .env")] = "",
) -> dict:
    """Lê recommendations de orçamento via GAQL. NUNCA aplica mutação sozinho —
    devolve as sugestões para confirmação humana antes de qualquer mudança."""
    tipos = ["CAMPAIGN_BUDGET", "MOVE_UNUSED_BUDGET",
             "MARGINAL_ROI_CAMPAIGN_BUDGET", "FORECASTING_CAMPAIGN_BUDGET"]
    # TODO: client = _get_google_client(); GAQL FROM recommendation WHERE type IN (...)
    return {"recommendations": [], "tipos_lidos": tipos,
            "aviso": "Aplicar mutação SOMENTE com confirmação da Priscila."}

# ==============================================================================
if __name__ == "__main__":
    mcp.run()
