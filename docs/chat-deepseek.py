#!/usr/bin/env python3
"""Chat direto com DeepSeek no terminal. Ctrl+C pra sair."""
import os, sys
sys.path.insert(0, '/var/www/imobiliaria')
from dotenv import load_dotenv
load_dotenv('/var/www/imobiliaria/.env')

from openai import OpenAI

client = OpenAI(
    api_key=os.environ['DEEPSEEK_API_KEY'],
    base_url='https://api.deepseek.com',
)

historico = []
print("=== DeepSeek Chat === (Ctrl+C pra sair)\n")

while True:
    try:
        msg = input("Você: ").strip()
        if not msg:
            continue
        historico.append({"role": "user", "content": msg})
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=historico,
            max_tokens=800,
        )
        texto = resp.choices[0].message.content or ""
        historico.append({"role": "assistant", "content": texto})
        print(f"\nDeepSeek: {texto}\n")
    except KeyboardInterrupt:
        print("\nAté mais!")
        break
