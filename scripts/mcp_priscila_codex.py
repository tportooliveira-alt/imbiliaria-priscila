"""Entrada local do MCP da Priscila para o Codex.

Este arquivo roda o MCP por stdio, sem abrir porta HTTP e sem depender de
token remoto. Por padrao, ferramentas com efeito externo ficam desligadas.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if os.getenv("CODEX_PRISCILA_MCP_ENABLE_EXTERNAL_ACTIONS", "0") != "1":
    os.environ["MCP_WRITE_ENABLED"] = "0"
    os.environ["MCP_WHATSAPP_ENABLED"] = "0"
    os.environ["MCP_IG_PUBLISH_ENABLED"] = "0"

from app.mcp_server import mcp  # noqa: E402


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
