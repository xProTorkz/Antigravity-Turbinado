# MANIFESTO DE REDE (NETWORK MANIFEST)

Este documento declara todos os hosts, protocolos e portas de rede que o **Antigravity Turbinado** acessa, garantindo conformidade anti-spyware e ausência total de túneis ou transmissões ocultas.

---

## 1. TABELA DE DESTINOS DE REDE

| Destino / Host | Protocolo / Porta | Finalidade | Obrigatório? |
|---|---|---|---|
| `api.github.com` | HTTPS (443) | Consulta e atualização da fila de Issues, leitura de commits e push de código. | **SIM** |
| `github.com` | HTTPS / SSH (443/22) | Operações do Git (clone, fetch, push de repositórios). | **SIM** |
| `127.0.0.1` (localhost) | HTTP (8765) | Comunicação interna local entre o Control Plane e o Antigravity (loopback estrito). | **SIM** |
| `raw.githubusercontent.com` | HTTPS (443) | Download de scripts oficiais de release e instalador assinado. | **SIM** |
| `generativelanguage.googleapis.com` | HTTPS (443) | Chamadas à API oficial do Google Gemini (somente quando invocado pelo Antigravity). | **SIM** |

---

## 2. GARANTIAS FORMALMENTE AUDITADAS

- `UNDECLARED_NETWORK_CALLS = 0`: Nenhuma conexão externa é feita fora dos domínios oficiais listados acima.
- `HIDDEN_TUNNEL = 0`: Não há abertura de túneis ngrok, Cloudflare Tunnel ou portas abertas para a internet pública sem autenticação.
- `LOOPBACK_BINDING = STRICT`: O daemon do Control Plane vincula-se exclusivamente ao endereço de loopback `127.0.0.1`, rejeitando conexões externas da rede local.
- `ENCRYPTION_IN_TRANSIT = TLS 1.3`: Toda comunicação com servidores remotos ocorre obrigatoriamente por HTTPS/TLS seguro.
