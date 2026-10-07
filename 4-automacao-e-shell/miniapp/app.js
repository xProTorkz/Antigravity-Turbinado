// Lógica Operacional do MiniApp Antigravity 2.0 (Chaining & Pipeline Queue)
document.addEventListener('DOMContentLoaded', () => {
  const commandsContainer = document.getElementById('commands-container');
  const searchInput = document.getElementById('search-input');
  const filterButtons = document.querySelectorAll('.filter-btn');
  const nextStepsContainer = document.getElementById('next-steps-container');
  const currentStepName = document.getElementById('current-step-name');
  const queueList = document.getElementById('queue-list');
  const queueEmptyMsg = document.getElementById('queue-empty-msg');
  const queueCountBadge = document.getElementById('queue-count-badge');
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toast-msg');

  let activeFilter = 'all';
  let executionQueue = [];
  let currentActiveCommand = SRE_COMMANDS[0]; // Inicia com unlock-git

  // 1. Renderizar Comandos
  function renderCommands(filter = 'all', query = '') {
    commandsContainer.innerHTML = '';
    const cleanQuery = query.toLowerCase().trim();

    const filtered = SRE_COMMANDS.filter(cmd => {
      const matchFilter = (filter === 'all') || (cmd.menu.toString() === filter);
      const matchQuery = !cleanQuery || 
        cmd.title.toLowerCase().includes(cleanQuery) ||
        cmd.slash.toLowerCase().includes(cleanQuery) ||
        cmd.phrase.toLowerCase().includes(cleanQuery) ||
        cmd.desc.toLowerCase().includes(cleanQuery) ||
        cmd.shell.toLowerCase().includes(cleanQuery) ||
        cmd.id.toLowerCase().includes(cleanQuery);
      return matchFilter && matchQuery;
    });

    if (filtered.length === 0) {
      commandsContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted); font-style: italic;">
          Nenhum comando encontrado para o termo "${query}". Tente buscar por sintomas como "travou", "porta" ou "disco".
        </div>
      `;
      return;
    }

    filtered.forEach(cmd => {
      const card = document.createElement('div');
      card.className = `command-card ${cmd.isSeries ? 'series-card' : ''} ${currentActiveCommand && currentActiveCommand.id === cmd.id ? 'highlight' : ''}`;
      card.id = `card-${cmd.id}`;

      const tagHtml = cmd.isSeries 
        ? `<span class="card-menu-tag card-series-tag">⚡ PIPELINE SEQUENCIAL (${cmd.seriesSteps ? cmd.seriesSteps.length : 0} ETAPAS)</span>`
        : `<span class="card-menu-tag">M${cmd.menu} • Grupo ${cmd.group}</span>`;

      let seriesStepsHtml = '';
      if (cmd.isSeries && cmd.seriesSteps && cmd.seriesSteps.length > 0) {
        seriesStepsHtml = `
          <div class="card-series-steps">
            ${cmd.seriesSteps.map((step, idx) => `
              <div class="series-step-badge">
                <span class="step-num">${idx + 1}</span>
                <span class="step-text">${step}</span>
              </div>
            `).join('')}
          </div>
        `;
      }

      card.innerHTML = `
        <div>
          <div class="card-top">
            ${tagHtml}
            <span class="card-slash">${cmd.slash}</span>
          </div>
          <h3 class="card-title">${cmd.title}</h3>
          <div class="card-phrase">💬 "${cmd.phrase.split(',')[0].trim()}"</div>
          <p class="card-desc">${cmd.desc}</p>
          ${seriesStepsHtml}
          <div class="code-box"><code>${cmd.shell}</code></div>
        </div>
        <div class="card-actions">
          <button class="btn-action btn-copy" data-type="shell" data-id="${cmd.id}">
            📋 Copiar Shell
          </button>
          <button class="btn-action" data-type="slash" data-id="${cmd.id}">
            💬 Copiar /Slash
          </button>
          <button class="btn-action btn-queue" data-id="${cmd.id}">
            ➕ Fila
          </button>
        </div>
      `;

      commandsContainer.appendChild(card);
    });

    attachCardEvents();
  }

  // 2. Anexar Eventos aos Botões dos Cards
  function attachCardEvents() {
    document.querySelectorAll('.btn-action').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const cmdId = btn.getAttribute('data-id');
        const cmd = SRE_COMMANDS.find(c => c.id === cmdId);
        if (!cmd) return;

        if (btn.classList.contains('btn-queue')) {
          addToQueue(cmd);
          return;
        }

        const copyType = btn.getAttribute('data-type');
        const textToCopy = copyType === 'slash' ? cmd.slash : cmd.shell;
        copyToClipboard(textToCopy, `Copiado: ${textToCopy}`);
        setActiveCommand(cmd);
      });
    });
  }

  // 3. Atualizar Comando Ativo e Sugestões do Próximo Passo
  function setActiveCommand(cmd) {
    currentActiveCommand = cmd;
    currentStepName.textContent = `${cmd.title} (${cmd.shell})`;

    // Atualizar destaque visual
    document.querySelectorAll('.command-card').forEach(c => c.classList.remove('highlight'));
    const activeEl = document.getElementById(`card-${cmd.id}`);
    if (activeEl) activeEl.classList.add('highlight');

    // Renderizar próximos passos sugeridos
    nextStepsContainer.innerHTML = '';
    const nextList = (cmd.next || []).map(nextId => SRE_COMMANDS.find(c => c.id === nextId)).filter(Boolean);

    if (nextList.length === 0) {
      nextStepsContainer.innerHTML = `
        <div style="color: var(--text-muted); font-size: 0.75rem; font-style: italic;">
          Nenhum encadeamento adicional obrigatório.
        </div>
      `;
      return;
    }

    nextList.forEach(nextCmd => {
      const card = document.createElement('div');
      card.className = 'next-step-card';
      card.innerHTML = `
        <div class="next-step-header">
          <span class="next-step-title">${nextCmd.title}</span>
          <span style="font-size: 0.7rem; color: var(--emerald-neon); font-family: var(--font-mono);">${nextCmd.slash}</span>
        </div>
        <p class="next-step-desc">${nextCmd.desc}</p>
        <div style="display: flex; gap: 0.4rem; margin-top: 0.4rem;">
          <button class="btn-action btn-copy" style="padding: 0.25rem 0.5rem; font-size: 0.7rem;" data-next-copy="${nextCmd.shell}">
            Copiar Próximo
          </button>
          <button class="btn-action btn-queue" style="padding: 0.25rem 0.5rem; font-size: 0.7rem;" data-next-queue="${nextCmd.id}">
            + Fila
          </button>
        </div>
      `;

      card.querySelector('[data-next-copy]').addEventListener('click', (e) => {
        e.stopPropagation();
        copyToClipboard(nextCmd.shell, `Próximo Passo Copiado: ${nextCmd.shell}`);
        setActiveCommand(nextCmd);
      });

      card.querySelector('[data-next-queue]').addEventListener('click', (e) => {
        e.stopPropagation();
        addToQueue(nextCmd);
      });

      card.addEventListener('click', () => {
        setActiveCommand(nextCmd);
      });

      nextStepsContainer.appendChild(card);
    });
  }

  // 4. Gerenciamento da Fila (Pipeline Ponto A -> Ponto B)
  function addToQueue(cmd) {
    executionQueue.push(cmd);
    renderQueue();
    copyToast(`Adicionado à Fila: ${cmd.title}`);
  }

  function removeFromQueue(index) {
    executionQueue.splice(index, 1);
    renderQueue();
  }

  function renderQueue() {
    queueList.innerHTML = '';
    queueCountBadge.textContent = `${executionQueue.length} passos`;

    if (executionQueue.length === 0) {
      queueList.appendChild(queueEmptyMsg);
      queueEmptyMsg.style.display = 'block';
      return;
    }

    queueEmptyMsg.style.display = 'none';

    executionQueue.forEach((cmd, idx) => {
      const item = document.createElement('div');
      item.className = 'queue-item';
      item.innerHTML = `
        <div class="queue-item-left">
          <span class="queue-index">${idx + 1}</span>
          <span class="queue-name">${cmd.id}</span>
        </div>
        <button class="queue-remove" title="Remover da fila">✕</button>
      `;

      item.querySelector('.queue-remove').addEventListener('click', () => removeFromQueue(idx));
      queueList.appendChild(item);
    });
  }

  // 5. Exportar Fila como Shell Script (.sh)
  document.getElementById('btn-export-sh').addEventListener('click', () => {
    if (executionQueue.length === 0) {
      alert("A fila está vazia. Adicione comandos clicando no botão '+ Fila'.");
      return;
    }

    const scriptLines = [
      "#!/usr/bin/env bash",
      "# ==============================================================================",
      "# Pipeline Automatizado SRE: Execução Sequencial do Ponto A ao Ponto B",
      "# Gerado pelo Console de Comandos Rápidos do Antigravity 2.0",
      "# ==============================================================================",
      "set -e  # Interrompe se qualquer etapa falhar criticamente",
      "",
      "echo \"🚀 Iniciando Pipeline Automatizado (" + executionQueue.length + " passos)...\"",
      ""
    ];

    executionQueue.forEach((cmd, idx) => {
      scriptLines.push(`# Passo ${idx + 1}: ${cmd.title}`);
      scriptLines.push(`echo "▶️ [${idx + 1}/${executionQueue.length}] Executando: ${cmd.title}..."`);
      scriptLines.push(`${cmd.shell}`);
      scriptLines.push("echo \"✅ Passo " + (idx + 1) + " concluído com sucesso.\"\n");
    });

    scriptLines.push("echo \"🎉 Pipeline completo executado com 100% de sucesso do Ponto A ao Ponto B!\"");

    const fullScript = scriptLines.join("\n");
    copyToClipboard(fullScript, `Pipeline Shell (${executionQueue.length} passos) copiado com sucesso!`);
  });

  // 6. Exportar Fila como Issue GitHub / ChatGPT (TASK_PROTOCOL v5)
  document.getElementById('btn-export-issue').addEventListener('click', () => {
    if (executionQueue.length === 0) {
      alert("A fila está vazia. Adicione comandos antes de gerar a Issue.");
      return;
    }

    const commandStepsYaml = executionQueue.map((cmd, idx) => `      - step: ${idx + 1}\n        name: "${cmd.title}"\n        cmd: "${cmd.shell}"\n        slash: "${cmd.slash}"`).join("\n");

    const issueText = `---
agent_task:
  version: 5
  task_id: task-sre-pipeline-${Date.now().toString().slice(-4)}
  target_project: antigravity-control-plane
  target_repo: xProTorkz/antigravity-control-plane
  priority: P0
  type: ops
  execution: implement
  source: chatgpt
  user_execution_confirmed: true
  risk: low
  pipeline_steps:
${commandStepsYaml}
---

# 📋 Fila de Execução Automatizada: Ponto A ➔ Ponto B

Esta tarefa foi empacotada pelo **ChatGPT** e delegada ao **GitHub**, onde o GitHub orquestra e comanda a execução direta pelo **Antigravity 2.0** no ambiente local.

## 🎯 Sequência Encadeada de Comandos:
${executionQueue.map((c, i) => `${i + 1}. **${c.title}** \`[${c.slash}]\` ➔ \`${c.shell}\``).join("\n")}

## ✅ Critérios de Aceite:
- Executar rigorosamente todas as etapas na ordem sequencial informada.
- Validar ausência de erros e verificar estado do repositório/processos ao final.
- Retornar recibo de confirmação com status **VALIDADO** e **DONE**.
`;

    copyToClipboard(issueText, `Contrato de Tarefa GitHub / ChatGPT copiado para a área de transferência!`);
  });

  // 7. Limpar Fila
  document.getElementById('btn-clear-queue').addEventListener('click', () => {
    executionQueue = [];
    renderQueue();
    copyToast("Fila esvaziada.");
  });

  // 8. Busca Instantânea
  searchInput.addEventListener('input', (e) => {
    renderCommands(activeFilter, e.target.value);
  });

  // 9. Filtro por Abas
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.getAttribute('data-filter');
      renderCommands(activeFilter, searchInput.value);
    });
  });

  // 10. Copiar para Área de Transferência & Toast
  function copyToClipboard(text, msg) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => copyToast(msg)).catch(() => fallbackCopy(text, msg));
    } else {
      fallbackCopy(text, msg);
    }
  }

  function fallbackCopy(text, msg) {
    const tempInput = document.createElement('textarea');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    copyToast(msg);
  }

  function copyToast(msg) {
    toastMsg.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }

  // Inicialização
  renderCommands();
  setActiveCommand(currentActiveCommand);
  renderQueue();
});
