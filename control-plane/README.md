# 🎛️ Antigravity Control Plane (Módulo Integrado)

O **Control Plane** é o núcleo de orquestração autônoma do **Antigravity Turbinado**. Ele atua como o elo de conexão entre o cérebro planejador (ChatGPT), o organizador canônico de tarefas (GitHub Issues) e o executor local (Google Antigravity).

---

## 🏗️ Arquitetura e Componentes

| Módulo | Arquivo | Responsabilidade |
| :--- | :--- | :--- |
| **Dispatcher** | `ag_control_plane/dispatcher.py` | Orquestrador de fila de tarefas e despacho de execuções. |
| **Scheduler** | `ag_control_plane/subagent_scheduler.py` | Agendador paralelo de subagentes com fan-out/fan-in e ConflictGuard. |
| **Task Parser** | `ag_control_plane/task_parser.py` | Parser de `agent_task v5` a partir do corpo de Issues do GitHub. |
| **Task Refiner** | `ag_control_plane/task_refiner.py` | Refinador semântico de contratos de execução e Scope Lock. |
| **Agent Invoker** | `ag_control_plane/agent_invoker.py` | Disparador de sessões e subprocessos do Antigravity CLI. |
| **Context Firewall** | `ag_control_plane/context_firewall.py` | Blindagem e sanitização de contexto contra vazamentos e loops. |
| **Lock Manager** | `ag_control_plane/lock_manager.py` | Gestão de concorrência e trava `MAX_WRITER_PER_PROJECT = 1`. |
| **GitHub Client** | `ag_control_plane/github_client.py` | Comunicação com a API do GitHub (labels, issues, status). |
| **Daemon** | `dispatcher_daemon.py` | Processo daemon em background para escuta de tarefas. |
| **Registry** | `PROJECT_REGISTRY.json` | Registro de projetos, repositórios e workspaces locais. |

---

## 🚀 Como Executar

```bash
# Executar o dispatcher em modo one-shot
python3 control-plane/dispatcher_daemon.py --once

# Executar o dispatcher contínuo em background
python3 control-plane/dispatcher_daemon.py
```
