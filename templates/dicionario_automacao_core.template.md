# 🗺️ Dicionário Canônico de Automação & Comandos de Alta Potência
**Template Oficial do Antigravity Turbinado**  
**Destino no Cliente:** `<projects_dir>/estruturas/dicionario_automacao_core.md`  
**Escopo:** Ecossistema Antigravity, CLI `agy`, IDE e Terminal do Desenvolvedor  

Este documento reúne o catálogo de comandos diretos, frases curtas em linguagem natural e `//comandos` contextualizados para controle de infraestrutura, alta performance e automação determinística, formulados sob a terminologia canônica de **Engenharia de Sistemas, SRE e DevOps**.

---

## 📊 Matriz de Focos e Gatilhos Operacionais

### 🎯 Foco 1: Gerenciamento Crítico de Processos & Recursos de CPU/RAM
*Elimina gargalos, encerra serviços concorrentes ou travados e garante prioridade de hardware.*

* **Gatilho Natural:** `"foco total"` | `"foco no projeto ativo"`  
  * **`//comando` Direto:** `//foco-ativo`  
  * **Ação Real:** Eleva a prioridade de CPU para a sessão corrente e encerra processos concorrentes.  
  * **Comando Shell:** `renice -n -20 -p $$; kill -9 $(pgrep -f "websocket_server|node_orphan") 2>/dev/null`

* **Gatilho Natural:** `"travar processos"` | `"encerrar travados"`  
  * **`//comando` Direto:** `//kill-zombies`  
  * **Ação Real:** Varre e encerra imediatamente processos órfãos ou suspensos na memória RAM.  
  * **Comando Shell:** `pkill -9 -f "antigravity_worker" 2>/dev/null; killall -9 Python 2>/dev/null || true`

* **Gatilho Natural:** `"prioridade máxima"` | `"tempo real"`  
  * **`//comando` Direto:** `//realtime-cpu`  
  * **Ação Real:** Aloca prioridade de agendamento do kernel para o processo ativo.  
  * **Comando Shell:** `sudo -n renice -n -20 -p $$ 2>/dev/null || renice -n -10 -p $$`

* **Gatilho Natural:** `"liberar memória"` | `"sincronizar ram"`  
  * **`//comando` Direto:** `//purge-ram`  
  * **Ação Real:** Sincroniza dados com o disco e força a liberação de buffers inativos do SO.  
  * **Comando Shell:** `sync; sudo -n purge 2>/dev/null || echo "Memória sincronizada"`

---

### 🧹 Foco 2: Limpeza Profunda de Buffers, Caches & File System (I/O)
*Gerencia acúmulo de dados volumosos sem interrupções visuais e previne sobrecarga de escrita em disco.*

* **Gatilho Natural:** `"ambiente limpo"` | `"purgar buffers"`  
  * **`//comando` Direto:** `//purgar-buffers`  
  * **Ação Real:** Trunca arquivos de log para 0 bytes sem deletar ponteiros de escrita.  
  * **Comando Shell:** `find . -name "*.log" -exec truncate -s 0 {} + 2>/dev/null`

* **Gatilho Natural:** `"limpar temporários"` | `"esvaziar scratch"`  
  * **`//comando` Direto:** `//clean-scratch`  
  * **Ação Real:** Remove caches e arquivos temporários da IDE e compiladores locais.  
  * **Comando Shell:** `rm -rf ~/.gemini/antigravity-ide/scratch/* /tmp/antigravity_* 2>/dev/null`

* **Gatilho Natural:** `"rotação de dados"` | `"reciclar logs"`  
  * **`//comando` Direto:** `//rotacionar-logs`  
  * **Ação Real:** Compacta em gzip arquivos de log que excederem 50MB.  
  * **Comando Shell:** `find . -name "*.log" -size +50M -exec gzip -f {} + 2>/dev/null`

* **Gatilho Natural:** `"reset de build"` | `"limpar artefatos"`  
  * **`//comando` Direto:** `//purge-build`  
  * **Ação Real:** Remove pastas pesadas de compilação (`.turbo`, `.next`, `dist`).  
  * **Comando Shell:** `find . -maxdepth 3 -type d \( -name ".turbo" -o -name ".next" -o -name "dist" \) -exec rm -rf {} + 2>/dev/null`

---

### 🔄 Foco 3: Persistência, Sincronização & Resiliência Git
*Garante espelhamento em tempo real, versionamento automático e preservação de estado.*

* **Gatilho Natural:** `"sincronize as estruturas"` | `"atualizar base"`  
  * **`//comando` Direto:** `//sync-base`  
  * **Ação Real:** Commit e push automático das estruturas de infraestrutura para o repositório remoto.  
  * **Comando Shell:** `git add -A && git commit -m "chore: auto-sync de infraestrutura" && git push origin main`

* **Gatilho Natural:** `"forçar snapshot"` | `"ponto de restauração"`  
  * **`//comando` Direto:** `//snapshot-force`  
  * **Ação Real:** Cria snapshot cronológico com timestamp UTC e força sincronização.  
  * **Comando Shell:** `git add -A && git commit -m "snapshot: $(date -u +'%Y-%m-%dT%H:%M:%SZ')" && git push --force origin HEAD`

* **Gatilho Natural:** `"resetar baseline"` | `"descartar alterações"`  
  * **`//comando` Direto:** `//reset-clean`  
  * **Ação Real:** Descarta alterações locais não comitadas e alinha a árvore estritamente com o HEAD.  
  * **Comando Shell:** `git reset --hard HEAD && git clean -fd`

* **Gatilho Natural:** `"espelhar workspace"` | `"backup total"`  
  * **`//comando` Direto:** `//backup-mirror`  
  * **Ação Real:** Sincronização incremental e espelhada para diretório de backup seguro isolado.  
  * **Comando Shell:** `rsync -aP --delete --exclude="node_modules" --exclude=".git" ./ ../Backup_Local/`

---

### 🔍 Foco 4: Telemetria, Diagnóstico Profundo & Mapeamento de Ambiente
*Visibilidade operacional de processos, portas abertas, sockets ativos e consumo de disco.*

* **Gatilho Natural:** `"diagnóstico completo"` | `"relatório de telemetria"`  
  * **`//comando` Direto:** `//telemetria-full`  
  * **Ação Real:** Mapeamento instantâneo de consumo de hardware, uso de CPU/RAM e partições de disco.  
  * **Comando Shell:** `top -l 1 -s 0 | head -n 25 && df -h /`

* **Gatilho Natural:** `"inspecionar tráfego"` | `"portas abertas"`  
  * **`//comando` Direto:** `//portas-ativas`  
  * **Ação Real:** Lista todos os processos ouvindo conexões TCP/UDP (WebSockets, APIs locais).  
  * **Comando Shell:** `lsof -i -P -n | grep LISTEN`

* **Gatilho Natural:** `"mapear arquivos pesados"` | `"varrer disco"`  
  * **`//comando` Direto:** `//varrer-grandes`  
  * **Ação Real:** Identifica todos os arquivos superiores a 50MB acumulados no workspace.  
  * **Comando Shell:** `find . -type f -size +50M -exec ls -lh {} +`

* **Gatilho Natural:** `"verificar integridade"` | `"check de runtime"`  
  * **`//comando` Direto:** `//check-health`  
  * **Ação Real:** Valida versões de sistema, toolchains de desenvolvimento e binários instalados.  
  * **Comando Shell:** `uname -a && which node python3 agy git`

---

### 🚀 Foco 5: Execução Desacoplada & Autonomia Não-Interativa (Background)
*Execução direta contínua sem bloqueio da interface do desenvolvedor.*

* **Gatilho Natural:** `"modo direto"` | `"execução raw"`  
  * **`//comando` Direto:** `//exec-raw`  
  * **Ação Real:** Ativa execução direta via CLI com flag de supressão de confirmações interativas.  
  * **Comando Shell:** `agy --dangerously-skip-permissions --effort high "$@"`

* **Gatilho Natural:** `"iniciar background"` | `"modo daemon"`  
  * **`//comando` Direto:** `//run-daemon`  
  * **Ação Real:** Despacha serviços em segundo plano desacoplados do terminal interativo.  
  * **Comando Shell:** `nohup "$@" > /dev/null 2>&1 &`

* **Gatilho Natural:** `"modo silencioso"` | `"suprimir logs"`  
  * **`//comando` Direto:** `//silence-logs`  
  * **Ação Real:** Ajusta variáveis de ambiente para registrar apenas erros críticos e economizar I/O.  
  * **Comando Shell:** `export LOG_LEVEL=ERROR && export NODE_ENV=production`

---

### 🛡️ Foco 6: Segurança, Integridade & Conformidade de Permissões
*Auditoria de permissões e blindagem de acesso restrito ao proprietário do sistema.*

* **Gatilho Natural:** `"auditar permissões"` | `"verificar conformidade"`  
  * **`//comando` Direto:** `//audit-perms`  
  * **Ação Real:** Localiza arquivos com permissões permissivas indevidas (world-writable).  
  * **Comando Shell:** `find . -type f \( -perm -o+w -o -perm -o+r \) -ls`

* **Gatilho Natural:** `"blindar acessos"` | `"endurecer segurança"`  
  * **`//comando` Direto:** `//harden-workspace`  
  * **Ação Real:** Restringe permissões de leitura/escrita estritamente ao usuário proprietário.  
  * **Comando Shell:** `chmod -R 750 .`

* **Gatilho Natural:** `"auditar sessões"` | `"histórico de logins"`  
  * **`//comando` Direto:** `//audit-logins`  
  * **Ação Real:** Exibe o histórico das últimas sessões autenticadas na máquina.  
  * **Comando Shell:** `last | head -n 15`

---

## 💻 Integração no Shell (`~/.zshrc` / Perfil)

```bash
# Parser de Linguagem Natural & Comandos de Alta Potência Antigravity
agy_router() {
    local cmd="$*"
    case "$cmd" in
        "foco total"|"//foco-ativo")
            echo "⚡ Aplicando foco total no processo..."
            renice -n -20 -p $$ 2>/dev/null
            kill -9 $(pgrep -f "websocket_server|node_orphan") 2>/dev/null
            echo "✅ Processos concorrentes ajustados."
            ;;
        "ambiente limpo"|"//purgar-buffers")
            echo "🧹 Purgando buffers e truncando logs pesados..."
            find . -name "*.log" -exec truncate -s 0 {} + 2>/dev/null
            echo "✅ Buffers limpos."
            ;;
        "sincronize as estruturas"|"//sync-base")
            echo "🔄 Sincronizando estruturas com o repositório..."
            git add -A && git commit -m "chore: auto-sync de infraestrutura" && git push origin main
            ;;
        "diagnóstico completo"|"//telemetria-full")
            echo "📊 Coletando telemetria de hardware..."
            top -l 1 -s 0 | head -n 20 && df -h /
            ;;
        "inspecionar tráfego"|"//portas-ativas")
            echo "🌐 Portas de rede em escuta ativa:"
            lsof -i -P -n | grep LISTEN
            ;;
        *)
            command agy "$@"
            ;;
    esac
}

alias agy="agy_router"
```
