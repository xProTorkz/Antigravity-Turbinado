#!/usr/bin/env python3
"""
License Guard & Hardware Fingerprint Lock — Antigravity Turbinado
================================================================
Garante a proteção contra pirataria e compartilhamento não autorizado:
- Vincula cada licença ao Telegram User ID do comprador.
- Trava no primeiro uso no HWID (Hardware UUID) e IP da máquina do cliente.
- Impede a execução da instalação em máquinas não autorizadas.
"""

import os
import sys
import hmac
import hashlib
import json
import sqlite3
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

SECRET_SALT = b"AntigravityTurbinado_HWID_Security_2026_xProTorkz"

def get_machine_hwid() -> str:
    """Obtém o identificador único e imutável de hardware da máquina atual."""
    hwid = ""
    # macOS
    if sys.platform == "darwin":
        try:
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/ { split($0, a, \"\\\"\"); print a[4] }'"
            hwid = subprocess.check_output(cmd, shell=True, text=True).strip()
        except Exception:
            pass
        if not hwid:
            try:
                cmd = "system_profiler SPHardwareDataType | awk '/Hardware UUID/{print $3}'"
                hwid = subprocess.check_output(cmd, shell=True, text=True).strip()
            except Exception:
                pass

    # Linux
    elif sys.platform.startswith("linux"):
        for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        hwid = f.read().strip()
                        if hwid:
                            break
                except Exception:
                    pass

    # Windows
    elif sys.platform == "win32":
        try:
            cmd = 'powershell -NoProfile -Command "(Get-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Cryptography).MachineGuid"'
            hwid = subprocess.check_output(cmd, shell=True, text=True).strip()
        except Exception:
            pass
        if not hwid:
            try:
                cmd = "wmic csproduct get uuid"
                lines = subprocess.check_output(cmd, shell=True, text=True).strip().splitlines()
                if len(lines) > 1:
                    hwid = lines[1].strip()
            except Exception:
                pass

    # Fallback seguro
    if not hwid:
        import uuid
        hwid = f"FALLBACK-{uuid.getnode()}"

    return hwid

def get_client_public_ip() -> str:
    """Detecta o endereço IP público da máquina para auditoria e binding."""
    for service in ["https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip"]:
        try:
            req = urllib.request.Request(service, headers={"User-Agent": "curl/7.68.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                ip = resp.read().decode("utf-8").strip()
                if ip:
                    return ip
        except Exception:
            pass
    return "127.0.0.1"

def generate_license_key(telegram_user_id: int, plan_id: str = "core") -> str:
    """Gera chave de licença determinística e criptograficamente assinada."""
    plan_code = "PRO" if "pro" in plan_id.lower() else "CORE"
    data = f"{telegram_user_id}:{plan_code}".encode()
    signature = hmac.new(SECRET_SALT, data, hashlib.sha256).hexdigest()[:12].upper()
    return f"TURBO-{plan_code}-{telegram_user_id}-{signature}"

def verify_license_signature(license_key: str):
    """Verifica criptograficamente se a chave possui assinatura autêntica da nossa chave privada."""
    parts = license_key.strip().split("-")
    if len(parts) == 4 and parts[0] == "TURBO":
        plan_code = parts[1].upper()
        try:
            user_id = int(parts[2])
        except ValueError:
            return False, 0, ""
        expected_sig = hmac.new(SECRET_SALT, f"{user_id}:{plan_code}".encode(), hashlib.sha256).hexdigest()[:12].upper()
        if hmac.compare_digest(parts[3].upper(), expected_sig):
            plan_id = "combo_pro" if plan_code == "PRO" else "core"
            return True, user_id, plan_id
    elif len(parts) == 3 and parts[0] == "TURBO":
        # Formato de compatibilidade TURBO-<user_id>-<sig>
        try:
            user_id = int(parts[1])
        except ValueError:
            return False, 0, ""
        for p in ["core", "combo_pro"]:
            for d_str in ["", f":{datetime.now().strftime('%Y%m%d')}", f":{datetime.now().strftime('%Y%m%d%H%M')}"]:
                expected_sig = hmac.new(SECRET_SALT, f"{user_id}:{p}{d_str}".encode(), hashlib.sha256).hexdigest()[:12].upper()
                if hmac.compare_digest(parts[2].upper(), expected_sig):
                    return True, user_id, p
    return False, 0, ""

def get_license_db_path() -> Path:
    # Procura banco de dados no Sharkbot ou na pasta local
    sharkbot_db = Path("/Users/lucasvinicius/projetos/Sharkbot/data/antigravity_turbinado_licenses.db")
    if sharkbot_db.parent.exists():
        return sharkbot_db
    local_db = Path.home() / ".gemini" / "antigravity" / "licenses.db"
    local_db.parent.mkdir(parents=True, exist_ok=True)
    return local_db

def init_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key     TEXT UNIQUE NOT NULL,
            user_id         INTEGER NOT NULL,
            plan_id         TEXT NOT NULL,
            hwid            TEXT,
            ip              TEXT,
            status          TEXT DEFAULT 'pending',
            created_at      TEXT NOT NULL,
            activated_at    TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_license(user_id: int, plan_id: str, license_key: str):
    db_path = get_license_db_path()
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("""
            INSERT OR REPLACE INTO licenses (license_key, user_id, plan_id, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        """, (license_key, user_id, plan_id, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()

def verify_and_bind_license(license_key: str, current_hwid: str, current_ip: str) -> dict:
    """
    Verifica a validade da licença e realiza o binding no HWID do cliente.
    Regra: 1 licença = 1 máquina física exclusiva.
    """
    # 1. Validação Criptográfica Estrita da Assinatura (Fail-Closed)
    is_valid, user_id, plan_id = verify_license_signature(license_key)
    if not is_valid:
        return {
            "ok": False,
            "error": "INVALID_LICENSE_SIGNATURE",
            "message": "FALHA CRÍTICA: Assinatura de licença inválida ou falsificada. Adquira sua licença oficial no Telegram: @xprotorkzbot"
        }

    # 2. Verificação no Banco de Dados de Licenças
    db_path = get_license_db_path()
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    try:
        row = cur.execute("SELECT user_id, plan_id, hwid, ip, status FROM licenses WHERE license_key=?", (license_key,)).fetchone()
        bound_hwid = row[2] if row else None
        status = row[4] if row else "pending"

        # Caso 1: Primeiro uso (Binding permanente do HWID e IP)
        if not bound_hwid or status == "pending":
            now_iso = datetime.now().isoformat()
            cur.execute("""
                INSERT OR REPLACE INTO licenses (license_key, user_id, plan_id, hwid, ip, status, created_at, activated_at)
                VALUES (?, ?, ?, ?, ?, 'active', coalesce((SELECT created_at FROM licenses WHERE license_key=?), ?), ?)
            """, (license_key, user_id, plan_id, current_hwid, current_ip, license_key, now_iso, now_iso))
            conn.commit()
            return {
                "ok": True,
                "status": "ACTIVATED_FIRST_TIME",
                "plan_id": plan_id,
                "user_id": user_id,
                "hwid": current_hwid,
                "ip": current_ip,
                "message": "Licença personalizada vinculada com sucesso a esta máquina física!"
            }

        # Caso 2: Máquina já autorizada (HWID idêntico)
        if bound_hwid == current_hwid:
            cur.execute("UPDATE licenses SET ip=? WHERE license_key=?", (current_ip, license_key))
            conn.commit()
            return {
                "ok": True,
                "status": "AUTHORIZED",
                "plan_id": plan_id,
                "user_id": user_id,
                "hwid": current_hwid,
                "message": "Acesso verificado e autorizado nesta máquina."
            }

        # Caso 3: HWID diferente -> TENTATIVA DE COMPARTILHAMENTO / PIRATARIA
        return {
            "ok": False,
            "error": "HWID_MISMATCH",
            "message": f"VIOLAÇÃO DE COMPARTILHAMENTO: Esta licença do Telegram ID {user_id} já está vinculada a outro computador (HWID {bound_hwid[:8]}...). Não é permitido compartilhar seu link de instalação."
        }
    finally:
        conn.close()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="License Guard & Hardware Lock")
    parser.add_argument("--hwid", action="store_true", help="Exibe o HWID desta máquina")
    parser.add_argument("--ip", action="store_true", help="Exibe o IP público detectado")
    parser.add_argument("--generate", type=int, help="Gera chave para Telegram User ID")
    parser.add_argument("--verify", type=str, help="Verifica e vincula uma chave de licença")
    parser.add_argument("--plan", type=str, default="core", help="Plano (core ou combo_pro)")
    args = parser.parse_args()

    hwid = get_machine_hwid()
    ip = get_client_public_ip()

    if args.hwid:
        print(f"HWID: {hwid}")
        return

    if args.ip:
        print(f"IP: {ip}")
        return

    if args.generate:
        key = generate_license_key(args.generate, args.plan)
        register_license(args.generate, args.plan, key)
        print(f"LICENSE_KEY={key}")
        return

    if args.verify:
        result = verify_and_bind_license(args.verify, hwid, ip)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if not result["ok"]:
            sys.exit(1)
        return

    print("Use --hwid, --ip, --generate <user_id> ou --verify <key>")

if __name__ == "__main__":
    main()
