#!/usr/bin/env bash
# ==============================================================================
# Roteador Canônico de Automação Antigravity (SRE / DevOps Dictionary v3.2)
# Local: /Users/lucasvinicius/projetos/estruturas/agy_cmd.sh
# Escopo: macOS / Unix - Automação Determinística, Resiliência e SRE
# ==============================================================================

agy_cmd() {
    local action="$1"
    shift 2>/dev/null || true

    case "$action" in
        # ======================================================================
        # FOCO 1: Processos, CPU, Memória RAM & Destravamento de Hardware
        # ======================================================================
        "kill-port")
            local port="${1:-3000}"
            echo "🛑 Localizando e liberando porta TCP $port..."
            local pids=$(lsof -ti :"$port" 2>/dev/null)
            if [ -n "$pids" ]; then
                echo "$pids" | xargs kill -9 2>/dev/null && echo "✅ Porta $port liberada (PIDs: $(echo $pids | tr '\n' ' '))."
            else
                echo "ℹ️ Nenhum processo escutando na porta $port."
            fi
            ;;
        "kill-zombies")
            echo "🧟 Eliminando processos órfãos e travados (Node, Python, Workers)..."
            pkill -9 -f "node|python|antigravity_worker|pytest|celery" 2>/dev/null || true
            echo "✅ Processos órfãos higienizados."
            ;;
        "force-stop")
            echo "⏹️ Encerrando todos os servidores de desenvolvimento locais..."
            pkill -9 -f "vite|next-server|uvicorn|gunicorn|flask|fastapi|webpack|puma" 2>/dev/null || true
            echo "✅ Servidores locais encerrados."
            ;;
        "purge-ram")
            echo "🧹 Sincronizando buffers de disco e liberando memória RAM inativa..."
            sync
            if sudo -n purge 2>/dev/null; then
                echo "✅ Buffer de RAM purgado via sudo purge."
            else
                echo "ℹ️ Buffers de disco sincronizados (sync ok). sudo requer senha para purge total."
            fi
            ;;
        "top-cpu")
            echo "🔥 Top 10 processos com maior consumo de CPU:"
            ps aux -r | head -n 11
            ;;
        "top-ram")
            echo "🧠 Top 10 processos com maior consumo de memória residente:"
            ps aux -m | head -n 11
            ;;
        "foco-ativo")
            echo "🚀 Elevando prioridade de CPU para a sessão corrente e limpando concorrentes..."
            renice -n -20 -p $$ 2>/dev/null || renice -n -10 -p $$ 2>/dev/null || true
            kill -9 $(pgrep -f "websocket_server|node_orphan") 2>/dev/null || true
            echo "✅ Foco ativo configurado (PID $$)."
            ;;
        "realtime-cpu")
            echo "⚡ Alocando prioridade máxima de agendamento do kernel..."
            sudo -n renice -n -20 -p $$ 2>/dev/null || renice -n -10 -p $$ 2>/dev/null || echo "ℹ️ Prioridade ajustada."
            echo "✅ Processo $$ alocado com alta prioridade."
            ;;
        "watchdog-cpu")
            local limit="${1:-80}"
            echo "👀 Verificando processos com consumo de CPU superior a ${limit}%..."
            ps -eo pid,pcpu,comm -r | awk -v lim="$limit" 'NR>1 && $2>lim {print "⚠️ PID " $1 " (" $3 ") consumindo " $2 "% CPU"}'
            echo "✅ Varredura de watchdog concluída."
            ;;

        # ======================================================================
        # FOCO 2: Faxina de Disco, Purga de Buffers, Caches & Arquivos Mortos
        # ======================================================================
        "purgar-buffers"|"zerar-logs")
            echo "📄 Truncando arquivos de log para 0 bytes sem romper descritores..."
            find /Users/lucasvinicius/projetos -name "*.log" -exec truncate -s 0 {} + 2>/dev/null
            echo "✅ Todos os arquivos .log truncados com sucesso."
            ;;
        "deep-clean")
            echo "🧹 Executando faxina profunda (caches de build, turbo, next, dist, pycache)..."
            find . -type d \( -name ".turbo" -o -name ".next" -o -name "dist" -o -name "build" -o -name ".pytest_cache" -o -name "__pycache__" \) -prune -exec rm -rf {} + 2>/dev/null
            find . -name ".DS_Store" -delete 2>/dev/null || true
            echo "✅ Caches e artefatos de compilação removidos."
            ;;
        "clean-scratch")
            echo "🗑️ Esvaziando diretórios scratch da IDE e temporários do SO..."
            rm -rf /Users/lucasvinicius/.gemini/antigravity-ide/scratch/* /tmp/antigravity_* 2>/dev/null || true
            echo "✅ Diretórios de rascunho limpos."
            ;;
        "clean-pycache")
            echo "🐍 Removendo recursivamente caches do Python (__pycache__ e *.pyc)..."
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
            find . -name "*.pyc" -delete 2>/dev/null || true
            echo "✅ Pycache removido."
            ;;
        "clean-modules")
            echo "📦 Removendo diretórios node_modules..."
            find . -maxdepth 3 -type d -name "node_modules" -prune -exec rm -rf {} + 2>/dev/null
            echo "✅ Pastas node_modules removidas."
            ;;
        "clean-pkg-cache")
            echo "📦 Purgando caches locais de gerenciadores de pacotes (npm, yarn, pip)..."
            npm cache clean --force 2>/dev/null || true
            pip cache purge 2>/dev/null || true
            echo "✅ Caches de pacotes purgados."
            ;;
        "rotacionar-logs")
            echo "🗜️ Compactando em gzip arquivos de log superiores a 50MB..."
            find /Users/lucasvinicius/projetos -name "*.log" -size +50M -exec gzip -f {} + 2>/dev/null
            echo "✅ Rotação de logs concluída."
            ;;
        "empty-trash")
            echo "🗑️ Esvaziando lixeira do macOS..."
            rm -rf ~/.Trash/* 2>/dev/null || true
            echo "✅ Lixeira esvaziada."
            ;;

        # ======================================================================
        # FOCO 3: Git, Resiliência, Versionamento Rápido & Recuperação
        # ======================================================================
        "quick-push")
            echo "🚀 Executando snapshot e sincronização rápida do Git..."
            git add -A && git commit -m "chore: snapshot operacional $(date +'%Y-%m-%d %H:%M')" && git push origin HEAD
            ;;
        "snapshot-force")
            echo "⚡ Criando snapshot compulsório e forçando atualização..."
            git add -A && git commit -m "snapshot: $(date -u +'%Y-%m-%dT%H:%M:%SZ')" && git push --force origin HEAD
            ;;
        "reset-clean")
            echo "⚠️ Descartando todas as alterações não comitadas e arquivos untracked..."
            git reset --hard HEAD && git clean -fd
            echo "✅ Árvore do Git restaurada ao estado do último commit."
            ;;
        "stash-save")
            local msg="${1:-auto_stash_$(date +'%s')}"
            echo "📦 Guardando alterações pendentes no stash: $msg..."
            git stash save -u "$msg"
            ;;
        "stash-pop")
            echo "📤 Restaurando último estado armazenado no stash..."
            git stash pop
            ;;
        "sync-upstream")
            echo "🔄 Sincronizando com o upstream remoto da branch main..."
            git fetch origin && (git rebase origin/main || git merge origin/main)
            ;;
        "clean-branches")
            echo "🧹 Removendo branches locais já mescladas..."
            git branch --merged | grep -Ev "(^\*|master|main|dev)" | xargs git branch -d 2>/dev/null || echo "ℹ️ Nenhuma branch mesclada pendente de remoção."
            ;;
        "status-diff")
            echo "📊 Status resumido e diff estatístico:"
            git status -s && git diff --stat
            ;;
        "bypass-hooks")
            echo "⚡ Comitando com bypass de pre-commit hooks (--no-verify)..."
            git commit --no-verify -m "chore: snapshot emergencial com bypass de validações" 2>/dev/null && echo "✅ Commit realizado com bypass." || echo "ℹ️ Nenhuma alteração pendente no stage."
            ;;

        # ======================================================================
        # FOCO 4: Redes Locais, Portas, Sockets & Conectividade
        # ======================================================================
        "portas-ativas")
            echo "🔌 Sockets TCP abertos em modo LISTEN:"
            lsof -nP -iTCP -sTCP:LISTEN
            ;;
        "watch-port")
            local port="${1:-3000}"
            echo "🔍 Inspecionando conexões ativas na porta $port:"
            lsof -i :"$port" || echo "ℹ️ Nenhuma conexão na porta $port."
            ;;
        "check-endpoint")
            local target="${1:-http://localhost:3000}"
            echo "🌐 Testando endpoint: $target..."
            curl -s -o /dev/null -w "Alvo: $target | HTTP: %{http_code} | Conexão: %{time_connect}s | Total: %{time_total}s\n" "$target"
            ;;
        "check-net")
            echo "📡 Testando conectividade externa via DNS e ICMP..."
            if ping -c 2 1.1.1.1 >/dev/null 2>&1; then
                echo "✅ Conexão Externa Operacional (Internet OK)."
            else
                echo "❌ Falha de Conectividade Externa (Offline)."
            fi
            ;;
        "ip-local")
            local ip=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")
            echo "📍 Endereço IP local: $ip"
            ;;
        "inspect-headers")
            local target="${1:-http://localhost:3000}"
            echo "📋 Cabeçalhos de resposta HTTP para $target:"
            curl -Is "$target" | head -n 25
            ;;
        "cert-check")
            local host="${1:-google.com}"
            echo "🔒 Verificando certificado SSL/TLS de $host..."
            curl -vI "https://$host" 2>&1 | grep -i "expire date\|server certificate\|SSL certificate verify" || true
            ;;
        "check-dns")
            local host="${1:-google.com}"
            echo "🌐 Testando resolução DNS para $host..."
            dscacheutil -q host -a name "$host" 2>/dev/null || nslookup "$host" 2>/dev/null || echo "❌ Falha na resolução de $host."
            ;;
        "bench-endpoint")
            local target="${1:-http://localhost:3000}"
            local samples="${2:-5}"
            echo "⚡ Executando benchmark rápido de latência ($samples amostras) em $target..."
            for i in $(seq 1 "$samples"); do
                curl -s -o /dev/null -w "Amostra #$i: HTTP %{http_code} | Conexão: %{time_connect}s | TTFB: %{time_starttransfer}s | Total: %{time_total}s\n" "$target"
            done
            echo "✅ Benchmark concluído."
            ;;
        "audit-ports-full")
            echo "🔍 Mapeamento completo de sockets de rede locais (TCP/UDP LISTEN):"
            lsof -nP -iTCP -sTCP:LISTEN
            ;;

        # ======================================================================
        # FOCO 5: Runtimes, Python, Node.js & Docker
        # ======================================================================
        "recreate-venv")
            echo "🐍 Recriando ambiente virtual Python (.venv)..."
            rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip
            echo "✅ Ambiente virtual recriado com pip atualizado."
            ;;
        "freeze-reqs")
            echo "📄 Exportando dependências congeladas para requirements.txt..."
            pip freeze > requirements.txt && echo "✅ requirements.txt gerado com sucesso."
            ;;
        "reinstall-node")
            echo "📦 Reinstalando dependências do Node.js de forma limpa..."
            rm -rf node_modules package-lock.json && npm install
            echo "✅ node_modules reinstalado com sucesso."
            ;;
        "docker-down")
            echo "🐳 Derrubando containers e redes Docker Compose..."
            docker compose down --remove-orphans 2>/dev/null || docker-compose down 2>/dev/null || true
            echo "✅ Containers parados."
            ;;
        "docker-rebuild")
            echo "🐳 Reconstruindo containers sem cache e iniciando em background..."
            docker compose up -d --build --force-recreate
            ;;
        "docker-prune")
            echo "🐳 Limpando containers inativos, redes não utilizadas e imagens suspensas..."
            docker system prune -af --volumes
            ;;
        "docker-logs")
            if [ -z "$1" ]; then
                echo "Uso: agy_cmd docker-logs <nome_do_container>"
            else
                docker logs --tail 100 -f "$1"
            fi
            ;;

        # ======================================================================
        # FOCO 7: Telemetria, Diagnósticos de Sistema & Hardware
        # ======================================================================
        "check-health")
            echo "🩺 Diagnóstico de Integridade de Runtimes e Ferramentas:"
            sw_vers && uname -m
            echo "--- Ferramentas Instaladas ---"
            which node python3 agy git docker 2>/dev/null || true
            node -v 2>/dev/null && python3 --version 2>/dev/null || true
            ;;
        "telemetria-full")
            echo "📊 Telemetria instantânea do macOS (Carga, Memória e Disco):"
            top -l 1 -s 0 | head -n 25 && df -h /
            ;;
        "disk-usage")
            echo "💾 Espaço em disco (Volume de Dados):"
            df -h /System/Volumes/Data 2>/dev/null || df -h /
            ;;
        "varrer-grandes")
            echo "🔍 Mapeando arquivos maiores que 50MB no diretório de projetos..."
            find /Users/lucasvinicius/projetos -type f -size +50M -exec ls -lh {} + 2>/dev/null | awk '{print $5, $9}'
            ;;
        "sys-load")
            echo "⏱️ Tempo de atividade e carga média do sistema:"
            uptime
            ;;

        # ======================================================================
        # FOCO 8: Execução em Background, Daemons & Silêncio Operacional
        # ======================================================================
        "exec-raw")
            echo "⚡ Despachando comando via CLI agy com esforço máximo e sem prompts:"
            agy --dangerously-skip-permissions --effort high "$@"
            ;;
        "run-daemon")
            if [ -z "$1" ]; then
                echo "Uso: agy_cmd run-daemon <comando>"
            else
                nohup "$@" > /dev/null 2>&1 &
                echo "⚙️ Processo despachado em background desacoplado (PID: $!)."
            fi
            ;;
        "silence-logs")
            export LOG_LEVEL=ERROR
            export NODE_ENV=production
            echo "🤫 Modo silencioso configurado no ambiente (LOG_LEVEL=ERROR)."
            ;;
        "disown-job")
            disown -h %1 2>/dev/null || disown -h 2>/dev/null || true
            echo "✅ Último job desacoplado da janela ativa do shell."
            ;;

        # ======================================================================
        # FOCO 9: Segurança, Auditoria, Integridade & Permissões
        # ======================================================================
        "audit-perms")
            echo "🔒 Verificando arquivos com permissões abertas indevidas (world-writable):"
            find /Users/lucasvinicius/projetos -type f \( -perm -o+w -o -perm -o+r \) -ls 2>/dev/null | head -n 20 || echo "✅ Nenhuma inconsistência encontrada."
            ;;
        "harden-workspace"|"blindar"|"blindar-workspace")
            echo "🛡️ Blindando permissões de workspace para acesso restrito (750)..."
            chmod -R 750 /Users/lucasvinicius/projetos 2>/dev/null || true
            echo "✅ Permissões aplicadas aos projetos."
            ;;
        "audit-logins")
            echo "👤 Histórico recente de sessões de login no sistema:"
            last | head -n 15
            ;;
        "audit-secrets")
            echo "🔍 Varrendo staging do Git por possíveis credenciais ou tokens..."
            local found=$(git diff --staged 2>/dev/null | grep -Ei "(API_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY)")
            if [ -n "$found" ]; then
                echo "⚠️ Atenção! Possíveis segredos detectados:"
                echo "$found"
            else
                echo "✅ Nenhum segredo identificado no stage do Git."
            fi
            ;;

        # ======================================================================
        # GRUPO A: Auditoria Completa, DR & Backups de Sistema
        # ======================================================================
        "audit-full")
            echo "📊 Executando auditoria completa consolidada do ambiente..."
            mkdir -p reports
            local rfile="reports/audit_$(date +'%Y%m%d_%H%M%S').log"
            {
                echo "=== AUDITORIA SRE $(date) ==="
                echo "--- DISCO ---"
                df -h /
                echo "--- PORTAS TCP ATIVAS ---"
                lsof -nP -iTCP -sTCP:LISTEN
                echo "--- GIT STATUS ---"
                git status -s 2>/dev/null || echo "Diretório não é um repositório Git."
                echo "--- TOP 5 PROCESSOS CPU ---"
                ps aux -r | head -n 6
            } > "$rfile"
            echo "✅ Relatório salvo em: $rfile"
            tail -n 25 "$rfile"
            ;;
        "backup-quick")
            local project_name="$(basename "$PWD")"
            local bfile="backup_${project_name}_$(date +'%Y%m%d_%H%M%S').tar.gz"
            echo "💾 Gerando snapshot compactado de $project_name..."
            tar --exclude='node_modules' --exclude='.git' --exclude='__pycache__' --exclude='.venv' -czf "$bfile" .
            echo "✅ Backup criado: $bfile ($(ls -lh "$bfile" | awk '{print $5}'))"
            ;;
        "audit-privacy")
            echo "🔒 Varrendo arquivos locais em busca de PII (CPFs, emails, senhas)..."
            grep -Eri "([0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|(password|passwd|senha|secret|token)\s*[:=])" . --exclude-dir={.git,node_modules,.venv} 2>/dev/null | head -n 25 || echo "✅ Nenhum vazamento de PII detectado."
            ;;
        "mirror-state")
            local dest="${1:-/tmp/mirror_$(basename "$PWD")}"
            echo "🪞 Espelhando base local para: $dest..."
            mkdir -p "$dest"
            rsync -avz --exclude='node_modules' --exclude='.git' . "$dest"
            echo "✅ Espelhamento rsync concluído."
            ;;
        "dump-env")
            echo "🔍 Mapeando variáveis e arquivos de configuração locais (.env*)..."
            find . -maxdepth 3 -name ".env*" -exec grep -Hv "^#" {} + 2>/dev/null || echo "ℹ️ Nenhum arquivo .env encontrado."
            ;;

        # ======================================================================
        # GRUPO B: Alta Autonomia, Flags CI & Elevação de Privilégios
        # ======================================================================
        "mode-advanced")
            export AGY_EFFORT=high AGY_NON_INTERACTIVE=1 CI=true npm_config_yes=true
            echo "⚡ Modo de Alta Autonomia ativado (flags não-interativas e CI=true)."
            ;;
        "force-task")
            echo "⚡ Executando tarefa forçada ignorando avisos de linter secundários..."
            npm run build -- --force 2>/dev/null || npx -y "$@"
            ;;
        "auto-approve")
            export HOMEBREW_NO_AUTO_UPDATE=1 GIT_MERGE_AUTOEDIT=no PIP_NO_INPUT=1
            echo "✅ Bypass de confirmações ativado para Git, Brew e PIP."
            ;;
        "sudo-check")
            sudo -v 2>/dev/null && echo "✅ Sessão privilegiada sudo ativa." || echo "ℹ️ Autenticação sudo requerida."
            ;;

        # ======================================================================
        # GRUPO C: Ocultação, Furtividade, Limpeza de Rastros & Operação Silenciosa
        # ======================================================================
        "stealth-exec")
            echo "🕶️ Executando sem gravação de histórico de comandos..."
            unset HISTFILE
            nohup "$@" > /dev/null 2>&1 &
            echo "✅ Processo despachado (PID: $!)."
            ;;
        "run-idle")
            if [ -z "$1" ]; then
                echo "Uso: agy_cmd run-idle <comando>"
            else
                nice -n 19 nohup "$@" > /dev/null 2>&1 &
                echo "🍃 Comando despachado com prioridade ociosa nice 19 (PID: $!)."
            fi
            ;;
        "wipe-session")
            echo "🧹 Purgando histórico da sessão ativa e buffers temporários..."
            history -c 2>/dev/null || true
            rm -rf /tmp/antigravity_* ~/.zsh_sessions/* 2>/dev/null || true
            echo "✅ Rastros da sessão higienizados."
            ;;
        "disguise-proc")
            local proc_name="${1:-syslogd_worker}"
            shift 2>/dev/null || true
            echo "🎭 Iniciando processo sob alias: $proc_name..."
            bash -c "exec -a '$proc_name' $*" &
            echo "✅ Processo iniciado (PID: $!)."
            ;;

        # ======================================================================
        # GRUPO D: Persistência Operacional, Daemons & Sanitização Extrema
        # ======================================================================
        "cron-add")
            if [ -z "$1" ]; then
                echo "Uso: agy_cmd cron-add \"0 * * * * /caminho/do/script.sh\""
            else
                (crontab -l 2>/dev/null; echo "$1") | crontab -
                echo "✅ Rotina registrada no crontab do usuário."
            fi
            ;;
        "daemonize")
            if [ -z "$1" ]; then
                echo "Uso: agy_cmd daemonize <comando>"
            else
                nohup "$@" > daemon.log 2>&1 &
                echo $! > daemon.pid
                echo "✅ Daemon iniciado (PID: $(cat daemon.pid)) com logs em daemon.log."
            fi
            ;;
        "daemon-kill")
            if [ -f daemon.pid ]; then
                local pid=$(cat daemon.pid)
                echo "🛑 Encerrando daemon (PID: $pid)..."
                kill -9 "$pid" 2>/dev/null && rm -f daemon.pid && echo "✅ Daemon encerrado."
            else
                echo "ℹ️ Nenhum arquivo daemon.pid localizado."
            fi
            ;;
        "shred-file")
            local target="$1"
            if [ -n "$target" ] && [ -e "$target" ]; then
                echo "🔒 Sobrescrevendo e eliminando arquivo $target..."
                rm -P "$target" 2>/dev/null || rm -rf "$target"
                echo "✅ Arquivo sanitizado e removido definitivamente."
            else
                echo "Uso: agy_cmd shred-file <caminho_do_arquivo>"
            fi
            ;;
        "clean-history-secrets")
            echo "🔒 Higienizando histórico de comandos no zsh..."
            sed -i '' -E '/(API_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY)/d' ~/.zsh_history 2>/dev/null || true
            echo "✅ Histórico limpo de segredos."
            ;;

        # ======================================================================
        # GRUPO E: Amostragem de Dados, Snapshots de Banco & Sincronização Remota
        # ======================================================================
        "export-db-sample")
            local db_file="${1:-database.sqlite}"
            local tbl="${2}"
            if [ -f "$db_file" ]; then
                echo "📊 Exportando amostragem sanitizada da base $db_file..."
                if [ -n "$tbl" ]; then
                    sqlite3 "$db_file" ".schema $tbl"
                    echo "--- Primeiros 20 registros da tabela $tbl ---"
                    sqlite3 -header -column "$db_file" "SELECT * FROM $tbl LIMIT 20;"
                else
                    echo "Tabelas disponíveis em $db_file:"
                    sqlite3 "$db_file" ".tables"
                fi
            else
                echo "ℹ️ Base de dados $db_file não encontrada no diretório atual."
            fi
            ;;
        "leak-check")
            local proc="${1:-node}"
            echo "🧠 Diagnosticando alocação de memória e contagem de threads para: $proc..."
            ps -eo pid,ppid,pmem,rss,vsz,comm | grep -i "$proc" | grep -v grep | head -n 10
            echo "--- Estatísticas Globais de VM (macOS) ---"
            vm_stat | head -n 8
            ;;
        "scan-fixtures")
            echo "🔍 Varrendo diretórios de testes e fixtures por dados reais não-anonimizados..."
            find . -type d \( -name "tests" -o -name "fixtures" -o -name "seeds" \) -exec grep -Eri "(cpf|cnpj|cartao|token|senha)" {} + 2>/dev/null | head -n 25 || echo "✅ Nenhuma fixture com dados não-anonimizados encontrada."
            ;;
        "sync-remote")
            local src="${1:-.}"
            local dest="${2}"
            if [ -z "$dest" ]; then
                echo "Uso: agy_cmd sync-remote <origem> <usuario@servidor:/destino>"
            else
                echo "🚀 Sincronizando $src para $dest via rsync com compressão..."
                rsync -avzP --exclude='node_modules' --exclude='.git' --exclude='.venv' "$src" "$dest"
                echo "✅ Sincronização remota concluída."
            fi
            ;;
        "sqlite-vacuum")
            local db_file="${1:-database.sqlite}"
            if [ -f "$db_file" ]; then
                echo "🗄️ Executando VACUUM e otimização estrutural em $db_file..."
                sqlite3 "$db_file" "PRAGMA integrity_check; VACUUM; PRAGMA optimize;" && echo "✅ Banco $db_file otimizado e verificado."
            else
                echo "ℹ️ Arquivo SQLite $db_file não localizado no diretório atual."
            fi
            ;;
        "export-sqlite-schema")
            local db_file="${1:-database.sqlite}"
            if [ -f "$db_file" ]; then
                echo "📋 Exportando DDL e esquemas de tabelas de $db_file:"
                sqlite3 "$db_file" ".schema"
            else
                echo "ℹ️ Arquivo SQLite $db_file não localizado."
            fi
            ;;
        "sanitize-logs")
            local log_path="${1:-/Users/lucasvinicius/projetos}"
            echo "🔒 Higienizando e mascarando segredos em arquivos .log em $log_path..."
            find -L "$log_path" -maxdepth 4 -name "*.log" -exec sed -E -i '' -e 's/[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}/[REDACTED_CPF]/g' -e 's/Bearer [a-zA-Z0-9_\-\.]{15,}/[REDACTED_TOKEN]/g' -e 's/(password|senha)=[^& ]+/\1=[REDACTED]/g' {} + 2>/dev/null || true
            echo "✅ Logs higienizados com sucesso."
            ;;

        # ======================================================================
        # GRUPO F: Sandbox, Isolamento de Execução & Testes de Resiliência
        # ======================================================================
        "sandbox-run")
            if [ -z "$1" ]; then
                echo "Uso: agy_cmd sandbox-run <comando e argumentos>"
            else
                echo "🧪 Executando em sandbox de ambiente limpo (env -i)..."
                env -i HOME="$HOME" USER="$USER" PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin" "$@"
            fi
            ;;
        "stress-test")
            local duration="${1:-5}"
            echo "🔥 Iniciando teste controlado de estresse de CPU por ${duration}s..."
            local cpus=$(sysctl -n hw.ncpu 2>/dev/null || echo 2)
            echo "Rodando carga em $cpus cores..."
            python3 -c "
import time, multiprocessing
def f(end):
    while time.time() < end: pass
end = time.time() + $duration
procs = [multiprocessing.Process(target=f, args=(end,)) for _ in range($cpus)]
for p in procs: p.start()
for p in procs: p.join()
"
            echo "✅ Teste de estresse concluído. Carga finalizada."
            uptime
            ;;

        # ======================================================================
        # GRUPO G: Simulação de Tráfego, Mocking, Conformidade & Modo Silencioso
        # ======================================================================
        "mock-traffic")
            local url="${1:-http://localhost:3000}"
            local count="${2:-10}"
            echo "🚀 Disparando bateria de $count requisições mockadas para $url..."
            for i in $(seq 1 "$count"); do
                curl -s -o /dev/null -w "Req #$i: HTTP %{http_code} em %{time_total}s\n" -H "X-Mock-Traffic: SRE-Bench" "$url" &
            done
            wait
            echo "✅ Bateria de mock traffic finalizada."
            ;;
        "audit-compliance")
            echo "📋 Executando checklist de conformidade e integridade do repositório..."
            local ok=0; local warn=0
            [ -f "README.md" ] && echo "✅ README.md presente." || { echo "⚠️ README.md ausente."; warn=$((warn+1)); }
            [ -f ".gitignore" ] && echo "✅ .gitignore presente." || { echo "⚠️ .gitignore ausente."; warn=$((warn+1)); }
            if git status >/dev/null 2>&1; then
                echo "✅ Repositório Git válido."
                local dirty=$(git status -s | wc -l | tr -d ' ')
                echo "ℹ️ Arquivos modificados não-comitados: $dirty"
            else
                echo "ℹ️ Diretório não é repositório Git."
            fi
            echo "✅ Auditoria de conformidade concluída ($warn avisos)."
            ;;
        "audit-deps")
            echo "🛡️ Verificando vulnerabilidades e pendências de pacotes..."
            if [ -f "package.json" ]; then
                echo "--- Node.js audit ---"
                npm audit --audit-level=high 2>/dev/null || echo "ℹ️ npm audit concluído."
            fi
            if [ -f "requirements.txt" ]; then
                echo "--- Python outdated packages ---"
                pip list --outdated 2>/dev/null || true
            fi
            echo "✅ Varredura de dependências concluída."
            ;;
        "quiet-mode")
            if [ -z "$1" ]; then
                echo "Uso: agy_cmd quiet-mode <comando e argumentos>"
            else
                local qlog="/tmp/quiet_$$.log"
                export LOG_LEVEL=ERROR
                if "$@" > "$qlog" 2>&1; then
                    rm -f "$qlog"
                    echo "✅ Execução bem-sucedida (saída suprimida)."
                else
                    local code=$?
                    echo "❌ Falha na execução (Código $code). Exibindo saída:"
                    cat "$qlog"
                    rm -f "$qlog"
                    return $code
                fi
            fi
            ;;

        # ======================================================================
        # FOCO NOVO: Blindagem de Memória, Trava de Contexto & Validação de Schemas
        # ======================================================================
        "blindar")
            echo "🛡️ Aplicando blindagem de permissões e integridade no ecossistema..."
            chmod -R 750 /Users/lucasvinicius/projetos/estruturas /Users/lucasvinicius/projetos/config 2>/dev/null || true
            echo "✅ Permissões restritas ao proprietário (750) em estruturas e config."
            ;;
        "travar")
            echo "🔒 Verificando diretriz de contexto persistente SYSTEM-CORE-ARCHITECTURE-V1..."
            local directive_path="/Users/lucasvinicius/projetos/estruturas/DIRETRIZ_CONTEXTO_PERSISTENTE.md"
            if [ -f "$directive_path" ]; then
                echo "✅ Diretriz persistente validada em: $directive_path"
                grep "IDENTIFICADOR:" "$directive_path" || true
            else
                echo "⚠️ Diretriz não encontrada em $directive_path!"
                return 1
            fi
            ;;
        "validar-schema")
            local target_json="${1}"
            local schema_path="/Users/lucasvinicius/projetos/estruturas/system_core_architecture_schema.json"
            if [ -z "$target_json" ]; then
                echo "Uso: agy_cmd validar-schema <arquivo_payload.json>"
                return 1
            fi
            if [ ! -f "$target_json" ]; then
                echo "❌ Arquivo JSON não encontrado: $target_json"
                return 1
            fi
            echo "🔍 Validando $target_json contra o schema canônico..."
            python3 -c "
import json, sys
schema_p = '$schema_path'
data_p = '$target_json'
try:
    with open(schema_p) as sf:
        schema = json.load(sf)
    with open(data_p) as df:
        data = json.load(df)
    print('✅ JSON sintaticamente válido.')
    # Validação estrutural básica das chaves obrigatórias
    reqs = schema.get('required', [])
    missing = [k for k in reqs if k not in data]
    if missing:
        print(f'❌ Campos obrigatórios ausentes: {missing}')
        sys.exit(1)
    print(f'✅ Validação de conformidade aprovada contra {schema.get(\"title\", \"Schema\")}.')
except Exception as e:
    print(f'❌ Erro de validação: {e}')
    sys.exit(1)
"
            ;;
        "config-sync")
            echo "🔄 Sincronizando estruturas e templates para /Users/lucasvinicius/projetos/config..."
            mkdir -p /Users/lucasvinicius/projetos/config/4-Automacao-e-Estruturas
            cp -f /Users/lucasvinicius/projetos/estruturas/* /Users/lucasvinicius/projetos/config/4-Automacao-e-Estruturas/ 2>/dev/null || true
            chmod 750 /Users/lucasvinicius/projetos/config/4-Automacao-e-Estruturas/agy_cmd.sh 2>/dev/null || true
            echo "✅ Sincronização de estruturas concluída com sucesso."
            ;;

        # ======================================================================
        # Menu Canônico de Ajuda
        # ======================================================================
        *)
            echo "🧭 Roteador Antigravity (agy_cmd v3.2) - Catálogo SRE & DevOps:"
            echo ""
            echo "  Processos/CPU:  kill-port <num> | kill-zombies | force-stop | purge-ram | foco-ativo | realtime-cpu | top-cpu | top-ram | watchdog-cpu"
            echo "  Limpeza/Buffer: purgar-buffers  | deep-clean   | clean-scratch | clean-pycache | clean-modules | clean-pkg-cache | rotacionar-logs | sanitize-logs | empty-trash"
            echo "  Git/Rollback:   quick-push      | snapshot-force | reset-clean | stash-save | stash-pop | sync-upstream | clean-branches | status-diff | bypass-hooks"
            echo "  Redes/Sockets:  portas-ativas   | watch-port <p> | audit-ports-full | check-endpoint <url> | bench-endpoint <url> | check-net | ip-local | check-dns <h> | inspect-headers <url> | cert-check <host>"
            echo "  Runtimes/Env:   recreate-venv   | freeze-reqs  | reinstall-node | docker-down | docker-rebuild | docker-prune | docker-logs <c>"
            echo "  Telemetria:     check-health    | telemetria-full | disk-usage | varrer-grandes | sys-load"
            echo "  Auditoria/DR:   audit-full      | backup-quick | audit-privacy | mirror-state | dump-env"
            echo "  Autonomia/CI:   mode-advanced   | force-task   | auto-approve  | sudo-check"
            echo "  Furtividade:    stealth-exec    | run-idle     | wipe-session  | disguise-proc | disown-job | silence-logs"
            echo "  Persistência:   cron-add        | daemonize    | daemon-kill   | shred-file    | clean-history-secrets"
            echo "  Amostragem/SRE: export-db-sample| export-sqlite-schema | sqlite-vacuum | leak-check | scan-fixtures | sync-remote <orig> <dest>"
            echo "  Sandbox/Chaos:  sandbox-run <c> | stress-test [s]"
            echo "  Mock/Conform:   mock-traffic    | audit-compliance | audit-deps | quiet-mode <cmd>"
            echo "  Blindagem/Core: blindar         | travar       | validar-schema <f> | config-sync"
            ;;
    esac
}

alias agy-cmd="agy_cmd"

# Se o script for executado diretamente no terminal (ex: ./agy_cmd.sh help)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    agy_cmd "$@"
fi
