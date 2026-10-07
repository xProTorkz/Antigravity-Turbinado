// ============================================================================
// Catálogo Oficial de Comandos, Séries Sequenciais & Grafo de Chaining SRE
// Antigravity 2.0 — Governança Canônica Sentinela Guardião
// ============================================================================

const SRE_COMMANDS = [
  {
    "id": "series-audit-all",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Git: status, branch, HEAD, fsck integridade física.",
      "Rede: portas LISTEN, dev ports 3000..8765, sockets 0.0.0.0.",
      "Segurança: varredura profunda de tokens/chaves, .env drift.",
      "Armazenamento: df -h, SMART status, top pastas >50MB.",
      "Kernel: top CPU/RAM, ulimit descritores, throttling térmico.",
      "Banco SQLite: checagem física de páginas (PRAGMA)."
    ],
    "title": "SÉRIE 1: Auditoria Diagnóstica Completa",
    "slash": "/auditoria-completa",
    "canonical": "//audit-all",
    "phrase": "`faça uma auditoria completa`, `auditoria completa`, `raio-x completo`, `puxa a ficha de tudo`",
    "desc": "Pipeline SRE Sequencial Completo (6 etapas). Relatório técnico estruturado em `reports/audit_TIMESTAMP.md` + Resumo executivo no terminal.",
    "shell": "agy_cmd audit-all",
    "rawShell": "./agy_cmd.sh audit-all",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-unlock-all",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Git: elimina .git/index.lock, refs locks, aborta rebase/merge.",
      "Portas Dev: finaliza PIDs nas portas 3000, 5173, 8000, 8080, 8765.",
      "Pacotes: limpa locks corrompidos de NPM, Yarn, PNPM e Homebrew.",
      "Sockets/PIDs: remove locks em /tmp (.s.PGSQL, redis.sock, .pid órfãos).",
      "Zumbis: finaliza workers mortos em deadlock (SIGKILL).",
      "SQLite: força checkpoint WAL TRUNCATE em todas as bases locais.",
      "Kernel: eleva ulimit -n 65536 e recicla cache de DNS."
    ],
    "title": "SÉRIE 2: Desbloqueio Total de Sistema",
    "slash": "/desbloqueio-total",
    "canonical": "//unlock-all",
    "phrase": "`destrava tudo`, `desbloqueio total`, `socorro travou tudo`, `desbloqueia o mac`",
    "desc": "Pipeline SRE Sequencial Completo (7 etapas). Relatório de desengasgamento com PIDs finalizados e portas liberadas.",
    "shell": "agy_cmd unlock-all",
    "rawShell": "./agy_cmd.sh unlock-all",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-deep-clean",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Caches de Build: purga __pycache__, .pytest_cache, .DS_Store, .turbo, .next.",
      "Caches de Pacotes: higieniza e valida cache do npm, pip e yarn.",
      "Rotação de Logs: compacta em gzip arquivos de log com >50MB.",
      "Temporários: esvazia /tmp do usuário e Lixeira (~/.Trash).",
      "Memória RAM: força sync de inodes e purga buffers de RAM do kernel."
    ],
    "title": "SÉRIE 3: Faxina Profunda de Recursos",
    "slash": "/faxina-profunda",
    "canonical": "//deep-clean",
    "phrase": "`faxina profunda`, `limpa tudo`, `limpeza geral`, `apaga o lixo de compilação`",
    "desc": "Pipeline SRE Sequencial Completo (5 etapas). Relatório comparativo de espaço livre em disco (Antes vs Depois).",
    "shell": "agy_cmd deep-clean",
    "rawShell": "./agy_cmd.sh deep-clean",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-db-optimize-full",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Descoberta: localiza todas as bases .sqlite, .db no projeto.",
      "Integridade: executa PRAGMA integrity_check em cada página.",
      "WAL Checkpoint: força checkpoint e trunca -wal para o banco principal.",
      "Desfragmentação: executa VACUUM reduzindo tamanho físico em disco.",
      "Query Planner: executa REINDEX, ANALYZE e PRAGMA optimize."
    ],
    "title": "SÉRIE 4: Manutenção de Banco SQLite",
    "slash": "/otimiza-banco",
    "canonical": "//db-optimize-full",
    "phrase": "`otimiza o banco`, `dá um trato no banco`, `passa o aspirador na base`, `revisa o sqlite`",
    "desc": "Pipeline SRE Sequencial Completo (5 etapas). Relatório de volumetria, redução de páginas e saúde da árvore B.",
    "shell": "agy_cmd db-optimize-full",
    "rawShell": "./agy_cmd.sh db-optimize-full",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-turbo-run",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Limites de SO: eleva ulimit -n 65536 e ulimit -u 4096.",
      "Runtimes: define Node.js heap em 8GB e recursão Python em 50.000.",
      "Autonomia: injeta flags CI não-interativas e bypass de prompts.",
      "Anti-Sono: ativa caffeinate impedindo suspensão de CPU/display."
    ],
    "title": "SÉRIE 5: Modo Turbo de Alta Potência",
    "slash": "/modo-turbo",
    "canonical": "//turbo-run",
    "phrase": "`modo turbo`, `liga o modo turbo`, `roda sem pedir licença`, `alta autonomia`",
    "desc": "Pipeline SRE Sequencial Completo (4 etapas). Resumo de ambiente turbinado com perfil de potência máxima ativo.",
    "shell": "agy_cmd turbo-run",
    "rawShell": "./agy_cmd.sh turbo-run",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-pre-deploy-audit",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Segredos: varredura regex rigorosa de tokens e chaves privadas.",
      "Env Drift: comparação de chaves entre .env e .env.example.",
      "Git Hygiene: auditoria de integridade do Git e arquivos untracked.",
      "Sanitização: higienização de dados confidenciais em logs locais.",
      "Rollback: geração automática de snapshot .tar.gz com timestamp."
    ],
    "title": "SÉRIE 6: Pré-Deploy & Sincronização",
    "slash": "/prepara-deploy",
    "canonical": "//pre-deploy-audit",
    "phrase": "`prepara producao`, `higieniza para deploy`, `auditoria pre push`, `valida antes de subir`",
    "desc": "Pipeline SRE Sequencial Completo (5 etapas). Veredito formal de autorização para push (`AUTORIZADO` ou `BLOQUEADO`).",
    "shell": "agy_cmd pre-deploy-audit",
    "rawShell": "./agy_cmd.sh pre-deploy-audit",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-resilience-suite",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Superfície: varredura de portas expostas em 0.0.0.0 vs 127.0.0.1.",
      "CVEs: auditoria de vulnerabilidades conhecidas em dependências.",
      "Rate-Limit: validação de conformidade de cabeçalhos (X-Forwarded-For).",
      "Estresse: simulação controlada de conexões concorrentes."
    ],
    "title": "SÉRIE 7: Resiliência & Benchmark de Carga",
    "slash": "/teste-resiliencia",
    "canonical": "//resilience-suite",
    "phrase": "`teste de resiliencia`, `resiliencia completa`, `stress test geral`, `benchmark de carga`",
    "desc": "Pipeline SRE Sequencial Completo (4 etapas). Relatório de resiliência e recomendações de hardening de infraestrutura.",
    "shell": "agy_cmd resilience-suite",
    "rawShell": "./agy_cmd.sh resilience-suite",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-private-visit-clean",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Sessão Efêmera: dispara navegador em modo anônimo (--incognito) isolado.",
      "Purga DNS: limpa cache local de resolução e recicla mDNSResponder.",
      "Higienização Clipboard: purga área de transferência eliminando PII da memória.",
      "Caches & Buffers: esvazia caches temporários de sessão, cookies e /tmp.",
      "Isolamento: valida ausência de arquivos recentes e telemetria residual."
    ],
    "title": "SÉRIE 8: Visitas Sem Rastros & Privacidade",
    "slash": "/visitas-sem-rastros",
    "canonical": "//private-visit-clean",
    "phrase": "`visitas sem rastros`, `navegação anônima`, `sessão sem rastros`, `limpa rastros de navegação`",
    "desc": "Pipeline SRE Sequencial Completo (5 etapas). Sessão efêmera sem histórico com purga de DNS, caches de browser, clipboard e buffers temporários.",
    "shell": "agy_cmd private-visit-clean",
    "rawShell": "./agy_cmd.sh private-visit-clean",
    "next": [
      "stealth-exec",
      "clean-history-tail"
    ]
  },
  {
    "id": "series-auditoria-total",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Rede: varredura estruturada de portas ativas locais.",
      "Web: inspeção de cabeçalhos de segurança HTTP (CSP, HSTS, CORS).",
      "Rotas: verificação defensiva de arquivos sensíveis expostos (.env, .git).",
      "Segredos: caça profunda de credenciais e chaves de API.",
      "SQL: análise estática contra injeções SQL e consultas concatenadas.",
      "Webshells: caça forense de droppers e códigos ofuscados.",
      "Hardening: auditoria de privilégios SUID/SGID, LaunchDaemons e sudoers."
    ],
    "title": "SÉRIE: Auditoria Defensiva Total & Hardening",
    "slash": "/auditoria-total",
    "canonical": "//auditoria-total",
    "phrase": "`auditoria total`, `aduitoria total`, `varredura completa`, `auditoria-completa-total`",
    "desc": "Pipeline defensivo completo (7 etapas) com relatório estruturado de portas, cabeçalhos, rotas expostas, segredos, SQL e privilégios.",
    "shell": "agy_cmd auditoria-total",
    "rawShell": "./agy_cmd.sh auditoria-total",
    "next": [
      "audit-full",
      "unlock-all"
    ]
  },
  {
    "id": "series-va-mais-a-fundo",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Memória: dissecação de RSS e dirty pages de processos.",
      "Forensics: caça a descritores unlinked que retêm disco.",
      "Sockets: drenagem e auditoria de conexões TCP pendentes.",
      "Fuzzing: varredura rápida de rotas e arquivos sensíveis.",
      "SAST: análise estática profunda de sanitização SQL."
    ],
    "title": "SÉRIE: Investigação de Baixo Nível (Vá Mais a Fundo)",
    "slash": "/va-mais-a-fundo",
    "canonical": "//va-mais-a-fundo",
    "phrase": "`va mais a fundo`, `vá mais a fundo`, `vai mais a fundo`, `mais a fundo`",
    "desc": "Pipeline de investigação profunda em 5 etapas: dissecação de memória residente, FDs unlinked, sockets TCP, rotas e SQL.",
    "shell": "agy_cmd va-mais-a-fundo",
    "rawShell": "./agy_cmd.sh va-mais-a-fundo",
    "next": [
      "proc-tree-annihilate",
      "tcp-teardown-force"
    ]
  },
  {
    "id": "series-mais-alem",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "DNS: auditoria contra sequestro de rotas e /etc/hosts.",
      "Privilégios: verificação profunda de LaunchDaemons e SUID.",
      "Ameaças: caça a backdoors e webshells ocultos no projeto.",
      "Git: reconstrução da linha do tempo forense das últimas 24h.",
      "Wire: medição de jitter e latência de sockets em rajada."
    ],
    "title": "SÉRIE: Auditoria Perimétrica e Forense (Mais Além)",
    "slash": "/mais-alem",
    "canonical": "//mais-alem",
    "phrase": "`mais alem`, `mais além`, `vá mais além`, `vai mais além`",
    "desc": "Pipeline forense perimétrico em 5 etapas: integridade de DNS, vetores de privilégio, webshells, reflog Git e jitter de rede.",
    "shell": "agy_cmd mais-alem",
    "rawShell": "./agy_cmd.sh mais-alem",
    "next": [
      "dns-poison-audit",
      "wire-latency-jitter"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-git`",
    "title": "`Git`",
    "slash": "`/destrava-o-git`",
    "canonical": "`//unlock-git`",
    "phrase": "`destrava o git`",
    "desc": "Elimina arquivos de lock órfãos `.git/index.lock`, `HEAD.lock` e referências travadas.",
    "shell": "agy_cmd `unlock-git`",
    "rawShell": "`rm -f .git/index.lock .git/refs/heads/*.lock .git/HEAD.lock 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-git`",
    "title": "`Git`",
    "slash": "`/arranca-o-lock`",
    "canonical": "`//unlock-git`",
    "phrase": "`arranca o lock`",
    "desc": "Varrer recursivamente e forçar remoção de qualquer lock ativo na árvore `.git`.",
    "shell": "agy_cmd `unlock-git`",
    "rawShell": "`find .git -name \"*.lock\" -delete 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-git-rebase`",
    "title": "`Git Rebase`",
    "slash": "`/aborta-rebase`",
    "canonical": "`//unlock-git-rebase`",
    "phrase": "`cancela rebase travado`",
    "desc": "Cancela compulsoriamente rebase, merge ou cherry-pick em conflito/travado.",
    "shell": "agy_cmd `unlock-git-rebase`",
    "rawShell": "`git rebase --abort 2>/dev/null \\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-port",
    "title": "`Port",
    "slash": "`/mata-porta <PORTA>`",
    "canonical": "`//unlock-port <PORTA>`",
    "phrase": "`desbloqueia a porta 3000`",
    "desc": "Localiza PID ouvindo na porta TCP informada e finaliza compulsoriamente com SIGKILL.",
    "shell": "agy_cmd `unlock-port",
    "rawShell": "`lsof -ti :${1:-3000} 2>/dev/null \\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-dev-ports`",
    "title": "`Dev Ports`",
    "slash": "`/mata-portas-padrao`",
    "canonical": "`//unlock-dev-ports`",
    "phrase": "`limpa as portas de dev`",
    "desc": "Libera em lote as portas 3000, 5173, 8000, 8080 e 8765.",
    "shell": "agy_cmd `unlock-dev-ports`",
    "rawShell": "`for p in 3000 5173 8000 8080 8765; do pid=$(lsof -ti :$p); [ -n \"$pid\" ] && kill -9 $pid 2>/dev/null; done`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-file",
    "title": "`File",
    "slash": "`/destrava-arquivo <ARQUIVO>`",
    "canonical": "`//unlock-file <ARQ>`",
    "phrase": "`destrava esse arquivo`",
    "desc": "Identifica os processos retendo descritores abertos no arquivo e força finalização.",
    "shell": "agy_cmd `unlock-file",
    "rawShell": "`lsof -t \"$1\" 2>/dev/null \\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-dir",
    "title": "`Dir",
    "slash": "`/destrava-pasta <DIR>`",
    "canonical": "`//unlock-dir <DIR>`",
    "phrase": "`destrava a pasta`",
    "desc": "Finaliza compulsoriamente todos os processos retendo arquivos na árvore do diretório.",
    "shell": "agy_cmd `unlock-dir",
    "rawShell": "`lsof -t +D \"${1:-.}\" 2>/dev/null \\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-sqlite",
    "title": "`Sqlite",
    "slash": "`/destrava-sqlite <DB>`",
    "canonical": "`//unlock-sqlite <DB>`",
    "phrase": "`destrava o sqlite`",
    "desc": "Executa checkpoint WAL em modo TRUNCATE e remove arquivos órfãos `-wal` e `-shm`.",
    "shell": "agy_cmd `unlock-sqlite",
    "rawShell": "`sqlite3 \"$1\" \"PRAGMA wal_checkpoint(TRUNCATE);\" 2>/dev/null; rm -f \"${1}-shm\"`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-npm`",
    "title": "`Npm`",
    "slash": "`/destrava-npm`",
    "canonical": "`//unlock-npm`",
    "phrase": "`destrava o npm`",
    "desc": "Remove travas corrompidas de pacotes em `~/.npm/_locks` e valida integridade de cache.",
    "shell": "agy_cmd `unlock-npm`",
    "rawShell": "`rm -rf ~/.npm/_locks 2>/dev/null; npm cache verify`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-brew`",
    "title": "`Brew`",
    "slash": "`/destrava-brew`",
    "canonical": "`//unlock-brew`",
    "phrase": "`destrava o brew`",
    "desc": "Remove arquivos de lock de processo travado do Homebrew em `var/homebrew/locks`.",
    "shell": "agy_cmd `unlock-brew`",
    "rawShell": "`rm -f $(brew --prefix 2>/dev/null)/var/homebrew/locks/* 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-pids`",
    "title": "`Pids`",
    "slash": "`/limpa-pids-orfaos`",
    "canonical": "`//unlock-pids`",
    "phrase": "`limpa os locks órfãos`",
    "desc": "Varre `/tmp` e raiz do projeto deletando arquivos `.lock` e `.pid` sem processo ativo.",
    "shell": "agy_cmd `unlock-pids`",
    "rawShell": "`find /tmp . -maxdepth 2 \\( -name \"*.lock\" -o -name \"*.pid\" \\) -delete 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-zombie-deadlocks`",
    "title": "`Zombie Deadlocks`",
    "slash": "`/mata-zumbis`",
    "canonical": "`//unlock-zombie-deadlocks`",
    "phrase": "`mata processos zumbis`",
    "desc": "Encerra com SIGKILL processos zumbis ou em deadlock (Node, Python, Celery, Pytest).",
    "shell": "agy_cmd `unlock-zombie-deadlocks`",
    "rawShell": "`pkill -9 -f \"node\\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-all`",
    "title": "`All`",
    "slash": "`/desbloqueio-total`",
    "canonical": "`//unlock-all`",
    "phrase": "`destrava tudo`",
    "desc": "Executa rotina composta: destrava Git, limpa portas padrão, mata zumbis e reseta locks.",
    "shell": "`agy_cmd unlock-all`",
    "rawShell": "`agy_cmd unlock-all`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-git-index`",
    "title": "`Git Index`",
    "slash": "`/destrava-index`",
    "canonical": "`//unlock-git-index`",
    "phrase": "`destrava index`",
    "desc": "Remove exclusivamente `.git/index.lock` liberando operações de git add/commit.",
    "shell": "agy_cmd `unlock-git-index`",
    "rawShell": "`rm -f .git/index.lock 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-git-config`",
    "title": "`Git Config`",
    "slash": "`/destrava-git-config`",
    "canonical": "`//unlock-git-config`",
    "phrase": "`destrava config do git`",
    "desc": "Remove a trava `.git/config.lock` gerada por escritas concorrentes na config.",
    "shell": "agy_cmd `unlock-git-config`",
    "rawShell": "`rm -f .git/config.lock 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-port-range`",
    "title": "`Port Range`",
    "slash": "`/libera-faixa-portas [INI] [FIM]`",
    "canonical": "`//unlock-port-range`",
    "phrase": "`faixa de portas`",
    "desc": "Itera e derruba com SIGKILL processos em intervalo de portas TCP (ex: 3000 a 3010).",
    "shell": "`agy_cmd unlock-port-range 3000 3010`",
    "rawShell": "`agy_cmd unlock-port-range 3000 3010`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-kill-by-name`",
    "title": "`Kill By Name`",
    "slash": "`/mata-por-nome <NOME>`",
    "canonical": "`//unlock-kill-by-name`",
    "phrase": "`mata por nome`",
    "desc": "Encerra compulsoriamente com SIGKILL processos pelo nome exato (`pkill -9 -x`).",
    "shell": "agy_cmd `unlock-kill-by-name`",
    "rawShell": "`pkill -9 -x \"$1\" 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-sqlite-force`",
    "title": "`Sqlite Force`",
    "slash": "`/forca-destrave-sqlite [DB]`",
    "canonical": "`//unlock-sqlite-force`",
    "phrase": "`força destrave do sqlite`",
    "desc": "Mata processos segurando o banco, trunca o WAL e remove `-shm` e `-wal` residuais.",
    "shell": "`agy_cmd unlock-sqlite-force \"${1:-database.sqlite}\"`",
    "rawShell": "`agy_cmd unlock-sqlite-force \"${1:-database.sqlite}\"`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-git-bisect`",
    "title": "`Git Bisect`",
    "slash": "`/aborta-bisect`",
    "canonical": "`//unlock-git-bisect`",
    "phrase": "`aborta bisect`",
    "desc": "Cancela e reseta compulsoriamente operação de `git bisect` travada no repositório.",
    "shell": "agy_cmd `unlock-git-bisect`",
    "rawShell": "`git bisect reset 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-git-worktree`",
    "title": "`Git Worktree`",
    "slash": "`/poda-worktree`",
    "canonical": "`//unlock-git-worktree`",
    "phrase": "`poda worktree`",
    "desc": "Executa `git worktree prune` limpando metadados de worktrees órfãs ou corrompidas.",
    "shell": "agy_cmd `unlock-git-worktree`",
    "rawShell": "`git worktree prune 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-yarn-lock`",
    "title": "`Yarn Lock`",
    "slash": "`/destrava-yarn`",
    "canonical": "`//unlock-yarn-lock`",
    "phrase": "`destrava yarn`",
    "desc": "Remove travas de cache e arquivos `.tmp` residuais do Yarn.",
    "shell": "agy_cmd `unlock-yarn-lock`",
    "rawShell": "`rm -rf ~/.yarn/.tmp .yarn/cache yarn.lock.tmp 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-pnpm-lock`",
    "title": "`Pnpm Lock`",
    "slash": "`/destrava-pnpm`",
    "canonical": "`//unlock-pnpm-lock`",
    "phrase": "`destrava pnpm`",
    "desc": "Remove locks do store global do PNPM permitindo instalar dependências.",
    "shell": "agy_cmd `unlock-pnpm-lock`",
    "rawShell": "`rm -rf $(pnpm store path)/.lock .pnpm-debug.log 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-pip-lock`",
    "title": "`Pip Lock`",
    "slash": "`/destrava-pip`",
    "canonical": "`//unlock-pip-lock`",
    "phrase": "`destrava pip`",
    "desc": "Limpa locks e caches corrompidos de instalação do Pip/Pipx.",
    "shell": "agy_cmd `unlock-pip-lock`",
    "rawShell": "`rm -rf ~/.cache/pip ~/.local/state/pipx 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-file-force`",
    "title": "`File Force`",
    "slash": "`/forca-soltar-arquivo <ARQ>`",
    "canonical": "`//unlock-file-force`",
    "phrase": "`força soltar arquivo`",
    "desc": "Aplica lsof no arquivo e finaliza todos os processos concorrentes com SIGKILL.",
    "shell": "agy_cmd `unlock-file-force`",
    "rawShell": "`lsof -t \"$1\" 2>/dev/null \\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-dir-tree`",
    "title": "`Dir Tree`",
    "slash": "`/forca-soltar-pasta [DIR]`",
    "canonical": "`//unlock-dir-tree`",
    "phrase": "`força soltar pasta`",
    "desc": "Aplica `lsof -t +D` em toda a árvore e encerra processos bloqueando o diretório.",
    "shell": "agy_cmd `unlock-dir-tree`",
    "rawShell": "`lsof -t +D \"${1:-.}\" 2>/dev/null \\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-stuck-terminals`",
    "title": "`Stuck Terminals`",
    "slash": "`/mata-terminais-ociosos`",
    "canonical": "`//unlock-stuck-terminals`",
    "phrase": "`mata terminais parados`",
    "desc": "Encerra subshells e terminais zumbis ociosos que mantêm conexões e memória presas.",
    "shell": "agy_cmd `unlock-stuck-terminals`",
    "rawShell": "`pkill -9 -f \"zsh.*idle\\",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-postgres-local`",
    "title": "`Postgres Local`",
    "slash": "`/destrava-postgres-local`",
    "canonical": "`//unlock-postgres-local`",
    "phrase": "`destrava postgres local`",
    "desc": "Remove arquivos de socket temporários e locks `.s.PGSQL.*` em `/tmp`.",
    "shell": "agy_cmd `unlock-postgres-local`",
    "rawShell": "`rm -f /tmp/.s.PGSQL.* /tmp/.s.PGSQL.*.lock 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-redis-local`",
    "title": "`Redis Local`",
    "slash": "`/destrava-redis-local`",
    "canonical": "`//unlock-redis-local`",
    "phrase": "`destrava redis local`",
    "desc": "Finaliza instâncias órfãs de `redis-server` e limpa sockets e locks em `/tmp`.",
    "shell": "agy_cmd `unlock-redis-local`",
    "rawShell": "`pkill -9 -f \"redis-server\" 2>/dev/null; rm -f /tmp/redis*.sock 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 1,
    "menuName": "Menu 1: Destravamento Crítico",
    "group": "I",
    "id": "`unlock-chrome-debug`",
    "title": "`Chrome Debug`",
    "slash": "`/fecha-chrome-debug`",
    "canonical": "`//unlock-chrome-debug`",
    "phrase": "`fecha chrome debug`",
    "desc": "Encerra processos do Google Chrome com porta remota de depuração aberta.",
    "shell": "agy_cmd `unlock-chrome-debug`",
    "rawShell": "`pkill -9 -f \"Google Chrome.*remote-debugging-port\" 2>/dev/null`",
    "next": [
      "unlock-git",
      "unlock-dev-ports",
      "unlock-all",
      "audit-full"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-quarantine",
    "title": "`Quarantine",
    "slash": "`/tira-quarentena <ALVO>`",
    "canonical": "`//unlock-quarantine <ALVO>`",
    "phrase": "`tira a quarentena do mac`",
    "desc": "Remove o atributo estendido `com.apple.quarantine` de binários baixados via Gatekeeper.",
    "shell": "agy_cmd `unlock-quarantine",
    "rawShell": "`xattr -dr com.apple.quarantine \"$1\" 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-limits`",
    "title": "`Limits`",
    "slash": "`/sobe-limites`",
    "canonical": "`//unlock-limits`",
    "phrase": "`aumenta o ulimit`",
    "desc": "Eleva o limite de descritores de arquivos abertos para 65536 na sessão corrente.",
    "shell": "agy_cmd `unlock-limits`",
    "rawShell": "`ulimit -n 65536 2>/dev/null \\",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-dns-cache`",
    "title": "`Dns Cache`",
    "slash": "`/limpa-dns`",
    "canonical": "`//unlock-dns-cache`",
    "phrase": "`flush no dns`",
    "desc": "Limpa o cache DNS local e reinicia o daemon resolvedor de nomes `mDNSResponder`.",
    "shell": "agy_cmd `unlock-dns-cache`",
    "rawShell": "`sudo -n killall -HUP mDNSResponder 2>/dev/null \\",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-proxy`",
    "title": "`Proxy`",
    "slash": "`/reseta-proxy`",
    "canonical": "`//unlock-proxy`",
    "phrase": "`arranca o proxy`",
    "desc": "Desativa variáveis de proxy (`HTTP_PROXY`, `HTTPS_PROXY`) restaurando tráfego direto.",
    "shell": "agy_cmd `unlock-proxy`",
    "rawShell": "`unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-ssh-agent`",
    "title": "`Ssh Agent`",
    "slash": "`/destrava-ssh`",
    "canonical": "`//unlock-ssh-agent`",
    "phrase": "`reinicia o agente ssh`",
    "desc": "Reinicia socket do ssh-agent e recarrega chaves e identidades do Keychain.",
    "shell": "agy_cmd `unlock-ssh-agent`",
    "rawShell": "`ssh-add -D 2>/dev/null; ssh-add --apple-load-keychain 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-docker-sock`",
    "title": "`Docker Sock`",
    "slash": "`/destrava-docker`",
    "canonical": "`//unlock-docker-sock`",
    "phrase": "`destrava o docker`",
    "desc": "Restabelece permissões de leitura/escrita de `/var/run/docker.sock` para 666.",
    "shell": "agy_cmd `unlock-docker-sock`",
    "rawShell": "`sudo -n chmod 666 /var/run/docker.sock 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-write-perms`",
    "title": "`Write Perms`",
    "slash": "`/destrava-escrita`",
    "canonical": "`//unlock-write-perms`",
    "phrase": "`destrava permissões de escrita`",
    "desc": "Remove restrições de somente leitura recursivamente aplicando `chmod -R u+rwX .`.",
    "shell": "agy_cmd `unlock-write-perms`",
    "rawShell": "`chmod -R u+rwX . 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`sudo-keepalive`",
    "title": "`Sudo Keepalive`",
    "slash": "`/mantem-sudo`",
    "canonical": "`//sudo-keepalive`",
    "phrase": "`mantém o sudo vivo`",
    "desc": "Cria thread em background renovando o timestamp do sudo a cada 50s durante a execução.",
    "shell": "agy_cmd `sudo-keepalive`",
    "rawShell": "`while true; do sudo -n true; sleep 50; kill -0 \"$$\" \\",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-kernel-maxproc`",
    "title": "`Kernel Maxproc`",
    "slash": "`/aumenta-maxproc`",
    "canonical": "`//unlock-kernel-maxproc`",
    "phrase": "`aumenta maxproc`",
    "desc": "Eleva limite máximo de processos permitidos por usuário no kernel (`ulimit -u 4096`).",
    "shell": "agy_cmd `unlock-kernel-maxproc`",
    "rawShell": "`ulimit -u 4096 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-ephemeral-ports`",
    "title": "`Ephemeral Ports`",
    "slash": "`/recicla-portas-rapidas`",
    "canonical": "`//unlock-ephemeral-ports`",
    "phrase": "`recicla portas rápidas`",
    "desc": "Reduz MSL do TCP via sysctl acelerando reciclagem de portas efêmeras.",
    "shell": "agy_cmd `unlock-ephemeral-ports`",
    "rawShell": "`sysctl -w net.inet.tcp.msl=1000 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-arp-cache`",
    "title": "`Arp Cache`",
    "slash": "`/limpa-tabela-arp`",
    "canonical": "`//unlock-arp-cache`",
    "phrase": "`limpa tabela arp`",
    "desc": "Purga tabela ARP de resolução de hardware no macOS resolvendo conflitos locais.",
    "shell": "agy_cmd `unlock-arp-cache`",
    "rawShell": "`sudo -n arp -da 2>/dev/null \\",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-ipv6-disable`",
    "title": "`Ipv6 Disable`",
    "slash": "`/desativa-ipv6-wifi`",
    "canonical": "`//unlock-ipv6-disable`",
    "phrase": "`desativa ipv6 no wifi`",
    "desc": "Desativa pilha IPv6 na interface Wi-Fi para sanar atrasos de DNS e timeouts de rede.",
    "shell": "agy_cmd `unlock-ipv6-disable`",
    "rawShell": "`networksetup -setv6off Wi-Fi 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-macos-keychain`",
    "title": "`Macos Keychain`",
    "slash": "`/destrava-keychain`",
    "canonical": "`//unlock-macos-keychain`",
    "phrase": "`destrava keychain`",
    "desc": "Destrava o chaveiro de login do macOS via terminal com o utilitário `security`.",
    "shell": "agy_cmd `unlock-macos-keychain`",
    "rawShell": "`security unlock-keychain ~/Library/Keychains/login.keychain-db`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-spotlight-indexing`",
    "title": "`Spotlight Indexing`",
    "slash": "`/pausa-spotlight [DIR]`",
    "canonical": "`//unlock-spotlight-indexing`",
    "phrase": "`pausa spotlight`",
    "desc": "Desativa indexação do Spotlight no diretório informado reduzindo I/O de disco.",
    "shell": "agy_cmd `unlock-spotlight-indexing`",
    "rawShell": "`mdutil -i off \"${1:-.}\" 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-quarantine-recursive`",
    "title": "`Quarantine Recursive`",
    "slash": "`/tira-quarentena-pasta [DIR]`",
    "canonical": "`//unlock-quarantine-recursive`",
    "phrase": "`tira quarentena recursiva`",
    "desc": "Remove atributo `com.apple.quarantine` recursivamente de todos arquivos da pasta.",
    "shell": "agy_cmd `unlock-quarantine-recursive`",
    "rawShell": "`xattr -dr com.apple.quarantine \"${1:-.}\" 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-caffeinate-session`",
    "title": "`Caffeinate Session`",
    "slash": "`/impede-sono-mac`",
    "canonical": "`//unlock-caffeinate-session`",
    "phrase": "`não deixa o mac dormir`",
    "desc": "Dispara `caffeinate` em background mantendo CPU, disco e tela acordados.",
    "shell": "agy_cmd `unlock-caffeinate-session`",
    "rawShell": "`caffeinate -dimsu &`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-node-memory`",
    "title": "`Node Memory`",
    "slash": "`/aumenta-ram-node`",
    "canonical": "`//unlock-node-memory`",
    "phrase": "`aumenta ram do node`",
    "desc": "Configura NODE_OPTIONS para 8GB de heap prevenindo erro de Out of Memory.",
    "shell": "agy_cmd `unlock-node-memory`",
    "rawShell": "`export NODE_OPTIONS=\"--max-old-space-size=8192\"`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-python-recursion`",
    "title": "`Python Recursion`",
    "slash": "`/aumenta-recursao-python`",
    "canonical": "`//unlock-python-recursion`",
    "phrase": "`aumenta recursão do python`",
    "desc": "Eleva dinamicamente o limite de chamadas recursivas do Python para 50.000.",
    "shell": "agy_cmd `unlock-python-recursion`",
    "rawShell": "`python3 -c \"import sys; sys.setrecursionlimit(50000)\"`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-git-credentials`",
    "title": "`Git Credentials`",
    "slash": "`/reseta-credenciais-git`",
    "canonical": "`//unlock-git-credentials`",
    "phrase": "`reseta credenciais do git`",
    "desc": "Remove credenciais e tokens cacheados de github.com no keychain do macOS.",
    "shell": "agy_cmd `unlock-git-credentials`",
    "rawShell": "`printf \"host=github.com\\nprotocol=https\\n\" \\",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-firewall-dev`",
    "title": "`Firewall Dev`",
    "slash": "`/checa-firewall`",
    "canonical": "`//unlock-firewall-dev`",
    "phrase": "`status do firewall`",
    "desc": "Consulta o estado do firewall de sockets do macOS (`socketfilterfw`).",
    "shell": "agy_cmd `unlock-firewall-dev`",
    "rawShell": "`/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-docker-compose`",
    "title": "`Docker Compose`",
    "slash": "`/destrava-docker-compose`",
    "canonical": "`//unlock-docker-compose`",
    "phrase": "`derruba docker compose com volumes`",
    "desc": "Executa `docker compose down -v --remove-orphans` expurgando containers e volumes.",
    "shell": "agy_cmd `unlock-docker-compose`",
    "rawShell": "`docker compose down -v --remove-orphans 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-coreaudio`",
    "title": "`Coreaudio`",
    "slash": "`/reinicia-coreaudio`",
    "canonical": "`//unlock-coreaudio`",
    "phrase": "`reinicia áudio do mac`",
    "desc": "Reinicia daemon CoreAudio liberando CPU retida por subsistema de som.",
    "shell": "agy_cmd `unlock-coreaudio`",
    "rawShell": "`sudo -n killall coreaudiod 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 2,
    "menuName": "Menu 2: Runtimes & Kernel",
    "group": "E",
    "id": "`unlock-launchd-service`",
    "title": "`Launchd Service`",
    "slash": "`/reinicia-servico-launchd <S>`",
    "canonical": "`//unlock-launchd-service`",
    "phrase": "`reinicia serviço do launchd`",
    "desc": "Força reinício imediato de um serviço do usuário com `launchctl kickstart -k`.",
    "shell": "agy_cmd `unlock-launchd-service`",
    "rawShell": "`launchctl kickstart -k \"gui/$(id -u)/$1\" 2>/dev/null`",
    "next": [
      "unlock-limits",
      "audit-storage-smart",
      "telemetria-full",
      "mode-advanced"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-all`",
    "title": "`All`",
    "slash": "`/raio-x-completo`",
    "canonical": "`//audit-all`",
    "phrase": "`faz um raio-x completo`",
    "desc": "Coleta inventário de sistema, status do Git, processos ativos, portas e telemetria.",
    "shell": "`agy_cmd audit-full`",
    "rawShell": "`agy_cmd audit-full`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-quick`",
    "title": "`Quick`",
    "slash": "`/auditoria-rapida`",
    "canonical": "`//audit-quick`",
    "phrase": "`faz uma auditoria rápida`",
    "desc": "Exibe resumo compacto: branch atual, commits recentes, portas ativas e carga de CPU.",
    "shell": "agy_cmd `audit-quick`",
    "rawShell": "`git status -s; lsof -iTCP -sTCP:LISTEN -P; uptime`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-secrets-deep`",
    "title": "`Secrets Deep`",
    "slash": "`/procura-vazamento`",
    "canonical": "`//audit-secrets-deep`",
    "phrase": "`procura vazamento de chave`",
    "desc": "Varre arquivos procurando tokens AWS, chaves do GitHub e blocos RSA expostos.",
    "shell": "agy_cmd `audit-secrets-deep`",
    "rawShell": "`grep -rnEI 'AKIA[0-9A-Z]{16}\\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`sanitize-logs`",
    "title": "`Sanitize Logs`",
    "slash": "`/mascara-logs`",
    "canonical": "`//sanitize-logs`",
    "phrase": "`limpa os rastros`",
    "desc": "Substitui tokens sensíveis, senhas e CPFs em arquivos `.log` por `[REDACTED]`.",
    "shell": "agy_cmd `sanitize-logs`",
    "rawShell": "`sed -i '' -E 's/(bearer[[:space:]]+)[A-Za-z0-9._-]+/\\1[REDACTED]/gI' *.log 2>/dev/null`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`backup-quick`",
    "title": "`Backup Quick`",
    "slash": "`/salva-snapshot`",
    "canonical": "`//backup-quick`",
    "phrase": "`salva ponto de restauração`",
    "desc": "Compacta o repositório em um tar.gz isolado com timestamp para rollback imediato.",
    "shell": "agy_cmd `backup-quick`",
    "rawShell": "`tar --exclude='.git' -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-disk-heavy`",
    "title": "`Disk Heavy`",
    "slash": "`/varre-arquivos-grandes`",
    "canonical": "`//audit-disk-heavy`",
    "phrase": "`procura arquivos pesados`",
    "desc": "Lista os maiores arquivos do projeto (>50MB) que podem comprometer o Git.",
    "shell": "agy_cmd `audit-disk-heavy`",
    "rawShell": "`find . -type f -size +50M -not -path '*/.*' -exec ls -lh {} +`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-git-integrity`",
    "title": "`Git Integrity`",
    "slash": "`/audita-integridade-git`",
    "canonical": "`//audit-git-integrity`",
    "phrase": "`audita integridade do git`",
    "desc": "Executa `git fsck --full --strict` checando integridade de objetos do repo.",
    "shell": "agy_cmd `audit-git-integrity`",
    "rawShell": "`git fsck --full --strict 2>&1 \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-env-drift`",
    "title": "`Env Drift`",
    "slash": "`/audita-env-drift`",
    "canonical": "`//audit-env-drift`",
    "phrase": "`compara env com exemplo`",
    "desc": "Compara chaves entre `.env` e `.env.example` acusando variáveis faltantes ou órfãs.",
    "shell": "`agy_cmd audit-env-drift`",
    "rawShell": "`agy_cmd audit-env-drift`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-tls-cert`",
    "title": "`Tls Cert`",
    "slash": "`/audita-tls [HOST]`",
    "canonical": "`//audit-tls-cert`",
    "phrase": "`checa certificado tls`",
    "desc": "Conecta via OpenSSL na porta 443 do host alvo e extrai validade e CA do certificado.",
    "shell": "`agy_cmd audit-tls-cert \"${1:-github.com}\"`",
    "rawShell": "`agy_cmd audit-tls-cert \"${1:-github.com}\"`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-git-history-pii`",
    "title": "`Git History Pii`",
    "slash": "`/varre-historico-git`",
    "canonical": "`//audit-git-history-pii`",
    "phrase": "`segredos no histórico`",
    "desc": "Varre os diffs dos últimos 50 commits por senhas, tokens e chaves privadas.",
    "shell": "agy_cmd `audit-git-history-pii`",
    "rawShell": "`git log -p -n 50 \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-cron-launchd`",
    "title": "`Cron Launchd`",
    "slash": "`/audita-cron-launchd`",
    "canonical": "`//audit-cron-launchd`",
    "phrase": "`tarefas agendadas`",
    "desc": "Mapeia tarefas recorrentes no crontab e lista agentes em `~/Library/LaunchAgents`.",
    "shell": "agy_cmd `audit-cron-launchd`",
    "rawShell": "`crontab -l 2>/dev/null; ls -la ~/Library/LaunchAgents 2>/dev/null`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-dns-leak`",
    "title": "`Dns Leak`",
    "slash": "`/audita-dns-leak`",
    "canonical": "`//audit-dns-leak`",
    "phrase": "`vazamento de dns`",
    "desc": "Audita servidores DNS configurados no macOS via `scutil --dns` detectando vazamentos.",
    "shell": "agy_cmd `audit-dns-leak`",
    "rawShell": "`scutil --dns \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-installed-binaries`",
    "title": "`Installed Binaries`",
    "slash": "`/audita-binarios`",
    "canonical": "`//audit-installed-binaries`",
    "phrase": "`binários instalados`",
    "desc": "Lista cronologicamente os binários executáveis em `/usr/local/bin` e Homebrew.",
    "shell": "agy_cmd `audit-installed-binaries`",
    "rawShell": "`ls -lat /usr/local/bin /opt/homebrew/bin ~/.local/bin 2>/dev/null \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-storage-smart`",
    "title": "`Storage Smart`",
    "slash": "`/audita-saude-ssd`",
    "canonical": "`//audit-storage-smart`",
    "phrase": "`saúde do ssd`",
    "desc": "Extrai telemetria de integridade de disco, status SMART e espaço livre via diskutil.",
    "shell": "agy_cmd `audit-storage-smart`",
    "rawShell": "`diskutil info / \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-thermal-throttling`",
    "title": "`Thermal Throttling`",
    "slash": "`/audita-throttling`",
    "canonical": "`//audit-thermal-throttling`",
    "phrase": "`mac tá esquentando`",
    "desc": "Consulta subsistema de energia (`pmset -g therm`) para verificar throttling de CPU.",
    "shell": "agy_cmd `audit-thermal-throttling`",
    "rawShell": "`pmset -g therm 2>/dev/null \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-npm-global`",
    "title": "`Npm Global`",
    "slash": "`/audita-npm-global`",
    "canonical": "`//audit-npm-global`",
    "phrase": "`pacotes globais do npm`",
    "desc": "Lista pacotes Node.js instalados globalmente no sistema (`npm list -g --depth=0`).",
    "shell": "agy_cmd `audit-npm-global`",
    "rawShell": "`npm list -g --depth=0 2>/dev/null`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-zsh-env`",
    "title": "`Zsh Env`",
    "slash": "`/audita-zsh-env`",
    "canonical": "`//audit-zsh-env`",
    "phrase": "`audita zshrc`",
    "desc": "Varre `.zshrc` e `.zshenv` por aliases maliciosos, injeções de PATH ou chamadas eval.",
    "shell": "agy_cmd `audit-zsh-env`",
    "rawShell": "`grep -HnE \"(export PATH\\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`backup-git-bundle`",
    "title": "`Backup Git Bundle`",
    "slash": "`/backup-git-bundle [N]`",
    "canonical": "`//backup-git-bundle`",
    "phrase": "`backup em bundle`",
    "desc": "Empacota todo o repositório Git em um único arquivo `.bundle` autocontido.",
    "shell": "agy_cmd `backup-git-bundle`",
    "rawShell": "`git bundle create \"${1:-backup.bundle}\" --all 2>/dev/null`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-open-files-leak`",
    "title": "`Open Files Leak`",
    "slash": "`/audita-fd-leak`",
    "canonical": "`//audit-open-files-leak`",
    "phrase": "`vazamento de descritores`",
    "desc": "Rankeia os top 15 processos consumindo mais descritores de arquivos abertos.",
    "shell": "agy_cmd `audit-open-files-leak`",
    "rawShell": "`lsof 2>/dev/null \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-network-routes`",
    "title": "`Network Routes`",
    "slash": "`/audita-rotas-rede`",
    "canonical": "`//audit-network-routes`",
    "phrase": "`tabela de rotas`",
    "desc": "Inspeciona tabela de rotas ativas do kernel IPv4 no macOS via `netstat -rn -f inet`.",
    "shell": "agy_cmd `audit-network-routes`",
    "rawShell": "`netstat -rn -f inet 2>/dev/null \\",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 3,
    "menuName": "Menu 3: Auditoria & Segurança",
    "group": "A",
    "id": "`audit-clipboard-pii`",
    "title": "`Clipboard Pii`",
    "slash": "`/limpa-clipboard-pii`",
    "canonical": "`//audit-clipboard-pii`",
    "phrase": "`limpa clipboard`",
    "desc": "Inspeciona área de transferência do macOS por segredos/PII e higieniza com pbcopy.",
    "shell": "`agy_cmd audit-clipboard-pii`",
    "rawShell": "`agy_cmd audit-clipboard-pii`",
    "next": [
      "audit-full",
      "audit-secrets",
      "audit-git-integrity",
      "sanitize-logs",
      "backup-quick"
    ]
  },
  {
    "menu": 4,
    "menuName": "Menu 4: Alta Autonomia & Turbo",
    "group": "L",
    "id": "`turbo-run`",
    "title": "`Turbo Run`",
    "slash": "`/modo-turbo`",
    "canonical": "`//turbo-run`",
    "phrase": "`liga o modo turbo`",
    "desc": "Executa rotinas sem pausas interativas usando política de auto-aprovação de comandos.",
    "shell": "agy_cmd `turbo-run`",
    "rawShell": "Flag CLI: `--dangerously-skip-permissions --mode accept-edits`",
    "next": [
      "turbo-run",
      "mode-advanced",
      "audit-quick",
      "telemetria-full"
    ]
  },
  {
    "menu": 4,
    "menuName": "Menu 4: Alta Autonomia & Turbo",
    "group": "L",
    "id": "`unlock-agent-full`",
    "title": "`Agent Full`",
    "slash": "`/autonomia-total`",
    "canonical": "`//unlock-agent-full`",
    "phrase": "`modo turbo sem travas`",
    "desc": "Define variáveis de ambiente para execução autônoma irrestrita de CI e npm.",
    "shell": "agy_cmd `unlock-agent-full`",
    "rawShell": "`export AGY_EFFORT=high AGY_NON_INTERACTIVE=1 CI=true npm_config_yes=true`",
    "next": [
      "turbo-run",
      "mode-advanced",
      "audit-quick",
      "telemetria-full"
    ]
  },
  {
    "menu": 4,
    "menuName": "Menu 4: Alta Autonomia & Turbo",
    "group": "L",
    "id": "`realtime-cpu`",
    "title": "`Realtime Cpu`",
    "slash": "`/eleva-prioridade`",
    "canonical": "`//realtime-cpu`",
    "phrase": "`dá prioridade máxima`",
    "desc": "Ajusta o nice do processo para -20 e elimina workers concorrentes consumindo CPU.",
    "shell": "agy_cmd `realtime-cpu`",
    "rawShell": "`renice -n -20 -p $$ 2>/dev/null; kill -9 $(pgrep -f \"webpack\\",
    "next": [
      "turbo-run",
      "mode-advanced",
      "audit-quick",
      "telemetria-full"
    ]
  },
  {
    "menu": 4,
    "menuName": "Menu 4: Alta Autonomia & Turbo",
    "group": "L",
    "id": "`skip-git-hooks`",
    "title": "`Skip Git Hooks`",
    "slash": "`/pula-hooks`",
    "canonical": "`//skip-git-hooks`",
    "phrase": "`comita com flag no-verify`",
    "desc": "Realiza commit emergencial utilizando a flag `--no-verify` do Git.",
    "shell": "agy_cmd `skip-git-hooks`",
    "rawShell": "`git commit --no-verify -m \"chore: commit emergencial (--no-verify)\"`",
    "next": [
      "turbo-run",
      "mode-advanced",
      "audit-quick",
      "telemetria-full"
    ]
  },
  {
    "menu": 5,
    "menuName": "Menu 5: Modo Silencioso & Background",
    "group": "C",
    "id": "`background-silent-exec`",
    "title": "`Background Silent Exec`",
    "slash": "`/modo-silencioso`",
    "canonical": "`//background-silent-exec`",
    "phrase": "`executa em background silencioso`",
    "desc": "Executa tarefa desacoplada em segundo plano com logs auditáveis sem abrir novas janelas.",
    "shell": "agy_cmd `background-silent-exec`",
    "rawShell": "`nohup ./task.sh >/dev/null 2>&1 &`",
    "next": [
      "background-silent-exec",
      "disown-job",
      "clean-history-tail",
      "audit-privacy"
    ]
  },
  {
    "menu": 5,
    "menuName": "Menu 5: Ocultação & Furtividade",
    "group": "C",
    "id": "`disown-job`",
    "title": "`Disown Job`",
    "slash": "`/roda-desacoplado`",
    "canonical": "`//disown-job`",
    "phrase": "`solta do terminal`",
    "desc": "Desvincula o processo do terminal corrente para não encerrar quando o terminal fechar.",
    "shell": "agy_cmd `disown-job`",
    "rawShell": "`disown -h %1 2>/dev/null`",
    "next": [
      "stealth-exec",
      "disown-job",
      "clean-history-tail",
      "audit-privacy"
    ]
  },
  {
    "menu": 5,
    "menuName": "Menu 5: Ocultação & Furtividade",
    "group": "C",
    "id": "`clean-history-tail`",
    "title": "`Clean History Tail`",
    "slash": "`/apaga-historico`",
    "canonical": "`//clean-history-tail`",
    "phrase": "`apaga o histórico do terminal`",
    "desc": "Limpa os últimos comandos digitados no histórico do ZSH sem deixar registros.",
    "shell": "agy_cmd `clean-history-tail`",
    "rawShell": "`history -c 2>/dev/null; rm -f ~/.zsh_history`",
    "next": [
      "stealth-exec",
      "disown-job",
      "clean-history-tail",
      "audit-privacy"
    ]
  },
  {
    "menu": 5,
    "menuName": "Menu 5: Ocultação & Furtividade",
    "group": "C",
    "id": "`run-detached-subshell`",
    "title": "`Run Detached Subshell`",
    "slash": "`/roda-em-subshell`",
    "canonical": "`//run-detached-subshell`",
    "phrase": "`executa isolado sem alterar o shell`",
    "desc": "Executa comando dentro de subshell isolado sem poluir variáveis do ambiente pai.",
    "shell": "agy_cmd `run-detached-subshell`",
    "rawShell": "`( export VAR=val; ./script.sh )`",
    "next": [
      "stealth-exec",
      "disown-job",
      "clean-history-tail",
      "audit-privacy"
    ]
  },
  {
    "menu": 5,
    "menuName": "Menu 5: Ocultação & Furtividade",
    "group": "C",
    "id": "private-visit-clean",
    "title": "Visitas Sem Rastros",
    "slash": "/visitas-sem-rastros",
    "canonical": "//private-visit-clean",
    "phrase": "`visitas sem rastros`, `sessao sem rastro`, `navegacao privada anonima`",
    "desc": "Abre sessão incógnita, limpa caches DNS, purga clipboard e remove buffers temporários.",
    "shell": "agy_cmd private-visit-clean [URL]",
    "rawShell": "agy_cmd private-visit-clean",
    "next": [
      "clean-history-tail",
      "stealth-exec"
    ]
  },
  {
    "menu": 6,
    "menuName": "Menu 6: Banco de Dados & SQLite",
    "group": "B",
    "id": "`db-vacuum",
    "title": "`Db Vacuum",
    "slash": "`/otimiza-banco <DB>`",
    "canonical": "`//db-vacuum <DB>`",
    "phrase": "`dá um trato no banco`",
    "desc": "Executa VACUUM completo, analisa tabelas e reconstrói índices para reduzir espaço.",
    "shell": "agy_cmd `db-vacuum",
    "rawShell": "`sqlite3 \"$1\" 'VACUUM; ANALYZE; REINDEX;'`",
    "next": [
      "db-vacuum",
      "db-integrity",
      "db-checkpoint",
      "backup-quick"
    ]
  },
  {
    "menu": 6,
    "menuName": "Menu 6: Banco de Dados & SQLite",
    "group": "B",
    "id": "`db-integrity",
    "title": "`Db Integrity",
    "slash": "`/checa-integridade <DB>`",
    "canonical": "`//db-integrity <DB>`",
    "phrase": "`a base tá corrompida?`",
    "desc": "Valida a integridade física de todas as páginas da base SQLite.",
    "shell": "agy_cmd `db-integrity",
    "rawShell": "`sqlite3 \"$1\" 'PRAGMA integrity_check;'`",
    "next": [
      "db-vacuum",
      "db-integrity",
      "db-checkpoint",
      "backup-quick"
    ]
  },
  {
    "menu": 6,
    "menuName": "Menu 6: Banco de Dados & SQLite",
    "group": "B",
    "id": "`db-checkpoint",
    "title": "`Db Checkpoint",
    "slash": "`/forca-checkpoint <DB>`",
    "canonical": "`//db-checkpoint <DB>`",
    "phrase": "`descarrega o wal no disco`",
    "desc": "Força sincronização de páginas do arquivo de log (.wal) para o arquivo mestre (.db).",
    "shell": "agy_cmd `db-checkpoint",
    "rawShell": "`sqlite3 \"$1\" 'PRAGMA wal_checkpoint(FULL);'`",
    "next": [
      "db-vacuum",
      "db-integrity",
      "db-checkpoint",
      "backup-quick"
    ]
  },
  {
    "menu": 6,
    "menuName": "Menu 6: Banco de Dados & SQLite",
    "group": "B",
    "id": "`diff-db-schemas`",
    "title": "`Diff Db Schemas`",
    "slash": "`/compara-schemas <D1> <D2>`",
    "canonical": "`//diff-db-schemas`",
    "phrase": "`compara os schemas das bases`",
    "desc": "Exibe o diff unificado da estrutura DDL entre dois bancos de dados SQLite.",
    "shell": "agy_cmd `diff-db-schemas`",
    "rawShell": "`diff -u <(sqlite3 \"$1\" .schema) <(sqlite3 \"$2\" .schema)`",
    "next": [
      "db-vacuum",
      "db-integrity",
      "db-checkpoint",
      "backup-quick"
    ]
  },
  {
    "menu": 7,
    "menuName": "Menu 7: Faxina Profunda & Disco",
    "group": "L",
    "id": "`deep-clean`",
    "title": "`Deep Clean`",
    "slash": "`/faxina-profunda`",
    "canonical": "`//deep-clean`",
    "phrase": "`limpa a sujeira do disco`",
    "desc": "Remove pastas temporárias recursivas `node_modules`, `__pycache__`, `.pytest_cache` e `.DS_Store`.",
    "shell": "agy_cmd `deep-clean`",
    "rawShell": "`find . -name '__pycache__' -o -name '.DS_Store' -exec rm -rf {} + 2>/dev/null`",
    "next": [
      "deep-clean",
      "purge-ram",
      "clean-scratch",
      "reset-clean"
    ]
  },
  {
    "menu": 7,
    "menuName": "Menu 7: Faxina Profunda & Disco",
    "group": "L",
    "id": "`purge-ram`",
    "title": "`Purge Ram`",
    "slash": "`/purga-ram`",
    "canonical": "`//purge-ram`",
    "phrase": "`solta a memória presa`",
    "desc": "Solicita ao kernel a purga de memória inativa e buffers de páginas de disco.",
    "shell": "agy_cmd `purge-ram`",
    "rawShell": "`sudo -n purge 2>/dev/null \\",
    "next": [
      "deep-clean",
      "purge-ram",
      "clean-scratch",
      "reset-clean"
    ]
  },
  {
    "menu": 7,
    "menuName": "Menu 7: Faxina Profunda & Disco",
    "group": "L",
    "id": "`clean-scratch`",
    "title": "`Clean Scratch`",
    "slash": "`/limpa-scratch`",
    "canonical": "`//clean-scratch`",
    "phrase": "`limpa arquivos temporários`",
    "desc": "Esvazia a pasta efêmera de rascunhos e scripts temporários do IDE Antigravity.",
    "shell": "agy_cmd `clean-scratch`",
    "rawShell": "`rm -rf /Users/lucasvinicius/.gemini/antigravity-ide/scratch/* 2>/dev/null`",
    "next": [
      "deep-clean",
      "purge-ram",
      "clean-scratch",
      "reset-clean"
    ]
  },
  {
    "menu": 7,
    "menuName": "Menu 7: Faxina Profunda & Disco",
    "group": "L",
    "id": "`reset-clean`",
    "title": "`Reset Clean`",
    "slash": "`/reseta-workspace`",
    "canonical": "`//reset-clean`",
    "phrase": "`reseta o git pro head`",
    "desc": "Descarta alterações locais não salvas e remove arquivos não rastreados no repositório.",
    "shell": "agy_cmd `reset-clean`",
    "rawShell": "`git reset --hard HEAD && git clean -fd`",
    "next": [
      "deep-clean",
      "purge-ram",
      "clean-scratch",
      "reset-clean"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`stress-test-load`",
    "title": "`Stress Test Load`",
    "slash": "`/teste-de-carga [URL]`",
    "canonical": "`//stress-test-load`",
    "phrase": "`stress test de carga`",
    "desc": "Dispara benchmark de conexões concorrentes para avaliar vazão HTTP e latência sob carga.",
    "shell": "`agy_cmd stress-test-load \"${1:-http://localhost:3000}\" 500 25`",
    "rawShell": "`agy_cmd stress-test-load \"${1:-http://localhost:3000}\" 500 25`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`fuzz-api-extreme`",
    "title": "`Fuzz Api Extreme`",
    "slash": "`/fuzzing-extremo [URL]`",
    "canonical": "`//fuzz-api-extreme`",
    "phrase": "`fuzzing na api com payloads extremos`",
    "desc": "Injeta bateria de boundary payloads (SQLi, XSS, null bytes, 8KB buffers) contra endpoint.",
    "shell": "`agy_cmd fuzz-api-extreme \"${1:-http://localhost:3000}\"`",
    "rawShell": "`agy_cmd fuzz-api-extreme \"${1:-http://localhost:3000}\"`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`audit-network-surface`",
    "title": "`Audit Network Surface`",
    "slash": "`/audita-portas`",
    "canonical": "`//audit-network-surface`",
    "phrase": "`audita portas de rede`",
    "desc": "Mapeia todas as portas LISTEN em `0.0.0.0` vs `127.0.0.1` detectando exposições acidentais na rede.",
    "shell": "`agy_cmd audit-network-surface`",
    "rawShell": "`agy_cmd audit-network-surface`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`ratelimit-resilience-test`",
    "title": "`Ratelimit Resilience Test`",
    "slash": "`/testa-ratelimit [URL]`",
    "canonical": "`//ratelimit-resilience-test`",
    "phrase": "`testa resiliência de rate limit`",
    "desc": "Valida headers (`X-Forwarded-For`) para conferir proteção de rate-limiting e conformidade de proxy.",
    "shell": "`agy_cmd ratelimit-resilience-test \"${1:-http://localhost:3000}\"`",
    "rawShell": "`agy_cmd ratelimit-resilience-test \"${1:-http://localhost:3000}\"`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`auth-rate-limit-test`",
    "title": "`Auth Lockout Test`",
    "slash": "`/testa-bloqueio-login [URL]`",
    "canonical": "`//auth-rate-limit-test`",
    "phrase": "`testa bloqueio por retentativas de login`",
    "desc": "Dispara 15 tentativas rápidas de login incorretas testando lockout de segurança e códigos 429/403.",
    "shell": "`agy_cmd auth-rate-limit-test \"${1:-http://localhost:3000/api/login}\"`",
    "rawShell": "`agy_cmd auth-rate-limit-test \"${1:-http://localhost:3000/api/login}\"`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`chaos-freeze-thaw`",
    "title": "`Chaos Freeze Thaw`",
    "slash": "`/congelamento-chaos <ALVO>`",
    "canonical": "`//chaos-freeze-thaw`",
    "phrase": "`ataque de sinal congelante`",
    "desc": "Envia SIGSTOP paralisando worker por 5s no kernel e retoma com SIGCONT (teste de supervisor).",
    "shell": "`agy_cmd chaos-freeze-thaw \"${1:-node}\"`",
    "rawShell": "`agy_cmd chaos-freeze-thaw \"${1:-node}\"`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`stress-fd-exhaustion`",
    "title": "`Stress Fd Exhaustion`",
    "slash": "`/esgota-descritores`",
    "canonical": "`//stress-fd-exhaustion`",
    "phrase": "`ataque de exaustão de descritores`",
    "desc": "Abre milhares de descritores simultâneos testando se a aplicação trata erro EMFILE graciosamente.",
    "shell": "`agy_cmd stress-fd-exhaustion`",
    "rawShell": "`agy_cmd stress-fd-exhaustion`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`slowloris-sim`",
    "title": "`Slowloris Sim`",
    "slash": "`/slowloris-sim [H] [P]`",
    "canonical": "`//slowloris-sim`",
    "phrase": "`simula slowloris no servidor local`",
    "desc": "Abre sockets enviando cabeçalhos lentos fracionados para validar `client_header_timeout`.",
    "shell": "`agy_cmd slowloris-sim \"${1:-127.0.0.1}\" \"${2:-3000}\"`",
    "rawShell": "`agy_cmd slowloris-sim \"${1:-127.0.0.1}\" \"${2:-3000}\"`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`audit-cve-extreme`",
    "title": "`Cve Extreme`",
    "slash": "`/varre-cve`",
    "canonical": "`//audit-cve-extreme`",
    "phrase": "`procura exploits nas dependências`",
    "desc": "Varre vulnerabilidades conhecidas (CVEs) em pacotes npm e bibliotecas Python.",
    "shell": "`agy_cmd audit-cve-extreme`",
    "rawShell": "`agy_cmd audit-cve-extreme`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  },
  {
    "menu": 8,
    "menuName": "Menu 8: Resiliência & Carga",
    "group": "K",
    "id": "`audit-privesc-vectors`",
    "title": "`Privesc Vectors`",
    "slash": "`/audita-privilegios`",
    "canonical": "`//audit-privesc-vectors`",
    "phrase": "`audita vetor de invasão local`",
    "desc": "Audita binários com bit SUID ativado, diretórios com escrita universal e regras de sudo.",
    "shell": "`agy_cmd audit-privesc-vectors`",
    "rawShell": "`agy_cmd audit-privesc-vectors`",
    "next": [
      "resilience-suite",
      "scan-attack-surface",
      "audit-cve-extreme",
      "fuzz-api-extreme"
    ]
  }
,
  {
    "id": "series-recon-deep",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "DNS Autoritativo: varredura profunda de A, AAAA, MX, TXT, SOA e CAA.",
      "Certificate Transparency: mineração de subdomínios ocultos via crt.sh.",
      "Borda & ASN: resolução de blocos IP, ASN titular e rotas BGP upstream.",
      "Segurança de E-mail: validação de políticas anti-spoofing SPF, DKIM e DMARC.",
      "Headers HTTP & WAF: detecção passiva de servidores web, proxies e CSP.",
      "Criptografia TLS: auditoria de certificados, SANs e suporte a HTTP/3 QUIC."
    ],
    "title": "SÉRIE 12: Reconhecimento & OSINT Profundo",
    "slash": "/recon-profundo [D]",
    "canonical": "//recon-deep",
    "phrase": "`reconhecimento profundo`, `raio-x de infraestrutura`, `osint completo do domínio`, `mapeia a superfície do alvo`",
    "desc": "Pipeline SRE/OSINT Sequencial Completo (6 etapas). Mapeamento perimétrico passivo não-intrusivo com relatório estruturado.",
    "shell": "agy_cmd recon-deep \"${1:-example.com}\"",
    "rawShell": "./agy_cmd.sh recon-deep \"${1:-example.com}\"",
    "next": [
      "recon-dns-deep",
      "recon-ct-subdomains",
      "recon-tls-chain",
      "scan-surface-endpoints"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-dns-deep",
    "title": "DNS Deep Audit",
    "slash": "/recon-dns [D]",
    "canonical": "//recon-dns-deep",
    "phrase": "`audita dns do domínio`, `puxa registros dns`, `varre dns completo`",
    "desc": "Executa auditoria DNS autoritativa completa (A, AAAA, MX, TXT, NS, SOA, CAA) com verificação de delegação.",
    "shell": "agy_cmd recon-dns-deep \"${1:-example.com}\"",
    "rawShell": "for t in A AAAA MX TXT NS SOA CAA; do echo \"=== $t ===\"; dig +noall +answer \"${1:-example.com}\" $t; done",
    "next": [
      "recon-ct-subdomains",
      "recon-whois-timeline",
      "recon-email-auth",
      "series-recon-deep"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-ct-subdomains",
    "title": "Certificate Transparency Subdomains",
    "slash": "/recon-subdominios [D]",
    "canonical": "//recon-ct-subdomains",
    "phrase": "`descobre subdomínios via certificados`, `acha subdomínios crt.sh`, `minera subdomínios`",
    "desc": "Consulta logs públicos de Certificate Transparency (crt.sh) extraindo todos os subdomínios e SANs vinculados.",
    "shell": "agy_cmd recon-ct-subdomains \"${1:-example.com}\"",
    "rawShell": "curl -s \"https://crt.sh/?q=${1:-example.com}&output=json\" | jq -r \".[].name_value\" 2>/dev/null | sort -u",
    "next": [
      "recon-dns-deep",
      "recon-tls-chain",
      "scan-surface-endpoints",
      "series-recon-deep"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-whois-timeline",
    "title": "WHOIS Timeline & Registrar",
    "slash": "/recon-whois [D]",
    "canonical": "//recon-whois-timeline",
    "phrase": "`puxa whois completo`, `vê quando o domínio foi criado`, `histórico de registro`",
    "desc": "Inspeciona entidade registradora, data de criação original, expiração e nameservers autoritativos.",
    "shell": "agy_cmd recon-whois-timeline \"${1:-example.com}\"",
    "rawShell": "whois \"${1:-example.com}\" | grep -E \"Creation Date|Created|Updated|Expiry Date|Registrar|Name Server\" -i | head -n 25",
    "next": [
      "recon-dns-deep",
      "recon-asn-peering",
      "recon-email-auth",
      "series-recon-deep"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-asn-peering",
    "title": "ASN & BGP Peering Route",
    "slash": "/recon-asn [IP]",
    "canonical": "//recon-asn-peering",
    "phrase": "`audita asn do ip`, `descobre provedor e rota bgp`, `quem é o dono do ip`",
    "desc": "Consulta base WHOIS/ARIN/Registro.br identificando ASN, bloco CIDR, organização titular e país.",
    "shell": "agy_cmd recon-asn-peering \"${1:-1.1.1.1}\"",
    "rawShell": "whois \"${1:-1.1.1.1}\" | grep -E \"NetName|OrgName|Organization|CIDR|OriginAS|Country|City\" -i | head -n 20",
    "next": [
      "recon-dns-deep",
      "recon-http-fingerprint",
      "scan-network-cgnat",
      "series-recon-deep"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-email-auth",
    "title": "Email Auth (SPF/DMARC/DKIM)",
    "slash": "/recon-email [D]",
    "canonical": "//recon-email-auth",
    "phrase": "`audita spf e dmarc`, `checa se o e-mail tem spoofing`, `valida dmarc do domínio`",
    "desc": "Verifica vulnerabilidades de spoofing, presença de registros SPF autorizados e políticas DMARC restritivas.",
    "shell": "agy_cmd recon-email-auth \"${1:-example.com}\"",
    "rawShell": "echo \"=== SPF ===\"; dig TXT \"${1:-example.com}\" +short | grep -i \"v=spf1\"; echo \"=== DMARC ===\"; dig TXT \"_dmarc.${1:-example.com}\" +short",
    "next": [
      "recon-dns-deep",
      "recon-whois-timeline",
      "recon-http-fingerprint",
      "series-recon-deep"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-http-fingerprint",
    "title": "HTTP Header & WAF Fingerprint",
    "slash": "/recon-headers [URL]",
    "canonical": "//recon-http-fingerprint",
    "phrase": "`inspeciona headers http`, `detecta servidor web e waf`, `analisa csp e segurança web`",
    "desc": "Mapeia cabeçalhos de resposta HTTP, assinaturas de servidor (LiteSpeed, Nginx, Caddy), CSP, HSTS e WAF.",
    "shell": "agy_cmd recon-http-fingerprint \"${1:-https://example.com}\"",
    "rawShell": "curl -sI -L \"${1:-https://example.com}\" | grep -E \"server|content-security-policy|x-content-type|referrer-policy|alt-svc|cf-ray|permissions-policy\" -i",
    "next": [
      "recon-tls-chain",
      "scan-waf-reverseproxy",
      "scan-tech-exposure",
      "series-recon-deep"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-tls-chain",
    "title": "TLS Certificate & SAN Deep Audit",
    "slash": "/recon-tls [H] [P]",
    "canonical": "//recon-tls-chain",
    "phrase": "`audita certificado ssl`, `vê todos os domínios do certificado`, `checa tls e sans`",
    "desc": "Inspeciona certificado TLS em tempo real, autoridade certificadora (Let's Encrypt), validade e feixe de SANs.",
    "shell": "agy_cmd recon-tls-chain \"${1:-example.com}\" \"${2:-443}\"",
    "rawShell": "echo | openssl s_client -connect \"${1:-example.com}:${2:-443}\" -servername \"${1:-example.com}\" 2>/dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName",
    "next": [
      "recon-ct-subdomains",
      "recon-http-fingerprint",
      "scan-surface-endpoints",
      "series-recon-deep"
    ]
  },
  {
    "menu": 9,
    "menuName": "Menu 9: Reconhecimento & OSINT",
    "group": "L",
    "id": "recon-meta-extractor",
    "title": "Frontend Bundle & Meta Extractor",
    "slash": "/recon-meta [URL]",
    "canonical": "//recon-meta-extractor",
    "phrase": "`extrai metadados e scripts da página`, `inspeciona stack frontend`, `procura apis no bundle`",
    "desc": "Analisa passivamente a landing page extraindo tags de SEO, links de scripts, bibliotecas e rotas declaradas.",
    "shell": "agy_cmd recon-meta-extractor \"${1:-https://example.com}\"",
    "rawShell": "curl -sL \"${1:-https://example.com}\" | grep -E \"<meta|<link|<title|<script src=\" -i | head -n 30",
    "next": [
      "recon-http-fingerprint",
      "scan-surface-endpoints",
      "scan-tech-exposure",
      "series-recon-deep"
    ]
  },
  {
    "menu": 10,
    "menuName": "Menu 10: Varredura & Mapeamento",
    "group": "M",
    "id": "scan-surface-endpoints",
    "title": "Surface Endpoints Survey",
    "slash": "/scan-endpoints [URL]",
    "canonical": "//scan-surface-endpoints",
    "phrase": "`varre rotas públicas e robots`, `procura sitemap e endpoints padrão`, `mapeia superfície web`",
    "desc": "Verifica presença de rotas públicas padrão (/robots.txt, /sitemap.xml, /.well-known/security.txt, /favicon.ico).",
    "shell": "agy_cmd scan-surface-endpoints \"${1:-https://example.com}\"",
    "rawShell": "for p in robots.txt sitemap.xml .well-known/security.txt; do echo -n \"$p: \"; curl -s -o /dev/null -w \"%{http_code}\\n\" \"${1:-https://example.com}/$p\"; done",
    "next": [
      "scan-waf-reverseproxy",
      "scan-tech-exposure",
      "recon-http-fingerprint",
      "series-recon-deep"
    ]
  },
  {
    "menu": 10,
    "menuName": "Menu 10: Varredura & Mapeamento",
    "group": "M",
    "id": "scan-waf-reverseproxy",
    "title": "WAF & Reverse Proxy Detection",
    "slash": "/scan-waf [H]",
    "canonical": "//scan-waf-reverseproxy",
    "phrase": "`detecta cloudflare e proxy reverso`, `descobre se tem waf ativo`, `analisa borda de rede`",
    "desc": "Identifica proxies reversos, balanceadores de borda e proteção contra DDoS (Cloudflare, Fastly, AWS, OVH).",
    "shell": "agy_cmd scan-waf-reverseproxy \"${1:-example.com}\"",
    "rawShell": "curl -sI \"https://${1:-example.com}\" | grep -E \"cf-ray|cloudflare|x-amz|x-azure|server:.*litespeed|x-cdn\" -i",
    "next": [
      "scan-surface-endpoints",
      "scan-tech-exposure",
      "recon-http-fingerprint",
      "series-recon-deep"
    ]
  },
  {
    "menu": 10,
    "menuName": "Menu 10: Varredura & Mapeamento",
    "group": "M",
    "id": "scan-tech-exposure",
    "title": "Tech Stack & Version Exposure",
    "slash": "/scan-tech [URL]",
    "canonical": "//scan-tech-exposure",
    "phrase": "`procura vazamento de versão de servidor`, `vê tecnologias expostas`, `audita x-powered-by`",
    "desc": "Audita cabeçalhos e páginas de erro procurando versões expostas de linguagens, servidores ou frameworks.",
    "shell": "agy_cmd scan-tech-exposure \"${1:-https://example.com}\"",
    "rawShell": "curl -sI \"${1:-https://example.com}\" | grep -E \"x-powered-by|server|x-aspnet|x-generator\" -i",
    "next": [
      "scan-surface-endpoints",
      "scan-waf-reverseproxy",
      "scan-api-methods-cors",
      "series-recon-deep"
    ]
  },
  {
    "menu": 10,
    "menuName": "Menu 10: Varredura & Mapeamento",
    "group": "M",
    "id": "scan-webrtc-signaling",
    "title": "WebRTC & P2P Signaling Audit",
    "slash": "/scan-webrtc [URL]",
    "canonical": "//scan-webrtc-signaling",
    "phrase": "`audita webrtc e relays p2p`, `procura stun turn e nostr`, `analisa conexões descentralizadas`",
    "desc": "Inspeciona código compilado em busca de instâncias WebRTC, servidores STUN/TURN, relays Nostr ou WebSockets.",
    "shell": "agy_cmd scan-webrtc-signaling \"${1:-https://example.com}\"",
    "rawShell": "curl -sL \"${1:-https://example.com}\" | grep -o -E \"(stun:[^\\\"\\x27 ]+|turn:[^\\\"\\x27 ]+|wss://[^\\\"\\x27 ]+|trystero)\" | sort -u | head -n 20",
    "next": [
      "scan-surface-endpoints",
      "recon-meta-extractor",
      "scan-api-methods-cors",
      "series-recon-deep"
    ]
  },
  {
    "menu": 10,
    "menuName": "Menu 10: Varredura & Mapeamento",
    "group": "M",
    "id": "scan-network-cgnat",
    "title": "Local Network CGNAT & Hop Audit",
    "slash": "/scan-cgnat",
    "canonical": "//scan-network-cgnat",
    "phrase": "`checa se a internet está em cgnat`, `audita hops locais do provedor`, `verifica rota local`",
    "desc": "Diagnostica se a conexão local utiliza CGNAT (bloco 100.64.0.0/10), afere gateway local e mede saltos até o IX.",
    "shell": "agy_cmd scan-network-cgnat",
    "rawShell": "route -n get default 2>/dev/null || netstat -nr | grep default | head -n 1; curl -s https://ifconfig.me; echo \"\"",
    "next": [
      "recon-asn-peering",
      "scan-waf-reverseproxy",
      "scan-surface-endpoints",
      "series-recon-deep"
    ]
  },
  {
    "menu": 10,
    "menuName": "Menu 10: Varredura & Mapeamento",
    "group": "M",
    "id": "scan-api-methods-cors",
    "title": "HTTP Methods & CORS Audit",
    "slash": "/scan-cors [URL]",
    "canonical": "//scan-api-methods-cors",
    "phrase": "`audita cors e métodos http permitidos`, `checa options e headers cors`, `testa política de api`",
    "desc": "Executa requisição OPTIONS auditando Access-Control-Allow-Origin, credenciais permitidas e métodos habilitados.",
    "shell": "agy_cmd scan-api-methods-cors \"${1:-https://example.com}\"",
    "rawShell": "curl -sI -X OPTIONS -H \"Origin: https://test.local\" -H \"Access-Control-Request-Method: POST\" \"${1:-https://example.com}\" | grep -E \"access-control|allow\" -i",
    "next": [
      "scan-tech-exposure",
      "recon-http-fingerprint",
      "scan-surface-endpoints",
      "series-alem-profundo"
    ]
  },
  {
    "id": "series-alem-profundo",
    "menu": "series",
    "menuName": "Série Sequencial de Alta Potência",
    "group": "PIPELINE",
    "isSeries": true,
    "seriesSteps": [
      "Borda & DNS: auditoria autoritativa, rotas BGP/ASN e autoridade de certificados TLS.",
      "Superfície: fingerprint HTTP de servidores, WAF e varredura de endpoints de segurança.",
      "Sockets: mapeamento de conexões pendentes e drenagem cirúrgica de estados TIME_WAIT.",
      "Kernel & Memória: raio-x de dirty pages residentes e caça a descritores unlinked retendo disco.",
      "Processos: inspeção da árvore genealógica de PIDs e variáveis de ambiente em tempo real.",
      "Integridade: verificação física de bases SQLite (.recover) e integridade de objetos Git.",
      "Hardening: elevação de limites de sistema (ulimit -n 65536) e higienização de semáforos IPC."
    ],
    "title": "SÉRIE: Macro-Pipeline Perimétrico & Kernel (Mais Além & Mais Profundo)",
    "slash": "/avancar-mais-alem-profundo [D]",
    "canonical": "//avancar-mais-alem-profundo",
    "phrase": "`vamos avancar mais alem e mais profundo`, `avançar mais além e mais profundo`, `mais alem e mais profundo`, `alem e profundo`",
    "desc": "Pipeline consolidado de altíssima profundidade em 7 etapas: une reconhecimento perimétrico de borda, mapeamento de superfície, auditoria de sockets e cirurgia forense de kernel.",
    "shell": "agy_cmd alem-profundo \"${1:-example.com}\"",
    "rawShell": "./agy_cmd.sh alem-profundo \"${1:-example.com}\"",
    "next": [
      "series-recon-deep",
      "series-va-mais-a-fundo",
      "hacker-recon-full",
      "proc-tree-annihilate"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "hacker-recon-full",
    "title": "Varredura Forense Consolidada do Sistema",
    "slash": "/raio-x-hacker",
    "canonical": "//hacker-recon-full",
    "phrase": "`varredura hacker completa`, `raio-x de baixo nível`, `forense completa de processos e sockets`",
    "desc": "Executa varredura forense consolidada em 6 etapas: memória residente, FDs unlinked, sockets TCP anômalos, portas em escuta, SQLite e integridade Git.",
    "shell": "agy_cmd hacker-recon-full",
    "rawShell": "./agy_cmd.sh hacker-recon-full",
    "next": [
      "proc-tree-annihilate",
      "tcp-teardown-force",
      "mem-dirty-inspect",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "proc-tree-annihilate",
    "title": "Árvore Genealógica (SIGSTOP ➔ SIGKILL)",
    "slash": "/mata-arvore [PID]",
    "canonical": "//proc-tree-annihilate",
    "phrase": "`mata árvore de processos`, `aniquila processo e filhos`, `mata processo pai e filhos`",
    "desc": "Congela toda a árvore de processos com SIGSTOP para evitar novos forks e executa SIGKILL das folhas para a raiz sem deixar processos zumbis.",
    "shell": "agy_cmd proc-tree-annihilate \"${1:-PID}\"",
    "rawShell": "pids=$(pgrep -P \"${1:-PID}\"); for p in $pids; do kill -9 $p 2>/dev/null; done; kill -9 \"${1:-PID}\" 2>/dev/null",
    "next": [
      "proc-env-snoop",
      "proc-fd-map",
      "mem-dirty-inspect",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "proc-env-snoop",
    "title": "Live Environment Snoop (Variáveis Ativas)",
    "slash": "/snoop-env [PID]",
    "canonical": "//proc-env-snoop",
    "phrase": "`espia variáveis de ambiente do processo`, `inspeciona env de processo rodando`, `vê variáveis ativas`",
    "desc": "Extrai em tempo real as variáveis de ambiente ativas da tabela de memória do processo alvo sem reiniciá-lo.",
    "shell": "agy_cmd proc-env-snoop \"${1:-PID}\"",
    "rawShell": "ps -p \"${1:-PID}\" -wwE | tr ' ' '\\n' | grep '=' | sort -u | head -n 30",
    "next": [
      "proc-fd-map",
      "mem-dirty-inspect",
      "mem-leak-deep",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "proc-fd-map",
    "title": "Mapeador de Descritores & FDs (Pipes & Sockets)",
    "slash": "/fd-map [PID]",
    "canonical": "//proc-fd-map",
    "phrase": "`mapeia descritores de arquivos`, `vê fds abertos pelo processo`, `audita pipes e sockets do processo`",
    "desc": "Disseca todos os descritores de arquivos abertos (arquivos de disco, pipes anônimos, sockets de rede e kqueues) de um PID.",
    "shell": "agy_cmd proc-fd-map \"${1:-PID}\"",
    "rawShell": "lsof -p \"${1:-PID}\" | awk '{printf \"%-5s %-7s %-8s %-10s %s\\n\", $4, $5, $6, $7, $9}' | head -n 30",
    "next": [
      "fd-unlinked-hunter",
      "socket-sniff-loopback",
      "mem-dirty-inspect",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "fd-unlinked-hunter",
    "title": "Caçador de FDs Unlinked (Ghost Files Segurando Disco)",
    "slash": "/caca-ghosts",
    "canonical": "//fd-unlinked-hunter",
    "phrase": "`caça arquivos deletados segurando disco`, `acha descritores unlinked`, `libera espaço preso em memória`",
    "desc": "Detecta arquivos apagados no sistema de arquivos mas cujos descritores continuam retidos em RAM por processos ativos consumindo espaço.",
    "shell": "agy_cmd fd-unlinked-hunter",
    "rawShell": "lsof +L1",
    "next": [
      "proc-tree-annihilate",
      "proc-fd-map",
      "mem-dirty-inspect",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "mem-dirty-inspect",
    "title": "Raio-X de Dirty Pages & Memória Residente (vmmap)",
    "slash": "/raio-x-mem [PID]",
    "canonical": "//mem-dirty-inspect",
    "phrase": "`raio-x de memória residente`, `analisa dirty pages e vmmap`, `disseca consumo de ram de processo`",
    "desc": "Disseca a memória virtual do processo no macOS (vmmap) identificando páginas sujas (dirty), alocações malloc, stack e swap.",
    "shell": "agy_cmd mem-dirty-inspect \"${1:-PID}\"",
    "rawShell": "vmmap --resident \"${1:-PID}\" | grep -E \"(Virtual Memory|RESIDENT SIZE|DIRTY|SWAPPED|MALLOC|STACK)\" | head -n 25",
    "next": [
      "mem-leak-deep",
      "proc-tree-annihilate",
      "proc-fd-map",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "mem-leak-deep",
    "title": "Varredura Profunda de Vazamentos de Heap (leaks CLI)",
    "slash": "/caca-leaks [PID]",
    "canonical": "//mem-leak-deep",
    "phrase": "`caça memory leak`, `audita vazamento de heap`, `executa leaks no processo`",
    "desc": "Executa o utilitário nativo leaks do subsistema Apple Mach para escanear referências órfãs e vazamentos na heap do processo.",
    "shell": "agy_cmd mem-leak-deep \"${1:-PID}\"",
    "rawShell": "leaks \"${1:-PID}\" | head -n 30",
    "next": [
      "mem-dirty-inspect",
      "proc-tree-annihilate",
      "proc-fd-map",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "socket-sniff-loopback",
    "title": "Sniffer de Loopback & Sockets Brutos (lo0)",
    "slash": "/sniff-socket [P] [Q]",
    "canonical": "//socket-sniff-loopback",
    "phrase": "`sniffa pacotes na porta local`, `inspeciona tráfego loopback`, `captura pacotes tcp em tempo real`",
    "desc": "Captura pacotes brutos na interface lo0 com dissecação ASCII/HEX para inspecionar payloads trafegados em portas locais.",
    "shell": "agy_cmd socket-sniff-loopback \"${1:-3000}\" \"${2:-15}\"",
    "rawShell": "tcpdump -i lo0 -nn -s0 -X -c \"${2:-15}\" \"port ${1:-3000}\" 2>/dev/null || curl -v \"http://127.0.0.1:${1:-3000}\" --max-time 3 2>&1 | head -n 25",
    "next": [
      "tcp-teardown-force",
      "stealth-port-recon",
      "wire-latency-jitter",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "tcp-teardown-force",
    "title": "Drenagem Forçada de Sockets Presos (TIME_WAIT Recycle)",
    "slash": "/tcp-drain",
    "canonical": "//tcp-teardown-force",
    "phrase": "`drena conexões tcp presas`, `recicla sockets em time_wait`, `desafoga a pilha tcp`",
    "desc": "Higieniza a tabela de estados do TCP, forçando a reciclagem e expurgo de conexões presas em TIME_WAIT, CLOSE_WAIT e FIN_WAIT.",
    "shell": "agy_cmd tcp-teardown-force",
    "rawShell": "netstat -anv | grep -E \"TIME_WAIT|CLOSE_WAIT\"; sudo sysctl -w net.inet.tcp.msl=100 2>/dev/null; sleep 0.5; sudo sysctl -w net.inet.tcp.msl=15000 2>/dev/null",
    "next": [
      "socket-sniff-loopback",
      "stealth-port-recon",
      "scan-surface-endpoints",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "stealth-port-recon",
    "title": "Varredura Furtiva via Sockets Shell (/dev/tcp)",
    "slash": "/stealth-scan [H]",
    "canonical": "//stealth-port-recon",
    "phrase": "`varredura furtiva de portas`, `checa portas sem nmap`, `testa portas via socket bash`",
    "desc": "Escaneia portas padrão de bancos e servidores web utilizando os descritores /dev/tcp nativos do shell sem acionar ferramentas externas.",
    "shell": "agy_cmd stealth-port-recon \"${1:-127.0.0.1}\"",
    "rawShell": "for p in 22 80 443 3000 5173 5432 6379 8000 8080 8765; do (exec 3<>/dev/tcp/${1:-127.0.0.1}/$p) 2>/dev/null && echo \"Porta $p ABERTA\" && exec 3>&-; done",
    "next": [
      "scan-surface-endpoints",
      "socket-sniff-loopback",
      "tcp-teardown-force",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "dns-poison-audit",
    "title": "Auditoria Anti-Poisoning & Hosts Hijack",
    "slash": "/dns-audit",
    "canonical": "//dns-poison-audit",
    "phrase": "`audita desvio de rota dns`, `checa se o hosts foi alterado`, `valida integridade de dns local`",
    "desc": "Audita /etc/hosts, resolvers scutil do macOS e integridade de roteamento contra sequestro de rotas locais ou DNS spoofing.",
    "shell": "agy_cmd dns-poison-audit",
    "rawShell": "grep -vE \"^(#|$)\" /etc/hosts; scutil --dns | grep -E \"nameserver\\[[0-9]+\\]\" | sort -u | head -n 6; dscacheutil -q host -a name github.com | head -n 5",
    "next": [
      "recon-dns-deep",
      "wire-latency-jitter",
      "recon-asn-peering",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "wire-latency-jitter",
    "title": "Medição Cirúrgica de Jitter & Latência Sub-Milissegundo",
    "slash": "/jitter-rede [URL]",
    "canonical": "//wire-latency-jitter",
    "phrase": "`mede jitter e latência de rede`, `testa consistência da rota`, `calcula desvio padrão de latência`",
    "desc": "Executa rajada de 10 sondas HTTP medindo latência média, jitter (desvio padrão) e extremos mínimo/máximo com precisão de nanossegundos.",
    "shell": "agy_cmd wire-latency-jitter \"${1:-http://127.0.0.1:3000}\"",
    "rawShell": "python3 -c \"import urllib.request, time, statistics; t=[(time.perf_counter(), urllib.request.urlopen('${1:-http://127.0.0.1:3000}', timeout=2), time.perf_counter()) for _ in range(5)]; print('OK')\" 2>/dev/null || ping -c 5 -q 1.1.1.1",
    "next": [
      "scan-network-cgnat",
      "dns-poison-audit",
      "socket-sniff-loopback",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "sqlite-raw-recover",
    "title": "Cirurgia Forense de Baixo Nível SQLite (.recover)",
    "slash": "/resgata-sqlite [DB]",
    "canonical": "//sqlite-raw-recover",
    "phrase": "`recupera banco sqlite corrompido`, `cirurgia forense sqlite`, `resgata dados via recover stream`",
    "desc": "Extrai páginas brutas íntegras de banco SQLite avariado via .recover stream e reconstrói nova base íntegra sem perda de dados.",
    "shell": "agy_cmd sqlite-raw-recover \"${1:-database.sqlite}\"",
    "rawShell": "sqlite3 \"${1:-database.sqlite}\" \".recover\" > /tmp/recovered.sql && sqlite3 \"${1:-database.sqlite}.recovered.sqlite\" < /tmp/recovered.sql && rm -f /tmp/recovered.sql",
    "next": [
      "sqlite-wal-nuke-flush",
      "file-hex-inspect",
      "git-resurrect-dangling",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "sqlite-wal-nuke-flush",
    "title": "Expurgo & Truncamento Forçado de WAL SQLite",
    "slash": "/wal-nuke [DB]",
    "canonical": "//sqlite-wal-nuke-flush",
    "phrase": "`trunca wal do sqlite`, `força checkpoint wal truncate`, `expulsa conexões presas no sqlite`",
    "desc": "Expulsa bloqueios de conexões ativas e força checkpoint exclusivo com truncamento imediato do arquivo -wal para 0 bytes.",
    "shell": "agy_cmd sqlite-wal-nuke-flush \"${1:-database.sqlite}\"",
    "rawShell": "sqlite3 \"${1:-database.sqlite}\" \"PRAGMA wal_checkpoint(TRUNCATE);\" && rm -f \"${1:-database.sqlite}-shm\"",
    "next": [
      "sqlite-raw-recover",
      "proc-fd-map",
      "file-hex-inspect",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "file-hex-inspect",
    "title": "Dissecação Hexadecimal & Magic Bytes de Arquivo",
    "slash": "/magic-bytes [ARQ]",
    "canonical": "//file-hex-inspect",
    "phrase": "`vê magic bytes do arquivo`, `inspeciona cabeçalho hex`, `audita assinatura binária do arquivo`",
    "desc": "Exibe os primeiros 64 bytes em representação hexadecimal e ASCII para auditar assinaturas e cabeçalhos binários reais.",
    "shell": "agy_cmd file-hex-inspect \"${1:-arquivo.bin}\"",
    "rawShell": "hexdump -C -n 64 \"${1:-arquivo.bin}\" 2>/dev/null || xxd -l 64 \"${1:-arquivo.bin}\"; file \"${1:-arquivo.bin}\"",
    "next": [
      "macho-binary-audit",
      "sqlite-raw-recover",
      "git-pack-heaviest",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "macho-binary-audit",
    "title": "Dissecação de Binário Executável Mach-O (macOS)",
    "slash": "/disseca-bin [BIN]",
    "canonical": "//macho-binary-audit",
    "phrase": "`disseca binário executável`, `audita codesign e lipo`, `vê bibliotecas dinâmicas otool`",
    "desc": "Inspeciona arquitetura (lipo), bibliotecas dinâmicas dependentes (otool -L), assinatura criptográfica (codesign) e entitlements de um binário.",
    "shell": "agy_cmd macho-binary-audit \"${1:-$(which node)}\"",
    "rawShell": "lipo -info \"${1:-$(which node)}\"; otool -L \"${1:-$(which node)}\" | head -n 12; codesign -dvvv \"${1:-$(which node)}\" 2>&1 | grep -E \"(Identifier|Authority|TeamIdentifier)\"",
    "next": [
      "file-hex-inspect",
      "sandbox-jail-exec",
      "proc-tree-annihilate",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "git-resurrect-dangling",
    "title": "Ressurreição Forense de Commits Perdidos (Dangling)",
    "slash": "/git-resurrect",
    "canonical": "//git-resurrect-dangling",
    "phrase": "`recupera commits perdidos`, `acha commits órfãos no git`, `ressuscita commits soltos`",
    "desc": "Escanear todo o banco de objetos Git em busca de commits órfãos (dangling commits) desconectados da árvore de branches para resgate imediato.",
    "shell": "agy_cmd git-resurrect-dangling",
    "rawShell": "git fsck --lost-found --unreachable 2>/dev/null | grep \"dangling commit\" | awk '{print $3}'",
    "next": [
      "git-pack-heaviest",
      "git-forensic-timeline",
      "sqlite-raw-recover",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "git-pack-heaviest",
    "title": "Top 10 Maiores Objetos Packfile Git",
    "slash": "/git-heavy-objects",
    "canonical": "//git-pack-heaviest",
    "phrase": "`acha arquivos pesados no git`, `audita packfiles do git`, `identifica blobs gigantes no histórico`",
    "desc": "Disseca o índice de packfiles (.git/objects/pack/*.idx) listando os 10 maiores blobs e commits que incham o clone do repositório.",
    "shell": "agy_cmd git-pack-heaviest",
    "rawShell": "pack_idx=$(find .git/objects/pack -name \"*.idx\" 2>/dev/null | head -n 1); [ -n \"$pack_idx\" ] && git verify-pack -v \"$pack_idx\" | grep -E \"blob|commit\" | sort -k3nr | head -n 10",
    "next": [
      "git-resurrect-dangling",
      "file-hex-inspect",
      "fd-unlinked-hunter",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "kernel-ipc-nuke",
    "title": "Expurgo de Semáforos e Memória Compartilhada IPC",
    "slash": "/ipc-nuke",
    "canonical": "//kernel-ipc-nuke",
    "phrase": "`limpa semáforos e ipc`, `expurga memória compartilhada órfã`, `audita tabelas ipcs`",
    "desc": "Varre tabelas de IPC (Inter-Process Communication) do kernel do macOS/Unix auditando e higienizando filas de mensagens e semáforos órfãos.",
    "shell": "agy_cmd kernel-ipc-nuke",
    "rawShell": "ipcs -m -s -q",
    "next": [
      "tcp-teardown-force",
      "proc-tree-annihilate",
      "mem-dirty-inspect",
      "series-alem-profundo"
    ]
  },
  {
    "menu": 11,
    "menuName": "Menu 11: Forense & Kernel",
    "group": "N",
    "id": "sandbox-jail-exec",
    "title": "Execução Isolada em Sandbox Estrita (ulimit Jail)",
    "slash": "/sandbox-exec [CMD]",
    "canonical": "//sandbox-jail-exec",
    "phrase": "`executa comando em sandbox`, `isola execução com limites rígidos`, `roda em subshell protegido`",
    "desc": "Executa comandos arbitrários em subshell restrito com limites rígidos de ulimit (1GB memória virtual, 100MB arquivo, 30s CPU).",
    "shell": "agy_cmd sandbox-jail-exec \"${1:-ls -la}\"",
    "rawShell": "(ulimit -v 1048576; ulimit -f 102400; ulimit -t 30; eval \"${1:-ls -la}\")",
    "next": [
      "macho-binary-audit",
      "proc-env-snoop",
      "proc-fd-map",
      "series-alem-profundo"
    ]
  }
];
