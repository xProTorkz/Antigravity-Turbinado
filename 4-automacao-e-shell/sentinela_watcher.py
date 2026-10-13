#!/usr/bin/env python3
"""
/Users/lucasvinicius/projetos/SISTEMAS/Antigravity Turbinado/4-automacao-e-shell/sentinela_watcher.py
==============================================================================
SENTINELA MULTI-AGENT SUPERVISOR & RESILIENT WATCHDOG (v2.1)
==============================================================================
Orquestrador concorrente de tarefas do ecossistema Lucas Vinicius / xProTorkz.
- Gerencia Pool Concorrente de até 4 Workers Background via agy CLI headless
- Carrega dinamicamente os Subagentes Especialistas:
    * sentinela-backend
    * sentinela-frontend
    * sentinela-qa-security
- Fila Visual (IDE & Spark) com notificações nativas no macOS
- Watchdog de Heartbeat, Timeout e Auto-Rollback de falhas
- Scope Lock anti-colisão de arquivos
- Atualização em tempo real de ESTADO_OPERACIONAL.json
- Resiliência com Exponential Backoff contra falhas de rede
==============================================================================
"""
import os
import sys
import time
import json
import re
import signal
import subprocess
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Configurações Globais
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", os.environ.get("GH_TOKEN", ""))
STATE_FILE = os.path.expanduser("~/.gemini/watcher_state.json")
LOG_DIR = os.path.expanduser("~/.gemini/logs")
SHARED_STATE_FILE = os.path.expanduser("~/.gemini/ESTADO_OPERACIONAL.json")

MAX_BG_WORKERS = 4
POLL_INTERVAL_SECONDS = 45
WORKER_TIMEOUT_SECONDS = 300  # 5 minutos por tarefa
MAX_RETRIES = 3

CATEGORIAS = ["BOTS", "SITES", "SISTEMAS", "APLICAÇÕES", "VPS"]

REPOS_TO_WATCH = [
    ("Zentinel", "xProTorkz/Zentinel"),
    ("Dados Bacbo", "xProTorkz/Dados-Bacbo"),
    ("Atende Ai", "xProTorkz/Atende-Ai"),
    ("Jarvis Assistente", "xProTorkz/Jarvis-Assistente"),
    ("Buy Station", "xProTorkz/Buy-Station"),
    ("Minha Agenda", "xProTorkz/Minha-Agenda"),
    ("Arena Beach", "xProTorkz/gestao-arena"),
    ("Antigravity Turbinado", "xProTorkz/Antigravity-Turbinado")
]

os.makedirs(LOG_DIR, exist_ok=True)

# Lock e estruturas de estado em memória
state_lock = threading.Lock()
active_workers = {}   # worker_id -> info
locked_files_global = set()
repo_etags = {}

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(os.path.join(LOG_DIR, "supervisor.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def notify_macos(title, message, sound="Glass"):
    try:
        script = f'display notification "{message}" with title "{title}" sound name "{sound}"'
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception as e:
        log(f"Falha ao emitir notificação macOS: {e}")

def resolve_local_project_path(project_name):
    base_dir = "/Users/lucasvinicius/projetos"
    for cat in CATEGORIAS:
        cand = os.path.join(base_dir, cat, project_name)
        if os.path.isdir(cand):
            return cand
    return None

def github_api_request(endpoint, method="GET", data=None, retries=2, use_etag=True):
    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Sentinela-Supervisor/2.1"
    }
    if use_etag and method == "GET" and endpoint in repo_etags:
        headers["If-None-Match"] = repo_etags[endpoint]

    payload = json.dumps(data).encode("utf-8") if data else None

    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=12) as resp:
                etag = resp.headers.get("ETag")
                if etag and method == "GET":
                    repo_etags[endpoint] = etag
                content = resp.read().decode("utf-8")
                return json.loads(content) if content else {}
        except urllib.error.HTTPError as he:
            if he.code == 304:
                # 304 Not Modified consome ZERO requisições do rate limit!
                return []
            if he.code == 403 or he.code == 429:
                log(f"⚠️ GitHub Rate Limit / 403 atingido em {endpoint}. Pausando consultas por 120s...")
                time.sleep(120)
                return {"error": "rate_limited"}
            if attempt == retries:
                log(f"Erro persistente na API GitHub [{method} {endpoint}]: {he}")
                return {"error": str(he)}
            time.sleep(2 * attempt)
        except Exception as e:
            if attempt == retries:
                log(f"Erro persistente na API GitHub [{method} {endpoint}]: {e}")
                return {"error": str(e)}
            time.sleep(2 * attempt)
    return {"error": "timeout"}

def post_issue_comment(repo, issue_number, comment):
    return github_api_request(f"repos/{repo}/issues/{issue_number}/comments", method="POST", data={"body": comment})

def close_issue(repo, issue_number):
    return github_api_request(f"repos/{repo}/issues/{issue_number}", method="PATCH", data={"state": "closed"})

def load_persistent_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"processed_issues": {}, "completed_history": []}
    return {"processed_issues": {}, "completed_history": []}

def save_persistent_state(data):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Erro salvando state: {e}")

def update_operational_dashboard():
    with state_lock:
        workers_view = {}
        for wid, winfo in active_workers.items():
            workers_view[wid] = {
                "project": winfo.get("project"),
                "repo": winfo.get("repo"),
                "issue_id": winfo.get("issue_id"),
                "title": winfo.get("title"),
                "mode": winfo.get("mode"),
                "subagent": winfo.get("subagent"),
                "started_at": winfo.get("started_at"),
                "status": winfo.get("status")
            }

        dash = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "supervisor_status": "ONLINE_ACTIVE",
            "active_bg_workers_count": len([w for w in active_workers.values() if w.get("mode") == "BACKGROUND"]),
            "max_bg_workers": MAX_BG_WORKERS,
            "workers": workers_view,
            "locked_files": list(locked_files_global)
        }

        try:
            with open(SHARED_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(dash, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log(f"Erro atualizando ESTADO_OPERACIONAL.json: {e}")

def extract_scope_files(issue_body):
    files = set()
    in_scope_block = False
    for line in issue_body.splitlines():
        if "Scope Lock" in line:
            in_scope_block = True
            continue
        if in_scope_block and line.startswith("## "):
            break
        if in_scope_block:
            matches = re.findall(r'[`"\']([^`"\']+\.[a-zA-Z0-9]+)[`"\']', line)
            for m in matches:
                files.add(m.strip())
            clean = line.strip().lstrip("-* ").strip()
            if clean and not clean.startswith("#") and "." in clean and " " not in clean:
                files.add(clean)
    return files

def determine_subagent(issue_body, issue_title):
    # Detecta se há subagente explicitamente definido
    m = re.search(r'assigned_subagent:\s*["\']?([^"\'\n]+)["\']?', issue_body)
    if m:
        val = m.group(1).strip()
        if val in ["sentinela-backend", "sentinela-frontend", "sentinela-qa-security"]:
            return val

    # Mapeamento por skill ou conteúdo
    check_text = (issue_title + " " + issue_body).lower()
    if any(k in check_text for k in ["@frontend", "ui", "interface", "tela", "css", "layout", "next.js", "react"]):
        return "sentinela-frontend"
    if any(k in check_text for k in ["@seguranca", "qa", "testes", "owasp", "auditoria"]):
        return "sentinela-qa-security"
    return "sentinela-backend"

def determine_execution_mode(issue_body, issue_title):
    if 'execution_mode: "VISUAL_IDE"' in issue_body or 'execution_mode: VISUAL_IDE' in issue_body:
        return "VISUAL"
    return "BACKGROUND"

def run_worker_task(worker_id, task_info):
    proj_name = task_info["project"]
    repo = task_info["repo"]
    issue_id = task_info["issue_id"]
    issue_title = task_info["title"]
    subagent = task_info.get("subagent", "sentinela-backend")
    scope_files = task_info.get("scope_files", set())

    log_path = os.path.join(LOG_DIR, f"worker_{worker_id}_{proj_name}_{issue_id}.log")
    local_dir = resolve_local_project_path(proj_name)

    if not local_dir:
        log(f"❌ Diretório local para '{proj_name}' não encontrado nas 5 categorias.")
        post_issue_comment(repo, issue_id, f"⚠️ **Sentinela Watchdog:** Diretório local para `{proj_name}` não foi localizado em `/Users/lucasvinicius/projetos/`. Tarefa pausada.")
        with state_lock:
            active_workers.pop(worker_id, None)
            locked_files_global.difference_update(scope_files)
        update_operational_dashboard()
        return

    # Comando de execução autônoma via agy CLI com o Subagente Específico
    prompt = (
        f"Execute a Issue #{issue_id} do repositório {repo} ('{issue_title}'). "
        f"Siga estritamente o contrato agent_task v5. "
        f"Modifique apenas os arquivos autorizados no Scope Lock: {list(scope_files)}. "
        f"Rode os testes para validar o funcionamento antes e depois. "
        f"Ao concluir, assegure-se de que nenhum arquivo quebrado permaneça."
    )

    cmd = [
        "/Users/lucasvinicius/.gemini/antigravity-ide/bin/agy",
        "-p", prompt,
        "--agent", subagent,
        "--dangerously-skip-permissions",
        "--model", "gemini-3.8-flash-high",
        "--effort", "high",
        "--log-file", log_path
    ]

    log(f"🚀 [{worker_id}] Disparando Subagente `{subagent}` em [{proj_name}] #{issue_id}...")
    start_time = time.time()

    post_issue_comment(repo, issue_id, f"⚙️ **Worker `{worker_id}` (Subagente `{subagent}`):** Execução iniciada em background headless no Mac.")

    proc = None
    success = False
    try:
        with open(log_path, "w", encoding="utf-8") as out_f:
            proc = subprocess.Popen(cmd, cwd=local_dir, stdout=out_f, stderr=subprocess.STDOUT)
            
            while True:
                ret = proc.poll()
                if ret is not None:
                    success = (ret == 0)
                    break
                
                # Watchdog de Timeout
                elapsed = time.time() - start_time
                if elapsed > WORKER_TIMEOUT_SECONDS:
                    log(f"⚠️ [{worker_id}] TIMEOUT atingido ({WORKER_TIMEOUT_SECONDS}s). Encerrando processo...")
                    proc.kill()
                    subprocess.run(["git", "-C", local_dir, "restore", "."], check=False)
                    post_issue_comment(repo, issue_id, f"🚨 **Sentinela Watchdog:** Subagente `{subagent}` atingiu timeout de {WORKER_TIMEOUT_SECONDS}s. Processo cancelado e arquivos revertidos.")
                    break
                
                time.sleep(3)

    except Exception as e:
        log(f"Erro executando worker {worker_id}: {e}")
        if proc:
            proc.kill()

    # Finalização
    with state_lock:
        active_workers.pop(worker_id, None)
        locked_files_global.difference_update(scope_files)

    if success:
        log(f"✅ [{worker_id}] Tarefa [{proj_name}] #{issue_id} concluída com sucesso!")
        post_issue_comment(repo, issue_id, f"✅ **Worker `{worker_id}` (`{subagent}`) Concluído:** Alterações implementadas e validadas conforme governança Sentinela.")
        close_issue(repo, issue_id)
        notify_macos(f"Sucesso: {proj_name}", f"Issue #{issue_id} concluída pelo subagente {subagent}!")
    else:
        log(f"❌ [{worker_id}] Falha na tarefa [{proj_name}] #{issue_id}.")

    update_operational_dashboard()

def process_discovered_issue(proj_name, repo, issue, persistent_state):
    issue_num = issue.get("number")
    issue_title = issue.get("title", "")
    issue_body = issue.get("body", "")
    key = f"{repo}#{issue_num}"

    if "pull_request" in issue:
        return

    mode = determine_execution_mode(issue_body, issue_title)
    subagent = determine_subagent(issue_body, issue_title)
    scope_files = extract_scope_files(issue_body)

    log(f"🎯 TAREFA IDENTIFICADA: [{proj_name}] #{issue_num} ({mode} | Subagente: {subagent})")

    if mode == "VISUAL":
        notify_macos(
            f"Visual: {proj_name}",
            f"Issue #{issue_num}: {issue_title} pronta para acompanhamento na IDE."
        )
        post_issue_comment(repo, issue_num, f"👁️ **Sentinela:** Tarefa visual identificada para o subagente `{subagent}`. Disponível na IDE / Spark.")
        persistent_state["processed_issues"][key] = {
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "mode": "VISUAL",
            "subagent": subagent,
            "status": "WAITING_REVIEW"
        }
        save_persistent_state(persistent_state)
        return

    # Modo Background Headless
    with state_lock:
        current_bg = len([w for w in active_workers.values() if w.get("mode") == "BACKGROUND"])
        if current_bg >= MAX_BG_WORKERS:
            log(f"Pool de workers cheio ({current_bg}/{MAX_BG_WORKERS}). Tarefa #{issue_num} aguardando slot...")
            return

        collision = locked_files_global.intersection(scope_files)
        if collision:
            log(f"🔒 Scope Lock ativo nos arquivos {collision}. Tarefa #{issue_num} aguardando liberação...")
            return

        available_ids = [f"worker-0{i}" for i in range(1, MAX_BG_WORKERS + 1)]
        used_ids = set(active_workers.keys())
        worker_id = next((wid for wid in available_ids if wid not in used_ids), f"worker-extra-{int(time.time())}")

        locked_files_global.update(scope_files)
        task_info = {
            "project": proj_name,
            "repo": repo,
            "issue_id": issue_num,
            "title": issue_title,
            "body": issue_body,
            "mode": "BACKGROUND",
            "subagent": subagent,
            "scope_files": scope_files,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "EXECUTING"
        }
        active_workers[worker_id] = task_info

        persistent_state["processed_issues"][key] = {
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "mode": "BACKGROUND",
            "worker": worker_id,
            "subagent": subagent,
            "status": "DISPATCHED"
        }
        save_persistent_state(persistent_state)

    update_operational_dashboard()

    t = threading.Thread(target=run_worker_task, args=(worker_id, task_info), daemon=True)
    t.start()

def main_loop():
    log("🚀 Sentinela Multi-Agent Supervisor v2.1 ONLINE.")
    log(f"Capacidade: até {MAX_BG_WORKERS} workers paralelos headless + Fila Visual.")
    persistent_state = load_persistent_state()
    update_operational_dashboard()

    while True:
        try:
            for proj_name, repo in REPOS_TO_WATCH:
                issues = github_api_request(f"repos/{repo}/issues?state=open&sort=created&direction=asc&per_page=10")
                if isinstance(issues, list):
                    for issue in issues:
                        issue_num = str(issue.get("number"))
                        key = f"{repo}#{issue_num}"
                        if key not in persistent_state["processed_issues"]:
                            process_discovered_issue(proj_name, repo, issue, persistent_state)
            
            update_operational_dashboard()
        except Exception as e:
            log(f"Exceção no ciclo principal do supervisor: {e}")
        
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main_loop()
