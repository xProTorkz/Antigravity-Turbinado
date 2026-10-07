# GUIA_INICIAR_PROJETO_COM_IA.md

# Guia simples para iniciar qualquer projeto com ChatGPT + GitHub + Antigravity

Este guia serve para iniciar um projeto do zero sem deixar a IA se perder, criar arquivos demais ou alterar partes do sistema que não fazem parte da tarefa.

A regra principal é:

> **MVP primeiro. Poucos arquivos. Uma tarefa por vez. GitHub como fonte de verdade. A IA deve entender antes de alterar.**

---

# 1. Ferramentas

Use três peças principais:

## ChatGPT
Responsável por:
- entender o pedido;
- arquitetar;
- consultar o GitHub;
- criar e organizar Issues;
- revisar o estado do projeto;
- coordenar o trabalho;
- validar o resultado.

## GitHub
É a fonte de verdade do projeto.

Deve guardar:
- código;
- Issues;
- commits;
- estado atual;
- decisões;
- documentação mínima;
- histórico.

## Antigravity
Responsável pela execução local:
- abrir a pasta correta;
- ler a tarefa;
- editar o código;
- executar comandos;
- testar;
- validar;
- commit;
- push;
- atualizar a Issue.

Fluxo:

```text
VOCÊ
  ↓
CHATGPT
  ↓
GITHUB ISSUE
  ↓
ANTIGRAVITY
  ↓
CÓDIGO + TESTES
  ↓
COMMIT + PUSH
  ↓
GITHUB ATUALIZADO
  ↓
CHATGPT REVISA
```

---

# 2. Configurar o ChatGPT com GitHub

No ChatGPT:

1. abra **Settings**;
2. abra **Plugins**;
3. procure o plugin/conexão do **GitHub**;
4. instale/conecte sua conta;
5. autorize somente os repositórios necessários.

Os nomes das telas podem variar conforme a versão do ChatGPT.

Depois da conexão, teste dizendo:

```text
Liste meus repositórios do GitHub.
```

Depois:

```text
Encontre o repositório NOME_DO_PROJETO e me diga qual é a branch principal e o último commit.
```

Se o ChatGPT conseguir responder consultando o GitHub, a conexão está pronta.

---

# 3. Criar a pasta local do projeto

Crie uma pasta principal para seus projetos.

Exemplo:

```text
Projetos/
```

Dentro dela:

```text
Projetos/
  MeuProjeto/
```

Cada projeto deve possuir sua própria pasta.

Nunca coloque dois projetos diferentes dentro da mesma raiz de código.

---

# 4. Estrutura mínima recomendada

Não comece criando dezenas de pastas.

Comece pequeno:

```text
MeuProjeto/
│
├── src/
├── tests/                  # somente se o projeto já tiver testes
│
├── README.md
├── AGENTS.md
├── PROJECT_CONTEXT.md
├── PROJECT_STATE.md
├── GLOBAL_AI_EXECUTION_PROTOCOL.md
├── .gitignore
└── .env.example            # se houver configurações/segredos
```

Dependendo do projeto, talvez nem todas as pastas sejam necessárias.

## Regra

> **Não criar uma pasta ou arquivo porque "pode ser útil no futuro". Criar somente quando existir necessidade atual.**

---

# 5. Arquivos de contexto

A IA precisa de pouco contexto, mas esse contexto precisa ser confiável.

## `GLOBAL_AI_EXECUTION_PROTOCOL.md`

Regra global.

Define como qualquer IA deve executar qualquer tarefa:

```text
IDENTIFICAR
→ RECUPERAR CONTEXTO
→ TESTAR BASELINE
→ TRAVAR ESCOPO
→ EXECUTAR
→ TESTAR NOVAMENTE
→ VALIDAR
→ SINCRONIZAR
```

Este arquivo pode ser igual em todos os projetos.

---

## `AGENTS.md`

Regras específicas para agentes naquele projeto.

Exemplo:

```md
# Regras para agentes

- Trabalhar somente neste projeto.
- Não alterar arquivos fora do escopo da Issue.
- Não criar arquitetura paralela.
- Não criar arquivos duplicados.
- Reutilizar antes de criar.
- Manter o MVP simples.
- Testar antes e depois.
- Atualizar GitHub ao concluir.
```

---

## `PROJECT_CONTEXT.md`

Explica o projeto em poucas linhas.

Exemplo:

```md
# Projeto

## Objetivo
Aplicativo para organizar agendamentos de clientes.

## Usuário
Profissionais autônomos.

## MVP
- criar cliente;
- criar agendamento;
- visualizar agenda.

## Arquitetura
Frontend web + backend simples + banco.

## Fora do MVP
- IA;
- relatórios avançados;
- automações complexas;
- aplicativo nativo.
```

---

## `PROJECT_STATE.md`

Mostra somente o estado atual.

Exemplo:

```md
# Estado atual

Fase: MVP

Issue ativa: #4

Último SHA validado:
abc123

Funcionando:
- login;
- cadastro de cliente.

Em desenvolvimento:
- agenda.

Bloqueios:
- nenhum.

Próximo passo:
- concluir Issue #4.
```

Não transforme esse arquivo em diário.

O histórico pertence ao Git.

---

# 6. Criar o repositório GitHub

Crie um repositório com o mesmo nome ou nome claramente relacionado ao projeto.

Exemplo:

```text
MeuProjeto
```

Depois conecte a pasta local ao repositório.

Confirme sempre:

```bash
git remote -v
git branch --show-current
git status
```

A IA nunca deve escolher um projeto apenas pelo nome da pasta.

Ela deve confirmar pelo Git remote.

---

# 7. Primeira instrução para o ChatGPT

Ao começar um novo projeto, envie algo próximo deste prompt:

```text
Este é um novo projeto.

Nome:
MeuProjeto

Repositório:
OWNER/MeuProjeto

A partir de agora, GitHub é a fonte de verdade operacional.

Antes de qualquer tarefa:

1. identifique o projeto correto;
2. consulte o GitHub;
3. leia GLOBAL_AI_EXECUTION_PROTOCOL.md;
4. leia AGENTS.md;
5. leia PROJECT_CONTEXT.md;
6. leia PROJECT_STATE.md;
7. verifique Issues e último commit;
8. entenda o estado real antes de sugerir mudanças.

Regras:

- MVP primeiro;
- solução mais simples possível;
- mínimo de arquivos;
- não criar arquitetura futura;
- não duplicar funções;
- não alterar áreas fora do pedido;
- uma tarefa ativa por vez;
- Issues representam entregas reais;
- GitHub deve permanecer atualizado.

Quando eu pedir uma funcionalidade, primeiro transforme o pedido em uma Issue bem definida e depois coordene a execução.
```

---

# 8. Como pedir uma tarefa ao ChatGPT

Depois da configuração inicial, você não precisa explicar novamente como o projeto funciona.

Você pode falar:

```text
No projeto MeuProjeto, crie a função para cadastrar clientes.
```

O ChatGPT deve automaticamente:

1. consultar o GitHub;
2. recuperar o estado;
3. verificar se já existe Issue;
4. entender o código relacionado;
5. evitar duplicação;
6. criar ou atualizar a Issue;
7. definir critérios de aceite;
8. manter o escopo pequeno.

---

# 9. Modelo de Issue

Uma Issue deve ser simples.

Exemplo:

```md
# Cadastro de clientes

## Objetivo
Permitir cadastrar um cliente no sistema.

## Escopo
- nome;
- telefone;
- email;
- salvar no banco.

## Não alterar
- autenticação;
- pagamentos;
- agenda.

## Critérios de aceite
- cliente pode ser criado;
- campos obrigatórios são validados;
- dados ficam persistidos;
- nenhuma função existente quebra.

## Testes
- cadastro válido;
- cadastro inválido;
- persistência;
- regressão básica.

## Definition of Done
- código implementado;
- testes realizados;
- validação concluída;
- commit/push;
- Issue atualizada.
```

---

# 10. Não criar Issues demais

Issue não é comando.

Evite:

```text
Issue: abrir arquivo
Issue: mudar função
Issue: rodar teste
Issue: fazer commit
```

Tudo isso pertence à mesma Issue.

Uma Issue deve representar:

> **uma entrega, correção ou problema real do produto.**

---

# 11. Como iniciar o Antigravity

Abra o Antigravity na pasta correta do projeto.

Antes de qualquer tarefa, ele deve confirmar:

```text
pasta local
git remote
branch
git status
HEAD
```

Depois envie este prompt base:

```text
Você está trabalhando no projeto:

OWNER/MeuProjeto

GitHub é a fonte de verdade.

Antes de alterar qualquer código:

1. confirme que esta pasta corresponde ao repositório correto;
2. leia GLOBAL_AI_EXECUTION_PROTOCOL.md;
3. leia AGENTS.md;
4. leia PROJECT_CONTEXT.md;
5. leia PROJECT_STATE.md;
6. consulte a Issue ativa;
7. confira HEAD e git status;
8. execute baseline da área afetada.

Depois:

- trave o escopo da Issue;
- procure antes de criar;
- reutilize antes de duplicar;
- faça a menor alteração possível;
- preserve tudo que não estiver relacionado;
- teste;
- valide;
- revise diff;
- commit;
- push;
- atualize a Issue;
- atualize PROJECT_STATE.md.

Não crie arquivos extras sem necessidade.

Não crie arquitetura paralela.

Não execute outra Issue automaticamente.
```

---

# 12. Como mandar o Antigravity puxar uma Issue

Use:

```text
Abra o projeto atual.

Consulte o GitHub e execute a Issue #12.

Antes de executar:

- leia o contexto canônico;
- confirme o HEAD;
- verifique o estado local;
- faça baseline;
- confirme mentalmente o escopo.

Execute somente o que a Issue pede.

Depois:

- teste;
- valide;
- revise o diff;
- commit;
- push;
- atualize a Issue;
- atualize PROJECT_STATE.md.

Não altere nada fora da Issue.
```

---

# 13. Regra de uma tarefa ativa

Por padrão:

> **Uma Issue em execução por projeto.**

Só use dois agentes simultaneamente quando:

- os escopos forem totalmente separados;
- não editarem os mesmos arquivos;
- ambos partirem do mesmo HEAD;
- houver integração controlada depois.

Se não houver necessidade real:

**não paralelize.**

---

# 14. MVP primeiro

Antes de criar qualquer funcionalidade, pergunte:

> Isso é necessário para o MVP funcionar?

Se não:

```text
BACKLOG
```

Não implementar agora.

## MVP significa

- resolver o problema principal;
- fluxo principal funcionando;
- poucos recursos;
- poucos arquivos;
- interface simples;
- fácil de testar;
- fácil de entender;
- fácil de alterar.

MVP não significa código ruim.

---

# 15. Regra dos poucos arquivos

Antes de criar um arquivo:

```text
1. Já existe um arquivo responsável por isso?
2. Posso adicionar a função nele sem confundir responsabilidades?
3. Este novo arquivo realmente simplifica o projeto?
```

Se a resposta para a terceira pergunta for não:

> **não criar.**

Evite:

```text
service_new.py
service_v2.py
helper2.py
final.py
final_final.py
manager_new.py
```

---

# 16. Não criar arquitetura antes da necessidade

Não adicionar automaticamente:

- microservices;
- Redis;
- filas;
- workers;
- Kubernetes;
- múltiplos bancos;
- camadas extras;
- abstrações genéricas;
- frameworks adicionais.

Primeiro prove que existe um problema real que exige isso.

Regra:

> **A arquitetura cresce porque o produto precisa, não porque a tecnologia existe.**

---

# 17. Como configurar Skills

Skill não é etapa de projeto.

Não crie Skills chamadas:

```text
planejar
analisar
desenvolver
testar
validar
entregar
```

Essas etapas já fazem parte do protocolo global.

Crie uma Skill somente quando existir uma capacidade reutilizável.

Exemplos:

```text
deploy-hostinger
auditoria-seguranca
integracao-stripe
validacao-api-especifica
```

## Regra

Antes de criar Skill:

```text
Isso será reutilizado várias vezes?
Existe conhecimento especializado?
Evita repetir um processo complexo?
```

Se não:

> não criar Skill.

Prefira poucas Skills boas a dezenas de Skills pequenas.

---

# 18. Ordem de contexto para a IA

A IA não deve ler o projeto inteiro.

Ordem:

```text
GLOBAL RULE
    ↓
AGENTS
    ↓
PROJECT_STATE
    ↓
ISSUE
    ↓
PROJECT_CONTEXT
    ↓
ARQUIVOS AFETADOS
    ↓
DEPENDÊNCIAS DIRETAS
```

Somente ampliar contexto se necessário.

---

# 19. Regra Search → Read → Reuse → Edit

Antes de criar código:

```text
SEARCH
↓
READ
↓
REUSE
↓
EDIT
↓
CREATE somente se necessário
```

Isso evita duplicação.

---

# 20. Baseline antes de editar

Antes da alteração:

```text
O projeto inicia?
A função funciona?
Qual erro existe?
Quais testes passam?
Qual é o HEAD?
Existe alteração local?
```

Depois da alteração, testar novamente.

Comparar:

```text
ANTES
vs
DEPOIS
```

---

# 21. A IA não deve perguntar o que pode descobrir

Não perguntar:

```text
Onde está o arquivo?
Qual branch?
Qual foi o último commit?
Qual Issue está ativa?
Como o projeto inicia?
```

se isso puder ser descoberto pelo:

```text
GitHub
Git
README
PROJECT_STATE
código
scripts
```

A IA deve pesquisar primeiro.

Perguntar ao usuário somente quando houver uma decisão real.

---

# 22. Não tocar fora do escopo

Regra absoluta:

> **Se não é necessário para concluir a Issue, não mexer.**

Se encontrar outro problema:

```text
registrar
↓
colocar no backlog/Issue adequada
↓
continuar a tarefa atual
```

---

# 23. Fluxo obrigatório de qualquer tarefa

```text
1. IDENTIFICAR PROJETO
        ↓
2. CONSULTAR GITHUB
        ↓
3. LER CONTEXTO
        ↓
4. LER ISSUE
        ↓
5. VERIFICAR HEAD
        ↓
6. TESTAR BASELINE
        ↓
7. TRAVAR ESCOPO
        ↓
8. SEARCH → READ → REUSE
        ↓
9. EXECUTAR MUDANÇA MÍNIMA
        ↓
10. TESTAR
        ↓
11. VALIDAR
        ↓
12. REVISAR DIFF
        ↓
13. COMMIT
        ↓
14. PUSH
        ↓
15. ATUALIZAR ISSUE
        ↓
16. ATUALIZAR PROJECT_STATE
        ↓
17. ENTREGAR
```

---

# 24. Quando pedir confirmação humana

Não interromper a execução por alterações normais e reversíveis dentro da Issue.

Pedir autorização para:

- deploy em produção;
- perda de dados;
- exclusão destrutiva;
- mudança importante de arquitetura;
- segurança/permissões;
- exposição pública;
- custos;
- credenciais;
- reescrita de histórico Git;
- ações externas irreversíveis.

---

# 25. Ritual de criação de um projeto novo

Use sempre esta sequência:

```text
1. definir problema
2. definir MVP
3. criar pasta
4. criar repositório GitHub
5. conectar pasta ao Git
6. adicionar protocolo global
7. criar AGENTS.md
8. criar PROJECT_CONTEXT.md
9. criar PROJECT_STATE.md
10. criar .gitignore
11. conectar ChatGPT ao GitHub
12. pedir auditoria inicial da estrutura
13. criar primeira Issue do MVP
14. abrir Antigravity na pasta
15. executar Issue
16. testar e validar
17. commit + push
18. atualizar Issue + estado
19. repetir com a próxima Issue
```

---

# 26. Prompt mestre para qualquer projeto

Você pode reutilizar este prompt:

```text
A partir de agora você trabalha seguindo o protocolo global deste projeto.

GitHub é a fonte de verdade.

Antes de qualquer tarefa:

- identifique o projeto;
- consulte o GitHub;
- recupere o contexto;
- leia o estado;
- leia a Issue;
- confira HEAD;
- faça baseline;
- trave o escopo.

Durante a execução:

- MVP primeiro;
- solução mais simples;
- mínimo de arquivos;
- mínimo de dependências;
- Search → Read → Reuse → Edit;
- não duplicar;
- não criar arquitetura paralela;
- não alterar fora do escopo.

Depois:

- testar;
- validar;
- revisar regressão;
- revisar diff;
- revisar segurança;
- commit;
- push;
- atualizar Issue;
- atualizar PROJECT_STATE.

Não pergunte algo que possa descobrir sozinho.

Não confie apenas na memória da conversa.

Não comece outra Issue automaticamente.
```

---

# 27. Regra final

Um projeto saudável deve ser fácil de entender depois de meses sem trabalhar nele.

Qualquer agente deve conseguir abrir o projeto e descobrir rapidamente:

```text
O QUE É?
ONDE ESTÁ?
O QUE FUNCIONA?
O QUE ESTÁ SENDO FEITO?
QUAL É A ISSUE?
QUAL FOI O ÚLTIMO COMMIT VALIDADO?
QUAL É O PRÓXIMO PASSO?
```

Se isso não estiver claro:

> **o projeto está complexo demais ou mal documentado.**

A meta não é criar mais contexto.

A meta é criar **o mínimo de contexto necessário para nunca se perder**.

---

# RESUMO

```text
MVP
+
POUCOS ARQUIVOS
+
GITHUB COMO FONTE DE VERDADE
+
CONTEXTO MÍNIMO
+
ISSUE CLARA
+
UMA TAREFA POR VEZ
+
MUDANÇA MÍNIMA
+
TESTE ANTES E DEPOIS
+
VALIDAÇÃO
+
COMMIT/PUSH
+
ESTADO SEMPRE ATUALIZADO
```

Esse é o padrão.
