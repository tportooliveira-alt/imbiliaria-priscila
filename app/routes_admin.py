"""Rotas de autenticação e CRUD admin."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app import auth, empreendimentos as emp, imagens, imoveis

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=200, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    senha: str = Field(..., min_length=6, max_length=200)


class LoginResponse(BaseModel):
    token: str | None = None
    email: str | None = None
    role: str | None = None
    expires_in_hours: int | None = None
    need_2fa: bool = False  # True quando falta o codigo por e-mail (1o login/aparelho novo)


class Verify2FARequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=200)
    codigo: str = Field(..., min_length=4, max_length=8)


class PasskeyFimRequest(BaseModel):
    credential: dict
    email: str | None = None
    apelido: str | None = None


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


class TipologiaPayload(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    area_util: float = 0
    quartos: int = 0
    suites: int = 0
    vagas: int = 0
    preco_a_partir: float = 0
    ordem: int = 0


class EmpreendimentoPayload(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    construtora: str = ""
    bairro: str = ""
    descricao: str = ""
    video_url: str | None = None
    status_obra: str = "na_planta"
    entrega_prevista: str = ""
    destaque: bool = False
    ativo: bool = True
    # ficha técnica (condomínio/obra grande)
    endereco: str = ""
    area_total: str = ""
    num_torres: int | None = None
    num_unidades: int | None = None
    num_andares: int | None = None
    vagas_info: str = ""
    data_lancamento: str = ""
    tour_360_url: str | None = None
    lazer: list[str] = Field(default_factory=list)
    diferenciais: list[str] = Field(default_factory=list)
    proximidades: str = ""
    condicoes_pagamento: str = ""
    tipologias: list[TipologiaPayload] = Field(default_factory=list)


class EmpreendimentoUpdate(BaseModel):
    nome: str | None = None
    construtora: str | None = None
    bairro: str | None = None
    descricao: str | None = None
    video_url: str | None = None
    status_obra: str | None = None
    entrega_prevista: str | None = None
    destaque: bool | None = None
    ativo: bool | None = None
    endereco: str | None = None
    area_total: str | None = None
    num_torres: int | None = None
    num_unidades: int | None = None
    num_andares: int | None = None
    vagas_info: str | None = None
    data_lancamento: str | None = None
    tour_360_url: str | None = None
    lazer: list[str] | None = None
    diferenciais: list[str] | None = None
    proximidades: str | None = None
    condicoes_pagamento: str | None = None
    tipologias: list[TipologiaPayload] | None = None


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

    # 2FA por e-mail (so se LIGADO + envio configurado): manda o codigo e ainda NAO da o token.
    if auth.dois_fatores_ativo():
        try:
            from app import email_util
            codigo = auth.gerar_codigo_2fa(user["email"])
            email_util.enviar_email(
                user["email"],
                "Seu codigo de acesso - Painel Priscila Vasconcelos",
                f"Seu codigo de acesso ao painel e: {codigo}\n\nVale por 10 minutos. "
                "Se nao foi voce, ignore este e-mail.",
            )
        except Exception:
            pass
        return LoginResponse(need_2fa=True, email=user["email"])

    token = auth.gerar_token(user["id"], user["email"], user["role"])
    return LoginResponse(
        token=token, email=user["email"], role=user["role"],
        expires_in_hours=auth.JWT_TTL_HOURS,
    )


@router.post("/api/auth/verify-2fa", response_model=LoginResponse)
def verify_2fa(payload: Verify2FARequest, request: Request) -> LoginResponse:
    """Confere o codigo enviado por e-mail e libera o token (1o login / aparelho novo)."""
    ip = _ip_de(request)
    if auth.excedeu_limite(ip):
        raise HTTPException(status_code=429, detail="muitas tentativas, aguarde 15 minutos")
    auth.registrar_tentativa(ip)
    if not auth.validar_codigo_2fa(payload.email, payload.codigo):
        raise HTTPException(status_code=401, detail="codigo invalido ou expirado")
    user = auth.buscar_usuario_por_email(payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="usuario nao encontrado")
    token = auth.gerar_token(user["id"], user["email"], user["role"])
    return LoginResponse(
        token=token, email=user["email"], role=user["role"],
        expires_in_hours=auth.JWT_TTL_HOURS,
    )


# ─── BIOMETRIA (passkey / digital / rosto) ───────────────────────────────────
@router.get("/api/auth/passkey/disponivel")
def passkey_disponivel(email: str) -> dict:
    """O navegador pergunta: esse e-mail ja tem biometria cadastrada? (mostra o botao)."""
    from app import passkey
    return {"tem_passkey": passkey.tem_passkey(email)}


@router.post("/api/auth/passkey/registrar/inicio")
def passkey_registrar_inicio(user: dict = Depends(usuario_atual)) -> dict:
    """Opcoes pra cadastrar a biometria DESTE aparelho (precisa estar logado)."""
    import json as _json
    from app import passkey
    return _json.loads(passkey.registro_inicio(user["id"], user["email"]))


@router.post("/api/auth/passkey/registrar/fim")
def passkey_registrar_fim(payload: PasskeyFimRequest, user: dict = Depends(usuario_atual)) -> dict:
    from app import passkey
    ok = passkey.registro_fim(user["id"], payload.credential, apelido=payload.apelido or "")
    if not ok:
        raise HTTPException(status_code=400, detail="nao foi possivel cadastrar a biometria")
    return {"ok": True}


@router.post("/api/auth/passkey/login/inicio")
def passkey_login_inicio(payload: dict | None = None) -> dict:
    """Opcoes pro navegador pedir a biometria (login)."""
    import json as _json
    from app import passkey
    email = (payload or {}).get("email")
    return _json.loads(passkey.login_inicio(email))


@router.post("/api/auth/passkey/login/fim", response_model=LoginResponse)
def passkey_login_fim(payload: PasskeyFimRequest, request: Request) -> LoginResponse:
    """Confere a biometria e libera o token."""
    from app import passkey
    user = passkey.login_fim(payload.credential, email=payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="biometria nao reconhecida")
    token = auth.gerar_token(user["id"], user["email"], user["role"])
    return LoginResponse(
        token=token, email=user["email"], role=user["role"],
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
# Empreendimentos (lançamentos de construtora) — público + admin
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/api/empreendimentos")
def listar_empreendimentos_pub() -> dict:
    items = emp.listar_empreendimentos()
    for it in items:
        it["tipologias"] = emp.listar_tipologias(it["id"])
        it["imagens"] = emp.listar_imagens(it["id"])
    return {"total": len(items), "items": items}


@router.get("/api/empreendimentos/{slug}")
def detalhe_empreendimento(slug: str) -> dict:
    item = emp.detalhar(slug)
    if not item or not item.get("ativo"):
        raise HTTPException(status_code=404, detail="empreendimento nao encontrado")
    return item


@router.post("/api/admin/empreendimentos", status_code=status.HTTP_201_CREATED)
def criar_empreendimento(body: EmpreendimentoPayload, _: dict = Depends(requer_admin)) -> dict:
    novo = emp.criar_empreendimento(body.model_dump())
    return emp.detalhar(novo["id"])


@router.put("/api/admin/empreendimentos/{emp_id}")
def atualizar_empreendimento(emp_id: int, body: EmpreendimentoUpdate, _: dict = Depends(requer_admin)) -> dict:
    dados = {k: v for k, v in body.model_dump().items() if v is not None}
    if not emp.atualizar_empreendimento(emp_id, dados):
        raise HTTPException(status_code=404, detail="empreendimento nao encontrado")
    return emp.detalhar(emp_id)


@router.delete("/api/admin/empreendimentos/{emp_id}", status_code=204)
def remover_empreendimento(emp_id: int, _: dict = Depends(requer_admin)) -> None:
    if not emp.desativar_empreendimento(emp_id):
        raise HTTPException(status_code=404, detail="empreendimento nao encontrado")


@router.post("/api/admin/empreendimentos/{emp_id}/imagens", status_code=201)
async def upload_imagens_empreendimento(
    emp_id: int,
    files: list[UploadFile] = File(...),
    tipo: str = Form("sala"),
    _: dict = Depends(requer_admin),
) -> dict:
    item = emp.buscar_por_id(emp_id)
    if not item:
        raise HTTPException(status_code=404, detail="empreendimento nao encontrado")
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
                blob, slug=item["slug"], pasta_destino=pasta_assets, subpasta="empreendimentos"
            )
        except imagens.ImagemInvalida as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        registro = emp.adicionar_imagem(emp_id, arquivo=processada.arquivo, tipo=tipo, legenda="")
        enviados.append(registro)
    return {"total": len(enviados), "imagens": enviados}


@router.delete("/api/admin/empreendimentos/imagens/{imagem_id}", status_code=204)
def remover_imagem_empreendimento(imagem_id: int, _: dict = Depends(requer_admin)) -> None:
    if not emp.remover_imagem(imagem_id):
        raise HTTPException(status_code=404, detail="imagem nao encontrada")


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

    imovel = imoveis.buscar_por_id(imovel_id)
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
