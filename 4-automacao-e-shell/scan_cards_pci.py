#!/usr/bin/env python3
"""
PCI-DSS & Financial Data Compliance Auditor (Zero-Dependency & Zero False-Positive)
Módulo universal de conformidade e auditoria de dados financeiros baseado em 3 categorias estritas:
  1. MAPEAMENTO DE CONTROLE (Metadados Permitidos: ID, BIN 6 dígitos, Brand, Bank, Level, Token)
  2. VERIFICAÇÃO DE VULNERABILIDADE (card_preview vazando PAN, have_cardholder_number=1, CVV/Password)
  3. LOG DE COMPLIANCE (Saída padronizada em ./reports/compliance_pci_audit.json com hashes SHA-256)
"""

import os
import sys
import re
import json
import argparse
import ssl
import hashlib
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser

# Regex refinado: números de 13 a 19 dígitos isolados (sem floats ou SVG)
CANDIDATE_DIGITS_REGEX = re.compile(r'(?<![\d\.])(\d{13,19})(?![\d\.])')

# Regras de BIN e prefixos estritos para emissores reais
CARD_PREFIXES = {
    "Visa": re.compile(r'^4[0-9]{12}(?:[0-9]{3})?$'),
    "Mastercard": re.compile(r'^(?:5[1-5][0-9]{14}|2(?:22[1-9]|2[3-9][0-9]|[3-6][0-9]{2}|7[0-1][0-9]|720)[0-9]{12})$'),
    "American Express": re.compile(r'^3[47][0-9]{13}$'),
    "Elo": re.compile(r'^(?:401178|401179|431274|438935|451416|457393|457631|457632|504175|627780|636297|636368|506699|5067[0-9]{2}|509[0-9]{3}|6500[0-9]{2}|6504[0-9]{2}|6505[0-9]{2}|6509[0-9]{2}|6516[0-9]{2}|6550[0-9]{2})[0-9]{10,12}$'),
    "Hipercard": re.compile(r'^(?:606282\d{10}|3841\d{12}|3841\d{15})$'),
    "Discover": re.compile(r'^6(?:011|5[0-9]{2})[0-9]{12}$'),
    "Diners": re.compile(r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$')
}

# Rotas canônicas e endpoints de pagamento / carteira
COMMON_API_ENDPOINTS = [
    "/api/v1/cards",
    "/api/v1/checkout",
    "/api/v1/wallet/list",
    "/api/v1/user/payments",
    "/api/v1/consultas",
    "/api/v1/profile",
    "/api/v1/user/cards",
    "/api/v1/wallet",
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
            if any(p in attr_lower or p in val_str for p in ["card_preview", "cardholder", "card_number", "cvv", "card_password"]):
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
    """Aplica o mascaramento mandatório PCI-DSS 3.3 (Primeiros 6 e últimos 4)."""
    clean = re.sub(r'\D', '', str(card_number))
    if len(clean) >= 12:
        return f"{clean[:6]}{'*' * (len(clean) - 10)}{clean[-4:]}"
    elif len(clean) > 4:
        return f"{'*' * (len(clean) - 4)}{clean[-4:]}"
    return "****"

def compute_sha256(content: str) -> str:
    return hashlib.sha256(str(content).encode('utf-8', errors='ignore')).hexdigest()

def auditar_estrutura_objeto(obj: dict, fonte: str, results: dict):
    """
    Aplica as 3 Categorias Canônicas de Auditoria PCI-DSS sobre objetos JSON:
      1. Mapeamento de Controle (Metadados Permitidos)
      2. Verificação de Vulnerabilidade (Sinalização de Risco)
    """
    # Verifica se o objeto possui traços de registro de cartão/pagamento
    chaves = [k.lower() for k in obj.keys()]
    eh_estrutura_cartao = any(k in chaves for k in ["bin", "card_token", "titular_preview", "card_preview", "have_cardholder_number", "brand", "bank", "level"])

    if not eh_estrutura_cartao:
        return

    # --- 1. MAPEAMENTO DE CONTROLE (METADADOS PERMITIDOS) ---
    reg_id = obj.get("id") or obj.get("card_id") or obj.get("payment_id")
    raw_bin = str(obj.get("bin") or "")[:6]
    brand = obj.get("brand") or obj.get("bandeira") or identify_brand(raw_bin) or "DESCONHECIDA"
    bank = obj.get("bank") or obj.get("banco") or "NÃO_INFORMADO"
    level = obj.get("level") or obj.get("categoria") or obj.get("tipo") or "PADRÃO"
    token = obj.get("card_token") or obj.get("token") or obj.get("payment_token") or "AUSENTE"

    metadado_permitido = {
        "id": reg_id,
        "bin": raw_bin if raw_bin else None,
        "brand": str(brand).upper(),
        "bank": str(bank).upper(),
        "level": str(level).upper(),
        "card_token_hash": compute_sha256(token)[:16] if token != "AUSENTE" else None,
        "fonte": fonte
    }
    results["mapeamento_controle"].append(metadado_permitido)

    # --- 2. VERIFICAÇÃO DE VULNERABILIDADE (SINALIZAÇÃO DE RISCO) ---
    
    # 2.1 Validação de card_preview
    card_preview = obj.get("card_preview")
    if card_preview is not None:
        val_str = str(card_preview).strip()
        # Se contiver mais do que os 4 últimos dígitos desmascarados ou for um PAN completo
        digitos_limpos = re.sub(r'\D', '', val_str)
        if len(digitos_limpos) > 4 and ('*' not in val_str and 'X' not in val_str.upper()):
            vuln = {
                "tipo": "ALERTA_CRITICO_VAZAMENTO_PAN",
                "requisito_pci": "PCI-DSS 3.3 (Proteção de PAN em exibição)",
                "campo": "card_preview",
                "valor_mascarado": mask_pan(val_str),
                "fonte": fonte,
                "criticidade": "CRÍTICA",
                "descricao": "O campo 'card_preview' está populado com PAN desmascarado excedendo os 4 dígitos finais permitidos."
            }
            results["verificacao_vulnerabilidade"].append(vuln)
            print(f"🔥 [CRÍTICO] Vazamento de PAN em 'card_preview' na {fonte}: {mask_pan(val_str)}")

    # 2.2 Validação de have_cardholder_number
    have_holder = obj.get("have_cardholder_number")
    raw_holder = obj.get("cardholder_number") or obj.get("cardholder") or obj.get("numero_cartao")
    if have_holder in [1, "1", True] or raw_holder:
        vuln = {
            "tipo": "NAO_CONFORME_RETENCAO_DADOS_SENSIVEIS",
            "requisito_pci": "PCI-DSS 3.4 & 3.2 (Retenção indevida de dados do titular/número)",
            "campo": "have_cardholder_number / cardholder_number",
            "fonte": fonte,
            "criticidade": "ALTA",
            "descricao": "Vulnerabilidade de retenção de dados sensíveis do titular (have_cardholder_number ativo ou número bruto persistido)."
        }
        results["verificacao_vulnerabilidade"].append(vuln)
        print(f"⚠️ [NÃO CONFORME] Retenção de dados sensíveis ('have_cardholder_number') detectada na {fonte}!")

    # 2.3 Validação de Dados de Autenticação Sensíveis (SAD): CVV, Senhas (PCI-DSS 3.2)
    for chave_sad in ["card_password", "senha_cartao", "cvv", "cvv2", "security_code", "card_cvv"]:
        val_sad = obj.get(chave_sad)
        if val_sad is True or (val_sad is not None and str(val_sad).strip() not in ["", "null", "false", "0"]):
            bloqueio = {
                "tipo": "BLOQUEIO_IMEDIATO_VIOLACAO_PCI_3_2",
                "requisito_pci": "PCI-DSS 3.2 (Proibição estrita de armazenamento de Dados de Autenticação Sensíveis após autorização)",
                "campo": chave_sad,
                "fonte": fonte,
                "criticidade": "FATAL",
                "descricao": f"Presença de dado de autenticação sensível ('{chave_sad}'). Disparando bloqueio imediato do pipeline."
            }
            results["verificacao_vulnerabilidade"].append(bloqueio)
            results["bloqueio_pipeline"] = True
            print(f"🚨 [BLOQUEIO IMEDIATO] Violação estrita do PCI-DSS Req 3.2: '{chave_sad}' presente na {fonte}!")

def varrer_json_recursivo(data, fonte: str, results: dict):
    """Percorre recursivamente árvores JSON em busca de objetos de cartão."""
    if isinstance(data, dict):
        auditar_estrutura_objeto(data, fonte, results)
        for _, v in data.items():
            varrer_json_recursivo(v, fonte, results)
    elif isinstance(data, list):
        for item in data:
            varrer_json_recursivo(item, fonte, results)

def scan_text_content(content: str, source_label: str, results: dict):
    """Varre strings brutas em busca de PAN e tenta parsear JSON embutido."""
    content_str = str(content)
    
    # 1. Tentar parsear JSON direto
    try:
        dados_json = json.loads(content_str)
        varrer_json_recursivo(dados_json, source_label, results)
    except Exception:
        pass

    # 2. Varredura por PAN (Apenas BINs reais + Luhn Check)
    candidates = set(CANDIDATE_DIGITS_REGEX.findall(content_str))
    for candidate in candidates:
        brand = identify_brand(candidate)
        if brand and luhn_checksum(candidate):
            masked = mask_pan(candidate)
            finding = {
                "tipo": "ALERTA_CRITICO_VAZAMENTO_PAN",
                "requisito_pci": "PCI-DSS 3.3",
                "bandeira": brand,
                "cartao_mascarado": masked,
                "fonte": source_label,
                "criticidade": "CRÍTICA",
                "descricao": f"Número de cartão de crédito válido ({brand}) exposto em texto claro."
            }
            results["verificacao_vulnerabilidade"].append(finding)
            print(f"🔥 [CRÍTICO] Cartão {brand} Válido detectado na {source_label}: {masked}")

def fetch_url(url: str, token: str = None, timeout: int = 10, method: str = "GET", payload: dict = None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/html, */*",
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    data_bytes = json.dumps(payload).encode('utf-8') if payload else None
    req = Request(url, headers=headers, data=data_bytes, method=method)
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
                results["verificacao_vulnerabilidade"].append({
                    "tipo": "ATRIBUTO_HTML_SENSIVEL",
                    "requisito_pci": "PCI-DSS 3.3 / Práticas Seguras de UI",
                    "tag": item["tag"],
                    "atributo": item["attr"],
                    "valor": item["val"],
                    "criticidade": "MÉDIA",
                    "descricao": f"Elemento HTML <{item['tag']}> com atributo potencialmente sensível '{item['attr']}' exposto no DOM."
                })
        except Exception:
            pass
    else:
        results["erros"].append(f"UI Error: {body}")

    print(f"\n🔍 [2/2] Escaneando Endpoints de API & Segregação de Dados Financeiros...")
    for endpoint in COMMON_API_ENDPOINTS:
        api_url = urljoin(target_url, endpoint)
        
        # Teste GET
        status, body = fetch_url(api_url, token=token, timeout=6, method="GET")
        if status in [200, 201]:
            print(f"🔎 Analisando endpoint ativo GET: {endpoint} (HTTP {status})")
            scan_text_content(body, f"API GET ({endpoint})", results)
            results["log_compliance"]["endpoints_testados"].append({
                "endpoint": endpoint,
                "metodo": "GET",
                "status_http": status,
                "hash_resposta": compute_sha256(body)
            })
        elif status in [401, 403]:
            results["meta"]["endpoints_autenticados"].append(endpoint)

        # Teste POST de Simulação Segura
        status_post, body_post = fetch_url(api_url, token=token, timeout=6, method="POST", payload={"check": True, "modalidade": "Consultavel"})
        if status_post in [200, 201]:
            print(f"🔎 Analisando resposta POST: {endpoint} (HTTP {status_post})")
            scan_text_content(body_post, f"API POST ({endpoint})", results)
            results["log_compliance"]["endpoints_testados"].append({
                "endpoint": endpoint,
                "metodo": "POST",
                "status_http": status_post,
                "hash_resposta": compute_sha256(body_post)
            })

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
                        results["log_compliance"]["endpoints_testados"].append({
                            "arquivo": rel_path,
                            "hash_arquivo": compute_sha256(content)
                        })
                except Exception:
                    pass

def main():
    parser = argparse.ArgumentParser(description="Auditoria de Conformidade de Dados Financeiros (PCI-DSS)")
    parser.add_argument("target", help="URL do site (ex: https://alvo.com) ou Caminho do Diretório Local (ex: .)")
    parser.add_argument("--token", help="Bearer Token de autenticação caso o site exija", default=None)
    parser.add_argument("--output", help="Arquivo de saída JSON para o relatório", default="./reports/compliance_pci_audit.json")
    args = parser.parse_args()

    # Estrutura Canônica em 3 Categorias de Governança
    results = {
        "meta": {
            "alvo": args.target,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "status_code": None,
            "endpoints_autenticados": []
        },
        "status_geral_compliance": "CONFORME",
        "bloqueio_pipeline": False,
        "mapeamento_controle": [],             # 1. Metadados Permitidos (ID, BIN, Brand, Bank, Level, Token)
        "verificacao_vulnerabilidade": [],     # 2. Riscos e Não-Conformidades (card_preview, cardholder, CVV)
        "log_compliance": {                    # 3. Registro Estruturado com Hashes de Governança
            "total_endpoints_analisados": 0,
            "endpoints_testados": []
        },
        "erros": []
    }

    print("==============================================================================")
    print("🛡️ AUDITORIA DE CONFORMIDADE DE DADOS FINANCEIROS & SEGREGAÇÃO PCI-DSS")
    print(f"🎯 Alvo: {args.target}")
    print("==============================================================================")

    if args.target.startswith("http://") or args.target.startswith("https://"):
        scan_web_target(args.target, token=args.token, results=results)
    else:
        scan_local_workspace(os.path.abspath(args.target), results=results)

    results["log_compliance"]["total_endpoints_analisados"] = len(results["log_compliance"]["endpoints_testados"])

    # Determinar Status Geral de Compliance
    if results["bloqueio_pipeline"]:
        results["status_geral_compliance"] = "BLOQUEIO_IMEDIATO"
    elif any(v["criticidade"] == "CRÍTICA" for v in results["verificacao_vulnerabilidade"]):
        results["status_geral_compliance"] = "ALERTA_CRITICO"
    elif any(v["criticidade"] == "ALTA" for v in results["verificacao_vulnerabilidade"]):
        results["status_geral_compliance"] = "NAO_CONFORME"
    else:
        results["status_geral_compliance"] = "CONFORME"

    # Resumo Executivo
    print("\n==============================================================================")
    print("📊 PAINEL DE CONFORMIDADE PCI-DSS & SEGREGAÇÃO DE DADOS")
    print("==============================================================================")
    print(f"📋 Status de Governança:               [{results['status_geral_compliance']}]")
    print(f"✅ Registros em Mapeamento de Controle: {len(results['mapeamento_controle'])}")
    print(f"⚠️ Vulnerabilidades / Não-Conformidades: {len(results['verificacao_vulnerabilidade'])}")
    print(f"🔒 Hashes de Validação Gerados:        {results['log_compliance']['total_endpoints_analisados']}")

    if results["status_geral_compliance"] == "CONFORME":
        print("\n✨ [RESULTADO: APROVADO] Nenhuma retenção indevida ou vazamento de PAN detectado.")
        print("   Todos os metadados estão devidamente segregados conforme requisitos PCI-DSS.")
    elif results["status_geral_compliance"] == "BLOQUEIO_IMEDIATO":
        print("\n🚨 [RESULTADO: BLOQUEIO IMEDIATO] Violação estrita do PCI-DSS Req 3.2 detectada!")
        print("   Presença de Dados de Autenticação Sensíveis (CVV ou senhas de cartão).")
    else:
        print(f"\n⚠️ [RESULTADO: {results['status_geral_compliance']}] Revisão de segurança necessária.")

    # Salva o arquivo de saída formatada de compliance
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Log de Compliance salvo com sucesso em: {args.output}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
