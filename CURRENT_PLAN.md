# CURRENT_PLAN.md - Arquitetura Modular do Dicionário Léxico & Pipelines Independentes

## Objetivo
Desacoplar completamente os pipelines operacionais do `dicionario_lexico.json`, transformando o dicionário em um catálogo léxico único, enxuto e inteligente (mapeando apenas palavras trocadas, variáveis e ponteiros), enquanto cada pipeline passa a residir em seu próprio arquivo JSON dedicado com suas variáveis e etapas executáveis.

---

## Fases do Plano

### Fase 1: Criação da Estrutura de Diretórios de Pipelines
* Criar o diretório canônico `4-automacao-e-shell/pipelines/`.

### Fase 2: Extração dos Pipelines Modulares (1 Arquivo por Gatilho)
* Criar e isolar cada pipeline em seu próprio arquivo JSON independente com variáveis, parâmetros de SO, etapas e critérios de aceitação:
  1. `pipelines/hwid_spoof.json` (5 fases de HWID spoofing e emulação AC 2.0).
  2. `pipelines/hwid_hardware_rebuild.json` (4 fases de reconstrução física de hardware e firmware limpo).
  3. `pipelines/inspecionar_hwid.json` (inspeção profunda de HWID e pre-flight check Gamers Club).
  4. `pipelines/sanitizar_ambiente.json` (sanitização de caches, DNS, ARP e logs de eventos).
  5. `pipelines/auditoria_total.json` (12 etapas de auditoria completa em 14 camadas).
  6. `pipelines/auditoria_pessoal.json` (14 camadas periciais de dossiê pessoal).
  7. `pipelines/auditoria_replicador.json` (espelhamento e réplica full-stack offline).
  8. `pipelines/dump_banco.json` (exportação contextual e checksum de banco de dados).
  9. `pipelines/limpeza_logs.json` (rotação determinística e truncamento de logs).
  10. `pipelines/sinc_git.json` (sincronização atômica e resolução de travas do Git).

### Fase 3: Unificação e Otimização Extrema do Dicionário Léxico
* Consolidar o dicionário em **um único arquivo canônico** (`dicionario_lexico.json`):
  * Manter apenas termos, aliases, descrições, variáveis e referências ao arquivo de pipeline correspondente (`pipeline_file: "pipelines/<nome>.json"`).
  * Eliminar os megablocos de pipelines embutidos que tornavam o arquivo pesado.
  * Remover módulos redundantes e manter a fonte de verdade limpa e coesa.

### Fase 4: Implementação do Executor Universal de Pipelines (`executar_pipeline.py`)
* Criar o executor leve e multiplataforma `4-automacao-e-shell/executar_pipeline.py`:
  * Resolução direta por gatilho ou nome do pipeline.
  * Injeção de variáveis contextuais.
  * Execução controlada com suporte nativo a Windows (PowerShell/cmd) e macOS/Linux (Bash).
  * Emissão de recibo de execução com status de cada etapa.

### Fase 5: Integração no `pipeline_engine.py`, `SENTINELA.md` e Atualizador
* Permitir que o `pipeline_engine.py` carregue dinamicamente os pipelines da pasta `pipelines/`.
* Atualizar o script de sincronização e o `SENTINELA.md`.
* Sincronizar o symlink global em `~/.gemini/config/dicionario_lexico.json`.

### Fase 6: Testes, Validação e Sincronização GitHub
* Executar testes unitários do runner para validar a resolução dos gatilhos (`hwid`, `inspecionar_hwid`, `sanitizar_hwid`).
* Executar o atualizador canônico.
* Realizar commit atômico e push para `origin main`.
