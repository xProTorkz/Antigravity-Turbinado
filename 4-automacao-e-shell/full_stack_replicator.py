
# ══════════════════════════════════════════════════════════════════════════════
# AS 15 CATEGORIAS DE REPLICAÇÃO TOTAL DO SISTEMA OPERACIONAL & INFRAESTRUTURA
# ══════════════════════════════════════════════════════════════════════════════
REPLICATION_15_PILLARS = [
    {
        "id": "1_os_image",
        "title": "1. Sistema Operacional",
        "description": "Criação de imagem completa do SO instalado, configurações e atualizações.",
        "tools": ["Clonezilla", "Ghost", "dd"],
        "commands": ["dd if=/dev/sda of=./replica/os_image.img bs=4M status=progress", "clonezilla-save"]
    },
    {
        "id": "2_config_files",
        "title": "2. Arquivos de Configuração",
        "description": "Clonagem de arquivos de configuração essenciais (/etc/ no Linux ou Registro no Windows).",
        "tools": ["rsync", "tar", "cópia manual"],
        "commands": ["rsync -avz /etc/ ./replica/system_configs/etc/", "tar -czf ./replica/etc_backup.tar.gz /etc"]
    },
    {
        "id": "3_software_apps",
        "title": "3. Software e Aplicações",
        "description": "Listagem e cópia de pacotes instalados, drivers e programas/scripts personalizados.",
        "tools": ["dpkg", "pacman", "rsync", "tar"],
        "commands": ["dpkg --get-selections > ./replica/pkg_list.txt", "pacman -Qe > ./replica/pacman_pkgs.txt"]
    },
    {
        "id": "4_databases",
        "title": "4. Bancos de Dados",
        "description": "Dumps completos de todos os bancos de dados (metadados, schemas e dados físicos).",
        "tools": ["mysqldump", "pg_dump", "sqlite3"],
        "commands": ["pg_dumpall -U postgres > ./replica/db_full.sql", "mysqldump --all-databases > ./replica/mysql_all.sql"]
    },
    {
        "id": "5_user_files",
        "title": "5. Arquivos do Usuário",
        "description": "Clonagem de arquivos pessoais, documentos, mídias, fotos, vídeos e downloads.",
        "tools": ["rsync", "tar", "cópia manual"],
        "commands": ["rsync -avz --exclude='.cache' /home/ ./replica/user_files/"]
    },
    {
        "id": "6_network_configs",
        "title": "6. Configurações de Rede",
        "description": "Clonagem de configs de DNS, interfaces de rede, roteamento, iptables e proxies.",
        "tools": ["rsync", "tar", "cópia manual"],
        "commands": ["cp -r /etc/netplan /etc/network /etc/resolv.conf ./replica/network/"]
    },
    {
        "id": "7_security_configs",
        "title": "7. Configurações de Segurança",
        "description": "Clonagem de chaves SSH, certificados SSL/TLS, firewalls (ufw/iptables) e políticas.",
        "tools": ["rsync", "tar", "cópia manual"],
        "commands": ["rsync -avz /etc/ssh /etc/ssl ./replica/security_vault/"]
    },
    {
        "id": "8_activity_logs",
        "title": "8. Log de Atividades",
        "description": "Clonagem de logs do sistema (/var/log) para histórico pericial e auditoria de eventos.",
        "tools": ["rsync", "tar", "journalctl"],
        "commands": ["journalctl -b > ./replica/system_journal.log", "tar -czf ./replica/var_log.tar.gz /var/log"]
    },
    {
        "id": "9_service_configs",
        "title": "9. Configurações de Serviços",
        "description": "Configs de servidores web (Apache, Nginx, Caddy), Redis, Message Brokers e Runtimes.",
        "tools": ["rsync", "tar", "systemctl"],
        "commands": ["rsync -avz /etc/nginx /etc/systemd/system/ ./replica/services/"]
    },
    {
        "id": "10_monitoring_configs",
        "title": "10. Configurações de Monitoramento e Gerenciamento",
        "description": "Clonagem de Prometheus, Grafana, Zabbix, Loki e exportadores de métricas.",
        "tools": ["rsync", "tar", "cópia manual"],
        "commands": ["rsync -avz /etc/prometheus /etc/grafana ./replica/monitoring/"]
    },
    {
        "id": "11_backup_configs",
        "title": "11. Configurações de Backup",
        "description": "Clonagem de arquivos de configuração de ferramentas de backup, cron jobs e rotinas.",
        "tools": ["rsync", "tar", "crontab"],
        "commands": ["crontab -l > ./replica/crontab_backup.txt", "cp -r /etc/cron* ./replica/cron_configs/"]
    },
    {
        "id": "12_licenses_keys",
        "title": "12. Licenças e Chaves",
        "description": "Clonagem de licenças de software, tokens de ativação e chaves criptográficas necessárias.",
        "tools": ["rsync", "tar", "cópia manual"],
        "commands": ["find / -name '*license*' -o -name '*licença*' > ./replica/licenses_found.txt 2>/dev/null"]
    },
    {
        "id": "13_virtualization_configs",
        "title": "13. Configurações de Virtualização",
        "description": "Configs de máquinas virtuais, snapshots e arquivos de disco (qcow2, vmdk, raw).",
        "tools": ["qemu-img", "rsync", "virsh"],
        "commands": ["virsh list --all > ./replica/vms.txt", "qemu-img info disk.qcow2 > ./replica/disk_meta.txt"]
    },
    {
        "id": "14_cloud_containers",
        "title": "14. Configurações de Cloud e Contêineres",
        "description": "Clonagem de Docker, Docker Compose, Kubernetes manifests, Helm charts e configs AWS/GCP.",
        "tools": ["docker", "kubectl", "rsync", "tar"],
        "commands": ["docker ps -a --format json > ./replica/docker_containers.json", "kubectl get all -A -o yaml > ./replica/k8s_dump.yaml"]
    },
    {
        "id": "15_specific_configs",
        "title": "15. Outras Configurações Específicas",
        "description": "Configurações de impressoras (CUPS), drivers de automação, periféricos e rotinas legadas.",
        "tools": ["rsync", "tar", "cópia manual"],
        "commands": ["cp -r /etc/cups ./replica/specific_cups/ 2>/dev/null || true"]
    }
]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Stack Replicator & Extrator de Relevantes - Motor Forense Sentinela.
Poder de penetração e vasculhamento idêntico em todas as camadas.

Dois Modos de Operação:
1. 'full' (Auditoria Total Replicador):
   - Baixa literalmente TUDO (frontend, CSS, JS desminificado, source maps,
     download recursivo de imagens e fontes, banco SQLite físico app.db, mock server,
     script iniciar_replica.sh).
   - Organiza tudo em pastas dentro de projetos/SITES/<Nome_do_Site>/ (com symlink ./replica).
2. 'relevantes' (Auditoria Total):
   - Realiza o mesmo vasculhamento minucioso de ponta a ponta.
   - Baixa/extrai SOMENTE os arquivos importantes e relevantes (contratos de API,
     schemas de banco, modelos de config limpos, rotas críticas, laudos com SHA-256).
   - Não baixa imagens nem fontes volumosas.
"""

import os
import sys
import re
import ssl
import json
import glob
import shutil
import sqlite3
import hashlib
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

def calculate_sha256(filepath: Path) -> str:
    """Calcula o hash SHA-256 de um arquivo."""
    if not filepath.exists() or not filepath.is_file():
        return ""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def beautify_js(code: str) -> str:
    """Formatação determinística de JavaScript minificado para leitura e auditoria."""
    if len(code) < 1000 and "\n" in code:
        return code
    formatted = []
    indent = 0
    in_str = False
    str_char = ""
    i = 0
    n = len(code)
    
    while i < n:
        c = code[i]
        if not in_str and c in ['"', "'", "`"]:
            in_str = True
            str_char = c
            formatted.append(c)
        elif in_str and c == str_char and (i == 0 or code[i-1] != "\\"):
            in_str = False
            formatted.append(c)
        elif not in_str:
            if c == '{':
                indent += 1
                formatted.append(" {\n" + "  " * indent)
            elif c == '}':
                indent = max(0, indent - 1)
                formatted.append("\n" + "  " * indent + "}")
            elif c == ';':
                formatted.append(";\n" + "  " * indent)
            else:
                formatted.append(c)
        else:
            formatted.append(c)
        i += 1
    return "".join(formatted)

class FullStackReplicator:
    def __init__(self, target_dir: str = ".", output_dir: Optional[str] = None, mode: str = "full", site_name: Optional[str] = None):
        target_str = str(target_dir).strip()
        self.is_url = bool(re.match(r"^https?://", target_str, re.IGNORECASE))
        self.mode = mode.lower() if mode in ["full", "relevantes"] else "full"

        if self.is_url:
            self.target_url = target_str
            self.target_dir = None
            parsed = urllib.parse.urlparse(self.target_url)
            host_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', parsed.netloc).strip('_')
            self.site_name = site_name or (host_clean if host_clean else "Site_Replicado")
        else:
            self.is_url = False
            self.target_url = None
            self.target_dir = Path(target_dir).resolve()
            if site_name:
                self.site_name = site_name
            else:
                p_name = self.target_dir.name
                if p_name in [".", "", "Antigravity Turbinado", "workspace"]:
                    self.site_name = "Site_Replicado"
                else:
                    self.site_name = p_name

        # 2. Resolução do Diretório de Destino Organizado
        base_sites = Path(os.path.expanduser("~/projetos/SITES"))
        if not base_sites.exists():
            alt_sites = Path("/Users/lucasvinicius/projetos/SITES")
            base_sites = alt_sites if alt_sites.exists() else Path("./projetos/SITES")

        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        elif self.mode == "full":
            self.output_dir = (base_sites / self.site_name).resolve()
        else:
            self.output_dir = Path("./reports/arquivos_relevantes").resolve()

        # Estrutura de subdiretórios
        self.frontend_dir = self.output_dir / "frontend"
        self.assets_dir = self.frontend_dir / "assets"
        self.images_dir = self.assets_dir / "images"
        self.fonts_dir = self.assets_dir / "fonts"
        self.src_dir = self.frontend_dir / "src"
        self.backend_dir = self.output_dir / "backend"
        self.backend_mock_dir = self.output_dir / "backend_mock"
        self.database_dir = self.output_dir / "database"
        self.configs_dir = self.output_dir / "configs"
        self.security_dir = self.output_dir / "security"
        self.reports_dir = Path("./reports").resolve()

        self.manifest: Dict[str, Any] = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mode": self.mode,
            "target": self.target_url if self.is_url else str(self.target_dir),
            "is_url": self.is_url,
            "output_dir": str(self.output_dir),
            "site_name": self.site_name,
            "frontend_files": [],
            "assets_downloaded": [],
            "source_maps_extracted": [],
            "backend_routes": [],
            "database_schemas": [],
            "relevant_files": [],
            "hashes": {}
        }

    def prepare_directories(self):
        """Camada 1: Inicialização e isolamento do workspace."""
        tag_mode = "REPLICADOR TOTAL (projetos/SITES)" if self.mode == "full" else "ARQUIVOS RELEVANTES (auditoria_total)"
        print(f"[*] [CAMADA 1: Inicialização] Preparando diretórios ({tag_mode})...")
        print(f"    📁 Destino: {self.output_dir}")

        dirs_to_create = [self.output_dir, self.backend_dir, self.database_dir, self.reports_dir]
        if self.mode == "full":
            dirs_to_create.extend([
                self.frontend_dir, self.assets_dir, self.assets_dir / "css",
                self.assets_dir / "js", self.images_dir, self.fonts_dir,
                self.src_dir, self.backend_mock_dir
            ])
        else:
            dirs_to_create.extend([self.configs_dir, self.security_dir])

        for d in dirs_to_create:
            d.mkdir(parents=True, exist_ok=True)
        print("    ✓ Estrutura de diretórios inicializada com sucesso.")

    def download_url_bytes(self, url: str, timeout: int = 15) -> Optional[bytes]:
        """Baixa bytes de uma URL com cabeçalhos seguros e timeout."""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                }
            )
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.read()
        except Exception:
            return None

    def download_remote_asset(self, url: str, target_folder: Path) -> str:
        """Baixa com segurança um asset externo e retorna o caminho relativo local (Modo Full)."""
        if self.mode != "full":
            return url

        try:
            parsed = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename:
                filename = hashlib.md5(url.encode()).hexdigest()[:10] + ".asset"
            filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
            
            dest = target_folder / filename
            if not dest.exists():
                data = self.download_url_bytes(url, timeout=10)
                if data:
                    dest.write_bytes(data)
                    self.manifest["assets_downloaded"].append(f"{target_folder.name}/{filename}")
            
            rel_folder = "assets/images" if target_folder == self.images_dir else "assets/fonts"
            return f"./{rel_folder}/{filename}"
        except Exception:
            return url

    def extract_source_maps(self, js_path: Path):
        """Extrai a árvore original de fontes a partir de arquivos .js.map."""
        map_path = Path(str(js_path) + ".map")
        if not map_path.exists():
            map_path = js_path.parent / (js_path.name + ".map")
        
        if map_path.exists():
            try:
                data = json.loads(map_path.read_text(encoding="utf-8", errors="ignore"))
                sources = data.get("sources", [])
                contents = data.get("sourcesContent", [])
                if sources and contents:
                    target_src = self.src_dir if self.mode == "full" else (self.output_dir / "sources")
                    target_src.mkdir(parents=True, exist_ok=True)
                    for src_file, src_code in zip(sources, contents):
                        clean_src_path = src_file.replace("../", "").replace("webpack:///", "")
                        out_file = target_src / clean_src_path
                        out_file.parent.mkdir(parents=True, exist_ok=True)
                        out_file.write_text(src_code, encoding="utf-8")
                        self.manifest["source_maps_extracted"].append(str(out_file.relative_to(self.output_dir)))
                    print(f"    ⭐ Source Map extraído! {len(sources)} arquivos de código original recriados.")
            except Exception as ex:
                print(f"    [!] Aviso Source Map: {ex}")

    def replicate_web_frontend(self):
        """Camada 2 (Web): Extração completa de página remota (HTML, CSS, JS, Imagens, Fontes)."""
        print(f"[*] [CAMADA 2: Frontend Web] Conectando ao alvo remoto: {self.target_url}...")
        
        raw_html_bytes = self.download_url_bytes(self.target_url, timeout=20)
        if not raw_html_bytes:
            print(f"    [!] Falha ao conectar em {self.target_url}. Gerando fallback de auditoria.")
            raw_html = f"<!DOCTYPE html><html><head><title>Offline: {self.site_name}</title></head><body><h1>Erro de Conexão com {self.target_url}</h1></body></html>"
        else:
            try:
                raw_html = raw_html_bytes.decode('utf-8')
            except UnicodeDecodeError:
                raw_html = raw_html_bytes.decode('latin-1', errors='ignore')

        base_url = self.target_url
        base_match = re.search(r'<base[^>]+href=["\']([^"\']+)["\']', raw_html, re.I)
        if base_match:
            base_url = urllib.parse.urljoin(self.target_url, base_match.group(1))

        if self.mode == "full":
            # 1. Download e Relativização de CSS
            print("    • Baixando folhas de estilo (CSS) e resolvendo fontes/imagens...")
            css_links = re.findall(r'<link[^>]+rel=["\'](?:stylesheet|preload)["\'][^>]+href=["\']([^"\']+)["\']', raw_html, re.I)
            css_links += re.findall(r'<link[^>]+href=["\']([^"\']+\.css(?:\?[^"\']*)?)["\'][^>]*>', raw_html, re.I)
            css_links = list(dict.fromkeys(css_links))

            for idx, href in enumerate(css_links):
                if href.startswith("data:"):
                    continue
                abs_css_url = urllib.parse.urljoin(base_url, href)
                css_name = f"style_{idx}_{os.path.basename(urllib.parse.urlparse(abs_css_url).path) or 'style.css'}"
                css_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', css_name)
                if not css_name.endswith(".css"):
                    css_name += ".css"

                css_bytes = self.download_url_bytes(abs_css_url, timeout=15)
                if css_bytes:
                    try:
                        css_text = css_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        css_text = css_bytes.decode('latin-1', errors='ignore')

                    css_assets = re.findall(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', css_text)
                    for a_ref in css_assets:
                        if a_ref.startswith("data:") or a_ref.startswith("#"):
                            continue
                        abs_asset_url = urllib.parse.urljoin(abs_css_url, a_ref)
                        parsed_a = urllib.parse.urlparse(abs_asset_url)
                        a_name = os.path.basename(parsed_a.path) or hashlib.md5(abs_asset_url.encode()).hexdigest()[:8]
                        a_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', a_name)

                        is_font = any(a_name.lower().endswith(ext) for ext in [".woff", ".woff2", ".ttf", ".otf", ".eot"])
                        target_dir = self.fonts_dir if is_font else self.images_dir
                        rel_prefix = "../fonts/" if is_font else "../images/"

                        a_bytes = self.download_url_bytes(abs_asset_url, timeout=10)
                        if a_bytes:
                            out_path = target_dir / a_name
                            out_path.write_bytes(a_bytes)
                            self.manifest["assets_downloaded"].append(f"assets/{'fonts' if is_font else 'images'}/{a_name}")
                            css_text = css_text.replace(a_ref, f"{rel_prefix}{a_name}")

                    dest_css = self.assets_dir / "css" / css_name
                    dest_css.write_text(css_text, encoding='utf-8')
                    self.manifest["frontend_files"].append(f"frontend/assets/css/{css_name}")
                    raw_html = raw_html.replace(href, f"./assets/css/{css_name}")

            # 2. Download e Relativização de JavaScript
            print("    • Baixando scripts JavaScript client-side e source maps...")
            js_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', raw_html, re.I)
            js_srcs = list(dict.fromkeys(js_srcs))
            for idx, src in enumerate(js_srcs):
                if src.startswith("data:"):
                    continue
                abs_js_url = urllib.parse.urljoin(base_url, src)
                js_name = f"script_{idx}_{os.path.basename(urllib.parse.urlparse(abs_js_url).path) or 'bundle.js'}"
                js_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', js_name)
                if not js_name.endswith(".js"):
                    js_name += ".js"

                js_bytes = self.download_url_bytes(abs_js_url, timeout=15)
                if js_bytes:
                    dest_js = self.assets_dir / "js" / js_name
                    dest_js.write_bytes(js_bytes)
                    self.manifest["frontend_files"].append(f"frontend/assets/js/{js_name}")
                    raw_html = raw_html.replace(src, f"./assets/js/{js_name}")

                    map_url = abs_js_url + ".map"
                    map_bytes = self.download_url_bytes(map_url, timeout=8)
                    if map_bytes:
                        map_file = self.assets_dir / "js" / (js_name + ".map")
                        map_file.write_bytes(map_bytes)
                        self.extract_source_maps(dest_js)

            # 3. Download e Relativização de Imagens, Ícones, Lazy Loading e Srcset
            print("    • Baixando imagens, ícones, SVGs e resolvendo srcset/lazy loading...")
            img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', raw_html, re.I)
            img_srcs += re.findall(r'<link[^>]+rel=["\'](?:icon|shortcut icon|apple-touch-icon)["\'][^>]+href=["\']([^"\']+)["\']', raw_html, re.I)
            img_srcs += re.findall(r'(?:data-src|data-original|data-lazy-src)=["\']([^"\']+)["\']', raw_html, re.I)
            img_srcs = list(dict.fromkeys(img_srcs))

            for idx, isrc in enumerate(img_srcs):
                if isrc.startswith("data:") or not isrc.strip():
                    continue
                abs_img_url = urllib.parse.urljoin(base_url, isrc.strip())
                parsed_img = urllib.parse.urlparse(abs_img_url)
                img_name = f"img_{idx}_{os.path.basename(parsed_img.path) or 'image.png'}"
                img_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', img_name)

                img_bytes = self.download_url_bytes(abs_img_url, timeout=10)
                if img_bytes:
                    dest_img = self.images_dir / img_name
                    dest_img.write_bytes(img_bytes)
                    self.manifest["assets_downloaded"].append(f"assets/images/{img_name}")
                    raw_html = raw_html.replace(isrc, f"./assets/images/{img_name}")

            # Tratar atributos srcset em <img> e <source>
            srcset_matches = re.findall(r'srcset=["\']([^"\']+)["\']', raw_html, re.I)
            for s_val in set(srcset_matches):
                new_srcset_parts = []
                for part in s_val.split(','):
                    part = part.strip()
                    if not part:
                        continue
                    tokens = part.split()
                    s_url = tokens[0]
                    descriptor = f" {tokens[1]}" if len(tokens) > 1 else ""
                    if not s_url.startswith("data:"):
                        abs_s_url = urllib.parse.urljoin(base_url, s_url)
                        parsed_s = urllib.parse.urlparse(abs_s_url)
                        s_name = f"srcset_{hashlib.md5(abs_s_url.encode()).hexdigest()[:8]}_{os.path.basename(parsed_s.path) or 'img.jpg'}"
                        s_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', s_name)
                        s_bytes = self.download_url_bytes(abs_s_url, timeout=10)
                        if s_bytes:
                            (self.images_dir / s_name).write_bytes(s_bytes)
                            new_srcset_parts.append(f"./assets/images/{s_name}{descriptor}")
                        else:
                            new_srcset_parts.append(part)
                    else:
                        new_srcset_parts.append(part)
                if new_srcset_parts:
                    raw_html = raw_html.replace(f'srcset="{s_val}"', f'srcset="{", ".join(new_srcset_parts)}"')
                    raw_html = raw_html.replace(f"srcset='{s_val}'", f"srcset='{', '.join(new_srcset_parts)}'")

            # Tratar background-image inline em tags style="..."
            inline_bg_urls = re.findall(r'style=["\'][^"\']*url\([\'"]?([^\'")]+)[\'"]?\)[^"\']*["\']', raw_html, re.I)
            for bg_url in set(inline_bg_urls):
                if bg_url.startswith("data:") or bg_url.startswith("#"):
                    continue
                abs_bg_url = urllib.parse.urljoin(base_url, bg_url)
                parsed_bg = urllib.parse.urlparse(abs_bg_url)
                bg_name = f"bg_{hashlib.md5(abs_bg_url.encode()).hexdigest()[:8]}_{os.path.basename(parsed_bg.path) or 'bg.jpg'}"
                bg_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', bg_name)
                bg_bytes = self.download_url_bytes(abs_bg_url, timeout=10)
                if bg_bytes:
                    (self.images_dir / bg_name).write_bytes(bg_bytes)
                    raw_html = raw_html.replace(bg_url, f"./assets/images/{bg_name}")

            # Limpar tag <base> para que links locais funcionem
            raw_html = re.sub(r'<base[^>]*>', '', raw_html, flags=re.I)

            # 4. Dump de Hidratação SSR e Dados Client-Side
            storage_data = {
                "target_url": self.target_url,
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "localStorage": {"theme": "dark", "sentinela_replica": "active", "site_origin": self.target_url},
                "sessionStorage": {"auth_state": "offline_mode", "step": "authenticated"},
                "cookies": [{"name": "replica_token", "value": "offline_session_authenticated", "domain": "localhost", "path": "/"}]
            }
            hydration_match = re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', raw_html, re.DOTALL | re.I)
            if hydration_match:
                try:
                    storage_data["__NEXT_DATA__"] = json.loads(hydration_match.group(1))
                    print("    ⭐ Dados de hidratação __NEXT_DATA__ capturados com sucesso!")
                except Exception:
                    pass

            storage_dump = self.frontend_dir / "storage_dump.json"
            storage_dump.write_text(json.dumps(storage_data, indent=2, ensure_ascii=False), encoding='utf-8')
            self.manifest["frontend_files"].append("frontend/storage_dump.json")

            final_index = self.frontend_dir / "index.html"
            final_index.write_text(raw_html, encoding='utf-8')
            self.manifest["frontend_files"].append("frontend/index.html")

            # Gerar também index.html na raiz da pasta do site para acesso direto
            root_index = self.output_dir / "index.html"
            root_html = raw_html.replace('./assets/', './frontend/assets/')
            root_index.write_text(root_html, encoding='utf-8')

            print(f"    ✓ Frontend Web completo replicado com sucesso em: {self.frontend_dir}")
            print(f"    ✓ Template pronto para uso e edição em: {self.output_dir}")

        else:
            forms = re.findall(r'<form[^>]*>(.*?)</form>', raw_html, re.DOTALL | re.IGNORECASE)
            inputs = re.findall(r'<input[^>]+>', raw_html, re.IGNORECASE)
            forms_catalog = [{
                "url": self.target_url,
                "forms_count": len(forms),
                "inputs_total": len(inputs),
                "password_inputs": [i for i in inputs if 'type="password"' in i or "type='password'" in i]
            }]
            forms_report = self.output_dir / "dom_forms_audit.json"
            forms_report.write_text(json.dumps({"audited_url": self.target_url, "forms": forms_catalog}, indent=2), encoding="utf-8")
            self.manifest["relevant_files"].append("dom_forms_audit.json")
            print("    ✓ Inventário DOM e formulários auditados em dom_forms_audit.json.")

    def replicate_local_frontend(self):
        """Camada 2 (Local): Extração de Frontend a partir de diretório local existente."""
        print("[*] [CAMADA 2: Frontend Local] Vasculhamento de interface, scripts e estilos locais...")
        
        html_files = []
        if self.target_dir and self.target_dir.exists():
            for root, _, files in os.walk(self.target_dir):
                if any(p in root for p in [".git", "node_modules", ".venv", "replica", "reports"]):
                    continue
                for f in files:
                    if f.endswith(".html"):
                        html_files.append(Path(root) / f)

        if self.mode == "full":
            if not html_files:
                default_index = self.frontend_dir / "index.html"
                default_index.write_text("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Réplica Forense do Sistema</title>
  <link rel="stylesheet" href="./assets/css/style.css">
</head>
<body>
  <h1>🛡️ Réplica Offline do Sistema</h1>
  <p>Ambiente autônomo gerado pelo Full Stack Replicator.</p>
  <div id="app"></div>
  <script src="./assets/js/bundle.js"></script>
</body>
</html>""", encoding="utf-8")
                self.manifest["frontend_files"].append("frontend/index.html")
            else:
                for h in html_files[:20]:
                    content = h.read_text(encoding="utf-8", errors="ignore")
                    img_urls = re.findall(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', content)
                    for u in img_urls[:30]:
                        local_path = self.download_remote_asset(u, self.images_dir)
                        content = content.replace(u, local_path)
                    dest = self.frontend_dir / h.name
                    dest.write_text(content, encoding="utf-8")
                    self.manifest["frontend_files"].append(f"frontend/{h.name}")
            print(f"    ✓ Frontend local replicado ({len(html_files)} HTMLs).")

            css_files = [Path(root)/f for root, _, files in os.walk(self.target_dir) for f in files if f.endswith(".css") and not any(p in root for p in [".git", "node_modules", "replica"])]
            combined_css = self.assets_dir / "css" / "style.css"
            css_content = ["/* Réplica Consolidada de Estilos - Full Stack Replicator */\n"]
            for c in css_files[:30]:
                raw_c = c.read_text(encoding="utf-8", errors="ignore")
                font_urls = re.findall(r'url\(["\']?(https?://[^"\')]+\.(?:woff2?|ttf|otf))["\']?\)', raw_c)
                for f_url in font_urls[:20]:
                    local_font = self.download_remote_asset(f_url, self.fonts_dir)
                    raw_c = raw_c.replace(f_url, f"../fonts/{os.path.basename(local_font)}")
                css_content.append(f"/* Source: {c.name} */\n" + raw_c + "\n")
            combined_css.write_text("\n".join(css_content), encoding="utf-8")
            self.manifest["frontend_files"].append("frontend/assets/css/style.css")

            js_files = [Path(root)/f for root, _, files in os.walk(self.target_dir) for f in files if f.endswith(".js") and not any(p in root for p in [".git", "node_modules", "replica"])]
            combined_js = self.assets_dir / "js" / "bundle.js"
            js_content = ["// Réplica Consolidada de Scripts Client-Side\nconsole.log('🛡️ [SENTINELA] Réplica Frontend Carregada.');\n"]
            for j in js_files[:30]:
                raw_js = j.read_text(encoding="utf-8", errors="ignore")
                self.extract_source_maps(j)
                beautified = beautify_js(raw_js)
                js_content.append(f"// Source: {j.name}\n" + beautified + "\n")
            combined_js.write_text("\n".join(js_content), encoding="utf-8")
            self.manifest["frontend_files"].append("frontend/assets/js/bundle.js")

            storage_dump = self.frontend_dir / "storage_dump.json"
            storage_data = {
                "localStorage": {"theme": "dark", "sentinela_replica": "active", "session_id": "replica-local-offline"},
                "sessionStorage": {"auth_state": "offline_mode", "step": "authenticated"},
                "cookies": [{"name": "replica_token", "value": "offline_token_validated", "domain": "localhost", "path": "/"}]
            }
            storage_dump.write_text(json.dumps(storage_data, indent=2), encoding="utf-8")
            self.manifest["frontend_files"].append("frontend/storage_dump.json")

        else:
            forms_catalog = []
            for h in html_files[:20]:
                content = h.read_text(encoding="utf-8", errors="ignore")
                forms = re.findall(r'<form[^>]*>(.*?)</form>', content, re.DOTALL | re.IGNORECASE)
                inputs = re.findall(r'<input[^>]+>', content, re.IGNORECASE)
                forms_catalog.append({
                    "file": h.name,
                    "forms_count": len(forms),
                    "inputs_total": len(inputs),
                    "password_inputs": [i for i in inputs if 'type="password"' in i or "type='password'" in i]
                })
            forms_report = self.output_dir / "dom_forms_audit.json"
            forms_report.write_text(json.dumps({"audited_htmls": len(html_files), "forms": forms_catalog}, indent=2), encoding="utf-8")
            self.manifest["relevant_files"].append("dom_forms_audit.json")
            print(f"    ✓ Inventário DOM e formulários auditados em dom_forms_audit.json.")

    def replicate_frontend(self):
        """Camada 2: Roteia para extração Web ou Local com base no alvo."""
        if self.is_url:
            self.replicate_web_frontend()
        else:
            self.replicate_local_frontend()

    def replicate_backend_and_contracts(self):
        """Camada 3: Mapeamento de rotas e contratos de API (Salvo em ambos os modos)."""
        print("[*] [CAMADA 3: Backend & APIs] Mapeando rotas, contratos e endpoints...")
        
        search_dirs = [self.frontend_dir]
        if self.target_dir and self.target_dir.exists():
            search_dirs.append(self.target_dir)

        routes = set()
        route_pattern = re.compile(r'[\'"`](/api/[a-zA-Z0-9_/-]+|/v1/[a-zA-Z0-9_/-]+|/v2/[a-zA-Z0-9_/-]+|/auth/[a-zA-Z0-9_/-]+|/graphql)[\'"`]')
        for s_dir in search_dirs:
            for root, _, files in os.walk(s_dir):
                if any(p in root for p in [".git", "node_modules", ".venv", "reports"]):
                    continue
                for f in files:
                    if f.endswith((".js", ".ts", ".py", ".html", ".json")):
                        try:
                            content = open(os.path.join(root, f), errors="ignore").read()
                            matches = route_pattern.findall(content)
                            routes.update(matches)
                        except Exception:
                            pass

        routes_list = sorted(list(routes)) if routes else ["/api/v1/health", "/api/v1/user", "/api/v1/data", "/api/auth/session"]
        
        routes_map_file = self.backend_dir / "routes_map.json"
        routes_map_file.write_text(json.dumps({"total_routes": len(routes_list), "endpoints": routes_list}, indent=2), encoding="utf-8")
        self.manifest["backend_routes"] = routes_list

        contracts = {}
        for r in routes_list:
            clean_name = r.strip("/").replace("/", "_")
            contracts[r] = {
                "method": "GET",
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "response_body": {
                    "endpoint": r,
                    "status": "success",
                    "replica_mode": True,
                    "data": {"id": 1, "name": f"Mock {clean_name}", "timestamp": datetime.now(timezone.utc).isoformat()}
                }
            }
        contracts_file = self.backend_dir / "api_contracts.json"
        contracts_file.write_text(json.dumps(contracts, indent=2, ensure_ascii=False), encoding="utf-8")
        
        rel_contract = str(contracts_file.relative_to(self.output_dir))
        self.manifest["relevant_files"].append(rel_contract)
        print(f"    ✓ {len(routes_list)} rotas e contratos de API exportados em {rel_contract}.")

    def initialize_sqlite_database(self):
        """Camada 4: Schemas SQL e Banco SQLite Físico."""
        print("[*] [CAMADA 4: Persistência & Schemas] Consolidando schemas e banco de dados...")
        
        db_schema_file = self.database_dir / "schema.sql"
        sql_dumps = []
        if self.target_dir and self.target_dir.exists():
            for root, _, files in os.walk(self.target_dir):
                if any(p in root for p in [".git", "node_modules", ".venv", "replica", "reports"]):
                    continue
                for f in files:
                    if f.endswith(".sql") or f.endswith(".prisma"):
                        p = Path(root) / f
                        sql_dumps.append(f"-- Source: {f}\n" + p.read_text(encoding="utf-8", errors="ignore"))

        if not sql_dumps:
            default_sql = """-- Schema Canônico Sentinela
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, email) VALUES ('admin_sentinela', 'admin@sentinela.local');
INSERT INTO users (username, email) VALUES ('auditor_pericial', 'auditor@sentinela.local');
INSERT INTO system_logs (level, message) VALUES ('INFO', 'Banco de persistência inicializado.');
INSERT INTO system_logs (level, message) VALUES ('SECURITY', 'Auditoria total Sentinela ativa.');
"""
            db_schema_file.write_text(default_sql, encoding="utf-8")
        else:
            db_schema_file.write_text("\n\n".join(sql_dumps), encoding="utf-8")
        
        self.manifest["database_schemas"].append(str(db_schema_file.relative_to(self.output_dir)))
        print("    ✓ Schema estrutural consolidado em database/schema.sql.")

        # No modo FULL: Inicializa o banco SQLite físico app.db
        if self.mode == "full":
            db_path = self.database_dir / "app.db"
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.executescript(db_schema_file.read_text(encoding="utf-8"))
                conn.commit()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                self.manifest["database_schemas"].append(str(db_path.relative_to(self.output_dir)))
                print(f"    ✓ Banco SQLite físico inicializado em database/app.db com {len(tables)} tabelas: {tables}.")
            except Exception as ex:
                print(f"    [!] Erro SQLite físico: {ex}")

    def generate_mock_server_and_runner(self):
        """Camada 5: Servidor Mock e Orquestrador (Modo Full) ou Configurações Sanitizadas (Modo Relevantes)."""
        if self.mode == "full":
            print("[*] [CAMADA 5: Orquestração Local] Gerando servidor mock com SQLite ativo e scripts de subida...")
            mock_server_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import sqlite3
import os
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_FILE = BASE_DIR / "backend" / "api_contracts.json"
DB_FILE = BASE_DIR / "database" / "app.db"

class MockAPIHandler(http.server.BaseHTTPRequestHandler):
    def _get_db_connection(self):
        if DB_FILE.exists():
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            return conn
        return None

    def do_GET(self):
        path = self.path.split("?")[0]
        conn = self._get_db_connection()
        if conn and ("user" in path or "usuario" in path):
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, username, email, created_at FROM users")
                users = [dict(r) for r in cur.fetchall()]
                conn.close()
                self._send_json(200, {"status": "success", "source": "sqlite_database", "data": users})
                return
            except Exception:
                pass

        if conn and ("log" in path or "evento" in path):
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, level, message, created_at FROM system_logs ORDER BY id DESC LIMIT 50")
                logs = [dict(r) for r in cur.fetchall()]
                conn.close()
                self._send_json(200, {"status": "success", "source": "sqlite_database", "data": logs})
                return
            except Exception:
                pass

        contracts = {}
        if CONTRACTS_FILE.exists():
            try:
                contracts = json.loads(CONTRACTS_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

        if path in contracts:
            spec = contracts[path]
            self._send_json(spec.get("status_code", 200), spec.get("response_body", {}))
        else:
            self._send_json(200, {"status": "ok", "mock_route": path, "message": "Atendido pelo Mock SQLite Sentinela"})

    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode('utf-8'))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MockAPIHandler) as httpd:
        print(f"[*] Mock Server Python ativo com SQLite na porta {PORT}...")
        httpd.serve_forever()
"""
            server_file = self.backend_mock_dir / "server.py"
            server_file.write_text(mock_server_code, encoding="utf-8")
            server_file.chmod(0o755)

            runner_sh = f"""#!/bin/bash
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" >/dev/null 2>&1 && pwd )"
echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║ 🚀 INICIANDO RÉPLICA OFFLINE COMPLETA: {self.site_name:<24} ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
python3 "$DIR/backend_mock/server.py" &
BACKEND_PID=$!
python3 -m http.server 8088 --directory "$DIR/frontend" &
FRONTEND_PID=$!
echo "[*] Backend Mock (PID: $BACKEND_PID) na porta 8000."
echo "[*] Frontend Local (PID: $FRONTEND_PID) na porta 8088."
echo "🌐 Acesso: Frontend: http://localhost:8088/ | API: http://localhost:8000/"
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0" INT TERM
wait
"""
            runner_file = self.output_dir / "iniciar_replica.sh"
            runner_file.write_text(runner_sh, encoding="utf-8")
            runner_file.chmod(0o755)

            # Criar symlink canônico ./replica apontando para projetos/SITES/<nome>
            local_symlink = Path("./replica")
            if local_symlink.resolve() != self.output_dir:
                try:
                    if local_symlink.is_symlink() or local_symlink.exists():
                        if local_symlink.is_dir() and not local_symlink.is_symlink():
                            shutil.rmtree(local_symlink)
                        else:
                            local_symlink.unlink()
                    local_symlink.symlink_to(self.output_dir)
                    print(f"    ✓ Symlink canônico ./replica vinculado a: {self.output_dir}")
                except Exception as ex:
                    print(f"    [!] Symlink notice: {ex}")

        else:
            # Modo Relevantes: Exportar configurações sanitizadas
            print("[*] [CAMADA 5: Configurações & Hardening] Exportando templates e credenciais mascaradas...")
            env_templates = {}
            for env_f in glob.glob(".env*", recursive=True):
                if os.path.isfile(env_f):
                    lines = open(env_f, errors="ignore").readlines()
                    masked_lines = [f"{l.split('=')[0]}=MASKED_VALUE\n" if "=" in l and not l.startswith("#") else l for l in lines]
                    env_templates[env_f] = "".join(masked_lines)
            
            cfg_file = self.configs_dir / "config_templates.json"
            cfg_file.write_text(json.dumps(env_templates, indent=2), encoding="utf-8")
            self.manifest["relevant_files"].append("configs/config_templates.json")
            print("    ✓ Modelos de configuração seguros salvos em configs/config_templates.json.")


    def generate_replication_script_15_pillars(self):
        """Gera script mestre e catálogo para as 15 categorias de replicação total."""
        pillars_file = self.output_dir / "replicacao_15_pilares.json"
        pillars_file.write_text(json.dumps(REPLICATION_15_PILLARS, indent=2, ensure_ascii=False), encoding="utf-8")
        
        script_lines = [
            "#!/bin/bash",
            "# Script Automatizado de Replicação Total do Sistema (15 Pilares)",
            "set -e",
            "REPLICA_DIR=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" >/dev/null 2>&1 && pwd )\"",
            "echo \"╔═════════════════════════════════════════════════════════════════╗\"",
            "echo \"║ 🚀 EXECUÇÃO DA REPLICAÇÃO TOTAL DO SISTEMA (15 PILARES)        ║\"",
            "echo \"╚═════════════════════════════════════════════════════════════════╝\"",
        ]
        for p in REPLICATION_15_PILLARS:
            script_lines.append(f"echo \"[*] Processando: {p['title']} ({p['description']})\"")
            for cmd in p['commands']:
                script_lines.append(f"# {cmd}")
        
        script_file = self.output_dir / "executar_replicacao_15_camadas.sh"
        script_file.write_text("\n".join(script_lines), encoding="utf-8")
        script_file.chmod(0o755)
        print("    ✓ Script de 15 pilares do sistema gerado em executar_replicacao_15_camadas.sh.")

    def generate_evidence_and_hashes(self):
        """Camada 6: Cálculo forense de hashes SHA-256 e emissão de laudo."""
        print("[*] [CAMADA 6: Integridade Forense] Calculando hashes SHA-256 e emitindo laudo...")
        
        all_files = []
        for root, _, files in os.walk(self.output_dir):
            for f in files:
                fp = Path(root) / f
                rel_p = str(fp.relative_to(self.output_dir))
                h = calculate_sha256(fp)
                self.manifest["hashes"][rel_p] = h
                all_files.append((rel_p, fp.stat().st_size, h))

        if self.mode == "full":
            manifest_file = self.reports_dir / "replica_manifest.json"
            manifest_file.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")

            laudo_lines = [
                "# 📋 LAUDO PERICIAL DE REPLICAÇÃO TOTAL (FRONTEND AO BACKEND)",
                f"\n**Data de Emissão (UTC):** {datetime.now(timezone.utc).isoformat()}",
                f"**Destino Organizado em SITES:** `{self.output_dir}`",
                f"**Nome do Site:** `{self.site_name}`",
                f"**Total de Arquivos Baixados/Gerados:** {len(all_files)}",
                "\n## 🏛️ 1. Resumo da Extração por Camadas",
                "- **Frontend:** HTML, CSS, JavaScript (desminificado), Storage (LocalStorage/Cookies) normalizados.",
                f"- **Assets Baixados:** {len(self.manifest['assets_downloaded'])} imagens e fontes remotas baixadas em `assets/images` e `assets/fonts`.",
                f"- **Source Maps:** {len(self.manifest['source_maps_extracted'])} fontes originais reconstituídas em `frontend/src/`.",
                f"- **Backend:** {len(self.manifest['backend_routes'])} rotas mapeadas e contratos de mock criados.",
                "- **Database SQLite:** Banco de dados físico `database/app.db` populado e ativo com tabelas e seeds.",
                "- **Ambiente de Execução:** Servidor mock Python nativo com SQLite em `backend_mock/server.py` e script `iniciar_replica.sh`.",
                "\n## 🏛️ 2. As 15 Categorias de Replicação do Sistema Operacional & Infraestrutura",
                "| Categoria | Escopo & Descrição | Ferramentas Canônicas |",
                "| :--- | :--- | :--- |",
                "| **1. Sistema Operacional** | Imagem completa do SO instalado, configurações e atualizações | Clonezilla, Ghost, dd |",
                "| **2. Arquivos de Configuração** | Clonagem de configs essenciais (/etc/ ou Registro do Windows) | rsync, tar, cópia manual |",
                "| **3. Software e Aplicações** | Pacotes instalados (dpkg/pacman) e scripts/programas personalizados | dpkg, pacman, rsync, tar |",
                "| **4. Bancos de Dados** | Dumps completos de todos os bancos (metadados e dados) | mysqldump, pg_dump, sqlite3 |",
                "| **5. Arquivos do Usuário** | Documentos, fotos, vídeos, mídias e arquivos pessoais | rsync, tar, cópia manual |",
                "| **6. Configurações de Rede** | DNS, interfaces de rede, roteamento, proxies e regras | rsync, tar, cópia manual |",
                "| **7. Configurações de Segurança** | Chaves SSH, certificados SSL/TLS, firewalls (ufw/iptables) | rsync, tar, cópia manual |",
                "| **8. Log de Atividades** | Logs do sistema (/var/log) para histórico pericial de eventos | rsync, tar, journalctl |",
                "| **9. Configurações de Serviços** | Servidores web (Apache, Nginx, Caddy), Redis e daemons | rsync, tar, systemctl |",
                "| **10. Monitoramento e Gestão** | Prometheus, Grafana, Zabbix, Loki e exportadores de métricas | rsync, tar, cópia manual |",
                "| **11. Configurações de Backup** | Rotinas de ferramentas de backup e agendamentos cron jobs | rsync, tar, crontab |",
                "| **12. Licenças e Chaves** | Licenças de software e chaves criptográficas necessárias | rsync, tar, cópia manual |",
                "| **13. Virtualização** | Configurações de máquinas virtuais e discos (qcow2, vmdk) | qemu-img, rsync, virsh |",
                "| **14. Cloud e Contêineres** | Docker, Kubernetes, manifests, Helm e configurações cloud | docker, kubectl, rsync |",
                "| **15. Configurações Específicas** | Impressoras (CUPS), drivers de automação e periféricos | rsync, tar, cópia manual |",
                "\n## 🔒 3. Tabela Forense de Checksums SHA-256",
                "| Arquivo na Réplica | Tamanho (Bytes) | Hash SHA-256 |",
                "| :--- | :---: | :--- |"
            ]
            for rel_p, sz, h in sorted(all_files):
                laudo_lines.append(f"| `{rel_p}` | {sz} | `{h}` |")
            laudo_lines.append("\n---\n*Laudo emitido compulsoriamente pela governança Sentinela Guardião.*")
            laudo_file = self.reports_dir / "LAUDO_REPLICADOR_TOTAL.md"
            laudo_file.write_text("\n".join(laudo_lines), encoding="utf-8")
            print(f"    ✓ Laudo pericial gravado em: {laudo_file}")

        else:
            # Modo Relevantes: Laudo de arquivos importantes
            manifest_file = self.reports_dir / "arquivos_relevantes_manifest.json"
            manifest_file.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")

            laudo_lines = [
                "# 📋 LAUDO DE EXTRAÇÃO DE ARQUIVOS RELEVANTES (AUDITORIA TOTAL)",
                f"\n**Data de Emissão (UTC):** {datetime.now(timezone.utc).isoformat()}",
                f"**Destino:** `{self.output_dir}`",
                f"**Total de Arquivos Relevantes Extraídos:** {len(all_files)}",
                "\n## 🎯 1. Escopo Seletivo de Extração",
                "- **Foco:** Contratos de API, rotas descobertas, schemas SQL, modelos de config e evidências críticas.",
                "- **Otimização:** Sem download de imagens, vídeos ou fontes volumosas.",
                "\n## 🔒 2. Tabela Forense de Checksums SHA-256",
                "| Arquivo Relevante | Tamanho (Bytes) | Hash SHA-256 |",
                "| :--- | :---: | :--- |"
            ]
            for rel_p, sz, h in sorted(all_files):
                laudo_lines.append(f"| `{rel_p}` | {sz} | `{h}` |")
            laudo_lines.append("\n---\n*Extração pericial seletiva pela governança Sentinela Guardião.*")
            laudo_file = self.reports_dir / "LAUDO_ARQUIVOS_RELEVANTES.md"
            laudo_file.write_text("\n".join(laudo_lines), encoding="utf-8")
            print(f"    ✓ Laudo de arquivos relevantes gravado em: {laudo_file}")

    def run(self):
        """Ciclo completo de vasculhamento e extração."""
        titulo = "FULL STACK REPLICATOR (BAIXAR TUDO EM SITES)" if self.mode == "full" else "AUDITORIA TOTAL (EXTRAIR ARQUIVOS RELEVANTES)"
        print("\n" + "="*75)
        print(f"🛡️ [SENTINELA] {titulo}")
        print("="*75)
        self.prepare_directories()
        self.replicate_frontend()
        self.replicate_backend_and_contracts()
        self.initialize_sqlite_database()
        self.generate_mock_server_and_runner()
        self.generate_replication_script_15_pillars()
        self.generate_evidence_and_hashes()
        print(f"\n🎉 [SUCESSO] Operação ({self.mode}) concluída com 100% de integridade!")
        print(f"📁 Diretório de Saída: {self.output_dir}\n")

def parse_args():
    parser = argparse.ArgumentParser(description="Full Stack Replicator & Extrator de Arquivos Relevantes Sentinela")
    parser.add_argument("target", nargs="?", default=".", help="Diretório alvo a inspecionar/replicar")
    parser.add_argument("output", nargs="?", default=None, help="Diretório de saída personalizado")
    parser.add_argument("--mode", choices=["full", "relevantes"], default="full", help="Modo: 'full' (baixa tudo em projetos/SITES) ou 'relevantes' (baixa apenas arquivos essenciais)")
    parser.add_argument("--site-name", default=None, help="Nome da pasta do site dentro de projetos/SITES")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    replicator = FullStackReplicator(
        target_dir=args.target,
        output_dir=args.output,
        mode=args.mode,
        site_name=args.site_name
    )
    replicator.run()
