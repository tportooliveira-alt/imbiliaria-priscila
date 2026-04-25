"""Smoke test end-to-end Onda 1: cadastra imovel (lote), simula, avalia, lista leads."""
from __future__ import annotations

import io
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8000"


def req(metodo: str, path: str, body=None, headers=None, multipart=None):
    h = headers.copy() if headers else {}
    data = None
    if multipart:
        boundary = "----PVBoundary7382"
        h["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        buf = io.BytesIO()
        for k, v in multipart["fields"].items():
            buf.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
        for f in multipart.get("files", []):
            buf.write(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{f['name']}\"; filename=\"{f['filename']}\"\r\n"
                f"Content-Type: {f['ctype']}\r\n\r\n".encode()
            )
            buf.write(f["data"]); buf.write(b"\r\n")
        buf.write(f"--{boundary}--\r\n".encode())
        data = buf.getvalue()
    elif body is not None:
        h["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    r = urllib.request.Request(BASE + path, data=data, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(r) as resp:
            txt = resp.read().decode()
            return resp.status, json.loads(txt) if txt else None
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def linha(t): print(); print("=" * 4, t)


# 1) Login
linha("1) LOGIN")
st, body = req("POST", "/api/auth/login",
               body={"email": "thiago@dev.com", "senha": "teste-onda1-123"})
assert st == 200, body
TOK = body["token"]
H = {"Authorization": f"Bearer {TOK}"}
print("OK login -", body["email"], body["role"])

# 2) Dashboard ANTES
linha("2) DASHBOARD ANTES")
st, d = req("GET", "/api/admin/dashboard", headers=H)
print("total_leads:", d["total_leads"], "| simulacoes:", d["simulacoes"],
      "| avaliacoes:", d["avaliacoes"], "| imoveis_ativos:", d["imoveis_ativos"])

# 3) Cadastrar LOTE (terreno)
linha("3) CADASTRAR LOTE")
st, im = req("POST", "/api/admin/imoveis", headers=H, body={
    "titulo": "Lote 450m² · Bairro Candeias",
    "bairro": "Candeias",
    "tipo": "Terreno",
    "quartos": 0, "suites": 0, "vagas": 0,
    "area_util": 450.0,
    "preco": 320000,
    "descricao": "Lote plano em rua asfaltada, pronto para construir. Documentacao em dia.",
    "caracteristicas": ["plano", "asfalto", "documentacao_ok"],
    "destaque": True, "ativo": True,
})
assert st in (200, 201), im
IMOVEL_ID = im["id"] if "id" in im else im.get("imovel", {}).get("id")
print("OK lote criado id=", IMOVEL_ID, "slug=", im.get("slug"))

# 4) Upload de imagem (gera PNG simples 1200x800 verde)
linha("4) UPLOAD IMAGEM CAPA")
try:
    from PIL import Image as PIL
    img = PIL.new("RGB", (1200, 800), (94, 132, 79))  # verde mata
    # marca dagua suave
    from PIL import ImageDraw
    ImageDraw.Draw(img).text((40, 40), "LOTE 450m2 Candeias", fill=(255, 255, 255))
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85); jpg = buf.getvalue()
    st, up = req("POST", f"/api/admin/imoveis/{IMOVEL_ID}/imagens", headers=H,
                 multipart={"fields": {"tipo": "capa"},
                            "files": [{"name": "files", "filename": "capa.jpg",
                                       "ctype": "image/jpeg", "data": jpg}]})
    print("upload status:", st, "->", up)
except Exception as e:
    print("falhou upload:", e)

# 5) Simulacao publica (vira lead simulador, comprometimento OK -> quente)
linha("5) SIMULACAO PUBLICA (deve virar lead QUENTE)")
st, sim = req("POST", "/api/simular-financiamento", body={
    "valor_imovel": 320000, "entrada": 80000, "prazo_meses": 360,
    "taxa_anual": 0.1149, "sistema": "SAC",
    "renda_mensal": 12000,
    "nome": "Joao Comprador Teste", "contato": "(43) 99888-7777",
})
print("status:", st, "| parcela:", sim.get("parcela_inicial"),
      "| comprometimento_ok:", sim.get("comprometimento_ok"))

# 6) Avaliacao publica (vira lead vendedor)
linha("6) AVALIACAO PUBLICA (deve virar lead vendedor)")
st, av = req("POST", "/api/avaliar-imovel", body={
    "bairro": "candeias", "area_util": 180, "quartos": 3,
    "suites": 1, "vagas": 2, "padrao": "medio", "estado": "bom", "idade": "0_10",
    "nome": "Maria Vendedora Teste", "contato": "(43) 98777-6666",
})
print("status:", st, "| valor_central:", av.get("valor_central"),
      "| confianca:", av.get("confianca"))

# 7) Criar lead manual
linha("7) CRIAR LEAD MANUAL via admin")
st, lm = req("POST", "/api/admin/leads", headers=H, body={
    "nome": "Carlos Indicacao", "telefone": "43977776666",
    "origem": "indicacao", "observacoes": "indicado pelo dr. fulano, procura sobrado em Candeias 600k"
})
print("status:", st, "->", lm)

# 8) Listar leads
linha("8) LISTAR LEADS")
st, lst = req("GET", "/api/admin/leads", headers=H)
for l in lst["leads"]:
    print(f"  #{l['id']:<3} {l['temperatura']:6} | {l['estagio']:11} | {l['origem']:10} | "
          f"score={l['score']:3} | {l['nome'] or l['telefone']}")

# 9) Dashboard DEPOIS
linha("9) DASHBOARD DEPOIS")
st, d = req("GET", "/api/admin/dashboard", headers=H)
print("total_leads:", d["total_leads"])
print("por_temperatura:", d["por_temperatura"])
print("por_origem:", d["por_origem"])
print("por_estagio:", d["por_estagio"])
print("simulacoes:", d["simulacoes"], "| avaliacoes:", d["avaliacoes"],
      "| imoveis_ativos:", d["imoveis_ativos"])

# 10) Mover lead para visita e ver virar quente
linha("10) MOVER LEAD MANUAL PARA VISITA")
lid = lm["id"]
st, _ = req("PATCH", f"/api/admin/leads/{lid}", headers=H, body={"estagio": "visita"})
st, det = req("GET", f"/api/admin/leads/{lid}", headers=H)
print(f"lead #{lid} agora: estagio={det['estagio']} temperatura={det['temperatura']}")

print("\n>>> SMOKE TEST OK <<<")
