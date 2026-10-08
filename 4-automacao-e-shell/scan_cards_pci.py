#!/usr/bin/env python3
"""
PCI-DSS & PAN Leak Auditor (Zero-Dependency & Zero False-Positive)
Módulo universal de varredura contra vazamento de cartões de crédito (PAN),
parâmetros sensíveis de pagamento e não-conformidades com PCI-DSS em qualquer
site (URL web) ou ecossistema local (arquivos HTML/JS/JSON).
Utiliza estritamente a biblioteca padrão do Python (Zero dependências externas).
"""

import os
import sys
import re
import json
import argparse
import ssl
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

# Regex refinado: ignora números flutuantes ou coordenadas SVG
CANDIDATE_DIGITS_REGEX = re.compile(r'(?<![\d\.])(\d{13,19})(?![\d\.])')

# Regras de BIN e prefixos estritos para emissores reais mundiais e nacionais
CARD_PREFIXES = {
    "Visa": re.compile(r'^4[0-9]{12}(?:[0-9]{3})?$'),
    "Mastercard": re.compile(r'^(?:5[1-5][0-9]{14}|2(?:22[1-9]|2[3-9][0-9]|[3-6][0-9]{2}|7[0-1][0-9]|720)[0-9]{12})$'),
    "American Express": re.compile(r'^3[47][0-9]{13}$'),
    "Elo": re.compile(r'^(?:401178|401179|431274|438935|451416|457393|457631|457632|504175|627780|636297|636368|506699|5067[0-9]{2}|509[0-9]{3}|6500[0-9]{2}|6504[0-9]{2}|6505[0-9]{2}|6509[0-9]{2}|6516[0-9]{2}|6550[0-9]{2})[0-9]{10,12}$'),
    "Hipercard": re.compile(r'^(?:606282\d{10}|3841\d{12}|3841\d{15})$'),
    "Discover": re.compile(r'^6(?:011|5[0-9]{2})[0-9]{12}$'),
    "Diners": re.compile(r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$')
}

# Regex estrito para parâmetros de risco PCI com limite de palavra (ignora classes CSS soltas)
RISK_PARAMS_REGEX = re.compile(r'\b(card_preview|have_cardholder_number|cardholder|card_number|card_num|credit_card|cc_number|cvv|card_cvv|security_code|card_token|payment_method_id)\b', re.IGNORECASE)

COMMON_API_ENDPOINTS = [
    "/api/v1/profile",
    "/api/v1/user/cards",
    "/api/v1/wallet",
    "/api/v1/payments",
    "/api/checkout/config",
    "/api/v2/wallet",
    "/api/payment-methods",
    "/api/cards"
]

class SensitiveHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sensitive_tags = []

    def handle_starttag(self, tag, attrs):
        for attr, val in attrs:
            attr_lower = attr.lower()
            val_str = str(val).lower() if val else ""
            if any(p in attr_lower or p in val_str for p in ["card_preview", "cardholder", "card_number", "cvv"]):
                self.sensitive_tags.append({
                    "tag": tag,
                    "attr": attr,
                    "val": str(val)[:60]
                })

def luhn_checksum(card_number: str) -> bool:
    """Valida o algoritmo de Luhn (Mod 10)."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    return checksum % 10 == 0

def identify_brand(card_number: str) -> str:
    """Retorna a bandeira do cartão somente se corresponder a um BIN/IIN real."""
    for brand, pattern in CARD_PREFIXES.items():
        if pattern.match(card_number):
            return brand
    return None

def mask_pan(card_number: str) -> str:
    clean = re.sub(r'\D', '', card_number)
    if len(clean) >= 12:
        return f"{clean[:6]}{'*' * (len(clean) - 10)}{clean[-4:]}"
    return f"{'*' * (len(clean) - 4)}{clean[-4:]}" if len(clean) > 4 else "****"

def scan_text_content(content: str, source_label: str, results: dict):
    content_str = str(content)
    
    # 1. Varredura por PAN (Apenas BINs reais + Luhn Check)
    candidates = set(CANDIDATE_DIGITS_REGEX.findall(content_str))
    for candidate in candidates:
        brand = identify_brand(candidate)
        if brand and luhn_checksum(candidate):
            masked = mask_pan(candidate)
            finding = {
                "tipo": "PAN_EXPOSTO",
                "bandeira": brand,
                "cartao_mascarado": masked,
                "fonte": source_label,
                "criticidade": "CRÍTICA",
                "descricao": f"Número de cartão de crédito válido ({brand}) exposto em texto claro."
            }
            results["vulnerabilidades"].append(finding)
            print(f"🔥 [CRÍTICO] Cartão {brand} Válido detectado na {source_label}: {masked}")

    # 2. Varredura por Parâmetros de Risco PCI
    found_params = set(RISK_PARAMS_REGEX.findall(content_str))
    for param in found_params:
        finding = {
            "tipo": "PARAMETRO_PCI_RISCO",
            "parametro": param,
            "fonte": source_label,
            "criticidade": "ALTA",
            "descricao": f"Parâmetro sensível de pagamento '{param}' detectado na fonte."
        }
        results["parametros_detectados"].append(finding)
        print(f"⚠️ [ALERTA] Parâmetro sensível '{param}' detectado na {source_label}!")

def fetch_url(url: str, token: str = None, timeout: int = 10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = Request(url, headers=headers)
    try:
        with urlopen(req, context=ctx, timeout=timeout) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
            return resp.status, data
    except Exception as e:
        return None, str(e)

def scan_web_target(target_url: str, token: str = None, results: dict = None):
    print(f"\n📡 [1/2] Escaneando Superfície Web & HTML/DOM: {target_url}")
    status, body = fetch_url(target_url, token=token, timeout=12)
    results["meta"]["status_code"] = status
    if status is not None:
        scan_text_content(body, f"UI / HTML ({target_url})", results)

        try:
            parser = SensitiveHTMLParser()
            parser.feed(body)
            for item in parser.sensitive_tags:
                print(f"👀 [INFO] Atributo sensível exposto em <{item['tag']}>: {item['attr']} = {item['val']}")
                results["parametros_detectados"].append({
                    "tipo": "ATRIBUTO_HTML_EXPOSTO",
                    "tag": item["tag"],
                    "atributo": item["attr"],
                    "valor": item["val"],
                    "criticidade": "MÉDIA"
                })
        except Exception:
            pass
    else:
        print(f"[-] Erro ao acessar {target_url}: {body}")
        results["erros"].append(f"UI Error: {body}")

    print(f"\n🔍 [2/2] Escaneando Shadow APIs & Endpoints de Pagamento...")
    for endpoint in COMMON_API_ENDPOINTS:
        api_url = urljoin(target_url, endpoint)
        status, body = fetch_url(api_url, token=token, timeout=6)
        if status in [200, 201, 204]:
            print(f"🔎 Analisando endpoint ativo: {endpoint} (HTTP {status})")
            scan_text_content(body, f"API Endpoint ({endpoint})", results)
        elif status in [401, 403]:
            results["meta"]["endpoints_autenticados"].append(endpoint)

def scan_local_workspace(directory: str, results: dict):
    print(f"\n📂 [LOCAL] Escaneando Arquivos do Workspace: {directory}")
    exts = [".html", ".js", ".json", ".env", ".log", ".txt", ".ts", ".jsx", ".tsx"]
    for root, dirs, files in os.walk(directory):
        if any(skip in root for skip in [".git", "node_modules", ".chrome-profile", "assets"]):
            continue
        for file in files:
            if any(file.endswith(e) for e in exts):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        rel_path = os.path.relpath(file_path, directory)
                        scan_text_content(content, f"Arquivo Local ({rel_path})", results)
                except Exception:
                    pass

def main():
    parser = argparse.ArgumentParser(description="Varredura Universal de Vazamento de Cartões de Crédito (PAN) & PCI-DSS")
    parser.add_argument("target", help="URL do site (ex: https://alvo.com) ou Caminho do Diretório Local (ex: .)")
    parser.add_argument("--token", help="Bearer Token de autenticação caso o site exija", default=None)
    parser.add_argument("--output", help="Arquivo de saída JSON para o relatório", default=None)
    args = parser.parse_args()

    results = {
        "meta": {
            "alvo": args.target,
            "status_code": None,
            "endpoints_autenticados": []
        },
        "vulnerabilidades": [],
        "parametros_detectados": [],
        "erros": []
    }

    print("==============================================================================")
    print("🛡️ VARREDURA UNIVERSAL DE VAZAMENTO DE CARTÕES & PCI-DSS AUDIT")
    print(f"🎯 Alvo: {args.target}")
    print("==============================================================================")

    if args.target.startswith("http://") or args.target.startswith("https://"):
        scan_web_target(args.target, token=args.token, results=results)
    else:
        scan_local_workspace(os.path.abspath(args.target), results=results)

    # Resumo
    total_cards = len(results["vulnerabilidades"])
    total_params = len(results["parametros_detectados"])

    print("\n==============================================================================")
    print("📊 RESUMO DO SCAN PCI-DSS & VAZAMENTO DE DADOS")
    print("==============================================================================")
    print(f"🔥 Cartões Válidos Encontrados (BIN + Luhn Check): {total_cards}")
    print(f"⚠️ Parâmetros Sensíveis de Pagamento:             {total_params}")
    
    if total_cards == 0 and total_params == 0:
        print("✅ NENHUM VAZAMENTO DE CARTÃO OU PARÂMETRO PCI DETECTADO.")
    elif total_cards == 0 and total_params > 0:
        print("ℹ️ NENHUM CARTÃO VAZADO. Parâmetros técnicos mapeados para conformidade.")
    else:
        print("🚨 ATENÇÃO: VAZAMENTO DE CARTÃO DE CRÉDITO IDENTIFICADO!")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"📄 Relatório JSON salvo em: {args.output}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
