---
name: menu-comandos-rapidos
description: "Menu de Comandos Rápidos e Desbloqueio do Antigravity 2.0. Permite executar ações avançadas de SRE, DevOps, destravamento de Git/portas/processos, modo turbo, auditoria e limpeza usando frases diretas como comandos (/frase-como-comando ou gírias naturais)."
category: operations
risk: safe
source: canonical
tags: "[quick-commands, menu, unlock, sre, devops, antigravity-2.0, shortcuts, series-sequenciais, pipelines]"
date_added: "2026-10-06"
---

# ⚡ Antigravity 2.0 — Menu de Comandos Rápidos & Desbloqueio SRE

Este é o menu oficial de comandos rápidos integrado ao **Antigravity 2.0** (Chat Canvas, Sidebar de Customizações, Slash Commands e Terminal). Ele converte automaticamente frases naturais, gírias operacionais e slash commands em rotinas de engenharia de confiabilidade (SRE), administração local Unix/macOS e **Séries Sequenciais de Alta Potência (Pipelines Multietapas)**.

---

## 🧭 Como Usar no Antigravity 2.0

Você pode invocar qualquer operação de **quatro formas intercambiáveis**:
1. **Slash Command no Chat:** Digite `/destrava-o-git`, `/mata-porta 8080`, `/modo-turbo`, `/auditoria-completa`, etc.
2. **Frase Natural como Comando:** Digite diretamente `"faça uma auditoria completa"`, `"destrava o git"`, `"arranca o lock"`, `"limpa tudo"`.
3. **Comando Canônico ou CLI:** Use `//unlock-git`, `//audit-all` ou execute no terminal `agy_cmd unlock-git`, `agy_cmd audit-full` ou `agy_cmd menu`.
4. **MiniApp Integrado (Console Web Local):** Digite `agy_cmd miniapp` ou abra [`~/.gemini/antigravity-ide/miniapp/index.html`](file:///Users/lucasvinicius/projetos/estruturas/miniapp/index.html) para interface visual com cópia rápida, execução de séries sequenciais e sugestão do próximo comando (*chaining*).

---

## 🔢 MENU NUMÉRICO RÁPIDO (Você Não Precisa Lembrar Frases!)

Se você não quiser lembrar comandos longos ou frases específicas, basta digitar apenas um **número** ou uma **palavra simples** no chat ou terminal:

| Digite apenas | O que o Antigravity executa na hora | Ação SRE Equivalente |
| :---: | :--- | :--- |
| `1` ou `git` | 🔓 **Destrava Git:** Remove `.git/index.lock`, `refs locks` e aborta rebases presos | `agy_cmd unlock-git` |
| `2` ou `porta` | 🚪 **Libera Portas:** Derruba processos ocupando portas 3000, 5173, 8000, 8080, 8765 | `agy_cmd unlock-dev-ports` |
| `3` ou `tudo` | 💥 **Desbloqueio Total (Série 2):** Limpa Git, portas, locks de pacotes, SQLite e kernel | `agy_cmd unlock-all` |
| `4` ou `turbo` | 🏎️ **Modo Turbo (Série 5):** Ativa execução autônoma irrestrita, 8GB heap e ulimit 65536 | `agy_cmd mode-advanced` |
| `5` ou `limpa` | 🧹 **Faxina Profunda (Série 3):** Purga `node_modules`, `__pycache__`, `.DS_Store` e buffers | `agy_cmd deep-clean` |
| `6` ou `audit` | 🛡️ **Auditoria Forense (Série 1):** Varre Git, portas, segredos, disco, kernel e SQLite | `agy_cmd audit-full` |
| `7` ou `limites`| ⚡ **Kernel & SO:** Eleva descritores de arquivo para 65536 e limpa DNS | `agy_cmd unlock-limits` |
| `8` ou `banco` | 🗄️ **SQLite Engine (Série 4):** Executa VACUUM, PRAGMA integrity e checkpoint WAL | `agy_cmd sqlite-vacuum` |
| `9` ou `backup`| 📦 **Snapshot / DR:** Cria arquivo tar.gz isolado com timestamp de segurança | `agy_cmd backup-quick` |
| `menu` ou `?` | 🧭 **Exibe este menu:** Lista todas as opções interativas | `agy_cmd menu` |

### 🧠 Detecção Automática por Sintoma (Fuzzy Intent):
Você não precisa se preocupar com sintaxe. Basta dizer o sintoma:
- *"travou"*, *"tá preso"*, *"deu lock"* ➔ Destrava Git e locks órfãos (Opção `1`)
- *"porta ocupada"*, *"porta em uso"*, *"erro de porta"* ➔ Libera sockets TCP (Opção `2`)
- *"mac lerdo"*, *"sem memória"*, *"ram cheia"* ➔ Purga RAM e buffers
- *"limpa o lixo"*, *"apaga temporários"* ➔ Faxina profunda (Opção `5`)
- *"socorro"*, *"desbloqueia tudo"* ➔ Desbloqueio geral do sistema (Opção `3`)

---

## 🌟 SÉRIES SEQUENCIAIS DE ALTA POTÊNCIA (UMA FRASE ➔ PIPELINE COMPLETO)

> **Princípio:** No Antigravity 2.0, comandos de macro-intenção coloquiais disparam automaticamente uma **Série Sequencial de Operações SRE Relacionadas**, compilando ao final um **Relatório Forense Hiper-Detalhado**.

| Série Sequencial | Frases-Gatilho Aceitas | Slash Command | Atalho | Pipeline de Etapas Executadas | Entregável / Relatório |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SÉRIE 1: Auditoria Forense Completa** | `"faça uma auditoria completa"`, `"auditoria completa"`, `"raio-x completo"`, `"puxa a ficha de tudo"` | `/auditoria-completa` | `//audit-all` | **[1] Git:** status, branch, HEAD, fsck integridade física.<br>**[2] Rede:** portas LISTEN, dev ports 3000..8765, sockets 0.0.0.0.<br>**[3] Segurança:** varredura de tokens/chaves, .env drift.<br>**[4] Armazenamento:** df -h, SMART status, top pastas >50MB.<br>**[5] Kernel:** top CPU/RAM, ulimit descritores, throttling térmico.<br>**[6] Banco SQLite:** checagem física de páginas (`PRAGMA`). | Relatório forense estruturado em `reports/audit_TIMESTAMP.md` + Resumo executivo no terminal. |
| **SÉRIE 2: Desbloqueio Total de Sistema** | `"destrava tudo"`, `"desbloqueio total"`, `"socorro travou tudo"`, `"desbloqueia o mac"` | `/desbloqueio-total` | `//unlock-all` | **[1] Git:** elimina `.git/index.lock`, `refs locks`, aborta rebase/merge.<br>**[2] Portas Dev:** finaliza PIDs nas portas 3000, 5173, 8000, 8080, 8765.<br>**[3] Pacotes:** limpa locks corrompidos de NPM, Yarn, PNPM e Homebrew.<br>**[4] Sockets/PIDs:** remove locks em `/tmp` (.s.PGSQL, redis.sock, .pid órfãos).<br>**[5] Zumbis:** finaliza workers mortos em deadlock (`SIGKILL`).<br>**[6] SQLite:** força checkpoint WAL TRUNCATE em todas as bases locais.<br>**[7] Kernel:** eleva `ulimit -n 65536` e recicla cache de DNS. | Relatório de desengasgamento com PIDs finalizados e portas liberadas. |
| **SÉRIE 3: Faxina Profunda de Recursos** | `"faxina profunda"`, `"limpa tudo"`, `"limpeza geral"`, `"apaga o lixo de compilação"` | `/faxina-profunda` | `//deep-clean` | **[1] Caches de Build:** purga `__pycache__`, `.pytest_cache`, `.DS_Store`, `.turbo`, `.next`.<br>**[2] Caches de Pacotes:** higieniza e valida cache do npm, pip e yarn.<br>**[3] Rotação de Logs:** compacta em gzip arquivos de log com >50MB.<br>**[4] Temporários:** esvazia `/tmp` do usuário e Lixeira (`~/.Trash`).<br>**[5] Memória RAM:** força `sync` de inodes e purga buffers de RAM do kernel. | Relatório comparativo de espaço livre em disco (Antes vs Depois). |
| **SÉRIE 4: Manutenção de Banco SQLite** | `"otimiza o banco"`, `"dá um trato no banco"`, `"passa o aspirador na base"`, `"revisa o sqlite"` | `/otimiza-banco` | `//db-optimize-full` | **[1] Descoberta:** localiza todas as bases `.sqlite`, `.db` no projeto.<br>**[2] Integridade:** executa `PRAGMA integrity_check` em cada página.<br>**[3] WAL Checkpoint:** força checkpoint e trunca `-wal` para o banco principal.<br>**[4] Desfragmentação:** executa `VACUUM` reduzindo tamanho físico em disco.<br>**[5] Query Planner:** executa `REINDEX`, `ANALYZE` e `PRAGMA optimize`. | Relatório de volumetria, redução de páginas e saúde da árvore B. |
| **SÉRIE 5: Modo Turbo de Alta Potência** | `"modo turbo"`, `"liga o modo turbo"`, `"modo pro"`, `"pro"`, `"roda sem pedir licença"`, `"alta autonomia"` | `/modo-turbo` | `//turbo-run` | **[1] Limites de SO:** eleva `ulimit -n 65536` e `ulimit -u 4096`.<br>**[2] Runtimes:** define Node.js heap em 8GB e recursão Python em 50.000.<br>**[3] Autonomia:** injeta flags CI não-interativas e bypass de prompts.<br>**[4] Anti-Sono:** ativa `caffeinate` impedindo suspensão de CPU/display. | Resumo de ambiente turbinado com perfil de potência máxima ativo. |
| **SÉRIE 6: Pré-Deploy & Sincronização** | `"prepara producao"`, `"higieniza para deploy"`, `"auditoria pre push"`, `"valida antes de subir"` | `/prepara-deploy` | `//pre-deploy-audit` | **[1] Segredos:** varredura regex rigorosa de tokens e chaves privadas.<br>**[2] Env Drift:** comparação de chaves entre `.env` e `.env.example`.<br>**[3] Git Hygiene:** auditoria de integridade do Git e arquivos untracked.<br>**[4] Sanitização:** higienização de dados confidenciais em logs locais.<br>**[5] Rollback:** geração automática de snapshot `.tar.gz` com timestamp. | Veredito formal de autorização para push (`AUTORIZADO` ou `BLOQUEADO`). |
| **SÉRIE 7: Red Teaming & Resiliência** | `"teste de resiliencia"`, `"red teaming completo"`, `"stress test geral"`, `"simula ataque de estresse"` | `/teste-resiliencia` | `//resilience-suite` | **[1] Superfície:** varredura de portas expostas em `0.0.0.0` vs `127.0.0.1`.<br>**[2] CVEs:** auditoria de vulnerabilidades conhecidas em dependências.<br>**[3] Rate-Limit:** teste de bypass de cabeçalhos (`X-Forwarded-For`).<br>**[4] Estresse:** simulação controlada de conexões concorrentes. | Relatório de resiliência e recomendações de hardening de infraestrutura. |
| **SÉRIE 9: Auditoria Total em 10 Camadas** | `"auditoria total"`, `"faça uma auditoria total"`, `"audite todas as camadas"`, `"auditoria em todas as camadas"` | `/auditoria-total` | `//audit-total` | **[1] UI:** Componentes, renderização e a11y.<br>**[2] Interação:** Handlers e fluxos UX.<br>**[3] Estado:** Stores e reatividade.<br>**[4] Rede/API:** Clientes e timeouts.<br>**[5] Gateway/Borda:** Reverse proxies e TLS.<br>**[6] Entrada/API:** Controladores e rotas.<br>**[7] Segurança:** Middlewares e tokens.<br>**[8] Serviços:** Regras de negócio e use cases.<br>**[9] ORM/Persistência:** Repositórios e migrations.<br>**[10] Banco de Dados:** Integridade, WAL e disco. | Execução invisível e silenciosa em background (`AGY_BACKGROUND`, sem foco visual) com relatório em `reports/audit_total_TIMESTAMP.md`. |
| **SÉRIE 10: Auditoria Global em 23 Camadas** | `"auditoria global"`, `"faça uma auditoria global"`, `"audite todas as camadas globais"`, `"auditoria global em todas as camadas"`, `"raio-x global"` | `/auditoria-global` | `//audit-global` | **[1] Frontend (Surface Web):** UI, Interação, Estado, Cliente API.<br>**[2] Borda & Perímetro:** WAF, CDN, Gateway & DNS/LB.<br>**[3] Backend (Deep Web):** APIs, Auth Middleware, Serviços, Filas, Cache, ORM.<br>**[4] Armazenamento & BI:** Storage SQL/NoSQL, Réplicas DW.<br>**[5] DevOps (Abaixo do Backend):** Web Servers, Containers, K8s, SO, IaC, Cloud.<br>**[6] Operações Transversais:** CI/CD, Observabilidade & Telemetria. | Execução invisível e silenciosa em background (`AGY_BACKGROUND`, sem foco visual) com relatório em `reports/audit_global_TIMESTAMP.md`. |

### 📑 Protocolo Obrigatório do Relatório Forense Hiper-Detalhado
Ao executar uma série sequencial, o Antigravity compila obrigatoriamente um relatório contendo:
1. **🧭 Identificação Operacional:** Data/Hora (local e UTC), Host, Workspace canônico, Modo e Status preliminar.
2. **⏱️ Linha do Tempo da Série Executada:** Tabela de passos 1..N com escopo, comando shell real executado e status (`[OK]`, `[ALERTA]`, `[FALHA]`).
3. **📊 Evidências Empíricas Quantitativas:** Espaço em disco (antes/depois), descritores abertos vs teto `ulimit`, PIDs terminados, portas liberadas, latência em ms.
4. **🔬 Diagnóstico Forense por Camada:** Análise de Git, Rede/Sockets, Segurança/Segredos, Armazenamento/Disco, Kernel/Processos e Banco de Dados.
5. **🎯 Matriz de Risco & Anomalias:** Severidade (`CRÍTICO`, `ALTO`, `MÉDIO`, `BAIXO`, `INFO`) com ações de remediação recomendadas.
6. **⚖️ Veredito Operacional Canônico:** Estado final validado (`VALIDADO`, `CONFORME`, `REQUER_ATENÇÃO`, `BLOCKED`, `DONE`).
7. **🔗 Grafo de Chaining Inteligente:** Próximo passo sugerido da esteira SRE para prosseguir o fluxo de trabalho.

---

## 🔓 MENU 1: DESTRAVAMENTO CRÍTICO DE SISTEMA (LOCKS, PORTAS & DEADLOCKS)

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/destrava-o-git` | `"destrava o git"`, `"arranca o lock"` | `//unlock-git` | Remove locks órfãos de índice e referências do Git. | `rm -f .git/index.lock .git/refs/heads/*.lock .git/HEAD.lock 2>/dev/null` |
| `/aborta-rebase` | `"cancela rebase travado"`, `"aborta o merge preso"` | `//unlock-git-rebase` | Cancela compulsoriamente rebase, merge ou cherry-pick em conflito/travado. | `git rebase --abort 2>/dev/null \|\| git merge --abort 2>/dev/null \|\| rm -rf .git/rebase-merge` |
| `/mata-porta <PORTA>` | `"libera a porta 8080"`, `"derruba quem tá na porta 3000"` | `//unlock-port <PORTA>` | Localiza o PID na porta TCP especificada e finaliza com SIGTERM seguido de SIGKILL. | `PID=$(lsof -ti :<PORTA>); [ -n "$PID" ] && kill -15 $PID 2>/dev/null \|\| kill -9 $PID 2>/dev/null` |
| `/mata-portas-padrao` | `"limpa as portas de dev"`, `"mata processos dev"` | `//unlock-dev-ports` | Libera em lote as portas 3000, 5173, 8000, 8080 e 8765. | `for p in 3000 5173 8000 8080 8765; do pid=$(lsof -ti :$p); [ -n "$pid" ] && kill -9 $pid 2>/dev/null; done` |
| `/libera-arquivo <ARQ>` | `"destrava esse arquivo"`, `"quem tá segurando esse arquivo"` | `//unlock-file <ARQ>` | Identifica os PIDs mantendo descritores abertos no arquivo e força liberação. | `fuser -k -9 <ARQ> 2>/dev/null \|\| lsof -t <ARQ> \| xargs kill -9 2>/dev/null` |
| `/destrava-banco <DB>` | `"destrava o sqlite"`, `"limpa o lock da base"` | `//unlock-sqlite <DB>` | Executa checkpoint WAL em modo TRUNCATE e remove locks temporários de transações. | `sqlite3 <DB> 'PRAGMA wal_checkpoint(TRUNCATE);' 2>/dev/null; rm -f <DB>-wal <DB>-shm 2>/dev/null` |
| `/destrava-pacotes` | `"destrava o npm"`, `"arranca trava de pacotes"` | `//unlock-package-managers` | Remove locks de pacotes e limpa índices corrompidos do Homebrew, NPM e Yarn. | `rm -f package-lock.json.lock yarn.lock.tmp 2>/dev/null; npm cache verify 2>/dev/null` |
| `/mata-zumbis` | `"mata processos zumbis"`, `"limpa tarefas penduradas"` | `//unlock-zombie-tasks` | Encerra processos orfãos e filhos em deadlock mantidos pelo usuário corrente. | `ps -A -o stat,ppid,pid \| grep -e '^[Zz]' \| awk '{print $2}' \| xargs kill -9 2>/dev/null` |
| `/desbloqueio-total` | `"destrava tudo"`, `"desbloqueio geral do sistema"` | `//unlock-all` | Dispara Série 2: destrava Git, limpa portas padrão, mata zumbis, trunca WAL e reseta locks. | `agy_cmd unlock-all` |
| `/destrava-index` | `"destrava index"`, `"apaga index.lock"` | `//unlock-git-index` | Remove exclusivamente `.git/index.lock` liberando operações de git add/commit. | `agy_cmd unlock-git-index` |
| `/destrava-git-config` | `"destrava config do git"`, `"apaga config.lock"` | `//unlock-git-config` | Remove trava `.git/config.lock` gerada por concorrência de escrita. | `agy_cmd unlock-git-config` |
| `/libera-faixa-portas [I] [F]` | `"faixa de portas"`, `"libera portas 3000 a 3010"` | `//unlock-port-range` | Itera e derruba com SIGKILL processos em intervalo de portas TCP. | `agy_cmd unlock-port-range 3000 3010` |
| `/mata-por-nome <N>` | `"mata por nome"`, `"mata sem piedade pelo nome"` | `//unlock-kill-by-name` | Encerra compulsoriamente com SIGKILL processos pelo nome exato (`pkill -9 -x`). | `agy_cmd unlock-kill-by-name "$1"` |
| `/forca-destrave-sqlite [DB]` | `"força destrave do sqlite"`, `"trunca wal na marra"` | `//unlock-sqlite-force` | Mata processos segurando o banco, trunca o WAL e remove `-shm` e `-wal`. | `agy_cmd unlock-sqlite-force "${1:-database.sqlite}"` |
| `/aborta-bisect` | `"aborta bisect"`, `"cancela git bisect"` | `//unlock-git-bisect` | Cancela e reseta compulsoriamente operação de `git bisect` travada no repo. | `agy_cmd unlock-git-bisect` |
| `/poda-worktree` | `"poda worktree"`, `"destrava worktree do git"` | `//unlock-git-worktree` | Executa `git worktree prune` limpando metadados de worktrees órfãs. | `agy_cmd unlock-git-worktree` |
| `/destrava-yarn` | `"destrava yarn"`, `"limpa lock do yarn"` | `//unlock-yarn-lock` | Remove travas de cache e arquivos `.tmp` residuais do Yarn. | `agy_cmd unlock-yarn-lock` |
| `/destrava-pnpm` | `"destrava pnpm"`, `"pnpm store travada"` | `//unlock-pnpm-lock` | Remove locks do store global do PNPM permitindo instalar dependências. | `agy_cmd unlock-pnpm-lock` |
| `/destrava-pip` | `"destrava pip"`, `"pip cache travado"` | `//unlock-pip-lock` | Limpa locks e caches corrompidos de instalação do Pip/Pipx. | `agy_cmd unlock-pip-lock` |
| `/forca-soltar-arquivo <A>` | `"força soltar arquivo"`, `"mata quem segura o arquivo"` | `//unlock-file-force` | Aplica lsof no arquivo e finaliza processos concorrentes com SIGKILL. | `agy_cmd unlock-file-force "$1"` |
| `/forca-soltar-pasta [D]` | `"força soltar pasta"`, `"destrava árvore inteira"` | `//unlock-dir-tree` | Aplica `lsof -t +D` em toda a árvore e encerra processos bloqueando o diretório. | `agy_cmd unlock-dir-tree "${1:-.}"` |
| `/mata-terminais-ociosos` | `"mata terminais parados"`, `"zumbis do zsh"` | `//unlock-stuck-terminals` | Encerra subshells e terminais zumbis ociosos retendo conexões e RAM. | `agy_cmd unlock-stuck-terminals` |
| `/destrava-postgres-local` | `"destrava postgres local"`, `"apaga socket do postgres"` | `//unlock-postgres-local` | Remove arquivos de socket temporários e locks `.s.PGSQL.*` em `/tmp`. | `agy_cmd unlock-postgres-local` |
| `/destrava-redis-local` | `"destrava redis local"`, `"apaga socket do redis"` | `//unlock-redis-local` | Finaliza instâncias órfãs de `redis-server` e limpa sockets em `/tmp`. | `agy_cmd unlock-redis-local` |
| `/fecha-chrome-debug` | `"fecha chrome debug"`, `"mata chrome com porta remota"` | `//unlock-chrome-debug` | Encerra processos do Google Chrome com porta de depuração ativa. | `agy_cmd unlock-chrome-debug` |

---

## ⚡ MENU 2: RUNTIMES, KERNEL & SISTEMA OPERACIONAL (macOS / UNIX)

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/limpa-quarentena <ALVO>` | `"tira a quarentena"`, `"remove bloqueio do mac"` | `//unlock-quarantine <ALVO>` | Remove atributo estendido `com.apple.quarantine` de binários baixados via Gatekeeper. | `xattr -dr com.apple.quarantine <ALVO> 2>/dev/null` |
| `/turbina-limites` | `"sobe os limites de arquivo"`, `"aumenta o ulimit"` | `//unlock-limits` | Eleva temporariamente o limite de descritores abertos para 65536 na sessão. | `ulimit -n 65536 2>/dev/null \|\| ulimit -n 8192 2>/dev/null` |
| `/reseta-dns` | `"limpa cache de rede"`, `"flush no dns"` | `//unlock-dns-cache` | Limpa o cache DNS local e reinicia o resolvedor de nomes mDNSResponder do macOS. | `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder 2>/dev/null` |
| `/reseta-proxy` | `"arranca o proxy"`, `"destrava a conexao de rede"` | `//unlock-network-proxies` | Desarma variáveis de ambiente que forçam proxies HTTP/HTTPS na sessão shell. | `unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy` |
| `/destrava-ssh` | `"reinicia o agente ssh"`, `"recarrega chaves ssh"` | `//unlock-ssh-agent` | Limpa e reinicia o socket do ssh-agent e recarrega identidades do Keychain. | `eval $(ssh-agent -s) >/dev/null; ssh-add --apple-load-keychain 2>/dev/null` |
| `/destrava-docker` | `"reinicia socket do docker"`, `"destrava o docker"` | `//unlock-docker-socket` | Reativa permissões e reconecta o socket Unix da VM Docker local. | `sudo chmod 666 /var/run/docker.sock 2>/dev/null \|\| open -a Docker` |
| `/aumenta-maxproc` | `"aumenta maxproc"`, `"erro cannot fork"` | `//unlock-kernel-maxproc` | Eleva limite máximo de processos permitidos por usuário no kernel (`ulimit -u 4096`). | `agy_cmd unlock-kernel-maxproc` |
| `/recicla-portas-rapidas` | `"recicla portas rápidas"`, `"ajusta msl do tcp"` | `//unlock-ephemeral-ports` | Reduz MSL do TCP via sysctl acelerando reciclagem de portas efêmeras. | `agy_cmd unlock-ephemeral-ports` |
| `/limpa-tabela-arp` | `"limpa tabela arp"`, `"reseta arp cache"` | `//unlock-arp-cache` | Purga tabela ARP de resolução de hardware no macOS resolvendo conflitos. | `agy_cmd unlock-arp-cache` |
| `/desativa-ipv6-wifi` | `"desativa ipv6 no wifi"`, `"dns lento ipv6"` | `//unlock-ipv6-disable` | Desativa pilha IPv6 na interface Wi-Fi sanando atrasos e timeouts de rede. | `agy_cmd unlock-ipv6-disable` |
| `/destrava-keychain` | `"destrava keychain"`, `"abre chaveiro de login"` | `//unlock-macos-keychain` | Destrava o chaveiro de login do macOS via terminal com o utilitário `security`. | `agy_cmd unlock-macos-keychain` |
| `/pausa-spotlight [DIR]` | `"pausa spotlight"`, `"para indexação da pasta"` | `//unlock-spotlight-indexing` | Desativa indexação do Spotlight no diretório informado reduzindo I/O. | `agy_cmd unlock-spotlight-indexing "${1:-.}"` |
| `/tira-quarentena-pasta [DIR]`| `"tira quarentena recursiva"` | `//unlock-quarantine-recursive` | Remove atributo `com.apple.quarantine` recursivamente de toda a pasta. | `agy_cmd unlock-quarantine-recursive "${1:-.}"` |
| `/impede-sono-mac` | `"não deixa o mac dormir"`, `"mantém mac acordado"` | `//unlock-caffeinate-session` | Dispara `caffeinate` em background mantendo CPU, disco e tela acordados. | `agy_cmd unlock-caffeinate-session` |
| `/aumenta-ram-node` | `"aumenta ram do node"`, `"node heap 8gb"` | `//unlock-node-memory` | Configura NODE_OPTIONS para 8GB de heap prevenindo erro de Heap Out of Memory. | `agy_cmd unlock-node-memory` |
| `/aumenta-recursao-python` | `"aumenta recursão do python"`, `"recursion limit 50000"` | `//unlock-python-recursion` | Eleva dinamicamente o limite de chamadas recursivas do Python para 50.000. | `agy_cmd unlock-python-recursion` |
| `/reseta-credenciais-git` | `"reseta credenciais do git"`, `"apaga chaveiro do git"` | `//unlock-git-credentials` | Remove credenciais e tokens cacheados de github.com no osxkeychain. | `agy_cmd unlock-git-credentials` |
| `/checa-firewall` | `"status do firewall"`, `"socketfilterfw status"` | `//unlock-firewall-dev` | Consulta o estado do firewall de sockets do macOS (`socketfilterfw`). | `agy_cmd unlock-firewall-dev` |
| `/destrava-docker-compose` | `"derruba docker compose com volumes"` | `//unlock-docker-compose` | Executa `docker compose down -v --remove-orphans` expurgando containers e volumes. | `agy_cmd unlock-docker-compose` |
| `/reinicia-coreaudio` | `"reinicia áudio do mac"`, `"killall coreaudiod"` | `//unlock-coreaudio` | Reinicia daemon CoreAudio liberando CPU retida por subsistema de som. | `agy_cmd unlock-coreaudio` |
| `/reinicia-servico-launchd <S>`| `"reinicia serviço do launchd"` | `//unlock-launchd-service` | Força reinício imediato de um serviço do usuário com `launchctl kickstart -k`. | `agy_cmd unlock-launchd-service "$1"` |

---

## 🛡️ MENU 3: AUDITORIA, PRIVACIDADE & SEGURANÇA

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/auditoria-completa` | `"faça uma auditoria completa"`, `"raio-x completo"`, `"puxa a ficha de tudo"` | `//audit-all` | Dispara Série 1: varre Git, portas, segredos, disco, kernel e SQLite gerando relatório forense. | `agy_cmd audit-full` |
| `/auditoria-total` | `"auditoria total"`, `"faça uma auditoria total"`, `"audite todas as camadas"` | `//audit-total` | Dispara Série 9: varre as 10 camadas de ponta a ponta (UI, Interação, Estado, API client, Gateway, Controller, Middleware, Services, ORM, DB) de forma invisível e silenciosa. | `agy_cmd audit-total` |
| `/auditoria-global` | `"auditoria global"`, `"faça uma auditoria global"`, `"raio-x global"` | `//audit-global` | Dispara Série 10: varre os 6 domínios e 23 camadas estruturais (Surface, Borda, Deep Web, Dados, DevOps, Operações Transversais) de forma invisível e silenciosa. | `agy_cmd auditoria-global` |
| `/varre-vazamentos` | `"procura vazamento de chave"`, `"tem token solto?"` | `//audit-secrets` | Varre o workspace procurando arquivos `.env`, chaves privadas SSH e tokens de API expostos. | `grep -rnEI 'AKIA[0-9A-Z]{16}\|ghp_[0-9a-zA-Z]{36}\|BEGIN PRIVATE KEY' . --exclude-dir=.git` |
| `/higieniza-logs` | `"limpa os rastros"`, `"apaga logs sensíveis"` | `//sanitize-logs` | Mascara senhas, CPFs, tokens e emails em arquivos `.log` do projeto. | `sed -i '' -E 's/(bearer[[:space:]]+)[A-Za-z0-9._-]+/\1[REDACTED]/gI' *.log 2>/dev/null` |
| `/snapshot-seguranca` | `"tira uma foto do estado"`, `"salva ponto de restauração"` | `//backup-snapshot` | Cria arquivo tar.gz isolado do estado atual com timestamp para rollback imediato. | `tar --exclude='.git' -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .` |
| `/audita-integridade-git` | `"audita integridade do git"`, `"fsck no git"` | `//audit-git-integrity` | Executa `git fsck --full --strict` checando integridade de objetos do repo. | `agy_cmd audit-git-integrity` |
| `/audita-env-drift` | `"compara env com exemplo"`, `"env drift"` | `//audit-env-drift` | Compara chaves entre `.env` e `.env.example` acusando variáveis faltantes ou órfãs. | `agy_cmd audit-env-drift` |
| `/audita-tls [HOST]` | `"checa certificado tls"`, `"quando expira o ssl"` | `//audit-tls-cert` | Conecta via OpenSSL na porta 443 do host alvo e extrai validade e CA do cert. | `agy_cmd audit-tls-cert "${1:-github.com}"` |
| `/varre-historico-git` | `"segredos no histórico"`, `"pii no git log"` | `//audit-git-history-pii` | Varre os diffs dos últimos 50 commits por senhas, tokens e chaves privadas. | `agy_cmd audit-git-history-pii` |
| `/audita-cron-launchd` | `"tarefas agendadas"`, `"lista cron e launchd"` | `//audit-cron-launchd` | Mapeia tarefas recorrentes no crontab e lista agentes em `~/Library/LaunchAgents`. | `agy_cmd audit-cron-launchd` |
| `/audita-dns-leak` | `"vazamento de dns"`, `"quais dns meu mac tá usando"` | `//audit-dns-leak` | Audita servidores DNS configurados no macOS via `scutil --dns` detectando vazamentos. | `agy_cmd audit-dns-leak` |
| `/audita-binarios` | `"binários instalados"`, `"programas em usr local bin"` | `//audit-installed-binaries` | Lista cronologicamente os binários executáveis em `/usr/local/bin` e Homebrew. | `agy_cmd audit-installed-binaries` |
| `/audita-saude-ssd` | `"saúde do ssd"`, `"smart status"` | `//audit-storage-smart` | Extrai telemetria de integridade de disco, status SMART e espaço livre via diskutil. | `agy_cmd audit-storage-smart` |
| `/audita-throttling` | `"mac tá esquentando"`, `"thermal throttling"` | `//audit-thermal-throttling` | Consulta subsistema de energia (`pmset -g therm`) para verificar throttling de CPU. | `agy_cmd audit-thermal-throttling` |
| `/audita-npm-global` | `"pacotes globais do npm"`, `"lista npm -g"` | `//audit-npm-global` | Lista pacotes Node.js instalados globalmente no sistema (`npm list -g --depth=0`). | `agy_cmd audit-npm-global` |
| `/audita-zsh-env` | `"audita zshrc"`, `"tem alias malicioso no terminal"` | `//audit-zsh-env` | Varre `.zshrc` e `.zshenv` por aliases maliciosos, injeções de PATH ou chamadas eval. | `agy_cmd audit-zsh-env` |
| `/backup-git-bundle [N]` | `"backup em bundle"`, `"bundle do git com tudo"` | `//backup-git-bundle` | Empacota todo o repositório Git em um único arquivo `.bundle` autocontido. | `agy_cmd backup-git-bundle "$1"` |
| `/audita-fd-leak` | `"vazamento de descritores"`, `"top processos fd leak"` | `//audit-open-files-leak` | Rankeia os top 15 processos consumindo mais descritores de arquivos abertos. | `agy_cmd audit-open-files-leak` |
| `/audita-rotas-rede` | `"tabela de rotas"`, `"rotas de rede no mac"` | `//audit-network-routes` | Inspeciona tabela de rotas ativas do kernel IPv4 no macOS via `netstat -rn -f inet`. | `agy_cmd audit-network-routes` |
| `/limpa-clipboard-pii` | `"limpa clipboard"`, `"apaga senha copiada"` | `//audit-clipboard-pii` | Inspeciona área de transferência do macOS por segredos/PII e higieniza com pbcopy. | `agy_cmd audit-clipboard-pii` |

---

## 🏎️ MENU 4: ALTA AUTONOMIA & MODO TURBO

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/modo-turbo` | `"liga o modo turbo"`, `"roda sem pedir licença"` | `//turbo-run` | Dispara Série 5: ulimit 65536, Node heap 8GB, Python recursion 50.000, caffeinate e flags CI. | `agy_cmd mode-advanced` |
| `/autonomia-total` | `"modo turbo sem travas"`, `"execução não interativa"` | `//unlock-agent-full` | Define variáveis de ambiente para execução autônoma irrestrita de CI e npm. | `export AGY_EFFORT=high AGY_NON_INTERACTIVE=1 CI=true npm_config_yes=true` |
| `/eleva-prioridade` | `"dá prioridade máxima"`, `"renice processo"` | `//realtime-cpu` | Ajusta o nice do processo para -20 e elimina workers concorrentes consumindo CPU. | `renice -n -20 -p $$ 2>/dev/null; kill -9 $(pgrep -f "webpack\|orphan") 2>/dev/null` |
| `/ignora-hooks` | `"ignora os hooks do git"`, `"pula validação pré-commit"` | `//bypass-hooks` | Realiza commit contornando compulsoriamente hooks do husky/pre-commit com `--no-verify`. | `git commit --no-verify -m "chore: bypass validation hooks"` |

---

## 🕵️ MENU 5: OCULTAÇÃO, FURTIVIDADE & AMBIENTE SILENCIOSO

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/modo-silencioso` | `"opera nas sombras"`, `"executa no sapatinho"` | `//stealth-exec` | Redireciona stdout e stderr para `/dev/null` e executa desacoplado via nohup. | `nohup ./task.sh >/dev/null 2>&1 &` |
| `/roda-desacoplado` | `"solta do terminal"`, `"disown no job"` | `//disown-job` | Desvincula o processo do terminal corrente para não encerrar quando o terminal fechar. | `disown -h %1 2>/dev/null` |
| `/apaga-historico` | `"apaga o histórico do terminal"`, `"limpa rastro zsh"` | `//clean-history-tail` | Limpa os últimos comandos digitados no histórico do ZSH sem deixar registros. | `history -c 2>/dev/null; rm -f ~/.zsh_history` |
| `/roda-em-subshell` | `"executa isolado sem alterar o shell"` | `//run-detached-subshell` | Executa comando dentro de subshell isolado sem poluir variáveis do ambiente pai. | `( export VAR=val; ./script.sh )` |

---

## 🗄️ MENU 6: BANCO DE DADOS & SQLITE ENGINE

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/otimiza-banco <DB>` | `"dá um trato no banco"`, `"passa o aspirador na base"` | `//db-vacuum <DB>` | Dispara Série 4: VACUUM completo, análise de tabelas e reconstrução de índices. | `sqlite3 "$1" 'VACUUM; ANALYZE; REINDEX;'` |
| `/checa-integridade <DB>` | `"a base tá corrompida?"`, `"passa o pente fino no sqlite"` | `//db-integrity <DB>` | Valida a integridade física de todas as páginas da base SQLite via PRAGMA. | `sqlite3 "$1" 'PRAGMA integrity_check;'` |
| `/forca-checkpoint <DB>` | `"descarrega o wal no disco"`, `"força o sync da base"` | `//db-checkpoint <DB>` | Força sincronização de páginas do arquivo de log (.wal) para o arquivo mestre (.db). | `sqlite3 "$1" 'PRAGMA wal_checkpoint(FULL);'` |
| `/compara-schemas <D1> <D2>` | `"compara os schemas das bases"`, `"diff nas tabelas"` | `//diff-db-schemas` | Exibe o diff unificado da estrutura DDL entre dois bancos de dados SQLite. | `diff -u <(sqlite3 "$1" .schema) <(sqlite3 "$2" .schema)` |

---

## 🧹 MENU 7: FAXINA PROFUNDA & LIBERAÇÃO DE DISCO

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/faxina-profunda` | `"limpa a sujeira do disco"`, `"apaga lixo de compilação"` | `//deep-clean` | Dispara Série 3: remove caches recursivos, compacta logs, esvazia temporários e purga RAM. | `agy_cmd deep-clean` |
| `/purga-ram` | `"solta a memória presa"`, `"drena o cache da ram"` | `//purge-ram` | Solicita ao kernel do macOS a purga de memória inativa e buffers de páginas de disco. | `sudo -n purge 2>/dev/null \|\| sync` |
| `/limpa-scratch` | `"limpa arquivos temporários"`, `"esvazia scratch"` | `//clean-scratch` | Esvazia a pasta efêmera de rascunhos e scripts temporários do IDE Antigravity. | `rm -rf /Users/lucasvinicius/.gemini/antigravity-ide/scratch/* 2>/dev/null` |
| `/reseta-workspace` | `"reseta o git pro head"`, `"descarta tudo que fiz de errado"` | `//reset-clean` | Descarta alterações locais não salvas e remove arquivos não rastreados no repositório. | `git reset --hard HEAD && git clean -fd` |

---

## 🎯 MENU 8: RED TEAMING, SIMULAÇÃO DE ATAQUE & RESILIÊNCIA EXTREMA (SRE DEFENSIVO)

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE Executada | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/teste-resiliencia` | `"teste de resiliencia"`, `"red teaming completo"` | `//resilience-suite` | Dispara Série 7: varredura de superfície, CVEs, bypass de headers e teste de estresse. | `agy_cmd resilience-suite` |
| `/ataque-ddos [URL]` | `"ataque ddos sintético"`, `"bombardeia a api"` | `//attack-ddos-sim` | Dispara bateria de até 1000 conexões concorrentes para testar resiliência a DoS/DDoS. | `agy_cmd attack-ddos-sim "${1:-http://localhost:3000}" 500 25` |
| `/fuzzing-extremo [URL]` | `"fuzzing na api com payloads extremos"` | `//fuzz-api-extreme` | Injeta bateria de boundary payloads (SQLi, XSS, null bytes, 8KB buffers) contra endpoint. | `agy_cmd fuzz-api-extreme "${1:-http://localhost:3000}"` |
| `/varre-portas` | `"mapeia superfície de ataque"`, `"vê o que tá aberto"` | `//scan-attack-surface` | Mapeia todas as portas LISTEN em `0.0.0.0` vs `127.0.0.1` detectando exposições acidentais na rede. | `agy_cmd scan-attack-surface` |
| `/testa-ratelimit [URL]` | `"testa se o rate limit é burlável"` | `//bypass-ratelimit-test` | Simula spoofing de IP via headers (`X-Forwarded-For`) para validar proteção de rate-limiting. | `agy_cmd bypass-ratelimit-test "${1:-http://localhost:3000}"` |
| `/forca-bruta-sim [URL]` | `"simula ataque de força bruta"` | `//bruteforce-sim` | Dispara 15 tentativas rápidas de login incorretas testando lockout e códigos 429/403. | `agy_cmd bruteforce-sim "${1:-http://localhost:3000/api/login}"` |
| `/congelamento-chaos <ALVO>` | `"ataque de sinal congelante"`, `"chaos test de freeze"` | `//chaos-freeze-thaw` | Envia SIGSTOP paralisando worker por 5s no kernel e retoma com SIGCONT (teste de supervisor). | `agy_cmd chaos-freeze-thaw "${1:-node}"` |
| `/esgota-descritores` | `"ataque de exaustão de descritores"` | `//stress-fd-exhaustion` | Abre milhares de descritores simultâneos testando se a aplicação trata erro EMFILE graciosamente. | `agy_cmd stress-fd-exhaustion` |
| `/slowloris-sim [H] [P]` | `"simula slowloris no servidor local"` | `//slowloris-sim` | Abre sockets enviando cabeçalhos lentos fracionados para validar `client_header_timeout`. | `agy_cmd slowloris-sim "${1:-127.0.0.1}" "${2:-3000}"` |
| `/varre-cve` | `"procura exploits nas dependências"`, `"audita cves"` | `//audit-cve-extreme` | Varre vulnerabilidades conhecidas (CVEs) em pacotes npm e bibliotecas Python. | `agy_cmd audit-cve-extreme` |
| `/audita-privilegios` | `"audita vetor de invasão local"`, `"procura suid root"` | `//audit-privesc-vectors` | Audita binários com bit SUID ativado, diretórios com escrita universal e regras de sudo. | `agy_cmd audit-privesc-vectors` |

---

## 🌐 MENU 9: ESPELHAMENTO & DOWNLOAD ESTÁTICO DE FRONTEND

| Frase como Comando (Slash) | Gíria Natural Aceita | Comando Canônico | Ação SRE / Operação | Comando Shell macOS / Unix |
| :--- | :--- | :--- | :--- | :--- |
| `/espelha-site <URL> [PASTA]` | `"faça uma cópia do que vê"`, `"copia tudo"`, `"copia"`, `"clone"`, `"espelho"`, `"replicar"`, `"salvando na pasta X"` | `//mirror-frontend <URL> [PASTA]` | Espelhamento recursivo de assets de frontend salvando obrigatoriamente em `/Users/lucasvinicius/projetos/<PASTA>` e abrindo no navegador. | `mkdir -p "/Users/lucasvinicius/projetos/${2:-site_clone}" && cd "/Users/lucasvinicius/projetos/${2:-site_clone}" && wget --mirror --convert-links --adjust-extension --page-requisites --no-parent "$1" && open index.html` |

---

## 🤖 COMPORTAMENTO DO AGENTE AO RECEBER UM COMANDO DO MENU

1. **Reconhecimento Imediato:** Qualquer slash command (`/destrava-o-git`, `/auditoria-completa`), comando canônico (`//unlock-git`) ou frase natural mapeada ativa a rotina SRE correspondente sem hesitações.
2. **Execução de Séries Sequenciais:** Se a frase corresponder a uma macro-intenção (ex: `"faça uma auditoria completa"` ou `"destrava tudo"`), o agente executa **toda a esteira de passos da série relacionada sequencialmente**.
3. **Relatório Forense Estruturado:** Ao concluir qualquer série sequencial, o agente gera e apresenta o **Relatório Forense Hiper-Detalhado** contendo Linha do Tempo, Evidências Empíricas, Diagnóstico por Camada, Matriz de Riscos, Veredito Canônico e Chaining Inteligente.
4. **Resumo Operacional:** O agente reporta o que foi destravado/executado, quais PIDs foram afetados e o estado canônico do sistema (`VALIDADO`, `CONFORME` ou `DONE`).
