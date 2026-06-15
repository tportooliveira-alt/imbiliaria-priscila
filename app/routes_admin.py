"""Rotas de autenticação e CRUD admin."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app import auth, imagens, imoveis

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=200, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    senha: str = Field(..., min_length=6, max_length=200)


class LoginResponse(BaseModel):
    token: str
    email: str
    role: str
    expires_in_hours: int


class ImovelPayload(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    bairro: str = Field(..., min_length=2, max_length=120)
    tipo: str = Field(..., max_length=40)
    quartos: int = 0
    suites: int = 0
    vagas: int = 0
    area_util: float = 0
    preco: float = Field(..., gt=0)
    descricao: str = ""
    caracteristicas: list[str] = Field(default_factory=list)
    destaque: bool = False
    ativo: bool = True
    tour_360_url: str | None = None


class ImovelUpdate(BaseModel):
    titulo: str | None = None
    bairro: str | None = None
    tipo: str | None = None
    quartos: int | None = None
    suites: int | None = None
    vagas: int | None = None
    area_util: float | None = None
    preco: float | None = None
    descricao: str | None = None
    caracteristicas: list[str] | None = None
    destaque: bool | None = None
    ativo: bool | None = None
    tour_360_url: str | None = None


class ReordemPayload(BaseModel):
    ordem: list[int]


# ─────────────────────────────────────────────────────────────────────────────
# Dependências
# ─────────────────────────────────────────────────────────────────────────────
def usuario_atual(cred: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not cred:
        raise HTTPException(status_code=401, detail="token ausente")
    payload = auth.decodar_token(cred.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="token invalido ou expirado")
    return payload


def requer_admin(user: dict = Depends(usuario_atual)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="acesso restrito a administrador")
    return user


def _ip_de(req: Request) -> str:
    if req.client:
        return req.client.host
    return "0.0.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request) -> LoginResponse:
    # ─── Modo dev local: DEV_OPEN_ADMIN=1 → entra com qualquer credencial ───
    # SEGURANÇA: bypass só é honrado se a requisição vier de localhost
    import os as _os
    _dev_origin = request.client.host if request.client else ""
    if _os.getenv("DEV_OPEN_ADMIN") == "1" and _dev_origin in ("127.0.0.1", "::1"):
        email = (payload.email or "dev@local").lower().strip()
        user = auth.buscar_usuario_por_email(email)
        if not user:
            auth.criar_usuario(email, payload.senha or "dev-open", role="admin")
            user = auth.buscar_usuario_por_email(email)
        token = auth.gerar_token(user["id"], user["email"], user["role"])
        return LoginResponse(
            token=token,
            email=user["email"],
            role=user["role"],
            expires_in_hours=auth.JWT_TTL_HOURS,
        )

    ip = _ip_de(request)
    auth.limpar_tentativas_antigas()
    if auth.excedeu_limite(ip):
        raise HTTPException(status_code=429, detail="muitas tentativas, aguarde 15 minutos")

    user = auth.autenticar(payload.email, payload.senha)
    auth.registrar_tentativa(ip)
    if not user:
        raise HTTPException(status_code=401, detail="email ou senha invalidos")

    token = auth.gerar_token(user["id"], user["email"], user["role"])
    return LoginResponse(
        token=token,
        email=user["email"],
        role=user["role"],
        expires_in_hours=auth.JWT_TTL_HOURS,
    )


@router.get("/api/auth/me")
def me(user: dict = Depends(usuario_atual)) -> dict:
    return {"email": user["email"], "role": user["role"]}


# ─────────────────────────────────────────────────────────────────────────────
# Imóveis (público)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/api/imoveis")
def listar(bairro: str | None = None) -> dict:
    items = imoveis.listar_imoveis(bairro=bairro)
    for it in items:
        it["imagens"] = imoveis.listar_imagens(it["id"])
    return {"total": len(items), "items": items}


@router.get("/api/imoveis/{slug}")
def detalhe(slug: str) -> dict:
    item = imoveis.buscar_por_slug(slug)
    if not item or not item.get("ativo"):
        raise HTTPException(status_code=404, detail="imovel nao encontrado")
    item["imagens"] = imoveis.listar_imagens(item["id"])
    return item


# ─────────────────────────────────────────────────────────────────────────────
# Imóveis (admin)
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/api/admin/imoveis", status_code=status.HTTP_201_CREATED)
def criar(body: ImovelPayload, _: dict = Depends(requer_admin)) -> dict:
    return imoveis.criar_imovel(body.model_dump())


@router.put("/api/admin/imoveis/{imovel_id}")
def atualizar(imovel_id: int, body: ImovelUpdate, _: dict = Depends(requer_admin)) -> dict:
    novo = imoveis.atualizar_imovel(
        imovel_id, {k: v for k, v in body.model_dump().items() if v is not None}
    )
    if not novo:
        raise HTTPException(status_code=404, detail="imovel nao encontrado")
    return novo


@router.delete("/api/admin/imoveis/{imovel_id}", status_code=204)
def remover(imovel_id: int, _: dict = Depends(requer_admin)) -> None:
    if not imoveis.desativar_imovel(imovel_id):
        raise HTTPException(status_code=404, detail="imovel nao encontrado")


# ─────────────────────────────────────────────────────────────────────────────
# Descrição editorial (B.3) — gera texto pronto via Claude
# ─────────────────────────────────────────────────────────────────────────────
class GerarDescricaoPayload(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    bairro: str = Field(..., min_length=2, max_length=120)
    tipo: str = Field(..., max_length=40)
    quartos: int = 0
    suites: int = 0
    vagas: int = 0
    area_util: float = 0
    preco: float = 0
    caracteristicas: list[str] = Field(default_factory=list)
    instrucao_extra: str | None = Field(None, max_length=400)


@router.post("/api/admin/imoveis/gerar-descricao")
def gerar_descricao(body: GerarDescricaoPayload, _: dict = Depends(requer_admin)) -> dict:
    from app.clients import ClienteClaude
    from app.prompts import Rota, system_prompt

    sistema = system_prompt(Rota.DESCRICAO)

    partes = [
        f"Tipo: {body.tipo}",
        f"Bairro: {body.bairro} (Vitoria da Conquista - BA)",
        f"Titulo de trabalho: {body.titulo}",
    ]
    if body.area_util:
        partes.append(f"Area util: {body.area_util:g} m²")
    ficha = []
    if body.quartos:
        ficha.append(f"{body.quartos} quartos")
    if body.suites:
        ficha.append(f"{body.suites} suites")
    if body.vagas:
        ficha.append(f"{body.vagas} vagas")
    if ficha:
        partes.append("Ficha: " + ", ".join(ficha))
    if body.preco:
        partes.append(f"Preco: R$ {body.preco:,.0f}".replace(",", "."))
    if body.caracteristicas:
        partes.append("Caracteristicas: " + ", ".join(body.caracteristicas))
    if body.instrucao_extra:
        partes.append("Instrucao adicional: " + body.instrucao_extra)

    mensagem = (
        "Gere a descricao editorial deste imovel agora. "
        "Entregue APENAS o texto pronto para o anuncio, sem titulos de secao, "
        "sem aspas externas, sem meta-comentarios.\n\n"
        + "\n".join(partes)
    )

    cli = ClienteClaude("claude-sonnet-4-5")
    if not cli.available():
        return {
            "texto": "",
            "fallback": True,
            "mensagem_fallback": "IA indisponivel (sem ANTHROPIC_API_KEY).",
        }
    resp = cli.gerar(sistema, mensagem)
    return {
        "texto": (resp.texto or "").strip(),
        "modelo": resp.modelo,
        "fallback": resp.fallback,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Imagens (admin)
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/api/admin/imoveis/{imovel_id}/imagens", status_code=201)
async def upload_imagens(
    imovel_id: int,
    files: list[UploadFile] = File(...),
    tipo: str = Form("sala"),
    _: dict = Depends(requer_admin),
) -> dict:
    imovel = imoveis.buscar_por_id(imovel_id)
    if not imovel:
        raise HTTPException(status_code=404, detail="imovel nao encontrado")
    if len(files) > 30:
        raise HTTPException(status_code=400, detail="maximo de 30 arquivos por upload")

    pasta_assets = Path(__file__).resolve().parent.parent / "assets"
    enviados: list[dict] = []

    for file in files:
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"tipo invalido: {file.content_type}")
        blob = await file.read()
        try:
            processada = imagens.processar_upload(
                blob, slug=imovel["slug"], pasta_destino=pasta_assets
            )
        except imagens.ImagemInvalida as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        registro = imoveis.adicionar_imagem(
            imovel_id, arquivo=processada.arquivo, tipo=tipo, legenda=""
        )
        enviados.append(registro)

    return {"total": len(enviados), "imagens": enviados}


@router.put("/api/admin/imoveis/{imovel_id}/imagens/ordem")
def reordenar(imovel_id: int, body: ReordemPayload, _: dict = Depends(requer_admin)) -> dict:
    imoveis.reordenar_imagens(imovel_id, body.ordem)
    return {"ok": True, "imagens": imoveis.listar_imagens(imovel_id)}


@router.post("/api/admin/imoveis/{imovel_id}/imagens/auto-organizar")
def auto_organizar_imagens(imovel_id: int, _: dict = Depends(requer_admin)) -> dict:
    """Studio (W3): classifica cada foto via Gemini Vision + ordena editorialmente.

    Sem GOOGLE_API_KEY, retorna `{fallback: True}` e nao altera nada.
    Erros de IA por imagem nao impedem o batch (mantem o tipo atual).
    """
    from app import visao

    imovel = imoveis.detalhe_por_id(imovel_id) if hasattr(imoveis, "detalhe_por_id") else None
    if imovel is None:
        # fallback: confirma existencia checando se ha imagens
        if not imoveis.listar_imagens(imovel_id):
            raise HTTPException(status_code=404, detail="imovel sem imagens ou inexistente")

    lista = imoveis.listar_imagens(imovel_id)
    if not lista:
        raise HTTPException(status_code=404, detail="nenhuma imagem para organizar")

    if not visao.disponivel():
        return {
            "fallback": True,
            "mensagem": "GOOGLE_API_KEY nao configurada; ordene manualmente.",
            "imagens": lista,
        }

    pasta_assets = Path(__file__).resolve().parent.parent / "assets"
    classificadas = 0
    ja_havia_capa = any(im.get("tipo") == "capa" for im in lista)

    for img in lista:
        # arquivo no DB e relativo a /assets, ex: "imoveis/slug/uuid"
        original = pasta_assets / img["arquivo"] / "original.jpg"
        if not original.exists():
            continue
        novo_tipo = visao.classificar_comodo(original)
        if not novo_tipo:
            continue
        # nao sobrescreve capa existente automaticamente (a primeira "capa"
        # detectada vira capa apenas se ainda nao existir uma)
        if novo_tipo == "capa" and ja_havia_capa:
            novo_tipo = "sala"
        try:
            imoveis.atualizar_imagem(int(img["id"]), tipo=novo_tipo)
            if novo_tipo == "capa":
                ja_havia_capa = True
            classificadas += 1
        except ValueError:
            continue

    # reordena editorialmente apos classificar
    atualizadas = imoveis.listar_imagens(imovel_id)
    nova_ordem = visao.ordenar_editorial(atualizadas)
    if nova_ordem:
        imoveis.reordenar_imagens(imovel_id, nova_ordem)

    return {
        "fallback": False,
        "classificadas": classificadas,
        "total": len(lista),
        "imagens": imoveis.listar_imagens(imovel_id),
    }


@router.delete("/api/admin/imagens/{imagem_id}", status_code=204)
def remover_imagem(imagem_id: int, _: dict = Depends(requer_admin)) -> None:
    if not imoveis.remover_imagem(imagem_id):
        raise HTTPException(status_code=404, detail="imagem nao encontrada")


class ImagemUpdate(BaseModel):
    tipo: str | None = None
    legenda: str | None = None


@router.patch("/api/admin/imagens/{imagem_id}")
def atualizar_imagem(imagem_id: int, body: ImagemUpdate, _: dict = Depends(requer_admin)) -> dict:
    try:
        out = imoveis.atualizar_imagem(imagem_id, tipo=body.tipo, legenda=body.legenda)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not out:
        raise HTTPException(status_code=404, detail="imagem nao encontrada")
    return out
