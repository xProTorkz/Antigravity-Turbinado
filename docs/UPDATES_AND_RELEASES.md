# CICLO DE RELEASES, ATUALIZAÇÕES & ROLLBACK

O **Antigravity Turbinado** adota um ciclo de desenvolvimento estável, previsível e seguro baseado em versionamento semântico estrito.

---

## 1. POLÍTICA DE VERSIONAMENTO SEMÂNTICO (SEMVER)

- `v0.x` — Versões de homologação, bootstrap e testes controlados.
- `v1.0.0` — Primeira versão comercial estável pronta para ambientes corporativos.
- `v1.x` — Melhorias incrementais, novas skills e otimizações de performance 100% retrocompatíveis.
- `v2.x` — Atualizações estruturais com breaking changes previamente notificadas.

---

## 2. ATUALIZAÇÕES AUDITÁVEIS & CHECKSUMS

Toda release gerada pelo time oficial acompanha:
1. **Tag Git Assinada:** Versionada no GitHub em `xProTorkz/ai-orchestration-kit`.
2. **Arquivo de Checksums (SHA256):** Garante que nenhum byte foi adulterado em trânsito.
3. **Changelog Detalhado:** Rastreabilidade completa de todas as alterações introduzidas.

---

## 3. PROCESSO DE ATUALIZAÇÃO SEGURA

Para verificar e aplicar atualizações na máquina do cliente:

```bash
# Executa a checagem de nova versão oficial
python3 scripts/updater.py --check

# Aplica a atualização preservando arquivos locais do usuário
python3 scripts/updater.py --apply
```

### Garantias do Atualizador:
- **Preservação de Configuração:** Nunca sobrescreve seu `PROJECT_REGISTRY.json`, tokens ou arquivos de projetos pessoais.
- **Rollback Instantâneo:** Se um teste de diagnóstico pós-atualização falhar, o script reverte automaticamente para a versão anterior sem downtime.
