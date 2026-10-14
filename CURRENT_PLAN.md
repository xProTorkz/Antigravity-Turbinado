# CURRENT_PLAN.md - Arquitetura Canônica: Dicionário Conceitual & Pipelines Executivos

## Visão e Princípio Fundamental
* **Dicionário (`dicionario_lexico.json`):** Mostra **exclusivamente o que é e o que faz** cada termo, com seus gatilhos e o ponteiro para a esteira correspondente. Nenhum comando cru de execução dentro do dicionário.
* **Pipelines (`pipelines/*.json`):** Cada pipeline em arquivo próprio executa **exclusivamente os comandos configurados** (etapas, comandos, timeouts, critérios).

---

## Fases de Execução & Status Operacional

### Fase 1: Padronização dos Arquivos de Pipeline (`4-automacao-e-shell/pipelines/`) [CONCLUÍDO]
* Todas as 18 esteiras executivas residem em arquivos independentes na pasta `pipelines/`:
  1. `auditoria_total.json` (14 etapas de auditoria profunda em todas as camadas)
  2. `auditoria_replicador.json` (12 etapas de espelhamento e réplica full-stack)
  3. `auditoria_pessoal.json` (5 etapas periciais de privacidade)
  4. `auditoria_global.json` (9 etapas de OSINT e superfície de rede)
  5. `auditoria.json` (4 etapas de diagnóstico rápido de projeto)
  6. `hwid_spoof.json` (5 etapas de emulação e spoofing AC 2.0)
  7. `hwid_hardware_rebuild.json` (4 etapas de reconstrução física de hardware)
  8. `inspecionar_hwid.json` (execução do inspecionar_hwid.ps1)
  9. `sanitizar_ambiente.json` (execução do sanitizar_ambiente.ps1)
  10. `dump_banco.json` (3 etapas de dump)
  11. `limpeza_logs.json` (3 etapas de truncamento de logs)
  12. `sinc_git.json` (3 etapas de sincronização atômica)
  13. `atualizar_sentinela.json` (execução do atualizador canônico)
  14. `trainer_de_jogo.json` (4 etapas de análise de memória e processos)
  15. `audit_pci_cards.json` (execução do scanner PCI-DSS de cartões)
  16. `scrape.json` (4 etapas de extração e raspagem web)
  17. `crawl.json` (3 etapas de mapeamento recursivo de rotas)
  18. `espelhamento_frontend.json` (4 etapas de cópia estática e relativização offline)

### Fase 2: Reestruturação Limpa do Dicionário Léxico (`dicionario_lexico.json`) [CONCLUÍDO]
* Dicionário canônico único e unificado com schema conceitual estrito:
  * `o_que_e`: Definição conceitual clara do termo.
  * `o_que_faz`: Explicação detalhada da finalidade e resultado da ação.
  * `gatilhos`: Sinônimos e expressões acionadoras.
  * `pipeline`: Caminho para o arquivo correspondente em `pipelines/<nome>.json`.
* Zero comandos crus poluindo o dicionário.

### Fase 3: Ajuste do Executor Universal (`executar_pipeline.py`) [CONCLUÍDO]
* Separação estrita de comportamentos:
  * Consulta de Termo (ex: `auditoria total`, `auditoria replicador`): Dicionário apenas mostra O QUE É e O QUE FAZ.
  * Chamada de Pipeline (ex: `pipeline auditoria total`, `pipeline replicador`, `pipeline completo`): Carrega o arquivo do pipeline e executa os comandos configurados.

### Fase 4: Validação, Compilação e Sincronização GitHub [CONCLUÍDO]
* `build_dicionario.py` executado com 100% de sucesso, gerando `dicionario_lexico.min.json` e atualizando o symlink global em `~/.gemini/config/dicionario_lexico.json`.
* Testes validados para consulta léxica (`auditoria total`, `auditoria replicador`) e execução de esteira (`pipeline auditoria`, `pipeline sinc_git`).

