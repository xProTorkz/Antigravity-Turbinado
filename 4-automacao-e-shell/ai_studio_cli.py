#!/usr/bin/env python3
"""
🚀 AI Studio CLI — Ponte Direta Google AI Studio <-> Antigravity
Envia prompts diretamente para os modelos do Google AI Studio via terminal/IDE.
Zero dependências externas (utiliza urllib.request padrão do Python 3).
"""

import sys
import os
import json
import urllib.request
import urllib.error
import argparse

KEY_FILE = os.path.expanduser("~/.gemini/ai_studio_key.txt")

def get_api_key(cli_key=None):
    if cli_key:
        return cli_key.strip()
    if os.environ.get("AI_STUDIO_API_KEY"):
        return os.environ.get("AI_STUDIO_API_KEY").strip()
    if os.environ.get("GEMINI_API_KEY") and os.environ.get("GEMINI_API_KEY") != "DISABLED_ZERO_TOKEN_LOCK":
        return os.environ.get("GEMINI_API_KEY").strip()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            k = f.read().strip()
            if k and k != "DISABLED_ZERO_TOKEN_LOCK":
                return k
    return None

def save_api_key(key):
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    with open(KEY_FILE, "w") as f:
        f.write(key.strip())
    print(f"✅ Chave do Google AI Studio salva com sucesso em {KEY_FILE}!")

def send_prompt(prompt, api_key, model="gemini-2.0-flash", system_instruction=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            try:
                text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                return text
            except (KeyError, IndexError):
                return json.dumps(res_json, indent=2)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("error", {}).get("message", error_body)
        except Exception:
            msg = error_body
        raise RuntimeError(f"Erro na API Google AI Studio (HTTP {e.code}): {msg}")
    except Exception as e:
        raise RuntimeError(f"Falha de conexão com Google AI Studio: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ponte Direta Antigravity <-> Google AI Studio")
    parser.add_argument("prompt", nargs="*", help="O prompt a ser enviado para o modelo")
    parser.add_argument("--key", help="Definir chave de API do Google AI Studio")
    parser.add_argument("--set-key", help="Salvar chave de API permanentemente")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Modelo a utilizar (padrão: gemini-2.0-flash)")
    parser.add_argument("--system", help="Instrução de sistema opcional")
    
    args = parser.parse_args()
    
    if args.set_key:
        save_api_key(args.set_key)
        if not args.prompt:
            return
            
    api_key = get_api_key(args.key)
    
    if not args.prompt:
        if not api_key:
            print("⚠️ Nenhuma chave de API configurada.")
            print("👉 Obtenha sua chave gratuitamente em: https://aistudio.google.com/app/apikey")
            print("👉 Para salvar execute: python3 ai_studio_cli.py --set-key AIzaSy...")
        else:
            print("✅ Google AI Studio CLI pronto!")
            print(f"🔑 Chave configurada em: {KEY_FILE}")
            print("👉 Uso: python3 ai_studio_cli.py 'Seu prompt aqui'")
        return
        
    if not api_key:
        print("❌ Erro: Chave de API do Google AI Studio não encontrada.")
        print("1. Acesse: https://aistudio.google.com/app/apikey")
        print("2. Clique em 'Create API key'")
        print("3. Execute: python3 ai_studio_cli.py --set-key <SUA_CHAVE>")
        sys.exit(1)
        
    full_prompt = " ".join(args.prompt)
    print(f"🤖 Enviando para Google AI Studio [{args.model}]...\n")
    
    try:
        response = send_prompt(full_prompt, api_key, model=args.model, system_instruction=args.system)
        print("--- RESPOSTA DO AI STUDIO ---")
        print(response)
        print("-----------------------------")
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
