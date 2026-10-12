#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compile_audit_report.py — Compilador e Gerador do Laudo Consolidado da Auditoria Total
Sentinela SRE / Antigravity Turbinado v5.0 (Deep Extraction Engine)

Varredura 100% Abrangente:
1. Mapeamento Profundo de APIs, Rotas e Endpoints (REST, GraphQL, Shadow APIs, Router paths).
2. Links Externos, Gateways e Webhooks Conectados (Stripe, Mercado Pago, AWS, Discord, etc.).
3. Parâmetros de Consulta (Query Params) e Flags Ocultas (?debug=, ?admin=, etc.).
4. Arquivos Ocultos (Dotfiles), .env*, Chaves .pem e Permissões chmod 0600.
5. Bancos de Dados Físicos (SQLite, schemas e contagem de tabelas).
6. DOM Oculto (inputs type=hidden, senhas, data-*, comentários HTML e SSR Hydration).
7. Score Unificado de Risco (0 a 100), Diff Forense Histórico, Matriz de Remediação e Dashboard HTML.
"""

import os
import sys
import re
import json
import socket
import hashlib
import sqlite3
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

def calculate_sha256(filepath: Path) -> str:
    """Calcula hash SHA-256 de um arquivo para integridade anti-tampering."""
    if not filepath.exists() or not filepath.is_file():
        return "N/A"
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return "ERROR_READING_FILE"

def is_port_externally_exposed(port: int) -> bool:
    """Verifica se a porta está ouvindo em 0.0.0.0, * ou interface pública (não apenas 127.0.0.1 / ::1)."""
    try:
        import subprocess
        res = subprocess.run(["lsof", f"-i:{port}", "-sTCP:LISTEN", "-n", "-P"], capture_output=True, text=True, timeout=2)
        for line in res.stdout.splitlines():
            if "LISTEN" in line:
                for chunk in line.split():
                    if f":{port}" in chunk:
                        if not (chunk.startswith("127.0.0.1:") or chunk.startswith("[::1]:") or chunk.startswith("localhost:")):
                            return True
        return False
    except Exception:
        return False

def scan_local_ports(host: str = "127.0.0.1", ports: list = None, timeout: float = 0.08) -> list:
    """Detecta rapidamente portas abertas essenciais."""
    if ports is None:
        ports = [21, 22, 80, 443, 3000, 3306, 5173, 5432, 6379, 8000, 8080, 8088, 8765, 9000, 27017]
    open_ports = []
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            if s.connect_ex((host, p)) == 0:
                service = "desconhecido"
                try:
                    service = socket.getservbyport(p, "tcp")
                except Exception:
                    pass
                open_ports.append({
                    "port": p,
                    "service": service,
                    "externally_exposed": is_port_externally_exposed(p)
                })
        except Exception:
            pass
        finally:
            s.close()
    return open_ports

def inspect_http_headers(host: str = "127.0.0.1", port: int = 80, timeout: float = 0.5) -> dict:
    """Dispara requisições HEAD/OPTIONS nos sockets locais para inspecionar cabeçalhos de segurança reais."""
    import http.client
    res = {
        "port": port,
        "http_responding": False,
        "status": 0,
        "server": None,
        "csp": None,
        "hsts": None,
        "cors": None,
        "x_frame_options": None,
        "x_content_type_options": None,
        "missing_headers": []
    }
    try:
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        conn.request("HEAD", "/")
        resp = conn.getresponse()
        res["http_responding"] = True
        res["status"] = resp.status
        headers = {k.lower(): v for k, v in resp.getheaders()}

        res["server"] = headers.get("server")
        res["csp"] = headers.get("content-security-policy")
        res["hsts"] = headers.get("strict-transport-security")
        res["cors"] = headers.get("access-control-allow-origin")
        res["x_frame_options"] = headers.get("x-frame-options")
        res["x_content_type_options"] = headers.get("x-content-type-options")

        if not res["csp"]: res["missing_headers"].append("Content-Security-Policy")
        if not res["x_frame_options"]: res["missing_headers"].append("X-Frame-Options")
        if not res["x_content_type_options"]: res["missing_headers"].append("X-Content-Type-Options")
        if not res["hsts"] and port in [443, 8443]: res["missing_headers"].append("Strict-Transport-Security")
        conn.close()
    except Exception:
        pass
    return res

def run_sca_analysis(scan_dir: Path) -> dict:
    """Executa Análise de Composição de Software (SCA) ativa e checagem de lockfiles/CVEs."""
    import subprocess
    sca_results = {
        "vulnerabilities": [],
        "total_vulns": 0,
        "critical": 0,
        "high": 0,
        "moderate": 0,
        "low": 0,
        "tool_used": "lockfile_inspection",
        "lockfiles_found": []
    }

    # 1. Lockfiles presentes
    for lk in ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "requirements.txt", "Pipfile.lock", "poetry.lock", "go.sum", "Cargo.lock"]:
        if (scan_dir / lk).exists():
            sca_results["lockfiles_found"].append(lk)

    # 2. Execução de npm audit se package.json existir
    if (scan_dir / "package.json").exists() and ((scan_dir / "package-lock.json").exists() or (scan_dir / "node_modules").exists()):
        try:
            res = subprocess.run(["npm", "audit", "--json"], cwd=str(scan_dir), capture_output=True, text=True, timeout=8)
            if res.stdout:
                data = json.loads(res.stdout)
                meta = data.get("metadata", {}).get("vulnerabilities", {})
                if meta:
                    sca_results["total_vulns"] = sum(meta.values())
                    sca_results["critical"] = meta.get("critical", 0)
                    sca_results["high"] = meta.get("high", 0)
                    sca_results["moderate"] = meta.get("moderate", 0)
                    sca_results["low"] = meta.get("low", 0)
                    sca_results["tool_used"] = "npm audit"

                vulns = data.get("vulnerabilities", {})
                if isinstance(vulns, dict):
                    for pkg, v_info in list(vulns.items())[:15]:
                        sev = v_info.get("severity", "moderate")
                        sca_results["vulnerabilities"].append({
                            "package": pkg,
                            "severity": sev,
                            "title": v_info.get("title", f"Vulnerabilidade identificada em {pkg}"),
                            "fix_available": bool(v_info.get("fixAvailable"))
                        })
        except Exception:
            pass

    # 3. Fallback / Adição para Python
    if (scan_dir / "requirements.txt").exists() and not sca_results["vulnerabilities"]:
        try:
            res = subprocess.run(["pip-audit", "--format=json", "-r", "requirements.txt"], cwd=str(scan_dir), capture_output=True, text=True, timeout=6)
            if res.stdout:
                data = json.loads(res.stdout)
                if isinstance(data, list):
                    for item in data:
                        for v in item.get("vulns", []):
                            sca_results["vulnerabilities"].append({
                                "package": item.get("name"),
                                "severity": "high",
                                "title": v.get("id", "Vulnerabilidade Python CVE"),
                                "fix_available": True
                            })
                            sca_results["high"] += 1
                            sca_results["total_vulns"] += 1
                    sca_results["tool_used"] = "pip-audit"
        except Exception:
            pass

    return sca_results

def categorize_route(route: str, method: str = "") -> dict:
    """Classifica detalhadamente a rota em categorias de negócio, criticidade e risco."""
    r_low = route.lower().strip()
    clean_r = r_low.split("?")[0]
    m_up = method.upper().strip() if method else ""

    # 1. Admin & Privilegiada
    if any(k in clean_r for k in ["/admin", "/administrator", "/root", "/manage", "/debug", "/internal", "/actuator", "/__inspect", "/env", "/config", "/system", "/terminal", "/bash", "/shell", "/phpmyadmin"]):
        return {
            "category": "ADMIN_PRIVILEGIADA",
            "risk_level": "CRITICA",
            "badge_cls": "badge-critica",
            "label": "🔴 ADMIN / PRIVILEGIADA"
        }

    # 2. Financeira & Pagamentos
    if any(k in clean_r for k in ["/checkout", "/payment", "/pagamento", "/pix", "/billing", "/cartao", "/card", "/invoice", "/fatura", "/subscription", "/assinatura", "/order", "/pedido", "/transacao", "/payout", "/wallet", "/carteira"]):
        return {
            "category": "FINANCEIRA_PAGAMENTO",
            "risk_level": "ALTA",
            "badge_cls": "badge-alta",
            "label": "🟠 FINANCEIRA / PAGAMENTO"
        }

    # 3. Autenticação & Sessão
    if any(k in clean_r for k in ["/login", "/signin", "/auth", "/oauth", "/register", "/signup", "/forgot-password", "/reset-password", "/token", "/refresh", "/logout", "/session", "/verify"]):
        return {
            "category": "AUTENTICACAO_SESSAO",
            "risk_level": "ALTA",
            "badge_cls": "badge-alta",
            "label": "🟡 AUTENTICAÇÃO / SESSÃO"
        }

    # 4. Webhooks & Callbacks
    if any(k in clean_r for k in ["/webhook", "/callback", "/ipn", "/notify", "/events", "/listener", "/dispatcher"]):
        return {
            "category": "WEBHOOK_CALLBACK",
            "risk_level": "MEDIA",
            "badge_cls": "badge-media",
            "label": "🟣 WEBHOOK / CALLBACK"
        }

    # 5. Documentação & Swagger
    if any(k in clean_r for k in ["/swagger", "/api-docs", "/openapi", "/docs", "/redoc"]):
        return {
            "category": "DOCUMENTACAO_SWAGGER",
            "risk_level": "BAIXA",
            "badge_cls": "badge-baixa",
            "label": "📘 DOCUMENTAÇÃO / DOCS"
        }

    # 6. GraphQL
    if "/graphql" in clean_r:
        return {
            "category": "GRAPHQL_ENDPOINT",
            "risk_level": "MEDIA",
            "badge_cls": "badge-media",
            "label": "🔷 GRAPHQL ENDPOINT"
        }

    # 7. WebSocket / Stream
    if any(k in clean_r for k in ["/ws", "/socket.io", "/eventsource", "/stream"]):
        return {
            "category": "STREAM_WEBSOCKET",
            "risk_level": "MEDIA",
            "badge_cls": "badge-media",
            "label": "⚡ WEBSOCKET / STREAM"
        }

    # 8. REST Resource / API pública
    if any(k in clean_r for k in ["/api", "/v1", "/v2", "/v3", "/rest"]):
        risk = "MEDIA" if m_up in ["POST", "PUT", "DELETE", "PATCH"] else "BAIXA"
        b_cls = "badge-media" if risk == "MEDIA" else "badge-info"
        return {
            "category": "RECURSO_REST",
            "risk_level": risk,
            "badge_cls": b_cls,
            "label": "🔵 RECURSO / REST API"
        }

    # 9. Interface / Navegação UI
    return {
        "category": "INTERFACE_NAVEGACAO",
        "risk_level": "INFO",
        "badge_cls": "badge-info",
        "label": "🟢 INTERFACE / UI"
    }

def categorize_external_url(url: str) -> str:
    """Classifica a URL externa em categorias estratégicas de arquitetura e risco."""
    u = url.lower()
    # 1. Gateways de Pagamento
    if any(k in u for k in [
        "stripe.com", "mercadopago", "pagar.me", "asaas.com", "paypal.com",
        "cielo.com", "pagseguro", "hotmart", "kiwify", "braip", "eduzz",
        "monetizze", "inter.co", "cora.com", "juno.com", "ebanx.com", "adyen.com",
        "stone.com", "pagbank", "infinitepay"
    ]):
        return "GATEWAY_PAGAMENTO"

    # 2. IA, LLMs & Computação Cognitiva
    if any(k in u for k in [
        "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com",
        "groq.com", "together.ai", "mistral.ai", "huggingface.co", "deepseek.com",
        "perplexity.ai", "cohere.ai", "replicate.com", "ollama", "elevenlabs.io", "runwayml.com"
    ]):
        return "IA_E_LLM"

    # 3. Nuvem, Storage & BaaS
    if any(k in u for k in [
        "amazonaws.com", "firebaseio.com", "googleapis.com", "supabase.co",
        "cloudflare.com", "vercel.app", "render.com", "railway.app", "neon.tech",
        "planetscale.com", "digitaloceanspaces.com", "azure.com", "backblazeb2.com"
    ]):
        return "NUVEM_E_STORAGE"

    # 4. Webhooks, Mensageria & Notificações
    if any(k in u for k in [
        "discord.com/api/webhooks", "telegram.org", "slack.com/api", "sendgrid.com",
        "twilio.com", "evolution-api", "z-api", "zenvia", "mailgun.net", "resend.com",
        "postmarkapp.com", "hooks.zapier.com", "make.com", "n8n"
    ]):
        return "WEBHOOK_E_MENSAGERIA"

    # 5. Autenticação & OAuth
    if any(k in u for k in [
        "auth0.com", "clerk.dev", "clerk.com", "accounts.google.com",
        "github.com/login/oauth", "facebook.com/v", "keycloak", "okta.com"
    ]):
        return "AUTENTICACAO_E_OAUTH"

    # 6. Analytics & Rastreamento
    if any(k in u for k in [
        "google-analytics.com", "googletagmanager.com", "connect.facebook.net",
        "clarity.ms", "hotjar.com", "tiktok.com", "mixpanel.com", "amplitude.com",
        "posthog.com", "segment.io"
    ]):
        return "ANALYTICS_E_TRACKING"

    # 7. CDNs & Fontes
    if any(k in u for k in [
        "cdnjs.cloudflare.com", "jsdelivr.net", "unpkg.com", "fonts.googleapis.com",
        "fonts.gstatic.com", "tailwindcss.com", "bootstrapcdn.com"
    ]):
        return "CDN_E_ASSETS"

    return "API_EXTERNA"

def inspect_sqlite_tables(db_path: Path) -> list:
    """Extrai esquemas e nomes de tabelas de arquivos SQLite em modo somente-leitura."""
    try:
        conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
        conn.close()
        return tables
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════════════
# ESPECIFICAÇÃO DE CAPACIDADES ARQUITETURAIS (27 Domínios, 187 Capacidades)
# ══════════════════════════════════════════════════════════════════════════════
ARCHITECTURAL_CAPABILITIES_SPECS = [
    # 1. Autenticação, Identidade & Criptografia
    {"id": "jwt", "name": "JSON Web Tokens (JWT)", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(jwt|jsonwebtoken|jwt\.sign|jwt\.verify|pyjwt|auth0|jwks|bearer\s+[a-zA-Z0-9_\-\.]+)\b', re.I)},
    {"id": "paseto", "name": "PASETO", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(paseto|pasetojs|pasetopy)\b', re.I)},
    {"id": "refresh_tokens", "name": "Refresh Tokens Rotativos", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(refresh_token|refreshtoken|rotateRefreshToken|rotation_token|rotate_token)\b', re.I)},
    {"id": "oauth2_oidc", "name": "OAuth2 / OpenID Connect", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(oauth2|openid|oidc|passport-oauth|next-auth|grant_type|client_credentials|authorization_code)\b', re.I)},
    {"id": "saml_ldap", "name": "SAML / LDAP", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(saml|ldap|passport-saml|activedirectory|shibboleth)\b', re.I)},
    {"id": "webauthn_fido2", "name": "WebAuthn / FIDO2", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(webauthn|fido2|simplewebauthn|navigator\.credentials|credentialcreationoptions)\b', re.I)},
    {"id": "totp_mfa", "name": "TOTP (MFA / 2FA)", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(totp|speakeasy|otplib|authenticator|2fa|mfa|pyotp)\b', re.I)},
    {"id": "rbac", "name": "RBAC (Role-Based Access Control)", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(rbac|role_based|hasRole|requireRole|roles\.includes|user_role|checkRole)\b', re.I)},
    {"id": "abac", "name": "ABAC (Attribute-Based Access Control)", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(abac|casl|attribute_based|defineAbility|policy_check)\b', re.I)},
    {"id": "rls", "name": "Row-Level Security (RLS)", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(row\s+level\s+security|create\s+policy|enable\s+row\s+level|supabase\.auth\.uid|alter\s+table.*enable\s+row\s+level)\b', re.I)},
    {"id": "multi_tenancy", "name": "Multi-Tenancy Engines", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(multi_tenant|multi_tenancy|tenant_id|tenantId|organization_id|workspace_id)\b', re.I)},
    {"id": "hmac_sha256", "name": "HMAC-SHA256 Signatures", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(hmac|crypto\.createHmac|hmac\.new|sha256|hmac-sha256)\b', re.I)},
    {"id": "secrets_vault", "name": "Secrets Vaults (KMS)", "domain": "Autenticação, Identidade & Criptografia", "pattern": re.compile(r'\b(hashicorp.*vault|aws-kms|kms:Decrypt|google\.cloud\.kms|azure\s+key\s+vault|secretmanager)\b', re.I)},

    # 2. Lógica de Negócio & Concorrência
    {"id": "fsm", "name": "Finite State Machine (FSM)", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(xstate|fsm|finite\s+state\s+machine|statemachine|state_machine|transitions|machine\.transition)\b', re.I)},
    {"id": "idempotency_keys", "name": "Idempotency Keys", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(idempotency|idempotency-key|idempotent|idempotency_key)\b', re.I)},
    {"id": "acid_transactions", "name": "Transações ACID", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(begin\s+transaction|start\s+transaction|\$transaction|session\.start_transaction|transaction\.atomic|commit|rollback)\b', re.I)},
    {"id": "pessimistic_locking", "name": "Pessimistic Locking", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(select.*for\s+update|pessimistic_write|pessimistic_read|with_for_update|lock\s+table)\b', re.I)},
    {"id": "optimistic_locking", "name": "Optimistic Locking", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(optimistic_lock|version_column|version_id|@Version|check_version|optimisticLocking)\b', re.I)},
    {"id": "audit_trails", "name": "Audit Trails (Logs Imutáveis)", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(audit_trail|audit_log|auditlog|immutable_log|historico_auditoria|changelog_table)\b', re.I)},
    {"id": "circuit_breakers", "name": "Circuit Breakers", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(circuit_breaker|circuitbreaker|opossum|resilience4j|pybreaker|py_circuit_breaker)\b', re.I)},
    {"id": "exponential_backoff", "name": "Exponential Backoff & Retries", "domain": "Lógica de Negócio & Concorrência", "pattern": re.compile(r'\b(exponential_backoff|backoff|max_retries|retry_after|retry_count|tenacity)\b', re.I)},

    # 3. Processamento Assíncrono & Filas
    {"id": "message_brokers", "name": "Message Brokers (RabbitMQ, Apache Kafka)", "domain": "Processamento Assíncrono & Filas", "pattern": re.compile(r'\b(rabbitmq|amqp|amqplib|kafka|confluent_kafka|kafkajs|librdkafka)\b', re.I)},
    {"id": "in_memory_queues", "name": "In-Memory Queues (BullMQ / Redis)", "domain": "Processamento Assíncrono & Filas", "pattern": re.compile(r'\b(bullmq|bull\.js|kue|rsmq|bee-queue|celery_redis)\b', re.I)},
    {"id": "background_workers", "name": "Background Workers", "domain": "Processamento Assíncrono & Filas", "pattern": re.compile(r'\b(worker|workers|background_task|background_job|work_pool|celery\.task|job_processor)\b', re.I)},
    {"id": "dead_letter_queues", "name": "Dead Letter Queues (DLQ)", "domain": "Processamento Assíncrono & Filas", "pattern": re.compile(r'\b(dlq|dead_letter|deadletter|dead_letter_queue)\b', re.I)},
    {"id": "cron_schedulers", "name": "Cron Schedulers", "domain": "Processamento Assíncrono & Filas", "pattern": re.compile(r'\b(cron|node-cron|cronjob|crontab|agenda|scheduler|celery_beat|apscheduler)\b', re.I)},
    {"id": "webhooks_consumers", "name": "Webhooks Consumers", "domain": "Processamento Assíncrono & Filas", "pattern": re.compile(r'\b(webhook_consumer|handle_webhook|consume_webhook|on_webhook|stripe_webhook)\b', re.I)},

    # 4. Dados, Cache & Busca
    {"id": "connection_poolers", "name": "Connection Poolers (PgBouncer)", "domain": "Dados, Cache & Busca", "pattern": re.compile(r'\b(pgbouncer|pool_mode|connection_pool|pool_size|max_connections|pg_pool)\b', re.I)},
    {"id": "database_migrations", "name": "Database Migrations", "domain": "Dados, Cache & Busca", "pattern": re.compile(r'\b(alembic|prisma\s+migrate|knex\s+migrate|flyway|typeorm\s+migration|db:migrate)\b', re.I)},
    {"id": "database_replicas", "name": "Database Replicas (Read/Write Splitting)", "domain": "Dados, Cache & Busca", "pattern": re.compile(r'\b(read_replica|write_replica|master_slave|replica_pool|read_write_splitting)\b', re.I)},
    {"id": "db_indexes", "name": "Índices B-Tree / GIN / GiST", "domain": "Dados, Cache & Busca", "pattern": re.compile(r'\b(create\s+index|btree|gin\s+index|gist\s+index|using\s+gin|using\s+gist|using\s+btree)\b', re.I)},
    {"id": "cache_in_memory", "name": "Cache In-Memory (Redis, Memcached)", "domain": "Dados, Cache & Busca", "pattern": re.compile(r'\b(redis|memcached|ioredis|redis-py|cache_store|memory_cache)\b', re.I)},
    {"id": "cache_invalidation", "name": "Cache Invalidation & TTL", "domain": "Dados, Cache & Busca", "pattern": re.compile(r'\b(cache_invalidation|ttl|cache\.set.*ex|expire_after|cache_tag|purge_cache)\b', re.I)},
    {"id": "full_text_search", "name": "Full-Text Search Engines (Elasticsearch, Meilisearch)", "domain": "Dados, Cache & Busca", "pattern": re.compile(r'\b(elasticsearch|meilisearch|opensearch|typesense|lucene|solr)\b', re.I)},

    # 5. Rede, Tráfego & APIs
    {"id": "reverse_proxies", "name": "Reverse Proxies (Nginx, Traefik, Caddy)", "domain": "Rede, Tráfego & APIs", "pattern": re.compile(r'\b(nginx|traefik|caddy|caddyfile|proxy_pass|reverse_proxy)\b', re.I)},
    {"id": "api_gateways", "name": "API Gateways", "domain": "Rede, Tráfego & APIs", "pattern": re.compile(r'\b(api_gateway|kong|apigee|tyk|kraken\s+d|zuul|aws_apigateway)\b', re.I)},
    {"id": "rest_graphql_grpc", "name": "REST / GraphQL / gRPC", "domain": "Rede, Tráfego & APIs", "pattern": re.compile(r'\b(graphql|apollo|grpc|proto3|restful|protobuf|nexus|schema\.gql)\b', re.I)},
    {"id": "websockets", "name": "WebSockets", "domain": "Rede, Tráfego & APIs", "pattern": re.compile(r'\b(websocket|socket\.io|ws://|wss://|actioncable|channels|uWebSockets)\b', re.I)},
    {"id": "sse", "name": "Server-Sent Events (SSE)", "domain": "Rede, Tráfego & APIs", "pattern": re.compile(r'\b(server-sent\s+events|text/event-stream|eventsource|sse)\b', re.I)},
    {"id": "rate_limiters", "name": "Rate Limiters (Token Bucket / Leaky Bucket)", "domain": "Rede, Tráfego & APIs", "pattern": re.compile(r'\b(rate_limit|rate_limiter|ratelimit|token_bucket|leaky_bucket|express-rate-limit)\b', re.I)},
    {"id": "load_balancers", "name": "Load Balancers", "domain": "Rede, Tráfego & APIs", "pattern": re.compile(r'\b(load_balancer|loadbalancer|round_robin|least_conn|ip_hash|upstream|alb|elb)\b', re.I)},

    # 6. Observabilidade, Telemetria & Monitoramento
    {"id": "apm", "name": "Application Performance Monitoring (APM)", "domain": "Observabilidade, Telemetria & Monitoramento", "pattern": re.compile(r'\b(datadog|newrelic|elastic_apm|dynatrace|signoz|appdynamics)\b', re.I)},
    {"id": "distributed_tracing", "name": "Distributed Tracing (Trace IDs / Span IDs)", "domain": "Observabilidade, Telemetria & Monitoramento", "pattern": re.compile(r'\b(opentelemetry|otel|tracer|span_id|trace_id|jaeger|zipkin)\b', re.I)},
    {"id": "structured_logging", "name": "Structured Logging (JSON Logs)", "domain": "Observabilidade, Telemetria & Monitoramento", "pattern": re.compile(r'\b(winston|pino|zap\.logger|logrus|structlog|json_logger|bunyan)\b', re.I)},
    {"id": "log_aggregators", "name": "Log Aggregators (ELK, Loki)", "domain": "Observabilidade, Telemetria & Monitoramento", "pattern": re.compile(r'\b(loki|logstash|fluentd|fluentbit|promtail|elasticsearch_log)\b', re.I)},
    {"id": "error_trackers", "name": "Error Trackers (Sentry)", "domain": "Observabilidade, Telemetria & Monitoramento", "pattern": re.compile(r'\b(sentry|bugsnag|rollbar|raven|@sentry/)\b', re.I)},
    {"id": "time_series_metrics", "name": "Métricas de Série Temporal (Prometheus, Grafana)", "domain": "Observabilidade, Telemetria & Monitoramento", "pattern": re.compile(r'\b(prometheus|grafana|prom-client|statsd|micrometer)\b', re.I)},
    {"id": "health_check_endpoints", "name": "Health Check Endpoints (Liveness / Readiness Probes)", "domain": "Observabilidade, Telemetria & Monitoramento", "pattern": re.compile(r'\b(healthz|livez|readyz|health_check|readiness_probe|liveness_probe)\b', re.I)},

    # 7. Arquitetura Avançada & Padrões Estruturais
    {"id": "event_sourcing", "name": "Event Sourcing", "domain": "Arquitetura Avançada & Padrões Estruturais", "pattern": re.compile(r'\b(event_sourcing|eventsourcing|event_store|eventstore|apply_event|event_stream)\b', re.I)},
    {"id": "cqrs", "name": "CQRS (Command Query Responsibility Segregation)", "domain": "Arquitetura Avançada & Padrões Estruturais", "pattern": re.compile(r'\b(cqrs|command_handler|query_handler|command_bus|query_bus)\b', re.I)},
    {"id": "saga_pattern", "name": "Saga Pattern (Coreografia e Orquestração)", "domain": "Arquitetura Avançada & Padrões Estruturais", "pattern": re.compile(r'\b(saga|saga_pattern|compensating_transaction|orchestrator_saga)\b', re.I)},
    {"id": "outbox_pattern", "name": "Outbox Pattern (Garantia de entrega transacional)", "domain": "Arquitetura Avançada & Padrões Estruturais", "pattern": re.compile(r'\b(outbox|transactional_outbox|outbox_table|outbox_pattern)\b', re.I)},
    {"id": "service_mesh", "name": "Service Mesh (Istio, Linkerd)", "domain": "Arquitetura Avançada & Padrões Estruturais", "pattern": re.compile(r'\b(service_mesh|istio|linkerd|envoy|consul_mesh)\b', re.I)},
    {"id": "eda", "name": "Event-Driven Architecture (EDA)", "domain": "Arquitetura Avançada & Padrões Estruturais", "pattern": re.compile(r'\b(event_driven|event_bus|event_emitter|publish_event|subscribe_event)\b', re.I)},
    {"id": "ddd", "name": "Domain-Driven Design (DDD - Bounded Contexts, Aggregates)", "domain": "Arquitetura Avançada & Padrões Estruturais", "pattern": re.compile(r'\b(domain_driven|bounded_context|aggregate_root|value_object|domain_event|domain_service)\b', re.I)},

    # 8. Armazenamento de Arquivos, Objetos & Mídia
    {"id": "object_storage", "name": "Object Storage (S3, MinIO, Cloudflare R2)", "domain": "Armazenamento de Arquivos, Objetos & Mídia", "pattern": re.compile(r'\b(s3|aws-sdk.*s3|minio|cloudflare_r2|boto3.*s3|blob_storage)\b', re.I)},
    {"id": "presigned_urls", "name": "Presigned URLs / Signed Uploads", "domain": "Armazenamento de Arquivos, Objetos & Mídia", "pattern": re.compile(r'\b(presigned_url|getSignedUrl|signed_upload|generate_presigned_url)\b', re.I)},
    {"id": "multipart_upload", "name": "Multipart Upload Chunks", "domain": "Armazenamento de Arquivos, Objetos & Mídia", "pattern": re.compile(r'\b(multipart_upload|upload_part|createMultipartUpload|chunk_size|chunked_upload)\b', re.I)},
    {"id": "cdn_edge_caching", "name": "CDN Edge Caching (Edge Workers, Purge Rules)", "domain": "Armazenamento de Arquivos, Objetos & Mídia", "pattern": re.compile(r'\b(cloudflare|cloudfront|edge_worker|fastly|edge_cache|purge_cache)\b', re.I)},
    {"id": "video_transcoding", "name": "Video Transcoding Pipelines (FFmpeg, HLS, DASH)", "domain": "Armazenamento de Arquivos, Objetos & Mídia", "pattern": re.compile(r'\b(ffmpeg|hls|m3u8|mp4box|transcode|video_transcoding)\b', re.I)},
    {"id": "file_deduplication", "name": "Deduplicação de Arquivos (Content Hash / SHA-256)", "domain": "Armazenamento de Arquivos, Objetos & Mídia", "pattern": re.compile(r'\b(file_hash|content_hash|sha256_checksum|deduplicat|hash_dedup)\b', re.I)},

    # 9. Dados Analíticos & Big Data (OLAP vs. OLTP)
    {"id": "cdc", "name": "Change Data Capture (CDC - ex: Debezium)", "domain": "Dados Analíticos & Big Data (OLAP vs. OLTP)", "pattern": re.compile(r'\b(change_data_capture|debezium|cdc|wal2json|canal|pgoutput)\b', re.I)},
    {"id": "data_warehouses", "name": "Data Warehouses & Data Lakes (ClickHouse, BigQuery, Snowflake)", "domain": "Dados Analíticos & Big Data (OLAP vs. OLTP)", "pattern": re.compile(r'\b(clickhouse|bigquery|snowflake|redshift|datalake|datawarehouse)\b', re.I)},
    {"id": "etl_engines", "name": "Motores de ETL / ELT (Airflow, Apache Spark)", "domain": "Dados Analíticos & Big Data (OLAP vs. OLTP)", "pattern": re.compile(r'\b(airflow|spark|pyspark|dbt|glue|dag_id|etl_pipeline)\b', re.I)},
    {"id": "time_series_dbs", "name": "Time-Series Databases (TimescaleDB, InfluxDB)", "domain": "Dados Analíticos & Big Data (OLAP vs. OLTP)", "pattern": re.compile(r'\b(timescaledb|influxdb|hypertable|questdb|victoria_metrics)\b', re.I)},
    {"id": "columnar_storage", "name": "Columnar Storage (Parquet, ORC)", "domain": "Dados Analíticos & Big Data (OLAP vs. OLTP)", "pattern": re.compile(r'\b(parquet|pyarrow|fastparquet|orc|columnar)\b', re.I)},
    {"id": "embeddable_bi", "name": "Visualização & BI Embeddable", "domain": "Dados Analíticos & Big Data (OLAP vs. OLTP)", "pattern": re.compile(r'\b(metabase|superset|tableau|looker|grafana_embed|cube\.js)\b', re.I)},

    # 10. Nuvem, Orquestração & Runtime
    {"id": "containerization", "name": "Containerização (Docker, Podman)", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(docker|dockerfile|podman|containerd|crun|runc)\b', re.I)},
    {"id": "container_orchestrators", "name": "Orquestradores de Containers (Kubernetes / K8s, Docker Swarm)", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(kubernetes|k8s|kubectl|docker-swarm|swarm_mode|pod_spec)\b', re.I)},
    {"id": "helm_kustomize", "name": "Helm Charts & Kustomize", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(helm|chart\.yaml|kustomize|kustomization\.yaml|values\.yaml)\b', re.I)},
    {"id": "process_managers", "name": "Process Managers (PM2, Systemd)", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(pm2|systemd|supervisord|systemctl|ecosystem\.config)\b', re.I)},
    {"id": "ingress_controllers", "name": "Ingress Controllers & Service Discovery", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(ingress|ingress_controller|traefik_ingress|nginx_ingress|service_discovery|consul)\b', re.I)},
    {"id": "iac", "name": "Infrastructure as Code (IaC - Terraform, Ansible, Pulumi)", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(terraform|ansible|pulumi|cloudformation|terragrunt)\b', re.I)},
    {"id": "serverless", "name": "Serverless & FaaS Runtimes (Lambda, Cloudflare Workers)", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(serverless|aws_lambda|lambda_handler|cloudflare_worker|google_cloud_functions)\b', re.I)},
    {"id": "autoscaling", "name": "Auto-Scaling Groups (HPA - Horizontal Pod Autoscaler)", "domain": "Nuvem, Orquestração & Runtime", "pattern": re.compile(r'\b(horizontalpodautoscaler|hpa|autoscaling|auto_scaler|scale_target_ref)\b', re.I)},

    # 11. Rede Baixo Nível & Comunicação
    {"id": "raw_sockets", "name": "Sockets TCP/UDP Puros", "domain": "Rede Baixo Nível & Comunicação", "pattern": re.compile(r'\b(net\.createServer|socket\.socket|socket\.AF_INET|net\.Socket|tokio::net::TcpStream)\b', re.I)},
    {"id": "tls_handshake", "name": "TLS Handshake & Certificados SSL Auto-Renováveis (Let\'s Encrypt / ACME)", "domain": "Rede Baixo Nível & Comunicação", "pattern": re.compile(r'\b(letsencrypt|certbot|acme|auto_tls|tls_config|self_signed)\b', re.I)},
    {"id": "http2_quic", "name": "Multiplexação HTTP/2 e QUIC (HTTP/3)", "domain": "Rede Baixo Nível & Comunicação", "pattern": re.compile(r'\b(http2|http/2|http3|http/3|quic|alpn|spdy)\b', re.I)},
    {"id": "dns_anycast", "name": "Resolução DNS Anycast", "domain": "Rede Baixo Nível & Comunicação", "pattern": re.compile(r'\b(anycast|dns_resolver|route53|cloudflare_dns|authoritative_dns)\b', re.I)},
    {"id": "bgp_routing", "name": "BGP Anycast Routing", "domain": "Rede Baixo Nível & Comunicação", "pattern": re.compile(r'\b(bgp|bgp_routing|autonomous_system|as_path|bird_bgp)\b', re.I)},
    {"id": "vpc_networking", "name": "Virtual Private Cloud (VPC), Subnets, NAT Gateways", "domain": "Rede Baixo Nível & Comunicação", "pattern": re.compile(r'\b(vpc|subnet|nat_gateway|internet_gateway|route_table)\b', re.I)},
    {"id": "mesh_vpns", "name": "VPNs & Mesh Networks (Tailscale, WireGuard)", "domain": "Rede Baixo Nível & Comunicação", "pattern": re.compile(r'\b(wireguard|tailscale|zerotier|openvpn|ipsec)\b', re.I)},

    # 12. Entrega Contínua & DevOps (CI/CD)
    {"id": "ci_cd_pipelines", "name": "CI/CD Pipelines (GitHub Actions, GitLab CI)", "domain": "Entrega Contínua & DevOps (CI/CD)", "pattern": re.compile(r'\b(github/workflows|gitlab-ci|\.circleci|travis\.yml|pipeline_job)\b', re.I)},
    {"id": "blue_green_deploy", "name": "Blue-Green Deployments", "domain": "Entrega Contínua & DevOps (CI/CD)", "pattern": re.compile(r'\b(blue_green|bluegreen|traffic_split|switch_active_deployment)\b', re.I)},
    {"id": "canary_deploy", "name": "Canary Deployments", "domain": "Entrega Contínua & DevOps (CI/CD)", "pattern": re.compile(r'\b(canary|canary_release|canary_deployment|progressive_delivery|flagger)\b', re.I)},
    {"id": "feature_flags", "name": "Feature Flags / Toggles (LaunchDarkly, Unleash)", "domain": "Entrega Contínua & DevOps (CI/CD)", "pattern": re.compile(r'\b(feature_flag|launchdarkly|unleash|feature_toggle|flagsmith|growthbook)\b', re.I)},
    {"id": "gitops", "name": "GitOps (ArgoCD, Flux)", "domain": "Entrega Contínua & DevOps (CI/CD)", "pattern": re.compile(r'\b(argocd|argo_cd|fluxcd|gitops|sync_policy)\b', re.I)},
    {"id": "chaos_engineering", "name": "Chaos Engineering (Chaos Monkey)", "domain": "Entrega Contínua & DevOps (CI/CD)", "pattern": re.compile(r'\b(chaos_monkey|chaos_engineering|gremlin|litmus_chaos)\b', re.I)},
    {"id": "auto_rollback", "name": "Rollback Engines Automáticos", "domain": "Entrega Contínua & DevOps (CI/CD)", "pattern": re.compile(r'\b(auto_rollback|automated_rollback|rollback_on_failure|rollback_trigger)\b', re.I)},

    # 13. IA, Vetores & Busca Semântica Moderna
    {"id": "vector_dbs", "name": "Vector Databases (Qdrant, Pinecone, Milvus, pgvector)", "domain": "IA, Vetores & Busca Semântica Moderna", "pattern": re.compile(r'\b(qdrant|pinecone|milvus|pgvector|chromadb|weaviate)\b', re.I)},
    {"id": "embeddings_engines", "name": "Embeddings Engines", "domain": "IA, Vetores & Busca Semântica Moderna", "pattern": re.compile(r'\b(text-embedding|embeddings|sentence_transformers|openai\.embeddings|all-MiniLM)\b', re.I)},
    {"id": "rag_pipelines", "name": "RAG Pipelines (Retrieval-Augmented Generation)", "domain": "IA, Vetores & Busca Semântica Moderna", "pattern": re.compile(r'\b(retrieval_augmented|rag_pipeline|rag_chain|vector_search|retriever)\b', re.I)},
    {"id": "llm_orchestrators", "name": "Tokenizers & LLM Orchestrators (LangChain, LlamaIndex)", "domain": "IA, Vetores & Busca Semântica Moderna", "pattern": re.compile(r'\b(langchain|llamaindex|langgraph|tiktoken|huggingface)\b', re.I)},
    {"id": "prompt_caches", "name": "Prompt Caches & Semantic Caching", "domain": "IA, Vetores & Busca Semântica Moderna", "pattern": re.compile(r'\b(prompt_cache|semantic_cache|gptcache|prompt_caching)\b', re.I)},

    # 14. Sistema Operacional & Kernel (O Chão de Fábrica)
    {"id": "kernel_syscalls", "name": "Linux Kernels & Syscalls (epoll, kqueue, io_uring)", "domain": "Sistema Operacional & Kernel (O Chão de Fábrica)", "pattern": re.compile(r'\b(epoll|kqueue|io_uring|syscall|posix|libc)\b', re.I)},
    {"id": "file_descriptors", "name": "File Descriptors & Inodes", "domain": "Sistema Operacional & Kernel (O Chão de Fábrica)", "pattern": re.compile(r'\b(file_descriptor|fileno|inode|ulimit|rlimit_nofile|max_open_files)\b', re.I)},
    {"id": "shared_memory", "name": "Shared Memory Segments (shm)", "domain": "Sistema Operacional & Kernel (O Chão de Fábrica)", "pattern": re.compile(r'\b(shm_open|shmget|mmap|shared_memory|ipc_rmid)\b', re.I)},
    {"id": "swap_paging", "name": "SWAP & Memory Paging", "domain": "Sistema Operacional & Kernel (O Chão de Fábrica)", "pattern": re.compile(r'\b(swap|vm\.swappiness|page_fault|swap_space|overcommit_memory)\b', re.I)},
    {"id": "oom_killer", "name": "OOM Killer (Out-of-Memory Killer)", "domain": "Sistema Operacional & Kernel (O Chão de Fábrica)", "pattern": re.compile(r'\b(oom_killer|oom_score_adj|out_of_memory|dmesg.*killed_process)\b', re.I)},
    {"id": "process_isolation", "name": "Process Isolation (cgroups, Linux Namespaces, SELinux)", "domain": "Sistema Operacional & Kernel (O Chão de Fábrica)", "pattern": re.compile(r'\b(cgroups|cgroup|namespaces|selinux|apparmor|unshare)\b', re.I)},

    # 15. Compliance, Governança & Retenção
    {"id": "data_anonymization", "name": "Data Anonymization & Masking (LGPD / GDPR)", "domain": "Compliance, Governança & Retenção", "pattern": re.compile(r'\b(lgpd|gdpr|anonymiz|data_masking|pseudonymiz|pii_sanitiz)\b', re.I)},
    {"id": "data_retention_purge", "name": "Motores de Retenção e Purga Automática de Dados", "domain": "Compliance, Governança & Retenção", "pattern": re.compile(r'\b(data_retention|retention_policy|auto_purge|purge_old_records|ttl_index)\b', re.I)},
    {"id": "pci_dss_tokenizers", "name": "PCI-DSS Compliance Tokenizers (para cartões de crédito)", "domain": "Compliance, Governança & Retenção", "pattern": re.compile(r'\b(pci_dss|tokeniz.*card|card_token|pan_masking|luhn)\b', re.I)},
    {"id": "disaster_recovery", "name": "Disaster Recovery (RTO - Recovery Time Objective / RPO - Recovery Point Objective)", "domain": "Compliance, Governança & Retenção", "pattern": re.compile(r'\b(disaster_recovery|recovery_time_objective|recovery_point_objective|rto|rpo)\b', re.I)},
    {"id": "pitr_recovery", "name": "Automated Snapshotting & Point-In-Time Recovery (PITR)", "domain": "Compliance, Governança & Retenção", "pattern": re.compile(r'\b(point_in_time|pitr|automated_snapshot|backup_restore|wal_archive)\b', re.I)},

    # 16. Consenso Distribuído & Algoritmos de Estado
    {"id": "raft_consensus", "name": "Raft Consensus", "domain": "Consenso Distribuído & Algoritmos de Estado", "pattern": re.compile(r'\b(raft|raft_consensus|etcd|hashicorp/raft|leader_election)\b', re.I)},
    {"id": "paxos_consensus", "name": "Paxos / Multi-Paxos", "domain": "Consenso Distribuído & Algoritmos de Estado", "pattern": re.compile(r'\b(paxos|multi_paxos|proposer|acceptor|zookeeper)\b', re.I)},
    {"id": "crdts", "name": "CRDTs (Conflict-free Replicated Data Types)", "domain": "Consenso Distribuído & Algoritmos de Estado", "pattern": re.compile(r'\b(crdt|yjs|automerge|conflict_free)\b', re.I)},
    {"id": "vector_clocks", "name": "Vector Clocks & Lamport Timestamps", "domain": "Consenso Distribuído & Algoritmos de Estado", "pattern": re.compile(r'\b(vector_clock|lamport_timestamp|logical_clock)\b', re.I)},
    {"id": "gossip_protocol", "name": "Gossip Protocol", "domain": "Consenso Distribuído & Algoritmos de Estado", "pattern": re.compile(r'\b(gossip|memberlist|gossip_protocol|swim_protocol)\b', re.I)},
    {"id": "two_phase_commit", "name": "Two-Phase Commit (2PC / 3PC)", "domain": "Consenso Distribuído & Algoritmos de Estado", "pattern": re.compile(r'\b(two_phase_commit|2pc|3pc|distributed_transaction)\b', re.I)},
    {"id": "quorum_reads_writes", "name": "Quorum Reads / Writes", "domain": "Consenso Distribuído & Algoritmos de Estado", "pattern": re.compile(r'\b(quorum|read_quorum|write_quorum|majority_vote)\b', re.I)},

    # 17. Compiladores, Runtimes & Gerenciamento de Memória
    {"id": "jit_compilers", "name": "JIT Compilers (Just-In-Time)", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(jit|just_in_time|turbofan|luajit|pypy)\b', re.I)},
    {"id": "garbage_collection", "name": "Garbage Collection (ZGC, Generational GC, Mark-and-Sweep)", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(garbage_collect|zgc|shenandoah|mark_and_sweep|gc_cycle)\b', re.I)},
    {"id": "heap_memory_dump", "name": "Call Stack & Heap Memory", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(call_stack|heap_memory|stack_overflow|heap_dump|max_old_space_size)\b', re.I)},
    {"id": "wasm_runtimes", "name": "WebAssembly (Wasm) Runtimes", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(webassembly|wasm|wasmer|wasmtime|emscripten)\b', re.I)},
    {"id": "v8_engine", "name": "V8 Engine Pipelines", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(v8|ignition|turbofan|node_v8)\b', re.I)},
    {"id": "llvm_ir", "name": "LLVM IR (Intermediate Representation)", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(llvm|llvm_ir|clang|llvmlite)\b', re.I)},
    {"id": "thread_pools_green", "name": "Thread Pools & Green Threads / Coroutines / Fibers", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(thread_pool|coroutine|greenlet|goroutine|fibers|asyncio)\b', re.I)},
    {"id": "atomic_operations", "name": "Atomic Operations & Memory Barriers", "domain": "Compiladores, Runtimes & Gerenciamento de Memória", "pattern": re.compile(r'\b(atomic|compare_and_swap|memory_barrier|atomics|interlocked)\b', re.I)},

    # 18. Segurança Ofensiva, Defensiva & Kernel Hardening
    {"id": "ebpf", "name": "eBPF (Extended Berkeley Packet Filter)", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(ebpf|bpf_program|cilium|bcc|libbpf)\b', re.I)},
    {"id": "waf", "name": "WAF (Web Application Firewall)", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(waf|modsecurity|coraza|cloudflare_waf|aws_waf)\b', re.I)},
    {"id": "ddos_scrubbing", "name": "DDoS Scrubbing Centers", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(ddos|scrubbing|rate_limiting|ddos_protection|syn_flood)\b', re.I)},
    {"id": "mtls_zero_trust", "name": "mTLS (Mutual TLS / Zero-Trust Network)", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(mtls|mutual_tls|client_certificate|zero_trust|spiffe)\b', re.I)},
    {"id": "aslr", "name": "ASLR (Address Space Layout Randomization)", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(aslr|pie|relro|stack_canary)\b', re.I)},
    {"id": "seccomp_filters", "name": "Seccomp Filters", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(seccomp|seccomp_bpf|secure_computing)\b', re.I)},
    {"id": "csp_hsts", "name": "CSP (Content Security Policy) & HSTS", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(content-security-policy|strict-transport-security|hsts|csp)\b', re.I)},
    {"id": "hsm_hardware", "name": "Hardware Security Modules (HSM)", "domain": "Segurança Ofensiva, Defensiva & Kernel Hardening", "pattern": re.compile(r'\b(hsm|pkcs11|hardware_security_module|cloudhsm)\b', re.I)},

    # 19. Hardware, Silício & Barramentos
    {"id": "cpu_cache_lines", "name": "CPU Cache Lines (L1, L2, L3)", "domain": "Hardware, Silício & Barramentos", "pattern": re.compile(r'\b(cache_line|cache_miss|l1_cache|l2_cache|l3_cache|false_sharing)\b', re.I)},
    {"id": "branch_predictors", "name": "Branch Predictors", "domain": "Hardware, Silício & Barramentos", "pattern": re.compile(r'\b(branch_predictor|likely|unlikely|branch_prediction)\b', re.I)},
    {"id": "numa_arch", "name": "NUMA Architecture (Non-Uniform Memory Access)", "domain": "Hardware, Silício & Barramentos", "pattern": re.compile(r'\b(numa|numactl|numa_node|libnuma)\b', re.I)},
    {"id": "dma_access", "name": "Direct Memory Access (DMA)", "domain": "Hardware, Silício & Barramentos", "pattern": re.compile(r'\b(dma|direct_memory_access|dma_buffer)\b', re.I)},
    {"id": "nvme_fabrics", "name": "NVMe Over Fabrics (NVMe-oF)", "domain": "Hardware, Silício & Barramentos", "pattern": re.compile(r'\b(nvme|nvme_of|rdma|roce)\b', re.I)},
    {"id": "gpu_compute", "name": "GPU Compute Engines (CUDA Cores / Tensor Cores)", "domain": "Hardware, Silício & Barramentos", "pattern": re.compile(r'\b(cuda|tensorrt|cudnn|gpu_device|torch\.cuda)\b', re.I)},
    {"id": "fpga_asics", "name": "FPGA / ASICs de Alta Frequência", "domain": "Hardware, Silício & Barramentos", "pattern": re.compile(r'\b(fpga|asic|verilog|vhdl|high_frequency)\b', re.I)},

    # 20. Motores Financeiros & Billing (FinOps)
    {"id": "double_entry_bookkeeping", "name": "Double-Entry Bookkeeping Engines (Razão Contábil de Partidas Dobradas)", "domain": "Motores Financeiros & Billing (FinOps)", "pattern": re.compile(r'\b(double_entry|partidas_dobradas|ledger|debit.*credit|chart_of_accounts)\b', re.I)},
    {"id": "metering_engines", "name": "Metering Engines (Tarifação granular por token, payload ou milissegundo)", "domain": "Motores Financeiros & Billing (FinOps)", "pattern": re.compile(r'\b(metering|usage_based|tier_pricing|token_usage|pay_per_use)\b', re.I)},
    {"id": "dunning_management", "name": "Dunning Management (Motores de recuperação de inadimplência)", "domain": "Motores Financeiros & Billing (FinOps)", "pattern": re.compile(r'\b(dunning|payment_retry|inadimplencia|failed_invoice|retry_schedule)\b', re.I)},
    {"id": "proration_engines", "name": "Proration Engines (Cálculo proporcional de planos/upgrades)", "domain": "Motores Financeiros & Billing (FinOps)", "pattern": re.compile(r'\b(proration|prorate|pro_rata|subscription_upgrade)\b', re.I)},
    {"id": "bank_reconciliation", "name": "Reconciliação Bancária Automatizada", "domain": "Motores Financeiros & Billing (FinOps)", "pattern": re.compile(r'\b(bank_reconciliation|reconcilia|ofx|cnab|reconciliation_engine)\b', re.I)},

    # 21. Criptografia Avançada & Provas Matemáticas
    {"id": "zk_proofs", "name": "Zero-Knowledge Proofs (zk-SNARKs, zk-STARKs)", "domain": "Criptografia Avançada & Provas Matemáticas", "pattern": re.compile(r'\b(zk-snark|zk-stark|zero_knowledge|snarkjs|circom|halo2)\b', re.I)},
    {"id": "homomorphic_enc", "name": "Homomorphic Encryption (FHE)", "domain": "Criptografia Avançada & Provas Matemáticas", "pattern": re.compile(r'\b(homomorphic|fhe|seal|tenseal|openfhe)\b', re.I)},
    {"id": "elliptic_curves", "name": "Elliptic Curve Cryptography (Ed25519, Secp256k1)", "domain": "Criptografia Avançada & Provas Matemáticas", "pattern": re.compile(r'\b(ed25519|secp256k1|ecdsa|curve25519)\b', re.I)},
    {"id": "post_quantum", "name": "Post-Quantum Cryptography (Lattice-based cryptography / Kyber)", "domain": "Criptografia Avançada & Provas Matemáticas", "pattern": re.compile(r'\b(kyber|post_quantum|dilithium|lattice_cryptography|sphincs)\b', re.I)},
    {"id": "shamir_secret", "name": "Shamir’s Secret Sharing", "domain": "Criptografia Avançada & Provas Matemáticas", "pattern": re.compile(r'\b(shamir|secret_sharing|threshold_cryptography)\b', re.I)},
    {"id": "merkle_trees", "name": "Merkle Trees & Patricia Tries", "domain": "Criptografia Avançada & Provas Matemáticas", "pattern": re.compile(r'\b(merkle|merkle_tree|merkle_root|patricia_trie)\b', re.I)},
    {"id": "diffie_hellman", "name": "Diffie-Hellman Key Exchange (ECDH)", "domain": "Criptografia Avançada & Provas Matemáticas", "pattern": re.compile(r'\b(diffie_hellman|ecdh|key_exchange|x25519)\b', re.I)},

    # 22. Firmware, BIOS & Bootstrapping
    {"id": "uefi_secureboot", "name": "UEFI / Secure Boot", "domain": "Firmware, BIOS & Bootstrapping", "pattern": re.compile(r'\b(uefi|secure_boot|efibootmgr|ovmf)\b', re.I)},
    {"id": "coreboot_libreboot", "name": "Coreboot / Libreboot", "domain": "Firmware, BIOS & Bootstrapping", "pattern": re.compile(r'\b(coreboot|libreboot|flashrom)\b', re.I)},
    {"id": "intel_me_amd_psp", "name": "Intel ME (Management Engine) / AMD PSP (Platform Security Processor)", "domain": "Firmware, BIOS & Bootstrapping", "pattern": re.compile(r'\b(intel_me|amd_psp|management_engine|me_cleaner)\b', re.I)},
    {"id": "ipmi_bmc", "name": "IPMI / BMC (Baseboard Management Controller / iDRAC / iLO)", "domain": "Firmware, BIOS & Bootstrapping", "pattern": re.compile(r'\b(ipmi|bmc|idrac|ilo|ipmitool)\b', re.I)},
    {"id": "bootloaders", "name": "Bootloaders (GRUB, systemd-boot)", "domain": "Firmware, BIOS & Bootstrapping", "pattern": re.compile(r'\b(grub|systemd-boot|bootloader|grub\.cfg)\b', re.I)},
    {"id": "microcode_updates", "name": "Microcode Updates", "domain": "Firmware, BIOS & Bootstrapping", "pattern": re.compile(r'\b(microcode|intel-microcode|amd-microcode)\b', re.I)},
    {"id": "rtc_ptp_clock", "name": "Real-Time Clocks (RTC) & PTP (Precision Time Protocol / IEEE 1588)", "domain": "Firmware, BIOS & Bootstrapping", "pattern": re.compile(r'\b(real_time_clock|rtc|ptp|ieee_1588|precision_time)\b', re.I)},

    # 23. Sistemas de Arquivos & Estruturas de Armazenamento
    {"id": "lsm_trees", "name": "LSM-Trees (Log-Structured Merge-Trees)", "domain": "Sistemas de Arquivos & Estruturas de Armazenamento", "pattern": re.compile(r'\b(lsm_tree|rocksdb|leveldb|sstable|memtable)\b', re.I)},
    {"id": "b_plus_trees", "name": "B+ Trees & Fractal Trees", "domain": "Sistemas de Arquivos & Estruturas de Armazenamento", "pattern": re.compile(r'\b(b_plus_tree|btree|fractal_tree|tokudb)\b', re.I)},
    {"id": "zfs_btrfs", "name": "ZFS & Btrfs (Copy-on-Write, Snapshots, Scrubbing)", "domain": "Sistemas de Arquivos & Estruturas de Armazenamento", "pattern": re.compile(r'\b(zfs|btrfs|copy_on_write|scrubbing|zpool)\b', re.I)},
    {"id": "distributed_fs", "name": "Distributed File Systems (Ceph, GlusterFS, Lustre)", "domain": "Sistemas de Arquivos & Estruturas de Armazenamento", "pattern": re.compile(r'\b(ceph|glusterfs|lustre|hdfs|rook)\b', re.I)},
    {"id": "wal_logging", "name": "WAL (Write-Ahead Logging)", "domain": "Sistemas de Arquivos & Estruturas de Armazenamento", "pattern": re.compile(r'\b(write_ahead_log|wal|pg_wal|wal_level)\b', re.I)},
    {"id": "mmap_files", "name": "Memory-Mapped Files (mmap)", "domain": "Sistemas de Arquivos & Estruturas de Armazenamento", "pattern": re.compile(r'\b(mmap|mprotect|memory_map|file_mapping)\b', re.I)},
    {"id": "block_devices_nvme", "name": "Block Devices & NVMe Queues", "domain": "Sistemas de Arquivos & Estruturas de Armazenamento", "pattern": re.compile(r'\b(block_device|lsblk|fdisk|nvme_queue|io_depth)\b', re.I)},

    # 24. Serialização & Protocolos Binários de Alta Performance
    {"id": "protobuf", "name": "Protocol Buffers (Protobuf)", "domain": "Serialização & Protocolos Binários de Alta Performance", "pattern": re.compile(r'\b(protobuf|protocol_buffers|protoc|\.proto\b|pbjs)\b', re.I)},
    {"id": "flatbuffers", "name": "FlatBuffers & Cap\'n Proto (Zero-copy deserialization)", "domain": "Serialização & Protocolos Binários de Alta Performance", "pattern": re.compile(r'\b(flatbuffers|capnproto|zero_copy|flatc)\b', re.I)},
    {"id": "apache_avro", "name": "Apache Avro", "domain": "Serialização & Protocolos Binários de Alta Performance", "pattern": re.compile(r'\b(avro|schema\.avsc|apache_avro)\b', re.I)},
    {"id": "msgpack_cbor", "name": "MessagePack & CBOR", "domain": "Serialização & Protocolos Binários de Alta Performance", "pattern": re.compile(r'\b(msgpack|messagepack|cbor|cbor-js)\b', re.I)},
    {"id": "asn1_spec", "name": "ASN.1", "domain": "Serialização & Protocolos Binários de Alta Performance", "pattern": re.compile(r'\b(asn1|der_decode|ber_decode)\b', re.I)},
    {"id": "apache_arrow", "name": "Apache Arrow (In-memory columnar format)", "domain": "Serialização & Protocolos Binários de Alta Performance", "pattern": re.compile(r'\b(apache_arrow|pyarrow|feather|arrow_table)\b', re.I)},

    # 25. Telecomunicações, Roteamento Core & Camada Física
    {"id": "bgp_peering_asn", "name": "BGP Peering & Autonomous Systems (ASN)", "domain": "Telecomunicações, Roteamento Core & Camada Física", "pattern": re.compile(r'\b(bgp_peering|asn|bird|frr|quagga|autonomous_system)\b', re.I)},
    {"id": "mpls_routing", "name": "MPLS (Multiprotocol Label Switching)", "domain": "Telecomunicações, Roteamento Core & Camada Física", "pattern": re.compile(r'\b(mpls|label_switched_path|rsvp-te)\b', re.I)},
    {"id": "dwdm_optical", "name": "DWDM (Dense Wavelength Division Multiplexing - Redes Ópticas)", "domain": "Telecomunicações, Roteamento Core & Camada Física", "pattern": re.compile(r'\b(dwdm|optical_network|wavelength)\b', re.I)},
    {"id": "sr_iov_virt", "name": "SR-IOV (Single Root I/O Virtualization)", "domain": "Telecomunicações, Roteamento Core & Camada Física", "pattern": re.compile(r'\b(sr_iov|virtual_function|physical_function)\b', re.I)},
    {"id": "dpdk_bypass", "name": "DPDK (Data Plane Development Kit - Bypass de Kernel)", "domain": "Telecomunicações, Roteamento Core & Camada Física", "pattern": re.compile(r'\b(dpdk|kernel_bypass|rte_eal|hugepages)\b', re.I)},
    {"id": "jumbo_frames_mtu", "name": "Jumbo Frames & MTU Discovery", "domain": "Telecomunicações, Roteamento Core & Camada Física", "pattern": re.compile(r'\b(jumbo_frames|mtu_9000|mtu_discovery)\b', re.I)},
    {"id": "pdu_ups_redundancy", "name": "PDU / UPS Redundancy Engines (Nível Datacenter)", "domain": "Telecomunicações, Roteamento Core & Camada Física", "pattern": re.compile(r'\b(pdu|ups|snmp_ups|apc_ups|nut_ups)\b', re.I)},

    # 26. Redes P2P & Arquiteturas Descentralizadas
    {"id": "kademlia_dht", "name": "Distributed Hash Tables (Kademlia DHT)", "domain": "Redes P2P & Arquiteturas Descentralizadas", "pattern": re.compile(r'\b(kademlia|dht|routing_table|node_id)\b', re.I)},
    {"id": "libp2p_stack", "name": "Libp2p", "domain": "Redes P2P & Arquiteturas Descentralizadas", "pattern": re.compile(r'\b(libp2p|multiaddr|peer_id|swarm_listener)\b', re.I)},
    {"id": "gossipsub_protocol", "name": "Gossipsub", "domain": "Redes P2P & Arquiteturas Descentralizadas", "pattern": re.compile(r'\b(gossipsub|floodsub|pubsub_peer)\b', re.I)},
    {"id": "bittorrent_protocol", "name": "BitTorrent Wire Protocol", "domain": "Redes P2P & Arquiteturas Descentralizadas", "pattern": re.compile(r'\b(bittorrent|torrent|peer_wire|bencode|info_hash)\b', re.I)},
    {"id": "hole_punching", "name": "Hole Punching (STUN, TURN, ICE)", "domain": "Redes P2P & Arquiteturas Descentralizadas", "pattern": re.compile(r'\b(stun|turn|ice_servers|hole_punching|webrtc)\b', re.I)},
    {"id": "nat_pmp_upnp", "name": "Nat-PMP / UPnP Traversal", "domain": "Redes P2P & Arquiteturas Descentralizadas", "pattern": re.compile(r'\b(nat_pmp|upnp|igd|port_mapping)\b', re.I)},

    # 27. Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)
    {"id": "slo_sla_sli", "name": "SLOs (Service Level Objectives) & SLAs / SLIs", "domain": "Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)", "pattern": re.compile(r'\b(slo|sla|sli|service_level_objective|sloth|pyrra)\b', re.I)},
    {"id": "error_budgets", "name": "Error Budgets", "domain": "Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)", "pattern": re.compile(r'\b(error_budget|budget_consumption|burn_rate)\b', re.I)},
    {"id": "deadlock_detectors", "name": "Distributed Deadlock Detectors", "domain": "Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)", "pattern": re.compile(r'\b(deadlock_detector|wait_for_graph|deadlock_prevention)\b', re.I)},
    {"id": "synthetic_probes", "name": "Synthetic Monitoring Probes", "domain": "Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)", "pattern": re.compile(r'\b(synthetic_monitoring|blackbox_exporter|uptime_kuma|ping_probe)\b', re.I)},
    {"id": "flame_graphs_heap", "name": "Heap Dump Analyzers & Flame Graphs", "domain": "Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)", "pattern": re.compile(r'\b(flame_graph|flamegraph|heap_dump|heap_profile|async_profiler)\b', re.I)},
    {"id": "continuous_profilers", "name": "Continuous Profilers (Pyroscope, Parca)", "domain": "Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)", "pattern": re.compile(r'\b(pyroscope|parca|continuous_profiling)\b', re.I)},
    {"id": "burn_rate_alerts", "name": "Burn Rate Alerts", "domain": "Engenharia de Resiliência & Métricas de Negócio (SRE / Observability 2.0)", "pattern": re.compile(r'\b(burn_rate_alert|multiwindow_multi_burn_rate)\b', re.I)},

    # 28. Proteção de Dados, Cartões & PCI
    {"id": "credit_cards", "name": "Cartões de Crédito", "domain": "Proteção de Dados, Cartões & PCI", "pattern": re.compile(r'\b(cartao|credit_card|creditcard|cc_num|card_number|pan|cvv|cvv2|track1|track2|carding|ccdumps)\b', re.I)},
    {"id": "financial_data", "name": "Dados Financeiros", "domain": "Proteção de Dados, Cartões & PCI", "pattern": re.compile(r'\b(financial_data|bank_account|routing_number|iban|swift|conta_bancaria|agencia_bancaria|transfers\.csv)\b', re.I)},
    {"id": "crypto_wallets", "name": "Carteiras Criptográficas", "domain": "Proteção de Dados, Cartões & PCI", "pattern": re.compile(r'\b(bitcoin_wallet|ethereum_wallet|monero_wallet|crypto_wallet|private_key|seed_phrase|bip39|xmr|btc|eth_address)\b', re.I)},
    {"id": "escrow_data", "name": "Dados de Escrow", "domain": "Proteção de Dados, Cartões & PCI", "pattern": re.compile(r'\b(escrow|escrow_data|escrow_agent|multisig_escrow|arbitrator|custody_contract)\b', re.I)},
    {"id": "transactions_data", "name": "Transações", "domain": "Proteção de Dados, Cartões & PCI", "pattern": re.compile(r'\b(transaction_id|txid|deal_info|trade_details|payment_intent|charge_id)\b', re.I)},

    # 29. Credenciais, Segredos & Gestão de Acesso
    {"id": "api_tokens_concept", "name": "Tokens de API", "domain": "Credenciais, Segredos & Gestão de Acesso", "pattern": re.compile(r'\b(api_token|api_key|access_token|bearer_token|x-api-key|secret_key)\b', re.I)},
    {"id": "access_keys_concept", "name": "Chaves de Acesso", "domain": "Credenciais, Segredos & Gestão de Acesso", "pattern": re.compile(r'\b(access_key|secret_access|aws_secret|private_key|access_key_id)\b', re.I)},
    {"id": "passwords_concept", "name": "Senhas", "domain": "Credenciais, Segredos & Gestão de Acesso", "pattern": re.compile(r'\b(password|passwd|pwd|passwords\.txt|user_password|secret_phrase)\b', re.I)},
    {"id": "login_info_concept", "name": "Informações de Login", "domain": "Credenciais, Segredos & Gestão de Acesso", "pattern": re.compile(r'\b(logins\.txt|login_details|account_info|user_data|login_credentials)\b', re.I)},
    {"id": "pgp_keys_concept", "name": "Chaves PGP", "domain": "Credenciais, Segredos & Gestão de Acesso", "pattern": re.compile(r'\b(pgp|gpg|keyring|pgp\.keyring|pubkey|armored_key|secring)\b', re.I)},
    {"id": "security_certs_concept", "name": "Certificados de Segurança", "domain": "Credenciais, Segredos & Gestão de Acesso", "pattern": re.compile(r'\b(ssl_certs|cert\.pem|keys\.pem|certs\.db|certs\.json|x509_certificate)\b', re.I)},
    {"id": "access_rules_concept", "name": "Regras de Acesso", "domain": "Credenciais, Segredos & Gestão de Acesso", "pattern": re.compile(r'\b(rules\.txt|access_rules|firewall_rules|security_group|iptables_rule|acl_rule)\b', re.I)},

    # 30. Metadados, Servidores & Configurações
    {"id": "server_configs_concept", "name": "Configurações de Servidor", "domain": "Metadados, Servidores & Configurações", "pattern": re.compile(r'\b(server_config|proxy_config|torrc|caddyfile|nginx\.conf|config\.yml)\b', re.I)},
    {"id": "metadata_concept", "name": "Metadados", "domain": "Metadados, Servidores & Configurações", "pattern": re.compile(r'\b(metadata\.json|site_metadata|exif|opengraph|dublin_core|meta_tags)\b', re.I)},
    {"id": "manifests_concept", "name": "Manifestos", "domain": "Metadados, Servidores & Configurações", "pattern": re.compile(r'\b(manifest\.json|app_manifest|webmanifest|k8s_manifest|deployment_manifest)\b', re.I)},

    # 31. Mídia, Anotações & Conteúdo
    {"id": "images_concept", "name": "Imagens", "domain": "Mídia, Anotações & Conteúdo", "pattern": re.compile(r'\b(images/|png|jpg|jpeg|webp|svg|gif|image_assets)\b', re.I)},
    {"id": "multimedia_concept", "name": "Arquivos Multimídia", "domain": "Mídia, Anotações & Conteúdo", "pattern": re.compile(r'\b(videos/|audios/|media/|mp4|webm|mp3|wav|streaming_media)\b', re.I)},
    {"id": "notes_concept", "name": "Arquivos de Anotações", "domain": "Mídia, Anotações & Conteúdo", "pattern": re.compile(r'\b(notes\.txt|readme\.txt|scratchpad|annotation|meeting_notes)\b', re.I)},
    {"id": "diaries_concept", "name": "Diários", "domain": "Mídia, Anotações & Conteúdo", "pattern": re.compile(r'\b(journal\.txt|diary\.json|daily_log|developer_journal)\b', re.I)},
    {"id": "memos_concept", "name": "Memos", "domain": "Mídia, Anotações & Conteúdo", "pattern": re.compile(r'\b(memos\.txt|memo|memorandum|internal_memo)\b', re.I)}
]

# ══════════════════════════════════════════════════════════════════════════════
# INVENTÁRIO DE ARQUIVOS ESTRUTURAIS & CANÔNICOS (18 Categorias, 160+ Arquivos)
# ══════════════════════════════════════════════════════════════════════════════
STRUCTURAL_FILES_CATEGORIES = [
    {
        "category": "1. Configuração de Raiz, Ambiente & Dependências",
        "entries": [
            ".env", ".env.example", ".env.production", ".gitignore", ".editorconfig", ".dockerignore",
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "go.mod", "go.sum",
            "Cargo.toml", "Cargo.lock", "requirements.txt", "pyproject.toml", "Pipfile.lock", "Makefile",
            "tsconfig.json", "ecosystem.config.js"
        ]
    },
    {
        "category": "2. Dados Financeiros, Cartões de Crédito & PCI",
        "entries": [
            "cards.txt", "ccdumps.txt", "carding.txt", "cardinfo.json", "cards.db",
            "banks.txt", "financial_data.json", "transfers.csv", "account_details.txt"
        ]
    },
    {
        "category": "3. Credenciais, Tokens, Senhas & Logins",
        "entries": [
            "tokens.txt", "api_keys.txt", "secrets.txt", "auth.txt", "credentials.json",
            "config.json", "keys.txt", "access_tokens.json", "api_config.json", "passwords.txt",
            "logins.txt", "account_info.json", "user_data.json", "login_details.csv",
            "credentials.txt", "auth_info.json"
        ]
    },
    {
        "category": "4. Carteiras Criptográficas, Escrow & Transações",
        "entries": [
            "wallets/", "bitcoin_wallets.txt", "ethereum_wallets.json", "monero_wallets.txt",
            "crypto_keys.txt", "crypto_wallets.db", "escrow.conf", "transactions.txt",
            "deal_info.json", "escrow_data.csv", "trade_details.txt"
        ]
    },
    {
        "category": "5. Chaves PGP, Certificados & Segurança",
        "entries": [
            "pgp.keyring", "certificates/", "ssl_certs.txt", "certs.db", "keys.pem",
            "certs.json", "cert.pem", "privkey.pem", "fullchain.pem", "id_rsa", "id_rsa.pub",
            "authorized_keys", "known_hosts", "vault-init.json", "sshd_config"
        ]
    },
    {
        "category": "6. Configurações de Servidor, Regras & Proxies",
        "entries": [
            "config.yml", "server_config.json", "rules.txt", "torrc", "nginx.conf",
            "caddyfile", "Caddyfile", "proxy_config.json", "default.conf", "traefik.yml",
            "haproxy.cfg", "robots.txt", "sitemap.xml", "app.service"
        ]
    },
    {
        "category": "7. Metadados, Manifestos & Informações de Serviço",
        "entries": [
            "manifest.json", "metadata.json", "info.txt", "service_info.json", "site_metadata.txt"
        ]
    },
    {
        "category": "8. Mídia, Imagens, Vídeos & Conteúdo",
        "entries": [
            "images/", "videos/", "audios/", "media/", "content/"
        ]
    },
    {
        "category": "9. Anotações, Diários & Memos",
        "entries": [
            "readme.txt", "notes.txt", "journal.txt", "diary.json", "memos.txt"
        ]
    },
    {
        "category": "10. Dados de Usuários & Listagens",
        "entries": [
            "users/", "users.json", "users.db", "listings.db"
        ]
    },
    {
        "category": "11. Redes Ocultas, Darknet, P2P & Tor (.onion)",
        "entries": [
            ".onion", "README.onion", "v3", "v2"
        ]
    },
    {
        "category": "12. Containers, Infraestrutura & Nuvem (IaC)",
        "entries": [
            "Dockerfile", "docker-compose.yml", "docker-compose.prod.yml", "main.tf",
            "variables.tf", "outputs.tf", "terraform.tfstate", "terraform.tfvars",
            "Chart.yaml", "values.yaml", "deployment.yaml", "service.yaml",
            "ingress.yaml", "kustomization.yaml"
        ]
    },
    {
        "category": "13. Pipelines de CI/CD & Automação",
        "entries": [
            ".github/workflows/ci.yml", ".github/workflows/deploy.yml", ".gitlab-ci.yml",
            "Jenkinsfile", "cloudbuild.yaml", "bitbucket-pipelines.yml", "deploy.yml"
        ]
    },
    {
        "category": "14. Banco de Dados, Schemas & Migrações",
        "entries": [
            "schema.prisma", "prisma/schema.prisma", "schema.sql", "seeds.sql", "seed.ts",
            "knexfile.js", "flyway.conf", "alembic.ini", "database.ts", "pg_hba.conf",
            "postgresql.conf", "redis.conf"
        ]
    },
    {
        "category": "15. Arquitetura de Código (Backend / Core)",
        "entries": [
            "server.ts", "main.go", "main.py", "index.js", "app.ts", "routes.ts",
            "auth.controller.ts", "payment.service.ts", "user.repository.ts", "order.entity.ts",
            "create-user.dto.ts", "jwt.strategy.ts", "rate-limiter.middleware.ts",
            "error-handler.middleware.ts", "database.connection.ts", "stripe.adapter.ts",
            "s3.storage.provider.ts", "auth.middleware.ts", "error.middleware.ts",
            "cors.middleware.ts", "rateLimiter.ts", "redis.ts", "queue.ts"
        ]
    },
    {
        "category": "16. Filas, Background Jobs & Workers",
        "entries": [
            "email.worker.ts", "invoice-processor.job.ts", "webhook.consumer.ts",
            "bullmq.config.ts", "kafka.producer.ts", "celery.py"
        ]
    },
    {
        "category": "17. Observabilidade, Métricas & Logs",
        "entries": [
            "prometheus.yml", "otel-collector-config.yaml", "loki-config.yaml", "vector.yaml",
            "grafana-dashboard.json", "sentry.client.config.ts"
        ]
    },
    {
        "category": "18. Sistema Operacional & Linux Core",
        "entries": [
            "/etc/hosts", "/etc/fstab", "/etc/resolv.conf", "/etc/sysctl.conf",
            "/etc/security/limits.conf", "/etc/systemd/system/app.service",
            "/var/log/syslog", "/var/log/nginx/error.log", "/var/log/nginx/access.log", "crontab"
        ]
    }
]

def analyze_workspace_static(scan_dir: Path) -> dict:
    """Realiza análise estática profunda e irrestrita (100% de cobertura com foco em APIs, rotas e conexões)."""
    metrics = {
        "html_files": 0,
        "js_ts_files": 0,
        "py_files": 0,
        "total_files_scanned": 0,
        "csp_enforced": False,
        "sri_found": False,
        "external_scripts": [],
        "sensitive_files": [],
        "dotfiles_found": [],
        "sql_concatenations": [],
        "secrets_found": [],
        "webshells_found": [],
        "dependencies": {},
        "unmasked_passwords": 0,
        "hidden_inputs": 0,
        "hidden_inputs_details": [],
        "hydration_variables": [],
        "html_comments_suspicious": [],
        "routes_discovered": [],
        "external_links": [],
        "webhooks_listeners": [],
        "websockets_discovered": [],
        "api_specs_discovered": [],
        "query_params_discovered": [],
        "http_headers_discovered": [],
        "databases_discovered": [],
        "architectural_capabilities": [],
        "structural_files_inventory": [],
        "live_audit_data": None
    }

    # Carregar relatórios pré-existentes de fases
    phase_files = {
        "p1": scan_dir / "reports" / "audit_phase1_dom_client.json",
        "p2": scan_dir / "reports" / "audit_phase2_network_ports.json",
        "p3": scan_dir / "reports" / "audit_phase3_api_gateways.json",
        "p4": scan_dir / "reports" / "audit_phase4_sensitive_routes.json",
        "p5": scan_dir / "reports" / "audit_phase5_secrets.json",
        "p6": scan_dir / "reports" / "audit_phase6_sca.json",
        "p7": scan_dir / "reports" / "audit_phase7_sql_sanitization.json",
        "p8": scan_dir / "reports" / "audit_phase8_webshells.json",
        "p10": scan_dir / "reports" / "audit_phase10_dom_snapshots.json",
        "sec_headers": scan_dir / "reports" / "audit_security_headers.json"
    }
    metrics["phase_reports"] = {}
    for pkey, ppath in phase_files.items():
        if ppath.exists():
            try:
                with open(ppath, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
                    metrics["phase_reports"][pkey] = pdata
                    if pkey == "sec_headers" and pdata.get("headers_presentes", {}).get("Content-Security-Policy"):
                        metrics["csp_enforced"] = True
            except Exception:
                pass

    # Verifica package.json
    pkg_file = scan_dir / "package.json"
    if pkg_file.exists():
        try:
            with open(pkg_file, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
                deps = pkg_data.get("dependencies", {})
                dev_deps = pkg_data.get("devDependencies", {})
                metrics["dependencies"]["npm"] = len(deps) + len(dev_deps)
        except Exception:
            pass

    # Verifica requirements.txt
    req_file = scan_dir / "requirements.txt"
    if req_file.exists():
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
                metrics["dependencies"]["python"] = len(lines)
        except Exception:
            pass

    # Padrões Regex Avançados para Frameworks
    framework_patterns = [
        # Express / Fastify / Koa / Connect: (app|router).get('/path', ...)
        (re.compile(r'(?:app|router|fastify|server)\.(get|post|put|delete|patch|all|use|route)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "FRAMEWORK_EXPRESS"),
        # NestJS decorators: @Get('/path') ou @Post('path')
        (re.compile(r'@(Get|Post|Put|Delete|Patch|Options|Head)\s*\(\s*(?:[\'"`]([^\'"`]*)[\'"`])?\s*\)', re.I), "NESTJS_DECORATOR"),
        # FastAPI / Flask / Starlette / Bottle: @app.get('/path')
        (re.compile(r'@(?:app|router|api|bp)\.(get|post|put|delete|patch|route)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "FASTAPI_FLASK"),
        # Django: path('route/', ...) ou url(r'^route/', ...)
        (re.compile(r'(?:path|re_path|url)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "DJANGO_PATH"),
        # PHP Laravel / Lumen: Route::get('/path', ...)
        (re.compile(r'Route::(get|post|put|delete|patch|match|any|resource|apiResource)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "LARAVEL_ROUTE"),
        # PHP Symfony: #[Route('/path')]
        (re.compile(r'#\[Route\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "SYMFONY_ROUTE"),
        # Ruby Rails: get '/path', to: ...
        (re.compile(r'(?:get|post|put|delete|patch|resources)\s+[\'":]([a-zA-Z0-9_\-\./:]+)', re.I), "RAILS_ROUTE"),
        # Go Gin / Echo / Fiber: r.GET("/path", ...)
        (re.compile(r'\.(GET|POST|PUT|DELETE|PATCH|Handle|HandleFunc)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "GO_ROUTE"),
        # Java Spring: @GetMapping("/path")
        (re.compile(r'@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\s*(?:(?:value|path)\s*=\s*)?[\'"`]([^\'"`]+)[\'"`]', re.I), "SPRING_ROUTE"),
        # C# ASP.NET Core: [HttpGet("path")] ou app.MapGet("/path")
        (re.compile(r'\[(?:HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch|Route)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|app\.Map(?:Get|Post|Put|Delete)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "ASPNET_ROUTE"),
        # Outgoing HTTP Client Calls (fetch, axios, requests, httpx, $.ajax)
        (re.compile(r'(?:fetch|axios(?:\.[a-z]+)?|\$\.ajax|\$\.get|\$\.post|requests\.(?:get|post|put|delete)|httpx\.(?:get|post))\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', re.I), "HTTP_CLIENT_CALL"),
        # Generic REST pattern nos arquivos
        (re.compile(r'[\'"`](/(?:api|v[0-9]+|rest|graphql|auth|webhook|internal|admin|debug|login|checkout|payment|user|users|order|orders)/[a-zA-Z0-9_\-\./:]*)[\'"`]', re.I), "GENERIC_REST_PATH")
    ]

    # Regex para Links Externos
    url_regex = re.compile(r'https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?::[0-9]+)?(?:/[^\s\'"`<>]*)?')

    # Regex para WebSockets e Streams
    ws_regex = re.compile(r'(?:wss?://[a-zA-Z0-9\-\.]+(?::[0-9]+)?(?:/[^\s\'"`<>]*)?|new\s+WebSocket\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|(?:io|io\.connect)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|socket\.(?:on|emit)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|new\s+EventSource\s*\(\s*[\'"`]([^\'"`]+)[\'"`])', re.I)

    # Regex para Query Parameters e Backend Getters
    param_regex = re.compile(r'[?&]([a-zA-Z0-9_]{2,35})=')
    backend_param_regex = re.compile(r'(?:req\.query\.([a-zA-Z0-9_]+)|req\.query\[[\'"`]([^\'"`]+)[\'"`]|(?:searchParams|params)\.get\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|request\.GET\.get\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|request\.args\.get\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|request\.query_params\.get\s*\(\s*[\'"`]([^\'"`]+)[\'"`]|\$_GET\[[\'"`]([^\'"`]+)[\'"`])', re.I)
    sensitive_param_names = {"debug", "admin", "token", "auth", "key", "secret", "password", "pass", "bypass", "sudo", "role", "privilege", "preview", "test", "demo", "impersonate", "internal", "mock", "staging"}

    # Regex para Headers HTTP
    header_regex = re.compile(r'[\'"`](Authorization|X-Api-Key|X-Auth-Token|X-Hub-Signature|Stripe-Signature|apikey|X-Forwarded-For)[\'"`]\s*:', re.I)

    # Regex para Segredos e Credenciais (Precisão Cirúrgica sem falsos positivos)
    secrets_patterns = [
        re.compile(r'\b(AKIA[0-9A-Z]{16})\b'),                                                # AWS Access Key
        re.compile(r'\b(ghp_[a-zA-Z0-9]{36})\b'),                                             # GitHub Personal Token
        re.compile(r'\b(AIza[0-9A-Za-z-_]{35})\b'),                                           # Google API Key
        re.compile(r'\b(sk-[a-zA-Z0-9]{48}|sk-proj-[a-zA-Z0-9\-_]{32,})\b'),                 # OpenAI Key
        re.compile(r'\b(stripe_(?:live|test)_[0-9a-zA-Z]{24,})\b'),                           # Stripe Key
        re.compile(r'\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b'),                                   # Slack Token
        re.compile(r'\b(ey[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,})\b'),   # JWT Token Real
        re.compile(r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----')                                # Private Key
    ]

    # Regex para SQL Concatenation (evita false positives em declarações de função e exige escopo de linha)
    sql_concat_regex = re.compile(r'(?:SELECT|INSERT|UPDATE|DELETE)[^\n]*\+[^\n]*(?:FROM|INTO|WHERE)|(?:cursor|db|conn|session)\.execute\([^\n,]*\+[^\n,]*\)|f["\'][^\n]*(?:SELECT|UPDATE|DELETE|INSERT)[^\n]*\{', re.I)

    # Regex para Webshells / RCE (Exclusivo para backends web .php, .py, .js)
    webshell_regex = re.compile(r'(eval\s*\(\s*base64_decode|system\s*\(\s*\$_GET|os\.system\s*\(\s*request\.|shell_exec\s*\(\s*\$_)', re.I)

    # Regex para Comentários HTML
    comment_regex = re.compile(r'<!--([\s\S]*?)-->')
    suspicious_comment_keywords = ["TODO", "FIXME", "SECRET", "PASSWORD", "KEY", "TEMP", "DEBUG", "ADMIN", "BACKEND"]

    seen_routes = set()
    seen_urls = set()
    seen_params = set()
    seen_ws = set()
    seen_headers = set()

    # Estruturas para Arquivos Estruturais
    workspace_files = set()
    files_by_name = defaultdict(list)
    dirs_by_name = defaultdict(list)

    # Inicializar rastreamento de capacidades arquiteturais
    capabilities_tracker = {}
    for cap in ARCHITECTURAL_CAPABILITIES_SPECS:
        capabilities_tracker[cap["id"]] = {
            "spec": cap,
            "detected": False,
            "evidence": []
        }

    # Varrer arquivos recursivamente (Incluindo Dotfiles e todas as extensões)
    target_suffixes = {
        ".html", ".htm", ".js", ".ts", ".jsx", ".tsx", ".vue", ".svelte",
        ".py", ".php", ".rb", ".go", ".java", ".json", ".yaml", ".yml",
        ".sql", ".sh", ".bash", ".zsh", ".env", ".conf", ".ini", ".xml", ".graphql", ".gql",
        ".txt", ".csv", ".md", ".toml", ".lock", ".prisma", ".cfg", ".log", ".service",
        ".pem", ".crt", ".key", ".pub"
    }

    for root, dirs, files in os.walk(scan_dir):
        # Pular apenas caches pesados de compilação, mantendo todo o restante
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", "reports", "backups", ".next", ".nuxt", "scratch"]]
        
        rel_root = Path(root).relative_to(scan_dir)

        for d in dirs:
            d_rel = str(rel_root / d).replace("\\", "/")
            dirs_by_name[d.lower()].append(d_rel)

        # 1. Checar Dotfiles na pasta
        for fname in files:
            f_rel = str(rel_root / fname).replace("\\", "/")
            workspace_files.add(f_rel)
            files_by_name[fname.lower()].append(f_rel)

            if fname.startswith("."):
                dot_rel = str(rel_root / fname)
                metrics["dotfiles_found"].append(dot_rel)
                # Ignorar arquivos de controle comuns que não contêm senhas e arquivos de template/exemplo
                if fname in [".gitignore", ".gitattributes", ".gitkeep", ".DS_Store", ".editorconfig", ".eslintrc"] or fname.endswith((".example", ".sample", ".template")):
                    continue
                if fname.startswith(".env") or fname in [".gitconfig", ".npmrc", ".pypirc"] or any(k in fname.lower() for k in [".aws", ".ssh", ".docker"]):
                    full_p = Path(root) / fname
                    is_secure = False
                    try:
                        mode = full_p.stat().st_mode & 0o777
                        if mode in (0o600, 0o400):
                            import subprocess
                            res = subprocess.run(
                                ["git", "ls-files", "--error-unmatch", str(full_p.relative_to(scan_dir))],
                                capture_output=True,
                                cwd=str(scan_dir)
                            )
                            if res.returncode != 0:
                                is_secure = True
                    except Exception:
                        pass
                    if not is_secure and dot_rel not in metrics["sensitive_files"]:
                        metrics["sensitive_files"].append(dot_rel)

            # Checagem de Arquivos Sensíveis de Dados, Cartões, Senhas e Carteiras
            high_risk_sensitive_names = [
                "cards.txt", "ccdumps.txt", "carding.txt", "cardinfo.json", "cards.db",
                "banks.txt", "financial_data.json", "transfers.csv", "account_details.txt",
                "tokens.txt", "api_keys.txt", "secrets.txt", "auth.txt", "credentials.json",
                "keys.txt", "access_tokens.json", "passwords.txt", "logins.txt",
                "account_info.json", "login_details.csv", "credentials.txt", "auth_info.json",
                "bitcoin_wallets.txt", "ethereum_wallets.json", "monero_wallets.txt",
                "crypto_keys.txt", "crypto_wallets.db", "escrow_data.csv", "trade_details.txt",
                "pgp.keyring", "keys.pem", "id_rsa"
            ]
            if fname.lower() in high_risk_sensitive_names:
                sens_rel = str(rel_root / fname)
                if sens_rel not in metrics["sensitive_files"]:
                    metrics["sensitive_files"].append(sens_rel)

        # 2. Checar Bancos de Dados
        for fname in files:
            if any(fname.endswith(ext) for ext in [".db", ".sqlite", ".sqlite3"]):
                db_p = Path(root) / fname
                tables = inspect_sqlite_tables(db_p)
                metrics["databases_discovered"].append({
                    "file": str(rel_root / fname),
                    "tables": tables,
                    "table_count": len(tables)
                })

        # 3. Mapeamento de Rotas Baseadas em Arquivos (Next.js, Nuxt, SvelteKit, Remix, Astro)
        for fname in files:
            fpath = Path(root) / fname
            rel_p = rel_root / fname
            rel_p_str = str(rel_p).replace("\\", "/")

            # Next.js App Router
            if "app/" in rel_p_str:
                if fname in ["route.js", "route.ts"]:
                    parts = rel_p_str.split("app/")[1].split("/" + fname)[0]
                    clean_route = "/" + re.sub(r'\([^)]+\)/?', '', parts).strip("/")
                    r_meta = categorize_route(clean_route, "HANDLER")
                    routes_key = (clean_route, "HANDLER", rel_p_str)
                    if routes_key not in seen_routes:
                        seen_routes.add(routes_key)
                        metrics["routes_discovered"].append({
                            "route": clean_route,
                            "method": "HANDLER",
                            "file": rel_p_str,
                            "type": "FILE_ROUTE_APP",
                            "category": r_meta["category"],
                            "risk_level": r_meta["risk_level"],
                            "label": r_meta["label"],
                            "badge_cls": r_meta["badge_cls"]
                        })
                elif fname in ["page.js", "page.ts", "page.jsx", "page.tsx"]:
                    parts = rel_p_str.split("app/")[1].split("/" + fname)[0]
                    clean_route = "/" + re.sub(r'\([^)]+\)/?', '', parts).strip("/")
                    r_meta = categorize_route(clean_route, "VIEW")
                    routes_key = (clean_route, "VIEW", rel_p_str)
                    if routes_key not in seen_routes:
                        seen_routes.add(routes_key)
                        metrics["routes_discovered"].append({
                            "route": clean_route,
                            "method": "VIEW",
                            "file": rel_p_str,
                            "type": "FILE_ROUTE_PAGE",
                            "category": r_meta["category"],
                            "risk_level": r_meta["risk_level"],
                            "label": r_meta["label"],
                            "badge_cls": r_meta["badge_cls"]
                        })

            # Next.js Pages Router
            elif "pages/" in rel_p_str and not rel_p_str.startswith("docs/"):
                ext = fpath.suffix.lower()
                if ext in [".js", ".ts", ".jsx", ".tsx"]:
                    parts = rel_p_str.split("pages/")[1]
                    base_no_ext = str(Path(parts).with_suffix(""))
                    if base_no_ext.endswith("/index"):
                        base_no_ext = base_no_ext[:-6]
                    clean_route = "/" + base_no_ext.strip("/")
                    if clean_route not in ["/_app", "/_document"]:
                        is_api = clean_route.startswith("/api")
                        m_type = "HANDLER" if is_api else "VIEW"
                        r_meta = categorize_route(clean_route, m_type)
                        routes_key = (clean_route, m_type, rel_p_str)
                        if routes_key not in seen_routes:
                            seen_routes.add(routes_key)
                            metrics["routes_discovered"].append({
                                "route": clean_route,
                                "method": m_type,
                                "file": rel_p_str,
                                "type": "FILE_ROUTE_PAGES",
                                "category": r_meta["category"],
                                "risk_level": r_meta["risk_level"],
                                "label": r_meta["label"],
                                "badge_cls": r_meta["badge_cls"]
                            })

            # Nuxt.js Server API
            elif "server/api/" in rel_p_str or "server/routes/" in rel_p_str:
                ext = fpath.suffix.lower()
                if ext in [".js", ".ts"]:
                    parts = rel_p_str.split("server/")[1]
                    base_no_ext = str(Path(parts).with_suffix(""))
                    clean_route = "/" + base_no_ext.strip("/")
                    r_meta = categorize_route(clean_route, "HANDLER")
                    routes_key = (clean_route, "HANDLER", rel_p_str)
                    if routes_key not in seen_routes:
                        seen_routes.add(routes_key)
                        metrics["routes_discovered"].append({
                            "route": clean_route,
                            "method": "HANDLER",
                            "file": rel_p_str,
                            "type": "FILE_ROUTE_NUXT",
                            "category": r_meta["category"],
                            "risk_level": r_meta["risk_level"],
                            "label": r_meta["label"],
                            "badge_cls": r_meta["badge_cls"]
                        })

            # 4. Mapeamento de Contratos de API (OpenAPI, Swagger, Postman)
            if fname.endswith(".postman_collection.json") or fname in ["swagger.json", "openapi.json"]:
                try:
                    spec_content = fpath.read_text(encoding="utf-8", errors="ignore")
                    spec_data = json.loads(spec_content)
                    if "paths" in spec_data and isinstance(spec_data["paths"], dict):
                        p_count = len(spec_data["paths"])
                        metrics["api_specs_discovered"].append({
                            "file": rel_p_str,
                            "format": "OPENAPI_SWAGGER",
                            "paths_count": p_count
                        })
                        for s_path, s_methods in spec_data["paths"].items():
                            if isinstance(s_methods, dict):
                                for s_m in s_methods.keys():
                                    if s_m.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
                                        r_meta = categorize_route(s_path, s_m.upper())
                                        s_key = (s_path, s_m.upper(), rel_p_str)
                                        if s_key not in seen_routes:
                                            seen_routes.add(s_key)
                                            metrics["routes_discovered"].append({
                                                "route": s_path,
                                                "method": s_m.upper(),
                                                "file": rel_p_str,
                                                "type": "SPEC_ENDPOINT",
                                                "category": r_meta["category"],
                                                "risk_level": r_meta["risk_level"],
                                                "label": r_meta["label"],
                                                "badge_cls": r_meta["badge_cls"]
                                            })
                    elif "item" in spec_data and isinstance(spec_data["item"], list):
                        def parse_postman_items(items):
                            count = 0
                            for item in items:
                                if "item" in item and isinstance(item["item"], list):
                                    count += parse_postman_items(item["item"])
                                elif "request" in item:
                                    count += 1
                                    req = item["request"]
                                    m = req.get("method", "GET").upper() if isinstance(req, dict) else "GET"
                                    url_obj = req.get("url", "") if isinstance(req, dict) else ""
                                    raw_url = url_obj if isinstance(url_obj, str) else (url_obj.get("raw", "") if isinstance(url_obj, dict) else "")
                                    if raw_url:
                                        p_only = "/" + raw_url.split("://")[-1].split("/", 1)[-1].split("?")[0] if "://" in raw_url else raw_url.split("?")[0]
                                        if p_only.startswith("/"):
                                            r_meta = categorize_route(p_only, m)
                                            s_key = (p_only, m, rel_p_str)
                                            if s_key not in seen_routes:
                                                seen_routes.add(s_key)
                                                metrics["routes_discovered"].append({
                                                    "route": p_only,
                                                    "method": m,
                                                    "file": rel_p_str,
                                                    "type": "POSTMAN_ENDPOINT",
                                                    "category": r_meta["category"],
                                                    "risk_level": r_meta["risk_level"],
                                                    "label": r_meta["label"],
                                                    "badge_cls": r_meta["badge_cls"]
                                                })
                            return count
                        total_pm = parse_postman_items(spec_data["item"])
                        metrics["api_specs_discovered"].append({
                            "file": rel_p_str,
                            "format": "POSTMAN_COLLECTION",
                            "paths_count": total_pm
                        })
                except Exception:
                    pass

        # 5. Inspeção Profunda de Conteúdo
        for fname in files:
            fpath = Path(root) / fname
            suffix = fpath.suffix.lower()
            rel_file_str = str(rel_root / fname)

            # Contabilizar métricas por tipo
            metrics["total_files_scanned"] += 1
            if suffix in [".html", ".htm"]:
                metrics["html_files"] += 1
            elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
                metrics["js_ts_files"] += 1
            elif suffix == ".py":
                metrics["py_files"] += 1

            # Filtrar extensões para leitura profunda de texto
            is_env = fname.startswith(".env")
            is_known_text_file = fname.lower() in [
                "dockerfile", "makefile", "caddyfile", "jenkinsfile", "torrc",
                "crontab", "v2", "v3", "readme.onion", "app.service", "sshd_config",
                "authorized_keys", "known_hosts"
            ]
            if suffix in target_suffixes or is_env or is_known_text_file:
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")

                    # A. Extração de Rotas & APIs com Método e Tipo
                    for r_pat, f_type in framework_patterns:
                        for m in r_pat.finditer(content):
                            groups = [g for g in m.groups() if g is not None]
                            if not groups:
                                continue
                            if len(groups) == 1:
                                route_val = groups[0]
                                method_val = "ALL"
                            else:
                                if groups[0].upper() in ["GET", "POST", "PUT", "DELETE", "PATCH", "ALL", "USE", "ROUTE", "OPTIONS", "HEAD"]:
                                    method_val = groups[0].upper()
                                    route_val = groups[1]
                                else:
                                    route_val = groups[0]
                                    method_val = groups[1].upper() if len(groups) > 1 else "GET"

                            if route_val and route_val.startswith("/") and len(route_val) > 1 and not route_val.startswith("//"):
                                clean_r = route_val.split("?")[0].strip()
                                # Filtrar caminhos absolutos do sistema operacional e arquivos estáticos locais
                                if clean_r.startswith(("/Users/", "/Applications/", "/System/", "/Library/", "/home/", "/etc/", "/var/", "/usr/", "/opt/", "/tmp/", "/root/")):
                                    continue
                                if clean_r.endswith((".py", ".sh", ".md", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".css", ".map")) and not clean_r.startswith(("/api", "/v", "/static", "/assets")):
                                    continue
                                r_meta = categorize_route(clean_r, method_val)
                                r_key = (clean_r, method_val, rel_file_str)
                                if r_key not in seen_routes:
                                    seen_routes.add(r_key)
                                    metrics["routes_discovered"].append({
                                        "route": clean_r,
                                        "method": method_val,
                                        "file": rel_file_str,
                                        "type": f_type,
                                        "category": r_meta["category"],
                                        "risk_level": r_meta["risk_level"],
                                        "label": r_meta["label"],
                                        "badge_cls": r_meta["badge_cls"]
                                    })

                                    # Checagem de Webhook Listener
                                    if r_meta["category"] == "WEBHOOK_CALLBACK":
                                        has_sig_check = any(k in content.lower() for k in [
                                            "stripe-signature", "x-hub-signature", "hmac", "sha256",
                                            "verify_signature", "webhook_secret", "crypto.createhmac"
                                        ])
                                        metrics["webhooks_listeners"].append({
                                            "route": clean_r,
                                            "method": method_val,
                                            "file": rel_file_str,
                                            "signature_verified": has_sig_check,
                                            "protection": "ASSINATURA_VERIFICADA" if has_sig_check else "DESPROTEGIDO"
                                        })

                    # B. Extração de Links Externos Categorizados
                    for u in url_regex.findall(content):
                        if u not in seen_urls and not any(loc in u for loc in ["127.0.0.1", "localhost"]):
                            seen_urls.add(u)
                            metrics["external_links"].append({
                                "url": u,
                                "category": categorize_external_url(u),
                                "file": rel_file_str
                            })

                    # C. Extração de WebSockets e Eventos Real-Time
                    for ws_m in ws_regex.finditer(content):
                        val = next((g for g in ws_m.groups() if g is not None), ws_m.group(0))
                        if val and val not in seen_ws and len(val) > 2:
                            seen_ws.add(val)
                            metrics["websockets_discovered"].append({
                                "stream": val[:80],
                                "file": rel_file_str
                            })

                    # D. Extração de Query Parameters (URL e Backend Getters)
                    for q in param_regex.findall(content):
                        if q not in seen_params and len(q) > 1:
                            seen_params.add(q)
                            metrics["query_params_discovered"].append({
                                "param": q,
                                "is_sensitive": q.lower() in sensitive_param_names,
                                "source": "URL_STRING",
                                "file": rel_file_str
                            })
                    for bq_m in backend_param_regex.finditer(content):
                        bq_val = next(g for g in bq_m.groups() if g is not None)
                        if bq_val and bq_val not in seen_params and len(bq_val) > 1:
                            seen_params.add(bq_val)
                            metrics["query_params_discovered"].append({
                                "param": bq_val,
                                "is_sensitive": bq_val.lower() in sensitive_param_names,
                                "source": "BACKEND_QUERY_GETTER",
                                "file": rel_file_str
                            })

                    # E. Extração de Headers HTTP
                    for h_m in header_regex.findall(content):
                        if h_m not in seen_headers:
                            seen_headers.add(h_m)
                            metrics["http_headers_discovered"].append({
                                "header": h_m,
                                "file": rel_file_str
                            })

                    # F. Segredos e Credenciais
                    for s_pat in secrets_patterns:
                        hits = s_pat.findall(content)
                        if hits:
                            for hit in hits:
                                metrics["secrets_found"].append(f"{rel_file_str}: {hit[:8]}*** (mascarado)")

                    # G. SQL Concatenations
                    if sql_concat_regex.search(content):
                        metrics["sql_concatenations"].append(rel_file_str)

                    # H. Webshells / RCE (em arquivos de servidor web)
                    if suffix in [".php", ".py", ".js", ".jsp", ".asp"] and webshell_regex.search(content):
                        metrics["webshells_found"].append(rel_file_str)

                    # I. Frontend, DOM & Comentários (HTML, Vue, Svelte, JSX)
                    if suffix in [".html", ".htm", ".vue", ".svelte", ".jsx", ".tsx"]:
                        if "Content-Security-Policy" in content:
                            metrics["csp_enforced"] = True
                        if "integrity=" in content:
                            metrics["sri_found"] = True

                        # Senhas & Inputs Hidden
                        pw_count = len(re.findall(r'type=["\']password["\']', content, re.I))
                        metrics["unmasked_passwords"] += pw_count

                        hidden_matches = re.findall(r'<input[^>]+type=["\']hidden["\'][^>]*>', content, re.I)
                        metrics["hidden_inputs"] += len(hidden_matches)
                        for hm in hidden_matches[:5]:
                            name_m = re.search(r'name=["\']([^"\']+)["\']', hm, re.I)
                            val_m = re.search(r'value=["\']([^"\']+)["\']', hm, re.I)
                            metrics["hidden_inputs_details"].append({
                                "name": name_m.group(1) if name_m else "sem-nome",
                                "value": val_m.group(1) if val_m else "vazio",
                                "file": rel_file_str
                            })

                        # Variáveis SSR
                        for h_var in ["__NEXT_DATA__", "__INITIAL_STATE__", "__NUXT__", "_sharedData", "__APOLLO_STATE__"]:
                            if h_var in content and h_var not in metrics["hydration_variables"]:
                                metrics["hydration_variables"].append(h_var)

                        # Comentários HTML suspeitos
                        for comm in comment_regex.findall(content):
                            if any(k in comm.upper() for k in suspicious_comment_keywords):
                                metrics["html_comments_suspicious"].append({
                                    "comment": comm.strip()[:100],
                                    "file": rel_file_str
                                })

                    # J. Detecção de Capacidades Arquiteturais (Excluindo o próprio compilador e testes)
                    if fname not in ["compile_audit_report.py", "build_dicionario.py", "modularizar_dicionario.py", "atualizar_dicionario_sequencial.py", "test_capabilities_and_files.py"] and "scratch" not in rel_file_str:
                        for cap in ARCHITECTURAL_CAPABILITIES_SPECS:
                            cid = cap["id"]
                            if len(capabilities_tracker[cid]["evidence"]) < 3:
                                m = cap["pattern"].search(content)
                                if m:
                                    capabilities_tracker[cid]["detected"] = True
                                    capabilities_tracker[cid]["evidence"].append({
                                        "file": rel_file_str,
                                        "match": m.group(0)[:60]
                                    })

                except Exception:
                    pass

    # Compilar Matriz Arquitetural
    for cap in ARCHITECTURAL_CAPABILITIES_SPECS:
        cid = cap["id"]
        c_info = capabilities_tracker[cid]
        metrics["architectural_capabilities"].append({
            "id": cid,
            "name": cap["name"],
            "domain": cap["domain"],
            "detected": c_info["detected"],
            "evidence_count": len(c_info["evidence"]),
            "evidence": c_info["evidence"]
        })

    # Compilar Inventário de Arquivos Estruturais & Canônicos
    for cat in STRUCTURAL_FILES_CATEGORIES:
        cat_name = cat["category"]
        for entry in cat["entries"]:
            found = False
            found_paths = []
            is_sys = entry.startswith("/")
            is_dir_entry = entry.endswith("/")

            if is_sys:
                sys_p = Path(entry)
                loc_p = scan_dir / entry.lstrip("/")
                if sys_p.exists():
                    found = True
                    found_paths.append(str(sys_p) + " (OS HOST)")
                elif loc_p.exists():
                    found = True
                    found_paths.append(str(loc_p.relative_to(scan_dir)) + " (LOCAL)")
            elif is_dir_entry:
                d_name = entry.rstrip("/").lower()
                if d_name in dirs_by_name:
                    found = True
                    found_paths.extend(dirs_by_name[d_name])
                elif (scan_dir / entry.rstrip("/")).is_dir():
                    found = True
                    found_paths.append(entry)
            else:
                if entry in workspace_files:
                    found = True
                    found_paths.append(entry)
                else:
                    entry_base = Path(entry).name.lower()
                    if entry_base in files_by_name:
                        found = True
                        found_paths.extend(files_by_name[entry_base])
                    elif (scan_dir / entry).exists():
                        found = True
                        found_paths.append(entry)

            metrics["structural_files_inventory"].append({
                "category": cat_name,
                "entry": entry,
                "status": "PRESENTE" if found else "AUSENTE",
                "paths": found_paths
            })

    # Análise de Composição de Software (SCA)
    metrics["sca"] = run_sca_analysis(scan_dir)

    return metrics

def calculate_security_score(metrics: dict, port_list: list, pci_data: dict) -> dict:
    """Calcula Score de Segurança e Saúde (0 a 100) com classificação e penalidades."""
    score = 100
    penalties = []

    # 1. Segredos e Chaves Expostas (-25 pts cada, max -50)
    sec_count = len(metrics.get("secrets_found", []))
    if sec_count > 0:
        p = min(50, sec_count * 25)
        score -= p
        penalties.append({"motivo": f"{sec_count} credencial(is)/segredo(s) exposto(s)", "deducao": p, "severidade": "CRÍTICA"})

    # 2. Webshells / Backdoors (-40 pts cada, max -60)
    ws_count = len(metrics.get("webshells_found", []))
    if ws_count > 0:
        p = min(60, ws_count * 40)
        score -= p
        penalties.append({"motivo": f"{ws_count} padrão(ões) de webshell/backdoor detectado(s)", "deducao": p, "severidade": "CRÍTICA"})

    # 3. Falhas PCI-DSS / PAN exposto (-35 pts)
    pci_status = pci_data.get("status_geral_compliance", "CONFORME")
    pci_vulns = len(pci_data.get("verificacao_vulnerabilidade", []))
    if pci_status == "BLOQUEIO_IMEDIATO" or pci_vulns > 0:
        p = 35
        score -= p
        penalties.append({"motivo": "Violação de integridade PCI-DSS (dados financeiros/PAN desmascarados)", "deducao": p, "severidade": "CRÍTICA"})

    # 4. Arquivos Críticos Expostos (.env, id_rsa, .git/config) (-10 pts cada, max -25)
    sens_count = len(metrics.get("sensitive_files", []))
    if sens_count > 0:
        p = min(25, sens_count * 10)
        score -= p
        penalties.append({"motivo": f"{sens_count} arquivo(s) sensível(is) exposto(s) (.env, .git, chaves)", "deducao": p, "severidade": "ALTA"})

    # 5. Queries SQL Concatenadas / Risco de Injeção (-10 pts cada, max -20)
    sql_count = len(metrics.get("sql_concatenations", []))
    if sql_count > 0:
        p = min(20, sql_count * 10)
        score -= p
        penalties.append({"motivo": f"{sql_count} query(ies) SQL concatenada(s) sem parametrização", "deducao": p, "severidade": "MÉDIA"})

    # 6. Portas de banco de dados e serviços sensíveis ativas externamente (-10 pts)
    risky_ports = [21, 3306, 5432, 6379, 27017]
    exposed_risky = [pt for pt in port_list if pt.get("port") in risky_ports and pt.get("externally_exposed", False)]
    if exposed_risky:
        p = min(20, len(exposed_risky) * 10)
        score -= p
        ports_str = ", ".join([str(pt["port"]) for pt in exposed_risky])
        penalties.append({"motivo": f"Portas de banco de dados abertas nas interfaces externas ({ports_str})", "deducao": p, "severidade": "MÉDIA"})

    # 7. Ausência de CSP ou SRI em frontends ativos (-5 pts cada)
    if metrics.get("html_files", 0) > 0:
        if not metrics.get("csp_enforced", False):
            score -= 5
            penalties.append({"motivo": "Ausência de cabeçalho Content-Security-Policy (CSP)", "deducao": 5, "severidade": "BAIXA"})
        if not metrics.get("sri_found", False) and metrics.get("external_scripts"):
            score -= 5
            penalties.append({"motivo": "Ausência de Subresource Integrity (SRI) em scripts externos", "deducao": 5, "severidade": "BAIXA"})

    score = max(0, min(100, score))

    if score >= 90:
        grade = "A"
        classification = "SEGURO (CONFORME)"
        color = "#10b981"
        badge = "success"
    elif score >= 75:
        grade = "B"
        classification = "MODERADO (BOM)"
        color = "#3b82f6"
        badge = "info"
    elif score >= 50:
        grade = "C"
        classification = "ATENÇÃO (RISCO MÉDIO)"
        color = "#f59e0b"
        badge = "warning"
    else:
        grade = "D"
        classification = "CRÍTICO (AÇÃO IMEDIATA NECESSÁRIA)"
        color = "#ef4444"
        badge = "danger"

    return {
        "score": score,
        "grade": grade,
        "classification": classification,
        "color": color,
        "badge": badge,
        "penalties": penalties
    }

def compare_with_previous_audit(reports_dir: Path, current_state: dict) -> dict:
    """Compara a execução atual com a anterior e gera diff forense."""
    history_dir = reports_dir / ".audit_history"
    history_dir.mkdir(parents=True, exist_ok=True)
    last_state_file = reports_dir / ".last_audit_state.json"

    diff = {
        "has_previous": False,
        "previous_date": None,
        "score_delta": 0,
        "previous_score": None,
        "new_ports": [],
        "closed_ports": [],
        "new_routes_count": 0,
        "new_sensitive": [],
        "fixed_sensitive": []
    }

    if last_state_file.exists():
        try:
            with open(last_state_file, "r", encoding="utf-8") as f:
                last_state = json.load(f)

            diff["has_previous"] = True
            diff["previous_date"] = last_state.get("timestamp_utc", "Anterior")
            diff["previous_score"] = last_state.get("score", 100)
            diff["score_delta"] = current_state.get("score", 100) - diff["previous_score"]

            prev_ports = set(last_state.get("open_ports", []))
            curr_ports = set(current_state.get("open_ports", []))
            diff["new_ports"] = sorted(list(curr_ports - prev_ports))
            diff["closed_ports"] = sorted(list(prev_ports - curr_ports))

            prev_sens = set(last_state.get("sensitive_files", []))
            curr_sens = set(current_state.get("sensitive_files", []))
            diff["new_sensitive"] = sorted(list(curr_sens - prev_sens))
            diff["fixed_sensitive"] = sorted(list(prev_sens - curr_sens))

            prev_routes = last_state.get("routes_count", 0)
            curr_routes = current_state.get("routes_count", 0)
            diff["new_routes_count"] = max(0, curr_routes - prev_routes)

        except Exception:
            pass

    # Gravar o estado atual para o próximo diff
    try:
        with open(last_state_file, "w", encoding="utf-8") as f:
            json.dump(current_state, f, indent=2, ensure_ascii=False)
        
        hist_file = history_dir / f"audit_state_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(hist_file, "w", encoding="utf-8") as f:
            json.dump(current_state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    return diff

def generate_remediation_matrix(metrics: dict, port_list: list, pci_data: dict) -> list:
    """Gera matriz de remediações acionáveis com comandos de terminal em 1 clique."""
    remediations = []

    # 1. Arquivos sensíveis expostos
    if metrics.get("sensitive_files"):
        files = " ".join([f"'{f}'" for f in metrics["sensitive_files"] if os.path.exists(f)])
        if files:
            remediations.append({
                "titulo": "Restringir Permissões de Arquivos Sensíveis (0600)",
                "severidade": "ALTA",
                "categoria": "SISTEMA_E_ARQUIVOS",
                "descricao": f"Arquivos sensíveis ({', '.join(metrics['sensitive_files'][:5])}) foram detectados. Restrinja o acesso ao proprietário e remova do cache Git.",
                "comando": f"chmod 0600 {files} && git rm --cached {files} 2>/dev/null || true"
            })

    # 2. Portas de banco expostas
    risky_ports = [pt for pt in port_list if pt.get("port") in [21, 3306, 5432, 6379, 27017] and pt.get("externally_exposed", False)]
    if risky_ports:
        ports_str = " ".join([str(p["port"]) for p in risky_ports])
        remediations.append({
            "titulo": "Isolar Portas de Bancos / Serviços Locais",
            "severidade": "MÉDIA",
            "categoria": "REDE_E_PORTAS",
            "descricao": f"Portas de banco/serviço ({ports_str}) detectadas escutando em interfaces externas/públicas. Garanta que o bind esteja estritamente em 127.0.0.1.",
            "comando": "python3 -c \"print('[*] Ajuste os arquivos my.cnf, postgresql.conf ou redis.conf para: bind 127.0.0.1')\""
        })

    # 3. Content-Security-Policy (CSP)
    if metrics.get("html_files", 0) > 0 and not metrics.get("csp_enforced"):
        remediations.append({
            "titulo": "Habilitar Cabeçalho de Proteção CSP (Borda / Nginx)",
            "severidade": "MÉDIA",
            "categoria": "CABECALHOS_HTTP",
            "descricao": "Nenhum cabeçalho Content-Security-Policy estrito encontrado. Injete o cabeçalho no proxy reverso ou nos templates HTML.",
            "comando": "echo \"add_header Content-Security-Policy \\\"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';\\\" always;\" >> ./nginx_csp.conf"
        })

    # 4. Falha PCI-DSS / Retenção de PAN
    pci_vulns = len(pci_data.get("verificacao_vulnerabilidade", []))
    if pci_vulns > 0:
        remediations.append({
            "titulo": "Sanitizar e Purgar Retenção Indevida de Cartões / PAN",
            "severidade": "CRÍTICA",
            "categoria": "CONFORMIDADE_FINANCEIRA",
            "descricao": f"{pci_vulns} registro(s) financeiro(s) com retenção inadequada de dados sensíveis de pagamento. Execute varredura DLP corretiva.",
            "comando": "grep -rE \"\\b([0-9]{4}[- ]?){3}[0-9]{4}\\b\" ./reports/ && python3 4-automacao-e-shell/scan_cards_pci.py ."
        })

    # 5. Sanitização SQL / Queries Concatenadas
    if metrics.get("sql_concatenations"):
        remediations.append({
            "titulo": "Parametrizar Consultas SQL Concatenadas",
            "severidade": "MÉDIA",
            "categoria": "BANCO_E_SQL",
            "descricao": f"{len(metrics['sql_concatenations'])} consulta(s) SQL concatenada(s). Substitua strings literais por placeholders parametrizados.",
            "comando": "python3 -c \"print('[*] Refatore queries SQL para usar (?, ?) ou (%s, %s) em vez de f-strings ou operador +' )\""
        })

    if not remediations:
        remediations.append({
            "titulo": "Ambiente em Alta Conformidade",
            "severidade": "INFO",
            "categoria": "GOVERNANCA",
            "descricao": "Nenhuma remediação urgente necessária. Mantenha os backups preventivos e a rotina contínua de auditoria.",
            "comando": "python3 4-automacao-e-shell/pipeline_engine.py match 'check de integridade'"
        })

    return remediations

def generate_interactive_html_dashboard(
    target: str,
    scan_dir: Path,
    score_data: dict,
    diff_data: dict,
    remediations: list,
    pci_data: dict,
    port_list: list,
    static_meta: dict,
    sha_table: list
) -> str:
    """Gera dashboard HTML autônomo, interativo e completo Dark Mode com Glassmorphism e visualizador avançado de APIs e Rotas."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    score = score_data["score"]
    grade = score_data["grade"]
    classification = score_data["classification"]
    color = score_data["color"]

    stroke_offset = 282.74 - (282.74 * (score / 100))

    live = static_meta.get("live_audit_data") or {}
    pci_status = pci_data.get("status_geral_compliance", "CONFORME")

    routes = static_meta.get("routes_discovered", [])
    external_links = static_meta.get("external_links", [])
    webhooks = static_meta.get("webhooks_listeners", [])
    websockets = static_meta.get("websockets_discovered", [])
    api_specs = static_meta.get("api_specs_discovered", [])
    params = static_meta.get("query_params_discovered", [])
    dotfiles = static_meta.get("dotfiles_found", [])
    dbs = static_meta.get("databases_discovered", [])
    caps = static_meta.get("architectural_capabilities", [])
    structs = static_meta.get("structural_files_inventory", [])

    routes_total = len(routes)
    routes_criticas = len([r for r in routes if r.get("risk_level") == "CRITICA"])
    routes_financeiras = len([r for r in routes if r.get("category") == "FINANCEIRA_PAGAMENTO"])
    routes_auth = len([r for r in routes if r.get("category") == "AUTENTICACAO_SESSAO"])
    webhooks_total = len(webhooks)
    websockets_total = len(websockets)
    gateways_total = len([l for l in external_links if l.get("category") == "GATEWAY_PAGAMENTO"])
    ai_total = len([l for l in external_links if l.get("category") == "IA_E_LLM"])
    specs_total = len(api_specs)

    caps_total = len(caps)
    caps_detected = len([c for c in caps if c.get("detected")])
    structs_total = len(structs)
    structs_present = len([s for s in structs if s.get("status") == "PRESENTE"])

    diff_html = ""
    if diff_data["has_previous"]:
        d_val = diff_data["score_delta"]
        d_cls = "diff-up" if d_val >= 0 else "diff-down"
        d_sign = f"+{d_val}" if d_val > 0 else f"{d_val}"
        diff_html = f"""
        <div class="diff-card">
            <h4>🔄 Variação vs Última Auditoria ({diff_data['previous_date']})</h4>
            <div class="diff-metrics">
                <span class="diff-badge {d_cls}">Score: {d_sign} pts</span>
                <span>Portas novas: <strong>{len(diff_data['new_ports'])}</strong></span>
                <span>Novas rotas: <strong>+{diff_data['new_routes_count']}</strong></span>
                <span>Arquivos corrigidos: <strong>{len(diff_data['fixed_sensitive'])}</strong></span>
            </div>
        </div>
        """

    penalties_html = ""
    if score_data["penalties"]:
        penalties_html = "<div class='penalties-box'><h4>⚠️ Penalidades de Risco Detectadas:</h4><ul>"
        for p in score_data["penalties"]:
            penalties_html += f"<li><span class='badge-{p['severidade'].lower()}'>-{p['deducao']} pts</span> {p['motivo']}</li>"
        penalties_html += "</ul></div>"

    remediations_html = ""
    for idx, rem in enumerate(remediations):
        remediations_html += f"""
        <div class="rem-item">
            <div class="rem-header">
                <span class="rem-title">{rem['titulo']}</span>
                <span class="badge-{rem['severidade'].lower()}">{rem['severidade']}</span>
            </div>
            <p class="rem-desc">{rem['descricao']}</p>
            <div class="code-box">
                <code id="cmd_{idx}">{rem['comando']}</code>
                <button class="copy-btn" onclick="copyCode('cmd_{idx}')">Copiar Comando</button>
            </div>
        </div>
        """

    # Linhas da Matriz Arquitetural
    cap_rows = ""
    for c in caps:
        st_badge = '<span class="badge-success">✓ DETECTADO</span>' if c["detected"] else '<span class="badge-info">⚪ NÃO DETECTADO</span>'
        ev_text = ""
        if c["evidence"]:
            ev_parts = [f"<code>{ev['file']}</code> (match: <em>{ev['match']}</em>)" for ev in c["evidence"][:2]]
            ev_text = "<br>".join(ev_parts)
        else:
            ev_text = "<span style='color: var(--text-muted)'>Nenhuma evidência no código</span>"
        cap_rows += f"""<tr data-domain="{c['domain']}" data-status="{'DETECTADO' if c['detected'] else 'NAO_DETECTADO'}">
            <td><span class="badge-domain">{c['domain']}</span></td>
            <td><strong>{c['name']}</strong></td>
            <td>{st_badge}</td>
            <td><div class="evidence-box">{ev_text}</div></td>
        </tr>"""

    # Linhas do Inventário de Arquivos Estruturais
    struct_rows = ""
    for s in structs:
        st_badge = '<span class="badge-success">✓ PRESENTE</span>' if s["status"] == "PRESENTE" else '<span class="badge-critica">⚪ AUSENTE</span>'
        path_text = "<br>".join([f"<code>{p}</code>" for p in s["paths"]]) if s["paths"] else "<span style='color: var(--text-muted)'>-</span>"
        struct_rows += f"""<tr data-category="{s['category']}" data-status="{s['status']}">
            <td><span class="badge-domain">{s['category']}</span></td>
            <td><strong><code>{s['entry']}</code></strong></td>
            <td>{st_badge}</td>
            <td>{path_text}</td>
        </tr>"""

    # Linhas de Rotas
    route_rows = ""
    for r in routes[:250]:
        m_lower = r.get("method", "GET").lower()
        badge_cls = r.get("badge_cls", "badge-info")
        risk = r.get("risk_level", "INFO")
        cat = r.get("category", "RECURSO_REST")
        route_rows += f"""<tr data-category="{cat}" data-risk="{risk}">
            <td><span class="method-badge method-{m_lower}">{r.get('method', 'GET')}</span></td>
            <td><strong><code>{r['route']}</code></strong></td>
            <td><span class="{badge_cls}">{r.get('label', cat)}</span></td>
            <td><span class="badge-type">{r.get('type', 'REST_ENDPOINT')}</span></td>
            <td><span class="file-text">{r['file']}</span></td>
        </tr>"""

    # Linhas de Links Externos
    link_rows = ""
    for l in external_links[:250]:
        cat = l.get("category", "API_EXTERNA")
        cat_badge = "badge-critica" if cat in ["GATEWAY_PAGAMENTO", "IA_E_LLM"] else ("badge-media" if cat == "WEBHOOK_E_MENSAGERIA" else "badge-info")
        link_rows += f"""<tr data-category="{cat}">
            <td><span class="{cat_badge}">{cat}</span></td>
            <td><a href="{l['url']}" target="_blank" rel="noopener noreferrer" class="ext-link">{l['url'][:80]}</a></td>
            <td><span class="file-text">{l['file']}</span></td>
        </tr>"""

    # Linhas de Webhooks Listeners
    webhook_rows = ""
    for wh in webhooks[:50]:
        prot_badge = '<span class="badge-success">✓ ASSINATURA VERIFICADA (HMAC)</span>' if wh.get("signature_verified") else '<span class="badge-critica">⚠️ DESPROTEGIDO (SEM ASSINATURA)</span>'
        webhook_rows += f"""<tr>
            <td><span class="method-badge method-{wh.get('method', 'POST').lower()}">{wh.get('method', 'POST')}</span></td>
            <td><strong><code>{wh['route']}</code></strong></td>
            <td>{prot_badge}</td>
            <td><span class="file-text">{wh['file']}</span></td>
        </tr>"""

    # Linhas de WebSockets
    ws_rows = ""
    for ws in websockets[:50]:
        ws_rows += f"""<tr>
            <td><span class="badge-media">⚡ STREAM / WS</span></td>
            <td><code>{ws['stream']}</code></td>
            <td><span class="file-text">{ws['file']}</span></td>
        </tr>"""

    # Linhas de Specs
    spec_rows = ""
    for sp in api_specs:
        spec_rows += f"""<tr>
            <td><span class="badge-baixa">{sp['format']}</span></td>
            <td><strong>{sp['paths_count']} endpoints declarados</strong></td>
            <td><span class="file-text">{sp['file']}</span></td>
        </tr>"""

    # Linhas de Query Params
    param_rows = ""
    for q in params[:80]:
        p_badge = '<span class="badge-critica">⚠️ SENSÍVEL</span>' if q.get("is_sensitive") else '<span class="badge-baixa">NORMAL</span>'
        param_rows += f"""<tr>
            <td><code>?{q['param']}=</code></td>
            <td>{p_badge}</td>
            <td><span class="badge-type">{q.get('source', 'URL_PARAM')}</span></td>
            <td><span class="file-text">{q['file']}</span></td>
        </tr>"""

    sha_rows = ""
    for item in sha_table:
        sha_rows += f"<tr><td><code>{item['file']}</code></td><td><code class='sha-text'>{item['hash']}</code></td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Executivo — Auditoria Total Sentinela Deep v5.0</title>
    <style>
        :root {{
            --bg-base: #0a0e17;
            --bg-card: rgba(18, 26, 44, 0.75);
            --bg-card-hover: rgba(26, 38, 64, 0.85);
            --border-glass: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-muted: #94a3b8;
            --accent-green: #10b981;
            --accent-blue: #3b82f6;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --score-color: {color};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: radial-gradient(circle at 10% 20%, #111827 0%, #0a0e17 90%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2.5rem 1.5rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1440px; margin: 0 auto; }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-glass);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .logo-box h1 {{
            font-size: 1.95rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa, #c084fc, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }}
        .logo-box p {{ color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem; }}
        .header-meta {{
            text-align: right;
            font-size: 0.85rem;
            color: var(--text-muted);
            background: var(--bg-card);
            padding: 0.6rem 1.1rem;
            border-radius: 8px;
            border: 1px solid var(--border-glass);
        }}
        .hero-grid {{
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        @media(max-width: 980px) {{ .hero-grid {{ grid-template-columns: 1fr; }} }}
        .card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            padding: 1.75rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            margin-bottom: 1.5rem;
        }}
        .score-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            justify-content: center;
        }}
        .score-circle-wrapper {{
            position: relative;
            width: 170px;
            height: 170px;
            margin: 1rem 0;
        }}
        .score-circle-wrapper svg {{ transform: rotate(-90deg); width: 100%; height: 100%; }}
        .score-circle-bg {{ fill: none; stroke: rgba(255, 255, 255, 0.08); stroke-width: 10; }}
        .score-circle-val {{
            fill: none;
            stroke: var(--score-color);
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: 282.74;
            stroke-dashoffset: {stroke_offset};
            transition: stroke-dashoffset 1s ease-out;
        }}
        .score-text-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .score-num {{ font-size: 2.75rem; font-weight: 800; color: var(--score-color); line-height: 1; }}
        .score-grade {{ font-size: 1rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }}
        .classification-tag {{
            font-size: 0.95rem;
            font-weight: 700;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--score-color);
            color: var(--score-color);
            margin-top: 0.5rem;
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .stat-item {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 1.15rem;
        }}
        .stat-label {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-val {{ font-size: 1.45rem; font-weight: 700; margin-top: 0.3rem; color: #fff; }}
        .diff-card {{
            background: rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.25);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-top: 1rem;
        }}
        .diff-card h4 {{ font-size: 0.9rem; margin-bottom: 0.5rem; color: #93c5fd; }}
        .diff-metrics {{ display: flex; gap: 1rem; font-size: 0.85rem; flex-wrap: wrap; align-items: center; }}
        .diff-badge {{ padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.8rem; }}
        .diff-up {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .diff-down {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); border: 1px solid var(--accent-red); }}
        .penalties-box {{
            background: rgba(239, 68, 68, 0.06);
            border: 1px solid rgba(239, 68, 68, 0.25);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
            font-size: 0.85rem;
        }}
        .penalties-box h4 {{ color: #fca5a5; margin-bottom: 0.5rem; }}
        .penalties-box ul {{ list-style: none; }}
        .penalties-box li {{ margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.5rem; }}
        .badge-critica, .badge-alta {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
        .badge-media {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
        .badge-baixa, .badge-info {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
        .badge-success {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
        .badge-type {{ font-size: 0.7rem; color: #a5b4fc; background: rgba(99, 102, 241, 0.15); padding: 0.15rem 0.45rem; border-radius: 4px; border: 1px solid rgba(99, 102, 241, 0.3); }}
        
        /* Method Badges */
        .method-badge {{
            padding: 0.2rem 0.55rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 800;
            font-family: monospace;
            display: inline-block;
            text-align: center;
            min-width: 52px;
        }}
        .method-get {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }}
        .method-post {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid #3b82f6; }}
        .method-put {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #f59e0b; }}
        .method-delete {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }}
        .method-patch {{ background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid #8b5cf6; }}
        .method-handler {{ background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid #06b6d4; }}
        .method-view {{ background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid #64748b; }}
        .method-all {{ background: rgba(255, 255, 255, 0.1); color: #f1f5f9; border: 1px solid rgba(255, 255, 255, 0.2); }}

        /* Interactive Filter Bar */
        .toolbar {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }}
        .search-box {{
            width: 100%;
            background: #050811;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 0.65rem 1rem;
            color: #fff;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s ease;
        }}
        .search-box:focus {{ border-color: #60a5fa; }}
        .chips-container {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        .chip {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            color: var(--text-muted);
            padding: 0.35rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .chip:hover {{ background: rgba(255, 255, 255, 0.12); color: #fff; }}
        .chip.active {{
            background: rgba(96, 165, 250, 0.2);
            color: #93c5fd;
            border-color: #60a5fa;
            font-weight: 700;
        }}

        .section-title {{ font-size: 1.3rem; font-weight: 700; margin: 2rem 0 1rem; display: flex; align-items: center; gap: 0.5rem; }}
        .rem-grid {{ display: grid; gap: 1rem; }}
        .rem-item {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 1.25rem;
        }}
        .rem-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
        .rem-title {{ font-size: 1rem; font-weight: 700; color: #fff; }}
        .rem-desc {{ font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem; }}
        .code-box {{
            background: #050811;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }}
        .code-box code {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.85rem;
            color: #38bdf8;
            word-break: break-all;
        }}
        .copy-btn {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-glass);
            color: #fff;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.75rem;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .copy-btn:hover {{ background: rgba(255, 255, 255, 0.18); border-color: rgba(255, 255, 255, 0.3); }}
        .table-responsive {{ overflow-x: auto; max-height: 520px; overflow-y: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; }}
        th, td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-glass); }}
        th {{ color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; background: rgba(255, 255, 255, 0.02); position: sticky; top: 0; backdrop-filter: blur(8px); }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        .sha-text {{ font-size: 0.75rem; color: #a78bfa; font-family: monospace; }}
        .file-text {{ font-size: 0.75rem; color: #94a3b8; font-family: monospace; }}
        .ext-link {{ color: #60a5fa; text-decoration: none; word-break: break-all; }}
        .ext-link:hover {{ text-decoration: underline; }}
        footer {{
            text-align: center;
            margin-top: 3.5rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border-glass);
            padding-top: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-box">
                <h1>🛡️ SENTINELA | AUDITORIA TOTAL DEEP</h1>
                <p>Laudo Pericial Irrestrito: 100% de Cobertura (APIs, Rotas, Gateways, Webhooks & Schemas)</p>
            </div>
            <div class="header-meta">
                <div>Alvo: <strong>{target}</strong></div>
                <div>Emissão: <strong>{now_utc}</strong></div>
            </div>
        </header>

        <div class="hero-grid">
            <!-- Score Card -->
            <div class="card score-card">
                <span class="stat-label">Índice de Saúde & Segurança</span>
                <div class="score-circle-wrapper">
                    <svg viewBox="0 0 100 100">
                        <circle class="score-circle-bg" cx="50" cy="50" r="45"></circle>
                        <circle class="score-circle-val" cx="50" cy="50" r="45"></circle>
                    </svg>
                    <div class="score-text-center">
                        <span class="score-num">{score}</span>
                        <span class="score-grade">Grau {grade}</span>
                    </div>
                </div>
                <div class="classification-tag">{classification}</div>
            </div>

            <!-- Stats & Diff -->
            <div class="card">
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-label">Rotas & APIs</div>
                        <div class="stat-val" style="color: #60a5fa">{routes_total}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Capacidades Ativas</div>
                        <div class="stat-val" style="color: #34d399">{caps_detected} / {caps_total}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Arquivos Canônicos</div>
                        <div class="stat-val" style="color: #a78bfa">{structs_present} / {structs_total}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Rotas Críticas / Admin</div>
                        <div class="stat-val" style="color: {'#ef4444' if routes_criticas > 0 else '#10b981'}">{routes_criticas}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Rotas Financeiras / Pix</div>
                        <div class="stat-val" style="color: #f59e0b">{routes_financeiras}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Webhooks Listeners</div>
                        <div class="stat-val" style="color: #c084fc">{webhooks_total}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Links & Gateways</div>
                        <div class="stat-val" style="color: #38bdf8">{len(external_links)}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Gateways Pagamento</div>
                        <div class="stat-val" style="color: #10b981">{gateways_total}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Provedores IA / LLM</div>
                        <div class="stat-val" style="color: #a78bfa">{ai_total}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Bancos SQLite</div>
                        <div class="stat-val">{len(dbs)}</div>
                    </div>
                </div>

                {diff_html}
                {penalties_html}
            </div>
        </div>

        <!-- 1. Matriz Arquitetural & Capacidades do Sistema -->
        <h2 class="section-title">🏛️ Matriz Arquitetural & Capacidades do Sistema (27 Domínios, {caps_detected} Detectadas de {caps_total})</h2>
        <div class="card">
            <div class="toolbar">
                <input type="text" id="capSearch" class="search-box" placeholder="🔍 Filtrar capacidades por nome, domínio, termo ou evidência..." onkeyup="filterCapabilities()">
                <div class="chips-container cap-status-chips">
                    <button class="chip active" onclick="setCapStatusFilter('ALL', this)">Todas ({caps_total})</button>
                    <button class="chip" onclick="setCapStatusFilter('DETECTADO', this)">✓ Detectadas ({caps_detected})</button>
                    <button class="chip" onclick="setCapStatusFilter('NAO_DETECTADO', this)">⚪ Não Detectadas ({caps_total - caps_detected})</button>
                </div>
            </div>
            <div class="table-responsive">
                <table id="capsTable">
                    <thead>
                        <tr>
                            <th style="width: 250px">Domínio Técnico</th>
                            <th>Capacidade / Engenharia</th>
                            <th style="width: 140px">Status</th>
                            <th>Evidências / Arquivos de Referência</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cap_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 2. Inventário de Arquivos Estruturais & Canônicos -->
        <h2 class="section-title">📁 Inventário de Arquivos Estruturais & Canônicos ({structs_present} Presentes de {structs_total})</h2>
        <div class="card">
            <div class="toolbar">
                <input type="text" id="structSearch" class="search-box" placeholder="🔍 Filtrar arquivos por nome (.env, Dockerfile, nginx, etc.), categoria ou status..." onkeyup="filterStructuralFiles()">
                <div class="chips-container struct-status-chips">
                    <button class="chip active" onclick="setStructStatusFilter('ALL', this)">Todos ({structs_total})</button>
                    <button class="chip" onclick="setStructStatusFilter('PRESENTE', this)">✓ Presentes ({structs_present})</button>
                    <button class="chip" onclick="setStructStatusFilter('AUSENTE', this)">⚪ Ausentes ({structs_total - structs_present})</button>
                </div>
            </div>
            <div class="table-responsive">
                <table id="structTable">
                    <thead>
                        <tr>
                            <th style="width: 280px">Categoria Estrutural</th>
                            <th>Arquivo Canônico</th>
                            <th style="width: 130px">Status</th>
                            <th>Caminho Identificado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {struct_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 3. Catálogo de Rotas e APIs com Filtro Instantâneo -->
        <h2 class="section-title">📡 Catálogo Completo de Rotas, Contratos e Endpoints de API ({routes_total})</h2>
        <div class="card">
            <div class="toolbar">
                <input type="text" id="routeSearch" class="search-box" placeholder="🔍 Filtrar rotas por endpoint, método, arquivo ou criticidade..." onkeyup="filterRoutes()">
                <div class="chips-container route-chips">
                    <button class="chip active" onclick="setRouteFilter('ALL', this)">Todas ({routes_total})</button>
                    <button class="chip" onclick="setRouteFilter('CRITICA', this)">🔴 Críticas / Admin ({routes_criticas})</button>
                    <button class="chip" onclick="setRouteFilter('FINANCEIRA_PAGAMENTO', this)">🟠 Financeiras / Pix ({routes_financeiras})</button>
                    <button class="chip" onclick="setRouteFilter('AUTENTICACAO_SESSAO', this)">🟡 Autenticação ({routes_auth})</button>
                    <button class="chip" onclick="setRouteFilter('WEBHOOK_CALLBACK', this)">🟣 Webhooks ({webhooks_total})</button>
                    <button class="chip" onclick="setRouteFilter('RECURSO_REST', this)">🔵 REST APIs</button>
                    <button class="chip" onclick="setRouteFilter('STREAM_WEBSOCKET', this)">⚡ WebSockets ({websockets_total})</button>
                </div>
            </div>
            <div class="table-responsive">
                <table id="routesTable">
                    <thead>
                        <tr>
                            <th style="width: 75px">Método</th>
                            <th>Endpoint / Rota</th>
                            <th>Classificação & Criticidade</th>
                            <th>Tipo de Rota</th>
                            <th>Arquivo de Origem</th>
                        </tr>
                    </thead>
                    <tbody>
                        {route_rows if route_rows else '<tr><td colspan="5" style="text-align:center">Nenhuma rota identificada.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 2. Links Externos, Gateways e Conexões com Filtro -->
        <h2 class="section-title">🌐 Conexões de Rede, Gateways & Provedores Externos ({len(external_links)})</h2>
        <div class="card">
            <div class="toolbar">
                <input type="text" id="linkSearch" class="search-box" placeholder="🔍 Filtrar conexões externas por URL, domínio ou categoria..." onkeyup="filterLinks()">
                <div class="chips-container link-chips">
                    <button class="chip active" onclick="setLinkFilter('ALL', this)">Todas ({len(external_links)})</button>
                    <button class="chip" onclick="setLinkFilter('GATEWAY_PAGAMENTO', this)">💳 Gateways Pagamento ({gateways_total})</button>
                    <button class="chip" onclick="setLinkFilter('IA_E_LLM', this)">🤖 Provedores IA / LLM ({ai_total})</button>
                    <button class="chip" onclick="setLinkFilter('WEBHOOK_E_MENSAGERIA', this)">💬 Webhooks & Chat</button>
                    <button class="chip" onclick="setLinkFilter('NUVEM_E_STORAGE', this)">☁️ Nuvem & BaaS</button>
                    <button class="chip" onclick="setLinkFilter('AUTENTICACAO_E_OAUTH', this)">🔑 OAuth & Auth</button>
                </div>
            </div>
            <div class="table-responsive">
                <table id="linksTable">
                    <thead>
                        <tr>
                            <th style="width: 220px">Categoria Estratégica</th>
                            <th>Destino / URL Externa</th>
                            <th>Arquivo de Origem</th>
                        </tr>
                    </thead>
                    <tbody>
                        {link_rows if link_rows else '<tr><td colspan="3" style="text-align:center">Nenhum link externo identificado.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 3. Webhooks & Streams Real-Time -->
        <h2 class="section-title">🪝 Central de Webhooks Listeners & Real-Time Streams ({webhooks_total + websockets_total})</h2>
        <div class="card table-responsive">
            <table>
                <thead>
                    <tr>
                        <th style="width: 75px">Método</th>
                        <th>Endpoint / Stream</th>
                        <th>Proteção de Assinatura</th>
                        <th>Arquivo de Origem</th>
                    </tr>
                </thead>
                <tbody>
                    {webhook_rows}
                    {ws_rows}
                    {'' if (webhook_rows or ws_rows) else '<tr><td colspan="4" style="text-align:center">Nenhum webhook listener ou websocket stream detectado.</td></tr>'}
                </tbody>
            </table>
        </div>

        <!-- 4. Contratos de API (Specs) -->
        {f'''
        <h2 class="section-title">📑 Contratos e Especificações de API ({specs_total})</h2>
        <div class="card table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Formato da Spec</th>
                        <th>Endpoints Declarados</th>
                        <th>Arquivo</th>
                    </tr>
                </thead>
                <tbody>
                    {spec_rows}
                </tbody>
            </table>
        </div>
        ''' if specs_total > 0 else ''}

        <!-- 5. Parâmetros de Consulta Ocultos -->
        <h2 class="section-title">🔍 Parâmetros de Consulta Ocultos (Query Params & Shadow Flags) ({len(params)})</h2>
        <div class="card table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Parâmetro</th>
                        <th>Classificação de Risco</th>
                        <th>Origem da Detecção</th>
                        <th>Arquivo de Origem</th>
                    </tr>
                </thead>
                <tbody>
                    {param_rows if param_rows else '<tr><td colspan="4" style="text-align:center">Nenhum parâmetro extraído.</td></tr>'}
                </tbody>
            </table>
        </div>

        <!-- 6. Remediação Automática -->
        <h2 class="section-title">🛠️ Matriz de Remediação Automática (Comandos de 1 Clique)</h2>
        <div class="rem-grid">
            {remediations_html}
        </div>

        <!-- 7. Hashes SHA-256 -->
        <h2 class="section-title">🔒 Integridade Criptográfica (GitOps Anti-Tampering)</h2>
        <div class="card table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Evidência / Artefato</th>
                        <th>Hash SHA-256 (Checksum)</th>
                    </tr>
                </thead>
                <tbody>
                    {sha_rows}
                </tbody>
            </table>
        </div>

        <footer>
            Sentinela Guardião de Projetos v5.0 Deep Engine • Antigravity Turbinado • Varredura forense irrestrita de APIs e Infraestrutura.
        </footer>
    </div>

    <script>
        let currentRouteCategory = 'ALL';
        function filterRoutes() {{
            const search = document.getElementById('routeSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#routesTable tbody tr');
            rows.forEach(row => {{
                const text = row.innerText.toLowerCase();
                const cat = row.getAttribute('data-category') || '';
                const risk = row.getAttribute('data-risk') || '';
                const matchesSearch = text.includes(search);
                let matchesCat = (currentRouteCategory === 'ALL' || cat === currentRouteCategory);
                if (currentRouteCategory === 'CRITICA') {{
                    matchesCat = (risk === 'CRITICA');
                }}
                row.style.display = (matchesSearch && matchesCat) ? '' : 'none';
            }});
        }}
        function setRouteFilter(cat, btn) {{
            currentRouteCategory = cat;
            document.querySelectorAll('.route-chips .chip').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            filterRoutes();
        }}

        let currentLinkCategory = 'ALL';
        function filterLinks() {{
            const search = document.getElementById('linkSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#linksTable tbody tr');
            rows.forEach(row => {{
                const text = row.innerText.toLowerCase();
                const cat = row.getAttribute('data-category') || '';
                const matchesSearch = text.includes(search);
                const matchesCat = (currentLinkCategory === 'ALL' || cat === currentLinkCategory);
                row.style.display = (matchesSearch && matchesCat) ? '' : 'none';
            }});
        }}
        function setLinkFilter(cat, btn) {{
            currentLinkCategory = cat;
            document.querySelectorAll('.link-chips .chip').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            filterLinks();
        }}

        function copyCode(id) {{
            const codeEl = document.getElementById(id);
            if (!codeEl) return;
            navigator.clipboard.writeText(codeEl.innerText).then(() => {{
                const btn = codeEl.nextElementSibling;
                const oldTxt = btn.innerText;
                btn.innerText = "✓ Copiado!";
                btn.style.borderColor = "var(--accent-green)";
                btn.style.color = "var(--accent-green)";
                setTimeout(() => {{
                    btn.innerText = oldTxt;
                    btn.style.borderColor = "";
                    btn.style.color = "";
                }}, 2000);
            }}).catch(err => {{
                alert("Erro ao copiar: " + err);
            }});
        }}
    </script>
</body>
</html>
"""
    return html

def build_markdown_report(
    target: str,
    scan_dir: Path,
    pci_data: dict,
    port_list: list,
    static_meta: dict,
    score_data: dict,
    diff_data: dict,
    remediations: list,
    sha_table: list
) -> str:
    """Gera o laudo unificado consolidado em Markdown com cobertura 100% detalhada de APIs, rotas e infra."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    pci_status = pci_data.get("status_geral_compliance", "CONFORME")

    score = score_data["score"]
    grade = score_data["grade"]
    classification = score_data["classification"]

    routes = static_meta.get("routes_discovered", [])
    external_links = static_meta.get("external_links", [])
    webhooks = static_meta.get("webhooks_listeners", [])
    websockets = static_meta.get("websockets_discovered", [])
    api_specs = static_meta.get("api_specs_discovered", [])
    params = static_meta.get("query_params_discovered", [])
    dotfiles = static_meta.get("dotfiles_found", [])
    dbs = static_meta.get("databases_discovered", [])
    caps = static_meta.get("architectural_capabilities", [])
    structs = static_meta.get("structural_files_inventory", [])

    routes_criticas = [r for r in routes if r.get("risk_level") == "CRITICA"]
    caps_detected = [c for c in caps if c.get("detected")]
    structs_present = [s for s in structs if s.get("status") == "PRESENTE"]
    routes_fin = [r for r in routes if r.get("category") == "FINANCEIRA_PAGAMENTO"]

    md = []
    md.append("# LAUDO TÉCNICO PERICIAL: AUDITORIA TOTAL DEEP (14 CAMADAS)")
    md.append(f"**Ecossistema:** Sentinela Guardião / Antigravity Turbinado v5.0  ")
    md.append(f"**Data da Execução:** `{now_utc}`  ")
    md.append(f"**Alvo Inspecionado:** `{target}`  ")
    md.append(f"**Workspace:** `{scan_dir}`  ")
    md.append(f"**Score de Segurança & Saúde:** `{score}/100` (Grau `{grade}` — `{classification}`)  ")
    md.append(f"**Dashboard Interativo:** [`reports/dashboard_auditoria.html`](file://{scan_dir}/reports/dashboard_auditoria.html)  \n")

    # Score Box
    md.append("> [!IMPORTANT]")
    md.append(f"> **ÍNDICE DE SAÚDE TÉCNICA: {score}/100 — GRAU {grade} ({classification})**  ")
    if score_data["penalties"]:
        md.append("> **Penalidades Identificadas:**")
        for p in score_data["penalties"]:
            md.append(f"> - `-{p['deducao']} pts` | [{p['severidade']}] {p['motivo']}")
    else:
        md.append("> Nenhuma penalidade de segurança identificada. Todas as camadas operam em conformidade máxima.")
    md.append("")

    # Diff Comparativo
    if diff_data["has_previous"]:
        md.append("---")
        md.append("## 🔄 COMPARATIVO FORENSE (DIFF COM EXECUÇÃO ANTERIOR)\n")
        d_val = diff_data["score_delta"]
        sign = f"+{d_val}" if d_val > 0 else f"{d_val}"
        md.append(f"- **Data da Última Auditoria:** `{diff_data['previous_date']}`")
        md.append(f"- **Variação do Score:** `{sign} pts` (Anterior: `{diff_data['previous_score']}/100` ➔ Atual: `{score}/100`)")
        if diff_data["new_routes_count"]:
            md.append(f"- **Novas Rotas Descobertas:** `+{diff_data['new_routes_count']}`")
        if diff_data["new_ports"]:
            md.append(f"- **Novas Portas Detectadas:** `{diff_data['new_ports']}`")
        if diff_data["closed_ports"]:
            md.append(f"- **Portas Fechadas / Desativadas:** `{diff_data['closed_ports']}`")
        if diff_data["fixed_sensitive"]:
            md.append(f"- **Arquivos Críticos Removidos / Corrigidos:** `{diff_data['fixed_sensitive']}`")
        if diff_data["new_sensitive"]:
            md.append(f"- **⚠️ Novos Arquivos Críticos Expostos:** `{diff_data['new_sensitive']}`")
        md.append("")

    # Matriz de Remediação
    md.append("---")
    md.append("## 🛠️ MATRIZ DE REMEDIAÇÃO AUTOMÁTICA (COMANDOS PRONTOS)\n")
    for r in remediations:
        md.append(f"### {r['titulo']} `[{r['severidade']}]`")
        md.append(f"{r['descricao']}\n")
        md.append("```bash")
        md.append(r["comando"])
        md.append("```\n")

    # Seção 1: Matriz Arquitetural
    md.append("---")
    md.append(f"## 1. MATRIZ ARQUITETURAL & CAPACIDADES DO SISTEMA ({len(caps_detected)} DETECTADAS DE {len(caps)} INSPECIONADAS)\n")
    md.append("| Domínio Técnico | Capacidade Arquitetural | Status | Evidências / Arquivo |")
    md.append("| :--- | :--- | :--- | :--- |")
    for c in caps_detected[:60]:
        ev = f"`{c['evidence'][0]['file']}` (match: `{c['evidence'][0]['match']}`)" if c["evidence"] else "-"
        md.append(f"| `{c['domain']}` | **{c['name']}** | `✓ DETECTADO` | {ev} |")
    if len(caps_detected) > 60:
        md.append(f"\n_... e mais {len(caps_detected) - 60} capacidades ativas catalogadas no painel `reports/dashboard_auditoria.html`._\n")
    md.append("")

    # Seção 2: Inventário de Arquivos Estruturais
    md.append("---")
    md.append(f"## 2. INVENTÁRIO DE ARQUIVOS ESTRUTURAIS & CANÔNICOS ({len(structs_present)} PRESENTES DE {len(structs)} INSPECIONADOS)\n")
    md.append("| Categoria Estrutural | Arquivo Canônico | Status | Caminho Local Encontrado |")
    md.append("| :--- | :--- | :--- | :--- |")
    for s in structs:
        if s["status"] == "PRESENTE":
            paths_str = ", ".join([f"`{p}`" for p in s["paths"][:2]])
            md.append(f"| `{s['category']}` | **`{s['entry']}`** | `✓ PRESENTE` | {paths_str} |")
    md.append("")

    # Seção 3: Mapeamento de Rotas e APIs
    md.append("---")
    md.append(f"## 3. ROTAS, CONTRATOS E ENDPOINTS DE API DESCOBERTOS ({len(routes)})\n")
    if routes_criticas:
        md.append(f"> [!WARNING]\n> **Atenção:** {len(routes_criticas)} rota(s) de privilégio administrativo ou debug identificada(s)!\n")
    if routes:
        md.append("| Método | Rota / Endpoint | Categoria | Risco | Arquivo de Origem |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for r in routes[:60]:
            md.append(f"| `{r.get('method', 'GET')}` | **`{r['route']}`** | `{r.get('category', 'REST')}` | `{r.get('risk_level', 'INFO')}` | `{r['file']}` |")
        if len(routes) > 60:
            md.append(f"\n_... e mais {len(routes) - 60} rotas catalogadas no painel interativo `reports/dashboard_auditoria.html`._\n")
    else:
        md.append("Nenhuma rota ou endpoint explícito localizado no código-fonte.\n")

    # Seção 2: Links Externos e Gateways
    md.append("---")
    md.append(f"## 4. LINKS EXTERNOS, GATEWAYS, IAS & WEBHOOKS CONECTADOS ({len(external_links)})\n")
    if external_links:
        md.append("| Categoria | URL / Destino Externo | Arquivo de Origem |")
        md.append("| :--- | :--- | :--- |")
        for l in external_links[:50]:
            md.append(f"| `{l['category']}` | [{l['url'][:65]}...]({l['url']}) | `{l['file']}` |")
        if len(external_links) > 50:
            md.append(f"\n_... e mais {len(external_links) - 50} conexões externas mapeadas no dashboard interativo._\n")
    else:
        md.append("Nenhum link ou gateway externo identificado nos arquivos.\n")

    # Seção 3: Webhooks & Streams Real-Time
    md.append("---")
    md.append(f"## 5. WEBHOOKS LISTENERS & REAL-TIME STREAMS ({len(webhooks) + len(websockets)})\n")
    if webhooks:
        md.append("### Webhooks Listeners (Incoming Endpoints):")
        md.append("| Método | Endpoint | Proteção de Assinatura | Arquivo |")
        md.append("| :--- | :--- | :--- | :--- |")
        for wh in webhooks[:20]:
            p_text = "✓ Protegido (HMAC)" if wh.get("signature_verified") else "⚠️ **DESPROTEGIDO**"
            md.append(f"| `{wh.get('method', 'POST')}` | `{wh['route']}` | {p_text} | `{wh['file']}` |")
        md.append("")
    if websockets:
        md.append(f"### WebSockets & Event Streams ({len(websockets)}):")
        for ws in websockets[:10]:
            md.append(f"- `⚡ {ws['stream']}` em `{ws['file']}`")
        md.append("")

    # Seção 4: Contratos de API
    if api_specs:
        md.append("---")
        md.append(f"## 6. CONTRATOS E ESPECIFICAÇÕES DE API ({len(api_specs)})\n")
        for sp in api_specs:
            md.append(f"- **`{sp['format']}`**: `{sp['paths_count']}` endpoints em `{sp['file']}`")
        md.append("")

    # Seção 5: Parâmetros de Consulta e Shadow APIs
    md.append("---")
    md.append(f"## 7. PARÂMETROS DE CONSULTA (QUERY PARAMS & SHADOW APIS) ({len(params)})\n")
    if params:
        md.append("| Parâmetro | Classificação de Risco | Origem | Arquivo de Origem |")
        md.append("| :--- | :--- | :--- | :--- |")
        for q in params[:40]:
            risco = "⚠️ **SENSÍVEL**" if q.get("is_sensitive") else "Normal"
            md.append(f"| `?{q['param']}=` | {risco} | `{q.get('source', 'URL')}` | `{q['file']}` |")
    else:
        md.append("Nenhum parâmetro de URL extraído.\n")

    # Seção 6: Arquivos Ocultos, Dotfiles e Bancos
    md.append("---")
    md.append(f"## 8. ARQUIVOS OCULTOS (DOTFILES) & BANCOS DE DADOS LOCAIS\n")
    md.append(f"- **Dotfiles Mapeados ({len(dotfiles)}):** {', '.join([f'`{d}`' for d in dotfiles[:15]]) or 'Nenhum'}")
    if dbs:
        md.append(f"- **Bancos de Dados SQLite Físicos Encontrados:**")
        for db in dbs:
            md.append(f"  • `{db['file']}`: `{db['table_count']}` tabelas mapeadas: `{', '.join(db['tables'][:10])}`")
    else:
        md.append("- **Bancos SQLite Locais:** Nenhum arquivo .sqlite ou .db encontrado.")
    md.append("")

    # Seção 7: DOM Oculto e Client-Side
    md.append("---")
    md.append("## 9. CLIENT-SIDE OCULTO, DOM & METADADOS DE SESSÃO\n")
    md.append(f"- **Inputs Password Desmascarados:** `{static_meta['unmasked_passwords']}`")
    md.append(f"- **Inputs type='hidden' Localizados:** `{static_meta['hidden_inputs']}`")
    if static_meta["hidden_inputs_details"]:
        md.append("  • **Amostra de Inputs Ocultos:**")
        for hi in static_meta["hidden_inputs_details"][:5]:
            md.append(f"    - Campo: `{hi['name']}` | Valor: `{hi['value']}` em `{hi['file']}`")
    md.append(f"- **Variáveis Globais de State / Hidratação:** `{', '.join(static_meta['hydration_variables']) or 'Nenhuma'}`")
    if static_meta["html_comments_suspicious"]:
        md.append(f"- **Comentários de Desenvolvedores com Palavras Suspeitas ({len(static_meta['html_comments_suspicious'])}):**")
        for sc in static_meta["html_comments_suspicious"][:5]:
            md.append(f"  • `<!-- {sc['comment']} -->` em `{sc['file']}`")
    md.append("")

    # Integridade Criptográfica
    md.append("---")
    md.append("## 10. INTEGRIDADE CRIPTOGRÁFICA & GITOPS ANTI-TAMPERING\n")
    md.append("Hashes SHA-256 de integridade de todas as evidências periciais geradas:\n")
    for item in sha_table:
        md.append(f"- `{item['file']}`: `{item['hash']}`")
    md.append("")

    md.append("---")
    md.append("## 11. RECOMENDAÇÕES E PRÓXIMOS PASSOS\n")
    md.append("1. **Proteger Endpoints Internos:** Assegure autenticação em rotas sensíveis e APIs de debug.")
    md.append("2. **Isolar Webhooks e Chaves:** Mantenha credenciais de pagamento estritamente em segredos do CI/CD.")
    md.append("3. **Visualização:** Abra o painel interativo local via `open reports/dashboard_auditoria.html`.")
    md.append("\n_Emitido automaticamente pelo Sentinela Guardião de Projetos (v5.0 Deep Engine)._")

    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Compilador do Laudo da Auditoria Total Deep")
    parser.add_argument("target", nargs="?", default=".", help="Alvo auditado (diretório ou URL)")
    parser.add_argument("--output", "-o", default=None, help="Caminho do arquivo Markdown de saída")
    parser.add_argument("--quick", action="store_true", help="Modo rápido (timeout reduzido e varredura expressa)")
    args = parser.parse_args()

    scan_dir = Path(args.target).resolve() if not args.target.startswith("http") else Path.cwd().resolve()
    reports_dir = scan_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = Path(args.output) if args.output else reports_dir / f"audit_total_{timestamp}.md"
    latest_file = reports_dir / "audit_total_latest.md"
    canonical_file = reports_dir / "LAUDO_AUDITORIA_TOTAL.md"
    dashboard_file = reports_dir / "dashboard_auditoria.html"

    # 1. Carrega dados de PCI
    pci_file = reports_dir / "compliance_pci_audit.json"
    pci_data = {}
    if pci_file.exists():
        try:
            with open(pci_file, "r", encoding="utf-8") as f:
                pci_data = json.load(f)
        except Exception:
            pass

    # 2. Varre portas locais (com suporte a quick)
    timeout_port = 0.02 if args.quick else 0.08
    ports_to_scan = [80, 443, 3000, 8000, 8080] if args.quick else None
    port_list = scan_local_ports("127.0.0.1", ports=ports_to_scan, timeout=timeout_port)

    # 2.1 Inspeção ativa de cabeçalhos HTTP nas portas abertas mapeadas (Camada 13)
    http_headers_inspections = []
    for p_info in port_list:
        p_num = p_info["port"]
        h_res = inspect_http_headers("127.0.0.1", p_num)
        if h_res["http_responding"]:
            http_headers_inspections.append(h_res)

    # 3. Análise estática profunda (100% de cobertura)
    static_meta = analyze_workspace_static(scan_dir)
    static_meta["http_security_headers"] = http_headers_inspections

    # 4. Cálculo do Score Unificado (0 a 100)
    score_data = calculate_security_score(static_meta, port_list, pci_data)

    # 5. Auditoria Comparativa (Diff Forense)
    current_state = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "target": args.target,
        "score": score_data["score"],
        "grade": score_data["grade"],
        "open_ports": [p["port"] for p in port_list],
        "routes_count": len(static_meta.get("routes_discovered", [])),
        "sensitive_files": static_meta.get("sensitive_files", []),
        "secrets_count": len(static_meta.get("secrets_found", [])),
        "webshells_count": len(static_meta.get("webshells_found", []))
    }
    diff_data = compare_with_previous_audit(reports_dir, current_state)

    # 6. Matriz de Remediação Automática
    remediations = generate_remediation_matrix(static_meta, port_list, pci_data)

    # 7. Tabela de Hashes SHA-256
    sha_table = []
    if reports_dir.exists():
        for r_file in sorted(reports_dir.glob("*.json")):
            if not r_file.name.startswith("."):
                sha_table.append({"file": f"reports/{r_file.name}", "hash": calculate_sha256(r_file)})
    dict_file = Path(__file__).parent / "dicionario_lexico.json"
    if dict_file.exists():
        sha_table.append({"file": "dicionario_lexico.json", "hash": calculate_sha256(dict_file)})

    # 8. Compila o Laudo Markdown
    md_content = build_markdown_report(
        args.target, scan_dir, pci_data, port_list, static_meta,
        score_data, diff_data, remediations, sha_table
    )

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(canonical_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    # Gravação explícita do laudo do projeto para evitar colisões com laudos pessoais
    project_canonical_file = reports_dir / "LAUDO_AUDITORIA_PROJETO.md"
    with open(project_canonical_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 9. Compila o Dashboard Visual HTML
    html_content = generate_interactive_html_dashboard(
        args.target, scan_dir, score_data, diff_data, remediations,
        pci_data, port_list, static_meta, sha_table
    )
    with open(dashboard_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    project_dashboard_file = reports_dir / "dashboard_auditoria_projeto.html"
    with open(project_dashboard_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 9.1 Compilação do PDF Executivo via Google Chrome se disponível
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    pdf_out = reports_dir / "LAUDO_AUDITORIA_TOTAL.pdf"
    if os.path.exists(chrome_path):
        import subprocess
        try:
            subprocess.run([
                chrome_path,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_out}",
                f"file://{dashboard_file}"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # 10. Exibição no Terminal
    score = score_data["score"]
    grade = score_data["grade"]
    classification = score_data["classification"]
    routes = static_meta.get("routes_discovered", [])
    routes_c = len(routes)
    routes_criticas = len([r for r in routes if r.get("risk_level") == "CRITICA"])
    routes_fin = len([r for r in routes if r.get("category") == "FINANCEIRA_PAGAMENTO"])
    links_c = len(static_meta.get("external_links", []))
    gateways_c = len([l for l in static_meta.get("external_links", []) if l.get("category") == "GATEWAY_PAGAMENTO"])
    ai_c = len([l for l in static_meta.get("external_links", []) if l.get("category") == "IA_E_LLM"])
    webhooks_c = len(static_meta.get("webhooks_listeners", []))
    dotfiles_c = len(static_meta.get("dotfiles_found", []))

    print("\n" + "═" * 78)
    print(f"📋 LAUDO PERICIAL SENTINELA v5.0 DEEP — SCORE: {score}/100 (GRAU {grade})")
    print("═" * 78)
    print(f"🎯 Classificação:       [{classification}]")
    print(f"🎯 Alvo Inspecionado:   {args.target} {'[MODO RÁPIDO]' if args.quick else '[MODO PROFUNDO]'}")
    print(f"📁 Diretório Workspace: {scan_dir}")
    caps_detected_c = len([c for c in static_meta.get("architectural_capabilities", []) if c.get("detected")])
    caps_total_c = len(static_meta.get("architectural_capabilities", []))
    structs_pres_c = len([s for s in static_meta.get("structural_files_inventory", []) if s.get("status") == "PRESENTE"])
    structs_tot_c = len(static_meta.get("structural_files_inventory", []))

    doms_tot_c = len(set(c.get("domain") for c in static_meta.get("architectural_capabilities", [])))
    cats_tot_c = len(set(s.get("category") for s in static_meta.get("structural_files_inventory", [])))

    print(f"📊 Cobertura Forense:   {static_meta['total_files_scanned']} arquivos analisados")
    print(f"🏛️ Matriz Arquitetural: {caps_detected_c} de {caps_total_c} capacidades ativas ({doms_tot_c} domínios)")
    print(f"📁 Arquivos Canônicos:  {structs_pres_c} de {structs_tot_c} arquivos identificados ({cats_tot_c} categorias)")
    print(f"📡 Rotas & APIs:        {routes_c} endpoints ({routes_criticas} admin/críticas, {routes_fin} financeiras)")
    print(f"🪝 Webhooks Listeners:  {webhooks_c} endpoints de callback mapeados")
    print(f"🌐 Conexões de Rede:    {links_c} destinos ({gateways_c} pagamentos, {ai_c} IAs/LLMs)")
    print(f"📁 Dotfiles Ocultos:    {dotfiles_c} arquivos .env/ocultos inspecionados")
    if diff_data["has_previous"]:
        d_val = diff_data["score_delta"]
        sign = f"+{d_val}" if d_val > 0 else f"{d_val}"
        print(f"🔄 Diff vs Anterior:    {sign} pts (Anterior: {diff_data['previous_score']} em {diff_data['previous_date']})")
    print("─" * 78)
    print("🛠️ REMEDIAÇÕES RECOMENDADAS:")
    for rem in remediations[:3]:
        print(f"  ▶ [{rem['severidade']}] {rem['titulo']}")
        print(f"    Comando: {rem['comando'][:65]}...")
    print("─" * 78)
    print(f"📄 Laudo Markdown:      {canonical_file}")
    print(f"🌐 Dashboard Visual:    open \"{dashboard_file}\"")
    print(f"🔒 SHA-256 do Laudo:    {calculate_sha256(canonical_file)}")
    print("═" * 78 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
