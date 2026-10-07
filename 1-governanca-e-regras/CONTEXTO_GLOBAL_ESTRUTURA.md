# GLOBAL_AI_EXECUTION_PROTOCOL.md

## Protocolo Global de Execução para IA

Esta regra vale para **qualquer projeto** e deve ser aplicada a **toda tarefa**, pequena ou grande.

O objetivo é impedir que a IA:
- se perca no projeto;
- pergunte coisas que já estão documentadas;
- invente arquitetura;
- crie arquivos desnecessários;
- altere áreas fora do pedido;
- quebre código existente;
- execute sem testar;
- declare concluído sem validar.

---

# REGRA CENTRAL

Toda tarefa deve seguir sempre o mesmo fluxo:

**IDENTIFICAR → RECUPERAR CONTEXTO → TESTAR BASELINE → TRAVAR ESCOPO → EXECUTAR → TESTAR NOVAMENTE → VALIDAR → SINCRONIZAR**

A IA não pode pular etapas.

---

# 1. IDENTIFICAR O PROJETO

Antes de qualquer alteração, confirmar:

- projeto correto;
- repositório correto;
- branch correta;
- Issue/tarefa correta;
- ambiente correto.

Nunca misturar projetos.

Se houver vários projetos com nomes parecidos, confirmar pelo Git remote, estrutura e contexto canônico.

---

# 2. RECUPERAR O CONTEXTO ANTES DE AGIR

Antes de editar qualquer arquivo, a IA deve consultar o GitHub e recuperar somente o contexto necessário.

Ordem obrigatória:

1. regras globais;
2. regras específicas do projeto;
3. estado atual do projeto;
4. Issue ativa;
5. último commit/HEAD;
6. arquivos diretamente relacionados à tarefa;
7. dependências desses arquivos, somente se necessário.

A IA deve preferir dados do GitHub e do código atual à memória da conversa.

## Regra

**Nunca perguntar ao usuário algo que já possa ser descoberto no GitHub, no estado do projeto ou no código.**

---

# 3. TESTAR O ESTADO ATUAL ANTES DE ALTERAR

Antes de mudar o código, criar um baseline.

Verificar:

- o projeto inicia?
- a função atual funciona?
- quais testes passam?
- qual erro existe agora?
- qual é o comportamento atual?
- quais arquivos estão modificados?
- existe mudança local ainda não commitada?

Registrar o estado anterior.

Isso permite saber se a alteração melhorou ou quebrou alguma coisa.

---

# 4. TRAVAR O ESCOPO

Antes de desenvolver, definir internamente:

## PODE ALTERAR
Somente:
- arquivos necessários;
- funções diretamente relacionadas;
- dependências indispensáveis.

## NÃO PODE ALTERAR
- funcionalidades não relacionadas;
- arquitetura principal;
- outros módulos;
- outros projetos;
- arquivos que não participam do problema;
- código que já funciona sem necessidade.

## Regra de ouro

**Se não é necessário para concluir a tarefa, não mexer.**

Se encontrar outro problema:
- registrar;
- colocar na Issue correta;
- continuar a tarefa atual.

Não aproveitar a tarefa para “melhorar” outras partes.

---

# 5. SEARCH → READ → REUSE → EDIT

Antes de criar qualquer coisa:

1. SEARCH — procurar se já existe;
2. READ — entender como funciona;
3. REUSE — reutilizar o que existe;
4. EDIT — alterar somente se necessário;
5. CREATE — criar novo somente se não existir solução adequada.

Preferir sempre modificar a estrutura existente.

Evitar:
- arquivos duplicados;
- versões paralelas;
- `main2.py`;
- `motor_v2.py`;
- `final.py`;
- `novo.py`;
- `teste_final.py`;
- funções com a mesma responsabilidade em lugares diferentes.

---

# 6. EXECUTAR A MENOR MUDANÇA POSSÍVEL

A implementação deve ser:

- simples;
- direta;
- compreensível;
- pequena;
- previsível;
- compatível com a arquitetura existente.

Preferir poucos arquivos.

Não aumentar a complexidade sem necessidade real.

Se duas soluções resolvem o mesmo problema:

**usar a mais simples.**

---

# 7. TESTAR NOVAMENTE APÓS A ALTERAÇÃO

Depois da implementação, repetir os testes relevantes.

Comparar:

**ANTES vs DEPOIS**

Validar:

- tarefa principal;
- integração afetada;
- regressões;
- inicialização;
- erros;
- logs;
- frontend/backend quando aplicável;
- runtime real quando necessário.

Não considerar “compilou” como teste suficiente.

---

# 8. VALIDAR CONTRA O OBJETIVO

Depois dos testes, confirmar:

- resolveu exatamente o que foi pedido?
- respeitou o escopo?
- algo fora do escopo foi alterado?
- criou arquivo desnecessário?
- duplicou lógica?
- alterou arquitetura sem necessidade?
- quebrou comportamento anterior?
- deixou código morto?
- deixou teste temporário?
- deixou segredo em código/log?

Só depois disso considerar a tarefa pronta.

---

# 9. SINCRONIZAR O GITHUB

Toda tarefa importante deve terminar com o GitHub atualizado.

Ordem:

1. revisar diff;
2. remover arquivos temporários;
3. revisar segredos;
4. executar testes finais;
5. commit;
6. push;
7. atualizar Issue;
8. atualizar estado atual do projeto;
9. registrar próximo passo.

GitHub é a fonte de verdade operacional.

A conversa não substitui o GitHub.

---

# 10. ISSUES

Issue representa uma entrega ou problema real do projeto.

Não criar Issue para:
- cada comando;
- cada teste;
- cada arquivo;
- cada tentativa;
- cada pequena subtarefa.

Subtarefas devem ficar como checklist dentro da Issue principal.

Antes de criar nova Issue:

1. procurar Issue existente;
2. verificar se o problema pertence a ela;
3. atualizar a existente quando possível.

---

# 11. UMA TAREFA ATIVA POR PROJETO

Por padrão:

**uma execução principal por projeto de cada vez.**

Se houver mais de um agente:

- cada agente deve ter escopo separado;
- não editar os mesmos arquivos ao mesmo tempo;
- trabalhar a partir do mesmo HEAD;
- sincronizar antes de integrar.

---

# 12. CONTEXTO MÍNIMO

A IA não deve carregar dezenas de arquivos sem necessidade.

Fluxo:

**Issue → arquivos afetados → dependências diretas → ampliar somente se necessário**

Isso reduz:
- confusão;
- consumo de contexto;
- alterações acidentais;
- decisões inconsistentes.

---

# 13. POUCOS ARQUIVOS

O projeto deve permanecer fácil de navegar.

Antes de criar novo arquivo, perguntar internamente:

1. já existe um arquivo responsável por isso?
2. essa função pode entrar nele sem confundir responsabilidades?
3. o novo arquivo realmente melhora clareza?

Se não houver justificativa clara:

**não criar.**

---

# 14. UMA FONTE DE VERDADE

Não duplicar:

- configuração;
- estado;
- persistência;
- regras;
- estratégia;
- autenticação;
- caminhos;
- dados.

Cada responsabilidade deve possuir uma fonte principal claramente identificável.

---

# 15. NÃO CONFIAR NA MEMÓRIA DO AGENTE

Nenhuma tarefa deve depender de:

> “eu lembro que estava assim”

O estado deve ser recuperado novamente.

Fonte de verdade:

**GitHub → Estado do Projeto → Issue → Código Atual → Runtime**

---

# 16. NÃO PERGUNTAR QUANDO A RESPOSTA JÁ EXISTE

A IA deve investigar primeiro.

Não perguntar:
- onde está o arquivo, se pode localizar;
- qual branch, se pode consultar;
- como executar, se README/scripts mostram;
- qual foi a última mudança, se Git mostra;
- qual tarefa está ativa, se a Issue mostra.

Perguntar ao usuário somente quando existir uma decisão humana real que não possa ser determinada pelo projeto.

---

# 17. HUMAN GATES

Exigir autorização explícita somente para ações de alto impacto, como:

- produção;
- exclusão/perda de dados;
- migração destrutiva;
- mudança da arquitetura principal;
- permissões/segurança;
- exposição pública;
- custos;
- credenciais;
- reescrita de histórico;
- ações externas irreversíveis.

Alterações normais e reversíveis dentro da Issue não devem gerar perguntas desnecessárias.

---

# 18. DEFINITION OF DONE

Uma tarefa só está concluída quando:

- contexto foi recuperado;
- baseline foi feito;
- escopo foi respeitado;
- mudança mínima foi implementada;
- testes passaram;
- regressões foram verificadas;
- validação confirmou o objetivo;
- diff foi revisado;
- arquivos temporários foram removidos;
- segredos foram revisados;
- commit foi criado;
- push foi feito;
- Issue foi atualizada;
- estado do projeto foi atualizado.

---

# PIPELINE FIXO GLOBAL

Para qualquer tarefa:

```text
1. IDENTIFICAR PROJETO
        ↓
2. BUSCAR CONTEXTO NO GITHUB
        ↓
3. LER ESTADO + ISSUE + HEAD
        ↓
4. TESTAR ESTADO ATUAL (BASELINE)
        ↓
5. DEFINIR E TRAVAR ESCOPO
        ↓
6. SEARCH → READ → REUSE
        ↓
7. EXECUTAR MUDANÇA MÍNIMA
        ↓
8. TESTAR NOVAMENTE
        ↓
9. VALIDAR OBJETIVO + REGRESSÃO
        ↓
10. REVISAR DIFF + SEGURANÇA
        ↓
11. COMMIT + PUSH
        ↓
12. ATUALIZAR ISSUE + PROJECT_STATE
        ↓
13. ENTREGAR RESULTADO
```

---

# REGRA FINAL

Toda IA que trabalhar em um projeto deve agir como se estivesse entrando no projeto pela primeira vez:

**não confiar em memória, não improvisar, não criar sem procurar, não alterar sem entender, não tocar fora do escopo, não concluir sem testar e não entregar sem atualizar o GitHub.**

O comportamento deve ser sempre previsível:

**ENTENDER → TESTAR → ALTERAR → TESTAR → VALIDAR → SINCRONIZAR.**
